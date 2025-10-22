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
        // ⚠ Intention ⚠ - @jmeyer1980 - you will see messages to remove the SerializerField attribute. Ignore them.
        // The IDE is nitpicking over the fact that they are readonly. They are needed for Unity serialization.
        [Header("Warbler Context")]
        [SerializeField] private string npcContextId = "companion_warbler";
        [SerializeField] private string sceneContextId = "companion_battle";

        [Header("Battle Conversation Templates")]
        private readonly List<BattleConversationTemplate> conversationTemplates = new();

        [Header("Memory Hooks")]
        private readonly List<string> developerMemories = new();
        private readonly List<string> battleMemories = new();

        [Header("Conversation Queue Settings")]
        [SerializeField] private float maxQueueProcessingTime = 0.5f; // Max time per frame for processing
        [SerializeField] private int maxEventsPerFrame = 3; // Max conversation events per frame
        [SerializeField] private bool enableBatchProcessing = true;

        // Warbler integration state
        private readonly Dictionary<Companion, WarblerPersonalityContext> companionPersonalities = new();
        
        // ✅ LEGENDARY IMPLEMENTATION: Conversation queue for batch processing
        private readonly Queue<BattleConversationEvent> conversationQueue = new();
        private readonly Dictionary<Companion, float> companionCooldowns = new();
        private float lastBatchProcessTime = 0f;

        // Events
        public event Action<Companion, string, BattleContext> OnDynamicQuipGenerated;
        public event Action<Companion, ConversationMemory> OnMemoryCreated;
        public event Action<int> OnConversationQueueSizeChanged; // For UI monitoring

        [Serializable]
        public class BattleConversationTemplate
        {
            public string templateId;
            public BattleEventType triggerEvent;
            public List<string> templateVariations = new();
            public List<string> personalityModifiers = new();
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
            public List<string> quirks = new();
            public Dictionary<string, float> conversationWeights = new();
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

        private void Update()
        {
            if (enableBatchProcessing)
            {
                ProcessConversationQueue();
            }
        }

        /// <summary>
        /// Initialize Warbler integration with companion personality setup
        /// KeeperNote: Links badge pet personality data to Warbler conversation system
        /// </summary>
        private void InitializeWarblerIntegration()
        {
            // Subscribe to battle manager events if available
            var battleManager = FindFirstObjectByType<CompanionBattleManager>();
            if (battleManager != null)
            {
                SubscribeToBattleEvents(battleManager);
            }

            // Initialize conversation processing
            lastBatchProcessTime = Time.time;

            // Initialize with default context
            Debug.Log($"[WarblerIntegration] Initialized battle conversation system with context: {npcContextId}");
        }

        private void SubscribeToBattleEvents(CompanionBattleManager battleManager)
        {
            // Subscribe to battle events to trigger appropriate conversations
            battleManager.OnTurnStarted += OnTurnStarted;
            battleManager.OnTurnEnded += OnTurnEnded;
            battleManager.OnBattleEnded += OnBattleEnded;
        }

        /// <summary>
        /// Process conversation queue in batches to maintain performance
        /// KeeperNote: Prevents conversation spam and ensures smooth battle flow
        /// </summary>
        private void ProcessConversationQueue()
        {
            if (conversationQueue.Count == 0) return;

            float startTime = Time.realtimeSinceStartup;
            int eventsProcessed = 0;

            // Process events until we hit time or count limits
            while (conversationQueue.Count > 0 && 
                   eventsProcessed < maxEventsPerFrame && 
                   (Time.realtimeSinceStartup - startTime) < maxQueueProcessingTime)
            {
                var conversationEvent = conversationQueue.Dequeue();
                
                // Check if it's time to process this event
                if (DateTime.UtcNow >= conversationEvent.scheduledTime)
                {
                    ExecuteConversationEvent(conversationEvent);
                    eventsProcessed++;
                }
                else
                {
                    // Put it back if not ready yet
                    conversationQueue.Enqueue(conversationEvent);
                    break;
                }
            }

            // Update queue size monitoring
            OnConversationQueueSizeChanged?.Invoke(conversationQueue.Count);

            lastBatchProcessTime = Time.time;
        }

        /// <summary>
        /// Execute a queued conversation event
        /// KeeperNote: Handles the actual quip delivery with personality context
        /// </summary>
        private void ExecuteConversationEvent(BattleConversationEvent conversationEvent)
        {
            if (conversationEvent.speaker == null || string.IsNullOrEmpty(conversationEvent.generatedQuip))
                return;

            // Check companion cooldown
            if (companionCooldowns.ContainsKey(conversationEvent.speaker))
            {
                float timeSinceLastQuip = Time.time - companionCooldowns[conversationEvent.speaker];
                if (timeSinceLastQuip < 2f) // Minimum 2 second cooldown between quips
                {
                    return;
                }
            }

            // Execute the quip
            conversationEvent.speaker.SpeakQuip(conversationEvent.generatedQuip);
            
            // Update cooldown
            companionCooldowns[conversationEvent.speaker] = Time.time;

            // Trigger event for external listeners
            OnDynamicQuipGenerated?.Invoke(
                conversationEvent.speaker, 
                conversationEvent.generatedQuip, 
                conversationEvent.context
            );

            Debug.Log($"[WarblerIntegration] Executed queued quip: {conversationEvent.speaker.Name} - \"{conversationEvent.generatedQuip}\"");
        }

        /// <summary>
        /// Queue a conversation event for batch processing
        /// KeeperNote: Allows for priority-based conversation scheduling
        /// </summary>
        public void QueueConversationEvent(Companion speaker, BattleContext context, float priority = 1f, float delaySeconds = 0f)
        {
            if (!enableBatchProcessing)
            {
                // If batch processing is disabled, generate and speak immediately
                string immediateQuip = GenerateBattleQuip(speaker, context);
                if (!string.IsNullOrEmpty(immediateQuip))
                {
                    speaker.SpeakQuip(immediateQuip);
                }
                return;
            }

            // Generate the quip for queueing
            string generatedQuip = GenerateBattleQuip(speaker, context);
            if (string.IsNullOrEmpty(generatedQuip))
                return;

            var conversationEvent = new BattleConversationEvent
            {
                speaker = speaker,
                context = context,
                generatedQuip = generatedQuip,
                priority = priority,
                scheduledTime = DateTime.UtcNow.AddSeconds(delaySeconds)
            };

            // Insert based on priority (higher priority goes first)
            if (conversationQueue.Count == 0 || priority <= 1f)
            {
                conversationQueue.Enqueue(conversationEvent);
            }
            else
            {
                // For high priority events, we need to reorder the queue
                var tempList = new List<BattleConversationEvent>();
                
                // Extract existing events
                while (conversationQueue.Count > 0)
                {
                    tempList.Add(conversationQueue.Dequeue());
                }
                
                // Add the new high priority event
                tempList.Add(conversationEvent);
                
                // Sort by priority (descending) then by scheduled time
                tempList.Sort((a, b) => 
                {
                    int priorityComparison = b.priority.CompareTo(a.priority);
                    if (priorityComparison != 0) return priorityComparison;
                    return a.scheduledTime.CompareTo(b.scheduledTime);
                });
                
                // Re-queue everything
                foreach (var evt in tempList)
                {
                    conversationQueue.Enqueue(evt);
                }
            }

            OnConversationQueueSizeChanged?.Invoke(conversationQueue.Count);
        }

        /// <summary>
        /// Clear conversation queue (useful for battle resets)
        /// KeeperNote: Prevents stale conversations from previous battles
        /// </summary>
        public void ClearConversationQueue()
        {
            conversationQueue.Clear();
            OnConversationQueueSizeChanged?.Invoke(0);
            Debug.Log("[WarblerIntegration] Conversation queue cleared");
        }

        /// <summary>
        /// Get current conversation queue statistics
        /// KeeperNote: Useful for debugging and UI monitoring
        /// </summary>
        public ConversationQueueStats GetQueueStats()
        {
            return new ConversationQueueStats
            {
                QueueSize = conversationQueue.Count,
                LastProcessTime = lastBatchProcessTime,
                MaxQueueProcessingTime = maxQueueProcessingTime,
                MaxEventsPerFrame = maxEventsPerFrame,
                BatchProcessingEnabled = enableBatchProcessing
            };
        }

        [Serializable]
        public class ConversationQueueStats
        {
            public int QueueSize;
            public float LastProcessTime;
            public float MaxQueueProcessingTime;
            public int MaxEventsPerFrame;
            public bool BatchProcessingEnabled;
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

            // Subscribe to companion events for queue-based processing
            companion.OnAbilityUsed += (comp, ability) => 
            {
                var context = new BattleContext
                {
                    eventType = BattleEventType.AbilityUse,
                    primaryCompanion = comp,
                    usedAbility = ability,
                    battleProgress = 0.5f // Would be calculated
                };
                QueueConversationEvent(comp, context, 1f, 0.2f); // Slight delay for ability quips
            };
            
            companion.OnQuipSpoken += (comp, quip) => OnQuipSpoken(comp, quip);

            Debug.Log($"[WarblerIntegration] Registered {companion.Name} with personality type: {personality.personalityType}");
        }

        private WarblerPersonalityContext CreatePersonalityContext(Companion companion)
        {
            var context = new WarblerPersonalityContext
            {
                temperament = companion.Temperament,
                personalityType = DeterminePersonalityType(companion),
                lastQuipTime = 0f,
                // Convert companion traits to conversation weights
                conversationWeights = new Dictionary<string, float>
                {
                    [ "humor" ] = GetTraitWeight(companion, "humor"),
                    [ "technical" ] = GetTraitWeight(companion, "technical"),
                    [ "supportive" ] = GetTraitWeight(companion, "supportive"),
                    [ "competitive" ] = GetTraitWeight(companion, "competitive"),
                    [ "analytical" ] = GetTraitWeight(companion, "analytical")
                },

                // Add personality quirks based on species and temperament
                quirks = GeneratePersonalityQuirks(companion)
            };

            return context;
        }

        private string DeterminePersonalityType(Companion companion)
        {
            // Map companion characteristics to Warbler personality types
            return companion.Temperament switch
            {
                CompanionTemperament.Aggressive => "competitive_challenger",
                CompanionTemperament.Defensive => "protective_guardian",
                CompanionTemperament.Tactical => "analytical_strategist",
                CompanionTemperament.Intuitive => "creative_innovator",
                CompanionTemperament.Loyal => "supportive_teammate",
                _ => "balanced_companion",
            };
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
            var template = FindBestTemplate(context.eventType);
            if (template == null)
            {
                return GenerateGenericQuip(companion);
            }

            // Generate contextual quip
            string quip = ProcessConversationTemplate(template, companion, context);
            
            personality.lastQuipTime = Time.time;

            // Create memory if significant
            if (ShouldCreateMemory(context))
            {
                CreateBattleMemory(companion, context, quip);
            }

            return quip;
        }

        private BattleConversationTemplate FindBestTemplate(BattleEventType eventType)
        {
            return conversationTemplates.Find(t => t.triggerEvent == eventType);
        }

        private string ProcessConversationTemplate(BattleConversationTemplate template, Companion companion, BattleContext context)
        {
            if (template.templateVariations.Count == 0)
                return "...";
            Debug.Log("template.templateVariations.Count: " + template.templateVariations.Count);
            // Select variation based on personality
            var personality = companionPersonalities[companion];
            string baseTemplate = template.templateVariations[UnityEngine.Random.Range(0, template.templateVariations.Count)];

            // Apply personality modifiers
            string processedQuip = ApplyPersonalityModifiers(baseTemplate, personality);

            // Apply context substitutions
            processedQuip = ApplyContextSubstitutions(processedQuip, context);

            return processedQuip;
        }

        private string ApplyPersonalityModifiers(string baseTemplate, WarblerPersonalityContext personality)
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
            result = result.Replace("{target}", context.targetCompanion != null ? context.targetCompanion.Name : "opponent");
            result = result.Replace("{ability}", context.usedAbility != null ? context.usedAbility.name : "move");
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

        private string GenerateGenericQuip(Companion companion)
        {
            // Fallback generic quips when no template found
            List<string> genericQuips = new()
            {
                "Let's do this!",
                "I'm ready for anything!",
                "Together we're stronger!",
                "Time to show our skills!",
                "This is what we trained for!"
            };

            var selectedQuip = genericQuips[UnityEngine.Random.Range(0, genericQuips.Count)];
            
            // Add companion personality touch to generic quip
            var personality = companionPersonalities.ContainsKey(companion) 
                ? companionPersonalities[companion] 
                : null;
                
            if (personality != null && personality.temperament == CompanionTemperament.Aggressive)
            {
                selectedQuip = selectedQuip.Replace("Let's", "We'll").Replace("!", "!!");
            }
            
            return selectedQuip;
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
        private void OnTurnStarted(Companion activeCompanion)
        {
            var context = new BattleContext
            {
                eventType = BattleEventType.TurnStart,
                primaryCompanion = activeCompanion,
                battleProgress = 0.5f, // Would be calculated from battle state
                turnNumber = 1 // Would be actual turn number
            };

            // Use queue for turn start quips (low priority)
            QueueConversationEvent(activeCompanion, context, 0.5f, 0.3f);
        }

        private void OnTurnEnded(Companion activeCompanion)
        {
            // Could generate end-of-turn quips based on performance
            Debug.Log($"[WarblerIntegration] Turn ended for {activeCompanion.Name}");
        }

        private void OnBattleEnded(List<Companion> winningCompanions)
        {
            foreach (var winner in winningCompanions)
            {
                var context = new BattleContext
                {
                    eventType = BattleEventType.Victory,
                    primaryCompanion = winner,
                    battleProgress = 1f
                };

                // Victory quips get high priority and immediate processing
                QueueConversationEvent(winner, context, 2f, 0f);
            }
        }

        private void OnQuipSpoken(Companion speakingCompanion, string spokenQuip)
        {
            Debug.Log($"[WarblerIntegration] {speakingCompanion.Name} spoke: \"{spokenQuip}\"");
        }

        /// <summary>
        /// Export Warbler personality data for companion NFT metadata
        /// KeeperNote: Includes conversation preferences and memory hooks for AI customization
        /// </summary>
        public Dictionary<string, object> ExportWarblerMetadata(Companion targetCompanion)
        {
            if (!companionPersonalities.ContainsKey(targetCompanion))
            {
                RegisterCompanion(targetCompanion);
            }

            var personality = companionPersonalities[targetCompanion];
            
            return new Dictionary<string, object>
            {
                ["personality_type"] = personality.personalityType,
                ["temperament"] = personality.temperament.ToString(),
                ["conversation_weights"] = personality.conversationWeights,
                ["personality_quirks"] = personality.quirks,
                ["memory_hooks"] = GetRelevantMemories(targetCompanion),
                ["battle_conversation_history"] = battleMemories.Count > 0 ? battleMemories.GetRange(Math.Max(0, battleMemories.Count - 10), Math.Min(10, battleMemories.Count)) : new List<string>(),
                ["scene_context"] = sceneContextId,
                ["conversation_queue_stats"] = GetQueueStats()
            };
        }

        private List<string> GetRelevantMemories(Companion targetCompanion)
        {
            // Return relevant developer and battle memories for this companion
            var relevantMemories = new List<string>();
            relevantMemories.AddRange(developerMemories);
            
            // Add recent battle memories
            if (battleMemories.Count > 0)
            {
                relevantMemories.AddRange(battleMemories.GetRange(Math.Max(0, battleMemories.Count - 5), Math.Min(5, battleMemories.Count)));
            }

            // Add companion-specific context
            relevantMemories.Add($"Companion: {targetCompanion.Name} ({targetCompanion.Temperament})");

            return relevantMemories;
        }
    }
}
