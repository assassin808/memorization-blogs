# 15-second video: Mitigating Memorization Where It Happens

NeurIPS 2026 poster · arXiv 2602.08901 · cut 1 of 2 (short teaser)

**One-line message:** LLMs memorize in a few tokens, so GSS finds those tokens and steers only them, cutting verbatim recall without retraining.

| Time | Beat | Voiceover | On screen | Source in paper |
|---|---|---|---|---|
| 0.0–3.0s | Hook | "Language models can repeat their training data, word for word." | "Alice's phone number is" completes with `555-0142`, highlighted in clay. Tags: privacy, copyright. | Intro; Sec. 3 example |
| 3.0–6.5s | Insight | "But memorization lives in just a few tokens." | Per-token signal bars (ω = log p_target − log p_ref): most low, a few clay spikes. Stat: 10% of positions carry up to 89% of the signal. | Fig. 1; Sec. 3 (30–89% across 12 settings) |
| 6.5–10.6s | Method | "So we fix it only there: probe, gate, steer." | Tokens flow Probe → Gate. Flagged tokens go up through Steer and turn olive; the rest pass below untouched. "Closed-form directions from one SVD · no weight updates." | Fig. 2, Fig. 3; Eq. 10; Thm. 4.1 |
| 10.6–13.4s | Result | "Memorization falls from 89 to 7 percent." | 89% → 7% countdown (Pythia-6.9B). 0% on TinyMem with accuracy kept (96.98 vs 97.00). 10–100× less compute. | Table 1, Table 2, Abstract |
| 13.4–15.0s | Close | "Mitigating Memorization Where It Happens. NeurIPS 2026." | Title, authors, UBC · Vector Institute, arXiv ID. | Title page |

## Style
Anthropic-inspired: ivory ground, near-black ink, one clay accent reserved for memorized tokens, olive for corrected ones. Serif headlines, sans body, mono for tokens and math. Wide margins, one idea per shot, short fades. Subtitles are burned in so it plays muted.

## Files
- `index.html`: animated preview with play, scrub and shot list
- `gss-15s.mp4`: 1920×1080, 30 fps render (no audio yet)
- `tools/export.js`: re-render the MP4 after editing (`node video-15s/tools/export.js`)

## Caveats to check before posting
- The 89% → 7% figure is Pythia-6.9B; perplexity rises there (19.46 → 29.15). The short cut doesn't mention it; the long cut should.
- "10–100× less compute" is the abstract's claim against optimization-based methods.
