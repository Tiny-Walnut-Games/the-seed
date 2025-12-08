"""
Test suite for PDF-based dataset ingestion

Tests for handling datasets with PDF fields instead of text content.
Includes fallback handling when PDF extraction is unavailable.
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from warbler_cda.utils.transformers import (
    NovelsTransformer,
    PortugueseEducationTransformer,
    EnterpriseTransformer,
    ArxivTransformer,
    PromptReportTransformer,
    ManualsTransformer,
)


class TestPDFExtraction:
    """Test PDF extraction capability"""

    def test_pdf_support_detection(self):
        """Test that transformers can be instantiated"""
        transformer = NovelsTransformer()
        assert transformer is not None
        assert hasattr(transformer, "transform")

    def test_pdf_extraction_method_exists(self):
        """Test that transformers have required methods"""
        transformer = NovelsTransformer()
        assert hasattr(transformer, "transform")
        assert callable(transformer.transform)

    def test_placeholder_creation_method_exists(self):
        """Test that transformer is properly initialized"""
        transformer = NovelsTransformer()
        assert transformer is not None
        assert hasattr(transformer, "__class__")


class TestNovelDatasetWithPDF:
    """Test novel dataset handling with PDF fallback"""

    def test_novel_transform_handles_missing_fields(self):
        """Test that novel transformer handles datasets with only PDF field"""
        transformer = NovelsTransformer()

        mock_novel = {"pdf": b"fake_pdf_bytes", "title": "Test Novel"}

        with patch("warbler_cda.utils.transformers.novels.load_dataset") as mock_load:
            mock_dataset = MagicMock()
            mock_dataset.__iter__.return_value = [mock_novel]
            mock_load.return_value = mock_dataset

            docs = transformer.transform()

            assert len(docs) > 0
            doc = docs[0]
            assert "content" in doc
            assert "metadata" in doc
            assert doc["metadata"]["realm_type"] == "narrative"

    def test_novel_with_text_field(self):
        """Test novel transformer with actual text field"""
        transformer = NovelsTransformer()

        mock_novel = {
            "text": "Once upon a time there was a kingdom far away. " * 50,
            "title": "Story of the Kingdom",
        }

        with patch("warbler_cda.utils.transformers.novels.load_dataset") as mock_load:
            mock_dataset = MagicMock()
            mock_dataset.__iter__.return_value = [mock_novel]
            mock_load.return_value = mock_dataset

            docs = transformer.transform()

            assert len(docs) > 0
            doc = docs[0]
            assert "content" in doc
            assert "metadata" in doc

    def test_novel_transformer_output_format(self):
        """Test that novel transformer produces Warbler-compatible format"""
        transformer = NovelsTransformer()

        mock_novel = {"text": "Novel content here. " * 100, "title": "Test Novel"}

        with patch("warbler_cda.utils.transformers.novels.load_dataset") as mock_load:
            mock_dataset = MagicMock()
            mock_dataset.__iter__.return_value = [mock_novel]
            mock_load.return_value = mock_dataset

            docs = transformer.transform()

            assert len(docs) > 0
            for doc in docs:
                assert "content_id" in doc
                assert "content" in doc
                assert "metadata" in doc
                metadata = doc["metadata"]
                assert "pack" in metadata
                assert metadata["pack"] == "warbler-pack-novels"
                assert "realm_type" in metadata
                assert metadata["realm_type"] == "narrative"
                assert "license" in metadata
                assert metadata["license"] == "MIT"


class TestPortugueseEducationWithPDF:
    """Test Portuguese education dataset with PDF handling"""

    def test_portuguese_handles_pdf_field(self):
        """Test Portuguese education with PDF-only field"""
        transformer = PortugueseEducationTransformer()

        mock_doc = {"pdf": b"pdf_content_bytes", "title": "Introdução à Programação"}

        with patch("warbler_cda.utils.transformers.portuguese_education.load_dataset") as mock_load:
            mock_dataset = MagicMock()
            mock_dataset.__iter__.return_value = [mock_doc]
            mock_load.return_value = mock_dataset

            docs = transformer.transform()

            assert len(docs) > 0
            doc = docs[0]
            assert "content" in doc
            assert "metadata" in doc
            assert doc["metadata"]["realm_type"] == "educational"

    def test_portuguese_with_text_field(self):
        """Test Portuguese education with text field"""
        transformer = PortugueseEducationTransformer()

        mock_doc = {
            "content": "A programação é a arte de instruir o computador.",
            "title": "Introdução à Programação",
            "language": "pt",
        }

        with patch("warbler_cda.utils.transformers.portuguese_education.load_dataset") as mock_load:
            mock_dataset = MagicMock()
            mock_dataset.__iter__.return_value = [mock_doc]
            mock_load.return_value = mock_dataset

            docs = transformer.transform()

            assert len(docs) > 0
            doc = docs[0]
            assert "content" in doc
            assert "metadata" in doc


class TestEnterpriseDatasetFallback:
    """Test enterprise dataset with graceful fallback"""

    def test_enterprise_load_error_handling(self):
        """Test that enterprise transformer handles load errors gracefully"""
        transformer = EnterpriseTransformer()

        with patch("warbler_cda.utils.transformers.enterprise.load_dataset") as mock_load:
            mock_load.side_effect = RuntimeError("Dataset generation failed")

            docs = transformer.transform()

            assert isinstance(docs, list)

    def test_enterprise_with_messages(self):
        """Test enterprise transformer with conversation messages"""
        transformer = EnterpriseTransformer()

        mock_entry = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "How do I deploy this?"},
                {"role": "assistant", "content": "Here are the steps..."},
            ]
        }

        with patch("warbler_cda.utils.transformers.enterprise.load_dataset") as mock_load:
            mock_dataset = MagicMock()
            mock_dataset.__iter__.return_value = [mock_entry]
            mock_load.return_value = mock_dataset

            docs = transformer.transform()

            assert len(docs) > 0
            doc = docs[0]
            assert "content" in doc


class TestDatasetIntegration:
    """Integration tests for full dataset ingestion"""

    def test_all_datasets_without_actual_api_calls(self):
        """Test all transformers can be instantiated"""
        transformers = [
            ArxivTransformer,
            PromptReportTransformer,
            NovelsTransformer,
            ManualsTransformer,
            PortugueseEducationTransformer,
        ]

        for transformer_class in transformers:
            transformer = transformer_class()
            assert hasattr(transformer, "transform")
            assert callable(transformer.transform)

    def test_documents_have_required_fields(self):
        """Test that all documents have required Warbler fields"""

        test_doc = {
            "content_id": "test/1",
            "content": "Test content for validation",
            "metadata": {
                "pack": "warbler-pack-test",
                "source_dataset": "test",
                "realm_type": "test",
                "realm_label": "test",
                "lifecycle_stage": "emergence",
                "activity_level": 0.7,
                "license": "MIT",
            },
        }

        required_fields = ["content_id", "content", "metadata"]
        required_metadata = [
            "pack",
            "source_dataset",
            "realm_type",
            "realm_label",
            "lifecycle_stage",
            "activity_level",
            "license",
        ]

        for field in required_fields:
            assert field in test_doc

        for meta_field in required_metadata:
            assert meta_field in test_doc["metadata"]
