using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;

namespace TWG.TLDA.NPCControl
{
    /// <summary>
    /// ??? PROTECTED CORE - Complete Warbler API for NPC decision making and dialogue generation
    /// Provides full HTTP communication with Warbler cognitive engine
    /// </summary>
    public static class WarblerAPI
    {
        private static string _baseUrl = "http://localhost:8080/warbler";
        private static readonly Dictionary<string, object> RequestCache = new Dictionary<string, object>();
        private static float _cacheTimeout = 30f; // 30 seconds
        private static readonly Dictionary<string, float> CacheTimestamps = new Dictionary<string, float>();

        /// <summary>
        /// Send decision request to Warbler cognitive engine
        /// </summary>
        public static async Task<string> SendDecisionRequest(WarblerDecisionRequest request)
        {
            try
            {
                // Create cache key for similar requests
                var cacheKey = $"decision_{request.context}_{string.Join(",", request.options)}";

                // Check cache first
                if (IsValidCache(cacheKey))
                {
                    return (string)RequestCache[cacheKey];
                }

                var jsonData = JsonUtility.ToJson(request);

                using (var webRequest = UnityWebRequest.PostWwwForm($"{_baseUrl}/decision", ""))
                {
                    webRequest.uploadHandler = new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(jsonData));
                    webRequest.downloadHandler = new DownloadHandlerBuffer();
                    webRequest.SetRequestHeader("Content-Type", "application/json");

                    var operation = webRequest.SendWebRequest();

                    // Wait for completion
                    while (!operation.isDone)
                    {
                        await Task.Yield();
                    }

                    if (webRequest.result == UnityWebRequest.Result.Success)
                    {
                        var response = JsonUtility.FromJson<WarblerDecisionResponse>(webRequest.downloadHandler.text);

                        // Cache the result
                        RequestCache[cacheKey] = response.selectedOption;
                        CacheTimestamps[cacheKey] = Time.time;

                        return response.selectedOption;
                    }
                    else
                    {
                        Debug.LogWarning($"Warbler decision request failed: {webRequest.error}");
                        return GetFallbackDecision(request.options);
                    }
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"Warbler API exception: {e.Message}");
                return GetFallbackDecision(request.options);
            }
        }

        /// <summary>
        /// Generate dialogue using Warbler intelligence
        /// </summary>
        public static async Task<string> GenerateDialogue(WarblerDialogueRequest request)
        {
            try
            {
                // Create cache key for dialogue requests
                var cacheKey = $"dialogue_{request.trigger}_{request.npcPersonality?.GetHashCode()}";

                // Check cache first
                if (IsValidCache(cacheKey))
                {
                    return (string)RequestCache[cacheKey];
                }

                var jsonData = JsonUtility.ToJson(request);

                using (var webRequest = UnityWebRequest.PostWwwForm($"{_baseUrl}/dialogue", ""))
                {
                    webRequest.uploadHandler = new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(jsonData));
                    webRequest.downloadHandler = new DownloadHandlerBuffer();
                    webRequest.SetRequestHeader("Content-Type", "application/json");

                    var operation = webRequest.SendWebRequest();

                    // Wait for completion
                    while (!operation.isDone)
                    {
                        await Task.Yield();
                    }

                    if (webRequest.result == UnityWebRequest.Result.Success)
                    {
                        var response = JsonUtility.FromJson<WarblerDialogueResponse>(webRequest.downloadHandler.text);

                        // Cache the result
                        RequestCache[cacheKey] = response.generatedDialogue;
                        CacheTimestamps[cacheKey] = Time.time;

                        return response.generatedDialogue;
                    }
                    else
                    {
                        Debug.LogWarning($"Warbler dialogue request failed: {webRequest.error}");
                        return GetFallbackDialogue(request.trigger);
                    }
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"Warbler dialogue API exception: {e.Message}");
                return GetFallbackDialogue(request.trigger);
            }
        }

        /// <summary>
        /// Configure Warbler API endpoint
        /// </summary>
        public static void SetEndpoint(string url)
        {
            _baseUrl = url;
            Debug.Log($"Warbler API endpoint set to: {_baseUrl}");
        }

        /// <summary>
        /// Clear request cache
        /// </summary>
        public static void ClearCache()
        {
            RequestCache.Clear();
            CacheTimestamps.Clear();
            Debug.Log("Warbler API cache cleared");
        }

        /// <summary>
        /// Check if warbler service is available
        /// </summary>
        public static async Task<bool> IsServiceAvailable()
        {
            try
            {
                using (var webRequest = UnityWebRequest.Get($"{_baseUrl}/health"))
                {
                    var operation = webRequest.SendWebRequest();

                    // Wait for completion with timeout
                    var timeout = 5f;
                    var elapsed = 0f;

                    while (!operation.isDone && elapsed < timeout)
                    {
                        elapsed += Time.deltaTime;
                        await Task.Yield();
                    }

                    return webRequest.result == UnityWebRequest.Result.Success;
                }
            }
            catch
            {
                return false;
            }
        }

        private static bool IsValidCache(string key)
        {
            if (!RequestCache.ContainsKey(key) || !CacheTimestamps.ContainsKey(key))
                return false;

            return (Time.time - CacheTimestamps[key]) < _cacheTimeout;
        }

        private static string GetFallbackDecision(string[] options)
        {
            if (options == null || options.Length == 0)
                return "continue";

            return options[UnityEngine.Random.Range(0, options.Length)];
        }

        private static string GetFallbackDialogue(string trigger)
        {
            var fallbackResponses = new Dictionary<string, string[]>
            {
                ["greeting"] = new[] { "Hello there!", "Greetings, traveler.", "Good to see you." },
                ["goodbye"] = new[] { "Farewell!", "Until we meet again.", "Safe travels." },
                ["question"] = new[] { "That's an interesting question.", "Let me think about that.", "I'm not sure about that." },
                ["combat"] = new[] { "Ready for battle!", "Let's do this!", "I won't back down!" },
                ["default"] = new[] { "...", "Indeed.", "Hmm." }
            };

            var key = fallbackResponses.ContainsKey(trigger.ToLower()) ? trigger.ToLower() : "default";
            var responses = fallbackResponses[key];
            return responses[UnityEngine.Random.Range(0, responses.Length)];
        }
    }

    [Serializable]
    public class WarblerDecisionResponse
    {
        public string selectedOption = "";
        public float confidence;
        public string reasoning = "";
    }

    [Serializable]
    public class WarblerDialogueResponse
    {
        public string generatedDialogue = "";
        public string emotionalTone = "";
        public string[] suggestedActions = new string[0];
    }

    [Serializable]
    public class WarblerDialogueRequest
    {
        public string trigger = "";
        public string npcPersonality = "";
        public List<string> conversationHistory = new List<string>();
        public Dictionary<string, object> WorldContext = new Dictionary<string, object>();
    }
}
