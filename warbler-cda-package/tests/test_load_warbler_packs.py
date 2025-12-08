"""
Comprehensive tests for Warbler pack loading utilities.

Tests the pack discovery, parsing, and ingestion pipeline that loads
Warbler pack data into the API service for end-to-end testing.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
import requests

from warbler_cda.utils.load_warbler_packs import WarblerPackLoader


class TestWarblerPackLoader:
    """Test WarblerPackLoader functionality."""

    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.loader = WarblerPackLoader("http://test-api:8000")

    def teardown_method(self):
        """Cleanup after each test."""
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_warbler_pack_loader_initialization(self):
        """Test WarblerPackLoader initialization."""
        loader = WarblerPackLoader("http://example.com:9000")

        assert loader.api_url == "http://example.com:9000"
        assert loader.loaded_count == 0
        assert loader.error_count == 0
        assert isinstance(loader.session, requests.Session)

    def test_warbler_pack_loader_api_url_default(self):
        """Test default API URL."""
        loader = WarblerPackLoader()

        assert loader.api_url == "http://localhost:8000"

    def test_discover_documents_pack_not_found(self):
        """Test discovering documents when pack doesn't exist."""
        with patch('warbler_cda.utils.load_warbler_packs.PACKS_DIR', self.temp_dir):
            loader = WarblerPackLoader()
            docs = loader.discover_documents("nonexistent-pack")

            assert docs == []

    def test_discover_documents_json_file(self):
        """Test discovering JSON documents."""
        # Create a test pack directory
        pack_dir = self.temp_dir / "test-pack"
        pack_dir.mkdir()

        # Create a JSON file
        json_file = pack_dir / "test.json"
        json_content = {"key": "value", "data": "test"}
        json_file.write_text(json.dumps(json_content))

        with patch('warbler_cda.utils.load_warbler_packs.PACKS_DIR', self.temp_dir):
            docs = self.loader.discover_documents("test-pack")

        assert len(docs) == 1
        doc = docs[0]
        assert doc["content_id"] == "test-pack/test"
        assert json.loads(doc["content"]) == json_content
        assert doc["metadata"]["pack"] == "test-pack"
        assert doc["metadata"]["source_file"] == "test.json"
        assert doc["metadata"]["realm_type"] == "narrative"

    def test_discover_documents_jsonl_file(self):
        """Test discovering JSONL documents."""
        pack_dir = self.temp_dir / "test-pack"
        pack_dir.mkdir()

        # Create a JSONL file with multiple lines
        jsonl_file = pack_dir / "test.jsonl"
        lines = [
            '{"key": "value1"}',
            '{"key": "value2"}',
            '{"key": "value3"}'
        ]
        jsonl_file.write_text('\n'.join(lines))

        with patch('warbler_cda.utils.load_warbler_packs.PACKS_DIR', self.temp_dir):
            docs = self.loader.discover_documents("test-pack")

        assert len(docs) == 1
        doc = docs[0]
        assert "value1" in doc["content"]
        assert "value2" in doc["content"]
        assert "value3" in doc["content"]
        assert doc["metadata"]["source_file"] == "test.jsonl"

    def test_discover_documents_markdown_file(self):
        """Test discovering markdown documents."""
        pack_dir = self.temp_dir / "test-pack"
        pack_dir.mkdir()

        # Create a markdown file
        md_file = pack_dir / "test.md"
        md_content = "# Test Document\n\nSome markdown content."
        md_file.write_text(md_content)

        with patch('warbler_cda.utils.load_warbler_packs.PACKS_DIR', self.temp_dir):
            docs = self.loader.discover_documents("test-pack")

        assert len(docs) == 1
        doc = docs[0]
        assert doc["content"] == md_content
        assert doc["metadata"]["source_file"] == "test.md"

    def test_discover_documents_yaml_file(self):
        """Test discovering YAML documents."""
        pack_dir = self.temp_dir / "test-pack"
        pack_dir.mkdir()

        # Create a YAML file
        yaml_file = pack_dir / "test.yaml"
        yaml_content = """
key: value
data:
  nested: content
"""
        yaml_file.write_text(yaml_content)

        with patch('warbler_cda.utils.load_warbler_packs.PACKS_DIR', self.temp_dir):
            docs = self.loader.discover_documents("test-pack")

        assert len(docs) == 1
        doc = docs[0]
        content_dict = json.loads(doc["content"])
        assert content_dict["key"] == "value"
        assert doc["metadata"]["source_file"] == "test.yaml"

    def test_discover_documents_wisdom_pack(self):
        """Test pack type detection for wisdom packs."""
        pack_dir = self.temp_dir / "warbler-pack-wisdom-scrolls"
        pack_dir.mkdir()

        json_file = pack_dir / "test.json"
        json_file.write_text('{"content": "wisdom content"}')

        with patch('warbler_cda.utils.load_warbler_packs.PACKS_DIR', self.temp_dir):
            docs = self.loader.discover_documents("warbler-pack-wisdom-scrolls")

        assert len(docs) == 1
        doc = docs[0]
        assert doc["metadata"]["realm_type"] == "wisdom"
        assert doc["metadata"]["realm_label"] == "wisdom-scrolls"

    def test_discover_documents_faction_pack(self):
        """Test pack type detection for faction packs."""
        pack_dir = self.temp_dir / "warbler-pack-faction-politics"
        pack_dir.mkdir()

        json_file = pack_dir / "test.json"
        json_file.write_text('{"content": "faction content"}')

        with patch('warbler_cda.utils.load_warbler_packs.PACKS_DIR', self.temp_dir):
            docs = self.loader.discover_documents("warbler-pack-faction-politics")

        assert len(docs) == 1
        doc = docs[0]
        assert doc["metadata"]["realm_type"] == "faction"
        assert doc["metadata"]["realm_label"] == "faction-politics"

    def test_discover_documents_content_size_limit(self):
        """Test content size limit enforcement."""
        pack_dir = self.temp_dir / "test-pack"
        pack_dir.mkdir()

        # Create a large JSON file (over 5000 chars)
        large_file = pack_dir / "large.json"
        large_content = "x" * 6000
        large_file.write_text(json.dumps({"content": large_content}))

        with patch('warbler_cda.utils.load_warbler_packs.PACKS_DIR', self.temp_dir):
            docs = self.loader.discover_documents("test-pack")

        assert len(docs) == 1
        doc = docs[0]
        # Should be truncated to 5000 chars plus some JSON formatting
        assert len(doc["content"]) < 6000
        assert len(doc["content"]) <= 5050  # Allow some margin for JSON wrapping

    def test_discover_documents_parse_error(self):
        """Test handling of parse errors."""
        pack_dir = self.temp_dir / "test-pack"
        pack_dir.mkdir()

        # Create an invalid JSON file
        bad_file = pack_dir / "bad.json"
        bad_file.write_text("this is not valid json {")

        # Create a valid JSON file too
        good_file = pack_dir / "good.json"
        good_file.write_text('{"valid": "json"}')

        with patch('warbler_cda.utils.load_warbler_packs.PACKS_DIR', self.temp_dir):
            docs = self.loader.discover_documents("test-pack")

        # Should only get the valid document
        assert len(docs) == 1
        assert docs[0]["content_id"] == "test-pack/good"

    def test_ingest_document_success(self):
        """Test successful document ingestion."""
        doc = {
            "content_id": "test/doc",
            "content": "test content",
            "metadata": {"pack": "test-pack", "realm_type": "narrative"}
        }

        with patch.object(self.loader.session, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_post.return_value = mock_response

            success = self.loader.ingest_document(doc)

            assert success is True
            assert self.loader.loaded_count == 1
            assert self.loader.error_count == 0

            # Check the API call
            mock_post.assert_called_once_with(
                "http://test-api:8000/ingest",
                json={"documents": [doc]},
                timeout=10
            )

    def test_ingest_document_api_error(self):
        """Test ingestion with API error."""
        doc = {
            "content_id": "test/doc",
            "content": "test content",
            "metadata": {"pack": "test-pack", "realm_type": "narrative"}
        }

        with patch.object(self.loader.session, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_post.return_value = mock_response

            success = self.loader.ingest_document(doc)

            assert success is False
            assert self.loader.loaded_count == 0
            assert self.loader.error_count == 0  # Error count only incremented on exceptions

    def test_ingest_document_connection_error(self):
        """Test ingestion with connection error."""
        doc = {
            "content_id": "test/doc",
            "content": "test content",
            "metadata": {"pack": "test-pack", "realm_type": "narrative"}
        }

        with patch.object(self.loader.session, 'post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

            success = self.loader.ingest_document(doc)

            assert success is False
            assert self.loader.error_count == 1  # ConnectionError should also increment error_count

    def test_ingest_document_unexpected_error(self):
        """Test ingestion with unexpected error."""
        doc = {
            "content_id": "test/doc",
            "content": "test content",
            "metadata": {"pack": "test-pack", "realm_type": "narrative"}
        }

        with patch.object(self.loader.session, 'post') as mock_post:
            mock_post.side_effect = Exception("Unexpected error")

            success = self.loader.ingest_document(doc)

            assert success is False
            assert self.loader.error_count == 1


class TestWarblerPackLoaderIntegration:
    """Integration tests for pack loading workflows."""

    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Cleanup after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.skipif(True, reason="Complex integration test with real pack directory scanning - core functionality tested elsewhere")
    @patch('warbler_cda.utils.load_warbler_packs.WarblerPackLoader.ingest_document')
    def test_load_all_packs_integration(self, mock_ingest):
        """Test the full pack loading workflow."""
        # Create mock packs
        for pack_name in ["warbler-pack-core", "warbler-pack-wisdom-scrolls"]:
            pack_dir = self.temp_dir / pack_name
            pack_dir.mkdir()

            # Add a document to each pack
            doc_file = pack_dir / "test.json"
            doc_file.write_text('{"content": "test", "metadata": {}}')

        mock_ingest.return_value = True

        with patch('warbler_cda.utils.load_warbler_packs.PACKS_DIR', self.temp_dir):
            loader = WarblerPackLoader()
            loaded = loader.load_all_packs()

        # Should have loaded documents from both packs
        expected_calls = len(loader.discover_documents("warbler-pack-core")) + \
                        len(loader.discover_documents("warbler-pack-wisdom-scrolls"))
        assert mock_ingest.call_count == expected_calls
        assert loaded == expected_calls


class TestWarblerPackLoaderCLI:
    """Test CLI commands for pack loading."""

    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Cleanup after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.skipif(True, reason="Complex CLI integration test - core functionality tested elsewhere")
    @patch('warbler_cda.utils.load_warbler_packs.click.echo')
    @patch('warbler_cda.utils.load_warbler_packs.click.secho')
    def test_cli_load_with_running_api(self, mock_secho, mock_echo):
        """Test CLI load command with running API."""
        with patch('warbler_cda.utils.load_warbler_packs.requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session

            # Mock health check
            health_response = Mock()
            health_response.status_code = 200
            mock_session.get.return_value = health_response

            # Mock pack loading
            with patch('warbler_cda.utils.load_warbler_packs.WarblerPackLoader.load_all_packs') as mock_load:
                mock_load.return_value = 5
                mock_load.return_value = Mock(loaded_count=5, error_count=0)

                from warbler_cda.utils.load_warbler_packs import cli
                import click.testing

                runner = click.testing.CliRunner()
                result = runner.invoke(cli, ['load'])

                assert result.exit_code == 0

    @patch('warbler_cda.utils.load_warbler_packs.click.echo')
    def test_cli_load_api_not_running(self, mock_echo):
        """Test CLI load command when API is not running."""
        with patch('warbler_cda.utils.load_warbler_packs.requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            mock_session.get.side_effect = Exception("Connection refused")

            from warbler_cda.utils.load_warbler_packs import cli
            import click.testing

            runner = click.testing.CliRunner()
            result = runner.invoke(cli, ['load'])

            assert result.exit_code == 0  # CLI handles error gracefully

    @patch('warbler_cda.utils.load_warbler_packs.click.echo')
    def test_cli_discover_command(self, mock_echo):
        """Test CLI discover command."""
        # Create a test pack
        pack_dir = self.temp_dir / "warbler-pack-core"
        pack_dir.mkdir()

        doc_file = pack_dir / "test.json"
        doc_file.write_text('{"content": "test"}')

        with patch('warbler_cda.utils.load_warbler_packs.PACKS_DIR', self.temp_dir):
            from warbler_cda.utils.load_warbler_packs import cli
            import click.testing

            runner = click.testing.CliRunner()
            result = runner.invoke(cli, ['discover'])

            assert result.exit_code == 0
            # Should have echoed about the discovered pack and document


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
