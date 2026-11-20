#!/usr/bin/env python3
"""Unit tests for verified_release_craft.py."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import verified_release_craft as vrc  # noqa: E402


class TestVerifiedReleaseCraft(unittest.TestCase):
    """Tests for SHA-256 manifest, crypto pattern, and UI slop scanners."""

    def test_manifest_generate_and_verify(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "bundle.js").write_text("console.log('ok');\n", encoding="utf-8")
            manifest = root / "SHA256SUMS.json"

            rc_gen = vrc.main(["sha256-manifest", "--dir", str(root), "--out", str(manifest)])
            self.assertEqual(rc_gen, 0)
            self.assertTrue(manifest.is_file())

            rc_ok = vrc.main(["verify-manifest", "--manifest", str(manifest)])
            self.assertEqual(rc_ok, 0)

            (root / "bundle.js").write_text("console.log('tampered');\n", encoding="utf-8")
            rc_bad = vrc.main(["verify-manifest", "--manifest", str(manifest)])
            self.assertEqual(rc_bad, 1)

    def test_verify_blocks_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "SHA256SUMS.json"
            manifest.write_text(
                json.dumps({"algorithm": "sha256", "artifacts": {"../escape.txt": "0" * 64}}),
                encoding="utf-8",
            )
            rc = vrc.main(["verify-manifest", "--manifest", str(manifest)])
            self.assertEqual(rc, 1)

    def test_crypto_and_ui_slop_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "auth.py").write_text("digest = hashlib.md5(b'data').hexdigest()\n", encoding="utf-8")
            (root / "Hero.tsx").write_text("<footer>Powered by AI</footer>\n", encoding="utf-8")

            self.assertEqual(vrc.main(["check-crypto-patterns", "--dir", str(root)]), 1)
            self.assertEqual(vrc.main(["audit-ui-slop", "--dir", str(root)]), 1)

            (root / "auth.py").write_text("import hashlib\n", encoding="utf-8")
            (root / "Hero.tsx").write_text("<footer>Market Haven</footer>\n", encoding="utf-8")

            self.assertEqual(vrc.main(["check-crypto-patterns", "--dir", str(root)]), 0)
            self.assertEqual(vrc.main(["audit-ui-slop", "--dir", str(root)]), 0)


if __name__ == "__main__":
    unittest.main()
