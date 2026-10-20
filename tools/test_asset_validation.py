"""Run with python -m unittest tools.test_asset_validation."""
import tempfile
import unittest
from pathlib import Path

from tools.assemble_assets import validate_powershell_encoding


class PowerShellEncodingTests(unittest.TestCase):
    def test_non_ascii_without_bom_is_rejected_before_packaging(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "resolve.ps1"
            script.write_bytes('throw "未找到"'.encode("utf-8"))
            with self.assertRaisesRegex(ValueError, "requires UTF-8 BOM"):
                validate_powershell_encoding(root)
            script.write_bytes(b"\xef\xbb\xbf" + script.read_bytes())
            validate_powershell_encoding(root)

    def test_ascii_script_remains_portable_without_bom(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "resolve.ps1").write_bytes(b'throw "Not found"')
            validate_powershell_encoding(root)
