using System;
using System.Collections.Generic;
using UnityEngine;

namespace TWG.TLDA.NPCControl
{
    /// <summary>
    /// ??? PROTECTED CORE - Complete dialogue system for Warbler NPCs
    /// Provides full dialogue functionality ready for customer use
    /// </summary>
    [System.Serializable]
    public class WarblerDialogueSystem
    {
        [Header("Dialogue Configuration")]
        [SerializeField] private int maxHistoryEntries = 50;
        [SerializeField] private bool enableDialogueLogging = true;

        private List<DialogueEntry> _conversationHistory = new List<DialogueEntry>();
        private Dictionary<string, List<string>> _dialogueResponseLibrary = new Dictionary<string, List<string>>();

        [System.Serializable]
        public class DialogueEntry
        {
            public string speaker = string.Empty;
            public string content = string.Empty;
            public DateTime Timestamp;
            public DialogueType type;
        }

        public enum DialogueType
        {
            PlayerInput,
            NpcResponse,
            SystemMessage,
            EmotionalContext
        }

        public WarblerDialogueSystem()
        {
            InitializeDialogueLibrary();
        }

        public void AddDialogue(string speaker, string content, DialogueType type = DialogueType.NpcResponse)
        {
            var entry = new DialogueEntry
            {
                speaker = speaker,
                content = content,
                Timestamp = DateTime.Now,
                type = type
            };

            _conversationHistory.Add(entry);

            // Maintain history size
            if (_conversationHistory.Count > maxHistoryEntries)
            {
                _conversationHistory.RemoveAt(0);
            }

            if (enableDialogueLogging)
            {
                Debug.Log($"💬 [{speaker}]: {content}");
            }
        }

        public List<string> GetRecentHistory(int count = 10)
        {
            var recentEntries = new List<string>();
            var startIndex = Mathf.Max(0, _conversationHistory.Count - count);

            for (var i = startIndex; i < _conversationHistory.Count; i++)
            {
                var entry = _conversationHistory[i];
                recentEntries.Add($"{entry.speaker}: {entry.content}");
            }

            return recentEntries;
        }

        public List<DialogueEntry> GetFullHistory()
        {
            return new List<DialogueEntry>(_conversationHistory);
        }

        public string GenerateContextualResponse(string trigger, NpcPersonality personality, Dictionary<string, object> worldState)
        {
            // Generate response based on personality and context
            var baseResponse = GetBaseResponse(trigger);
            var personalizedResponse = PersonalizeResponse(baseResponse, personality, worldState);

            AddDialogue(personality.name, personalizedResponse, DialogueType.NpcResponse);

            return personalizedResponse;
        }

        private string GetBaseResponse(string trigger)
        {
            trigger = trigger.ToLower();

            // Check for specific triggers in our library
            foreach (var kvp in _dialogueResponseLibrary)
            {
                if (trigger.Contains(kvp.Key))
                {
                    var responses = kvp.Value;
                    return responses[UnityEngine.Random.Range(0, responses.Count)];
                }
            }

            // Default responses
            var defaultResponses = new string[]
            {
                "That's interesting. Tell me more.",
                "I see. What do you think about that?",
                "Hmm, I hadn't considered that perspective.",
                "That reminds me of something...",
                "How does that make you feel?"
            };

            return defaultResponses[UnityEngine.Random.Range(0, defaultResponses.Length)];
        }

        private string PersonalizeResponse(string baseResponse, NpcPersonality personality, Dictionary<string, object> worldState)
        {
            var personalizedResponse = baseResponse;

            // Modify based on personality traits
            if (personality.aggression > 0.7f)
            {
                personalizedResponse = MakeMoreAggressive(personalizedResponse);
            }
            else if (personality.aggression < 0.3f)
            {
                personalizedResponse = MakeMoreGentle(personalizedResponse);
            }

            if (personality.intelligence > 0.8f)
            {
                personalizedResponse = AddIntellectualFlair(personalizedResponse);
            }

            // Add contextual information
            personalizedResponse = AddWorldContext(personalizedResponse, worldState);

            return personalizedResponse;
        }

        private string MakeMoreAggressive(string response)
        {
            var aggressiveModifiers = new string[] { "Listen here,", "Look,", "Frankly,", "To be blunt," };
            var modifier = aggressiveModifiers[UnityEngine.Random.Range(0, aggressiveModifiers.Length)];
            return $"{modifier} {response.ToLower()}";
        }

        private string MakeMoreGentle(string response)
        {
            var gentleModifiers = new string[] { "Perhaps", "I wonder if", "It seems to me that", "Gently speaking," };
            var modifier = gentleModifiers[UnityEngine.Random.Range(0, gentleModifiers.Length)];
            return $"{modifier} {response.ToLower()}";
        }

        private string AddIntellectualFlair(string response)
        {
            var intellectualPhrases = new string[]
            {
                "From an analytical perspective,",
                "Considering the broader implications,",
                "If we examine this logically,",
                "The data suggests that"
            };
            var phrase = intellectualPhrases[UnityEngine.Random.Range(0, intellectualPhrases.Length)];
            return $"{phrase} {response.ToLower()}";
        }

        private string AddWorldContext(string response, Dictionary<string, object> worldState)
        {
            if (worldState == null) return response;

            // Add contextual awareness based on world state
            var contextualAdditions = new List<string>();

            if (worldState.ContainsKey("timeOfDay"))
            {
                var timeOfDay = worldState["timeOfDay"].ToString();
                if (timeOfDay.Contains("night") || timeOfDay.Contains("evening"))
                {
                    contextualAdditions.Add("It's getting late, but");
                }
                else if (timeOfDay.Contains("morning"))
                {
                    contextualAdditions.Add("This fine morning,");
                }
            }

            if (worldState.ContainsKey("location"))
            {
                contextualAdditions.Add("Here in this place,");
            }

            if (contextualAdditions.Count > 0)
            {
                var addition = contextualAdditions[UnityEngine.Random.Range(0, contextualAdditions.Count)];
                return $"{addition} {response.ToLower()}";
            }

            return response;
        }

        private void InitializeDialogueLibrary()
        {
            _dialogueResponseLibrary["greeting"] = new List<string>
            {
                "Well hello there! How can I help you today?",
                "Greetings, traveler. What brings you here?",
                "Good to see you! What's on your mind?",
                "Welcome! How may I assist you?"
            };

            _dialogueResponseLibrary["goodbye"] = new List<string>
            {
                "Farewell! Safe travels on your journey.",
                "Until we meet again, friend.",
                "Take care out there!",
                "May your path be blessed."
            };

            _dialogueResponseLibrary["quest"] = new List<string>
            {
                "Ah, you seek adventure! I might have something for you.",
                "Quests, you say? There are always challenges to face.",
                "A noble pursuit! Let me think of what needs doing.",
                "Adventure calls to you, I can tell."
            };

            _dialogueResponseLibrary["trade"] = new List<string>
            {
                "Looking to trade? I have some fine wares.",
                "Commerce is the lifeblood of civilization!",
                "What treasures do you seek today?",
                "I deal in only the finest goods."
            };

            _dialogueResponseLibrary["help"] = new List<string>
            {
                "Of course! I'm always happy to help.",
                "What assistance do you need?",
                "Help is freely given to those who ask.",
                "I'm at your service!"
            };
        }

        public void ClearHistory()
        {
            _conversationHistory.Clear();
            Debug.Log("🗑️ Dialogue history cleared");
        }

        public int GetHistoryCount()
        {
            return _conversationHistory.Count;
        }

        public bool HasSpokenBefore(string speaker)
        {
            return _conversationHistory.Exists(entry => entry.speaker.Equals(speaker, StringComparison.OrdinalIgnoreCase));
        }
    }
}
