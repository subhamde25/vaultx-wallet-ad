# Breakdown

## Creative approach

A fintech launch film in the style of a premium app keynote. The canvas is a near-black green with one soft
radial glow and a faint grid, there is one lime accent (the logo's green, #91C950), and everything else is white
and grey. The phone is the anchor: features pop out of it as cards and float beside it, and the camera pushes
gently between beats instead of cutting. Every visual beat is pinned to a word in the voiceover (timings in
[`docs/VO_TIMELINE.md`](docs/VO_TIMELINE.md)), so callouts land on "manage", "grow", "protect", "encryption",
"biometric", "investing", "trading" and "holding". The music was edited so its breakdown sits under the security
section and the drop lands on "VaultX keeps you ahead".

The references studied (prompt-motion, originkit, templens and YouTube fintech promos, ideas only, nothing
copied) are in [`docs/STYLE_RESEARCH.md`](docs/STYLE_RESEARCH.md).

## Beat sheet

Times are in the final cut. The voiceover starts at 0.2 s. Frames are at 30 fps.

| Time | Scene (comp) | Voiceover | Picture |
|---|---|---|---|
| 0.0–3.5 | `C01_Hook_Crypto_Moves_Fast` (0–104) | "Crypto moves fast. Your wallet should too." | Kinetic type with speed streaks and a market ticker; an underline draws under "too." |
| 3.5–8.9 | `C02_Logo_Reveal_Value_Prop` (105–266) | "Meet VaultX Wallet, the smarter way to manage, grow, and protect your digital assets." | The supplied logo builds piece by piece, then Manage / Grow / Protect chips pop on their words |
| 8.9–12.7 | `C03_Instant_Transactions_Swaps` (267–380) | "Instant transactions. Lightning-fast swaps." | Phone UI: send, confirm with a success ring, then a BTC→ETH swap; toasts pop out of the phone |
| 12.7–16.9 | `C04_Portfolio_Chart` (381–506) | "Real-time portfolio tracking with interactive performance charts." | **Line chart** draws on, the balance counts up to $48,256.80, a cursor scrubs the line with a tooltip |
| 16.9–20.2 | `C05_Price_Alerts_Trends` (507–605) | "Set price alerts. Analyze trends." | Alert toggle and notification, then a weekly **bar chart** with a trend line |
| 20.2–24.9 | `C06_Dashboard_Insights` (606–746) | "Make confident decisions with powerful insights built right into your dashboard." | Dashboard phone with an allocation donut, AI insight, risk level and top-mover cards around it |
| 24.9–31.6 | `C07_Security_Encryption_Biometric` (747–947) | "And with bank-level encryption and biometric security, your assets stay protected every step of the way." | **Shield** draws on and the lock closes over an encryption stream, a fingerprint traces on under a scan line, then tokens orbit the locked shield |
| 31.6–38.2 | `C08_Investing_Trading_Holding` (948–1145) | "Whether you're investing, trading, or holding long-term — VaultX keeps you ahead." | Three mode cards land on their words, then push away for the headline and a rising arrow on the music drop |
| 38.2–45.0 | `C09_EndCard_CTA` (1146–1349) | "Download VaultX Wallet today. Own your crypto journey." | App splash with App Store and Google Play badges, then the **logo end screen** with tagline and CTA pill |

## Motion rules

- **Easing:** every key is a Bézier spline with a CSS-style ease (out for entrances, in for exits, in-out for
  moves). The only linear motion is deliberate constant drift: the ticker, the token orbit and the background.
- **Motion blur:** on every moving layer, 180° shutter. Its quality drops to one sample whenever the layer is
  still, which made renders several times faster without changing a moving frame.
- **Kinetic type:** each headline line sits in its own tight clip and words rise into it 1.55 cap heights,
  staggered to the voiceover. Accent words switch to green.
- **Transitions:** a slow camera push in every scene, eased hand-overs between scenes, and two short dips to
  dark around the security scene.

## Design system

| Token | Value |
|---|---|
| Background | #0B0E0B with a radial glow, faint grid and vignette |
| Card | #1E231E, 1 px border #2C332C, 24–32 px corners |
| Accent | #91C950 (from the logo) |
| Brand charcoal | #3E433E (from the logo) |
| Negative | #E5484D, only on falling values |
| Text | #FFFFFF, labels #8A938A |
| Type | Inter Display and Inter (Bold, SemiBold, Medium) |

The full set, including the 24 stroke icons, is exported in [`deliverables/assets/`](deliverables/assets/).

## Sound

- **Voiceover:** as supplied, placed at 0.2 s, with a 75 Hz high-pass, light EQ and compression.
- **Music:** "Innovation Needed" by ZoneX (Jamendo, CC BY 3.0), started 26.82 s into the track so its breakdown
  sits under the security scene and the drop lands on "VaultX keeps you ahead" at 36.5 s. It ends on a button
  at 43.72 s with a short reverb tail. It ducks 11 dB under the voice (40 ms attack, 600 ms release), so the
  voice sits about 10 dB above it.
- **Sound effects:** 73 cues from 51 sounds. No sound is used more than twice (the mix script asserts it).
  Each one is levelled by the loudness of its body rather than its peak, then soft-limited.
- **Mix:** about −15.6 LUFS integrated, −1.2 dBTP.

### Cue sheet

| # | Time (s) | Scene | Sound | Marks |
|---|---|---|---|---|
| 1 | 0.07 | C01 | `subhit.mp3` | open: low hit |
| 2 | 0.80 | C01 | `low_flyby.mp3` | speed streaks |
| 3 | 1.43 | C01 | `silk_swipe.mp3` | line 1 out |
| 4 | 3.03 | C01 | `pen_sweep.mp3` | underline "too." |
| 5 | 3.13 | C01 | `snap_whip.mp3` | hook whip out |
| 6 | 3.50 | C02 | `bass_bloom.mp3` | logo burst ring |
| 7 | 4.03 | C02 | `brand-twinkle.mp3` | logo mark dots |
| 8 | 5.07 | C02 | `air_suck.mp3` | logo moves up |
| 9 | 5.93 | C02 | `soft_pop.mp3` | chip Manage |
| 10 | 6.53 | C02 | `pop.mp3` | chip Grow |
| 11 | 7.23 | C02 | `felt_tap.mp3` | chip Protect |
| 12 | 8.43 | C02 | `dive-whoosh.mp3` | drop into phone |
| 13 | 8.90 | C03 | `slider_glide.mp3` | phone rises |
| 14 | 8.97 | C03 | `data_morph.mp3` | amount count |
| 15 | 9.80 | C03 | `click-soft.mp3` | tap Send |
| 16 | 10.20 | C03 | `chime.mp3` | sent |
| 17 | 10.47 | C03 | `blip_two.mp3` | toast confirmed |
| 18 | 10.83 | C03 | `push-whoosh.mp3` | screen to swap |
| 19 | 11.77 | C03 | `reverse_snap.mp3` | swap arrows rotate |
| 20 | 12.13 | C03 | `light-shimmer.mp3` | swap instantly |
| 21 | 12.20 | C03 | `glass-ting.mp3` | toast swapped |
| 22 | 12.23 | C03 | `swoosh-air.mp3` | push to chart |
| 23 | 12.97 | C04 | `data_morph.mp3` | balance count |
| 24 | 13.43 | C04 | `line_glide.mp3` | chart draws |
| 25 | 14.17 | C04 | `key-press.mp3` | tab 1M |
| 26 | 15.13 | C04 | `felt_tap.mp3` | cursor lands |
| 27 | 15.40 | C04 | `slider_glide.mp3` | scrub drag |
| 28 | 16.43 | C04 | `zoom_fly.mp3` | zoom through |
| 29 | 17.07 | C05 | `soft_pop.mp3` | alert card |
| 30 | 17.43 | C05 | `latch.mp3` | toggle on |
| 31 | 17.80 | C05 | `kalimba.mp3` | notification |
| 32 | 18.07 | C05 | `marimba.mp3` | bell shake |
| 33 | 18.93 | C05 | `rise_sweep.mp3` | bars grow |
| 34 | 19.73 | C05 | `pop.mp3` | +8.6% pill |
| 35 | 19.90 | C05 | `air_suck.mp3` | trend exit |
| 36 | 20.20 | C06 | `low_flyby.mp3` | dashboard phone |
| 37 | 21.10 | C06 | `glass_bloom.mp3` | allocation card |
| 38 | 21.30 | C06 | `shutter_roll.mp3` | donut segments |
| 39 | 22.37 | C06 | `warm_shimmer.mp3` | AI insight card |
| 40 | 22.63 | C06 | `blip_two.mp3` | risk card |
| 41 | 22.90 | C06 | `wood_knock.mp3` | top mover card |
| 42 | 24.10 | C06 | `rise-into-drop.mp3` | push into dashboard |
| 43 | 24.47 | C06 | `dark_sweep.mp3` | darken to security |
| 44 | 25.00 | C07 | `sonar_bloom.mp3` | shield draws |
| 45 | 25.57 | C07 | `tom_thud.mp3` | lock appears |
| 46 | 25.43 | C07 | `typing.mp3` | encryption stream |
| 47 | 26.10 | C07 | `latch.mp3` | shackle locks |
| 48 | 26.23 | C07 | `impact-bass-1.mp3` | lock flash |
| 49 | 26.83 | C07 | `silk_swipe.mp3` | shield slides left |
| 50 | 27.23 | C07 | `scan_sweep.wav` | fingerprint scan |
| 51 | 28.37 | C07 | `chime.mp3` | verified |
| 52 | 28.67 | C07 | `reverse_snap.mp3` | fingerprint into shield |
| 53 | 28.87 | C07 | `flood_shimmer.mp3` | coins orbit |
| 54 | 29.13 | C07 | `bass_bloom.mp3` | pulse rings |
| 55 | 31.23 | C07 | `iris-whoosh.mp3` | security out |
| 56 | 32.50 | C08 | `panel-flick.mp3` | card investing in |
| 57 | 32.70 | C08 | `ui_tick_a.wav` | investing active |
| 58 | 33.43 | C08 | `panel-paper1.mp3` | card trading in |
| 59 | 33.63 | C08 | `ui_tick_b.wav` | trading active |
| 60 | 34.20 | C08 | `panel-paper3.mp3` | card holding in |
| 61 | 34.40 | C08 | `ui_tick_c.wav` | holding active |
| 62 | 36.17 | C08 | `dive-whoosh.mp3` | cards drop |
| 63 | 36.50 | C08 | `impact-bass-1.mp3` | drop: keeps you ahead |
| 64 | 37.00 | C08 | `rise_sweep.mp3` | arrow draws |
| 65 | 37.73 | C08 | `snap_whip.mp3` | arrow head |
| 66 | 37.87 | C08 | `swoosh-air.mp3` | ahead out |
| 67 | 38.20 | C09 | `zoom_fly.mp3` | end phone rises |
| 68 | 40.33 | C09 | `ui_pop_c.wav` | App Store badge |
| 69 | 40.47 | C09 | `ui_pop_d.wav` | Google Play badge |
| 70 | 40.93 | C09 | `rise-into-logo.mp3` | into final lockup |
| 71 | 41.70 | C09 | `brand-twinkle.mp3` | final logo mark |
| 72 | 42.73 | C09 | `glass_bloom.mp3` | CTA |
| 73 | 43.73 | C09 | `subhit.mp3` | button ending |

73 cues, 51 different sounds; the most any sound is used is 2 times.
