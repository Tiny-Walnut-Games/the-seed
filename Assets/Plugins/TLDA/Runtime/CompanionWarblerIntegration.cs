using System;
using System.Collections.Generic;
using UnityEngine;

namespace LivingDevAgent.Runtime.CompanionBattler
{
    /// <summary>
    /// Warbler integration for companion battle personality and dynamic conversation
    /// KeeperNote: Bridges Warbler conversation system with battle events for dynamic quips
    /// </summary>
    public class CompanionWarblerIntegration : MonoBehaviour
    {
        [Header("Warbler Context")]
        [SerializeField] private string npcContextId;
        [SerializeField] private string sceneContextId = "companion_battle";

        [Header("Battle Conversation Templates")]
        [SerializeField] private List<BattleConversationTemplate> conversationTemplates = new List<BattleConversationTemplate>();

        [Header("Memory Hooks")]
        [SerializeField] private List<string> developerMemories = new List<string>();
        [SerializeField] private List<string> battleMemories = new List<string>();

        // Warbler integration state
        private Dictionary<Companion, WarblerPersonalityContext> companionPersonalities = new Dictionary<Companion, WarblerPersonalityContext>();
        private Queue<BattleConversationEvent> conversationQueue = new Queue<BattleConversationEvent>();

        // Events
        public event Action<Companion, string, BattleContext> OnDynamicQuipGenerated;
        public event Action<Companion, ConversationMemory> OnMemoryCreated;

        [Serializable]
        public class BattleConversationTemplate
        {
            public string templateId;
            public BattleEventType triggerEvent;
            public List<string> templateVariations = new List<string>();
            public List<string> personalityModifiers = new List<string>();
            public float cooldownSeconds = 5f;
        }

        [Serializable]
        public enum BattleEventType
        {
            BattleStart,
            TurnStart,
            AbilityUse,
            TakeDamage,
            DealDamage,
            LowHealth,
            HighEnergy,
            StatusEffect,
            Victory,
            Defeat,
            Synergy,
            Evolution
        }

        [Serializable]
        public class WarblerPersonalityContext
        {
            public string personalityType;
            public CompanionTemperament temperament;
            public List<string> quirks = new List<string>();
            public Dictionary<string, float> conversationWeights = new Dictionary<string, float>();
            public float lastQuipTime;
        }

        [Serializable]
        public class BattleContext
        {
            public BattleEventType eventType;
            public Companion primaryCompanion;
            public Companion targetCompanion;
            public CompanionAbility usedAbility;
            public float battleProgress;
            public int turnNumber;
            public string additionalContext;
        }

        [Serializable]
        public class ConversationMemory
        {
            public string memoryId;
            public string developerName;
            public string memoryText;
            public BattleEventType associatedEvent;
            public DateTime createdAt;
            public int referencedCount;
        }

        [Serializable]
        public class BattleConversationEvent
        {
            public Companion speaker;
            public BattleContext context;
            public string generatedQuip;
            public float priority;
            public DateTime scheduledTime;
        }

        private void Start()
        {
            InitializeWarblerIntegration();
        }

        /// <summary>
        /// Initialize Warbler integration with companion personality setup
        /// KeeperNote: Links badge pet personality data to Warbler conversation system
        /// </summary>
        private void InitializeWarblerIntegration()
        {
            // Subscribe to battle manager events if available
            var battleManager = FindObjectOfType<CompanionBattleManager>();
            if (battleManager != null)
            {
                SubscribeToBattleEvents(battleManager);
            }

            Debug.Log("[WarblerIntegration] Initialized battle conversation system");
        }

        private void SubscribeToBattleEvents(CompanionBattleManager battleManager)
        {
            // Subscribe to battle events to trigger appropriate conversations
            battleManager.OnTurnStarted += OnTurnStarted;
            battleManager.OnTurnEnded += OnTurnEnded;
            battleManager.OnBattleEnded += OnBattleEnded;
        }

        /// <summary>
        /// Register companion with Warbler personality context
        /// KeeperNote: Converts badge pet traits to Warbler conversation weights
        /// </summary>
        public void RegisterCompanion(Companion companion)
        {
            if (companionPersonalities.ContainsKey(companion))
                return;

            var personality = CreatePersonalityContext(companion);
            companionPersonalities[companion] = personality;

            // Subscribe to companion events
            companion.OnAbilityUsed += (comp, ability) => OnAbilityUsed(comp, ability);
            companion.OnQuipSpoken += (comp, quip) => OnQuipSpoken(comp, quip);

            Debug.Log($"[WarblerIntegration] Registered {companion.Name} with personality type: {personality.personalityType}");
        }

        private WarblerPersonalityContext CreatePersonalityContext(Companion companion)
        {
            var context = new WarblerPersonalityContext
            {
                temperament = companion.Temperament,
                personalityType = DeterminePersonalityType(companion),
                lastQuipTime = 0f
            };

            // Convert companion traits to conversation weights
            context.conversationWeights = new Dictionary<string, float>
            {
                ["humor"] = GetTraitWeight(companion, "humor"),
                ["technical"] = GetTraitWeight(companion, "technical"),
                ["supportive"] = GetTraitWeight(companion, "supportive"),
                ["competitive"] = GetTraitWeight(companion, "competitive"),
                ["analytical"] = GetTraitWeight(companion, "analytical")
            };

            // Add personality quirks based on species and temperament
            context.quirks = GeneratePersonalityQuirks(companion);

            return context;
        }

        private string DeterminePersonalityType(Companion companion)
        {
            // Map companion characteristics to Warbler personality types
            switch (companion.Temperament)
            {
                case CompanionTemperament.Aggressive:
                    return "competitive_challenger";
                case CompanionTemperament.Defensive:
                    return "protective_guardian";
                case CompanionTemperament.Tactical:
                    return "analytical_strategist";
                case CompanionTemperament.Intuitive:
                    return "creative_innovator";
                case CompanionTemperament.Loyal:
                    return "supportive_teammate";
                default:
                    return "balanced_companion";
            }
        }

        private float GetTraitWeight(Companion companion, string traitCategory)
        {
            // Convert companion traits to Warbler conversation weights
            float weight = 0.5f; // Base weight

            switch (traitCategory)
            {
                case "humor":
                    weight += companion.Temperament == CompanionTemperament.Intuitive ? 0.3f : 0f;
                    break;
                case "technical":
                    weight += companion.Element == CompanionElement.Logic ? 0.3f : 0f;
                    break;
                case "supportive":
                    weight += companion.Archetype == CompanionArchetype.Support ? 0.3f : 0f;
                    weight += companion.Temperament == CompanionTemperament.Loyal ? 0.2f : 0f;
                    break;
                case "competitive":
                    weight += companion.Archetype == CompanionArchetype.Striker ? 0.3f : 0f;
                    weight += companion.Temperament == CompanionTemperament.Aggressive ? 0.2f : 0f;
                    break;
                case "analytical":
                    weight += companion.Archetype == CompanionArchetype.Controller ? 0.3f : 0f;
                    weight += companion.Temperament == CompanionTemperament.Tactical ? 0.2f : 0f;
                    break;
            }

            return Mathf.Clamp01(weight);
        }

        private List<string> GeneratePersonalityQuirks(Companion companion)
        {
            var quirks = new List<string>();

            // Species-based quirks
            switch (companion.Id.ToLower())
            {
                case var id when id.Contains("scrollhound"):
                    quirks.Add("references_documentation_frequently");
                    quirks.Add("uses_formal_language");
                    break;
                case var id when id.Contains("debugger_ferret"):
                    quirks.Add("mentions_bugs_and_fixes");
                    quirks.Add("uses_debugging_metaphors");
                    break;
                case var id when id.Contains("chrono_cat"):
                    quirks.Add("time_management_focused");
                    quirks.Add("mentions_deadlines_and_sprints");
                    break;
            }

            // Temperament-based quirks
            switch (companion.Temperament)
            {
                case CompanionTemperament.Aggressive:
                    quirks.Add("uses_competitive_language");
                    quirks.Add("challenges_opponents");
                    break;
                case CompanionTemperament.Defensive:
                    quirks.Add("protective_of_teammates");
                    quirks.Add("cautious_optimism");
                    break;
                case CompanionTemperament.Tactical:
                    quirks.Add("analyzes_situations_aloud");
                    quirks.Add("suggests_strategies");
                    break;
            }

            return quirks;
        }

        /// <summary>
        /// Generate dynamic battle quip using Warbler conversation templates
        /// KeeperNote: Creates contextual dialogue based on battle state and companion personality
        /// </summary>
        public string GenerateBattleQuip(Companion companion, BattleContext context)
        {
            if (!companionPersonalities.ContainsKey(companion))
            {
                RegisterCompanion(companion);
            }

            var personality = companionPersonalities[companion];

            // Check cooldown
            if (Time.time - personality.lastQuipTime < 3f)
            {
                return null;
            }

            // Find appropriate conversation template
            var template = FindBestTemplate(context.eventType, personality);
            if (template == null)
            {
                return GenerateGenericQuip(companion, context);
            }

            // Generate contextual quip
            string quip = ProcessConversationTemplate(template, companion, context);
            
            personality.lastQuipTime = Time.time;

            // Create memory if significant
            if (ShouldCreateMemory(context))
            {
                CreateBattleMemory(companion, context, quip);
            }

            OnDynamicQuipGenerated?.Invoke(companion, quip, context);
            return quip;
        }

        private BattleConversationTemplate FindBestTemplate(BattleEventType eventType, WarblerPersonalityContext personality)
        {
            return conversationTemplates.Find(t => t.triggerEvent == eventType);
        }

        private string ProcessConversationTemplate(BattleConversationTemplate template, Companion companion, BattleContext context)
        {
            if (template.templateVariations.Count == 0)
                return "...";

            // Select variation based on personality
            var personality = companionPersonalities[companion];
            string baseTemplate = template.templateVariations[UnityEngine.Random.Range(0, template.templateVariations.Count)];

            // Apply personality modifiers
            string processedQuip = ApplyPersonalityModifiers(baseTemplate, personality, context);

            // Apply context substitutions
            processedQuip = ApplyContextSubstitutions(processedQuip, context);

            return processedQuip;
        }

        private string ApplyPersonalityModifiers(string baseTemplate, WarblerPersonalityContext personality, BattleContext context)
        {
            string modified = baseTemplate;

            // Apply temperament-specific modifications
            switch (personality.temperament)
            {
                case CompanionTemperament.Aggressive:
                    modified = modified.Replace("{tone}", "forcefully");
                    modified = modified.Replace("{attitude}", "challenging");
                    break;
                case CompanionTemperament.Defensive:
                    modified = modified.Replace("{tone}", "carefully");
                    modified = modified.Replace("{attitude}", "protective");
                    break;
                case CompanionTemperament.Tactical:
                    modified = modified.Replace("{tone}", "analytically");
                    modified = modified.Replace("{attitude}", "strategic");
                    break;
                case CompanionTemperament.Intuitive:
                    modified = modified.Replace("{tone}", "creatively");
                    modified = modified.Replace("{attitude}", "unpredictable");
                    break;
                case CompanionTemperament.Loyal:
                    modified = modified.Replace("{tone}", "supportively");
                    modified = modified.Replace("{attitude}", "team-focused");
                    break;
            }

            return modified;
        }

        private string ApplyContextSubstitutions(string template, BattleContext context)
        {
            string result = template;

            // Context-specific substitutions
            result = result.Replace("{target}", context.targetCompanion?.Name ?? "opponent");
            result = result.Replace("{ability}", context.usedAbility?.name ?? "move");
            result = result.Replace("{turn}", context.turnNumber.ToString());

            // Battle progress substitutions
            if (context.battleProgress < 0.25f)
                result = result.Replace("{battle_phase}", "early battle");
            else if (context.battleProgress < 0.75f)
                result = result.Replace("{battle_phase}", "mid battle");
            else
                result = result.Replace("{battle_phase}", "late battle");

            return result;
        }

        private string GenerateGenericQuip(Companion companion, BattleContext context)
        {
            // Fallback generic quips when no template found
            List<string> genericQuips = new List<string>
            {
                "Let's do this!",
                "I'm ready for anything!",
                "Together we're stronger!",
                "Time to show our skills!",
                "This is what we trained for!"
            };

            return genericQuips[UnityEngine.Random.Range(0, genericQuips.Count)];
        }

        private bool ShouldCreateMemory(BattleContext context)
        {
            // Create memories for significant events
            return context.eventType == BattleEventType.Victory ||
                   context.eventType == BattleEventType.Evolution ||
                   context.eventType == BattleEventType.Synergy;
        }

        private void CreateBattleMemory(Companion companion, BattleContext context, string quip)
        {
            var memory = new ConversationMemory
            {
                memoryId = Guid.NewGuid().ToString(),
                developerName = "Unknown", // Would be filled from companion data
                memoryText = $"{companion.Name} said '{quip}' during {context.eventType}",
                associatedEvent = context.eventType,
                createdAt = DateTime.UtcNow,
                referencedCount = 0
            };

            battleMemories.Add(memory.memoryText);
            OnMemoryCreated?.Invoke(companion, memory);

            Debug.Log($"[WarblerIntegration] Created battle memory: {memory.memoryText}");
        }

        // Event handlers
        private void OnTurnStarted(Companion companion)
        {
            var context = new BattleContext
            {
                eventType = BattleEventType.TurnStart,
                primaryCompanion = companion,
                battleProgress = 0.5f, // Would be calculated from battle state
                turnNumber = 1 // Would be actual turn number
            };

            string quip = GenerateBattleQuip(companion, context);
            if (!string.IsNullOrEmpty(quip))
            {
                companion.GetComponent<Companion>()?.OnQuipSpoken?.Invoke(companion, quip);
            }
        }

        private void OnTurnEnded(Companion companion)
        {
            // Could generate end-of-turn quips based on performance
        }

        private void OnBattleEnded(List<Companion> winners)
        {
            foreach (var winner in winners)
            {
                var context = new BattleContext
                {
                    eventType = BattleEventType.Victory,
                    primaryCompanion = winner,
                    battleProgress = 1f
                };

                string quip = GenerateBattleQuip(winner, context);
                if (!string.IsNullOrEmpty(quip))
                {
                    winner.GetComponent<Companion>()?.OnQuipSpoken?.Invoke(winner, quip);
                }
            }
        }

        private void OnAbilityUsed(Companion user, CompanionAbility ability)
        {
            var context = new BattleContext
            {
                eventType = BattleEventType.AbilityUse,
                primaryCompanion = user,
                usedAbility = ability,
                battleProgress = 0.5f // Would be calculated
            };

            string quip = GenerateBattleQuip(user, context);
            if (!string.IsNullOrEmpty(quip))
            {
                user.GetComponent<Companion>()?.OnQuipSpoken?.Invoke(user, quip);
            }
        }

        private void OnQuipSpoken(Companion speaker, string quip)
        {
            Debug.Log($"[WarblerIntegration] {speaker.Name} spoke: \"{quip}\"");
        }

        /// <summary>
        /// Export Warbler personality data for companion NFT metadata
        /// KeeperNote: Includes conversation preferences and memory hooks for AI customization
        /// </summary>
        public Dictionary<string, object> ExportWarblerMetadata(Companion companion)
        {
            if (!companionPersonalities.ContainsKey(companion))
            {
                RegisterCompanion(companion);
            }

            var personality = companionPersonalities[companion];
            
            return new Dictionary<string, object>
            {
                ["personality_type"] = personality.personalityType,
                ["temperament"] = personality.temperament.ToString(),
                ["conversation_weights"] = personality.conversationWeights,
                ["personality_quirks"] = personality.quirks,
                ["memory_hooks"] = GetRelevantMemories(companion),
                ["battle_conversation_history"] = battleMemories.Count > 0 ? battleMemories.GetRange(Math.Max(0, battleMemories.Count - 10), Math.Min(10, battleMemories.Count)) : new List<string>()
            };
        }

        private List<string> GetRelevantMemories(Companion companion)
        {
            // Return relevant developer and battle memories for this companion
            var relevantMemories = new List<string>();
            relevantMemories.AddRange(developerMemories);
            
            // Add recent battle memories
            if (battleMemories.Count > 0)
            {
                relevantMemories.AddRange(battleMemories.GetRange(Math.Max(0, battleMemories.Count - 5), Math.Min(5, battleMemories.Count)));
            }

            return relevantMemories;
        }
    }
}