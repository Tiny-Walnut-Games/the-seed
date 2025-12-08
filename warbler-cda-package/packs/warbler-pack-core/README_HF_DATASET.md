---
license: mit
datasets:
  - tiny-walnut-games/warbler-pack-core
pretty_name: Warbler Pack Core - Conversation Templates
description: Essential conversation templates for the Warbler NPC conversation system
language:
  - en
tags:
  - warbler
  - conversation
  - npc
  - templates
  - dialogue
size_categories:
  - n<1K
source_datasets: []
---

# Warbler Pack Core - Conversation Templates

Essential conversation templates for the Warbler NPC conversation system.

## Dataset Overview

This dataset contains foundational conversation templates that form the backbone of NPC interactions. It includes greetings, farewells, help responses, trade inquiries, and general conversation fallbacks suitable for a wide variety of NPCs and scenarios.

**Documents**: ~10 templates
**Language**: English
**License**: MIT
**Source**: Tiny Walnut Games - The Seed Project

## Dataset Structure

```
{
  "template_id": str,
  "intent_types": [str],
  "content": str,
  "required_slots": [str],
  "tags": [str],
  "max_length": int
}
```

## Template Categories

- **Greetings**: friendly and formal greetings for NPCs
- **Farewells**: warm and professional goodbyes
- **Help & Assistance**: general assistance offers
- **Commerce**: trade and merchant interactions
- **Conversation**: fallback templates for maintaining conversation flow

## Use Cases

- NPC dialogue systems
- Conversational AI training
- Game narrative generation
- Interactive fiction engines
- Dialogue management systems

## Attribution

Part of **Warbler CDA** (Cognitive Development Architecture) - a production-ready RAG system featuring FractalStat multi-dimensional addressing.

**Project**: [The Seed](https://github.com/tiny-walnut-games/the-seed)
**Organization**: [Tiny Walnut Games](https://github.com/tiny-walnut-games)

## Related Datasets

- [warbler-pack-faction-politics](https://huggingface.co/datasets/tiny-walnut-games/warbler-pack-faction-politics) - Political intrigue templates
- [warbler-pack-wisdom-scrolls](https://huggingface.co/datasets/tiny-walnut-games/warbler-pack-wisdom-scrolls) - Wisdom generation templates
- [warbler-pack-hf-npc-dialogue](https://huggingface.co/datasets/tiny-walnut-games/warbler-pack-hf-npc-dialogue) - NPC dialogue from HuggingFace sources

## License

MIT License - See project LICENSE file for details.
