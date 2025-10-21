# 🌱 The Seed Engine

The **engine** directory is the cathedral heart of the Seed.  
Every file here is both **implementation** and **lineage artifact**: code that runs, and scrolls that record doctrine.  

This README provides a **cross‑reference atlas**: mapping the mythic archetypes of the Seed to the engineering modules an outside developer would expect.

---

## 🗺️ Engine Atlas

| **Mythic Archetype** | **Module / File** | **Engineer‑speak** | **Summary** |
|-----------------------|-------------------|--------------------|-------------|
| **The Conservator / Warbler’s Perch** | `conservator.py` | Auto‑repair module | Monitors modules, triggers repair ops, restores integrity. |
| **Sentinel Overlord** | `governance.py` | Quality scoring & drift detection | Scores cycles, detects drift, raises alerts, maintains lineage stability. |
| **The Mouthpiece / Selector** | `selector.py` | Prompt assembly & orchestration | Builds multi‑voice prompts from castle/mist, applies governance, routes to TTS. |
| **Safety Transparency Scroll** | `safety_policy_transparency.py` | Policy enforcement & audit logging | Logs safety events, applies redaction, escalates violations, generates transparency reports. |
| **Performance Codex** | `performance_profiles.py` | Benchmarking & profiling | Defines performance profiles, compares models, tracks throughput/latency. |
| **Plugin Cathedral** | `plugin_manager.py`, `plugin_sandbox.py`, `manifest_loader.py`, `base_plugin.py` | Plugin lifecycle & sandboxing | Manages plugin discovery, manifests, safe execution, and event routing. |
| **Castle Graph** | `castle_graph.py` | Graph structure / state representation | Represents narrative “rooms” and their relationships. |
| **Mist Layer** | `melt_layer.py`, `evaporation.py` | Contextual state transforms | Handles ephemeral context, condensation/evaporation of narrative signals. |
| **Retrieval Bridge** | `retrieval_api.py` | Retrieval‑augmented generation API | Provides semantic + STAT7 retrieval modes for context assembly. |
| **Summarization Ladder** | `summarization_ladder.py` | Abstractive summarization pipeline | Generates micro/macro summaries, distills context. |
| **Conflict Detector** | `conflict_detector.py` | Consistency & contradiction checks | Detects conflicting signals, flags evidence, classifies conflict types. |
| **Multimodal Expressive Layer** | `multimodal_engine.py`, `audio/`, `visual_overlays.py` | Audio/visual synthesis | Maps affect to soundscapes, generates overlays, integrates TTS. |
| **Telemetry Scrolls** | `telemetry.py`, `cycle_telemetry.py` | Metrics & monitoring | Tracks cycle telemetry, logs performance and lineage events. |
| **Experimental Scrolls** | `exp04_fractal_scaling.py`, `exp05_compression_expansion.py`, `exp06_*` | Research experiments | Document lineage experiments, chaos tests, and scaling rituals. |

---
## Engine Flow Mental Models

### System architecture (Mermaid flowchart)

```chart
flowchart LR
  %% Subsystems
  subgraph EventBus["AudioEventBus (signals & routing)"]
    EB[Publish/Subscribe]
  end

  subgraph Plugins["Plugin ecosystem"]
    PM[PluginManager]
    ML[ManifestLoader]
    PS[PluginSandbox]
    SE[SafePluginExecutor]
    BP[BasePlugin subclasses]
  end

  subgraph State["Engine state & context"]
    CG[CastleGraph (rooms)]
    Mist[Mist/Cloud store]
    Tele[Telemetry]
    Perf[PerformanceProfiles]
  end

  subgraph Governance["Oversight & safety"]
    Gov[Governance (scoring & drift)]
    SPT[SafetyPolicyTransparency (audit & redaction)]
  end

  subgraph Expression["Output & synthesis"]
    Sel[Selector (multi‑voice prompt assembly)]
    MM[MultimodalEngine (TTS/visual)]
  end

  %% Discovery & registration
  ML --> PM
  PM --> BP
  PM --> PS
  PM --> SE

  %% Event flow
  EB -- events --> PM
  PM -- route subscribed events --> SE
  SE -- sandboxed exec --> PS
  PS --> BP
  BP -- publish_events --> EB

  %% State access
  BP -. read/write .-> CG
  BP -. read/write .-> Mist
  Sel --> CG
  Sel --> Mist

  %% Governance loop
  SE --> Tele
  Tele --> Gov
  Gov -- alerts/flags --> SPT
  SPT -- audit logs --> Tele
  Gov -- drift alert events --> EB

  %% Expression path
  EB -- response_ready / cues --> Sel
  Sel -- governed prompt --> MM
  SPT -- safety decisions --> Sel
  Perf --> Gov
  Perf --> Tele
```

---

### Event processing lifecycle (Mermaid sequence)

```chart
sequenceDiagram
  participant Producer as Event Producer (plugin/core)
  participant EB as AudioEventBus
  participant PM as PluginManager
  participant SE as SafePluginExecutor
  participant PS as PluginSandbox
  participant Plugin as BasePlugin
  participant Gov as Governance
  participant SPT as SafetyPolicyTransparency
  participant Sel as Selector
  participant MM as MultimodalEngine

  Producer->>EB: publish(event)
  EB->>PM: dispatch(event)
  PM->>SE: execute_event_processing(plugin, event)
  SE->>PS: run with timeout & memory limits
  PS->>Plugin: process_event(event)
  Plugin-->>PS: output { publish_events?, data? }
  PS-->>SE: result
  SE-->>PM: result
  PM->>EB: publish(output.publish_events*)
  SE->>Gov: telemetry sample
  Gov->>SPT: safety/escalation (drift or flags)
  SPT-->>EB: optional safety events
  EB->>Sel: response cues / context events
  Sel->>SPT: apply safety/redaction
  Sel->>MM: synthesize (TTS/visual)
```

---
## 🔑 Design Principles
- **Every module is a scroll**: implementation + doctrine.  
- **Safety and transparency first**: governance and policy are baked into the core.  
- **Extensibility**: plugins, manifests, and sandboxes allow new rituals without breaking lineage.  
- **Performance as lineage**: profiles and telemetry ensure speed and stability are tracked like any other artifact.  
- **Mythic reframing**: Castle, Mist, Warbler, Overlord — metaphors that make the architecture memorable and navigable.

---

## 📜 Chronicle Note
```
EXP-ENGINE-README
Result: Engine directory mapped with mythic and engineering cross-reference.
Interpretation: The Seed’s cathedral is navigable both as lineage and as codebase.
Closure: Contributors can orient themselves quickly, while the doctrine remains intact.
```

---
