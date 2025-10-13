using System;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;

namespace LivingDevAgent.Runtime.CompanionBattler
{
    /// <summary>
    /// Main companion class integrating TLDA/Warbler sprite pipeline with battle system
    /// KeeperNote: Bridge between badge pet data and Unity battle interface
    /// </summary>
    [Serializable]
    public class Companion : MonoBehaviour
    {
        [Header("Identity")]
        [SerializeField] private string companionId;
        [SerializeField] private string companionName;
        [SerializeField] private string species;
        [SerializeField] private string developerName;

        [Header("Battle Semantics")]
        [SerializeField] private CompanionElement element = CompanionElement.Balance;
        [SerializeField] private CompanionArchetype archetype = CompanionArchetype.Hybrid;
        [SerializeField] private CompanionTemperament temperament = CompanionTemperament.Loyal;
        [SerializeField] private int bondLevel = 1;

        [Header("Battle System")]
        [SerializeField] private CompanionBattleStats battleStats;
        [SerializeField] private List<CompanionAbility> abilities = new List<CompanionAbility>();

        [Header("TLDA/Warbler Integration")]
        [SerializeField] private string spriteSheetPath;
        [SerializeField] private SpriteRenderer spriteRenderer;
        [SerializeField] private Animator animator;

        [Header("Warbler Personality")]
        [SerializeField] private List<string> battleStartQuips = new List<string>();
        [SerializeField] private List<string> victoryQuips = new List<string>();
        [SerializeField] private List<string> defeatQuips = new List<string>();
        [SerializeField] private List<string> lowHealthQuips = new List<string>();

        // Events for battle system integration
        public event Action<Companion> OnCompanionDefeated;
        public event Action<Companion> OnCompanionVictory;
        public event Action<Companion, CompanionAbility> OnAbilityUsed;
        public event Action<Companion, string> OnQuipSpoken;

        // Properties
        public string Id => companionId;
        public string Name => companionName;
        public CompanionElement Element => element;
        public CompanionArchetype Archetype => archetype;
        public CompanionTemperament Temperament => temperament;
        public int BondLevel => bondLevel;
        public CompanionBattleStats BattleStats => battleStats;
        public List<CompanionAbility> Abilities => abilities;
        public bool IsAlive => battleStats.isAlive;

        private void Awake()
        {
            if (battleStats == null)
            {
                battleStats = new CompanionBattleStats();
            }

            if (spriteRenderer == null)
            {
                spriteRenderer = GetComponent<SpriteRenderer>();
            }

            if (animator == null)
            {
                animator = GetComponent<Animator>();
            }
        }

        /// <summary>
        /// Initialize companion from badge pet data (JSON integration)
        /// KeeperNote: Bridges Python badge pet system with Unity battle interface
        /// </summary>
        public void InitializeFromBadgePetData(string jsonData)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(jsonData);
                
                companionId = data.ContainsKey("pet_id") ? data["pet_id"].ToString() : Guid.NewGuid().ToString();
                companionName = data.ContainsKey("pet_name") ? data["pet_name"].ToString() : "Unknown Companion";
                species = data.ContainsKey("species") ? data["species"].ToString() : "unknown";
                developerName = data.ContainsKey("developer_name") ? data["developer_name"].ToString() : "Unknown Developer";

                // Parse battle semantics
                if (data.ContainsKey("element"))
                {
                    Enum.TryParse(data["element"].ToString(), true, out element);
                }
                
                if (data.ContainsKey("archetype"))
                {
                    Enum.TryParse(data["archetype"].ToString(), true, out archetype);
                }
                
                if (data.ContainsKey("temperament"))
                {
                    Enum.TryParse(data["temperament"].ToString(), true, out temperament);
                }

                bondLevel = data.ContainsKey("bond_level") ? Convert.ToInt32(data["bond_level"]) : 1;

                // Load sprite data if available
                if (data.ContainsKey("sprite_sheet_path"))
                {
                    spriteSheetPath = data["sprite_sheet_path"].ToString();
                    LoadSpriteSheet();
                }

                // Initialize battle stats based on evolution stage and bond level
                InitializeBattleStats(data);

                Debug.Log($"[Companion] Initialized {companionName} ({species}) - Element: {element}, Archetype: {archetype}");
            }
            catch (Exception e)
            {
                Debug.LogError($"[Companion] Failed to initialize from badge pet data: {e.Message}");
            }
        }

        private void InitializeBattleStats(Dictionary<string, object> data)
        {
            // Base stats from evolution stage
            string stage = data.ContainsKey("current_stage") ? data["current_stage"].ToString() : "hatchling";
            
            int baseHealth = GetBaseStatForStage("health", stage);
            int baseEnergy = GetBaseStatForStage("energy", stage);
            int baseAttack = GetBaseStatForStage("attack", stage);
            int baseDefense = GetBaseStatForStage("defense", stage);
            int baseSpeed = GetBaseStatForStage("speed", stage);

            // Apply bond level bonuses
            float bondMultiplier = 1.0f + (bondLevel - 1) * 0.1f;

            battleStats.maxHealth = Mathf.RoundToInt(baseHealth * bondMultiplier);
            battleStats.health = battleStats.maxHealth;
            battleStats.maxEnergy = Mathf.RoundToInt(baseEnergy * bondMultiplier);
            battleStats.energy = battleStats.maxEnergy;
            battleStats.attack = Mathf.RoundToInt(baseAttack * bondMultiplier);
            battleStats.defense = Mathf.RoundToInt(baseDefense * bondMultiplier);
            battleStats.speed = Mathf.RoundToInt(baseSpeed * bondMultiplier);

            // Load existing battle experience if available
            if (data.ContainsKey("battle_stats"))
            {
                var battleData = data["battle_stats"] as Dictionary<string, object>;
                if (battleData != null)
                {
                    battleStats.battlesWon = battleData.ContainsKey("battles_won") ? Convert.ToInt32(battleData["battles_won"]) : 0;
                    battleStats.battlesLost = battleData.ContainsKey("battles_lost") ? Convert.ToInt32(battleData["battles_lost"]) : 0;
                    battleStats.damageDealt = battleData.ContainsKey("damage_dealt") ? Convert.ToInt32(battleData["damage_dealt"]) : 0;
                    battleStats.damageTaken = battleData.ContainsKey("damage_taken") ? Convert.ToInt32(battleData["damage_taken"]) : 0;
                }
            }
        }

        private int GetBaseStatForStage(string statType, string stage)
        {
            // Base stat progressions by evolution stage
            Dictionary<string, Dictionary<string, int>> stageStats = new Dictionary<string, Dictionary<string, int>>
            {
                ["egg"] = new Dictionary<string, int> { ["health"] = 50, ["energy"] = 25, ["attack"] = 5, ["defense"] = 5, ["speed"] = 5 },
                ["hatchling"] = new Dictionary<string, int> { ["health"] = 75, ["energy"] = 35, ["attack"] = 8, ["defense"] = 7, ["speed"] = 8 },
                ["juvenile"] = new Dictionary<string, int> { ["health"] = 100, ["energy"] = 50, ["attack"] = 12, ["defense"] = 10, ["speed"] = 12 },
                ["adult"] = new Dictionary<string, int> { ["health"] = 150, ["energy"] = 75, ["attack"] = 18, ["defense"] = 15, ["speed"] = 18 },
                ["elder"] = new Dictionary<string, int> { ["health"] = 200, ["energy"] = 100, ["attack"] = 25, ["defense"] = 20, ["speed"] = 25 },
                ["legendary"] = new Dictionary<string, int> { ["health"] = 300, ["energy"] = 150, ["attack"] = 35, ["defense"] = 30, ["speed"] = 35 }
            };

            if (stageStats.ContainsKey(stage) && stageStats[stage].ContainsKey(statType))
            {
                return stageStats[stage][statType];
            }

            // Default to juvenile stats
            return stageStats["juvenile"][statType];
        }

        /// <summary>
        /// Load sprite sheet from TLDA/Warbler pipeline
        /// KeeperNote: Integrates with existing ScribeImageManager for asset handling
        /// </summary>
        private void LoadSpriteSheet()
        {
            if (string.IsNullOrEmpty(spriteSheetPath))
                return;

            try
            {
                // Load sprite from Resources or AssetDatabase
                Sprite companionSprite = Resources.Load<Sprite>(spriteSheetPath);
                if (companionSprite != null && spriteRenderer != null)
                {
                    spriteRenderer.sprite = companionSprite;
                }
                else
                {
                    Debug.LogWarning($"[Companion] Could not load sprite from path: {spriteSheetPath}");
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[Companion] Error loading sprite sheet: {e.Message}");
            }
        }

        /// <summary>
        /// Execute a battle ability with Warbler personality integration
        /// KeeperNote: Core battle action with optional quip generation
        /// </summary>
        public bool UseAbility(CompanionAbility ability, Companion target = null)
        {
            if (!ability.CanUse(battleStats))
            {
                return false;
            }

            // Consume energy
            battleStats.ConsumeEnergy(ability.energyCost);

            // Apply ability effects
            float effectivePower = ability.GetEffectivePower(archetype);
            ApplyAbilityEffect(ability, effectivePower, target);

            // Trigger Warbler personality quip
            TriggerBattleQuip(ability);

            // Trigger animation if available
            if (animator != null)
            {
                animator.SetTrigger($"Use{ability.effectType}");
            }

            OnAbilityUsed?.Invoke(this, ability);

            Debug.Log($"[Companion] {companionName} used {ability.name} (Power: {effectivePower})");
            return true;
        }

        private void ApplyAbilityEffect(CompanionAbility ability, float power, Companion target)
        {
            switch (ability.effectType)
            {
                case BattleEffectType.Damage:
                    if (target != null)
                    {
                        float effectiveness = GetElementalEffectiveness(target.element);
                        int damage = Mathf.RoundToInt(power * effectiveness);
                        target.battleStats.TakeDamage(damage);
                        battleStats.damageDealt += damage;
                    }
                    break;

                case BattleEffectType.Heal:
                    battleStats.Heal(Mathf.RoundToInt(power));
                    break;

                case BattleEffectType.Buff:
                case BattleEffectType.Debuff:
                    // Apply status effect (simplified)
                    var statusEffect = new StatusEffect(
                        ability.id + "_effect",
                        ability.name + " Effect",
                        3, // Duration
                        ability.effectType,
                        power
                    );
                    
                    if (ability.targetType == TargetType.Self || ability.effectType == BattleEffectType.Buff)
                    {
                        battleStats.activeEffects.Add(statusEffect);
                    }
                    else if (target != null)
                    {
                        target.battleStats.activeEffects.Add(statusEffect);
                    }
                    break;
            }
        }

        /// <summary>
        /// Calculate elemental effectiveness against target
        /// KeeperNote: Implements rock-paper-scissors combat triangle
        /// </summary>
        public float GetElementalEffectiveness(CompanionElement targetElement)
        {
            switch (element)
            {
                case CompanionElement.Logic:
                    return targetElement == CompanionElement.Chaos ? 2.0f :
                           targetElement == CompanionElement.Creativity ? 0.5f : 1.0f;
                case CompanionElement.Creativity:
                    return targetElement == CompanionElement.Logic ? 2.0f :
                           targetElement == CompanionElement.Order ? 0.5f : 1.0f;
                case CompanionElement.Order:
                    return targetElement == CompanionElement.Creativity ? 2.0f :
                           targetElement == CompanionElement.Chaos ? 0.5f : 1.0f;
                case CompanionElement.Chaos:
                    return targetElement == CompanionElement.Order ? 2.0f :
                           targetElement == CompanionElement.Logic ? 0.5f : 1.0f;
                case CompanionElement.Balance:
                default:
                    return 1.0f; // Neutral effectiveness
            }
        }

        /// <summary>
        /// Trigger personality-driven battle quip using Warbler integration
        /// KeeperNote: Connects to Warbler conversation system for dynamic dialogue
        /// </summary>
        private void TriggerBattleQuip(CompanionAbility ability)
        {
            List<string> quipPool = ability.battleQuips;
            
            // Add context-specific quips based on battle state
            if (battleStats.healthPercentage < 0.25f && lowHealthQuips.Count > 0)
            {
                quipPool = lowHealthQuips;
            }

            if (quipPool.Count > 0)
            {
                string selectedQuip = quipPool[UnityEngine.Random.Range(0, quipPool.Count)];
                OnQuipSpoken?.Invoke(this, selectedQuip);
                
                // TODO: Integration with Warbler conversation system for dynamic quip generation
                Debug.Log($"[{companionName}]: \"{selectedQuip}\"");
            }
        }

        /// <summary>
        /// Handle companion defeat with personality response
        /// KeeperNote: Triggers evolution ceremony if conditions met
        /// </summary>
        public void OnDefeated()
        {
            if (defeatQuips.Count > 0)
            {
                string quip = defeatQuips[UnityEngine.Random.Range(0, defeatQuips.Count)];
                OnQuipSpoken?.Invoke(this, quip);
            }

            OnCompanionDefeated?.Invoke(this);
        }

        /// <summary>
        /// Handle companion victory with celebration
        /// KeeperNote: Updates battle experience and checks for evolution triggers
        /// </summary>
        public void OnVictory()
        {
            battleStats.battlesWon++;
            
            if (victoryQuips.Count > 0)
            {
                string quip = victoryQuips[UnityEngine.Random.Range(0, victoryQuips.Count)];
                OnQuipSpoken?.Invoke(this, quip);
            }

            OnCompanionVictory?.Invoke(this);

            // Check for evolution ceremony trigger
            CheckEvolutionReadiness();
        }

        private void CheckEvolutionReadiness()
        {
            // Simple evolution check - could be enhanced with narrative triggers
            bool readyForEvolution = battleStats.battlesWon > 0 && battleStats.battlesWon % 5 == 0;
            
            if (readyForEvolution)
            {
                Debug.Log($"[Companion] {companionName} is ready for evolution ceremony!");
                // TODO: Trigger evolution ceremony UI/event
            }
        }

        /// <summary>
        /// Export companion data for NFT minting integration
        /// KeeperNote: Generates battle-proven NFT metadata
        /// </summary>
        public string ExportForNFTMinting()
        {
            var nftData = new Dictionary<string, object>
            {
                ["companion_id"] = companionId,
                ["name"] = companionName,
                ["species"] = species,
                ["developer"] = developerName,
                ["element"] = element.ToString(),
                ["archetype"] = archetype.ToString(),
                ["temperament"] = temperament.ToString(),
                ["bond_level"] = bondLevel,
                ["battle_proven"] = battleStats.battlesWon > 0,
                ["victory_count"] = battleStats.battlesWon,
                ["total_battles"] = battleStats.battlesWon + battleStats.battlesLost,
                ["damage_dealt"] = battleStats.damageDealt,
                ["battle_dna"] = GenerateBattleDNA(),
                ["timestamp"] = DateTime.UtcNow.ToString("O")
            };

            return JsonConvert.SerializeObject(nftData, Formatting.Indented);
        }

        private string GenerateBattleDNA()
        {
            // Generate unique battle DNA based on performance and characteristics
            string dnaInput = $"{companionId}{battleStats.battlesWon}{battleStats.damageDealt}{element}{archetype}{temperament}";
            return Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes(dnaInput)).Substring(0, 16);
        }
    }
}