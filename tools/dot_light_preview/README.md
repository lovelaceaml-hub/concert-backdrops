# The Light We Share

Independent experimental light-only concert promo. The full draft is 62 seconds at native 60 fps, rendered at 960x540 for review. It is not a final 1080p production render or an approved replacement for the masterpiece.

## Creative treatment

- 0 to 8 seconds: the approved opening lockup holds for seven full seconds over a gold lake. A bright drop sends ripples through a nine-petal light garden.
- 8 to 44 seconds: nine exact expressions from PW.EXPRESSIONS, each with a 3.1-second reading hold. Paired lights meet, yield, shelter, listen, rise and celebrate below the words. There is no human cast, so natural human acting and the approved casting have not been delivered in this abstract alternative.
- 44 to 54 seconds: the existing engine Earth and logo assets form the finale. Nine subtle campaign symbols orbit the globe.
- 54.9 to 62 seconds: the official-style card stays readable. A process-local 0.8 percent eased push-in settles for the last second. The picture never fades to black.

All added source lives here. Existing engine, sky, fonts, exact wording, logo and globe assets are reused. The light choreography, layout/timeline and seven-recording edit are independent. No protected file is edited.

## Full render

Install the normal engine dependencies and fonts. Put the seven authorized original recordings, not just their 60-second promo clips, into work/dot-music/sources/sNN.mp3. Source 03 must contain its original ending. Never commit source recordings, generated audio, frames, videos, features or caches.

```sh
python tools/dot_light_preview/build_score.py
ffmpeg -v error -y -i work/dot-music/The-Light-We-Share-score.wav -ac 1 -ar 22050 work/dot-music/analysis.wav
NUMBA_CACHE_DIR="$PWD/work/dot-music/numba" python engine/analyze.py work/dot-music/analysis.wav work/dot-music/features.npz
FEATURES="$PWD/work/dot-music/features.npz" python tools/dot_light_preview/render_full.py --range 0 3720 --name silent
ffmpeg -v error -y -i work/dot-light-full/silent.mp4 -i work/dot-music/The-Light-We-Share-score.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -t 62 -movflags +faststart work/dot-light-full/The-Light-We-Share.mp4
python tools/dot_light_preview/verify_full.py work/dot-light-full/The-Light-We-Share.mp4
```

DOT_ENGINE_ROOT, DOT_PREVIEW_OUT and DOT_MUSIC_WORK may select isolated engine, output and music work folders. The renderer registers a song module in memory, not under engine/songs. Split ranges are half-open and must cover [0,3720) once with fixed source and features.

The initial eight-second render_preview.py study remains for history. It has a paler scene and only reused soundtrack, unlike the full draft's new score. Its source and outputs should not be confused with the full film.

## Music and limits

Seven-recording order: 01, 04, 08, 05, 09, 07, 03. The first two seconds are silent, then a 1.5-second fade. Six equal-power 2.5-second blends start at 10, 18, 26, 34, 42 and 50 seconds. The original recorded tail from source 03 maps to approximately 55.8 to 60.8 seconds, followed by quiet. No AI music or synthetic reverb.

Beat positions, modest pitch-preserving tempo adjustments and local gain riding are algorithmically selected. A compound-pulse interpretation is assumed above 145 detected bpm. Phrase continuity, meter, tonal relationships and gain pumping have not been auditioned. The score is a listening draft, not musically approved.

Before full rendering, six raw PNG probes in sequential and reversed fresh processes matched byte for byte, including the 31-second split. All nine expression stills, Earth and card were reviewed at draft resolution. A local title adapter clears opening dust by eight seconds so it cannot cross the first expression. Encoded-file results and remaining limitations belong in VALIDATION.md after completion.

No paid GitHub Render workflow, protected-file edit, media commit or merge. Anthony decides; coordinator review remains pending.
