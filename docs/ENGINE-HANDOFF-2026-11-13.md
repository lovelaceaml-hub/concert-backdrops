# Concert backdrops: how to continue

Concert: "The Words of Mother's Love That Bring Peace". Theme: the nine Words of Mother's Love
(wording from https://heavenlymotherslove.org/en/checklist, used word for word).
Status on 2026-11-13: song 3, "I Reminisce About Your Love", is built. The other 10 songs are not started.

## What exists
- Engine code (this zip): song.py (timeline, palettes, the nine expressions and their times),
  text.py (words as pictures), shaders.py (the drawing programs), render.py (renders frames to video),
  analyze.py and analyze2.py (measure the recording), sheet.py (contact sheets for checking).
- Delivered to Anthony in chat: a first-half sample with the opening title (2 min 11 sec),
  and an earlier full set without the title (stage version silent 5 min 30, share video with music, 77 second teaser).
- Not done: the full-length render with the opening title. Anthony has not yet approved the sample.

## Anthony's decisions so far
- One song first, then the rest. 1080p widescreen, 30 frames a second.
- A few words at key moments: each of the nine expressions appears once, then becomes one of nine lights.
- Opening: song title large with the concert title beneath, 0:00 to 0:05, then it rests small in the top left corner.
- Studio recordings preferred. Lyrics come from the WAPLE app (members only, on his own device).
- "(or root)" is kept in the Encouragement line until he says otherwise.

## Open questions for Anthony
- The set list says 5:13 for this song; the recording is 4:11. How does the live version differ?
- Approval of the sample, then render the full version.

## Method for each song
1. Set up a cloud machine: pip install numpy scipy librosa moderngl pillow fonttools brotli;
   apt-get update and install libegl1 libgles2 (software graphics); ffmpeg is needed.
   Fonts: npm pack @fontsource/cormorant-garamond and @fontsource/jost, convert the latin woff2 files to ttf
   with fontTools into a fonts folder beside the code folder.
2. Convert the recording to mono 22050 Hz wav and run analyze.py, then analyze2.py. Read off: where the voice enters,
   where each chorus starts (the loudness jump), the drops, the strongest entries, the last sounding moment.
3. In song.py set the landmarks (VOICE_IN, CHORUS1, CHORUS2 and so on), MUSIC_END, TOTAL, the palette keys,
   the tracks, and the PHRASES times: each expression starts forming at a phrase start and its light is lit
   on a strong entry. Set CREDIT to the song title and concert title.
4. Check stills first (python3 render.py --stills 5,30,60 ...), look at them, fix, repeat.
5. Full render: three workers with --range over thirds of the frames, join with ffmpeg concat (copy),
   then encode: stage version silent, share version with the music, short teaser. About 6 minutes of
   rendering per minute of video.
6. Check the joins, check the music is present, look at frames from the finished files, then send the files in chat.

## Next steps
1. Get the 11 recordings and the lyrics (Anthony drops them in chat, or a session on his Mac puts them in the
   Google Drive folder "Concert Backdrops - Songs" with the doc "Concert Backdrops - Lyrics").
2. With lyrics, time the words on screen to what is sung.
3. Give each song its own scene and palette while keeping the shared look (title card, corner title, nine lights where they fit).
