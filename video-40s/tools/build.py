"""Build the ~45 s GSS video: voiceover, timing, music, MP4.

Usage (from the repo root, with a Python that has numpy + soundfile, and kokoro-onnx for the voice):
    python video-40s/tools/build.py [--kokoro DIR] [--voice af_heart] [--speed 1.0] [--no-render]

--kokoro DIR points at a folder holding onnx/model.onnx and voices/<name>.bin from
onnx-community/Kokoro-82M-v1.0-ONNX on Hugging Face. Without it the video gets music only,
and scene lengths fall back to the estimates in index.html.
"""
import argparse, json, re, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "index.html"
SR = 44100

# What the narrator says (numbers spelled out so the voice reads them right).
# Subtitles use the written version in index.html.
SPOKEN = [
    "Language models can memorize their training data, and repeat it word for word.",
    "Most fixes correct every token the same way, and the model gets worse at everything else.",
    "Compared with a reference model, the memorization signal is concentrated. Ten percent of tokens carry up to eighty-nine percent of it.",
    "So G.S.S. fixes it only there. A probe reads each token, a gate checks a threshold, and a steer corrects just the flagged ones.",
    "On Pythia six point nine B, memorization falls from eighty-nine to seven percent, with ten to a hundred times less compute than optimization methods.",
    "Mitigating Memorization Where It Happens. See you at NeurIPS.",
]
MIN_LEN = [6.0, 6.5, 8.6, 9.6, 8.8, 5.0]   # shortest each shot may be, so animations finish
LEAD, TAIL = 0.4, 0.75                      # silence before / after each line


def tts(kdir, voice, speed):
    from kokoro_onnx import Kokoro
    k = Kokoro(str(Path(kdir) / "onnx/model.onnx"), str(_voices_npz(kdir)))
    clips = []
    for line in SPOKEN:
        audio, sr = k.create(line, voice=voice, speed=speed, lang="en-us")
        clips.append(_resample(np.asarray(audio, dtype=np.float32), sr))
    return clips


def _voices_npz(kdir):
    """kokoro-onnx wants one .npz of voices; build it from the per-voice .bin files."""
    out = Path(kdir) / "voices.npz"
    if not out.exists():
        np.savez(out, **{p.stem: np.fromfile(p, dtype=np.float32).reshape(-1, 1, 256)
                         for p in (Path(kdir) / "voices").glob("*.bin")})
    return out


def _resample(x, sr):
    if sr == SR:
        return x
    n = int(round(len(x) * SR / sr))
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)


def trim(x, thr=0.004):
    idx = np.where(np.abs(x) > thr)[0]
    return x[max(0, idx[0] - 400): idx[-1] + 2000] if len(idx) else x


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def music(D, vo_windows):
    """Soft ambient bed: warm pad chords, a quiet plucked arpeggio, a little room."""
    n = int(D * SR) + SR
    t = np.arange(n) / SR
    chords = [[50, 57, 61, 64, 66], [47, 54, 57, 61, 62], [43, 50, 54, 59, 62], [45, 52, 57, 59, 64]]
    clen = 6.0
    pad = np.zeros(n)
    for ci in range(int(D / clen) + 2):
        notes = chords[ci % 4]
        a, b = ci * clen - 1.2, (ci + 1) * clen + 1.2
        env = np.clip((t - a) / 1.6, 0, 1) * np.clip((b - t) / 1.6, 0, 1)
        env = np.sin(env * np.pi / 2) ** 2
        mask = env > 0
        for m in notes:
            f = midi(m)
            for det in (-0.0018, 0, 0.0021):
                ph = 2 * np.pi * f * (1 + det) * t[mask]
                pad[mask] += env[mask] * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)) / 3
    pad = _lowpass(pad, 1800) * 0.06

    pluck = np.zeros(n)
    step = 60 / 80 / 2          # eighth notes at 80 bpm
    pattern = [0, 2, 4, 3, 1, 3, 2, 4]
    i = 0
    for s in np.arange(1.5, D - 1.5, step):
        notes = chords[int(s // clen) % 4]
        m = notes[pattern[i % 8] % len(notes)] + 12
        i += 1
        a = int(s * SR); L = int(1.2 * SR)
        tt = np.arange(L) / SR
        tone = np.sin(2 * np.pi * midi(m) * tt) * np.exp(-tt / 0.35) * (1 - np.exp(-tt / 0.004))
        vel = 0.55 + 0.45 * (i % 4 == 1)
        pluck[a:a + L] += tone[: n - a] * vel
    d = int(step * 3 * SR)
    echo = np.zeros(n); echo[d:] = pluck[:-d] * 0.32
    pluck = (pluck + echo) * 0.035

    x = pad + pluck
    x = x + _reverb(x) * 0.35
    fade = np.clip(t / 1.5, 0, 1) * np.clip((D - t) / 2.5, 0, 1)
    duck = np.ones(n)
    for a, b in vo_windows:
        duck -= 0.55 * np.clip(np.minimum((t - a + 0.3) / 0.3, (b + 0.4 - t) / 0.4), 0, 1)
    return (x * fade * duck)[: int(D * SR)]


def _lowpass(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / (1 + (f / fc) ** 4), len(x))


def _reverb(x, secs=2.2):
    rng = np.random.default_rng(7)
    L = int(secs * SR); ir = rng.standard_normal(L) * np.exp(-np.arange(L) / SR / (secs / 5))
    ir = _lowpass(ir, 3500); ir /= np.sqrt((ir ** 2).sum())
    m = len(x) + L - 1; nfft = 1 << (m - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[: len(x)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kokoro"); ap.add_argument("--voice", default="af_heart")
    ap.add_argument("--speed", type=float, default=1.0); ap.add_argument("--no-render", action="store_true")
    args = ap.parse_args()

    html = HTML.read_text()
    block = re.search(r'(<script id="timing" type="application/json">\s*)(.*?)(\s*</script>)', html, re.S)
    timing = json.loads(block.group(2))

    clips = None
    if args.kokoro:
        clips = [trim(c) for c in tts(args.kokoro, args.voice, args.speed)]
        durs = [max(mn, LEAD + len(c) / SR + TAIL) for mn, c in zip(MIN_LEN, clips)]
        timing = {"durations": [round(d, 2) for d in durs],
                  "vo": [[LEAD, round(len(c) / SR, 2)] for c in clips], "audio": True}
        html = html[: block.start(2)] + json.dumps(timing) + html[block.end(2):]
        HTML.write_text(html)

    starts = np.concatenate([[0], np.cumsum(timing["durations"])])
    D = float(starts[-1])
    windows = [(starts[i] + v0, starts[i] + v0 + vl) for i, (v0, vl) in enumerate(timing["vo"])] if clips else []
    mix = music(D, windows)
    if clips:
        for (a, _), c in zip(windows, clips):
            s = int(a * SR); mix[s: s + len(c)] += c[: len(mix) - s] * 0.9

    with tempfile.TemporaryDirectory() as tmp:
        raw = Path(tmp) / "mix.wav"
        sf.write(raw, (mix / max(1e-6, np.abs(mix).max()) * 0.8).astype(np.float32), SR)
        norm = "loudnorm=I=-16:TP=-1.5:LRA=11"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", norm, "-ar", "44100",
                        "-c:a", "libmp3lame", "-b:a", "192k", ROOT / "soundtrack.mp3"], check=True)
    print(f"soundtrack.mp3: {D:.1f}s, voice={'yes' if clips else 'no'}")

    if not args.no_render:
        subprocess.run(["node", str(ROOT / "tools/export.js")], check=True)


if __name__ == "__main__":
    sys.exit(main())
