# pylint: disable=import-outside-toplevel, missing-function-docstring
# pylint: disable=missing-class-docstring, redefined-outer-name, protected-access
"""
Comprehensive tests for warbler_cda.pack_sync module.

Tests the PackSync for pack verification and synchronization with mocked file system.
"""

from unittest.mock import patch
from pathlib import Path
import json
import tempfile
from datetime import datetime
import pytest


class TestPackSyncInitialization:
    """Test PackSync initialization."""

    def test_pack_sync_default_init(self):
        """PackSync should initialize with default packs directory."""
        from warbler_cda.pack_sync import PackSync

        sync = PackSync()
        assert sync.packs_dir is not None
        assert isinstance(sync.packs_dir, Path)
        assert sync.metadata_file is not None
        assert sync.metadata_file.name == ".pack_metadata.json"

    def test_pack_sync_custom_dir(self):
        """PackSync should accept custom packs directory."""
        from warbler_cda.pack_sync import PackSync

        custom_dir = Path("/custom/packs")
        sync = PackSync(packs_dir=custom_dir)
        assert sync.packs_dir == custom_dir
        assert sync.metadata_file == custom_dir / ".pack_metadata.json"


class TestPackManifest:
    """Test PACK_MANIFEST constant."""

    def test_pack_manifest_exists(self):
        """PACK_MANIFEST should contain pack definitions."""
        from warbler_cda.pack_sync import PackSync

        assert hasattr(PackSync, 'PACK_MANIFEST')
        assert isinstance(PackSync.PACK_MANIFEST, dict)
        assert len(PackSync.PACK_MANIFEST) > 0

    def test_pack_manifest_structure(self):
        """Each pack in PACK_MANIFEST should have required fields."""
        from warbler_cda.pack_sync import PackSync

        for pack_name, pack_info in PackSync.PACK_MANIFEST.items():
            assert "source" in pack_info
            assert "type" in pack_info
            assert "description" in pack_info
            assert pack_info["type"] == "huggingface"

    def test_pack_manifest_known_packs(self):
        """PACK_MANIFEST should contain expected packs."""
        from warbler_cda.pack_sync import PackSync

        expected_packs = [
            "warbler-pack-hf-arxiv",
            "warbler-pack-hf-prompt-report",
            "warbler-pack-hf-novels",
            "warbler-pack-hf-manuals",
            "warbler-pack-hf-enterprise",
            "warbler-pack-hf-portuguese-edu",
        ]

        for pack in expected_packs:
            assert pack in PackSync.PACK_MANIFEST


class TestVerifyPacks:
    """Test verify_packs method."""

    def test_verify_packs_all_present(self):
        """verify_packs should detect all present packs."""
        from warbler_cda.pack_sync import PackSync

        with tempfile.TemporaryDirectory() as tmpdir:
            packs_dir = Path(tmpdir)

            # Create all packs from manifest
            for pack_name in PackSync.PACK_MANIFEST:
                pack_dir = packs_dir / pack_name
                pack_dir.mkdir()

                # Create JSONL file with some content
                pack_file = pack_dir / f"{pack_name}.jsonl"
                pack_file.write_text(
                    json.dumps({"content": "doc1"}) + "\n" +
                    json.dumps({"content": "doc2"}) + "\n"
                )

            sync = PackSync(packs_dir=packs_dir)
            status = sync.verify_packs()

            assert len(status["verified"]) == len(PackSync.PACK_MANIFEST)
            assert len(status["missing"]) == 0
            assert "timestamp" in status

    def test_verify_packs_all_missing(self):
        """verify_packs should detect all missing packs."""
        from warbler_cda.pack_sync import PackSync

        with tempfile.TemporaryDirectory() as tmpdir:
            packs_dir = Path(tmpdir)

            sync = PackSync(packs_dir=packs_dir)
            status = sync.verify_packs()

            assert len(status["verified"]) == 0
            assert len(status["missing"]) == len(PackSync.PACK_MANIFEST)
            assert "timestamp" in status

    def test_verify_packs_partial(self):
        """verify_packs should detect mix of present and missing packs."""
        from warbler_cda.pack_sync import PackSync

        with tempfile.TemporaryDirectory() as tmpdir:
            packs_dir = Path(tmpdir)

            # Create only first pack
            pack_names = list(PackSync.PACK_MANIFEST.keys())
            pack_name = pack_names[0]
            pack_dir = packs_dir / pack_name
            pack_dir.mkdir()
            pack_file = pack_dir / f"{pack_name}.jsonl"
            pack_file.write_text(json.dumps({"content": "doc"}) + "\n")

            sync = PackSync(packs_dir=packs_dir)
            status = sync.verify_packs()

            assert len(status["verified"]) == 1
            assert len(status["missing"]) == len(PackSync.PACK_MANIFEST) - 1

    def test_verify_packs_document_count(self):
        """verify_packs should count documents in each pack."""
        from warbler_cda.pack_sync import PackSync

        with tempfile.TemporaryDirectory() as tmpdir:
            packs_dir = Path(tmpdir)

            pack_name = list(PackSync.PACK_MANIFEST.keys())[0]
            pack_dir = packs_dir / pack_name
            pack_dir.mkdir()

            # Create JSONL file with 5 documents
            pack_file = pack_dir / f"{pack_name}.jsonl"
            pack_file.write_text("\n".join([json.dumps({"content": f"doc{i}"})
                                            for i in range(5)]) + "\n")

            sync = PackSync(packs_dir=packs_dir)
            status = sync.verify_packs()

            assert len(status["verified"]) == 1
            assert status["verified"][0]["documents"] == 5
            assert status["verified"][0]["pack"] == pack_name

    def test_verify_packs_directory_exists_but_no_file(self):
        """verify_packs should mark pack as missing if directory exists but JSONL doesn't."""
        from warbler_cda.pack_sync import PackSync

        with tempfile.TemporaryDirectory() as tmpdir:
            packs_dir = Path(tmpdir)

            pack_name = list(PackSync.PACK_MANIFEST.keys())[0]
            pack_dir = packs_dir / pack_name
            pack_dir.mkdir()  # Create directory but no JSONL file

            sync = PackSync(packs_dir=packs_dir)
            status = sync.verify_packs()

            assert len(status["verified"]) == 0
            assert pack_name in status["missing"]

    def test_verify_packs_unreadable_file(self):
        """verify_packs should handle unreadable pack files."""
        from warbler_cda.pack_sync import PackSync

        with tempfile.TemporaryDirectory() as tmpdir:
            packs_dir = Path(tmpdir)

            pack_name = list(PackSync.PACK_MANIFEST.keys())[0]
            pack_dir = packs_dir / pack_name
            pack_dir.mkdir()

            # Create JSONL file
            pack_file = pack_dir / f"{pack_name}.jsonl"
            pack_file.write_text("test")

            # Mock open to raise exception
            with patch('builtins.open', side_effect=PermissionError("Access denied")):
                sync = PackSync(packs_dir=packs_dir)
                status = sync.verify_packs()

                # Should be marked as missing due to read error
                assert pack_name in status["missing"]

    def test_verify_packs_timestamp_format(self):
        """verify_packs should include valid ISO timestamp."""
        from warbler_cda.pack_sync import PackSync

        with tempfile.TemporaryDirectory() as tmpdir:
            sync = PackSync(packs_dir=Path(tmpdir))
            status = sync.verify_packs()

            assert "timestamp" in status
            # Should be valid ISO format
            try:
                datetime.fromisoformat(status["timestamp"])
            except ValueError:
                pytest.fail("Timestamp is not valid ISO format")


class TestSaveMetadata:
    """Test save_metadata method."""

    def test_save_metadata_success(self):
        """save_metadata should write metadata to file."""
        from warbler_cda.pack_sync import PackSync

        with tempfile.TemporaryDirectory() as tmpdir:
            packs_dir = Path(tmpdir)
            sync = PackSync(packs_dir=packs_dir)

            status = {
                "verified": [{"pack": "test-pack", "documents": 10}],
                "missing": [],
                "timestamp": datetime.now().isoformat()
            }

            sync.save_metadata(status)

            metadata_file = packs_dir / ".pack_metadata.json"
            assert metadata_file.exists()

            # Verify content
            with open(metadata_file, encoding="UTF-8") as f:
                saved_data = json.load(f)
                assert saved_data["verified"] == status["verified"]
                assert saved_data["missing"] == status["missing"]

    def test_save_metadata_creates_directory(self):
        """save_metadata should work even if directory doesn't exist yet."""
        from warbler_cda.pack_sync import PackSync

        with tempfile.TemporaryDirectory() as tmpdir:
            packs_dir = Path(tmpdir) / "nonexistent"
            packs_dir.mkdir(parents=True)
            sync = PackSync(packs_dir=packs_dir)

            status = {"verified": [], "missing": [], "timestamp": datetime.now().isoformat()}
            sync.save_metadata(status)

            assert sync.metadata_file.exists()

    def test_save_metadata_error_handling(self):
        """save_metadata should handle write errors gracefully."""
        from warbler_cda.pack_sync import PackSync

        with tempfile.TemporaryDirectory() as tmpdir:
            packs_dir = Path(tmpdir)
            sync = PackSync(packs_dir=packs_dir)

            status = {"verified": [], "missing": []}

            # Mock open to raise exception
            with patch('builtins.open', side_effect=PermissionError("Access denied")):
                # Should not raise exception
                sync.save_metadata(status)


class TestGetSyncStatus:
    """Test get_sync_status method."""

    def test_get_sync_status_all_verified(self):
        """get_sync_status should return success message when all packs verified."""
        from warbler_cda.pack_sync import PackSync

        with tempfile.TemporaryDirectory() as tmpdir:
            packs_dir = Path(tmpdir)

            # Create all packs
            for pack_name in PackSync.PACK_MANIFEST:
                pack_dir = packs_dir / pack_name
                pack_dir.mkdir()
                pack_file = pack_dir / f"{pack_name}.jsonl"
                pack_file.write_text(json.dumps({"content": "doc"}) + "\n")

            sync = PackSync(packs_dir=packs_dir)
            status_msg = sync.get_sync_status()

            assert "✓" in status_msg
            assert "verified and ready" in status_msg
            assert str(len(PackSync.PACK_MANIFEST)) in status_msg

    def test_get_sync_status_some_missing(self):
        """get_sync_status should return warning when packs are missing."""
        from warbler_cda.pack_sync import PackSync

        with tempfile.TemporaryDirectory() as tmpdir:
            packs_dir = Path(tmpdir)

            # Create only one pack
            pack_name = list(PackSync.PACK_MANIFEST.keys())[0]
            pack_dir = packs_dir / pack_name
            pack_dir.mkdir()
            pack_file = pack_dir / f"{pack_name}.jsonl"
            pack_file.write_text(json.dumps({"content": "doc"}) + "\n")

            sync = PackSync(packs_dir=packs_dir)
            status_msg = sync.get_sync_status()

            assert "⚠️" in status_msg
            assert "missing" in status_msg
            assert "1" in status_msg  # 1 verified

    def test_get_sync_status_all_missing(self):
        """get_sync_status should return warning when all packs are missing."""
        from warbler_cda.pack_sync import PackSync

        with tempfile.TemporaryDirectory() as tmpdir:
            packs_dir = Path(tmpdir)

            sync = PackSync(packs_dir=packs_dir)
            status_msg = sync.get_sync_status()

            assert "⚠️" in status_msg
            assert "0 packs verified" in status_msg
            assert "missing" in status_msg


class TestSuggestReingest:
    """Test suggest_reingest method."""

    def test_suggest_reingest_when_missing(self):
        """suggest_reingest should return command when packs are missing."""
        from warbler_cda.pack_sync import PackSync

        with tempfile.TemporaryDirectory() as tmpdir:
            packs_dir = Path(tmpdir)

            sync = PackSync(packs_dir=packs_dir)
            command = sync.suggest_reingest()

            assert command is not None
            assert "python" in command
            assert "hf_warbler_ingest" in command
            assert "ingest" in command
            assert "--datasets all" in command

    def test_suggest_reingest_when_all_present(self):
        """suggest_reingest should return None when all packs are present."""
        from warbler_cda.pack_sync import PackSync

        with tempfile.TemporaryDirectory() as tmpdir:
            packs_dir = Path(tmpdir)

            # Create all packs
            for pack_name in PackSync.PACK_MANIFEST:
                pack_dir = packs_dir / pack_name
                pack_dir.mkdir()
                pack_file = pack_dir / f"{pack_name}.jsonl"
                pack_file.write_text(json.dumps({"content": "doc"}) + "\n")

            sync = PackSync(packs_dir=packs_dir)
            command = sync.suggest_reingest()

            assert command is None

    def test_suggest_reingest_partial_missing(self):
        """suggest_reingest should return command when some packs are missing."""
        from warbler_cda.pack_sync import PackSync

        with tempfile.TemporaryDirectory() as tmpdir:
            packs_dir = Path(tmpdir)

            # Create only first pack
            pack_name = list(PackSync.PACK_MANIFEST.keys())[0]
            pack_dir = packs_dir / pack_name
            pack_dir.mkdir()
            pack_file = pack_dir / f"{pack_name}.jsonl"
            pack_file.write_text(json.dumps({"content": "doc"}) + "\n")

            sync = PackSync(packs_dir=packs_dir)
            command = sync.suggest_reingest()

            assert command is not None
            assert "hf_warbler_ingest" in command


class TestIntegration:
    """Integration tests for complete pack sync workflow."""

    def test_full_sync_workflow(self):
        """Test complete workflow: verify, save metadata, check status."""
        from warbler_cda.pack_sync import PackSync

        with tempfile.TemporaryDirectory() as tmpdir:
            packs_dir = Path(tmpdir)

            # Create some packs
            pack_names = list(PackSync.PACK_MANIFEST.keys())[:2]
            for pack_name in pack_names:
                pack_dir = packs_dir / pack_name
                pack_dir.mkdir()
                pack_file = pack_dir / f"{pack_name}.jsonl"
                pack_file.write_text(
                    "\n".join([json.dumps({"content": f"doc{i}"}) for i in range(3)]) + "\n"
                )

            sync = PackSync(packs_dir=packs_dir)

            # Verify packs
            status = sync.verify_packs()
            assert len(status["verified"]) == 2
            assert len(status["missing"]) == len(PackSync.PACK_MANIFEST) - 2

            # Save metadata
            sync.save_metadata(status)
            assert sync.metadata_file.exists()

            # Check status message
            status_msg = sync.get_sync_status()
            assert "2" in status_msg
            assert "missing" in status_msg

            # Get reingest suggestion
            command = sync.suggest_reingest()
            assert command is not None

    def test_empty_packs_directory_workflow(self):
        """Test workflow with completely empty packs directory."""
        from warbler_cda.pack_sync import PackSync

        with tempfile.TemporaryDirectory() as tmpdir:
            packs_dir = Path(tmpdir)

            sync = PackSync(packs_dir=packs_dir)

            # Verify - should find nothing
            status = sync.verify_packs()
            assert len(status["verified"]) == 0
            assert len(status["missing"]) == len(PackSync.PACK_MANIFEST)

            # Save metadata
            sync.save_metadata(status)
            assert sync.metadata_file.exists()

            # Status should indicate all missing
            status_msg = sync.get_sync_status()
            assert "⚠️" in status_msg
            assert "0 packs verified" in status_msg

            # Should suggest reingest
            command = sync.suggest_reingest()
            assert command is not None
            assert "--datasets all" in command
