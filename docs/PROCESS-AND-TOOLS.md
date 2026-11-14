# How the song 3 backdrop was made: process and tools

Recorded 2026-11-13 from the cloud Claude session that built "I Reminisce About Your Love". Saved here at Anthony's request.

## Process
1. Measured the recording: loudness over time, where notes begin, and the strongest entries, to find the verses and choruses.
2. Took the nine expressions word for word from https://heavenlymotherslove.org/en/checklist.
3. Planned a timeline that gives each part of the song a scene and places each expression at the start of a musical phrase.
4. Wrote a program that draws the sky, mountains, water, stars, sparks, petals and lettering by formula.
5. Tested with single still pictures and adjusted.
6. Rendered all 9,900 frames with three workers in about 33 minutes.
7. Checked the joins, that brightness follows the music, and that the sound was present.
8. Cut the stage, share and teaser versions.

## Tools
All free and open source, on a cloud computer with no graphics card:
- Python: the program.
- librosa: measuring the recording.
- GLSL shaders with ModernGL: drawing each frame.
- Mesa llvmpipe: graphics on an ordinary processor.
- Pillow: the words as pictures.
- The typefaces Cormorant Garamond and Jost.
- FFmpeg: joining frames into video and adding the music.

No stock footage, no video generator and no editing software were used.
