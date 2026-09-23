import os
import sys
import unittest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Dynamic path configuration
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))

if __name__ == "__main__":
    print("=" * 70)
    print("CRYPTEX CLOUD VAULT // AUTOMATED CRYPTOGRAPHIC TEST SUITE")
    print("=" * 70)
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.join(PROJECT_ROOT, "tests"), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("\nALL CRYPTOGRAPHIC & INTEGRITY TESTS PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\nTEST FAILURES DETECTED!")
        sys.exit(1)
