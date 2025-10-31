"""
Warbler Pack Loader: Load and manage conversation templates from pack files

Loads JSON template files from warbler packs and provides slot-filling
and reputation-aware template selection for NPC dialogue generation.

Features:
- Load templates from multiple warbler packs
- Slot-filling with dialogue context variables
- Reputation-aware template filtering
- Template caching for performance
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TemplateSlot:
    """A slot to be filled in a template."""
    name: str
    slot_type: str  # "string", "number", etc.
    required: bool
    description: str
    default: Any = None


@dataclass
class ConversationTemplate:
    """A conversation template from a warbler pack."""
    template_id: str
    version: str
    title: str
    description: str
    content: str
    slots: List[TemplateSlot]
    tags: List[str]
    max_length: int
    pack_name: str = ""


class WarblerPackLoader:
    """
    Loads Warbler conversation templates from pack files.
    
    Provides slot-filling, reputation-aware template filtering, and
    semantic similarity search using embeddings (Phase 3).
    """
    
    def __init__(self, pack_root_path: Optional[Path] = None, embedding_service: Optional[Any] = None):
        """
        Initialize pack loader.
        
        Args:
            pack_root_path: Root path to warbler packs directory.
                          If None, uses default: packages/com.twg.the-seed/The Living Dev Agent/packs/
            embedding_service: Optional WarblerEmbeddingService for semantic search
        """
        if pack_root_path is None:
            # Default path from repo root
            pack_root_path = Path(__file__).parent.parent.parent / "packages" / "com.twg.the-seed" / \
                           "The Living Dev Agent" / "packs"
        
        self.pack_root = pack_root_path
        self.templates: Dict[str, ConversationTemplate] = {}
        self.templates_by_tag: Dict[str, List[str]] = {}  # tag -> list of template_ids
        self.embedding_service = embedding_service  # Optional semantic search
        self.jsonl_documents: Dict[str, Dict[str, Any]] = {}  # document_id -> document data
        self.reputation_tier_to_template_selector = {
            "revered": self._select_reverent_templates,
            "trusted": self._select_friendly_templates,
            "neutral": self._select_neutral_templates,
            "suspicious": self._select_suspicious_templates,
            "hostile": self._select_hostile_templates,
        }
    
    def load_pack(self, pack_name: str) -> bool:
        """
        Load templates from a warbler pack.
        
        Args:
            pack_name: Name of the pack (e.g., "warbler-pack-core")
            
        Returns:
            True if loaded successfully, False otherwise
        """
        pack_path = self.pack_root / pack_name / "pack" / "templates.json"
        
        if not pack_path.exists():
            print(f"Warning: Pack file not found: {pack_path}")
            return False
        
        try:
            with open(pack_path, 'r', encoding='utf-8') as f:
                pack_data = json.load(f)
            
            # Load templates from this pack
            for template_data in pack_data.get("templates", []):
                template_id = template_data.get("id", "")
                
                # Convert slots to TemplateSlot objects
                slots = [
                    TemplateSlot(
                        name=slot["name"],
                        slot_type=slot.get("type", "string"),
                        required=slot.get("required", False),
                        description=slot.get("description", ""),
                        default=slot.get("default")
                    )
                    for slot in template_data.get("requiredSlots", [])
                ]
                
                template = ConversationTemplate(
                    template_id=template_id,
                    version=template_data.get("version", "1.0.0"),
                    title=template_data.get("title", ""),
                    description=template_data.get("description", ""),
                    content=template_data.get("content", ""),
                    slots=slots,
                    tags=template_data.get("tags", []),
                    max_length=template_data.get("maxLength", 500),
                    pack_name=pack_name
                )
                
                self.templates[template_id] = template
                
                # Index by tags
                for tag in template.tags:
                    if tag not in self.templates_by_tag:
                        self.templates_by_tag[tag] = []
                    self.templates_by_tag[tag].append(template_id)
            
            print(f"Loaded {len(pack_data.get('templates', []))} templates from {pack_name}")
            return True
            
        except Exception as e:
            print(f"Error loading pack {pack_name}: {e}")
            return False
    
    def load_all_packs(self) -> int:
        """
        Load all available packs from pack root.
        
        Returns:
            Number of packs loaded
        """
        if not self.pack_root.exists():
            print(f"Pack root not found: {self.pack_root}")
            return 0
        
        # Find all pack directories
        pack_dirs = [d for d in self.pack_root.iterdir() 
                    if d.is_dir() and d.name.startswith("warbler-pack-")]
        
        count = 0
        for pack_dir in pack_dirs:
            if self.load_pack(pack_dir.name):
                count += 1
        
        return count
    
    def fill_slots(self, template: ConversationTemplate, 
                  context: Dict[str, Any]) -> str:
        """
        Fill template slots with context values.
        
        Args:
            template: Template to fill
            context: Dictionary with values for slot filling
            
        Returns:
            Filled template string
        """
        content = template.content
        
        # Fill each slot in the template
        for slot in template.slots:
            placeholder = f"{{{{{slot.name}}}}}"
            value = context.get(slot.name, slot.default or f"[{slot.name}]")
            content = content.replace(placeholder, str(value))
        
        return content
    
    def select_template_for_reputation(self, 
                                      reputation_tier: str,
                                      context_tags: Optional[List[str]] = None) -> Optional[ConversationTemplate]:
        """
        Select a template based on player reputation tier.
        
        Args:
            reputation_tier: One of "revered", "trusted", "neutral", "suspicious", "hostile"
            context_tags: Optional list of tags to filter templates (e.g., ["greeting", "friendly"])
            
        Returns:
            Selected ConversationTemplate or None
        """
        selector = self.reputation_tier_to_template_selector.get(reputation_tier)
        if not selector:
            return None
        
        # Get candidate templates based on tags
        candidates = self._get_candidates(context_tags)
        
        # Select from candidates using reputation-specific logic
        return selector(candidates)
    
    def _get_candidates(self, tags: Optional[List[str]]) -> List[ConversationTemplate]:
        """Get templates matching tags."""
        if not tags:
            return list(self.templates.values())
        
        # Find templates with any of the requested tags
        candidate_ids = set()
        for tag in tags:
            candidate_ids.update(self.templates_by_tag.get(tag, []))
        
        return [self.templates[tid] for tid in candidate_ids]
    
    def _select_reverent_templates(self, candidates: List[ConversationTemplate]) -> Optional[ConversationTemplate]:
        """Select reverent/respectful templates."""
        # Prefer formal, respectful tags
        for t in candidates:
            if any(tag in t.tags for tag in ["formal", "reverent", "respectful", "blessing"]):
                return t
        return candidates[0] if candidates else None
    
    def _select_friendly_templates(self, candidates: List[ConversationTemplate]) -> Optional[ConversationTemplate]:
        """Select friendly, warm templates."""
        for t in candidates:
            if any(tag in t.tags for tag in ["friendly", "warm", "casual", "joyful"]):
                return t
        return candidates[0] if candidates else None
    
    def _select_neutral_templates(self, candidates: List[ConversationTemplate]) -> Optional[ConversationTemplate]:
        """Select neutral, professional templates."""
        for t in candidates:
            if any(tag in t.tags for tag in ["neutral", "professional", "business", "formal"]):
                return t
        return candidates[0] if candidates else None
    
    def _select_suspicious_templates(self, candidates: List[ConversationTemplate]) -> Optional[ConversationTemplate]:
        """Select suspicious/cautious templates."""
        for t in candidates:
            if any(tag in t.tags for tag in ["warning", "suspicious", "wary", "caution"]):
                return t
        # If no specific suspicious templates, use neutral
        return self._select_neutral_templates(candidates)
    
    def _select_hostile_templates(self, candidates: List[ConversationTemplate]) -> Optional[ConversationTemplate]:
        """Select hostile/aggressive templates."""
        for t in candidates:
            if any(tag in t.tags for tag in ["hostile", "aggressive", "threat", "warning"]):
                return t
        # If no specific hostile templates, use suspicious
        return self._select_suspicious_templates(candidates)
    
    def get_templates_by_tag(self, tag: str) -> List[ConversationTemplate]:
        """Get all templates with a specific tag."""
        template_ids = self.templates_by_tag.get(tag, [])
        return [self.templates[tid] for tid in template_ids]
    
    def get_dialogue_starters(self) -> List[ConversationTemplate]:
        """Get all greeting/dialogue starter templates."""
        return self.get_templates_by_tag("greeting")
    
    def get_dialogue_closers(self) -> List[ConversationTemplate]:
        """Get all farewell/dialogue close templates."""
        return self.get_templates_by_tag("farewell")
    
    def load_jsonl_pack(self, pack_name: str) -> int:
        """
        Load JSONL documents from a pack (e.g., HuggingFace dataset pack).
        
        Args:
            pack_name: Name of the pack (e.g., "warbler-pack-hf-npc-dialogue")
            
        Returns:
            Number of documents loaded
        """
        pack_dir = self.pack_root / pack_name
        if not pack_dir.exists():
            logger.warning(f"Pack directory not found: {pack_dir}")
            return 0
        
        # Find JSONL files
        jsonl_files = list(pack_dir.glob("*.jsonl"))
        if not jsonl_files:
            logger.warning(f"No JSONL files found in {pack_dir}")
            return 0
        
        count = 0
        for jsonl_file in jsonl_files:
            try:
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            doc = json.loads(line)
                            doc_id = doc.get("content_id", f"{pack_name}_{count}")
                            self.jsonl_documents[doc_id] = doc
                            count += 1
                
                logger.info(f"✓ Loaded {count} documents from {jsonl_file.name}")
            except Exception as e:
                logger.error(f"Error loading {jsonl_file}: {e}")
        
        return count
    
    def build_embeddings(self, embedding_service: Optional[Any] = None) -> bool:
        """
        Build embeddings for all loaded templates and documents.
        
        Args:
            embedding_service: WarblerEmbeddingService instance
            
        Returns:
            True if embeddings built successfully
        """
        if embedding_service:
            self.embedding_service = embedding_service
        
        if not self.embedding_service:
            logger.warning("No embedding service provided")
            return False
        
        # Prepare template data for embedding
        templates_to_embed = []
        for template_id, template in self.templates.items():
            templates_to_embed.append({
                "template_id": template_id,
                "content": template.content,
                "metadata": {
                    "title": template.title,
                    "description": template.description,
                    "pack": template.pack_name,
                    "max_length": template.max_length
                },
                "tags": template.tags
            })
        
        # Prepare JSONL documents for embedding
        for doc_id, doc in self.jsonl_documents.items():
            templates_to_embed.append({
                "template_id": doc_id,
                "content": doc.get("content", ""),
                "metadata": doc.get("metadata", {}),
                "tags": []
            })
        
        if templates_to_embed:
            try:
                self.embedding_service.add_templates_batch(templates_to_embed)
                logger.info(f"✓ Built embeddings for {len(templates_to_embed)} items")
                return True
            except Exception as e:
                logger.error(f"Error building embeddings: {e}")
                return False
        
        return True
    
    def search_semantic(
        self,
        query: str,
        top_k: int = 5,
        reputation_tier: Optional[str] = None
    ) -> List[Tuple[str, float, Any]]:
        """
        Find semantically similar templates/documents.
        
        Args:
            query: Query text (e.g., player input)
            top_k: Number of results to return
            reputation_tier: Optional reputation filter
            
        Returns:
            List of (template_id, similarity_score, template/document)
        """
        if not self.embedding_service:
            logger.warning("Embedding service not available for semantic search")
            return []
        
        results = self.embedding_service.search_semantic(
            query, top_k=top_k, reputation_tier=reputation_tier
        )
        
        # Enrich results with template/document data
        enriched = []
        for template_id, similarity, embedded_template in results:
            # Get template if it exists
            if template_id in self.templates:
                enriched.append((template_id, similarity, self.templates[template_id]))
            elif template_id in self.jsonl_documents:
                enriched.append((template_id, similarity, self.jsonl_documents[template_id]))
        
        return enriched
    
    def get_stats(self) -> Dict[str, Any]:
        """Get loader statistics."""
        stats = {
            "total_templates": len(self.templates),
            "jsonl_documents_loaded": len(self.jsonl_documents),
            "packs_loaded": len(set(t.pack_name for t in self.templates.values())),
            "tags": list(self.templates_by_tag.keys()),
            "tag_distribution": {tag: len(ids) for tag, ids in self.templates_by_tag.items()}
        }
        
        if self.embedding_service:
            stats["embedding_service"] = self.embedding_service.get_stats()
        
        return stats