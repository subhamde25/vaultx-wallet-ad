# Assets

Every file the film uses: where it came from, how it was treated and where it lands.

**Storage:** committed are the final master (`deliverables/*.mp4`, Git LFS), the custom assets, the generated
Fusion comps, the music, every sound effect used, the fonts and the tools that make all of it. The client's
brand kit (logo files, script, voiceover), the built audio stems, the per-scene ProRes renders and the Resolve
project archive are not.

## 1. Brand kit (supplied, not committed)

| File | Used as |
|---|---|
| `brandkit/Logo.svg` | Drawn into the comps as Fusion polyline masks, path for path and unmodified (`vx_common.logo`). Used in C02, the phone splash and the end card |
| `brandkit/voiceover.mp3` | The voiceover, 43.05 s. Cleaned and placed at 0.2 s by `tools/mix_audio.py` (A1) |
| `brandkit/script.txt` | Read against the voiceover. Its line "See where your money is going…" is not spoken, so it has no scene |
| `Logo_Image_*.png`, `Logoai.ai` | Not used; the SVG is the master |

The logo's wordmark reads "Valut.X" while the script and voiceover say "VaultX". It is used exactly as
supplied; swapping it means replacing `brandkit/Logo.svg` and regenerating the comps.

## 2. Type

Inter and Inter Display by Rasmus Andersson (SIL Open Font License 1.1, licence in
[`assets/fonts/`](../assets/fonts/)). The comp generator measures text with these files, so they are needed to
rebuild, and they must be installed for Resolve to render the comps.

## 3. Music

[`assets/audio/music/`](../assets/audio/music/): "Innovation Needed" by ZoneX, from Jamendo, licensed
[CC BY 3.0](https://creativecommons.org/licenses/by/3.0/). Credit it wherever the film is shown. The edit
(start point, ducking, button ending) is made by `tools/mix_audio.py`, see [`BREAKDOWN.md`](../BREAKDOWN.md#sound).

## 4. Sound effects

| Folder | What | Source |
|---|---|---|
| [`assets/audio/sfx_used/`](../assets/audio/sfx_used/) | The 51 sounds the cue sheet uses, copied here by the mix script | The author's own sound libraries from earlier projects, plus the six below |
| [`assets/audio/sfx_custom/`](../assets/audio/sfx_custom/) | Scan sweep, three UI ticks, two UI pops | Synthesised from scratch by `tools/make_sfx.py` |

No sound is used more than twice; `tools/mix_audio.py` asserts it before it mixes anything.

## 5. Fusion comps

[`build/comps/`](../build/comps/), all written by the Python tools (nothing hand-placed):

| Comp | Made by |
|---|---|
| `C01_Hook_Crypto_Moves_Fast`, `C02_Logo_Reveal_Value_Prop` | `tools/scenes_a.py` |
| `C03_Instant_Transactions_Swaps`, `C04_Portfolio_Chart`, `C05_Price_Alerts_Trends` | `tools/scenes_b.py` |
| `C06_Dashboard_Insights`, `C07_Security_Encryption_Biometric`, `C08_Investing_Trading_Holding`, `C09_EndCard_CTA` | `tools/scenes_c.py` |
| `UI_01_Send` … `UI_05_Splash` (900×1860) | `tools/make_ui_assets.py` |

Each element is built in its own labelled column (an underlay such as `HL_Instant_Transactions`, `Chart_Line`,
`Card_Allocation` or `Fingerprint`). Inside a column the masks feed the fills, then the transforms; finished
elements merge left to right along an `OUTPUT SPINE` row, then go through `CAMERA`, `GRAIN_Overlay` and
`MediaOut1`.

## 6. Custom assets (deliverables)

[`deliverables/assets/`](../deliverables/assets/), the "custom assets created" part of the brief:

| File | What | Made by |
|---|---|---|
| `icons/vx_icon_*.svg` | 24 icons on a 24-unit grid in the accent green: 21 with a 2-unit round stroke, 3 solid (bolt, spark, play). Send, swap, wallet, shield, lock, chart, bell and more | `tools/export_assets.py`, from the same definitions the comps draw (`vx_common.ICONS`) |
| `tokens/vx_token_{BTC,ETH,SOL}.svg` | Token badges used in the UI and the security orbit | `tools/export_assets.py` |
| `ui_screens/UI_01_Send.png` … `UI_05_Splash.png` | Five phone screens at 900×1860 | The `UI_*` comps, rendered from the `Assets_UI_Screens` timeline in Resolve (`tools/make_lua_assets.py`) |
| `vaultx_ui_screens_overview.png` | The five screens side by side | Tiled from the five PNGs at half size with Pillow |
| `vaultx_icons_contact_sheet.png` | The icon set on one sheet | `tools/export_assets.py` |
| `vaultx_design_tokens.json` | Colours, type styles, radii and motion settings | `tools/export_assets.py` |

## 7. Not committed

| What | Where it lives | Why |
|---|---|---|
| Built audio: VO, music edit, SFX bus, 73 SFX clips, reference mix | `build/audio/` | Rebuilt by `tools/mix_audio.py`; it contains the client's voiceover |
| Per-scene ProRes 422 HQ renders | `~/vxs/chunks/` | About 615 MB of intermediates; rebuilt by rendering the timeline |
| The Resolve project (`VaultX_Wallet_Ad.dra`) | Delivered to the client as a zip | It carries the client's voiceover and logo |
| Review stills, Console scratch scripts, calibration comps | `build/` | Working files |
