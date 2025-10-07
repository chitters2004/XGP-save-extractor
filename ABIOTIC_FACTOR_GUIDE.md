# Abiotic Factor Save Extraction & Conversion

Complete guide for extracting and converting Abiotic Factor saves from Xbox Game Pass to **Steam Dedicated Server**.

> **⚠️ IMPORTANT:** This converter is specifically designed for **Steam Dedicated Server** saves.
> It does NOT support converting saves for Steam singleplayer/co-op mode.
> The converted saves will only work on a Steam dedicated server.

## Quick Start (2-Step Process)

### Step 1: Extract Xbox Saves

Run the main extractor:
```bash
python main.py
```

This creates a ZIP file with your organized saves:
```
WorldName/
  ├── WorldSave_MetaData.sav
  ├── WorldSave_*.sav (28+ files)
  ├── SandboxSettings.ini
  └── PlayerData/
      └── Player_*.sav (2 files)
```

### Step 2: Convert to Steam Dedicated Server (REQUIRED)

**You MUST have a working Steam dedicated server save as a template first!**

Get a template by:
1. Start your Abiotic Factor dedicated server
2. Let it create a new world (or load an existing one)
3. Stop the server
4. The template save will be in `{ServerRoot}/Saved/SaveGames/Server/Worlds/{WorldName}/`

Then convert:
```bash
# Auto-detect latest extraction and search for template
python convert_to_steam.py

# Or specify paths
python convert_to_steam.py --input "abiotic_factor_xxx.zip" --template "path/to/server/save"
```

Output: `converted_saves/WorldName/` ready for your dedicated server!

## Requirements

### For Extraction (Step 1):
- **Python 3.10+**
- **oo2core_9_win64.dll** - Included

### For Conversion (Step 2):
- **Rust** - Required to install uesave-rs. Get it from [rustup.rs](https://rustup.rs/)
- **uesave-rs** - After installing Rust, run:
  ```bash
  cargo install --git https://github.com/trumank/uesave-rs --branch patch-abiotic-factor
  ```
  This may take 5-10 minutes to compile.
- **Working Steam save** (template) - See Step 2 above

## Template Auto-Detection

The converter automatically searches common dedicated server locations:
- `{SteamApps}/common/AbioticFactorDedicatedServer/Saved/SaveGames/Server/Worlds/`
- `F:/Games/Servers/AbioticFactor/Saved/SaveGames/Server/Worlds/`
- `D:/Games/Servers/AbioticFactor/Saved/SaveGames/Server/Worlds/`

If found, you don't need to specify `--template`!

> **Note:** The converter does NOT auto-detect singleplayer Steam game saves, as those are incompatible with dedicated servers.

## Conversion Process (What It Does)

The converter automatically:
1. **Extracts** - Unzips your saves (if needed)
2. **Injects GVAS Headers** - Adds Unreal Engine save format headers from template
3. **Fixes save_game_type** - Sets correct types for world/player saves
4. **Removes Compression Flag** - Strips Xbox-specific metadata
5. **Fixes Player Data** - Updates af_data variant structure
6. **Saves Output** - Copies to `converted_saves/WorldName/`

## Troubleshooting

**Q: "No Steam save template found!"**
A: You need a working Steam **dedicated server** save first. Start your dedicated server, let it create a world, then stop it and try again.

**Q: "uesave failed. Is it installed?"**
A: You need to install Rust first, then uesave-rs:
1. Install Rust from [rustup.rs](https://rustup.rs/)
2. Restart your terminal
3. Install uesave-rs:
```bash
cargo install --git https://github.com/trumank/uesave-rs --branch patch-abiotic-factor
```

**Q: "cargo: command not found"**
A: Rust is not installed. Install it from [rustup.rs](https://rustup.rs/), then restart your terminal.

**Q: Can I use the extracted saves directly in Steam?**
A: No, they MUST be converted first using `convert_to_steam.py`.

**Q: The extractor says "Abiotic Factor extraction requires oo2core_9_win64.dll"**
A: The DLL should be included. Make sure it's in the same folder as main.py.

**Q: My extracted ZIP is empty or corrupted**
A: Try running the extractor again. Xbox cloud sync can sometimes cause temporary issues.

**Q: Where do I put the converted saves?**
A: Copy the `WorldName` folder to your dedicated server's `{ServerRoot}/Saved/SaveGames/Server/Worlds/` directory, then restart the server.

**Q: Can I use these converted saves in Steam singleplayer/co-op mode?**
A: **No.** These saves are specifically formatted for dedicated servers and will not work in singleplayer or non-dedicated co-op sessions.

## File Locations

**Xbox Saves:**
`%LOCALAPPDATA%\Packages\PlayStack.AbioticFactor_3wcqaesafpzfy\SystemAppData\wgs\{UserID}_{TitleID}\`

**Steam Dedicated Server Saves:**
`{ServerRoot}\Saved\SaveGames\Server\Worlds\{WorldName}\`

> **Note:** Steam singleplayer saves (`%UserProfile%\AppData\LocalLow\Deep Field Games\Abiotic Factor\Saved\SaveGames\{SteamID}\`) use a different format and are NOT compatible with this converter.

## For Developers

If you want to contribute or improve the conversion process:
- See `convert_to_steam.py` for the complete converter implementation
- The conversion requires GVAS headers from a working Steam save (template-based approach)
- Handler implementation is in `main.py` (search for `"abiotic-factor"`)

## Credits

- Original XGP-save-extractor by contributors
- Abiotic Factor handler integration: 2025-10-07
- Template-based converter: 2025-10-07
- Thanks to @trumank for uesave-rs with Abiotic Factor support
