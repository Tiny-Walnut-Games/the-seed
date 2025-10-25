# 🧙‍♂️ Warbler → School → Report Orchestration Integration Guide

## The Problem We're Solving

Previously, the workflow felt disconnected:
```
❌ Warbler analyzes → (lost) → School runs experiments → (isolated) → Report generated
```

Now it flows with strategic continuity:
```
✅ Warbler analyzes → (saved) → School uses context → (validated) → Report produces intelligence
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ WarblerIntelligentOrchestrator                                  │
│ (Produces ProjectAnalysis)                                      │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓ (NEW) SaveWarblerAnalysis()
┌──────────────────────────────────────────────────────────────────┐
│ WarblerContextBridge                                             │
│ - Saves ProjectAnalysis to persistent context                   │
│ - Generates strategic hypotheses                                │
│ - Creates TLDL entry for continuity                            │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓ LoadActiveAnalysis() in School stages
┌──────────────────────────────────────────────────────────────────┐
│ SchoolExperimentWorkbench (Stages 0-5)                          │
│ - Stage 1: Hypotheses informed by Warbler analysis              │
│ - Stage 2: Manifests reference Warbler strategies               │
│ - Stage 3-4: Run experiments and validate                       │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓ CollectValidatedClaims()
┌──────────────────────────────────────────────────────────────────┐
│ IntelligenceSynthesizer                                          │
│ - Combines Warbler context + validated claims                   │
│ - Produces strategic recommendations (70% AI-quality)           │
│ - Generates risk assessments and priorities                     │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓ GenerateIntelligenceReport()
┌──────────────────────────────────────────────────────────────────┐
│ ReportSynthesizer (Stage 5)                                      │
│ Output: Actionable Intelligence Report                          │
│ - Strategic summary                                             │
│ - Priorities with validation status                             │
│ - Evidence-based recommendations                                │
│ - Risk assessment with mitigations                              │
│ - Next steps (immediate/week/month)                             │
└──────────────────────────────────────────────────────────────────┘
```

## Integration Steps

### Step 1: Hook Warbler to Save Analysis

In `WarblerIntelligentOrchestrator.cs`, modify the execution methods:

```csharp
// In ExecuteAIProjectSetup() after analysis completes
if (analysis != null)
{
    // NEW: Save analysis to School context
    WarblerContextBridge.SaveWarblerAnalysis(
        analysis, 
        projectRequest, 
        preferGitHubCopilot ? "GitHub Copilot" : "Ollama"
    );
    
    // NEW: Create TLDL entry for continuity
    var context = WarblerContextBridge.LoadActiveAnalysis();
    WarblerContextBridge.CreateTLDLFromWarbler(context);
    
    // Existing: Create project structure, etc.
    await CreateIntelligentProjectStructure(analysis);
}
```

**Location:** `WarblerIntelligentOrchestrator.cs` around line 900-950 (in ExecuteAIProjectSetup method)

### Step 2: Update School Hypothesis Stage

In `HypothesisExtractor.cs`, load Warbler context:

```csharp
// At start of hypothesis generation
var warblerContext = WarblerContextBridge.LoadActiveAnalysis();

if (warblerContext != null)
{
    // Use Warbler's strategic hypotheses as seeds
    var hypotheses = new List<Hypothesis>(warblerContext.strategic_hypotheses.Select(h =>
        new Hypothesis { content = h }
    ));
    
    // Add user hypotheses on top
    hypotheses.AddRange(userHypotheses);
    
    return hypotheses;
}
```

**Location:** `Assets/TWG/TLDA/Tools/School/Editor/HypothesisExtractor.cs` (modify generation method)

### Step 3: Update Report Synthesizer

In `ReportSynthesizer.cs`, add intelligence synthesis:

```csharp
private async Task GenerateReport()
{
    isGenerating = true;
    
    try
    {
        // Step 1: Load Warbler context
        var warblerContext = WarblerContextBridge.LoadActiveAnalysis();
        
        // Step 2: Get validated claims
        LoadValidatedClaims();
        
        // Step 3: Synthesize intelligence
        var intelligence = IntelligenceSynthesizer.Synthesize(
            warblerContext,
            loadedClaims
        );
        
        // Step 4: Generate markdown report
        string reportContent = IntelligenceSynthesizer.FormatAsMarkdown(intelligence);
        
        // Step 5: Save report
        string reportPath = Path.Combine(REPORTS_DIR, 
            $"intelligence_{DateTime.Now:yyyyMMdd_HHmmss}.md");
        File.WriteAllText(reportPath, reportContent);
        
        lastReportMetadata = new ReportMetadata { ReportPath = reportPath };
    }
    finally
    {
        isGenerating = false;
    }
}
```

**Location:** `ReportSynthesizer.cs` in the `GenerateReport()` method

## File Locations & Persistence

### Warbler Context Storage
```
Assets/experiments/school/warbler_context/
├── active_analysis.json          # Current active analysis
└── history/
    ├── warbler_20250121_143022.json
    ├── warbler_20250121_150430.json
    └── ...
```

### TLDL Integration
```
TLDL/entries/
├── warbler_warbler_20250121_143022.json
└── ...
```

### School Pipeline Context
```
Assets/experiments/school/
├── inventory.json
├── hypothesis_drafts.json
├── manifests/
├── outputs/
│   └── runs/
├── claims/
│   ├── validated/
│   ├── hypotheses/
│   └── ...
├── reports/
│   ├── intelligence_20250121_143022.md
│   └── ...
└── warbler_context/          # NEW: Persists Warbler output
```

## ClaimData Reference

```csharp
[System.Serializable]
public class ClaimData
{
    public string id = "";
    public string run_id = "";
    public string experiment_name = "";
    public string description = "";
    public bool success = false;
    public float confidence_score = 0f;
    public string category = "";  // validated, regression, anomaly, improvement, etc.
    public string baseline_comparison = "";
    public DateTime validation_time = DateTime.Now;
}
```

## Usage Flow

### For a Developer Using Warbler → School → Report

1. **Open Warbler Intelligent Orchestrator**
   - Enter project request: "Create a Zork-like text adventure game"
   - Click "Orchestrate Project with AI"
   - Review analysis results

2. **Analysis is automatically saved** ✅
   - Warbler context persisted to `Assets/experiments/school/warbler_context/`
   - TLDL entry created for documentation continuity

3. **Open School Experiment Workbench**
   - Navigate to Stage 1: Hypotheses
   - See hypotheses pre-populated from Warbler analysis
   - Add team-specific hypotheses
   - Proceed through experiments

4. **Run experiments** (Stages 2-4)
   - Manifests reference Warbler strategies
   - Experiments validate the analysis
   - Claims accumulate evidence

5. **Open ReportSynthesizer** (Stage 5)
   - Click "Generate Report"
   - Intelligence Synthesizer combines:
     - Warbler's strategic analysis
     - Validated/failed claims
     - Experimental evidence
   - Output: Professional-quality intelligence report

6. **Review Intelligence Report**
   - Strategic Summary (game type, complexity, confidence)
   - Priorities (with validation status)
   - Evidence-based Recommendations (with confidence scores)
   - Risk Assessment (with mitigations)
   - Next Steps (immediate/week/month)

## Expected Output Quality

### Before Integration
```
Report: "✓ Run 1 passed, ✓ Run 2 passed, ✗ Run 3 failed"
Quality: Low-level summary of test results
Actionability: "What do I do about Run 3 failing?"
```

### After Integration
```
Report:
- Strategic Summary: Text adventure game at MEDIUM complexity, 6-week timeline
- Priority 1: Implement dialogue system (VALIDATED via Run 2)
- Priority 2: Validate map/room traversal (PARTIALLY VALIDATED, Run 3 failed)
- Recommendation: Adopt MVC architecture for dialogue separation
  - Rationale: Reduces coupling, tested successfully in Run 2
  - Confidence: 85%
- Risk: Room state management complexity
  - Mitigation: Implement state machine pattern (suggested in architecture)
- Next: Debug Run 3 failures related to room state persistence

Quality: High-level strategic intelligence with evidence
Actionability: "Here's what to do next, backed by data"
```

## Testing the Integration

### Quick Test
```powershell
# 1. Open WarblerIntelligentOrchestrator
# 2. Enter: "Create a survivor.io game"
# 3. Click "Orchestrate Project with AI"
# 4. Wait for analysis (check that file is created):
ls Assets/experiments/school/warbler_context/
# 5. Open School Workbench, go to Stage 1
# 6. Verify hypotheses are pre-populated from Warbler
# 7. Go to Stage 5: Report
# 8. Click "Generate Report"
# 9. Open the generated markdown file
# 10. Verify it contains strategic summary, priorities, recommendations
```

### Validation Checklist
- [ ] Warbler analysis saves successfully
- [ ] TLDL entry created with correct metadata
- [ ] School Stage 1 loads Warbler context
- [ ] Hypotheses include strategic hypotheses from Warbler
- [ ] ReportSynthesizer loads both context and claims
- [ ] Generated report includes all sections (summary, priorities, recommendations, risks, next steps)
- [ ] Report confidence scores are calculated from claim validation rates
- [ ] Report markdown is readable and well-formatted

## Troubleshooting

### "Warbler context not found"
- Check: `Assets/experiments/school/warbler_context/active_analysis.json` exists
- Solution: Run Warbler orchestrator again to generate new analysis

### "Hypotheses not loading from Warbler"
- Check: HypothesisExtractor is calling `WarblerContextBridge.LoadActiveAnalysis()`
- Check: Context file has `strategic_hypotheses` populated
- Solution: Verify Warbler analysis was saved with `SaveWarblerAnalysis()`

### "Report shows no recommendations"
- Check: Both Warbler context AND validated claims exist
- Check: `IntelligenceSynthesizer.Synthesize()` is being called
- Solution: Run some experiments to generate validated claims

## Next: Capsule Scroll Integration

Once the Intelligence Report is generated, create a **Capsule Scroll** to preserve:
- Analysis ID and timestamp
- Strategic decisions made
- Validation evidence
- Recommendations followed/rejected
- Outcomes

This creates continuity for the next conversation when context truncates.

---

**The Goal:** Make your project setup experience feel like talking to an experienced AI agent, not just running isolated tools.

**Quality Target:** 70% of the depth you'd get from consulting an expert agent directly.