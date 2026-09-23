import os
import sys
import shutil
import tempfile
import unittest

# Ensure backend directory is in python path
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from crypto_engine import chunk_and_encrypt, decrypt_and_reassemble
from verifier import verify_integrity

class TestCryptoEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="cryptex_test_")
        self.sample_file = os.path.join(self.test_dir, "sample_payload.dat")
        # Generate 256 KB test binary payload
        self.test_payload = os.urandom(256 * 1024)
        with open(self.sample_file, "wb") as f:
            f.write(self.test_payload)

    def test_encryption_decryption_pipeline(self):
        storage_dir = os.path.join(self.test_dir, "storage_blocks")
        restored_dir = os.path.join(self.test_dir, "restored")
        key_path = os.path.join(self.test_dir, "test.key")

        # 1. Chunk and Encrypt with 64KB blocks
        manifest_path = chunk_and_encrypt(
            self.sample_file,
            block_size=64 * 1024,
            storage_dir=storage_dir,
            key_path=key_path
        )
        self.assertTrue(os.path.exists(manifest_path))

        # 2. Decrypt and Reassemble
        result = decrypt_and_reassemble(
            manifest_path=manifest_path,
            restored_dir=restored_dir,
            key_path=key_path
        )
        self.assertTrue(result["verified"])
        self.assertTrue(os.path.exists(result["restored_path"]))

        # 3. Verify SHA-256 Parity Match
        verification = verify_integrity(self.sample_file, result["restored_path"])
        self.assertTrue(verification["match"])
        self.assertEqual(verification["original_hash"], verification["restored_hash"])

    def test_block_tamper_detection(self):
        storage_dir = os.path.join(self.test_dir, "storage_tamper_blocks")
        restored_dir = os.path.join(self.test_dir, "restored_tamper")
        key_path = os.path.join(self.test_dir, "test.key")

        manifest_path = chunk_and_encrypt(
            self.sample_file,
            block_size=64 * 1024,
            storage_dir=storage_dir,
            key_path=key_path
        )

        # Corrupt block 0 by altering ciphertext byte
        block_0_path = os.path.join(storage_dir, "block_0.enc")
        with open(block_0_path, "rb") as bf:
            block_bytes = bytearray(bf.read())

        # Modify byte in ciphertext area (after 12-byte nonce)
        block_bytes[20] ^= 0xFF

        with open(block_0_path, "wb") as bf:
            bf.write(block_bytes)

        # Decrypt should detect GCM tag mismatch
        result = decrypt_and_reassemble(
            manifest_path=manifest_path,
            restored_dir=restored_dir,
            key_path=key_path
        )
        self.assertFalse(result["verified"])
        self.assertTrue(len(result["tampered_blocks"]) > 0)

    def test_variable_block_sizes(self):
        for block_size in [32 * 1024, 128 * 1024, 512 * 1024]:
            storage_dir = os.path.join(self.test_dir, f"blocks_{block_size}")
            restored_dir = os.path.join(self.test_dir, f"restored_{block_size}")
            key_path = os.path.join(self.test_dir, "test.key")

            manifest_path = chunk_and_encrypt(
                self.sample_file,
                block_size=block_size,
                storage_dir=storage_dir,
                key_path=key_path
            )

            result = decrypt_and_reassemble(
                manifest_path=manifest_path,
                restored_dir=restored_dir,
                key_path=key_path
            )
            self.assertTrue(result["verified"], f"Failed for block size: {block_size}")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
