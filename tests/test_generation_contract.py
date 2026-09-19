"""Contract checks that do not require a CUDA device or model weights."""
from __future__ import annotations

import unittest

from scripts.generate_chemllama import extract_smiles, h100_device_record


class _Cuda:
    def __init__(self, names): self.names = names
    def is_available(self): return True
    def device_count(self): return len(self.names)
    def get_device_name(self, index): return self.names[index]
    def get_device_properties(self, index): return type("Props", (), {"uuid": f"GPU-{index}"})()


class _Torch:
    __version__ = "test"
    version = type("Version", (), {"cuda": "test"})()
    def __init__(self, names): self.cuda = _Cuda(names)


class GenerationContractTests(unittest.TestCase):
    def test_h100_guard_accepts_h100_and_rejects_a6000_before_loading(self):
        self.assertEqual(h100_device_record(_Torch(["NVIDIA H100 SXM5"]))["visible_device_count"], 1)
        with self.assertRaisesRegex(RuntimeError, "non-H100"):
            h100_device_record(_Torch(["NVIDIA RTX A6000"]))
        with self.assertRaisesRegex(RuntimeError, "non-H100"):
            h100_device_record(_Torch(["NVIDIA A100"]))

    def test_seed_echo_is_not_a_candidate(self):
        seed = "CCO"
        extracted, reason = extract_smiles(seed, seed)
        self.assertIsNone(extracted)
        self.assertEqual(reason, "no_parseable_new_smiles")


if __name__ == "__main__":
    unittest.main()
