using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEditor;

namespace TWG.TLDA.School.Editor
{
    /// <summary>
    /// Converts Unity-generated experiment manifests to Python harness format
    /// </summary>
    public class ManifestConverter
    {
        public static string ConvertToHarnessFormat(string unityManifestPath)
        {
            var content = File.ReadAllText(unityManifestPath);
            var unityManifest = ParseUnityManifest(content);
            var harnessManifest = ConvertToHarnessManifest(unityManifest);
            return SerializeHarnessManifest(harnessManifest);
        }
        
        private static UnityManifest ParseUnityManifest(string yamlContent)
        {
            var manifest = new UnityManifest();
            var lines = yamlContent.Split('\n');
            
            foreach (var line in lines)
            {
                var trimmed = line.Trim();
                if (trimmed.StartsWith("name:"))
                {
                    manifest.Name = GetYamlValue(trimmed);
                }
                else if (trimmed.StartsWith("description:"))
                {
                    manifest.Description = GetYamlValue(trimmed);
                }
                else if (trimmed.StartsWith("hypothesis_id:"))
                {
                    manifest.HypothesisId = GetYamlValue(trimmed);
                }
                else if (trimmed.StartsWith("hypothesis_type:"))
                {
                    manifest.HypothesisType = GetYamlValue(trimmed);
                }
                else if (trimmed.StartsWith("faculty_surface:"))
                {
                    manifest.FacultySurface = GetYamlValue(trimmed);
                }
                else if (trimmed.StartsWith("batch_size:"))
                {
                    if (int.TryParse(GetYamlValue(trimmed), out int batchSize))
                        manifest.BatchSize = batchSize;
                }
                else if (trimmed.StartsWith("size:") && manifest.CorpusSize == 0)
                {
                    if (int.TryParse(GetYamlValue(trimmed), out int size))
                        manifest.CorpusSize = size;
                }
                else if (trimmed.StartsWith("seed:"))
                {
                    if (int.TryParse(GetYamlValue(trimmed), out int seed))
                        manifest.Seed = seed;
                }
                else if (trimmed.StartsWith("threshold:"))
                {
                    if (float.TryParse(GetYamlValue(trimmed), out float threshold))
                        manifest.ValidationThreshold = threshold;
                }
            }
            
            return manifest;
        }
        
        private static string GetYamlValue(string line)
        {
            var colonIndex = line.IndexOf(':');
            if (colonIndex == -1) return "";
            
            var value = line[ (colonIndex + 1).. ].Trim();
            // Remove quotes if present
            if (value.StartsWith("\"") && value.EndsWith("\""))
                value = value[ 1..^1 ];
            if (value.StartsWith("'") && value.EndsWith("'"))
                value = value[ 1..^1 ];
                
            return value;
        }
        
        private static HarnessManifest ConvertToHarnessManifest(UnityManifest unity)
        {
            return new HarnessManifest
            {
                Metadata = new Dictionary<string, object>
                {
                    ["name"] = unity.Name,
                    ["description"] = unity.Description,
                    ["version"] = "1.0.0",
                    ["author"] = "School Experiment Framework",
                    ["created"] = DateTime.UtcNow.ToString("O"),
                    ["tags"] = new string[] { "school", "hypothesis", unity.HypothesisType.ToLower() }
                },
                
                Model = new Dictionary<string, object>
                {
                    ["type"] = "behavioral_governance",
                    ["instance_config"] = new Dictionary<string, object>
                    {
                        ["enable_intervention_tracking"] = true
                    },
                    ["performance_profile"] = "experiment"
                },
                
                Conditions = new Dictionary<string, object>
                {
                    ["hypothesis_types"] = new string[] { unity.HypothesisType }
                },
                
                Corpus = new Dictionary<string, object>
                {
                    ["type"] = "synthetic",
                    ["size"] = Math.Min(unity.CorpusSize > 0 ? unity.CorpusSize : 50, 50), // Limit for testing
                    ["shuffle"] = true,
                    ["seed"] = unity.Seed > 0 ? unity.Seed : 42
                },
                
                Processing = new Dictionary<string, object>
                {
                    ["batch_size"] = Math.Min(unity.BatchSize > 0 ? unity.BatchSize : 5, 10), // Limit for testing
                    ["mode"] = "sequential",
                    ["max_workers"] = 1,
                    ["timeout_seconds"] = 60 // Shorter timeout for testing
                },
                
                Metrics = new Dictionary<string, object>
                {
                    ["behavioral_metrics"] = new string[] 
                    { 
                        "processing_time_ms"
                    },
                    ["performance_metrics"] = new string[]
                    {
                        "throughput_items_per_sec",
                        "success_rate_pct"
                    }
                },
                
                Output = new Dictionary<string, object>
                {
                    ["base_path"] = "assets/experiments/school/outputs",
                    ["formats"] = new string[] { "json" },
                    ["artifacts"] = new Dictionary<string, object>
                    {
                        ["save_raw_results"] = true,
                        ["save_processed_metrics"] = true
                    }
                },
                
                Execution = new Dictionary<string, object>
                {
                    ["random_seeds"] = new Dictionary<string, object>
                    {
                        ["global_seed"] = unity.Seed > 0 ? unity.Seed : 42,
                        ["corpus_seed"] = (unity.Seed > 0 ? unity.Seed : 42) + 100
                    },
                    ["retry_policy"] = new Dictionary<string, object>
                    {
                        ["max_retries"] = 1
                    },
                    ["resource_limits"] = new Dictionary<string, object>
                    {
                        ["max_memory_mb"] = 256,
                        ["max_duration_minutes"] = 2 // Shorter duration for testing
                    }
                },
                
                Validation = new Dictionary<string, object>
                {
                    ["success_criteria"] = new Dictionary<string, object>
                    {
                        ["min_processed_items"] = Math.Max(5, Math.Min(unity.CorpusSize > 0 ? unity.CorpusSize : 50, 50) * 0.7), // 70% of corpus, max 35
                        ["max_error_rate"] = 0.2 // More lenient for testing
                    }
                },
                
                Integration = new Dictionary<string, object>
                {
                    ["chronicle_integration"] = new Dictionary<string, object>
                    {
                        ["enabled"] = true,
                        ["auto_generate_tldl"] = false
                    },
                    ["pet_events"] = new Dictionary<string, object>
                    {
                        ["enabled"] = false
                    },
                    ["telemetry"] = new Dictionary<string, object>
                    {
                        ["enabled"] = true,
                        ["track_developer_state"] = false,
                        ["include_system_metrics"] = true
                    }
                }
            };
        }
        
        private static string SerializeHarnessManifest(HarnessManifest manifest)
        {
            var yaml = new System.Text.StringBuilder();
            
            // Metadata section
            yaml.AppendLine("metadata:");
            SerializeDictionary(yaml, manifest.Metadata, 1);
            yaml.AppendLine();
            
            // Model section
            yaml.AppendLine("model:");
            SerializeDictionary(yaml, manifest.Model, 1);
            yaml.AppendLine();
            
            // Conditions section
            yaml.AppendLine("conditions:");
            SerializeDictionary(yaml, manifest.Conditions, 1);
            yaml.AppendLine();
            
            // Corpus section
            yaml.AppendLine("corpus:");
            SerializeDictionary(yaml, manifest.Corpus, 1);
            yaml.AppendLine();
            
            // Processing section
            yaml.AppendLine("processing:");
            SerializeDictionary(yaml, manifest.Processing, 1);
            yaml.AppendLine();
            
            // Metrics section
            yaml.AppendLine("metrics:");
            SerializeDictionary(yaml, manifest.Metrics, 1);
            yaml.AppendLine();
            
            // Output section
            yaml.AppendLine("output:");
            SerializeDictionary(yaml, manifest.Output, 1);
            yaml.AppendLine();
            
            // Execution section
            yaml.AppendLine("execution:");
            SerializeDictionary(yaml, manifest.Execution, 1);
            yaml.AppendLine();
            
            // Validation section
            yaml.AppendLine("validation:");
            SerializeDictionary(yaml, manifest.Validation, 1);
            yaml.AppendLine();
            
            // Integration section
            yaml.AppendLine("integration:");
            SerializeDictionary(yaml, manifest.Integration, 1);
            
            return yaml.ToString();
        }
        
        private static void SerializeDictionary(System.Text.StringBuilder yaml, Dictionary<string, object> dict, int indent)
        {
            var indentStr = new string(' ', indent * 2);
            
            foreach (var kvp in dict)
            {
                if (kvp.Value is Dictionary<string, object> nestedDict)
                {
                    yaml.AppendLine($"{indentStr}{kvp.Key}:");
                    SerializeDictionary(yaml, nestedDict, indent + 1);
                }
                else if (kvp.Value is string[] array)
                {
                    yaml.AppendLine($"{indentStr}{kvp.Key}:");
                    foreach (var item in array)
                    {
                        yaml.AppendLine($"{indentStr}  - \"{item}\"");
                    }
                }
                else if (kvp.Value is string str)
                {
                    yaml.AppendLine($"{indentStr}{kvp.Key}: \"{str}\"");
                }
                else
                {
                    yaml.AppendLine($"{indentStr}{kvp.Key}: {kvp.Value}");
                }
            }
        }
    }
    
    public class UnityManifest
    {
        public string Name = "";
        public string Description = "";
        public string HypothesisId = "";
        public string HypothesisType = "";
        public string FacultySurface = "";
        public int BatchSize = 0;
        public int CorpusSize = 0;
        public int Seed = 0;
        public float ValidationThreshold = 0;
    }
    
    public class HarnessManifest
    {
        public Dictionary<string, object> Metadata;
        public Dictionary<string, object> Model;
        public Dictionary<string, object> Conditions;
        public Dictionary<string, object> Corpus;
        public Dictionary<string, object> Processing;
        public Dictionary<string, object> Metrics;
        public Dictionary<string, object> Output;
        public Dictionary<string, object> Execution;
        public Dictionary<string, object> Validation;
        public Dictionary<string, object> Integration;
    }
}