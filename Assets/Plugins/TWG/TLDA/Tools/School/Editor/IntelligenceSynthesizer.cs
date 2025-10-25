using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using UnityEngine;
using Newtonsoft.Json;

namespace TWG.TLDA.School.Editor
{
    /// <summary>
    /// Synthesizes strategic actionable intelligence from:
    /// - Warbler's strategic analysis
    /// - School's experimental validation
    /// - Claims' detailed evidence
    /// 
    /// Output: 70% of the strategic thinking an AI agent would produce
    /// </summary>
    public class IntelligenceSynthesizer
    {
        [System.Serializable]
        public class ActionableIntelligence
        {
            public string generated_at = "";
            public string analysis_id = "";
            
            public StrategicSummary summary = new();
            public List<PriorityItem> priorities = new();
            public List<Recommendation> recommendations = new();
            public List<RiskAssessment> risks = new();
            public NextSteps next_steps = new();
        }

        [System.Serializable]
        public class StrategicSummary
        {
            public string game_type = "";
            public string complexity_assessment = "";
            public string architecture_fit = "";
            public string overall_confidence = "";
            public string timeline_assessment = "";
        }

        [System.Serializable]
        public class PriorityItem
        {
            public int priority = 0;
            public string item = "";
            public string rationale = "";
            public string validation_status = "";
        }

        [System.Serializable]
        public class Recommendation
        {
            public string category = "";
            public string recommendation = "";
            public string rationale = "";
            public string evidence = "";
            public float confidence = 0f;
        }

        [System.Serializable]
        public class RiskAssessment
        {
            public string risk = "";
            public string severity = "";
            public string mitigation = "";
            public string validation_needed = "";
        }

        [System.Serializable]
        public class NextSteps
        {
            public List<string> immediate = new();
            public List<string> this_week = new();
            public List<string> this_month = new();
        }

        /// <summary>
        /// Synthesize actionable intelligence from all available data
        /// </summary>
        public static ActionableIntelligence Synthesize(
            WarblerContextBridge.WarblerContext warblerContext,
            List<ClaimData> validatedClaims)
        {
            var intelligence = new ActionableIntelligence
            {
                generated_at = DateTime.Now.ToString("o"),
                analysis_id = warblerContext?.analysis_id ?? "unknown",
            };

            // Build strategic summary
            intelligence.summary = BuildStrategicSummary(warblerContext, validatedClaims);

            // Identify priorities
            intelligence.priorities = IdentifyPriorities(warblerContext, validatedClaims);

            // Generate recommendations
            intelligence.recommendations = GenerateRecommendations(warblerContext, validatedClaims);

            // Assess risks
            intelligence.risks = AssessRisks(warblerContext, validatedClaims);

            // Build next steps
            intelligence.next_steps = BuildNextSteps(warblerContext, validatedClaims);

            return intelligence;
        }

        private static StrategicSummary BuildStrategicSummary(
            WarblerContextBridge.WarblerContext warblerContext,
            List<ClaimData> validatedClaims)
        {
            var summary = new StrategicSummary();

            if (warblerContext != null)
            {
                summary.game_type = warblerContext.game_type;
                summary.complexity_assessment = $"{warblerContext.complexity_level} complexity, estimated {warblerContext.estimated_dev_time} dev time";
                summary.architecture_fit = $"Suggested architecture: {warblerContext.suggested_architecture}";
                
                // Calculate confidence based on claims
                var confirmedClaims = validatedClaims?.Where(c => c.Success).Count() ?? 0;
                var totalClaims = validatedClaims?.Count ?? 1;
                float claimsConfidence = (float)confirmedClaims / totalClaims;
                
                summary.overall_confidence = GenerateConfidenceStatement(claimsConfidence);
                summary.timeline_assessment = $"Original estimate: {warblerContext.estimated_dev_time}, validation data: {(validatedClaims?.Count ?? 0)} experiments";
            }

            return summary;
        }

        private static List<PriorityItem> IdentifyPriorities(
            WarblerContextBridge.WarblerContext warblerContext,
            List<ClaimData> validatedClaims)
        {
            var priorities = new List<PriorityItem>();

            if (warblerContext == null) return priorities;

            int priority = 1;

            // Priority 1: Core systems
            foreach (var system in warblerContext.required_systems.Take(3))
            {
                var validations = validatedClaims?.Where(c => c.ExperimentName?.Contains(system) == true).ToList() ?? new();
                priorities.Add(new PriorityItem
                {
                    priority = priority++,
                    item = $"Implement {system} system",
                    rationale = "Core system identified as essential by architecture analysis",
                    validation_status = validations.Any() ? "Partially validated" : "Not yet validated"
                });
            }

            // Priority 2: Key mechanics
            foreach (var mechanic in warblerContext.key_mechanics.Take(2))
            {
                priorities.Add(new PriorityItem
                {
                    priority = priority++,
                    item = $"Validate {mechanic} mechanic",
                    rationale = "Key mechanic for game feel - must validate early",
                    validation_status = "Pending validation"
                });
            }

            // Priority 3: Architecture
            priorities.Add(new PriorityItem
            {
                priority = priority++,
                item = $"Confirm {warblerContext.suggested_architecture} architecture viability",
                rationale = "Strategic decision point - affects entire project scope",
                validation_status = "Critical validation needed"
            });

            return priorities;
        }

        private static List<Recommendation> GenerateRecommendations(
            WarblerContextBridge.WarblerContext warblerContext,
            List<ClaimData> validatedClaims)
        {
            var recommendations = new List<Recommendation>();

            if (warblerContext == null) return recommendations;

            // Recommendation 1: Architecture
            recommendations.Add(new Recommendation
            {
                category = "Architecture",
                recommendation = $"Adopt {warblerContext.suggested_architecture} pattern",
                rationale = "Provides optimal balance between complexity and deliverability",
                evidence = $"Suggested by AI analysis based on {warblerContext.game_type} patterns",
                confidence = 0.85f
            });

            // Recommendation 2: Development approach
            var devMilestones = string.Join(" → ", warblerContext.development_milestones.Take(3));
            recommendations.Add(new Recommendation
            {
                category = "Development",
                recommendation = $"Follow milestone progression: {devMilestones}",
                rationale = "Staged approach reduces risk and enables early validation",
                evidence = "Strategic milestone plan from Warbler analysis",
                confidence = 0.80f
            });

            // Recommendation 3: Testing focus
            if (warblerContext.testing_strategy.Length > 0)
            {
                var testStrategy = string.Join(", ", warblerContext.testing_strategy.Take(2));
                recommendations.Add(new Recommendation
                {
                    category = "Testing",
                    recommendation = $"Prioritize testing: {testStrategy}",
                    rationale = "These areas have highest impact on project success",
                    evidence = "Testing strategy from AI analysis",
                    confidence = 0.75f
                });
            }

            // Recommendation 4: Risk mitigation (based on technical considerations)
            if (warblerContext.technical_considerations.Length > 0)
            {
                var topRisk = warblerContext.technical_considerations.First();
                recommendations.Add(new Recommendation
                {
                    category = "Risk",
                    recommendation = $"Mitigate: {topRisk}",
                    rationale = "Identified as critical technical consideration",
                    evidence = "From technical analysis phase",
                    confidence = 0.70f
                });
            }

            return recommendations;
        }

        private static List<RiskAssessment> AssessRisks(
            WarblerContextBridge.WarblerContext warblerContext,
            List<ClaimData> validatedClaims)
        {
            var risks = new List<RiskAssessment>();

            if (warblerContext == null) return risks;

            // Risk 1: Timeline slippage
            risks.Add(new RiskAssessment
            {
                risk = "Timeline slippage on complex systems",
                severity = warblerContext.complexity_level.Contains("high") ? "HIGH" : "MEDIUM",
                mitigation = "Front-load complex system prototyping in milestones 1-2",
                validation_needed = "Weekly velocity tracking and risk burndown"
            });

            // Risk 2: Architecture mismatch
            risks.Add(new RiskAssessment
            {
                risk = $"Suggested {warblerContext.suggested_architecture} architecture doesn't work in practice",
                severity = "MEDIUM",
                mitigation = "Run proof-of-concept for architecture before full implementation",
                validation_needed = "POC validation against required systems"
            });

            // Risk 3: Scope creep
            risks.Add(new RiskAssessment
            {
                risk = "Feature scope expands beyond original game type definition",
                severity = "HIGH",
                mitigation = $"Strict adherence to {warblerContext.game_type} feature set",
                validation_needed = "Feature validation against original type definition"
            });

            // Risk 4: Validation failures (from claims data)
            var failedClaims = validatedClaims?.Where(c => !c.Success).Count() ?? 0;
            if (failedClaims > 0)
            {
                risks.Add(new RiskAssessment
                {
                    risk = $"{failedClaims} validation failures indicate unresolved issues",
                    severity = failedClaims > 5 ? "HIGH" : "MEDIUM",
                    mitigation = "Prioritize investigation and resolution of failed claims",
                    validation_needed = "Root cause analysis and retry validation"
                });
            }

            return risks;
        }

        private static NextSteps BuildNextSteps(
            WarblerContextBridge.WarblerContext warblerContext,
            List<ClaimData> validatedClaims)
        {
            var nextSteps = new NextSteps();

            if (warblerContext == null) return nextSteps;

            // Immediate (next 1-2 days)
            nextSteps.immediate.Add("Review and confirm Warbler analysis with team");
            nextSteps.immediate.Add($"Validate {warblerContext.suggested_architecture} pattern against project constraints");
            if (warblerContext.development_milestones.Length > 0)
            {
                nextSteps.immediate.Add($"Plan Milestone 1: {warblerContext.development_milestones.First()}");
            }

            // This week
            nextSteps.this_week.Add($"Prototype core {warblerContext.game_type} systems");
            nextSteps.this_week.Add("Run initial validation experiments");
            nextSteps.this_week.Add($"Architecture proof-of-concept for {warblerContext.suggested_architecture}");
            if (warblerContext.key_mechanics.Length > 0)
            {
                nextSteps.this_week.Add($"Playtest {warblerContext.key_mechanics.First()} mechanic");
            }

            // This month
            nextSteps.this_month.Add($"Complete Milestone 1 of {warblerContext.estimated_dev_time} timeline");
            nextSteps.this_month.Add("Integrate all required systems (alpha)");
            nextSteps.this_month.Add("Run comprehensive validation suite");
            nextSteps.this_month.Add("Generate Capsule Scroll with validated learnings");

            return nextSteps;
        }

        private static string GenerateConfidenceStatement(float confidence)
        {
            return confidence switch
            {
                >= 0.9f => "VERY HIGH - Predictions well-validated",
                >= 0.75f => "HIGH - Most predictions confirmed",
                >= 0.60f => "MODERATE - Mixed validation results",
                >= 0.40f => "LOW - Significant unresolved items",
                _ => "VERY LOW - Extensive re-planning needed"
            };
        }

        /// <summary>
        /// Format intelligence report as human-readable markdown
        /// </summary>
        public static string FormatAsMarkdown(ActionableIntelligence intelligence)
        {
            var sb = new StringBuilder();

            sb.AppendLine("# 🧠 Actionable Intelligence Report");
            sb.AppendLine();
            sb.AppendLine($"**Generated:** {intelligence.generated_at}");
            sb.AppendLine($"**Analysis ID:** {intelligence.analysis_id}");
            sb.AppendLine();

            // Strategic Summary
            sb.AppendLine("## 📋 Strategic Summary");
            sb.AppendLine();
            sb.AppendLine($"- **Game Type:** {intelligence.summary.game_type}");
            sb.AppendLine($"- **Complexity:** {intelligence.summary.complexity_assessment}");
            sb.AppendLine($"- **Architecture:** {intelligence.summary.architecture_fit}");
            sb.AppendLine($"- **Confidence:** {intelligence.summary.overall_confidence}");
            sb.AppendLine($"- **Timeline:** {intelligence.summary.timeline_assessment}");
            sb.AppendLine();

            // Priorities
            sb.AppendLine("## 🎯 Priorities");
            sb.AppendLine();
            foreach (var priority in intelligence.priorities)
            {
                sb.AppendLine($"### Priority {priority.priority}: {priority.item}");
                sb.AppendLine($"**Rationale:** {priority.rationale}");
                sb.AppendLine($"**Status:** {priority.validation_status}");
                sb.AppendLine();
            }

            // Recommendations
            sb.AppendLine("## 💡 Recommendations");
            sb.AppendLine();
            foreach (var rec in intelligence.recommendations)
            {
                sb.AppendLine($"### {rec.category}: {rec.recommendation}");
                sb.AppendLine($"**Rationale:** {rec.rationale}");
                sb.AppendLine($"**Evidence:** {rec.evidence}");
                sb.AppendLine($"**Confidence:** {(rec.confidence * 100):F0}%");
                sb.AppendLine();
            }

            // Risks
            sb.AppendLine("## ⚠️ Risk Assessment");
            sb.AppendLine();
            foreach (var risk in intelligence.risks)
            {
                sb.AppendLine($"### {risk.risk}");
                sb.AppendLine($"**Severity:** {risk.severity}");
                sb.AppendLine($"**Mitigation:** {risk.mitigation}");
                sb.AppendLine($"**Validation:** {risk.validation_needed}");
                sb.AppendLine();
            }

            // Next Steps
            sb.AppendLine("## 📅 Next Steps");
            sb.AppendLine();
            
            if (intelligence.next_steps.immediate.Count > 0)
            {
                sb.AppendLine("### Immediate (Next 1-2 days)");
                foreach (var step in intelligence.next_steps.immediate)
                {
                    sb.AppendLine($"- [ ] {step}");
                }
                sb.AppendLine();
            }

            if (intelligence.next_steps.this_week.Count > 0)
            {
                sb.AppendLine("### This Week");
                foreach (var step in intelligence.next_steps.this_week)
                {
                    sb.AppendLine($"- [ ] {step}");
                }
                sb.AppendLine();
            }

            if (intelligence.next_steps.this_month.Count > 0)
            {
                sb.AppendLine("### This Month");
                foreach (var step in intelligence.next_steps.this_month)
                {
                    sb.AppendLine($"- [ ] {step}");
                }
                sb.AppendLine();
            }

            return sb.ToString();
        }
    }
}