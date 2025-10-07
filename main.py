import json
import os
import struct
import subprocess
import sys
import tempfile
import traceback
import uuid
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePath
from typing import Any, Dict, List, Tuple

# Import Abiotic Factor extraction module
try:
    import extract_abf_saves
    ABIOTIC_FACTOR_AVAILABLE = True
except ImportError:
    ABIOTIC_FACTOR_AVAILABLE = False

# Xbox Game Pass for PC savefile extractor

# Running: Just run the script with Python 3 to create ZIP files that contain the save files

# Thanks to @snoozbuster for figuring out the container format at https://github.com/goatfungus/NMSSaveEditor/issues/306

filetime_epoch = datetime(1601, 1, 1, tzinfo=timezone.utc)
packages_root = Path(os.path.expandvars(f"%LOCALAPPDATA%\\Packages"))

# Abiotic Factor constants (from v1.0, 2025-10-07)
ABIOTIC_GVAS_HEADER_HEX = "47564153030000000a020000f40300000500040004004c420f80090000002b2b44462b41424600030000004a00000022d5549cbe4f26a846072194d082b4612c000000a35c9162f74b8e1cc7120ea3f79d21c822000000240d40cc7b4ee9e083a2f99b27e0000000e40bb2b0184fe91ec0b953a3c7050a00000000c3751e0639467eb484c87064ecefe7402800000041e8066e44f49482311d72a18e3713250000000609bd37cf80430f734c166a4d63f6c0370000000f64c4b5e0ae44bd39c2f33c2f36a6fc000000005c86c1a3e30f4974cd48ccaeda941339000000007b13f378c24be916df47a4e81cce8e1c14000000292e765da12049fcbdb27f89481c09d830000000a51ec67ba12441d86ec7b5e0f84d075a0d000000f77e3bd8b5354e10a9579852087a0002000000281cf7c26e2d8146a786e0409c540d550100000006ea736cf71047b67c0355826fa50a6a03000000dc2968d716dd4d1de2a0aa64cc8308840300000075ba7dc2264cdfc31718b75e531df71f01000000d4d4686e3ea42c05b179e0c154f0e5c60100000091fb98d664ec494d78e5a9f1dc86ad2211000000d8271baf46bb4f65e48c58cf5daf590f00000000a3e1d4e2e26349c7b5f89e6d0a042048010000004e82d5e9600947aafbb60da0e37aa91f030000006cbbce6cb60740a7e71817c7538f06310e000000d1c3e00b35e8014d8ebf5e38fdbf00230f0000004b066e89974ee02f8d67b38c72e7065a01000000f68c74dd074fab0d718799f2e87913e301000000e2d142d77024427e800aa0f72b46ee980f000000d1d30d72e940416ea4af09742eb064d001000000bafd63b02478fb72810ae6f8b49e20cd86000000bb5a48dbcb6d7f81f8cfa2d60c905b6e08000000ddbb4c5bae5b4b12e9cad67f86aeba550c000000689170e7bb2340587e994ca9bdb0f19e0d0000008806cbd99fff58014ea290d05fc1b810050000003f6b6d12f2e2bf5f6c7e29530cd5e17a01000000a3b3740f4f634d55e6a2e8c1729fd9970a000000c21ecf35ec26254a60a2c948770f79f329000000bde0b468fe6b49479873e380f3b66e1b28000000609e02b3201b1fe5a304b3e3fd26320300000060b77dae6f24fce23a18f73014bc5e07010000006d5f0da6cde13e58211ecc9fb482a71f00000000e4368a7bf9a09548f973219bbf41a77c020000008aceb4303958728f3b4efb7714cf58e901000000075b37716aa64e179c7398c83a7e62107700000000fc0da1f27e5b46f2baa5a1ff701bb8ac33000000d4cc7e89eb41fb9a0959a01884ab85e808000000c261105ec1964c77e1e1f4a4b22ebf8e12000000e1b03a9227624ec5aa7e21e0dd059e9c13000000bd86ff9d494fe201a28812c3a86f77060a000000ac07a1f2aff63e161df39c1742fc3a68010000000b1f742f93174c1009a1cf0c7b09e0f70a00000028f94c35e63a410f8c8d9fcf91f5b55100000027dda3c235f80bc1834c3b1699d37d0e000000a27e74a4e8cda82e0a498d9c60186c4007000000dc087e80952b49bd8b415a81e3fa4f6b05000000eb3fb52e54956a754ae4b59ac4dbb0b805000000f9e510fb4ec9118f1e368f5ab4f9edc301000000e7ac61a10c49fb5ec91dcea3ce76025e320000002edd750a0341bdb96fc66a11f28c16a701000000d0e37afe57b3c14c86990f55f5fcf85658000000040d3e26f0a363e66c044e38e5d7adb20000000081ddae93be1aea4775b7097b3a7df9c609000000ac0b5e2ce69a11117c4bab11a5415411000000bbe11ce2b67ef90020d1c97428b30f5d00000000301dbe5d725f03a39ea4bfd5b3852f6503000000798d5ddc4169460e9c4e56f3fc8fb73909000000bf5c7aa7ea0f5c28b46482cf5d9dbe371e000000b86af06e8e63c2a4047ef6ed463818120000000047567f7d6fec71488c9a23b6e9fb63e503000000fc90f9f8fbe3a0a3c8f1af83802074c204000000dc8e427ea4bd7e0e68490f8fa4eefd1a05000000d0486ff81ed1c2119dfa76f0fa5d2e4a01000000db0379fb5b53dd88e8dbfe9e82403d7502000000e066c19a4f40ffe82127a3ba96bd5f5502000000dcc0f2fc30afdb16e1ae98fcec06570756000000e41b046304a36a9e05005df874d5ed6600000007a0a7e8cb0f1bfb85ef3b8f7fe8594a080000000070caee97d9a8524d9afa6f2e5f00de0005000000ca5ff16dc09c4e4f5f84feead2e1b6e900000000a05d9531a00a5a02add60b96c9ab8fc303000000d2a99adc64534f01b6de0dc02fb96b7009000000bec1a7a0ea072ec8305d9f5ca8c1cd501e000000f6df23f6aa7bbb494e18fff68d6df04702000000b0dd6b2a7f0f4708980f28f996564bf805000000fa14f82d3e99e5c40f5b3f99f1e43e5f01000000c3bb3624e74620051bb6ed50b6e51e7505000000e03c385f91104d14b66e817f6016a95101000000d23dbb22759eaf91023ba8dd52ab2f76020000008a76cf5c99c34e19b3691f71c1d40cfc550000004d021e63f77c3d4e0a0508e41ebe76000000000021c44a72fa8ea27b4be5d1db12e50aa003000000a6eec5db7c30f22f64dfb4cdd60a090600000000"
ABIOTIC_GVAS_HEADER = bytes.fromhex(ABIOTIC_GVAS_HEADER_HEX)
ABIOTIC_SAVE_TYPES = {
    "metadata": "/Game/Blueprints/Saves/Abiotic_WorldMetadataSave.Abiotic_WorldMetadataSave_C",
    "world": "/Game/Blueprints/Saves/Abiotic_WorldSave.Abiotic_WorldSave_C",
    "player": "/Game/Blueprints/Saves/Abiotic_CharacterSave.Abiotic_CharacterSave_C",
}


def read_game_list() -> Dict[str, Any] | None:
    try:
        # Search for the games JSON in the script directory
        games_json_path = Path("games.json")
        if not games_json_path.exists():
            # Search for the games JSON in the bundle directory
            games_json_path = Path(__file__).resolve().with_name("games.json")
        if not games_json_path.exists():
            return None
        with games_json_path.open("r") as f:
            without_comments = "\n".join(
                [l for l in f.readlines() if not l.lstrip().startswith("//")]
            )
        j = json.loads(without_comments)
        # Create a dict with the package name as the key
        games: Dict[str, Any] = {}
        for entry in j["games"]:
            games[entry["package"]] = {
                "name": entry["name"],
                "handler": entry["handler"],
                "handler_args": entry.get("handler_args") or {}
            }
        return games
    except:
        return None


def discover_games(supported_games: Dict[str, Any]) -> List[str]:
    found_games = []
    for pkg_name in supported_games.keys():
        pkg_path = packages_root / pkg_name
        if pkg_path.exists():
            found_games.append(pkg_name)
    return found_games


def read_utf16_str(f, str_len=None) -> str:
    if not str_len:
        str_len = struct.unpack("<i", f.read(4))[0]
    return f.read(str_len * 2).decode("utf-16").rstrip("\0")


def read_filetime(f) -> datetime:
    filetime = struct.unpack("<Q", f.read(8))[0]
    filetime_seconds = filetime / 10_000_000
    return filetime_epoch + timedelta(seconds=filetime_seconds)


def print_sync_warning(title: str):
    print()
    print(f"  !! {title} !!")
    print("     Xbox cloud save syncing might not be complete, try again later.")
    print("     Extracted saves for this game might be corrupted!")
    print("     Press enter to skip and continue.")
    input()


def get_xbox_user_name(user_id: int) -> str | None:
    xbox_app_package = "Microsoft.XboxApp_8wekyb3d8bbwe"
    try:
        live_gamer_path = (
            packages_root / xbox_app_package / "LocalState/XboxLiveGamer.xml"
        )
        with live_gamer_path.open("r", encoding="utf-8") as f:
            gamer = json.load(f)
        known_user_id = gamer.get("XboxUserId")
        if known_user_id != user_id:
            return None
        return gamer.get("Gamertag")
    except:
        return None


def find_user_containers(pkg_name: str) -> List[Tuple[int | str, Path]]:
    # Find container dir
    wgs_dir = packages_root / pkg_name / "SystemAppData/wgs"
    if not wgs_dir.is_dir():
        return []
    # Get the correct user directory
    has_backups = False
    valid_user_dirs = []
    for entry in wgs_dir.iterdir():
        if not entry.is_dir():
            continue
        if entry.name == "t":
            continue
        if "backup" in entry.name:
            has_backups = True
            continue
        if len(entry.name.split("_")) == 2:
            valid_user_dirs.append(entry)

    if has_backups:
        print("  !! The save directory contains backups !!")
        print("     This script will currently skip backups made by the Xbox app.")
        print("     Press enter to continue.")
        input()

    if len(valid_user_dirs) == 0:
        # No saves for any users
        return []

    user_dirs = []

    for valid_user_dir in valid_user_dirs:
        user_id_hex, title_id_hex = valid_user_dir.name.split("_", 1)
        user_id = int(user_id_hex, 16)
        user_name = get_xbox_user_name(user_id)
        user_dirs.append((user_name or user_id, valid_user_dir))

    return user_dirs


def read_user_containers(user_wgs_dir: Path) -> Tuple[str, List[Dict[str, Any]]]:
    containers_dir = user_wgs_dir
    containers_idx_path = containers_dir / "containers.index"

    containers = []

    # Read the index file
    with containers_idx_path.open("rb") as f:
        # Unknown
        f.read(4)

        container_count = struct.unpack("<i", f.read(4))[0]

        # Package display name seems to be available only on console saves
        pkg_display_name = read_utf16_str(f)

        store_pkg_name = read_utf16_str(f).split("!")[0]

        # Creation date, FILETIME
        creation_date = read_filetime(f)
        # print(f"  Container index created at {creation_date}")
        # Unknown
        f.read(4)
        read_utf16_str(f)

        # Unknown
        f.read(8)

        for _ in range(container_count):
            # Container name
            container_name = read_utf16_str(f)
            # Duplicate of the file name
            read_utf16_str(f)
            # Unknown quoted hex number
            read_utf16_str(f)
            # Container number
            container_num = struct.unpack("B", f.read(1))[0]
            # Unknown
            f.read(4)
            # Read container (folder) GUID
            container_guid = uuid.UUID(bytes_le=f.read(16))
            # Creation date, FILETIME
            container_creation_date = read_filetime(f)
            # print(f"Container created at {container_creation_date}")
            # Unknown
            f.read(16)

            files = []

            # Read the container file in the container directory
            container_path = containers_dir / container_guid.hex.upper()
            container_file_path = container_path / f"container.{container_num}"

            if not container_file_path.is_file():
                print_sync_warning(f'Missing container "{container_name}"')
                continue

            with container_file_path.open("rb") as cf:
                # Unknown (always 04 00 00 00 ?)
                cf.read(4)
                # Number of files in this container
                file_count = struct.unpack("<i", cf.read(4))[0]
                for _ in range(file_count):
                    # File name, 0x80 (128) bytes UTF-16 = 64 characters
                    file_name = read_utf16_str(cf, 64)
                    # Read file GUID
                    file_guid = uuid.UUID(bytes_le=cf.read(16))
                    # Read the copy of the GUID
                    file_guid_2 = uuid.UUID(bytes_le=cf.read(16))

                    if file_guid == file_guid_2:
                        file_path = container_path / file_guid.hex.upper()
                    else:
                        # Check if one of the file paths exist
                        file_guid_1_path = container_path / file_guid.hex.upper()
                        file_guid_2_path = container_path / file_guid_2.hex.upper()

                        file_1_exists = file_guid_1_path.is_file()
                        file_2_exists = file_guid_2_path.is_file()

                        if file_1_exists and not file_2_exists:
                            file_path = file_guid_1_path
                        elif not file_1_exists and file_2_exists:
                            file_path = file_guid_2_path
                        elif file_1_exists and file_2_exists:
                            # Which one to use?
                            print_sync_warning(
                                f'Two files exist for container "{container_name}" file "{file_name}": {file_guid} and {file_guid_2}, can\'t choose one'
                            )
                            continue
                        else:
                            print_sync_warning(
                                f'Missing file "{file_name}" inside container "{container_name}"'
                            )
                            continue

                    files.append(
                        {
                            "name": file_name,
                            # "guid": file_guid,
                            "path": file_path,
                        }
                    )

            containers.append(
                {
                    "name": container_name,
                    "number": container_num,
                    # "guid": container_guid,
                    "files": files,
                }
            )

    return (store_pkg_name, containers)


def _fix_abiotic_save_type(save_path: Path, correct_type: str):
    """Fix save_game_type for an Abiotic Factor save file"""
    try:
        result = subprocess.run(
            ["uesave", "to-json", "-i", str(save_path)],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"  ERROR: uesave failed on {save_path.name}")
        print(f"  stdout: {e.stdout}")
        print(f"  stderr: {e.stderr}")
        raise

    data = json.loads(result.stdout)
    data["root"]["save_game_type"] = correct_type

    json_path = save_path.with_suffix(".json")
    with open(json_path, "w") as f:
        json.dump(data, f)

    save_path.unlink()
    subprocess.run(
        ["uesave", "from-json", "-i", str(json_path), "-o", str(save_path)],
        capture_output=True,
        check=True,
    )
    json_path.unlink()


def _remove_abiotic_compression_flag(save_path: Path):
    """Remove bHasBeenCompressed_0 from Abiotic Factor MetaData save"""
    result = subprocess.run(
        ["uesave", "to-json", "-i", str(save_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)

    if "bHasBeenCompressed_0" in data["root"]["properties"]:
        del data["root"]["properties"]["bHasBeenCompressed_0"]

        json_path = save_path.with_suffix(".json")
        with open(json_path, "w") as f:
            json.dump(data, f)

        save_path.unlink()
        subprocess.run(
            ["uesave", "from-json", "-i", str(json_path), "-o", str(save_path)],
            capture_output=True,
            check=True,
        )
        json_path.unlink()


def _fix_abiotic_player_af_data(save_path: Path):
    """Fix player af_data variant for Abiotic Factor"""
    result = subprocess.run(
        ["uesave", "to-json", "-i", str(save_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    data["root"]["af_data"]["variant"] = "None"

    json_path = save_path.with_suffix(".json")
    with open(json_path, "w") as f:
        json.dump(data, f)

    save_path.unlink()
    subprocess.run(
        ["uesave", "from-json", "-i", str(json_path), "-o", str(save_path)],
        capture_output=True,
        check=True,
    )
    json_path.unlink()


def get_save_paths(
    supported_games: Dict[str, Any],
    store_pkg_name: str,
    containers: List[Dict[str, Any]],
    temp_dir: tempfile.TemporaryDirectory,
) -> List[Tuple[str, Path]]:
    save_meta = []

    handler_name = supported_games[store_pkg_name]["handler"]
    handler_args = supported_games[store_pkg_name].get("handler_args") or {}

    if handler_name == "1c1f":
        # "1 container, 1 file" (1c1f). Each container contains only one file which name will be the name of the container.
        file_suffix = handler_args.get("suffix")
        for container in containers:
            fname = container["name"]
            if file_suffix is not None:
                # Add a suffix to the file name if configured
                fname += file_suffix
            fpath = container["files"][0]["path"]
            save_meta.append((fname, fpath))

    elif handler_name == "1cnf":
        # "1 container, n files" (1cnf). There's only one container that contains all the savefiles.
        file_suffix = handler_args.get("suffix")
        container = containers[0]
        for c_file in container["files"]:
            final_filename = c_file["name"]
            if file_suffix is not None:
                # Add a suffix to the file name if configured
                final_filename += file_suffix
            save_meta.append((final_filename, c_file["path"]))

    elif handler_name == "1cnf-folder":
        # Each container represents one folder
        for container in containers:
            folder_name: str = container["name"]
            for file in container["files"]:
                fname = file["name"]
                zip_fname = f"{folder_name}/{fname}"
                fpath = file["path"]
                save_meta.append((zip_fname, fpath))

    elif handler_name == "control":
        # Handle Control saves
        # Control uses container in a "n containers, n files" manner (ncnf),
        # where the container represents a folder that has named files.
        # Epic Games Store (and Steam?) use the same file names, but with a ".chunk" file extension.
        # TODO: Are files named "meta" unnecessary?
        for container in containers:
            path = PurePath(container["name"])

            # Create "--containerDisplayName.chunk" that contains the container name
            # TODO: Does Control _need_ "--containerDisplayName.chunk"?
            temp_container_disp_name_path = (
                Path(temp_dir.name)
                / f"{container['name']}_--containerDisplayName.chunk"
            )
            with temp_container_disp_name_path.open("w") as f:
                f.write(container["name"])
            save_meta.append(
                (path / "--containerDisplayName.chunk", temp_container_disp_name_path)
            )

            for file in container["files"]:
                save_meta.append((path / f"{file['name']}.chunk", file["path"]))

    elif handler_name == "starfield":
        # Starfield
        # The Steam version uses SFS ("Starfield save"?) files, whereas the Store version splits the SFS files into multiple files inside the containers.
        # One container is one save.
        # It seems that the "BETHESDAPFH" file is a header which is padded to the next 16 byte boundary with the string "padding\0", where \0 is NUL.
        # The other files ("PnP", where n is a number starting from 0) are then concatenated into the SFS file, also with padding.

        # As of at least Starfield version 1.9.51.0, the containers contain "toc" and one or more "BlobDataN" files (where N is a number starting from 0).
        # The new format seems to already include the padding.

        temp_folder = Path(temp_dir.name) / "Starfield"
        temp_folder.mkdir()

        pad_str = "padding\0" * 2

        for container in containers:
            path = PurePath(container["name"])
            # There can be other files than saves, e.g. files under "Settings/" path. Skip those.
            if path.parent.name != "Saves":
                continue
            # Strip out the parent folder name
            sfs_name = path.name
            # Arrange the files: header as index 0, P0P as 1, P1P as 2, etc. (or BlobData0, ... for the new format)
            parts = {}

            is_new_format = "toc" in [f["name"] for f in container["files"]]

            for file in container["files"]:
                if file["name"] == "toc":
                    continue
                if is_new_format:
                    idx = int(file["name"].removeprefix("BlobData"))
                else:
                    if file["name"] == "BETHESDAPFH":
                        idx = 0
                    else:
                        idx = int(file["name"].strip("P")) + 1
                parts[idx] = file["path"]

            # Construct the SFS file
            sfs_path = temp_folder / sfs_name
            with sfs_path.open("wb") as sfs_f:
                for idx, part_path in sorted(parts.items(), key=lambda t: t[0]):
                    with open(part_path, "rb") as part_f:
                        data = part_f.read()
                    size = sfs_f.write(data)
                    pad = 16 - (size % 16)
                    if pad != 16:
                        sfs_f.write(pad_str[:pad].encode("ascii"))

            save_meta.append((sfs_name, sfs_path))

    elif handler_name == "lies-of-p":
        # Lies of P
        for container in containers:
            fname: str = container["name"]
            # Lies of P prefixes the save file names with a numeric ID
            # Filter the numbers out
            for i, c in enumerate(fname):
                if c.isdigit():
                    continue
                fname = fname[i:]
                break

            # The names also need a ".sav" suffix
            fname += ".sav"
            fpath = container["files"][0]["path"]

            save_meta.append((fname, fpath))

    elif handler_name == "palworld":
        for container in containers:
            fname = container["name"]
            # Each "-" in the name is a directory separator
            fname = fname.replace("-", "/")
            fname += ".sav"
            fpath = container["files"][0]["path"]
            save_meta.append((fname, fpath))

    elif handler_name == "like-a-dragon":
        for container in containers:
            path = PurePath(container["name"])
            if path.name == "datasav":
                fpath = path.with_name("data.sav")
            elif path.name == "datasys":
                fpath = path.with_name("data.sys")
            else:
                fpath = path

            for file in container["files"]:
                if file["name"].lower() == "data":
                    save_meta.append((str(fpath), file["path"]))
                elif file["name"].lower() == "icon":
                    icon_format = handler_args.get("icon_format")
                    if icon_format is None:
                        continue
                    save_meta.append(
                        (
                            str(
                                fpath.with_name(
                                    f"{fpath.parent.name}_icon.{icon_format}"
                                )
                            ),
                            file["path"],
                        )
                    )

    elif handler_name == "cricket-24":
        # 1cnf-folder, but with a file suffix and "CHUNK" suffix removal
        # TODO: Can there be more than one chunk?
        # Each container represents one folder
        for container in containers:
            folder_name: str = container["name"]
            for file in container["files"]:
                fname = file["name"]
                fname = fname.removesuffix(".CHUNK0")
                if "CHUNK" in fname:
                    raise Exception(
                        f"Unexpected chunk name in {file['name']}! Please report this issue on the GitHub repository!"
                    )
                fname += ".SAV"
                zip_fname = f"{folder_name}/{fname}"
                fpath = file["path"]
                save_meta.append((zip_fname, fpath))

    elif handler_name == "forza":
        # Container name is the filename prefix, file names inside container are appended to that after "."
        for container in containers:
            for file in container["files"]:
                fname = f"{container['name']}.{file['name']}"
                save_meta.append((fname, file["path"]))

    elif handler_name == "arcade-paradise":
        # Arcade Paradise seems to save to one container with one file, which should be renamed to "RATSaveData.dat" for Steam
        fpath = containers[0]["files"][0]["path"]
        save_meta.append(("RATSaveData.dat", fpath))

    elif handler_name == "state-of-decay-2":
        # This is otherwise identical to 1cnf, but we ignore the path in the file names
        for file in containers[0]["files"]:
            fname = file["name"].split("/")[-1] + ".sav"
            save_meta.append((fname, file["path"]))

    elif handler_name == "railway-empire-2":
        # Each container is one file.
        # The files inside the container are "savegame" and "description". It seems that we can ignore "description".
        for container in containers:
            for file in container["files"]:
                if file["name"] != "savegame":
                    continue
                save_meta.append((container["name"], file["path"]))

    elif handler_name == "coral-island":
        # 1c1f with ".sav" suffix, but if the file name is prefixed with "Backup", we place it in a folder
        # without the prefix.
        for container in containers:
            fname = f"{container['name']}.sav"
            if fname.startswith("Backup"):
                fname = f"Backup/{fname.removeprefix('Backup')}"
            fpath = container["files"][0]["path"]
            save_meta.append((fname, fpath))

    elif handler_name == "abiotic-factor":
        # Abiotic Factor - Extract raw Xbox saves from bundled archive
        # NOTE: Extracted saves are RAW format and need conversion for Steam
        # Use convert_to_steam.py for full Steam conversion

        if not ABIOTIC_FACTOR_AVAILABLE:
            raise Exception("Abiotic Factor extraction requires extract_abf_saves.py module")

        # Check for Oodle DLL
        oodle_dll_path = Path(__file__).parent / "oo2core_9_win64.dll"
        if not oodle_dll_path.exists():
            raise Exception(
                "Abiotic Factor extraction requires oo2core_9_win64.dll\n"
                "Place the DLL in the same directory as main.py"
            )

        # Get world name from container or handler_args
        world_name = handler_args.get("world_name", "AbioticFactorWorld")
        if len(containers) > 0 and containers[0]["name"]:
            # Try to use container name as world name (e.g., "Erebus-WC" -> "Erebus")
            container_name = containers[0]["name"]
            world_name = container_name.split("-")[0] if "-" in container_name else container_name

        # Find bundled archive
        bundled_archive = None
        for container in containers:
            if len(container["files"]) > 0:
                bundled_archive = container["files"][0]["path"]
                break

        if not bundled_archive:
            raise Exception("No bundled archive found in Abiotic Factor save container")

        # Create extraction temp dir
        extract_temp = Path(temp_dir.name) / "abf_extract"
        extract_temp.mkdir(exist_ok=True)

        # Extract and decompress bundled archive
        success = extract_abf_saves.extract_archive(
            str(bundled_archive),
            str(extract_temp),
            str(oodle_dll_path)
        )

        if not success:
            raise Exception("Failed to extract Abiotic Factor bundled archive")

        # Create output structure in temp dir
        world_temp = Path(temp_dir.name) / world_name
        world_temp.mkdir(exist_ok=True)
        player_temp = world_temp / "PlayerData"
        player_temp.mkdir(exist_ok=True)

        # Organize extracted files into proper structure
        extracted_files = list(extract_temp.glob("*.sav"))

        for save_file in extracted_files:
            # Determine output path based on file type
            if "Player_" in save_file.name:
                output_path = player_temp / save_file.name
            elif save_file.name == "SandboxSettings.ini.sav":
                output_path = world_temp / "SandboxSettings.ini"
            else:
                output_path = world_temp / save_file.name

            # Copy to organized location
            import shutil
            shutil.copy(save_file, output_path)

        # Add all files to save_meta for ZIP packaging
        for file_path in world_temp.rglob("*"):
            if file_path.is_file():
                # Get relative path from world folder
                rel_path = file_path.relative_to(Path(temp_dir.name))
                save_meta.append((str(rel_path), file_path))

    else:
        raise Exception('Unsupported XGP app "%s"' % store_pkg_name)

    return save_meta


def main():
    print("Xbox Game Pass for PC savefile extractor")
    print("========================================")

    games = read_game_list()
    if games is None:
        print("Failed to read game list. Check that games.json exists and is valid.")
        print()
        print("Press enter to quit")
        input()
        sys.exit(1)

    # Discover supported games
    found_games = discover_games(games)

    if len(found_games) == 0:
        print("No supported games installed")
        print()
        print("Press enter to quit")
        input()
        sys.exit(1)

    print("Installed supported games:")
    for package_name in found_games:
        name: str = games[package_name]["name"]
        print("- %s" % name)

        try:
            user_containers = find_user_containers(package_name)
            if len(user_containers) == 0:
                print(
                    "  No containers for the game, maybe the game is not installed anymore"
                )
                print()
                continue

            for xbox_username_or_id, container_dir in user_containers:
                read_result = read_user_containers(container_dir)
                store_pkg_name, containers = read_result

                # Create tempfile directory
                # Some save files need this, as we need to create files that do not exist in the XGP save data
                temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)

                # Get save file paths
                save_paths = get_save_paths(games, store_pkg_name, containers, temp_dir)
                if len(save_paths) == 0:
                    continue
                print(f"  Save files for user {xbox_username_or_id}:")
                for file_name, _ in save_paths:
                    print(f"  - {file_name}")

                # Create a ZIP file
                formatted_game_name = (
                    name.replace(" ", "_")
                    .replace(":", "_")
                    .replace("'", "")
                    .replace("!", "")
                    .lower()
                )
                timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
                zip_name = "{}_{}_{}.zip".format(
                    formatted_game_name, xbox_username_or_id, timestamp
                )
                with zipfile.ZipFile(zip_name, "x", zipfile.ZIP_DEFLATED) as save_zip:
                    for file_name, file_path in save_paths:
                        save_zip.write(file_path, arcname=file_name)

                temp_dir.cleanup()

                print()
                print('  Save files written to "%s"' % zip_name)
                print()

        except Exception:
            print(f"  Failed to extract saves:")
            traceback.print_exc()
            print()

    print()
    print("Press enter to quit")
    input()


if __name__ == "__main__":
    main()
