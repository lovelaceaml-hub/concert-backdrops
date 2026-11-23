# Song kit

Full-length songs made the way **Almighty God Knows the Future** (Song 11) was made. Design and plan:
[SONG-KIT.md](../../project-docs/production-system/SONG-KIT.md). Song 11's delivered source is not changed; the
kit is a generalized copy of its shared parts plus the new Words of Mother's Love section.

    python tools/song_kit/prepare.py <song> [--audio file]       # engines + the song's music (unstretched)
    python tools/song_kit/render.py <song> --stills 4,13.5 --scale 0.5
    python tools/song_kit/render.py <song> --range 0 600 --out part.mp4

Cloud CPU only. A song is a folder `songs/<song>/` with `song_data.py` (the music, edit list, phrases,
expressions, looks; see `songs/kit_demo/song_data.py`) and its own sets (each with `OWNER`, `SHOTS`, `add(scene)`).

| Module | From Song 11 | What it does |
| --- | --- | --- |
| `modules/kit_film.py` | `s11_full2.py` core | timing, light budget, lights, comets, clouds, pillars, sky, the edit, camera, flashes, titles |
| `modules/kit_light.py` | `s11_light.py` | the song's looks, sun and rays |
| `modules/kit_words.py` | `s11_words.py` | phrases in the approved promo's word style |
| `kit_cards.py` | `s11_cards.py` signature | opening, corner signature with the song title, end card |
| `modules/kit_love.py` | new | the Words of Mother's Love: the arch, the expressions' words into their stars, acts (`ACTS`), answers (`ANSWERS`) |

Acts so far: `greeting` (two men, a slight bow each), `consideration` (helped up from one knee). Answers:
`peace_ring`. Add new ones in `kit_love.py`; every song can use them.
