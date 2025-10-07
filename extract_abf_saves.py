#!/usr/bin/env python3
"""
Abiotic Factor ABF Archive Extractor
Extracts individual GVAS save files from ABF_SAVE_VERSION archive

Requirements:
- oo2core DLL (from Abiotic Factor or any UE5 game)
- Place oo2core_*_win64.dll in same directory as this script
"""

import struct
import os
import sys
import ctypes
from pathlib import Path

def find_oodle_dll():
    """Find oo2core DLL in current directory or system"""

    # Check current directory
    current_dir = Path(__file__).parent

    # Look for various versions
    dll_patterns = [
        'oo2core_9_win64.dll',
        'oo2core_8_win64.dll',
        'oo2core_7_win64.dll',
        'oo2core_6_win64.dll',
        'oo2core_5_win64.dll',
    ]

    for pattern in dll_patterns:
        dll_path = current_dir / pattern
        if dll_path.exists():
            print(f"✓ Found Oodle DLL: {dll_path}")
            return str(dll_path)

    # Check if user provided path
    if len(sys.argv) > 2:
        dll_path = Path(sys.argv[2])
        if dll_path.exists():
            return str(dll_path)

    return None

def load_oodle_dll(dll_path):
    """Load Oodle DLL and get decompress function"""

    try:
        oodle = ctypes.CDLL(dll_path)

        # Function signature: OodleLZ_Decompress
        # int OodleLZ_Decompress(
        #     const void* compressed_data,
        #     size_t compressed_size,
        #     void* output_buffer,
        #     size_t output_size,
        #     int fuzz, int crc, int verbose,
        #     void* dst_base, size_t dst_base_size,
        #     void* fpCallback, void* callback_userdata,
        #     void* decoder_memory, size_t decoder_memory_size,
        #     int thread_phase
        # )

        decompress = oodle.OodleLZ_Decompress
        decompress.argtypes = [
            ctypes.c_void_p,  # compressed_data
            ctypes.c_size_t,  # compressed_size
            ctypes.c_void_p,  # output_buffer
            ctypes.c_size_t,  # output_size
            ctypes.c_int,     # fuzz
            ctypes.c_int,     # crc
            ctypes.c_int,     # verbose
            ctypes.c_void_p,  # dst_base
            ctypes.c_size_t,  # dst_base_size
            ctypes.c_void_p,  # fpCallback
            ctypes.c_void_p,  # callback_userdata
            ctypes.c_void_p,  # decoder_memory
            ctypes.c_size_t,  # decoder_memory_size
            ctypes.c_int,     # thread_phase
        ]
        decompress.restype = ctypes.c_int

        print("✓ Loaded OodleLZ_Decompress function")
        return decompress

    except Exception as e:
        print(f"✗ Failed to load Oodle DLL: {e}")
        return None

def parse_toc(data):
    """Parse ABF archive table of contents"""

    offset = 0

    # Header
    magic_len = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4
    magic = data[offset:offset+magic_len-1].decode('ascii')
    offset += magic_len

    version = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4

    total_uncomp_size = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4

    file_count = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4

    print(f"Archive: {magic} v{version}")
    print(f"Expected uncompressed size: {total_uncomp_size:,} bytes")
    print(f"File count (claimed): {file_count}")

    entries = []

    # Entry 1 (special format)
    len1 = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4
    len2 = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4
    path = data[offset:offset+len2-1].decode('utf-8')
    offset += len2
    size = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4
    class_len = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4
    class_path = data[offset:offset+class_len-1].decode('utf-8')
    offset += class_len
    reserved = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4

    entries.append({'path': path, 'size': size, 'class': class_path})

    # Entries 2-31
    for i in range(30):
        try:
            path_len = struct.unpack('<I', data[offset:offset+4])[0]
            if path_len > 500:
                break
            offset += 4
            path = data[offset:offset+path_len-1].decode('utf-8')
            offset += path_len
            size = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            class_len = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            class_path = data[offset:offset+class_len-1].decode('utf-8')
            offset += class_len
            reserved = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4

            entries.append({'path': path, 'size': size, 'class': class_path})
        except:
            break

    print(f"Found {len(entries)} TOC entries")
    print(f"TOC ends at: 0x{offset:04x}")

    return entries, offset, total_uncomp_size

def decompress_oodle(decompress_func, compressed_data, uncompressed_size):
    """Decompress Oodle compressed data"""

    print(f"\nDecompressing {len(compressed_data):,} bytes with Oodle...")

    # Allocate output buffer
    output_buffer = ctypes.create_string_buffer(uncompressed_size)

    # Call OodleLZ_Decompress
    result = decompress_func(
        ctypes.c_char_p(compressed_data),  # compressed_data
        len(compressed_data),               # compressed_size
        ctypes.byref(output_buffer),        # output_buffer
        uncompressed_size,                  # output_size
        0,  # fuzz
        0,  # crc
        0,  # verbose
        None,  # dst_base
        0,  # dst_base_size
        None,  # fpCallback
        None,  # callback_userdata
        None,  # decoder_memory
        0,  # decoder_memory_size
        0,  # thread_phase
    )

    if result != uncompressed_size:
        raise Exception(f"Decompression failed! Expected {uncompressed_size}, got {result}")

    print(f"✓ Decompressed to {result:,} bytes")
    return output_buffer.raw

def extract_archive(archive_path, output_dir, oodle_dll_path=None):
    """Main extraction function"""

    print("="*70)
    print("ABIOTIC FACTOR ABF ARCHIVE EXTRACTOR")
    print("="*70)
    print()

    # Find and load Oodle DLL
    if not oodle_dll_path:
        oodle_dll_path = find_oodle_dll()

    if not oodle_dll_path:
        print("\n" + "="*70)
        print("ERROR: Oodle DLL not found!")
        print("="*70)
        print("\nPlease obtain oo2core_*_win64.dll from:")
        print("1. Abiotic Factor Steam installation")
        print("2. Any Unreal Engine 5 game installation")
        print("3. Unreal Engine 5 installation")
        print()
        print("Common locations:")
        print("  Steam: C:\\Program Files (x86)\\Steam\\steamapps\\common\\AbioticFactor\\")
        print("  UE5: C:\\Program Files\\Epic Games\\UE_5.*\\Engine\\Binaries\\ThirdParty\\Oodle\\")
        print()
        print("Copy the DLL to this script's directory and run again.")
        return False

    decompress_func = load_oodle_dll(oodle_dll_path)
    if not decompress_func:
        return False

    # Load archive
    print(f"\nLoading archive: {archive_path}")
    with open(archive_path, 'rb') as f:
        data = f.read()

    print(f"Archive size: {len(data):,} bytes")

    # Parse TOC
    entries, data_offset, expected_size = parse_toc(data)

    # Parse compression header
    data_section = data[data_offset:]
    format_byte = data_section[0]
    comp_size = struct.unpack('<I', data_section[4:8])[0]

    print(f"\nCompression format: 0x{format_byte:02x}")
    print(f"Compressed size: {comp_size:,} bytes")

    # Extract compressed data
    compressed_data = data_section[8:8+comp_size]

    # Decompress
    decompressed = decompress_oodle(decompress_func, compressed_data, expected_size)

    # Verify
    if len(decompressed) != expected_size:
        print(f"\n✗ Size mismatch! Expected {expected_size}, got {len(decompressed)}")
        return False

    # Check for GVAS
    gvas_count = decompressed.count(b'GVAS')
    print(f"\n✓ Found {gvas_count} GVAS signatures in decompressed data")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Extract files
    print(f"\n" + "="*70)
    print("EXTRACTING FILES")
    print("="*70)
    print()

    offset = 0
    for i, entry in enumerate(entries):
        filename = entry['path'].split('/')[-1]
        output_path = os.path.join(output_dir, f"{filename}.sav")

        file_data = decompressed[offset:offset+entry['size']]
        offset += entry['size']

        # Check if it's GVAS
        is_gvas = file_data[:4] == b'GVAS'
        status = "GVAS ✓" if is_gvas else "?"

        print(f"  {i+1:2d}. {filename:40s} {entry['size']:9,} bytes [{status}]")

        with open(output_path, 'wb') as f:
            f.write(file_data)

    print(f"\n✓✓✓ Extraction complete!")
    print(f"Output directory: {output_dir}")
    print(f"Extracted {len(entries)} files")

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_abf_saves.py <archive.sav> [output_dir] [oodle_dll_path]")
        print()
        print("Examples:")
        print("  python extract_abf_saves.py Erebus-WC.sav")
        print("  python extract_abf_saves.py Erebus-WC.sav extracted/")
        print("  python extract_abf_saves.py Erebus-WC.sav extracted/ oo2core_9_win64.dll")
        sys.exit(1)

    archive_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "extracted"
    oodle_dll = sys.argv[3] if len(sys.argv) > 3 else None

    success = extract_archive(archive_path, output_dir, oodle_dll)

    if success:
        print("\n" + "="*70)
        print("NEXT STEPS")
        print("="*70)
        print("\n1. Verify extracted files are valid GVAS")
        print("2. Convert to Steam format (rename player IDs, create folder structure)")
        print("3. Copy to Steam save location")
        print("4. Test loading in Steam version")
    else:
        print("\n✗ Extraction failed")
        sys.exit(1)
