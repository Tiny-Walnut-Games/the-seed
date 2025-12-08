# pylint: disable=import-outside-toplevel, missing-function-docstring
# pylint: disable=missing-class-docstring, redefined-outer-name, protected-access
"""
Comprehensive tests for warbler_cda.pack_loader module.

Tests the PackLoader for loading Warbler pack data with mocked file system.
"""

from pathlib import Path
import json
import tempfile


class TestPackLoaderInitialization:
    """Test PackLoader initialization."""

    def test_pack_loader_default_init(self):
        """PackLoader should initialize with default packs directory."""
        from warbler_cda.pack_loader import PackLoader

        loader = PackLoader()
        assert loader.packs_dir is not None
        assert isinstance(loader.packs_dir, Path)
        assert not loader.documents

    def test_pack_loader_custom_dir(self):
        """PackLoader should accept custom packs directory."""
        from warbler_cda.pack_loader import PackLoader

        custom_dir = Path("/custom/packs")
        loader = PackLoader(packs_dir=custom_dir)
        assert loader.packs_dir == custom_dir


class TestDiscoverDocuments:
    """Test discover_documents method."""

    def test_discover_documents_missing_directory(self):
        """discover_documents should handle missing packs directory."""
        from warbler_cda.pack_loader import PackLoader

        loader = PackLoader(packs_dir=Path("/nonexistent/path"))
        documents = loader.discover_documents()

        assert not documents
        assert not loader.documents

    def test_discover_documents_empty_directory(self):
        """discover_documents should handle empty packs directory."""
        from warbler_cda.pack_loader import PackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            loader = PackLoader(packs_dir=Path(tmpdir))
            documents = loader.discover_documents()

            assert not documents

    def test_discover_documents_with_packs(self):
        """discover_documents should load documents from valid packs."""
        from warbler_cda.pack_loader import PackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a valid pack
            pack_dir = Path(tmpdir) / "warbler-pack-test"
            pack_dir.mkdir()

            # Create package.json
            package_json = pack_dir / "package.json"
            package_json.write_text(json.dumps({
                "name": "warbler-pack-test",
                "version": "1.0.0"
            }))

            # Create JSONL file
            jsonl_file = pack_dir / "warbler-pack-test.jsonl"
            jsonl_file.write_text(json.dumps({"content": "Test document"}) + "\n")

            loader = PackLoader(packs_dir=Path(tmpdir))
            documents = loader.discover_documents()

            assert len(documents) > 0
            assert loader.documents == documents


class TestIsValidWarblerPack:
    """Test _is_valid_warbler_pack validation."""

    def test_valid_pack_with_package_json(self):
        """_is_valid_warbler_pack should accept pack with package.json."""
        from warbler_cda.pack_loader import PackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "test-pack"
            pack_dir.mkdir()

            # Create valid package.json
            package_json = pack_dir / "package.json"
            package_json.write_text(json.dumps({
                "name": "test-pack",
                "version": "1.0.0"
            }))

            # Create JSONL file
            jsonl_file = pack_dir / "test-pack.jsonl"
            jsonl_file.write_text("")

            loader = PackLoader()
            is_valid = loader._is_valid_warbler_pack(pack_dir, "test-pack", jsonl_file)

            assert is_valid is True

    def test_valid_hf_pack_without_package_json(self):
        """_is_valid_warbler_pack should accept HF packs without package.json."""
        from warbler_cda.pack_loader import PackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "warbler-pack-hf-test"
            pack_dir.mkdir()

            # Create JSONL file
            jsonl_file = pack_dir / "warbler-pack-hf-test.jsonl"
            jsonl_file.write_text("")

            loader = PackLoader()
            is_valid = loader._is_valid_warbler_pack(pack_dir, "warbler-pack-hf-test", jsonl_file)

            assert is_valid is True

    def test_invalid_pack_no_metadata(self):
        """_is_valid_warbler_pack should reject pack without metadata."""
        from warbler_cda.pack_loader import PackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "invalid-pack"
            pack_dir.mkdir()

            jsonl_file = pack_dir / "invalid-pack.jsonl"

            loader = PackLoader()
            is_valid = loader._is_valid_warbler_pack(pack_dir, "invalid-pack", jsonl_file)

            assert is_valid is False

    def test_valid_chunked_pack(self):
        """_is_valid_warbler_pack should accept chunked packs."""
        from warbler_cda.pack_loader import PackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "chunked-pack"
            pack_dir.mkdir()

            # Create package.json with chunked flag
            package_json = pack_dir / "package.json"
            package_json.write_text(json.dumps({
                "name": "chunked-pack",
                "version": "1.0.0",
                "chunked": True
            }))

            # Create chunk files
            chunk1 = pack_dir / "chunked-pack-chunk-001.jsonl"
            chunk1.write_text("")

            jsonl_file = pack_dir / "chunked-pack.jsonl"

            loader = PackLoader()
            is_valid = loader._is_valid_warbler_pack(pack_dir, "chunked-pack", jsonl_file)

            assert is_valid is True

    def test_invalid_chunked_pack_no_chunks(self):
        """_is_valid_warbler_pack should reject chunked pack without chunks."""
        from warbler_cda.pack_loader import PackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "chunked-pack"
            pack_dir.mkdir()

            # Create package.json with chunked flag but no chunk files
            package_json = pack_dir / "package.json"
            package_json.write_text(json.dumps({
                "name": "chunked-pack",
                "version": "1.0.0",
                "chunked": True
            }))

            jsonl_file = pack_dir / "chunked-pack.jsonl"

            loader = PackLoader()
            is_valid = loader._is_valid_warbler_pack(pack_dir, "chunked-pack", jsonl_file)

            assert is_valid is False


class TestLoadJsonlPack:
    """Test _load_jsonl_pack method."""

    def test_load_single_file_pack(self):
        """_load_jsonl_pack should load single-file pack."""
        from warbler_cda.pack_loader import PackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "test-pack"
            pack_dir.mkdir()

            # Create package.json
            package_json = pack_dir / "package.json"
            package_json.write_text(json.dumps({
                "name": "test-pack",
                "version": "1.0.0",
                "chunked": False
            }))

            # Create JSONL file with test data
            jsonl_file = pack_dir / "test-pack.jsonl"
            jsonl_file.write_text(
                json.dumps({"content": "Document 1"}) + "\n" +
                json.dumps({"content": "Document 2"}) + "\n"
            )

            loader = PackLoader()
            documents = loader._load_jsonl_pack(pack_dir, "test-pack")

            assert len(documents) == 2
            assert "Document 1" in documents[0]["content"]
            assert "Document 2" in documents[1]["content"]

    def test_load_chunked_pack(self):
        """_load_jsonl_pack should load chunked pack."""
        from warbler_cda.pack_loader import PackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "chunked-pack"
            pack_dir.mkdir()

            # Create package.json
            package_json = pack_dir / "package.json"
            package_json.write_text(json.dumps({
                "name": "chunked-pack",
                "version": "1.0.0",
                "chunked": True
            }))

            # Create chunk files
            chunk1 = pack_dir / "chunked-pack-chunk-001.jsonl"
            chunk1.write_text(json.dumps({"content": "Chunk 1 Doc 1"}) + "\n")

            chunk2 = pack_dir / "chunked-pack-chunk-002.jsonl"
            chunk2.write_text(json.dumps({"content": "Chunk 2 Doc 1"}) + "\n")

            loader = PackLoader()
            documents = loader._load_jsonl_pack(pack_dir, "chunked-pack")

            assert len(documents) == 2

    def test_load_jsonl_pack_missing_file(self):
        """_load_jsonl_pack should handle missing JSONL file."""
        from warbler_cda.pack_loader import PackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "test-pack"
            pack_dir.mkdir()

            loader = PackLoader()
            documents = loader._load_jsonl_pack(pack_dir, "test-pack")

            assert not documents


class TestLoadJsonlFile:
    """Test _load_jsonl_file method."""

    def test_load_jsonl_file_valid(self):
        """_load_jsonl_file should load valid JSONL file."""
        from warbler_cda.pack_loader import PackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            jsonl_file = Path(tmpdir) / "test.jsonl"
            jsonl_file.write_text(
                json.dumps({"content": "Doc 1"}) + "\n" +
                json.dumps({"content": "Doc 2"}) + "\n"
            )

            loader = PackLoader()
            documents = loader._load_jsonl_file(jsonl_file, "test-pack")

            assert len(documents) == 2

    def test_load_jsonl_file_with_errors(self):
        """_load_jsonl_file should skip invalid lines."""
        from warbler_cda.pack_loader import PackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            jsonl_file = Path(tmpdir) / "test.jsonl"
            jsonl_file.write_text(
                json.dumps({"content": "Doc 1"}) + "\n" +
                "invalid json line\n" +
                json.dumps({"content": "Doc 2"}) + "\n"
            )

            loader = PackLoader()
            documents = loader._load_jsonl_file(jsonl_file, "test-pack")

            # Should load 2 valid documents, skip 1 invalid
            assert len(documents) == 2

    def test_load_jsonl_file_empty_lines(self):
        """_load_jsonl_file should skip empty lines."""
        from warbler_cda.pack_loader import PackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            jsonl_file = Path(tmpdir) / "test.jsonl"
            jsonl_file.write_text(
                json.dumps({"content": "Doc 1"}) + "\n" +
                "\n" +
                "   \n" +
                json.dumps({"content": "Doc 2"}) + "\n"
            )

            loader = PackLoader()
            documents = loader._load_jsonl_file(jsonl_file, "test-pack")

            assert len(documents) == 2


class TestLoadStructuredPack:
    """Test _load_structured_pack method."""

    def test_load_structured_pack_with_templates(self):
        """_load_structured_pack should load templates.json."""
        from warbler_cda.pack_loader import PackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "structured-pack"
            pack_dir.mkdir()
            pack_subdir = pack_dir / "pack"
            pack_subdir.mkdir()

            # Create templates.json
            templates_file = pack_subdir / "templates.json"
            templates_file.write_text(json.dumps([
                {"id": "template1", "content": "Template 1"},
                {"id": "template2", "content": "Template 2"}
            ]))

            loader = PackLoader()
            documents = loader._load_structured_pack(pack_dir, "structured-pack")

            assert len(documents) == 2
            assert documents[0]["metadata"]["type"] == "template"

    def test_load_structured_pack_missing_templates(self):
        """_load_structured_pack should handle missing templates.json."""
        from warbler_cda.pack_loader import PackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "structured-pack"
            pack_dir.mkdir()

            loader = PackLoader()
            documents = loader._load_structured_pack(pack_dir, "structured-pack")

            assert not documents

    def test_load_structured_pack_dict_format(self):
        """_load_structured_pack should handle dict format with templates key."""
        from warbler_cda.pack_loader import PackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "structured-pack"
            pack_dir.mkdir()
            pack_subdir = pack_dir / "pack"
            pack_subdir.mkdir()

            # Create templates.json with dict format
            templates_file = pack_subdir / "templates.json"
            templates_file.write_text(json.dumps({
                "templates": [
                    {"id": "template1", "content": "Template 1"}
                ]
            }))

            loader = PackLoader()
            documents = loader._load_structured_pack(pack_dir, "structured-pack")

            assert len(documents) == 1


class TestFormatDocument:
    """Test _format_document method."""

    def test_format_document_with_content(self):
        """_format_document should format entry with content field."""
        from warbler_cda.pack_loader import PackLoader

        loader = PackLoader()
        entry = {"content": "Test content", "type": "dialogue"}
        doc = loader._format_document(entry, "test-pack", "doc-1")

        assert doc["id"] == "test-pack/doc-1"
        assert doc["content"] == "Test content"
        assert doc["metadata"]["pack"] == "test-pack"
        assert doc["metadata"]["type"] == "dialogue"

    def test_format_document_with_text(self):
        """_format_document should use text field if content missing."""
        from warbler_cda.pack_loader import PackLoader

        loader = PackLoader()
        entry = {"text": "Test text"}
        doc = loader._format_document(entry, "test-pack", "doc-1")

        assert doc["content"] == "Test text"

    def test_format_document_fallback_to_json(self):
        """_format_document should fallback to JSON dump if no content/text."""
        from warbler_cda.pack_loader import PackLoader

        loader = PackLoader()
        entry = {"key": "value"}
        doc = loader._format_document(entry, "test-pack", "doc-1")

        assert "key" in doc["content"]
        assert "value" in doc["content"]

    def test_format_document_metadata_merge(self):
        """_format_document should merge entry fields into metadata."""
        from warbler_cda.pack_loader import PackLoader

        loader = PackLoader()
        entry = {"content": "Test", "custom_field": "custom_value"}
        doc = loader._format_document(entry, "test-pack", "doc-1")

        assert doc["metadata"]["custom_field"] == "custom_value"


class TestInferRealm:
    """Test _infer_realm method."""

    def test_infer_realm_wisdom(self):
        """_infer_realm should detect wisdom realm."""
        from warbler_cda.pack_loader import PackLoader

        loader = PackLoader()
        realm = loader._infer_realm("warbler-pack-wisdom-core")
        assert realm == "wisdom"

    def test_infer_realm_faction(self):
        """_infer_realm should detect faction realm."""
        from warbler_cda.pack_loader import PackLoader

        loader = PackLoader()
        realm = loader._infer_realm("warbler-pack-faction-politics")
        assert realm == "faction"

    def test_infer_realm_politics(self):
        """_infer_realm should detect politics as faction realm."""
        from warbler_cda.pack_loader import PackLoader

        loader = PackLoader()
        realm = loader._infer_realm("warbler-pack-politics-core")
        assert realm == "faction"

    def test_infer_realm_dialogue(self):
        """_infer_realm should detect dialogue as narrative realm."""
        from warbler_cda.pack_loader import PackLoader

        loader = PackLoader()
        realm = loader._infer_realm("warbler-pack-dialogue-npc")
        assert realm == "narrative"

    def test_infer_realm_npc(self):
        """_infer_realm should detect npc as narrative realm."""
        from warbler_cda.pack_loader import PackLoader

        loader = PackLoader()
        realm = loader._infer_realm("warbler-pack-npc-core")
        assert realm == "narrative"

    def test_infer_realm_default(self):
        """_infer_realm should default to narrative."""
        from warbler_cda.pack_loader import PackLoader

        loader = PackLoader()
        realm = loader._infer_realm("warbler-pack-unknown")
        assert realm == "narrative"


class TestGenerateJsonlFromTemplates:
    """Test _generate_jsonl_from_templates method."""

    def test_generate_jsonl_from_templates(self):
        """_generate_jsonl_from_templates should create JSONL file."""
        from warbler_cda.pack_loader import PackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "test-pack"
            pack_dir.mkdir()

            documents = [
                {"id": "doc-1", "content": "Content 1"},
                {"id": "doc-2", "content": "Content 2"}
            ]

            loader = PackLoader()
            loader._generate_jsonl_from_templates(pack_dir, "test-pack", documents)

            jsonl_file = pack_dir / "test-pack.jsonl"
            assert jsonl_file.exists()

            # Verify content
            lines = jsonl_file.read_text().strip().split("\n")
            assert len(lines) == 2

    def test_generate_jsonl_skip_if_exists(self):
        """_generate_jsonl_from_templates should skip if file exists."""
        from warbler_cda.pack_loader import PackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "test-pack"
            pack_dir.mkdir()

            # Create existing JSONL file
            jsonl_file = pack_dir / "test-pack.jsonl"
            jsonl_file.write_text("existing content")

            documents = [{"id": "doc-1", "content": "New content"}]

            loader = PackLoader()
            loader._generate_jsonl_from_templates(pack_dir, "test-pack", documents)

            # Should not overwrite
            assert jsonl_file.read_text() == "existing content"


class TestIntegration:
    """Integration tests for complete pack loading workflow."""

    def test_full_pack_loading_workflow(self):
        """Test complete workflow from discovery to document loading."""
        from warbler_cda.pack_loader import PackLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple packs
            for i in range(3):
                pack_dir = Path(tmpdir) / f"warbler-pack-test-{i}"
                pack_dir.mkdir()

                # Create package.json
                package_json = pack_dir / "package.json"
                package_json.write_text(json.dumps({
                    "name": f"warbler-pack-test-{i}",
                    "version": "1.0.0"
                }))

                # Create JSONL file
                jsonl_file = pack_dir / f"warbler-pack-test-{i}.jsonl"
                jsonl_file.write_text(
                    json.dumps({"content": f"Document from pack {i}"}) + "\n"
                )

            loader = PackLoader(packs_dir=Path(tmpdir))
            documents = loader.discover_documents()

            assert len(documents) == 3
            assert all("content" in doc for doc in documents)
            assert all("metadata" in doc for doc in documents)
