// AlchemistScaffold (v0.1.0)
// Simple console scaffold generator to mirror Python script functionality.
//
// Build:
//   dotnet new console -n AlchemistScaffold (adjust project structure as needed)
//   Place this file in tools/Alchemist and include in solution.
// Usage:
//   dotnet run -- --issue 123 --logline "..." --tension "..." --metric avg_frame_time_ms:reduce:ms:2 --output ./experiments/gu_pot/issue-123/manifest_v1.json
//
// Metric format: name:direction:unit:precision
// Directions: reduce | improve | increase | stabilize

using System;
using System.CommandLine;
using System.CommandLine.Invocation;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace Alchemist
{
    public class AlchemistScaffold
    {
        private const string AlchemistVersion = "0.1.0";

        public static int Main(string[] args)
        {
            var root = new RootCommand("Alchemist manifest scaffold")
            {
                new Option<int>("--issue") { IsRequired = true },
                new Option<string>("--issue-url", description: "Override issue URL"),
                new Option<string>("--logline") { IsRequired = true },
                new Option<string>("--tension") { IsRequired = true },
                new Option<string>("--hypothesis"),
                new Option<string[]>("--metric", description: "Repeatable metric specs", getDefaultValue: () => Array.Empty<string>()),
                new Option<int>("--seed", getDefaultValue: () => 1337),
                new Option<string>("--platform", getDefaultValue: () => "win64"),
                new Option<string>("--engine-version", getDefaultValue: () => "2025.1.0f1"),
                new Option<int>("--iterations", getDefaultValue: () => 1),
                new Option<string>("--output") { IsRequired = true }
            };

            root.SetHandler((InvocationContext ctx) =>
            {
                try
                {
                    int issue = ctx.ParseResult.GetValueForOption(root.Options.OfType<Option<int>>().First(o => o.HasAlias("--issue")));
                    string logline = ctx.ParseResult.GetValueForOption(root.Options.OfType<Option<string>>().First(o => o.HasAlias("--logline")));
                    string tension = ctx.ParseResult.GetValueForOption(root.Options.OfType<Option<string>>().First(o => o.HasAlias("--tension")));
                    string hypothesis = ctx.ParseResult.GetValueForOption(root.Options.OfType<Option<string>>().First(o => o.HasAlias("--hypothesis")));
                    string issueUrl = ctx.ParseResult.GetValueForOption(root.Options.OfType<Option<string>>().First(o => o.HasAlias("--issue-url")));
                    string[] metrics = ctx.ParseResult.GetValueForOption(root.Options.OfType<Option<string[]>>().First(o => o.HasAlias("--metric")));
                    int seed = ctx.ParseResult.GetValueForOption(root.Options.OfType<Option<int>>().First(o => o.HasAlias("--seed")));
                    string platform = ctx.ParseResult.GetValueForOption(root.Options.OfType<Option<string>>().First(o => o.HasAlias("--platform")));
                    string engineVersion = ctx.ParseResult.GetValueForOption(root.Options.OfType<Option<string>>().First(o => o.HasAlias("--engine-version")));
                    int iterations = ctx.ParseResult.GetValueForOption(root.Options.OfType<Option<int>>().First(o => o.HasAlias("--iterations")));
                    string output = ctx.ParseResult.GetValueForOption(root.Options.OfType<Option<string>>().First(o => o.HasAlias("--output")));

                    if (metrics == null || metrics.Length == 0)
                        throw new ArgumentException("At least one --metric required.");

                    var manifest = new
                    {
                        schema_version = "0.1.0",
                        kind = "experiment_manifest",
                        generated_on = DateTime.UtcNow.ToString("o"),
                        alchemist_version = AlchemistVersion,
                        origin = new {
                            type = "gu_pot",
                            issue_number = issue,
                            issue_url = issueUrl ?? $"https://github.com/OWNER/REPO/issues/{issue}"
                        },
                        logline = logline,
                        tension = tension,
                        hashes = new {
                            logline_hash = HashNormalized(logline),
                            tension_hash = HashNormalized(tension)
                        },
                        hypothesis = hypothesis ?? "Because <mechanism>, we expect <metric> to <direction> by <range>.",
                        metrics = metrics.Select(ParseMetric).ToArray(),
                        determinism = new {
                            seed = seed,
                            platform = platform,
                            engine_version = engineVersion
                        },
                        execution = new {
                            runner = "alchemist_runner_v1",
                            iterations = iterations
                        },
                        thresholds = new {
                            placeholder = "Define success/regression thresholds in validation phase."
                        },
                        notes = "Generated by AlchemistScaffold.cs"
                    };

                    Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(output))!);
                    var json = JsonSerializer.Serialize(manifest, new JsonSerializerOptions { WriteIndented = true });
                    File.WriteAllText(output, json);
                    Console.WriteLine($"[alchemist] wrote manifest -> {output}");
                }
                catch (Exception ex)
                {
                    Console.Error.WriteLine($"[alchemist][error] {ex.Message}");
                    ctx.ExitCode = 1;
                }
            });

            return root.Invoke(args);
        }

        private static object ParseMetric(string spec)
        {
            var parts = spec.Split(':');
            if (parts.Length != 4)
                throw new ArgumentException($"Metric '{spec}' must be name:direction:unit:precision");
            string name = parts[0];
            string direction = parts[1];
            string unit = parts[2];
            if (!int.TryParse(parts[3], out int precision))
                throw new ArgumentException($"Precision invalid in '{spec}'");

            if (!(direction == "reduce" || direction == "improve" || direction == "increase" || direction == "stabilize"))
                throw new ArgumentException($"Unsupported direction '{direction}'");

            return new {
                name,
                direction,
                unit,
                precision
            };
        }

        private static string HashNormalized(string input)
        {
            var normalized = Regex.Replace(input.Trim().ToLowerInvariant(), "\\s+", " ");
            using var sha = SHA256.Create();
            var bytes = sha.ComputeHash(Encoding.UTF8.GetBytes(normalized));
            var sb = new StringBuilder("sha256:");
            foreach (var b in bytes) sb.Append(b.ToString("x2"));
            return sb.ToString();
        }
    }
}