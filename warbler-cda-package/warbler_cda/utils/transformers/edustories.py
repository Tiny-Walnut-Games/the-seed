"""Educational case studies dataset transformer."""

import logging
from typing import List, Dict, Any

from datasets import load_dataset

from .base import BaseWarblerTransformer


logger = logging.getLogger(__name__)


class EdustoriesTransformer(BaseWarblerTransformer):
    """Transform MU-NLPC/Edustories-en dataset."""

    def transform(self, dataset_name: str = "MU-NLPC/Edustories-en") -> List[Dict[str, Any]]:
        """
        Transform MU-NLPC/Edustories-en dataset.

        Format: Educational case studies with structured teaching situations

        The dataset contains structured case studies from student teachers documenting
        classroom situations with: description (background), anamnesis (situation),
        solution (teacher intervention), and outcome (final state).
        """
        logger.info(f"Loading {dataset_name}...")
        try:
            dataset = load_dataset(dataset_name)
        except Exception as e:
            logger.warning(f"Failed to load {dataset_name}: {e}")
            return []

        warbler_docs = []

        items = []
        try:
            if hasattr(dataset, "__getitem__") and "train" in dataset:
                items = list(dataset["train"])
                logger.info(f"Loaded {len(items)} items from 'train' split")
            else:
                items = self.extract_dataset_items(dataset)
                logger.info(f"Extracted {len(items)} items from dataset")
        except Exception as e:
            logger.warning(f"Error accessing dataset: {e}")
            items = self.extract_dataset_items(dataset)

        for idx, item in enumerate(items):
            if isinstance(item, str):
                logger.warning(f"Edustory {idx + 1}: Item is a string, skipping")
                continue

            if isinstance(item, dict) or hasattr(item, "__getitem__"):

                def safe_get(field_name: str, default: str = "") -> str:
                    """Safely extract field from item."""
                    try:
                        if isinstance(item, dict):
                            return item.get(field_name, default) or default
                        elif hasattr(item, "__getitem__"):
                            return item[field_name] if field_name in item else default
                    except (KeyError, TypeError):
                        return default
                    return default

                description = safe_get("description", "")
                anamnesis = safe_get("anamnesis", "")
                solution = safe_get("solution", "")
                outcome = safe_get("outcome", "")

                if not any([description, anamnesis, solution, outcome]):
                    logger.warning(f"Edustory {idx + 1}: No case study content found, skipping")
                    continue

                entry_id = safe_get("id", str(idx))

                student_age_year = safe_get("age, school year", "")
                student_hobbies = safe_get("hobbies", "")
                student_diagnoses = safe_get("diagnoses", "")
                student_disorders = safe_get("disorders", "")

                teacher_approbation = safe_get("approbation", "")
                teacher_practice_years = safe_get("practice_years", "")

                problems_annotated = safe_get("problems_annotated", "")
                problems_possible = safe_get("problems_possible_annotated", "")
                solutions_annotated = safe_get("solutions_annotated", "")
                solutions_possible = safe_get("solutions_possible_annotated", "")
                implications_annotated = safe_get("implications_annotated", "")
                implications_possible = safe_get("implications_possible_annotated", "")

                annotator_id = safe_get("annotator_id", "")

                doc = {
                    "content_id": f"edustory/{entry_id}",
                    "content": self._create_content(item),
                    "metadata": {
                        "pack": "warbler-pack-edustories",
                        "source_dataset": dataset_name,
                        "entry_id": str(entry_id),
                        "student_age_year": student_age_year,
                        "student_hobbies": student_hobbies,
                        "student_diagnoses": student_diagnoses,
                        "student_disorders": student_disorders,
                        "teacher_approbation": teacher_approbation,
                        "teacher_practice_years": teacher_practice_years,
                        "problems_annotated": problems_annotated,
                        "problems_possible_annotated": problems_possible,
                        "solutions_annotated": solutions_annotated,
                        "solutions_possible_annotated": solutions_possible,
                        "implications_annotated": implications_annotated,
                        "implications_possible_annotated": implications_possible,
                        "annotator_id": annotator_id,
                        "realm_type": "educational",
                        "realm_label": "educational_case_studies",
                        "lifecycle_stage": "emergence",
                        "activity_level": 0.7,
                        "dialogue_type": "teaching_case_study",
                        "license": "MIT",
                    },
                }
                warbler_docs.append(doc)

        logger.info(f"✓ Transformed {len(warbler_docs)} educational case study entries")
        return warbler_docs

    @staticmethod
    def _create_content(item: Dict[str, Any]) -> str:
        """Create content string for educational case studies.

        With structured teaching situations.
        """

        def safe_get(field_name: str, default: str = "") -> str:
            try:
                if isinstance(item, dict):
                    return item.get(field_name, default) or default
                elif hasattr(item, "__getitem__"):
                    return item[field_name] if field_name in item else default
            except (KeyError, TypeError):
                return default
            return default

        description = safe_get("description", "[No background provided]")
        anamnesis = safe_get("anamnesis", "[No situation description provided]")
        solution = safe_get("solution", "[No intervention described]")
        outcome = safe_get("outcome", "[No outcome reported]")

        student_age_year = safe_get("age, school year", "")
        student_hobbies = safe_get("hobbies", "")
        student_diagnoses = safe_get("diagnoses", "")
        student_disorders = safe_get("disorders", "")

        student_profile_parts = []
        if student_age_year:
            student_profile_parts.append(f"Age/Year: {student_age_year}")
        if student_hobbies:
            student_profile_parts.append(f"Hobbies: {student_hobbies}")
        if student_diagnoses:
            student_profile_parts.append(f"Diagnoses: {student_diagnoses}")
        if student_disorders:
            student_profile_parts.append(f"Disorders: {student_disorders}")

        student_profile = (
            "\n".join(student_profile_parts)
            if student_profile_parts
            else "[No student profile available]"
        )

        problems_annotated = safe_get("problems_annotated", "")
        solutions_annotated = safe_get("solutions_annotated", "")
        implications_annotated = safe_get("implications_annotated", "")

        annotation_parts = []
        if problems_annotated:
            annotation_parts.append(f"Problems Identified: {problems_annotated}")
        if solutions_annotated:
            annotation_parts.append(f"Solutions Applied: {solutions_annotated}")
        if implications_annotated:
            annotation_parts.append(f"Implications: {implications_annotated}")

        annotations = (
            "\n".join(annotation_parts) if annotation_parts else "[No annotations available]"
        )

        content = f"""TEACHING CASE STUDY

Background:
{description}

Situation (Anamnesis):
{anamnesis}

Teacher Intervention (Solution):
{solution}

Outcome:
{outcome}

Student Profile:
{student_profile}

Analysis & Annotations:
{annotations}

This case study documents a real classroom situation from student teacher experience."""

        return content
