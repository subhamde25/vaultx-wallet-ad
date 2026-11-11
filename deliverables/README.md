# VaultX Wallet — 45s Product Motion Ad

**Deliverables**

| Folder / file | What it is |
| --- | --- |
| `VaultX_Wallet_Ad_1920x1080_H264.mp4` | Final exported video. 1920×1080, 30 fps, H.264 High at 16 Mbps, AAC 320 kbps, 45.0 s, about -15.7 LUFS. The scenes were rendered from DaVinci Resolve as ProRes 422 HQ, then encoded once to H.264 with the timeline's audio mix |
| `Project/VaultX_Wallet_Ad_Resolve_Archive.zip` | Project file, collected. Unzip to get `VaultX_Wallet_Ad.dra`, the Resolve project archive with all media included (restore with *File > Restore Project Archive*) |
| `Project/Fonts/` | Inter and Inter Display (SIL Open Font License). Install before opening the project |
| `Assets/` | Custom assets: 24 stroke icons (SVG), token badges (SVG), five UI screens at 900×1860 (PNG) plus an overview, design tokens (JSON), icon sheet |

**Opening the project**

1. Install the fonts in `Project/Fonts`.
2. Open the project in DaVinci Resolve 21 (free or Studio).
3. Timeline `VaultX_Ad_Master` has nine Fusion Composition clips on V1. Each is named after its scene, `C01_Hook_Crypto_Moves_Fast` to `C09_EndCard_CTA`. Open any clip on the Fusion page to see its comp.
4. Timeline `Assets_UI_Screens` (900×1860) holds the five phone screens used for the UI exports.

**How the comps are organised**

Every element is built in its own labelled column (underlay), for example `HL_Instant_Transactions`, `Chart_Line`, `Card_Allocation` or `Fingerprint`. Inside a column the masks feed the fills, then the transforms. Finished elements merge left to right along an **OUTPUT SPINE** row, then go through `CAMERA` (a slow push), `GRAIN_Overlay` and `MediaOut1`.

- All keyframes are eased Bézier splines. There are no linear moves except deliberate constant drifts such as the ticker and the background.
- Motion blur (180° shutter) is on for every moving layer. Its quality drops to 1 sample while a layer is still, which keeps renders fast.
- Static branches go through a `*_Static` TimeSpeed node at speed 0, so Fusion renders them once and reuses them.

**Audio tracks**

| Track | Content |
| --- | --- |
| A1 | Voiceover as provided (light EQ and compression, starts at 0.2 s) |
| A2 | Music edit: the breakdown sits under the security section, the drop lands on "VaultX keeps you ahead", and it ends on a button with a short tail |
| A3–A8 | 73 SFX cues from 51 different sounds. No sound is used more than twice |

**Scenes and voiceover sync**

| Scene | Time | Voiceover | Visual |
| --- | --- | --- | --- |
| C01 | 0.0–3.5 s | "Crypto moves fast. Your wallet should too." | Kinetic type, market ticker, speed streaks |
| C02 | 3.5–8.9 s | "Meet VaultX Wallet… manage, grow, and protect…" | Logo build, Manage / Grow / Protect chips |
| C03 | 8.9–12.7 s | "Instant transactions. Lightning-fast swaps." | Phone UI: send, then confirm, then swap, with pop-out toasts |
| C04 | 12.7–16.9 s | "Real-time portfolio tracking with interactive performance charts." | **Line chart** that draws on, live balance counter, scrub tooltip |
| C05 | 16.9–20.2 s | "Set price alerts. Analyze trends." | Alert toggle and notification, **bar chart** with trend line |
| C06 | 20.2–24.9 s | "Make confident decisions… built right into your dashboard." | Dashboard phone, allocation donut, AI insight, risk and top-mover cards |
| C07 | 24.9–31.6 s | "Bank-level encryption and biometric security…" | **Shield and lock**, encryption stream, fingerprint scan, protected orbit |
| C08 | 31.6–38.2 s | "Investing, trading, or holding long-term — VaultX keeps you ahead." | Three mode cards, rising "ahead" arrow |
| C09 | 38.2–45.0 s | "Download VaultX Wallet today. Own your crypto journey." | App splash, store badges, **logo end screen with CTA** |

**Notes**

- **Logo:** the supplied logo is used exactly as delivered. Its wordmark reads "Valut.X", while the script and voiceover say "VaultX". It can be swapped in one place, the `LOGO_*` sections.
- **Script vs voiceover:** the script line "See where your money is going — and where it's growing." is not in the voiceover, so it has no matching scene.
- **Data:** all numbers, balances and charts are illustrative.

**Credits**

- **Music:** "Innovation Needed" by ZoneX (Jamendo), licensed CC BY 3.0 (creativecommons.org/licenses/by/3.0).
- **Typeface:** Inter / Inter Display by Rasmus Andersson (SIL OFL 1.1).
- **Icons, UI, charts and animation:** custom made for this project.
