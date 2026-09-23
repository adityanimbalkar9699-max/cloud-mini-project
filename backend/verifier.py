import os
import hashlib

def calculate_sha256(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found for hash calculation: {file_path}")
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verify_integrity(original_path, restored_path):
    orig_size = os.path.getsize(original_path) if os.path.exists(original_path) else -1
    rest_size = os.path.getsize(restored_path) if os.path.exists(restored_path) else -1

    orig_hash = calculate_sha256(original_path)
    rest_hash = calculate_sha256(restored_path)
    match = (orig_hash == rest_hash) and (orig_size == rest_size)

    return {
        "original_path": original_path,
        "restored_path": restored_path,
        "original_hash": orig_hash,
        "restored_hash": rest_hash,
        "original_size": orig_size,
        "restored_size": rest_size,
        "match": match
    }
