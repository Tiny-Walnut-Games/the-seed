# The Seed

A practical framework evolving toward a fractal/chain-based addressing and retrieval model, integrated with the Living Dev Agent (TLDA) template. This page serves as the README and table of contents for onboarding. It focuses on what exists today and where to find it.

## What it is (today)
- A set of experiments and utilities exploring a 7-dimensional (STAT7) addressing model and deterministic serialization.
- A Unity-integrated project that uses TLDA as a template, with Seed-specific bridges and gameplay hooks under Assets/TWG and related packages.
- A growing codebase with Python experiments, C#/Unity integrations, and GitHub workflows.

What it is not (yet): a finished “fractal-chain” product. Several documents in lore describe long-term intent, metaphors, and speculative architectures; treat those as exploratory reading, not a completed spec.

## Where the code lives
- Core app and services: src/
- Seed engine experiments (Python): seed/engine/
- Scripts and utilities: scripts/
- Unity game code (Seed-specific): Assets/TWG/
- Unity package (core/warbler): packages/warbler-core/
- Workflows: .github/workflows/

Note: Many TLDA-related scripts exist (this repo builds on TLDA). Seed-specific pieces are concentrated under seed/, scripts/, Assets/TWG/, and packages/warbler-core/.

## Current status (truth-first)
- STAT7 validation framework exists: seed/engine/stat7_experiments.py
  - Implements EXP-01, EXP-02, EXP-03 (address uniqueness, retrieval efficiency, dimension necessity)
  - Runner: scripts/run_exp_phase1.py (quick/default/full modes)
- Unity bridges and gameplay stubs exist under Assets/TWG (e.g., chat, platform, visualization) and integrate with TLDA.
- CI/CD workflows are present under .github/workflows.

Validation results depend on your runtime and scale. The docs in lore may use forward-looking or celebratory language; rely on this page and IMPLEMENTATION_STATUS.md for the current view.

## Start here
- Implementation status: seed/docs/lore/TheSeedConcept/IMPLEMENTATION_STATUS.md
- Concept overview (exploratory): seed/docs/lore/TheSeedConcept/TheSeedConcept.md
- Firewall/architecture notes: seed/docs/lore/TheSeedConcept/WFC-FIREWALL-ARCHITECTURE.md
- Doctrine and integrity notes: seed/docs/lore/TheSeedConcept/DOCTRINE-INTEGRITY-SECURITY-SCROLLS.md

Optional deep-lore and mythos live under seed/docs/lore/TheSeedConcept/. These are valuable for vision and flavor but are not required to get productive.

## How Seed relates to TLDA
- TLDA is the template/base. This repo inherits a lot of TLDA scripts and structure.
- Seed adds experiments (seed/engine), scripts, and Unity bridges under Assets/TWG plus packages/warbler-core.
- When in doubt, read code first: prefer Assets/TWG, packages/warbler-core, seed/engine, and scripts.

## Minimal glossary
- STAT7: Seven-dimension addressing/serialization model explored in Python experiments.
- Bit-chain: Canonical, deterministic representation used to compute addresses.
- Fractal/chain: Long-term direction for hierarchical, self-similar addressing; not fully realized yet.

## Contributing/next steps
- If you’re onboarding: clone, explore seed/engine and scripts/, then open Assets/TWG and packages/warbler-core in Unity.
- If you’re validating: run scripts/run_exp_phase1.py with quick mode and inspect results JSON; adjust scales as needed.
- If you’re integrating: treat IMPLEMENTATION_STATUS.md as the source of truth; file issues for gaps between lore and code.

Feedback welcome. The goal is clarity over hype: ship working parts, describe the rest plainly.
