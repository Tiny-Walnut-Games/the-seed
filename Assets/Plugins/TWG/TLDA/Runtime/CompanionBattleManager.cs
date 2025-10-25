using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace LivingDevAgent.Runtime.CompanionBattler
{
    /// <summary>
    /// Main battle manager handling turn-based tactical combat
    /// KeeperNote: Core battle loop with energy/turn system and synergy combos
    /// </summary>
    public class CompanionBattleManager : MonoBehaviour
    {
        [Header("Battle Configuration")]
        [SerializeField] private bool isTurnBased = true;
        [SerializeField] private float turnDuration = 30f;
        [SerializeField] private int maxTeamSize = 3;

        [Header("Teams")]
        [SerializeField] private List<Companion> playerTeam = new();
        [SerializeField] private List<Companion> enemyTeam = new();

        [Header("UI References")]
        [SerializeField] private CompanionBattleUI battleUI;
        [SerializeField] private Transform playerTeamContainer;
        [SerializeField] private Transform enemyTeamContainer;

        // Battle state
        private BattlePhase currentPhase = BattlePhase.Preparation;
        private int currentTurn = 0;
        private Companion activeCompanion;
        private readonly Queue<Companion> turnQueue = new();
        private float turnTimer = 0f;

        // Battle events
        public event Action<BattlePhase> OnPhaseChanged;
        public event Action<Companion> OnTurnStarted;
        public event Action<Companion> OnTurnEnded;
        public event Action<List<Companion>> OnBattleEnded;

        public enum BattlePhase
        {
            Preparation,
            Battle,
            Resolution,
            Complete
        }

        private void Start()
        {
            InitializeBattle();
        }

        private void Update()
        {
            if (currentPhase == BattlePhase.Battle)
            {
                UpdateBattlePhase();
            }
        }

        /// <summary>
        /// Initialize battle with team setup and turn order
        /// KeeperNote: Handles companion positioning and battle preparation
        /// </summary>
        public void InitializeBattle()
        {
            currentPhase = BattlePhase.Preparation;
            currentTurn = 0;
            turnTimer = 0f;

            // Setup companion positions
            SetupTeamPositions();

            // Calculate turn order based on speed stats
            CalculateTurnOrder();

            // Subscribe to companion events
            SubscribeToCompanionEvents();

            // Initialize UI
            if (battleUI != null)
            {
                battleUI.InitializeBattleUI(playerTeam, enemyTeam);
            }

            Debug.Log($"[BattleManager] Battle initialized - Player: {playerTeam.Count}, Enemy: {enemyTeam.Count}");
        }

        private void SetupTeamPositions()
        {
            // Position player team
            for (int i = 0; i < playerTeam.Count; i++)
            {
                if (playerTeam[i] != null && playerTeamContainer != null)
                {
                    Vector3 position = playerTeamContainer.position + Vector3.right * (i * 2f);
                    playerTeam[i].transform.position = position;
                    playerTeam[i].transform.SetParent(playerTeamContainer);
                }
            }

            // Position enemy team
            for (int i = 0; i < enemyTeam.Count; i++)
            {
                if (enemyTeam[i] != null && enemyTeamContainer != null)
                {
                    Vector3 position = enemyTeamContainer.position + Vector3.right * (i * 2f);
                    enemyTeam[i].transform.position = position;
                    enemyTeam[i].transform.SetParent(enemyTeamContainer);
                }
            }
        }

        private void CalculateTurnOrder()
        {
            turnQueue.Clear();

            // Combine all living companions and sort by speed
            List<Companion> allCompanions = new();
            allCompanions.AddRange(playerTeam.FindAll(c => c.IsAlive));
            allCompanions.AddRange(enemyTeam.FindAll(c => c.IsAlive));

            allCompanions.Sort((a, b) => b.BattleStats.speed.CompareTo(a.BattleStats.speed));

            foreach (var companion in allCompanions)
            {
                turnQueue.Enqueue(companion);
            }

            Debug.Log($"[BattleManager] Turn order calculated - {turnQueue.Count} active companions");
        }

        private void SubscribeToCompanionEvents()
        {
            foreach (var companion in playerTeam)
            {
                if (companion != null)
                {
                    companion.OnCompanionDefeated += OnCompanionDefeated;
                    companion.OnCompanionVictory += OnCompanionVictory;
                    companion.OnAbilityUsed += OnAbilityUsed;
                    companion.OnQuipSpoken += OnQuipSpoken;
                }
            }

            foreach (var companion in enemyTeam)
            {
                if (companion != null)
                {
                    companion.OnCompanionDefeated += OnCompanionDefeated;
                    companion.OnCompanionVictory += OnCompanionVictory;
                    companion.OnAbilityUsed += OnAbilityUsed;
                    companion.OnQuipSpoken += OnQuipSpoken;
                }
            }
        }

        /// <summary>
        /// Start the battle phase with turn-based combat
        /// KeeperNote: Begins tactical combat loop
        /// </summary>
        public void StartBattle()
        {
            if (currentPhase != BattlePhase.Preparation)
                return;

            currentPhase = BattlePhase.Battle;
            OnPhaseChanged?.Invoke(currentPhase);

            if (turnQueue.Count > 0)
            {
                StartNextTurn();
            }

            Debug.Log("[BattleManager] Battle started!");
        }

        private void UpdateBattlePhase()
        {
            if (isTurnBased)
            {
                UpdateTurnBasedBattle();
            }
            else
            {
                UpdateRealTimeBattle();
            }
        }

        private void UpdateTurnBasedBattle()
        {
            if (activeCompanion == null)
                return;

            turnTimer += Time.deltaTime;

            // Auto-end turn if time expires
            if (turnTimer >= turnDuration)
            {
                EndCurrentTurn();
            }

            // Check for battle end conditions
            CheckBattleEndConditions();
        }

        private void UpdateRealTimeBattle()
        {
            // Real-time battle logic - energy regeneration, auto-abilities, etc.
            foreach (var companion in GetAllLivingCompanions())
            {
                // Regenerate energy over time
                companion.BattleStats.RestoreEnergy(1);

                // Process status effects
                ProcessStatusEffects(companion);
            }

            CheckBattleEndConditions();
        }

        private void StartNextTurn()
        {
            if (turnQueue.Count == 0)
            {
                // Recalculate turn order for next round
                CalculateTurnOrder();
                currentTurn++;
            }

            if (turnQueue.Count > 0)
            {
                activeCompanion = turnQueue.Dequeue();
                turnTimer = 0f;

                OnTurnStarted?.Invoke(activeCompanion);

                // Handle AI turn for enemy companions
                if (enemyTeam.Contains(activeCompanion))
                {
                    StartCoroutine(HandleAITurn(activeCompanion));
                }
                else
                {
                    // Player turn - enable UI controls
                    if (battleUI != null)
                    {
                        battleUI.EnablePlayerControls(activeCompanion);
                    }
                }

                Debug.Log($"[BattleManager] Turn {currentTurn}: {activeCompanion.Name}'s turn");
            }
        }

        private void EndCurrentTurn()
        {
            if (activeCompanion == null)
                return;

            OnTurnEnded?.Invoke(activeCompanion);

            // Process end-of-turn effects
            ProcessStatusEffects(activeCompanion);

            // Restore some energy
            activeCompanion.BattleStats.RestoreEnergy(10);

            activeCompanion = null;
            StartNextTurn();
        }

        /// <summary>
        /// Handle AI companion turn with temperament-based behavior
        /// KeeperNote: AI uses companion temperament to guide decision making
        /// </summary>
        private IEnumerator HandleAITurn(Companion aiCompanion)
        {
            yield return new WaitForSeconds(1f); // Brief pause for visibility

            // Select action based on temperament
            CompanionAbility selectedAbility = SelectAIAbility(aiCompanion);
            Companion target = SelectAITarget(aiCompanion, selectedAbility);

            if (selectedAbility != null)
            {
                aiCompanion.UseAbility(selectedAbility, target);
                yield return new WaitForSeconds(1.5f); // Animation/effect time
            }

            EndCurrentTurn();
        }

        private CompanionAbility SelectAIAbility(Companion aiCompanion)
        {
            var usableAbilities = aiCompanion.Abilities.FindAll(a => a.CanUse(aiCompanion.BattleStats));
            
            if (usableAbilities.Count == 0)
                return null;

            // Select based on temperament
            switch (aiCompanion.Temperament)
            {
                case CompanionTemperament.Aggressive:
                    return usableAbilities.Find(a => a.effectType == BattleEffectType.Damage) ?? usableAbilities[0];
                
                case CompanionTemperament.Defensive:
                    if (aiCompanion.BattleStats.HealthPercentage < 0.5f)
                        return usableAbilities.Find(a => a.effectType == BattleEffectType.Heal) ?? usableAbilities[0];
                    return usableAbilities.Find(a => a.effectType == BattleEffectType.Buff) ?? usableAbilities[0];
                
                case CompanionTemperament.Tactical:
                    return usableAbilities.Find(a => a.effectType == BattleEffectType.Debuff || a.effectType == BattleEffectType.Status) ?? usableAbilities[0];
                
                case CompanionTemperament.Loyal:
                    // Prioritize helping teammates
                    var ally = GetWeakestAlly(aiCompanion);
                    if (ally != null && ally.BattleStats.HealthPercentage < 0.6f)
                        return usableAbilities.Find(a => a.effectType == BattleEffectType.Heal || a.effectType == BattleEffectType.Buff) ?? usableAbilities[0];
                    break;
                
                case CompanionTemperament.Intuitive:
                default:
                    return usableAbilities[UnityEngine.Random.Range(0, usableAbilities.Count)];
            }

            return usableAbilities[0];
        }

        private Companion SelectAITarget(Companion aiCompanion, CompanionAbility ability)
        {
            if (ability == null)
                return null;

            switch (ability.targetType)
            {
                case TargetType.Self:
                    return aiCompanion;
                
                case TargetType.Ally:
                    return GetWeakestAlly(aiCompanion);
                
                case TargetType.Enemy:
                    var enemies = IsPlayerTeamMember(aiCompanion) ? enemyTeam : playerTeam;
                    var livingEnemies = enemies.FindAll(e => e.IsAlive);
                    return livingEnemies.Count > 0 ? livingEnemies[UnityEngine.Random.Range(0, livingEnemies.Count)] : null;
                
                default:
                    return null;
            }
        }

        private Companion GetWeakestAlly(Companion companion)
        {
            var allies = IsPlayerTeamMember(companion) ? playerTeam : enemyTeam;
            var livingAllies = allies.FindAll(a => a.IsAlive && a != companion);
            
            if (livingAllies.Count == 0)
                return null;

            livingAllies.Sort((a, b) => a.BattleStats.HealthPercentage.CompareTo(b.BattleStats.HealthPercentage));
            return livingAllies[0];
        }

        private bool IsPlayerTeamMember(Companion companion)
        {
            return playerTeam.Contains(companion);
        }

        private void ProcessStatusEffects(Companion companion)
        {
            for (int i = companion.BattleStats.activeEffects.Count - 1; i >= 0; i--)
            {
                var effect = companion.BattleStats.activeEffects[i];
                
                // Apply effect
                switch (effect.effectType)
                {
                    case BattleEffectType.Damage:
                        companion.BattleStats.TakeDamage(Mathf.RoundToInt(effect.magnitude));
                        break;
                    case BattleEffectType.Heal:
                        companion.BattleStats.Heal(Mathf.RoundToInt(effect.magnitude));
                        break;
                }

                // Tick duration
                effect.Tick();

                // Remove expired effects
                if (effect.IsExpired)
                {
                    companion.BattleStats.activeEffects.RemoveAt(i);
                }
            }
        }

        private void CheckBattleEndConditions()
        {
            bool playerTeamAlive = playerTeam.Exists(c => c.IsAlive);
            bool enemyTeamAlive = enemyTeam.Exists(c => c.IsAlive);

            if (!playerTeamAlive || !enemyTeamAlive)
            {
                EndBattle(playerTeamAlive ? playerTeam : enemyTeam);
            }
        }

        private void EndBattle(List<Companion> winners)
        {
            currentPhase = BattlePhase.Complete;
            OnPhaseChanged?.Invoke(currentPhase);

            // Award victory to winners
            foreach (var winner in winners)
            {
                if (winner.IsAlive)
                {
                    winner.OnVictory();
                }
            }

            OnBattleEnded?.Invoke(winners);

            Debug.Log($"[BattleManager] Battle ended! Winners: {string.Join(", ", winners.ConvertAll(w => w.Name))}");
        }

        private List<Companion> GetAllLivingCompanions()
        {
            var living = new List<Companion>();
            living.AddRange(playerTeam.FindAll(c => c.IsAlive));
            living.AddRange(enemyTeam.FindAll(c => c.IsAlive));
            return living;
        }

        // Event handlers
        private void OnCompanionDefeated(Companion companion)
        {
            Debug.Log($"[BattleManager] {companion.Name} was defeated!");
            
            if (battleUI != null)
            {
                battleUI.UpdateCompanionStatus(companion);
            }
        }

        private void OnCompanionVictory(Companion companion)
        {
            Debug.Log($"[BattleManager] {companion.Name} achieved victory!");
        }

        private void OnAbilityUsed(Companion user, CompanionAbility ability)
        {
            Debug.Log($"[BattleManager] {user.Name} used {ability.name}");
            
            if (battleUI != null)
            {
                battleUI.ShowAbilityEffect(user, ability);
            }
        }

        private void OnQuipSpoken(Companion speaker, string quip)
        {
            Debug.Log($"[BattleManager] {speaker.Name}: \"{quip}\"");
            
            if (battleUI != null)
            {
                battleUI.ShowBattleQuip(speaker, quip);
            }
        }

        // Public interface methods
        public void AddToPlayerTeam(Companion companion)
        {
            if (playerTeam.Count < maxTeamSize && !playerTeam.Contains(companion))
            {
                playerTeam.Add(companion);
                Debug.Log($"[BattleManager] Added {companion.Name} to player team");
            }
        }

        public void AddToEnemyTeam(Companion companion)
        {
            if (enemyTeam.Count < maxTeamSize && !enemyTeam.Contains(companion))
            {
                enemyTeam.Add(companion);
                Debug.Log($"[BattleManager] Added {companion.Name} to enemy team");
            }
        }

        public void UsePlayerAbility(CompanionAbility ability, Companion target)
        {
            if (activeCompanion != null && playerTeam.Contains(activeCompanion))
            {
                if (activeCompanion.UseAbility(ability, target))
                {
                    EndCurrentTurn();
                }
            }
        }
    }
}
