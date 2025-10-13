#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.Text;

namespace TinyWalnutGames.TLDA.Editor
{
    /// <summary>
    /// Handles markdown generation from form data
    /// </summary>
    public static class ScribeMarkdownGenerator
    {
        public static string BuildMarkdown(ScribeFormData formData, string createdTs, string dateOverride = null, string safeTitleOverride = null)
        {
            // KeeperNote: Deterministic section builder; toggles act as feature flags so raw regen remains idempotent given same form snapshot.
            var date = string.IsNullOrEmpty(dateOverride) ? DateTime.UtcNow.ToString("yyyy-MM-dd") : dateOverride;
            var safeTitle = string.IsNullOrEmpty(safeTitleOverride) ? ScribeUtils.SanitizeTitle(formData.Title) : safeTitleOverride;

            var sb = new StringBuilder();
            sb.AppendLine("# TLDL Entry Template");
            sb.AppendLine($"**Entry ID:** TLDL-{date}-{GetCreatedNormalizedTs()}-{safeTitle}");
            sb.AppendLine($"**Author:** {(formData.Author?.Trim().Length > 0 ? formData.Author.Trim() : "@copilot")} ");
            sb.AppendLine($"**Context:** {formData.Context}");
            sb.AppendLine($"**Summary:** {formData.Summary}");
            sb.AppendLine();
            sb.AppendLine("---");
            sb.AppendLine("");
            sb.AppendLine("> 📜 \"[Insert inspirational quote from Secret Art of the Living Dev using: `python3 src/ScrollQuoteEngine/quote_engine.py --context documentation --format markdown`]\"");
            sb.AppendLine();
            sb.AppendLine("---");
            sb.AppendLine();

            if (formData.IncludeDiscoveries)
            {
                BuildDiscoveriesSection(sb, formData.Discoveries);
            }

            if (formData.IncludeActions)
            {
                BuildActionsSection(sb, formData.Actions);
            }

            if (formData.IncludeTechnicalDetails)
            {
                BuildTechnicalDetailsSection(sb, formData);
            }

            if (formData.IncludeTerminalProof && !string.IsNullOrWhiteSpace(formData.TerminalProof))
            {
                BuildTerminalProofSection(sb, formData.TerminalProof);
            }

            if (formData.IncludeDependencies)
            {
                BuildDependenciesSection(sb, formData);
            }

            if (formData.IncludeImages && formData.ImagePaths.Count > 0)
            {
                BuildImagesSection(sb, formData.ImagePaths);
            }

            if (formData.IncludeLessons)
            {
                BuildLessonsSection(sb, formData);
            }

            if (formData.IncludeNextSteps)
            {
                BuildNextStepsSection(sb, formData);
            }

            if (formData.IncludeReferences)
            {
                BuildReferencesSection(sb, formData);
            }

            if (formData.IncludeDevTimeTravel)
            {
                BuildDevTimeTravelSection(sb, formData);
            }

            sb.AppendLine("---");
            sb.AppendLine();

            if (formData.IncludeMetadata)
            {
                BuildMetadataSection(sb, formData, createdTs);
            }

            return sb.ToString();
        }

        private static void BuildDiscoveriesSection(StringBuilder sb, List<Discovery> discoveries)
        {
            sb.AppendLine("## Discoveries");
            sb.AppendLine();
            foreach (var d in discoveries)
            {
                var heading = string.IsNullOrWhiteSpace(d.Category) ? "[Discovery]" : $"[{d.Category}]";
                sb.AppendLine($"### {heading}");
                if (!string.IsNullOrWhiteSpace(d.KeyFinding)) sb.AppendLine($"- **Key Finding**: {d.KeyFinding}");
                if (!string.IsNullOrWhiteSpace(d.Impact)) sb.AppendLine($"- **Impact**: {d.Impact}");
                if (!string.IsNullOrWhiteSpace(d.Evidence)) sb.AppendLine($"- **Evidence**: {d.Evidence}");
                if (!string.IsNullOrWhiteSpace(d.RootCause)) sb.AppendLine($"- **Root Cause**: {d.RootCause}");
                if (!string.IsNullOrWhiteSpace(d.PatternRecognition)) sb.AppendLine($"- **Pattern Recognition**: {d.PatternRecognition}");
                sb.AppendLine();
            }
        }

        private static void BuildActionsSection(StringBuilder sb, List<ActionItem> actions)
        {
            sb.AppendLine("## Actions Taken");
            sb.AppendLine();
            for (int i = 0; i < actions.Count; i++)
            {
                var a = actions[i];
                var idx = i + 1;
                sb.AppendLine($"{idx}. **[{(string.IsNullOrWhiteSpace(a.Name) ? $"Action {idx}" : a.Name)}]**");
                if (!string.IsNullOrWhiteSpace(a.What)) sb.AppendLine($"   - **What**: {a.What}");
                if (!string.IsNullOrWhiteSpace(a.Why)) sb.AppendLine($"   - **Why**: {a.Why}");
                if (!string.IsNullOrWhiteSpace(a.How)) sb.AppendLine($"   - **How**: {a.How}");
                if (!string.IsNullOrWhiteSpace(a.Result)) sb.AppendLine($"   - **Result**: {a.Result}");
                if (!string.IsNullOrWhiteSpace(a.FilesChanged)) sb.AppendLine($"   - **Files Changed**: {a.FilesChanged}");
                if (!string.IsNullOrWhiteSpace(a.Validation)) sb.AppendLine($"   - **Validation**: {a.Validation}");
                sb.AppendLine();
            }
        }

        private static void BuildTechnicalDetailsSection(StringBuilder sb, ScribeFormData formData)
        {
            sb.AppendLine("## Technical Details");
            sb.AppendLine();
            if (!string.IsNullOrWhiteSpace(formData.CodeChanges))
            {
                sb.AppendLine("### Code Changes");
                sb.AppendLine("```diff");
                sb.AppendLine(formData.CodeChanges);
                sb.AppendLine("```");
                sb.AppendLine();
            }
            if (!string.IsNullOrWhiteSpace(formData.ConfigUpdates))
            {
                sb.AppendLine("### Configuration Updates");
                sb.AppendLine("```yaml");
                sb.AppendLine(formData.ConfigUpdates);
                sb.AppendLine("```");
                sb.AppendLine();
            }
        }

        private static void BuildTerminalProofSection(StringBuilder sb, string terminalProof)
        {
            sb.AppendLine("### Terminal Proof of Work");
            sb.AppendLine("```");
            sb.AppendLine(terminalProof);
            sb.AppendLine("```");
            sb.AppendLine();
        }

        private static void BuildDependenciesSection(StringBuilder sb, ScribeFormData formData)
        {
            sb.AppendLine("### Dependencies");
            if (!string.IsNullOrWhiteSpace(formData.DepsAdded)) sb.AppendLine($"- **Added**:\n{ScribeUtils.Bulletize(formData.DepsAdded)}");
            if (!string.IsNullOrWhiteSpace(formData.DepsRemoved)) sb.AppendLine($"- **Removed**:\n{ScribeUtils.Bulletize(formData.DepsRemoved)}");
            if (!string.IsNullOrWhiteSpace(formData.DepsUpdated)) sb.AppendLine($"- **Updated**:\n{ScribeUtils.Bulletize(formData.DepsUpdated)}");
            sb.AppendLine();
        }

        private static void BuildImagesSection(StringBuilder sb, List<string> imagePaths)
        {
            sb.AppendLine("## Images");
            sb.AppendLine();
            foreach (var img in imagePaths)
            {
                if (string.IsNullOrWhiteSpace(img)) continue;
                var alt = System.IO.Path.GetFileNameWithoutExtension(img);
                sb.AppendLine($"![{alt}]({img})");
            }
            sb.AppendLine();
        }

        private static void BuildLessonsSection(StringBuilder sb, ScribeFormData formData)
        {
            sb.AppendLine("## Lessons Learned");
            if (!string.IsNullOrWhiteSpace(formData.LessonsWorked)) sb.AppendLine($"\n### What Worked Well\n{ScribeUtils.Bulletize(formData.LessonsWorked)}");
            if (!string.IsNullOrWhiteSpace(formData.LessonsImprove)) sb.AppendLine($"\n### What Could Be Improved\n{ScribeUtils.Bulletize(formData.LessonsImprove)}");
            if (!string.IsNullOrWhiteSpace(formData.LessonsGaps)) sb.AppendLine($"\n### Knowledge Gaps Identified\n{ScribeUtils.Bulletize(formData.LessonsGaps)}");
            sb.AppendLine();
        }

        private static void BuildNextStepsSection(StringBuilder sb, ScribeFormData formData)
        {
            sb.AppendLine("## Next Steps");
            if (!string.IsNullOrWhiteSpace(formData.NextImmediate)) sb.AppendLine($"\n### Immediate Actions (High Priority)\n{ScribeUtils.Checklist(formData.NextImmediate)}");
            if (!string.IsNullOrWhiteSpace(formData.NextMedium)) sb.AppendLine($"\n### Medium-term Actions (Medium Priority)\n{ScribeUtils.Checklist(formData.NextMedium)}");
            if (!string.IsNullOrWhiteSpace(formData.NextLong)) sb.AppendLine($"\n### Long-term Considerations (Low Priority)\n{ScribeUtils.Checklist(formData.NextLong)}");
            sb.AppendLine();
        }

        private static void BuildReferencesSection(StringBuilder sb, ScribeFormData formData)
        {
            sb.AppendLine("## References");
            sb.AppendLine();

            if (formData.ReferencePaths.Count > 0)
            {
                sb.AppendLine("### Internal Links");
                foreach (var p in formData.ReferencePaths)
                {
                    var fileName = System.IO.Path.GetFileName(p);
                    var linkPath = p.Replace('\\', '/');
                    sb.AppendLine($"- [{fileName}]({linkPath})");
                }
                sb.AppendLine();
            }

            if (!string.IsNullOrWhiteSpace(formData.InternalLinks))
            {
                sb.AppendLine("### Internal Links");
                sb.AppendLine(formData.InternalLinks);
                sb.AppendLine();
            }

            if (!string.IsNullOrWhiteSpace(formData.ExternalResources))
            {
                sb.AppendLine("### External Resources");
                sb.AppendLine(formData.ExternalResources);
                sb.AppendLine();
            }
        }

        private static void BuildDevTimeTravelSection(StringBuilder sb, ScribeFormData formData)
        {
            sb.AppendLine("## DevTimeTravel Context");
            sb.AppendLine();
            sb.AppendLine("### Snapshot Information");
            if (!string.IsNullOrWhiteSpace(formData.SnapshotId)) sb.AppendLine($"- **Snapshot ID**: {formData.SnapshotId}");
            if (!string.IsNullOrWhiteSpace(formData.Branch)) sb.AppendLine($"- **Branch**: {formData.Branch}");
            if (!string.IsNullOrWhiteSpace(formData.CommitHash)) sb.AppendLine($"- **Commit Hash**: {formData.CommitHash}");
            if (!string.IsNullOrWhiteSpace(formData.Environment)) sb.AppendLine($"- **Environment**: {formData.Environment}");
            sb.AppendLine();
        }

        private static void BuildMetadataSection(StringBuilder sb, ScribeFormData formData, string createdTs)
        {
            sb.AppendLine("## TLDL Metadata");
            var tagsLine = ScribeUtils.FormatTags(formData.TagsCsv);
            if (!string.IsNullOrWhiteSpace(tagsLine)) sb.AppendLine($"\n**Tags**: {tagsLine}");
            sb.AppendLine($"**Complexity**: {formData.Complexity}");
            sb.AppendLine($"**Impact**: {formData.Impact}");
            if (!string.IsNullOrWhiteSpace(formData.TeamMembers)) sb.AppendLine($"**Team Members**: {formData.TeamMembers}");
            if (!string.IsNullOrWhiteSpace(formData.Duration)) sb.AppendLine($"**Duration**: {formData.Duration}");
            sb.AppendLine($"**Created**: {createdTs}");
            sb.AppendLine($"**Last Updated**: {createdTs}");
            sb.AppendLine($"**Status**: {FormatStatus(formData.Status)}");
        }

        private static string FormatStatus(Status s)
        {
            return s switch
            {
                Status.Draft => "Draft",
                Status.InProgress => "In Progress",
                Status.Complete => "Complete",
                Status.Archived => "Archived",
                _ => s.ToString(),
            };
        }

        private static string GetCreatedNormalizedTs()
        {
            return DateTime.UtcNow.ToString(format: "yyyy-MM-dd-HHmmss-utc");
        }
    }
}
#endif
