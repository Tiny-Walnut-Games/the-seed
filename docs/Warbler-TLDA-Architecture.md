# 🧠 Warbler + TLDA: End-to-End Cognition Engine Architecture

This document outlines the full system architecture behind Warbler—the modular cognition engine—and TLDA, the structured logging system. Together, they form a teachable, versioned, and cloud-feedable framework for NPC narration, memory graphs, and contributor rituals.

---

## 🧩 System Overview

Warbler is a runtime engine that synthesizes ambient narration and NPC responses using structured memory, emotional state, and contributor logs. TLDA (Temporal Log of Development Artifacts) captures every meaningful event as a fragment, which fuels Warbler's evolution.

The system is modular, versioned, and designed for Unity DOTS projects. It supports local-only operation, cloud enrichment (opt-in), and contributor-facing feedback loops.

---

## 🧙 Flowchart: Ritual Lifecycle

```mermaid
flowchart TD
    A[Inputs] --> B[TLDA Capture]
    B --> C[Giant Compression]
    C --> D[Magma Store]
    D --> E[Evaporation]
    E --> F[Warbler Cloud]
    F --> G[Selector + Synthesizer]
    G --> H[Mind Castle Graph]
    H --> I[Governance & Faculty Rules]
    I --> J[Outputs: NPC lines, UI narration, logs]
    J --> K[Pets & Local Agents]
    K --> L[Cloud Feed (opt-in)]
    L --> F
```

---

## 🧠 Component Breakdown

| Component | Role |
|----------|------|
| TLDAFragment | Immutable log of events, annotated with emotional weight and tags |
| GiantCompressor | Clusters and compresses TLDA fragments into latent magma |
| MagmaStore | Persistent memory layer for compressed fragments |
| EvaporationEngine | Distills magma into lightweight mist lines |
| WarblerCloud | Ambient proto-thought stream (local or cloud-fed) |
| Selector | Scores mist lines based on context and resonance |
| Synthesizer | Assembles final narration from selected lines |
| CastleGraph | Long-term memory graph with heat/decay and backlinks |
| Governance | Enforces safety, privacy, and symbolic integrity |
| Pets | Local agents that assist with compression and sharing |
| Faculty | Advisor, Oracle, Sentinel roles for contributor rituals |

---

## 🛠️ Code Snippets (Simplified)

### TLDA Fragment

```csharp
[CreateAssetMenu(menuName="Warbler/TLDA Fragment")]
public sealed class TLDAFragment : ScriptableObject
{
    public string Id;
    public string Source;
    public string Text;
    public float EmotionalWeight;
    public string[] Tags;
    public string ProvenanceHash;
    public long UnixMillis;
}
```

### Giant Compression

```csharp
public interface IGiantCompressor
{
    IEnumerable<MagmaEntry> Compress(IEnumerable<TLDAFragment> fragments);
}
```

### Evaporation

```csharp
public interface IEvaporationEngine
{
    IEnumerable<MistLine> Distill(IEnumerable<MagmaEntry> magma);
}
```

### Selector + Synthesizer

```csharp
public interface ISelector
{
    IEnumerable<MistLine> Rank(IEnumerable<MistLine> candidates, SelectionContext ctx);
}

public sealed class Synthesizer
{
    public string Compose(IEnumerable<MistLine> ranked, SelectionContext ctx)
        => string.Join(" ", TakeTopFragments(ranked, ctx.MaxFragments));
}
```

### Castle Graph

```csharp
public sealed class CastleGraph
{
    public void Touch(string id, float deltaHeat, string[] backlinks) { /* ... */ }
    public void Decay(float factor = 0.98f) { /* ... */ }
}
```

---

## ☁️ Cloud Feed (Optional)

- Contributors can opt-in to share distilled mist lines.
- No raw TLDA fragments are uploaded.
- Cloud enrichment improves Warbler's ambient narration and onboarding suggestions.

---

## 📦 Distribution & Updates

- Warbler is versioned via `npm`, Unity package, or Git submodule.
- Conversation packs (`warbler-pack-*`) are modular and updateable.
- Dependabot + RitualBot Phase 0 automate PRs and merges.

---

## 🧾 TLDA Fragment Example

```json
{
  "id": "TLDA-2025-09-02-WarblerGenesis",
  "source": "Warbler",
  "text": "The mist thickens. The Giant has stomped. The Castle remembers.",
  "emotional_weight": 0.9,
  "tags": ["origin", "narration", "selector", "cloud"]
}
```

---

## 🧙 Summary

This system is:

- Modular 🧩
- Teachable 📜
- Scrollworthy 🧙‍♂️
- Cloud-aware ☁️
- Emotionally annotated 🧠

It's not a full LLM. It's a **cognition scaffold**—a deterministic, explainable engine that narrates, remembers, and evolves through contributor rituals.

You can drop it into a Unity project, feed it TLDA fragments, and watch it synthesize ambient narration that reflects your development journey.

---
