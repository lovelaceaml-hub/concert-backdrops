# The Light We Share: opening study

Independent eight-second visual concept, not a finished 62-second film. Newly authored gold light petals unfurl over cream water with a slowly drifting camera. The existing engine supplies the sky, logo, fonts and approved TITLES lockup. No people or all-nine-expression sequence appear in this short opening study.

Native 60 fps at 960x540. The opening title stays fully readable throughout. Generated video, frames, audio and caches belong under work/ and must not be committed. This branch changes no protected files and invokes no hosted workflow.

## Reproduce locally

Install the normal engine dependencies and fonts. Supply existing analyzed features from an authorized concert score. Run from the repository root:

```sh
FEATURES="$PWD/work/master_peace/features.npz" python tools/dot_light_preview/render_preview.py
ffmpeg -v error -y -i audio/promo/concert-medley-leadin.mp3 -t 8 -af 'afade=t=out:st=6:d=2' -c:a pcm_s24le work/dot-light-preview/preview-score.wav
ffmpeg -v error -y -i work/dot-light-preview/The-Light-We-Share-silent.mp4 -i work/dot-light-preview/preview-score.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -t 8 -movflags +faststart work/dot-light-preview/The-Light-We-Share-preview.mp4
```

DOT_ENGINE_ROOT and DOT_PREVIEW_OUT can point to an isolated engine snapshot and output folder. The entry point installs its song module in process memory and never writes under engine/songs.

## Scope and limitations

Music is a reused concert medley excerpt with a two-second preview fade-out, not a new seven-song arrangement and not AI-generated music. The tested cloud snapshot's source audio was extracted from the existing v7 test share; reproduction with the production master will not be byte-identical audio. The visual concept uses newly rendered pixels, not existing video footage.

This modest opening study is a concept to evaluate, not an assertion that the requested full film/music work is complete. No full-resolution production review, all-scene review or listening audition is claimed. Claude coordinator review and Anthony's creative decision are still pending. Do not merge automatically.
