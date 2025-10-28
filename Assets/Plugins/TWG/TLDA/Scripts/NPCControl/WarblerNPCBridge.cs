using System;
using UnityEngine;
using System.Collections.Generic;
using TWG.TLDA; // For GameManager and QuestManager

namespace TWG.TLDA.NPCControl
{
    /// <summary>
    /// ?? INTENDED EXPANSION - Bridge between TLDA/Warbler decision engine and Unity NPC controllers
    /// ?Intended use!? NPC AI Decision Making - Expand as needed for your project
    ///
    /// Customer-facing extension point for:
    /// - Custom dialogue systems integration
    /// - Game-specific decision contexts
    /// - Project-specific personality traits
    /// - Custom world state providers
    /// </summary>
    public class WarblerNpcBridge : MonoBehaviour
    {
        [Header("Warbler Connection")]
        // [SerializeField] private string warblerEndpoint = "http://localhost:8080/warbler";  // Reserved for 👀future expansion
        // [SerializeField] private bool useLocalWarbler = true;  // Reserved for 👀future expansion

        [Header("NPC Configuration")]
        [SerializeField] private NpcPersonality personality = new NpcPersonality();
        [SerializeField] private WarblerDialogueSystem dialogueSystem = new WarblerDialogueSystem();

        private Dictionary<string, object> _npcContext = new Dictionary<string, object>();
        private List<string> _conversationHistory = new List<string>();

        public async void MakeDecision(string decisionContext, string[] options, Action<string> onDecisionMade)
        {
            try
            {
                var request = new WarblerDecisionRequest
                {
                    context = $"{personality.name}: {decisionContext}",
                    options = options,
                    npcPersonality = personality.ToJson(),
                    WorldState = GetWorldState()
                };

                // Send to Warbler for cognitive decision
                var decision = await WarblerAPI.SendDecisionRequest(request);

                Debug.Log($"🧠 Warbler decided for {personality.name}: {decision}");
                onDecisionMade?.Invoke(decision);
            }
            catch (Exception e)
            {
                Debug.LogError($"Warbler decision failed: {e.Message}");
                // Fallback to simple AI
                onDecisionMade?.Invoke(options[UnityEngine.Random.Range(0, options.Length)]);
            }
        }

        public async void GenerateDialogue(string trigger, Action<string> onDialogueGenerated)
        {
            try
            {
                var dialogueRequest = new WarblerDialogueRequest
                {
                    trigger = trigger,
                    npcPersonality = personality.ToJson(),
                    conversationHistory = GetRecentHistory(),
                    WorldContext = GetWorldState()
                };

                var dialogue = await WarblerAPI.GenerateDialogue(dialogueRequest);

                // Store in both local history and dialogue system
                _conversationHistory.Add($"Trigger: {trigger}");
                _conversationHistory.Add($"Response: {dialogue}");

                dialogueSystem.AddDialogue(personality.name, dialogue, WarblerDialogueSystem.DialogueType.NpcResponse);

                // Keep history manageable
                if (_conversationHistory.Count > 20)
                {
                    _conversationHistory.RemoveRange(0, 4);
                }

                onDialogueGenerated?.Invoke(dialogue);
            }
            catch (Exception e)
            {
                Debug.LogError($"Warbler dialogue generation failed: {e.Message}");
                // Use dialogue system fallback
                var fallbackDialogue = dialogueSystem.GenerateContextualResponse(trigger, personality, GetWorldState());
                onDialogueGenerated?.Invoke(fallbackDialogue);
            }
        }

        private List<string> GetRecentHistory()
        {
            return new List<string>(_conversationHistory);
        }

        private Dictionary<string, object> GetWorldState()
        {
            var worldState = new Dictionary<string, object>
            {
                {"location", transform.position.ToString()}
            };

            // Safe access to GameManager using FindFirstObjectByType as fallback
            var gameManager = FindFirstObjectByType<TWG.TLDA.GameManager>();
            if (gameManager != null)
            {
                worldState["playerLevel"] = gameManager.PlayerLevel;
                worldState["timeOfDay"] = gameManager.CurrentTimeOfDay.ToString();
            }
            else
            {
                worldState["playerLevel"] = 1;
                worldState["timeOfDay"] = "Morning";
            }

            // Safe access to QuestManager using FindFirstObjectByType as fallback
            var questManager = FindFirstObjectByType<TWG.TLDA.QuestManager>();
            if (questManager != null)
            {
                worldState["questStates"] = questManager.GetActiveQuests();
            }
            else
            {
                worldState["questStates"] = new List<string>();
            }

            return worldState;
        }
    }

    [Serializable]
    public class NpcPersonality
    {
        public string name = "Unknown NPC";
        public string species = "Human"; // From companion_battle.json
        public string element = "Neutral";
        public string temperament = "Balanced";
        [Range(0, 1)] public float aggression = 0.5f;
        [Range(0, 1)] public float loyalty = 0.5f;
        [Range(0, 1)] public float intelligence = 0.5f;

        public string ToJson() => JsonUtility.ToJson(this);
    }

    [Serializable]
    public class WarblerDecisionRequest
    {
        public string context = "";
        public string[] options = new string[0];
        public string npcPersonality = "";
        public Dictionary<string, object> WorldState = new Dictionary<string, object>();
    }
}
