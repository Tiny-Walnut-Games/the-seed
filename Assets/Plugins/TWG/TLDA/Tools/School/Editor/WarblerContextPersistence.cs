using System;
using System.IO;
using UnityEngine;
using Newtonsoft.Json;

namespace TWG.TLDA.School.Editor
{
    /// <summary>
    /// Persists Warbler's ProjectAnalysis for use by School pipeline
    /// ?Intended use!? - Expand context data model as needed for your project
    /// </summary>
    public static class WarblerContextPersistence
    {
        private const string CONTEXT_DIR = "Assets/experiments/school/warbler_context/";
        private const string CONTEXT_FILE = "Assets/experiments/school/warbler_context/active_analysis.json";

        /// <summary>
        /// Save Warbler analysis to persistent storage
        /// </summary>
        public static bool SaveAnalysis<T>(T analysis, string gameName) where T : class
        {
            try
            {
                Directory.CreateDirectory(CONTEXT_DIR);

                var wrapper = new WarblerContextSnapshot
                {
                    analysis_type = typeof(T).Name,
                    game_name = gameName,
                    timestamp = DateTime.Now.ToString("o"),
                    raw_analysis = JsonConvert.SerializeObject(analysis, Formatting.Indented)
                };

                string json = JsonConvert.SerializeObject(wrapper, Formatting.Indented);
                File.WriteAllText(CONTEXT_FILE, json);

                Debug.Log($"✅ Warbler context saved: {CONTEXT_FILE}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"❌ Failed to save Warbler context: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Load saved Warbler analysis for School pipeline
        /// </summary>
        public static WarblerContextSnapshot LoadAnalysis()
        {
            if (!File.Exists(CONTEXT_FILE))
            {
                return null;
            }

            try
            {
                string json = File.ReadAllText(CONTEXT_FILE);
                var context = JsonConvert.DeserializeObject<WarblerContextSnapshot>(json);
                return context;
            }
            catch (Exception ex)
            {
                Debug.LogError($"❌ Failed to load Warbler context: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get parsed analysis as dynamic object (allows type-agnostic access)
        /// </summary>
        public static dynamic GetAnalysisDynamic()
        {
            var snapshot = LoadAnalysis();
            if (snapshot == null) return null;

            return JsonConvert.DeserializeObject<dynamic>(snapshot.raw_analysis);
        }
    }

    [System.Serializable]
    public class WarblerContextSnapshot
    {
        public string analysis_type;           // e.g., "ProjectAnalysis"
        public string game_name;               // Game type from Warbler
        public string timestamp;               // ISO 8601 timestamp
        public string raw_analysis;            // Full JSON of ProjectAnalysis
    }
}
