# XGP-save-extractor
Python script to extract/backup savefiles out of Xbox Game Pass for PC games.

When run, the script produces a ZIP file for each supported game save found in the system.

In most cases the files in the ZIP can be copied to the save directory of the Steam/Epic version of the game. To find out the save file location, check [PCGamingWiki](https://www.pcgamingwiki.com/).

## 🎮 Abiotic Factor Support

**Special support for Abiotic Factor** with Xbox → Steam conversion! See **[ABIOTIC_FACTOR_GUIDE.md](ABIOTIC_FACTOR_GUIDE.md)** for:
- Extracting Xbox Game Pass saves (bundled archive format)
- Converting to Steam dedicated server format
- Complete 2-step workflow with auto-detection

> [!IMPORTANT]
> If you want the script to support another game, please open an issue [here](https://github.com/Z1ni/XGP-save-extractor/issues/new/choose).
>
> Check the [incompatible game list](#incompatible-games) below and search the issues for a duplicate before creating a new one.

## Supported games
If you migrate a save to Steam/Epic version that's listed with ❔ below, please open an issue and confirm whether it worked, so the table can be updated.

Legend: ✅ Confirmed working, ❔ Unconfirmed, - Not available in the store

| Game | Tested w/ Steam | Tested w/ Epic |
|-|-|-|
| **Abiotic Factor** | ✅ | - |
| Arcade Paradise | ✅ | ✅ |
| Atomic Heart | ✅ | - |
| The Callisto Protocol | ✅ | - |
| Celeste | ❔ | ❔ |
| Chained Echoes | ❔ | ❔ |
| Chorus | ✅ | ❔ |
| Control | ❔ | ✅ |
| Coral Island | ✅ | - |
| Clair Obscur: Expedition 33 | ✅ | - |
| Cricket 24 | ✅ | - |
| Final Fantasy XV | ✅ | - |
| Forza Horizon 5 | ✅ | - |
| Fuga: Melodies of Steel 2 | ❔ | ❔ |
| Hades | ✅ | ❔ |
| High on Life | ✅ | ❔ |
| Hi-Fi RUSH | ✅ | ❔ |
| Hypnospace Outlaw | ✅ | ❔ |
| Just Cause 4 | ❔ | ❔ |
| Lies of P | ✅ | - |
| Manor Lords | ✅ | ❔ |
| Monster Train | ✅ | - |
| Ninja Gaiden Sigma | ✅ | - |
| Oblivion Remastered | ✅ | ❔ |
| Octopath Traveller | ❔ | ❔ |
| Palworld | ✅ | - |
| Persona 5 Royal | ✅ | - |
| Persona 5 Tactica | ✅ | - |
| Railway Empire 2 | ❔ | ❔ |
| Remnant 2 | ✅ | ❔ |
| Remnant: From the Ashes | ❔ | ❔ |
| Solar Ash | ✅ | ❔ |
| SpiderHeck | ✅ | ❔ |
| Starfield | ✅ | - |
| State of Decay 2 | ✅ | ❔ |
| Totally Accurate Battle Simulator | ✅ | - |
| Wo Long: Fallen Dynasty | ❔ | - |
| Yakuza 0 | ✅ | - |

## Incompatible games
These games use different save formats than the Steam/Epic version that can't be easily converted.

| Game | Issue |
|-|-|
| A Plague Tale: Requiem | [#139](https://github.com/Z1ni/XGP-save-extractor/issues/139) |
| ARK: Survival Ascended | [#165](https://github.com/Z1ni/XGP-save-extractor/issues/165) |
| Chivarly 2 | [#39](https://github.com/Z1ni/XGP-save-extractor/issues/39) |
| Death's Door | [#79](https://github.com/Z1ni/XGP-save-extractor/issues/79) |
| Forza Horizon 4 | [#71](https://github.com/Z1ni/XGP-save-extractor/issues/71) |
| Like a Dragon Gaiden: The Man Who Erased His Name | [#66](https://github.com/Z1ni/XGP-save-extractor/issues/66) |
| Like a Dragon: Ishin! | [#180](https://github.com/Z1ni/XGP-save-extractor/issues/180) |
| Neon White | [#185](https://github.com/Z1ni/XGP-save-extractor/issues/185) |
| Persona 3 Reload | [#114](https://github.com/Z1ni/XGP-save-extractor/issues/114) |
| Tinykin | [#28](https://github.com/Z1ni/XGP-save-extractor/issues/28) |
| Yakuza: Like a Dragon | [#72](https://github.com/Z1ni/XGP-save-extractor/issues/72) |

## Running
> [!IMPORTANT]
> If the save file extraction fails, wait for a bit and try again. The Xbox cloud save sync can take some time and produce invalid files while syncing is in progress.

> [!IMPORTANT]
> Some anti-virus/anti-malware software can flag the executable as malicious. The executable is produced with [PyInstaller](https://pyinstaller.org/) and contains the Python interpreter alongside with the same `main.py` script as in this repo.

Download the latest release for an one-file executable: https://github.com/Z1ni/XGP-save-extractor/releases

*Or*

Run `main.py` with Python 3.10+. The script produces ZIP files for each of the supported games that are installed for the current user.

## Thanks
Thanks to [@snoozbuster](https://github.com/snoozbuster) for figuring out the container format at https://github.com/goatfungus/NMSSaveEditor/issues/306.

Also thanks to everyone that has [contributed](https://github.com/Z1ni/XGP-save-extractor/graphs/contributors) by adding support for new games.
