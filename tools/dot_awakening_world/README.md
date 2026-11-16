# A loving word awakens a world

A complete independent 62-second procedural 3D concert film draft, made locally in Python and ModernGL. It is not the parked lake study and is not a pan across a generated picture.

## Reproduce

Use the engine assets and fonts at commit bfac3adbc26c5ddcba0218ed7ce0efb6630c500d on master/words-that-bring-peace. Install numpy, Pillow and moderngl, with ffmpeg and EGL available. Set DOT_ENGINE_ROOT to the checkout and DOT_FILM_OUT to a writable output folder. Run `python film.py --range 0 3720 --name complete-silent`.

Default output is native 960x540 at 60 fps. `DOT_RES=1080p` renders the 3D scene natively at 1920x1080; cached text plates are scaled from their 540p layout, so this is not native 1080p typography. It is an optional slower export, not the delivered review's claimed resolution.

Build the independent seven-source score using build_score.py and the authorized original full recordings in sources/s01.mp3, s04.mp3, s08.mp3, s05.mp3, s09.mp3, s07.mp3 and s03.mp3. Do not substitute the 60-second promotional clips: the ending uses the full original source 03's recorded decay. See SCORE.md for the musical caveats.

Mux without changing the video frames:

```sh
ffmpeg -i complete-silent.mp4 -i The-Light-We-Share-score.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -t 62 -movflags +faststart The-Light-Awakens-World-62s.mp4
```

All generated media, original recordings, frames and caches stay out of git. No GitHub Render workflow is needed or dispatched.

## Interpretation

The drop touches a winding river; a traveling wave awakens spatial blossoms. The camera travels through a rose valley, passing nine light gestures and exact source expression phrases. A branching light tree grows and a textured spherical world rises, followed by a campaign-colored end card. The geometry, ray-traced terrain, water reflections, particles, camera and Earth are functions of time. No generated still is used as the background. Camera changes at 7.5 and 44 seconds act as shot changes rather than fully seamless camera splines.

The opening is readable from frame zero through seven seconds. Each expression gets a four-second section, including short fades. The end card is fully visible from 54.8 seconds through the last frame and gently pushes in before easing to stillness. The score starts with two seconds of quiet and ends with a real recorded decay.

## Departures and limits

This is a complete creative draft, not an approved production or a claim to feature-film realism. Abstract lights replace the requested human acting; there are no anatomical faces, hands or embraces. Blossoms are spatial light sprites rather than modeled petals. The nine colored finale lights are not all nine official pictograms. The world transitions to the card rather than morphing into the logo. The compact signature omits the additional HEALING CONCERT / LAS VEGAS line, though the opening includes it. The landscape is deliberately stylized. There is no temporal motion blur. The music's level and join measurements do not replace listening approval.

The authoring changes are confined to this new tools directory. Protected engine, song, audio and workflow files are not changed. Anthony decides whether to merge.
