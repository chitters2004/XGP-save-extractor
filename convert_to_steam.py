#!/usr/bin/env python3
"""
ABIOTIC FACTOR: XBOX → STEAM CONVERTER (Fork Version)

This converter works with extracted saves from main.py and converts them to Steam format.

Usage:
    # Auto-detect latest extraction
    python convert_to_steam.py --template "path/to/steam/save"

    # Specify extraction ZIP
    python convert_to_steam.py --input "abiotic_factor_xxx.zip" --template "path/to/steam/save"

    # Specify extracted folder
    python convert_to_steam.py --input "extracted/WorldName" --template "path/to/steam/save"

Requirements:
- uesave-rs: cargo install --git https://github.com/trumank/uesave-rs --branch patch-abiotic-factor
- Working Steam save as template (from Steam dedicated server or Steam game)

Template Locations (Auto-Checked):
- Steam Dedicated Server: {SteamApps}/common/AbioticFactorDedicatedServer/Saved/SaveGames/Server/Worlds/{WorldName}/
- Steam Game: {UserProfile}/AppData/LocalLow/Deep Field Games/Abiotic Factor/Saved/SaveGames/{SteamID}/
"""

import os
import sys
import json
import shutil
import zipfile
import argparse
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple, List

# Common Steam locations to check for templates
STEAM_TEMPLATE_PATHS = [
    # Dedicated Server
    Path("C:/Program Files (x86)/Steam/steamapps/common/AbioticFactorDedicatedServer/Saved/SaveGames/Server/Worlds"),
    Path("F:/Games/Servers/AbioticFactor/Saved/SaveGames/Server/Worlds"),
    Path("D:/Games/Servers/AbioticFactor/Saved/SaveGames/Server/Worlds"),
    # Steam Game
    Path(os.path.expanduser("~")) / "AppData/LocalLow/Deep Field Games/Abiotic Factor/Saved/SaveGames",
]


class AbioticConverter:
    """Convert extracted Xbox saves to Steam format"""

    def __init__(self, input_path: Optional[Path], template_path: Optional[Path], output_dir: Path):
        self.input_path = input_path
        self.template_path = template_path
        self.output_dir = output_dir
        self.temp_dir = None
        self.extracted_dir = None

    def log(self, message: str, level: str = "INFO"):
        """Simple logging"""
        prefix = {"INFO": "  ", "SUCCESS": "✓ ", "ERROR": "✗ ", "WARN": "⚠ "}.get(level, "  ")
        print(f"{prefix}{message}")

    def find_latest_extraction(self) -> Optional[Path]:
        """Find the most recent extraction ZIP in current directory"""
        zips = sorted(Path(".").glob("abiotic_factor_*.zip"), key=os.path.getmtime, reverse=True)
        return zips[0] if zips else None

    def find_template(self) -> Optional[Path]:
        """Auto-detect Steam save template"""
        self.log("Searching for Steam save template...")

        for base_path in STEAM_TEMPLATE_PATHS:
            if not base_path.exists():
                continue

            # Look for world folders
            for world_dir in base_path.iterdir():
                if not world_dir.is_dir():
                    continue

                # Check for required template files
                metadata = world_dir / "WorldSave_MetaData.sav"
                world_save = world_dir / "WorldSave_Facility.sav"
                player_dir = world_dir / "PlayerData"

                if metadata.exists() and world_save.exists() and player_dir.exists():
                    player_saves = list(player_dir.glob("Player_*.sav"))
                    if player_saves:
                        self.log(f"Found template: {world_dir}", "SUCCESS")
                        return world_dir

        return None

    def extract_input(self) -> Tuple[bool, Optional[Path]]:
        """Extract or locate input saves"""
        self.log("Locating input saves...")

        # If no input specified, find latest ZIP
        if not self.input_path:
            self.input_path = self.find_latest_extraction()
            if not self.input_path:
                self.log("No extraction ZIP found. Run main.py first!", "ERROR")
                return False, None
            self.log(f"Using latest extraction: {self.input_path.name}")

        # If input is a ZIP, extract it
        if self.input_path.suffix == ".zip":
            self.temp_dir = Path(tempfile.mkdtemp(prefix="abf_convert_"))
            self.log(f"Extracting {self.input_path.name}...")

            with zipfile.ZipFile(self.input_path, 'r') as zf:
                zf.extractall(self.temp_dir)

            # Find the world folder
            world_folders = [d for d in self.temp_dir.iterdir() if d.is_dir()]
            if not world_folders:
                self.log("No world folder found in ZIP", "ERROR")
                return False, None

            self.extracted_dir = world_folders[0]
            self.log(f"Extracted to: {self.extracted_dir.name}", "SUCCESS")
            return True, self.extracted_dir

        # Input is already a folder
        elif self.input_path.is_dir():
            self.extracted_dir = self.input_path
            self.log(f"Using folder: {self.extracted_dir}", "SUCCESS")
            return True, self.extracted_dir

        else:
            self.log(f"Invalid input: {self.input_path}", "ERROR")
            return False, None

    def get_template_headers(self) -> Tuple[Optional[bytes], Optional[str], Optional[str]]:
        """Extract headers from template saves"""
        self.log("Extracting template headers...")

        if not self.template_path:
            self.template_path = self.find_template()
            if not self.template_path:
                self.log("No Steam save template found!", "ERROR")
                self.log("Please specify --template path/to/steam/save")
                return None, None, None

        metadata_template = self.template_path / "WorldSave_MetaData.sav"
        world_template = self.template_path / "WorldSave_Facility.sav"
        player_dir = self.template_path / "PlayerData"
        player_saves = list(player_dir.glob("Player_*.sav"))

        if not all([metadata_template.exists(), world_template.exists(), player_saves]):
            self.log("Template missing required files", "ERROR")
            return None, None, None

        player_template = player_saves[0]

        try:
            # Extract GVAS header from MetaData
            with open(metadata_template, 'rb') as f:
                data = f.read()

            # Find where properties start
            prop_offset = data.find(b'MinutesPassed')
            if prop_offset == -1:
                prop_offset = data.find(b'SaveVersion')
            if prop_offset == -1:
                self.log("Could not find property data in template", "ERROR")
                return None, None, None

            header_end = prop_offset - 4  # 4 bytes before property name
            gvas_header = data[:header_end]

            # Get save_game_type from templates using uesave
            result = subprocess.run(['uesave', 'to-json', '-i', str(world_template)],
                                  capture_output=True, text=True, check=True)
            world_data = json.loads(result.stdout)
            world_type = world_data['root']['save_game_type']

            result = subprocess.run(['uesave', 'to-json', '-i', str(player_template)],
                                  capture_output=True, text=True, check=True)
            player_data = json.loads(result.stdout)
            player_type = player_data['root']['save_game_type']

            self.log(f"Extracted {len(gvas_header)} byte GVAS header", "SUCCESS")
            self.log(f"World type: {world_type.split('.')[-1]}")
            self.log(f"Player type: {player_type.split('.')[-1]}")

            return gvas_header, world_type, player_type

        except subprocess.CalledProcessError as e:
            self.log("uesave failed. Is it installed?", "ERROR")
            self.log("Install Rust from rustup.rs, then install uesave-rs:")
            self.log("cargo install --git https://github.com/trumank/uesave-rs --branch patch-abiotic-factor")
            return None, None, None
        except FileNotFoundError:
            self.log("uesave not found. Is Rust installed?", "ERROR")
            self.log("1. Install Rust from rustup.rs")
            self.log("2. Run: cargo install --git https://github.com/trumank/uesave-rs --branch patch-abiotic-factor")
            return None, None, None
        except Exception as e:
            self.log(f"Error extracting headers: {e}", "ERROR")
            return None, None, None

    def apply_headers(self, gvas_header: bytes) -> bool:
        """Apply GVAS headers to extracted saves"""
        self.log("Applying GVAS headers...")

        # Process all .sav files
        save_files = list(self.extracted_dir.rglob("*.sav"))
        player_dir = self.extracted_dir / "PlayerData"

        for save_file in save_files:
            with open(save_file, 'rb') as f:
                raw_data = f.read()

            # Skip if already has GVAS header
            if raw_data[:4] == b'GVAS':
                continue

            # Skip wrapper byte and add GVAS header
            xbox_properties = raw_data[1:]
            fixed_data = gvas_header + xbox_properties

            with open(save_file, 'wb') as f:
                f.write(fixed_data)

        self.log(f"Applied headers to {len(save_files)} files", "SUCCESS")
        return True

    def fix_save_types(self, world_type: str, player_type: str) -> bool:
        """Fix save_game_type for each file"""
        self.log("Fixing save_game_type...")

        try:
            # Fix world saves (not MetaData)
            world_saves = [s for s in self.extracted_dir.glob("WorldSave_*.sav")
                          if s.name != "WorldSave_MetaData.sav"]

            for save_path in world_saves:
                self._fix_save_type(save_path, world_type)

            # Fix player saves
            player_dir = self.extracted_dir / "PlayerData"
            player_saves = list(player_dir.glob("Player_*.sav"))

            for save_path in player_saves:
                self._fix_save_type(save_path, player_type)

            self.log(f"Fixed {len(world_saves)} world + {len(player_saves)} player saves", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"Error fixing save types: {e}", "ERROR")
            return False

    def _fix_save_type(self, save_path: Path, correct_type: str):
        """Fix save_game_type for a single file"""
        result = subprocess.run(['uesave', 'to-json', '-i', str(save_path)],
                              capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        data['root']['save_game_type'] = correct_type

        json_path = save_path.with_suffix('.json')
        with open(json_path, 'w') as f:
            json.dump(data, f)

        save_path.unlink()
        subprocess.run(['uesave', 'from-json', '-i', str(json_path), '-o', str(save_path)],
                     capture_output=True, check=True)
        json_path.unlink()

    def fix_metadata(self) -> bool:
        """Remove compression flag from MetaData"""
        self.log("Fixing MetaData compression flag...")

        metadata_path = self.extracted_dir / "WorldSave_MetaData.sav"
        if not metadata_path.exists():
            self.log("MetaData not found", "WARN")
            return True

        try:
            result = subprocess.run(['uesave', 'to-json', '-i', str(metadata_path)],
                                  capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)

            if 'bHasBeenCompressed_0' in data['root']['properties']:
                del data['root']['properties']['bHasBeenCompressed_0']

                json_path = metadata_path.with_suffix('.json')
                with open(json_path, 'w') as f:
                    json.dump(data, f)

                metadata_path.unlink()
                subprocess.run(['uesave', 'from-json', '-i', str(json_path), '-o', str(metadata_path)],
                             capture_output=True, check=True)
                json_path.unlink()

                self.log("Removed compression flag", "SUCCESS")
            else:
                self.log("No compression flag found", "INFO")

            return True

        except Exception as e:
            self.log(f"Error fixing metadata: {e}", "ERROR")
            return False

    def fix_player_data(self) -> bool:
        """Fix player af_data variant"""
        self.log("Fixing player af_data...")

        player_dir = self.extracted_dir / "PlayerData"
        player_saves = list(player_dir.glob("Player_*.sav"))

        try:
            for save_path in player_saves:
                result = subprocess.run(['uesave', 'to-json', '-i', str(save_path)],
                                      capture_output=True, text=True, check=True)
                data = json.loads(result.stdout)

                if data['root']['af_data']['variant'] != 'None':
                    data['root']['af_data']['variant'] = 'None'

                    json_path = save_path.with_suffix('.json')
                    with open(json_path, 'w') as f:
                        json.dump(data, f)

                    save_path.unlink()
                    subprocess.run(['uesave', 'from-json', '-i', str(json_path), '-o', str(save_path)],
                                 capture_output=True, check=True)
                    json_path.unlink()

            self.log(f"Fixed {len(player_saves)} player saves", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"Error fixing player data: {e}", "ERROR")
            return False

    def copy_output(self) -> bool:
        """Copy converted saves to output directory"""
        self.log("Copying to output directory...")

        world_name = self.extracted_dir.name
        output_world = self.output_dir / world_name

        if output_world.exists():
            self.log(f"Output already exists: {output_world}", "WARN")
            response = input("  Overwrite? (y/n): ")
            if response.lower() != 'y':
                self.log("Cancelled", "INFO")
                return False
            shutil.rmtree(output_world)

        shutil.copytree(self.extracted_dir, output_world)
        self.log(f"Saved to: {output_world}", "SUCCESS")
        return True

    def cleanup(self):
        """Clean up temp files"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def convert(self) -> bool:
        """Run complete conversion"""
        print("=" * 80)
        print("ABIOTIC FACTOR: XBOX → STEAM CONVERTER")
        print("=" * 80)
        print()

        try:
            # Step 1: Extract/locate input
            print("STEP 1: Locate Input Saves")
            print("-" * 80)
            success, extracted_dir = self.extract_input()
            if not success:
                return False
            print()

            # Step 2: Get template headers
            print("STEP 2: Extract Template Headers")
            print("-" * 80)
            gvas_header, world_type, player_type = self.get_template_headers()
            if not gvas_header:
                return False
            print()

            # Step 3: Apply headers
            print("STEP 3: Apply GVAS Headers")
            print("-" * 80)
            if not self.apply_headers(gvas_header):
                return False
            print()

            # Step 4: Fix save types
            print("STEP 4: Fix save_game_type")
            print("-" * 80)
            if not self.fix_save_types(world_type, player_type):
                return False
            print()

            # Step 5: Fix metadata
            print("STEP 5: Fix MetaData")
            print("-" * 80)
            if not self.fix_metadata():
                return False
            print()

            # Step 6: Fix player data
            print("STEP 6: Fix Player Data")
            print("-" * 80)
            if not self.fix_player_data():
                return False
            print()

            # Step 7: Copy output
            print("STEP 7: Save Output")
            print("-" * 80)
            if not self.copy_output():
                return False
            print()

            # Success!
            print("=" * 80)
            print("✓ CONVERSION COMPLETE!")
            print("=" * 80)
            print()
            print(f"Converted saves: {self.output_dir / self.extracted_dir.name}")
            print()
            print("Your saves are now ready for Steam!")
            print()

            return True

        except Exception as e:
            self.log(f"Unexpected error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False

        finally:
            self.cleanup()


def main():
    parser = argparse.ArgumentParser(
        description="Convert Abiotic Factor Xbox saves to Steam format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Input ZIP or extracted folder (auto-detects latest if not specified)"
    )
    parser.add_argument(
        "--template",
        type=Path,
        help="Path to working Steam save folder (auto-searches if not specified)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("converted_saves"),
        help="Output directory (default: converted_saves)"
    )

    args = parser.parse_args()

    converter = AbioticConverter(
        input_path=args.input,
        template_path=args.template,
        output_dir=args.output
    )

    success = converter.convert()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
