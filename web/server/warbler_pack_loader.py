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
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


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
    
    Provides slot-filling and reputation-aware template filtering.
    """
    
    def __init__(self, pack_root_path: Optional[Path] = None):
        """
        Initialize pack loader.
        
        Args:
            pack_root_path: Root path to warbler packs directory.
                          If None, uses default: packages/com.twg.the-seed/The Living Dev Agent/packs/
        """
        if pack_root_path is None:
            # Default path from repo root
            pack_root_path = Path(__file__).parent.parent.parent / "packages" / "com.twg.the-seed" / \
                           "The Living Dev Agent" / "packs"
        
        self.pack_root = pack_root_path
        self.templates: Dict[str, ConversationTemplate] = {}
        self.templates_by_tag: Dict[str, List[str]] = {}  # tag -> list of template_ids
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
    
    def get_stats(self) -> Dict[str, Any]:
        """Get loader statistics."""
        return {
            "total_templates": len(self.templates),
            "packs_loaded": len(set(t.pack_name for t in self.templates.values())),
            "tags": list(self.templates_by_tag.keys()),
            "tag_distribution": {tag: len(ids) for tag, ids in self.templates_by_tag.items()}
        }