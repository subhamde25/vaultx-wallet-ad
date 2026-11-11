# Production notes

How the film was made, and what broke along the way.

## Pipeline

1. **Time** the voiceover word by word (`tools/transcribe.py`, faster-whisper) and map every beat to a word
   ([`VO_TIMELINE.md`](VO_TIMELINE.md)). The word times live in `tools/vx_common.py` as `W`.
2. **Design** in code: one design system (`tools/vx_common.py`) holds the palette, type, icons, scene table and
   the shared builders (background, headlines, cards, pills, phone frame, logo).
3. **Generate** the Fusion comps with Python (`tools/fu.py` writes the .comp format, `tools/kit.py` works in
   pixel space on top of it, `tools/scenes_{a,b,c}.py` build the nine scenes).
4. **Assemble** in DaVinci Resolve: a 1920×1080 30 fps timeline, `VaultX_Ad_Master`, with nine Fusion
   Composition clips on V1, each loaded from its .comp through the Resolve Console.
5. **Mix** in Python (`tools/mix_audio.py`), then lay the stems and the 73 SFX clips on named tracks A1–A8 in
   Resolve (`tools/make_resolve_audio.py`), so the timeline plays the same mix as the reference file.
6. **Render** each scene from Resolve as ProRes 422 HQ, in short segments.
7. **Encode** once to H.264 with the reference mix, and verify (`tools/finalize.py`).
8. **Export** the custom assets (`tools/export_assets.py`, `tools/make_ui_assets.py`, `tools/make_lua_assets.py`).

## Commands

Run from the repo root. `brandkit/` (not in the repo) must hold the client's `Logo.svg` and `voiceover.mp3`,
and the fonts in `assets/fonts/` must be installed. Needs Python 3.12 with numpy and Pillow, ffmpeg, and
DaVinci Resolve 21 (the free version is enough).

```sh
# audio
python -I tools/make_sfx.py            # six synthesised UI sounds → assets/audio/sfx_custom/
python -I tools/mix_audio.py           # VO clean-up, music edit, 73 SFX cues, stems and reference mix → build/audio/

# comps
python -I tools/scenes_a.py            # C01, C02 → build/comps/
python -I tools/scenes_b.py            # C03, C04, C05
python -I tools/scenes_c.py            # C06, C07, C08, C09
python -I tools/make_ui_assets.py      # UI_01 … UI_05 phone screens (900×1860)
python -I tools/export_assets.py       # icons, tokens, design tokens JSON, icon sheet → deliverables/assets/

# Resolve Console lines (paste into Workspace > Console, Lua)
python -I tools/make_lua_setup.py      # build/lua_setup.txt: helpers p, tl, LOADC, REIMP, RJ
python -I tools/make_resolve_audio.py  # build/resolve_audio.txt: bins and tracks A1 VO, A2 music, A3–A8 SFX
python -I tools/make_lua_assets.py     # build/lua_assets.txt: the Assets_UI_Screens timeline and its PNG renders

# master, from the per-scene renders in ~/vxs/chunks
python -I tools/finalize.py
```

In the Console, after pasting `build/lua_setup.txt`, a scene is reloaded with `REIMP({[7]=true})` and a
segment is queued with, for example,

```lua
RJ(747, 813, "C:/Users/<you>/vxs/chunks", "VX_C07a", "mov", "ProRes422HQ", 1920, 1080, false)
p:StartRendering()
```

`finalize.py` checks that every scene's pieces add up to its exact frame count before it encodes.

## Fusion, measured

The comp writer was calibrated against Fusion with two test comps (`tools/make_calib.py`,
`tools/make_calib2.py`). What they showed:

- **Rectangle masks:** width and height are fractions of their own axis; corner radius is
  `r / (min(w, h) / 2)`.
- **Ellipse masks:** width *and* height are fractions of the frame **width**. Treating height as a fraction of
  frame height made every circle twice as tall.
- **Polylines:** X is `(px − W/2) / W` and Y is `(H/2 − py) / H`, so Y is normalised by height. Getting this
  wrong squashed the logo. Stroke width is a fraction of the width.
- **Text+:** cap height is about `920 × Size` px at 1920 wide, centred on the middle of the cap. Pillow's width
  measurement runs 10–12% narrower than Text+ renders it, so widths get a margin.
- **Background** does not premultiply: RGB has to be scaled by alpha by hand, or soft glows render as solid
  blocks.
- **Write-on strokes** with the end at 0 still draw a dot, so their mask level is gated off until the stroke
  starts.
- **Keyframes** must be in time order. The writer collects any out-of-order key in `fu.WARN`, and every build
  keeps it at zero.

## Render cost

The first renders took 5–12 s a frame. What brought it to about 3–7 s:

- **Motion blur quality** is animated: full while a layer moves, one sample while it is still.
- **Frozen branches:** everything static goes through a `*_Static` TimeSpeed node at speed 0, so Fusion
  renders it once and reuses it.
- **Half-resolution phone:** the phone screen is authored at 900×1860 and rendered at half size, which is
  still sharper than it appears on screen.
- **Gradient backgrounds** instead of blurred shapes.

The machine has 7.5 GB of RAM, and a full-length render ran out of it and crashed Resolve more than once.
Each scene was rendered as its own job, and the heavy ones in pieces of about 66 frames (`VX_C07a`, `b`, `c`),
with Resolve restarted between batches when needed.

## Gotchas

- `InsertFusionCompositionIntoTimeline` adds a 150-frame clip and ripple-inserts it at the playhead. Moving
  the playhead right after `OpenPage` can fail silently, so check it before inserting. Clip lengths were then
  set on the Edit page (Ctrl+D, frames).
- `ExportCurrentFrameAsStill` was unreliable (Color page only, fails on paths with spaces). Single-frame render
  jobs are used for stills instead.
- A reopened project can carry old render jobs. Delete every job before `StartRendering`.
- After a crash and relaunch, a queue can sit at "Rendering 2%" while `IsRenderingInProgress()` returns false.
  `p:StopRendering()` then `p:StartRendering()` gets it moving.
- Paste Console paths with forward slashes; backslashes get eaten on the way in.

## Review pass

A senior-editor pass on the first master led to these changes:

- **Mix:** the music sat only about 4.6 dB under the voice. It now ducks 11 dB with a 600 ms release, its base
  level dropped, and five sound effects came down. The voice now sits about 10 dB above the music.
- **Store badges** are sized from their text, so "Google Play" fits inside its badge.
- **Security opening:** the shield starts drawing on the first frame, the dim is lighter and the encryption
  stream arrives earlier, so the scene no longer opens on an empty dark frame.
- **Security to modes:** a shorter, lighter dip, so the pace does not stall.
- **"Ahead" arrow:** rerouted around the headline and inside the safe area.
- **Master:** encoded at a constant 16 Mbps without a timecode track.

## Final checks

`deliverables/VaultX_Wallet_Ad_1920x1080_H264.mp4`: 1920×1080, 30 fps, 1350 frames (45.0 s), H.264 High at
16 Mbps, AAC 320 kbps, −15.7 LUFS integrated, −1.2 dBTP. Every join between rendered pieces was checked frame by
frame.
