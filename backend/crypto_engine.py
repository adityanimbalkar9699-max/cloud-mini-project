import os
import json
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

# Dynamic Root Path Resolution
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

DEFAULT_KEY_PATH = os.path.join(BACKEND_DIR, "secret.key")
DEFAULT_STORAGE_DIR = os.path.join(PROJECT_ROOT, "storage_blocks")
DEFAULT_RESTORED_DIR = os.path.join(PROJECT_ROOT, "restored")
BLOCK_SIZE = 512 * 1024  # 512 KB (Default)

def get_or_create_key(key_path=None):
    if key_path is None:
        key_path = DEFAULT_KEY_PATH
    os.makedirs(os.path.dirname(key_path), exist_ok=True)
    if os.path.exists(key_path):
        with open(key_path, "rb") as f:
            return f.read()
    key = AESGCM.generate_key(bit_length=256)
    with open(key_path, "wb") as f:
        f.write(key)
    return key

def calculate_sha256_bytes(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()

def calculate_sha256_file(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def chunk_and_encrypt(file_path, block_size=BLOCK_SIZE, storage_dir=None, key_path=None):
    if storage_dir is None:
        storage_dir = DEFAULT_STORAGE_DIR
    if key_path is None:
        key_path = DEFAULT_KEY_PATH

    key = get_or_create_key(key_path)
    aesgcm = AESGCM(key)
    os.makedirs(storage_dir, exist_ok=True)

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    orig_sha256 = calculate_sha256_bytes(file_bytes)
    filename = os.path.basename(file_path)
    total_size = len(file_bytes)

    manifest = {
        "filename": filename,
        "original_size": total_size,
        "sha256": orig_sha256,
        "block_size": block_size,
        "cipher": "AES-256-GCM",
        "blocks": []
    }

    # Handle 0-byte file edge case safely
    if total_size == 0:
        chunks = [b""]
    else:
        chunks = [file_bytes[i:i + block_size] for i in range(0, total_size, block_size)]

    for idx, chunk in enumerate(chunks):
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        encrypted_chunk = aesgcm.encrypt(nonce, chunk, None)
        chunk_sha256 = calculate_sha256_bytes(chunk)

        block_filename = f"block_{idx}.enc"
        block_path = os.path.join(storage_dir, block_filename)

        # Prepend 12-byte nonce to payload: [12-byte nonce][ciphertext + 16-byte auth tag]
        with open(block_path, "wb") as bf:
            bf.write(nonce + encrypted_chunk)

        manifest["blocks"].append({
            "block_index": idx,
            "block_file": block_filename,
            "size": len(encrypted_chunk) + 12,
            "plain_size": len(chunk),
            "block_sha256": chunk_sha256
        })

    manifest_path = os.path.join(storage_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=4)

    return manifest_path

def decrypt_and_reassemble(manifest_path=None, restored_dir=None, key_path=None):
    if storage_dir_default := DEFAULT_STORAGE_DIR:
        if manifest_path is None:
            manifest_path = os.path.join(storage_dir_default, "manifest.json")
    if restored_dir is None:
        restored_dir = DEFAULT_RESTORED_DIR
    if key_path is None:
        key_path = DEFAULT_KEY_PATH

    key = get_or_create_key(key_path)
    aesgcm = AESGCM(key)
    os.makedirs(restored_dir, exist_ok=True)

    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Manifest file not found at: {manifest_path}")

    with open(manifest_path, "r", encoding="utf-8") as mf:
        manifest = json.load(mf)

    storage_dir = os.path.dirname(manifest_path)
    restored_bytes = bytearray()
    tampered_blocks = []

    for block_info in sorted(manifest["blocks"], key=lambda x: x["block_index"]):
        block_path = os.path.join(storage_dir, block_info["block_file"])
        if not os.path.exists(block_path):
            tampered_blocks.append((block_info["block_file"], "Block file missing"))
            continue

        with open(block_path, "rb") as bf:
            data = bf.read()
            if len(data) < 12:
                tampered_blocks.append((block_info["block_file"], "Invalid block size"))
                continue
            nonce = data[:12]
            ciphertext = data[12:]
            try:
                decrypted_chunk = aesgcm.decrypt(nonce, ciphertext, None)
                restored_bytes.extend(decrypted_chunk)
            except InvalidTag:
                tampered_blocks.append((block_info["block_file"], "GCM Tag Mismatch / Tamper Detected"))

    if tampered_blocks:
        return {
            "restored_path": None,
            "sha256": None,
            "verified": False,
            "tampered_blocks": tampered_blocks,
            "error": f"Cryptographic integrity failed: {len(tampered_blocks)} block(s) tampered or corrupted."
        }

    restored_file_path = os.path.join(restored_dir, manifest["filename"])
    with open(restored_file_path, "wb") as rf:
        rf.write(restored_bytes)

    restored_sha256 = calculate_sha256_bytes(bytes(restored_bytes))
    integrity_verified = restored_sha256 == manifest["sha256"]

    return {
        "restored_path": restored_file_path,
        "sha256": restored_sha256,
        "verified": integrity_verified,
        "tampered_blocks": [],
        "original_sha256": manifest["sha256"]
    }
