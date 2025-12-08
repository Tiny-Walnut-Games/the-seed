"""Test suite for new MIT-licensed HuggingFace datasets integration.

Tests ingestion of:
- arxiv-papers: Scholarly papers (2.55M)
- prompt-report: Prompt engineering docs (83)
- generated-novels: Narrative text (20)
- anac-manuals: Technical manuals (52)
- chatenv: Software development chat (SustcZhangYX/ChatEnv)
- portuguese-edu: Multilingual education (21)
- edustories: Educational stories in English (MU-NLPC/Edustories-en)
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from warbler_cda.utils.transformers import (
    ArxivTransformer,
    PromptReportTransformer,
    NovelsTransformer,
    ManualsTransformer,
    EnterpriseTransformer,
    PortugueseEducationTransformer,
    EdustoriesTransformer,
    WarblerPackBuilder,
)

sys.path.insert(0, str(Path(__file__).parent.parent))

class TestArxivPapersTransformer:
    """Test arXiv papers dataset transformer."""

    def test_arxiv_transformer_exists(self):
        """Test that arxiv transformer exists and is callable."""
        transformer = ArxivTransformer()
        assert hasattr(transformer, "transform")
        assert callable(transformer.transform)

    def test_arxiv_output_format(self):
        """Test arXiv transformer produces Warbler-compatible format."""
        transformer = ArxivTransformer()

        mock_paper = {
            "arxiv_id": "2301.00001",
            "title": "Test Paper on Machine Learning",
            "authors": "Author One, Author Two",
            "abstract": "This is a test abstract about ML research.",
            "year": 2023,
            "categories": "cs.LG;cs.AI",
        }

        with patch(
            "warbler_cda.utils.transformers.arxiv.load_dataset"
        ) as mock_load:
            mock_dataset = MagicMock()
            mock_dataset.__getitem__.return_value = [mock_paper]
            mock_dataset.keys.return_value = ["train"]
            mock_load.return_value = mock_dataset

            docs = transformer.transform(limit=1)

            assert len(docs) > 0
            doc = docs[0]
            assert "content_id" in doc
            assert "content" in doc
            assert "metadata" in doc
            assert (
                doc["metadata"]["source_dataset"] == "nick007x/arxiv-papers"
            )
            assert doc["metadata"]["license"] == "MIT"

    def test_arxiv_metadata_fields(self):
        """Test that arXiv metadata contains required fields."""
        transformer = ArxivTransformer()

        mock_paper = {
            "arxiv_id": "2301.00001",
            "title": "Test Paper",
            "authors": "Author",
            "abstract": "Abstract",
            "year": 2023,
            "categories": "cs.LG",
        }

        with patch(
            "warbler_cda.utils.transformers.arxiv.load_dataset"
        ) as mock_load:
            mock_dataset = MagicMock()
            mock_dataset.__getitem__.return_value = [mock_paper]
            mock_dataset.keys.return_value = ["train"]
            mock_load.return_value = mock_dataset

            docs = transformer.transform(limit=1)
            metadata = docs[0]["metadata"]

            assert "pack" in metadata
            assert "arxiv_id" in metadata
            assert "year" in metadata
            assert "categories" in metadata
            assert metadata["realm_type"] == "scholarly"
            assert metadata["realm_label"] == "arxiv"

    def test_arxiv_limit_parameter(self):
        """Test that arxiv transformer respects limit parameter."""
        transformer = ArxivTransformer()

        mock_papers = [
            {
                "arxiv_id": f"2301.{i:05d}",
                "title": f"Paper {i}",
                "authors": f"Author {i}",
                "abstract": f"Abstract {i}",
                "year": 2023,
                "categories": "cs.LG",
            }
            for i in range(10)
        ]

        with patch(
            "warbler_cda.utils.transformers.arxiv.load_dataset"
        ) as mock_load:
            mock_dataset = MagicMock()
            mock_dataset.__getitem__.return_value = mock_papers
            mock_dataset.keys.return_value = ["train"]
            mock_load.return_value = mock_dataset

            docs = transformer.transform(limit=5)

            assert len(docs) <= 5


class TestPromptReportTransformer:
    """Test prompt engineering report dataset transformer."""

    def test_prompt_report_transformer_exists(self):
        """Test that prompt report transformer exists."""
        transformer = PromptReportTransformer()
        assert hasattr(transformer, "transform")
        assert callable(transformer.transform)

    def test_prompt_report_output_format(self):
        """Test prompt report produces Warbler format."""
        transformer = PromptReportTransformer()

        mock_report = {
            "id": "report_001",
            "title": "The Prompt Report: A Systematic Study",
            "text": "This is the full report text about prompting.",
            "category": "prompting",
        }

        with patch(
            "warbler_cda.utils.transformers.prompt_report.load_dataset"
        ) as mock_load:
            mock_dataset = MagicMock()
            mock_dataset = [mock_report]
            mock_load.return_value = mock_dataset

            docs = transformer.transform()

            assert len(docs) > 0
            doc = docs[0]
            assert "content_id" in doc
            assert "content" in doc
            assert "metadata" in doc
            assert (
                doc["metadata"]["source_dataset"]
                == "PromptSystematicReview/ThePromptReport"
            )
            assert doc["metadata"]["license"] == "MIT"


class TestGeneratedNovelsTransformer:
    """Test generated novels dataset transformer."""

    def test_novels_transformer_exists(self):
        """Test that novels transformer exists."""
        transformer = NovelsTransformer()
        assert hasattr(transformer, "transform")
        assert callable(transformer.transform)

    def test_novels_chunking_for_long_text(self):
        """Test that long novels are properly chunked."""
        transformer = NovelsTransformer()

        long_text = " ".join(["This is a sentence about a novel."] * 500)
        mock_novel = {"id": "novel_001", "title": "Test Novel", "text": long_text}

        with patch(
            "warbler_cda.utils.transformers.novels.load_dataset"
        ) as mock_load:
            mock_dataset = MagicMock()
            mock_dataset = [mock_novel]
            mock_load.return_value = mock_dataset

            docs = transformer.transform()

            for doc in docs:
                assert "content_id" in doc
                assert "metadata" in doc
                assert (
                    doc["metadata"]["source_dataset"]
                    == "GOAT-AI/generated-novels"
                )
                assert doc["metadata"]["license"] == "MIT"


class TestManualnsTransformer:
    """Test technical manuals dataset transformer."""

    def test_manuals_transformer_exists(self):
        """Test that manuals transformer exists."""
        transformer = ManualsTransformer()
        assert hasattr(transformer, "transform")
        assert callable(transformer.transform)

    def test_manuals_output_format(self):
        """Test manuals transformer produces Warbler format."""
        transformer = ManualsTransformer()

        mock_manual = {
            "id": "manual_001",
            "title": "Technical Manual",
            "text": "This is technical documentation.",
            "category": "technology",
        }

        with patch(
            "warbler_cda.utils.transformers.manuals.load_dataset"
        ) as mock_load:
            mock_dataset = MagicMock()
            mock_dataset = [mock_manual]
            mock_load.return_value = mock_dataset

            docs = transformer.transform()

            assert len(docs) > 0
            doc = docs[0]
            assert "content_id" in doc
            assert "content" in doc
            assert "metadata" in doc
            assert doc["metadata"]["source_dataset"] == "nlasso/anac-manuals-23"
            assert doc["metadata"]["license"] == "MIT"


class TestEnterpriseTransformer:
    """Test enterprise/SustainabilityEntered transformer."""

    def test_enterprise_transformer_exists(self):
        """Test that enterprise transformer exists."""
        transformer = EnterpriseTransformer()
        assert hasattr(transformer, "transform")
        assert callable(transformer.transform)

    def test_enterprise_output_format(self):
        """Test enterprise transformer produces Warbler format."""
        transformer = EnterpriseTransformer()

        mock_conversation = {
            "id": "conv_001",
            "messages": [
                {
                    "role": "user",
                    "content": "Can you help with software development?",
                }
            ],
        }

        with patch(
            "warbler_cda.utils.transformers.enterprise.load_dataset"
        ) as mock_load:
            mock_dataset = MagicMock()
            mock_dataset = [mock_conversation]
            mock_load.return_value = mock_dataset

            docs = transformer.transform()

            assert len(docs) > 0
            doc = docs[0]
            assert "content_id" in doc
            assert "content" in doc
            assert "metadata" in doc
            assert (
                doc["metadata"]["source_dataset"] == "SustcZhangYX/ChatEnv"
            )
            assert doc["metadata"]["license"] == "MIT"
            assert doc["metadata"]["realm_type"] == "software_development"


class TestPortugueseEducationTransformer:
    """Test Portuguese education dataset transformer."""

    def test_portuguese_transformer_exists(self):
        """Test that Portuguese education transformer exists."""
        transformer = PortugueseEducationTransformer()
        assert hasattr(transformer, "transform")
        assert callable(transformer.transform)

    def test_portuguese_output_format(self):
        """Test Portuguese education produces Warbler format."""
        transformer = PortugueseEducationTransformer()

        mock_doc = {
            "id": "port_001",
            "title": "Portuguese Education Article",
            "text": "Conteúdo educacional em português",
        }

        with patch(
            "warbler_cda.utils.transformers"
            ".portuguese_education.load_dataset"
        ) as mock_load:
            mock_dataset = MagicMock()
            mock_dataset = [mock_doc]
            mock_load.return_value = mock_dataset

            docs = transformer.transform()

            assert len(docs) > 0
            doc = docs[0]
            assert "content_id" in doc
            assert "content" in doc
            assert "metadata" in doc
            assert (
                doc["metadata"]["source_dataset"]
                == "Solshine/Portuguese_Language_Education_Texts"
            )
            assert doc["metadata"]["license"] == "MIT"
            assert doc["metadata"]["language"] == "pt"


class TestEdustoriesTransformer:
    """Test educational stories (edustories) transformer."""

    def test_edustories_transformer_exists(self):
        """Test that edustories transformer exists."""
        transformer = EdustoriesTransformer()
        assert hasattr(transformer, "transform")
        assert callable(transformer.transform)

    def test_edustories_metadata_completeness(self):
        """Test that edustories metadata is complete."""
        transformer = EdustoriesTransformer()

        mock_case_study = {
            "id": 123,
            "description": "Classroom with diverse learners.",
            "anamnesis": "Student had learning difficulties.",
            "solution": "Implemented personalized learning approach.",
            "outcome": "Student improved academically.",
            "age, school year": "10 years, 4th grade",
            "hobbies": "Reading, art",
            "diagnoses": "Dyslexia",
            "disorders": "",
            "problems_annotated": "reading_difficulty",
            "solutions_annotated": "reading_intervention",
            "implications_annotated": "literacy_support",
        }

        with patch(
            "warbler_cda.utils.transformers.edustories.load_dataset"
        ) as mock_load:
            mock_dataset = MagicMock()
            mock_dataset = [mock_case_study]
            mock_load.return_value = mock_dataset

            docs = transformer.transform()

            assert len(docs) > 0
            doc = docs[0]
            metadata = doc["metadata"]

            # Check for case study metadata
            assert "pack" in metadata
            assert metadata["pack"] == "warbler-pack-edustories"
            assert "source_dataset" in metadata
            assert metadata["source_dataset"] == "MU-NLPC/Edustories-en"
            assert "license" in metadata
            assert metadata["license"] == "MIT"

            # Check for annotations
            assert "problems_annotated" in metadata
            assert metadata["problems_annotated"] == "reading_difficulty"
            assert "solutions_annotated" in metadata
            assert metadata["solutions_annotated"] == "reading_intervention"
            assert "implications_annotated" in metadata
            assert (
                metadata["implications_annotated"] == "literacy_support"
            )

            # Check realm and dialogue type
            assert metadata["realm_label"] == "educational_case_studies"
            assert metadata["dialogue_type"] == "teaching_case_study"
            assert metadata["pack"] == "warbler-pack-edustories"

    def test_edustories_content_structure(self):
        """Test that edustories content has structured sections."""
        transformer = EdustoriesTransformer()

        mock_case_study = {
            "id": 789,
            "description": (
                "A diverse classroom with students of varying abilities."
            ),
            "anamnesis": (
                "Student struggled with group work and social interactions."
            ),
            "solution": (
                "Teacher introduced structured cooperative learning "
                "activities."
            ),
            "outcome": (
                "Student became more comfortable working with peers."
            ),
            "age, school year": "9 years, 3rd grade",
            "hobbies": "Video games",
            "diagnoses": "Autism Spectrum Disorder",
            "disorders": "",
            "problems_annotated": "social_skills_deficit",
            "solutions_annotated": "cooperative_learning",
            "implications_annotated": "social_improvement",
        }

        with patch(
            "warbler_cda.utils.transformers.edustories.load_dataset"
        ) as mock_load:
            mock_dataset = MagicMock()
            mock_dataset = [mock_case_study]
            mock_load.return_value = mock_dataset

            docs = transformer.transform()

            assert len(docs) > 0
            doc = docs[0]
            content = doc["content"]

            # Check for structured sections
            assert "Background" in content
            assert "Situation" in content
            assert (
                "Teacher Intervention" in content or "Intervention" in content
            )
            assert "Outcome" in content
            assert "Student Profile" in content

            # Check that actual content is present
            assert "diverse classroom" in content
            assert "struggled with group work" in content
            assert "cooperative learning" in content
            assert "more comfortable working with peers" in content

            # Check for student profile information
            assert "9 years, 3rd grade" in content
            assert "Video games" in content
            assert "Autism Spectrum Disorder" in content

            # Check for annotations section
            assert (
                "Annotations" in content or "Identified Problems" in content
            )
            assert "social_skills_deficit" in content
            assert "cooperative_learning" in content

            # Check for case study marker
            assert "case study" in content.lower() or "Case Study" in content


class TestNewDatasetsIntegrationWithRetrieval:
    """Test that new data integrates with retrieval API."""

    def test_warbler_document_structure(self):
        """Test that transformed documents have proper Warbler structure."""
        transformer = ArxivTransformer()

        mock_paper = {
            "arxiv_id": "2301.00001",
            "title": "Test Paper",
            "authors": "Author",
            "abstract": "Abstract",
            "year": 2023,
            "categories": "cs.LG",
        }

        with patch(
            "warbler_cda.utils.transformers.arxiv.load_dataset"
        ) as mock_load:
            mock_dataset = MagicMock()
            mock_dataset.__getitem__.return_value = [mock_paper]
            mock_dataset.keys.return_value = ["train"]
            mock_load.return_value = mock_dataset

            docs = transformer.transform(limit=1)

            for doc in docs:
                assert "content_id" in doc
                assert isinstance(doc["content_id"], str)
                assert doc["content_id"].strip() != ""

                assert "content" in doc
                assert isinstance(doc["content"], str)
                assert doc["content"].strip() != ""

                assert "metadata" in doc
                metadata = doc["metadata"]
                assert "pack" in metadata
                assert "source_dataset" in metadata
                assert "license" in metadata
                assert metadata["license"] == "MIT"
                assert "realm_type" in metadata
                assert "realm_label" in metadata

    def test_pack_creation_with_new_datasets(self):
        """Test that packs can be created from new datasets."""
        builder = WarblerPackBuilder()

        test_docs = [
            {
                "content_id": f"test_{i}",
                "content": f"Test content {i}",
                "metadata": {
                    "pack": "warbler-pack-test",
                    "source_dataset": "test/dataset",
                    "license": "MIT",
                    "realm_type": "test",
                    "realm_label": "test",
                    "lifecycle_stage": "emergence",
                    "activity_level": 0.5,
                    "dialogue_type": "test",
                },
            }
            for i in range(3)
        ]

        assert builder is not None
        assert hasattr(builder, "create_pack")


class TestNewDatasetsPerformance:
    """Test performance characteristics of new transformers."""

    def test_arxiv_handles_large_dataset(self):
        """Test that arxiv transformer can handle large limits efficiently."""
        transformer = ArxivTransformer()

        large_dataset = [
            {
                "arxiv_id": f"2301.{i:05d}",
                "title": f"Paper {i}",
                "authors": f"Author {i}",
                "abstract": f"Abstract {i}",
                "year": 2023,
                "categories": "cs.LG",
            }
            for i in range(100)
        ]

        with patch(
            "warbler_cda.utils.transformers.arxiv.load_dataset"
        ) as mock_load:
            mock_dataset = MagicMock()
            mock_dataset.__getitem__.return_value = large_dataset
            mock_dataset.keys.return_value = ["train"]
            mock_load.return_value = mock_dataset

            import time

            start = time.time()
            docs = transformer.transform(limit=100)
            elapsed = time.time() - start

            assert len(docs) <= 100
            assert elapsed < 10.0


class TestNewDatasetsAllAtOnce:
    """Test ingesting all new datasets together."""

    def test_all_transformers_callable(self):
        """Test that all new transformers can be called."""
        transformers = [
            ArxivTransformer,
            PromptReportTransformer,
            NovelsTransformer,
            ManualsTransformer,
            EnterpriseTransformer,
            PortugueseEducationTransformer,
            EdustoriesTransformer,
        ]

        for transformer_class in transformers:
            transformer = transformer_class()
            assert hasattr(
                transformer, "transform"
            ), f"Missing transform method in {transformer_class.__name__}"
            assert callable(transformer.transform)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
