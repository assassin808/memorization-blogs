# ~47-second video: Mitigating Memorization Where It Happens

NeurIPS 2026 · arXiv 2602.08901 · cut 2 (each shot held longer, with sound)

| Time | Beat | Voiceover | On screen | Source |
|---|---|---|---|---|
| 0.0–6.0 | Hook | "Language models can memorize their training data, and repeat it word for word." | "Alice's phone number is" completes with 555-0142 in clay. Tags: privacy, copyright. | Intro; Sec. 3 |
| 6.0–12.5 | Problem | "Most fixes correct every token the same way, and the model gets worse at everything else." | A bar sweeps across every token and pushes them all down. Accuracy 97.0 → 63.3 (Slim, TinyMem math). | Fig. 3a; Table 1 |
| 12.5–21.7 | Insight | "Compared with a reference model, the memorization signal is concentrated. Ten percent of tokens carry up to eighty-nine percent of it." | Per-token signal bars, a few clay spikes. 10% of positions carry up to 89%. | Fig. 1; Sec. 3 |
| 21.7–31.3 | Method | "So GSS fixes it only there. A probe reads each token, a gate checks a threshold, and a steer corrects just the flagged ones." | Probe → Gate → Steer appear as they are named. Flagged tokens rise and turn olive; the rest pass untouched. | Fig. 2, 3b; Eq. 10; Thm 4.1 |
| 31.3–41.9 | Result | "On Pythia 6.9B, memorization falls from 89 to 7 percent, with ten to a hundred times less compute than optimization methods." | 89% → 7% countdown; 0% on TinyMem with accuracy kept; 10–100× less compute. | Tables 1–2; Abstract |
| 41.9–46.9 | Close | "Mitigating Memorization Where It Happens. See you at NeurIPS." | Title, authors, affiliations, arXiv ID. | Title page |

Times above are fitted to the current voiceover (Kokoro `af_heart`). `tools/build.py` re-fits each shot whenever the voice changes.

## Sound
- Music: a soft generated pad with a quiet plucked arpeggio (no licensing issues), ducked under the voice, loudness-normalized to -16 LUFS.
- Voice: Kokoro-82M (open model, `af_heart` voice) via `tools/build.py --kokoro DIR`. Needs the model files from Hugging Face. To use your own recording instead, record the six lines above and mix them in place of the TTS clips.

## Rebuild
```bash
python video-40s/tools/build.py --kokoro path/to/kokoro    # voice + music + MP4
python video-40s/tools/build.py                            # music only
```
