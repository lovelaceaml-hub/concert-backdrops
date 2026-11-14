# Concert Backdrops: instructions for every AI

All AIs (Claude, Codex, Gemini, helpers) work from this one folder. Anthony, 2026-11-13: "Make sure that this is all being recorded, communicated, and stored in the same folder so that all the AIs can work together on the same project". Reorganized 2026-11-13 by the coordinating Claude Code session; every earlier instruction is kept below.

## Read first, in this order
1. DESIGN-SYSTEM.md: the message, the number one priority, the official concert facts, the rules, and the decisions waiting for Anthony.
2. README.md: what is where.
3. Your track's status page: VIDEO-HANDOFF.md (videos) or SHARED-HANDOFF.txt and production-status.json (sample pictures).
4. The last lines of production-log.jsonl.

## For everyone
- The message (Anthony, 2026-11-13): "Make sure each of the chats and the whole project understand that the mother's words of love that bring peace are the main theme and the main importance of this concert. That is the message we are trying to get across." Every picture, video, document and decision here serves it.
- Number one priority (Anthony, 2026-11-13): study the Mother's Love campaign thoroughly first, then make everything magnificent, glorious and heavenly. Full quote in DESIGN-SYSTEM.md section 2.
- Helpers (Anthony, 2026-11-13): "Each thread can use as many Haiku agents as necessary. No limit in the cloud." Use them for research, reading the campaign, checking documents and measuring recordings. Heavy work (rendering, big media jobs) runs in the cloud, never on the Mac.
- Add a line to production-log.jsonl for every change. Do not delete anything. Do not edit the MP3s, the Lyrics doc or the Visual Plan doc. Do not copy lyrics into new files. No em dash or en dash anywhere. No paid services without Anthony's OK.
- Shell commands on the Mac run with nice -n 19; if the 1-minute load is above 50, pause and say so.
- One active writer per area at a time; do not start other AI sessions or duplicate generation without coordination.

## Two tracks, separate areas
- Video track (Claude Code coordinator and the 11 song design sessions): Engine/, Designs/, Storyboards/, Videos/, VIDEO-HANDOFF.md. Engine code also lives in the private GitHub repo lovelaceaml-hub/concert-backdrops for cloud rendering.
- Samples track (Codex): Samples/, SHARED-HANDOFF.txt, production-status.json, generation-archive.json, generation-specifications.json, FILE-LIST.txt, Generation Archive/.
- Each track never writes to the other's area. Shared files (this one, DESIGN-SYSTEM.md, README.md, production-log.jsonl, Reference/) are open to both; append or edit carefully and log it.

## Samples track rules (written by Codex, kept as written)
Task: 30 individual PNG sample backdrops, not video production. Shot list owns scene, phrase, color, and exact filename. Anthony explicitly superseded its photoreal style: match his glowing scenic reference. People must be artistic outlines or forms of light, mist, ribbons, or particles, never actual-looking people. Sparkles are optional. No realistic faces or skin. Heavenly Mother only rear-view outline or hands.
Reference: Design Reference.png in this folder. Bottom third calm and uncluttered. Text only where shot list specifies a phrase, exact wording, elegant thin serif in upper third with specified color and faint glow. No titles, extra text, logos or watermarks. Preserve all existing source assets.
Native image generation authorized. One generation at a time. Inspect every output before saving. Redo once for defect, save best and log any remaining issue.
Samples contains final selected images only, exact shot list names. Update shared records after each batch. Check production-status.json and live Samples files before resuming. Earlier versions remain in generator libraries; don't delete them.
Note from the video track: the shot list's shortened expression wording and older style are superseded by DESIGN-SYSTEM.md (full campaign wording, label above the phrase). See REVIEW-Samples-2026-11-13.md and REVIEW-Claude-Designs-2026-11-13.txt before any new generation.
