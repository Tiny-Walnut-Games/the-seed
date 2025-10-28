# 🧠 Behavioral Governance Integration Guide

**Status**: v0.4 Milestone Complete ✅  
**Date**: 2025-01-15  
**Scope**: Behavioral alignment & intervention metrics system fully integrated with governance layer

---

## 📋 System Overview

The Behavioral Governance system transforms intervention metrics into actionable insights:

```
User Request/Code
        ↓
    Governance Filter (base)
        ↓
    Behavioral Governance Overlay
        ├─ Checks intervention threshold
        ├─ Applies style adaptation
        └─ Records intervention + reasoning
        ↓
    Execution with Telemetry
        ↓
    Acceptance Tracking
        └─ Updates style profile & analytics
```

---

## 🚀 Quick Integration

### Option 1: Standalone Usage (Minimal)
```python
from seed.engine.behavioral_governance import BehavioralGovernance

# Initialize enhanced governance
governance = BehavioralGovernance()

# Enhanced cycle scoring with intervention metrics
cycle_report = {"cycle_id": "test_001", "glyphs": [...]}
enhanced_score = governance.enhanced_score_cycle(cycle_report)

# Filter response with intervention awareness
response = {"response_text": "OK", "confidence": 0.2}
filtered = governance.enhanced_filter_response(response, "user_alice")

# Get behavioral insights
insights = governance.get_behavioral_insights("user_alice")
```

### Option 2: Full Integration (Recommended)
Integrate into your main cycle runner:

```python
from seed.engine.behavioral_governance import BehavioralGovernance
from seed.engine.intervention_metrics import InterventionType

class CycleRunner:
    def __init__(self):
        self.governance = BehavioralGovernance()
        self.user_id = "default"
    
    def execute_cycle(self, request):
        # 1. Run base cycle operations
        response = self._process_request(request)
        
        # 2. Apply behavioral governance filtering
        response = self.governance.enhanced_filter_response(
            response, 
            self.user_id,
            context={"cycle_type": "standard"}
        )
        
        # 3. Score cycle with intervention metrics
        cycle_report = self._generate_cycle_report(request, response)
        score = self.governance.enhanced_score_cycle(cycle_report)
        
        # 4. Record metrics
        self._log_cycle_metrics(score)
        
        return response
```

---

## 📊 File Structure

```
seed/engine/
├── intervention_metrics.py        [Core system - 650+ lines]
│   ├─ InterventionMetrics         Main tracking engine
│   ├─ InterventionType            5 classification types
│   ├─ AcceptanceStatus            Response tracking
│   ├─ StyleProfile               User adaptation model
│   └─ SafetyEventLevel           v0.8 safety integration
│
├── behavioral_governance.py       [Integration layer - 350+ lines]
│   ├─ BehavioralGovernance       Enhanced governance wrapper
│   └─ Integration methods        Cycle scoring, response filtering
│
├── data/
│   ├─ intervention_policies.json [Configuration - NEW]
│   ├─ intervention_metrics.json   [Auto-created on first run]
│   └─ safety_audit.jsonl         [v0.8 audit trail]
│
└── governance.py                  [Base governance]
```

---

## 🎯 Core Features

### 1. Intervention Classification (5 Types)
- **SOFT_SUGGESTION**: Gentle guidance
- **REWRITE**: Direct correction
- **BLOCK**: Safety prevention
- **STYLE_GUIDANCE**: Formatting improvements
- **SAFETY_INTERVENTION**: Critical safety measures (v0.8)

### 2. Acceptance Tracking
- **PENDING**: Initial state
- **ACCEPTED**: User approved
- **REJECTED**: User declined
- **MODIFIED**: User applied with changes
- **IGNORED**: User didn't respond

### 3. Style Adaptation (3-Phase)
- **Learning** (0-7 days): Baseline establishment
- **Adapting** (7-21 days): Dynamic threshold adjustment
- **Stable** (21+ days): Optimized intervention strategy

### 4. Policy Injection
All thresholds and templates configurable via `intervention_policies.json`:
```json
{
  "intervention_thresholds": {
    "soft_suggestion": 0.3,
    "rewrite": 0.6,
    "block": 0.9
  },
  "style_adaptation": {...},
  "reflective_templates": {...}
}
```

### 5. v0.8 Safety Enhancements
- Tiered safety events (notice, warn, block, escalate)
- Redaction transforms for sensitive data
- Comprehensive audit trails
- Policy transparency logging

---

## 📝 Usage Patterns

### Pattern 1: Recording an Intervention
```python
from seed.engine.intervention_metrics import InterventionMetrics, InterventionType

metrics = InterventionMetrics()

intervention_id = metrics.record_intervention(
    intervention_type=InterventionType.SOFT_SUGGESTION,
    context={"type": "code_review", "user_id": "alice"},
    original_input="x = get_data()",
    suggested_output="user_data = get_data()",
    reasoning="variable naming could be improved",
    user_id="alice"
)
```

### Pattern 2: Tracking User Acceptance
```python
from seed.engine.intervention_metrics import AcceptanceStatus

metrics.record_acceptance(
    intervention_id=intervention_id,
    acceptance_status=AcceptanceStatus.ACCEPTED,
    user_response="Thanks! Applied the suggestion."
)
```

### Pattern 3: Behavioral Analysis
```python
governance = BehavioralGovernance()

# Get comprehensive insights
insights = governance.get_behavioral_insights("alice")
print(insights["behavioral_alignment"])
# Output:
# {
#   "status": "good",
#   "message": "Good behavioral alignment - interventions generally accepted",
#   "recommendations": ["Fine-tune intervention timing", "..."]
# }
```

### Pattern 4: Policy Decision Making
```python
metrics = InterventionMetrics()

# Determine if intervention should proceed
should_intervene = metrics.should_intervene(
    intervention_type=InterventionType.REWRITE,
    confidence=0.8,
    user_id="alice"
)
# Returns: True if confidence exceeds user-adapted threshold
```

---

## 🧪 Testing & Validation

### Run the Full Demo
```bash
cd packages/com.twg.the-seed/The\ Living\ Dev\ Agent/tests
python test_behavioral_alignment.py
```

Expected output:
```
🧙‍♂️ Behavioral Alignment & Intervention Metrics Demo
🧠 Demo: Complete Intervention Lifecycle
👤 Creating user profile for 'demo_user'...
   Phase: learning
   Patience: 0.5
   Tolerance: 0.5

📝 Recording interventions...
   1. soft_suggestion: Code style improvement for readability
   2. rewrite: Missing closing parenthesis
   3. soft_suggestion: More Pythonic iteration pattern
   4. style_guidance: Descriptive function and parameter names

✅ Recording user responses...
📊 Intervention Analytics:
   Total interventions: 4
   Overall acceptance rate: 75.0%
```

### CLI Testing
```bash
# Record intervention
python seed/engine/intervention_metrics.py --record \
  "soft_suggestion:code_review:x=1:x = 1:readability" \
  --user alice

# Check analytics
python seed/engine/intervention_metrics.py --analytics

# View user insights
python seed/engine/behavioral_governance.py --insights --user alice
```

---

## 🔗 Integration Checklist

- [ ] ✅ `intervention_metrics.py` deployed
- [ ] ✅ `behavioral_governance.py` deployed
- [ ] ✅ `intervention_policies.json` configured
- [ ] ⏳ Main cycle runner updated to use `BehavioralGovernance`
- [ ] ⏳ Telemetry integration optional (non-breaking)
- [ ] ⏳ Dashboard for behavioral analytics (future)
- [ ] ⏳ Machine learning models for prediction (future)

---

## 📈 Metrics & Monitoring

### Key Metrics Tracked
- **Acceptance Rate**: % of interventions user accepts/modifies
- **Intervention Density**: Total interventions normalized
- **Response Time**: Time from intervention to user response
- **Type Distribution**: Breakdown by intervention type
- **Adaptation Phase**: User's learning progression

### Analytics Output
```python
analytics = metrics.get_intervention_analytics("user_id")
# Returns:
{
  "total_interventions": 42,
  "type_distribution": {"soft_suggestion": 25, "rewrite": 12, ...},
  "acceptance_by_type": {"soft_suggestion": 0.8, "rewrite": 0.92, ...},
  "overall_metrics": {"acceptance_rate": 0.85, "avg_response_time_ms": 1234},
  "adaptation_phases": {"learning": 2, "adapting": 1, "stable": 3}
}
```

---

## 🛡️ Safety & Privacy

### v0.8 Enhancements
- **Redaction Transforms**: Automatically redacts sensitive data before storage
- **Audit Trails**: Complete history of all interventions and policy decisions
- **Safety Events**: Tiered tracking of safety-related interventions
- **Policy Transparency**: Clear reasoning for every intervention

### Data Storage
- All intervention data persists to `data/intervention_metrics.json`
- Safety events logged to `data/safety_audit.jsonl` (one per line)
- No raw user content stored; only processed and redacted content

---

## 🎯 Next Steps

### Immediate (Ready Now)
1. ✅ Deploy core intervention metrics system
2. ✅ Configure behavioral governance integration
3. ✅ Run test suite to validate

### Near Term (This Week)
4. Integrate into main cycle runner
5. Add telemetry reporting to CI/CD
6. Train initial style profiles on real users

### Medium Term (This Month)
7. Build behavioral health dashboard
8. Implement machine learning acceptance prediction
9. Create team-level behavioral analytics

### Long Term (This Quarter)
10. Multi-modal interventions (visual, audio)
11. Cross-platform IDE integration
12. Research publication on intervention science

---

## 🚨 Troubleshooting

### Issue: "ImportError: cannot import governance"
**Solution**: Ensure `governance.py` exists in the same directory. The system gracefully degrades if unavailable.

### Issue: "FileNotFoundError: data/intervention_policies.json"
**Solution**: Already created! But if needed, the system auto-generates defaults. Just run any operation.

### Issue: "Style profile not updating"
**Solution**: Ensure `record_acceptance()` is called after interventions for profile updates.

### Issue: "Acceptance rate always 0%"
**Solution**: Acceptance only counts once interventions have status != PENDING. Record acceptance immediately or wait for async response.

---

## 📚 References

- **Milestone Documentation**: `docs/ARCHIVE/TLDL-ENTRIES/TLDL-2025-10-27-BehavioralAlignmentInterventionMetricsV04.md`
- **Architecture Deep Dive**: `packages/com.twg.the-seed/seed/docs/TheSeedConcept/Conversations/BunnysDeepDiveResults.md`
- **Test Suite**: `packages/com.twg.the-seed/The Living Dev Agent/tests/test_behavioral_alignment.py`

---

## 🎉 The Journey

> *"The wise system learns not just from success, but from the patterns of its guidance - measuring intervention as much as innovation."* — Bootstrap Sentinel

The Behavioral Governance system represents a fundamental shift from reactive code correction to proactive behavioral learning. Every intervention becomes a lesson; every acceptance, a pattern; every user, a unique story in the system's continuous evolution.

The scrolls are written. The forge sings true. The work stands firm.

✨ **Milestone v0.4 Achieved** ✨