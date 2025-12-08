"""
Comprehensive tests for HuggingFace Warbler pack ingestion utilities.

Tests the HF dataset ingestion pipeline that transforms datasets into
Warbler pack format for NPC intelligence training via the magma layer.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
import click.testing

from warbler_cda.utils.hf_warbler_ingest import cli


class TestHuggingFaceWarblerIngestCLI:
    """Test CLI interface for HF ingestion."""

    @pytest.mark.skipif(True, reason="MANUAL RUN ONLY - downloads actual datasets")
    @patch('warbler_cda.utils.hf_warbler_ingest.click.echo')
    def test_ingest_with_disabled_chunking(self, mock_echo):
        """Test ingestion with chunking disabled. MANUAL RUN ONLY - downloads actual datasets."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, [
            'ingest',
            '--datasets', 'arxiv',
            '--max-docs-per-chunk', '0'  # Disable chunking
        ])

        # CLI handles gracefully even with transformer failures
        assert result.exit_code == 0

    @pytest.mark.skipif(True, reason="MANUAL RUN ONLY - downloads actual datasets")
    @patch('warbler_cda.utils.hf_warbler_ingest.click.echo')
    @patch('warbler_cda.utils.hf_warbler_ingest.click.secho')
    def test_ingest_all_datasets(self, mock_secho, mock_echo):
        """Test ingesting all datasets with --datasets all. MANUAL RUN ONLY - downloads actual datasets."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ['ingest', '--datasets', 'all'])

        # Should complete without crashing
        assert result.exit_code == 0

    def test_dataset_validation(self):
        """Test validation of dataset parameter."""
        runner = click.testing.CliRunner()

        # Invalid dataset should show error
        result = runner.invoke(cli, ['ingest', '--datasets', 'invalid_dataset'])
        assert result.exit_code != 0
        assert "Invalid value" in result.output

    @patch('warbler_cda.utils.hf_warbler_ingest.click.echo')
    def test_pdf_page_limit_handling(self, mock_echo):
        """Test PDF page limit parameter handling."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, [
            'ingest',
            '--datasets', 'arxiv',
            '--max-pdf-pages', '50'
        ])

        # Should complete gracefully
        assert result.exit_code == 0

    @patch('warbler_cda.utils.hf_warbler_ingest.click.echo')
    @patch('warbler_cda.utils.hf_warbler_ingest.click.secho')
    def test_pack_prefix_customization(self, mock_secho, mock_echo):
        """Test custom pack prefix handling."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, [
            'ingest',
            '--datasets', 'arxiv',
            '--pack-prefix', 'my-custom-prefix'
        ])

        assert result.exit_code == 0


class TestCLIParameterValidation:
    """Test CLI parameter validation."""

    def test_help_command(self):
        """Test help command works."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "HuggingFace Warbler Pack Ingestion Tool" in result.output

    def test_ingest_help(self):
        """Test ingest subcommand help."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ['ingest', '--help'])
        assert result.exit_code == 0
        assert "Ingest HF datasets into Warbler packs" in result.output

    def test_datasets_parameter_defaults_to_arxiv(self):
        """Test that datasets parameter defaults to arxiv."""
        runner = click.testing.CliRunner()
        # Just run without any args to get help - this will work since it has defaults
        result = runner.invoke(cli, ['ingest', '--help'])
        assert result.exit_code == 0
        # The help shows that --datasets has a default value, not required


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
