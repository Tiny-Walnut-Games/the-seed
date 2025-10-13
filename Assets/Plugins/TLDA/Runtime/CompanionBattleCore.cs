using System;
using System.Collections.Generic;
using UnityEngine;

namespace LivingDevAgent.Runtime.CompanionBattler
{
    /// <summary>
    /// Companion battle semantics - element, archetype, temperament
    /// KeeperNote: Core semantic DNA that defines companion battle behavior
    /// </summary>
    [Serializable]
    public enum CompanionElement
    {
        Logic,      // Strong vs Chaos, weak vs Creativity
        Creativity, // Strong vs Logic, weak vs Order  
        Order,      // Strong vs Creativity, weak vs Chaos
        Chaos,      // Strong vs Order, weak vs Logic
        Balance     // Neutral against all
    }

    [Serializable]
    public enum CompanionArchetype
    {
        Guardian,   // High defense, protective abilities
        Striker,    // High attack, damage-focused
        Support,    // Healing and buff abilities
        Controller, // Status effects and manipulation
        Hybrid      // Balanced stats and flexible abilities
    }

    [Serializable]
    public enum CompanionTemperament
    {
        Aggressive, // Prefers offensive actions
        Defensive,  // Prefers protective actions
        Tactical,   // Prefers strategic moves
        Intuitive,  // Unpredictable creative actions
        Loyal       // Team-focused supportive actions
    }

    [Serializable]
    public enum BattleEffectType
    {
        Damage,
        Heal,
        Buff,
        Debuff,
        Status,
        Synergy
    }

    [Serializable]
    public enum TargetType
    {
        Self,
        Ally,
        Enemy,
        AllAllies,
        AllEnemies,
        All
    }

    /// <summary>
    /// Companion battle statistics and performance tracking
    /// KeeperNote: Integrates with existing badge pet XP system
    /// </summary>
    [Serializable]
    public class CompanionBattleStats
    {
        [Header("Core Stats")]
        public int health = 100;
        public int maxHealth = 100;
        public int energy = 50;
        public int maxEnergy = 50;
        public int attack = 10;
        public int defense = 10;
        public int speed = 10;

        [Header("Battle Experience")]
        public int battlesWon = 0;
        public int battlesLost = 0;
        public int damageDealt = 0;
        public int damageTaken = 0;

        [Header("Status")]
        public List<StatusEffect> activeEffects = new List<StatusEffect>();
        public bool isAlive => health > 0;
        public float healthPercentage => maxHealth > 0 ? (float)health / maxHealth : 0f;
        public float energyPercentage => maxEnergy > 0 ? (float)energy / maxEnergy : 0f;

        public void TakeDamage(int damage)
        {
            int actualDamage = Mathf.Max(1, damage - defense);
            health = Mathf.Max(0, health - actualDamage);
            damageTaken += actualDamage;
        }

        public void Heal(int amount)
        {
            health = Mathf.Min(maxHealth, health + amount);
        }

        public bool ConsumeEnergy(int amount)
        {
            if (energy >= amount)
            {
                energy -= amount;
                return true;
            }
            return false;
        }

        public void RestoreEnergy(int amount)
        {
            energy = Mathf.Min(maxEnergy, energy + amount);
        }
    }

    /// <summary>
    /// Status effect system for battles
    /// KeeperNote: Enables tactical depth and archetype synergies
    /// </summary>
    [Serializable]
    public class StatusEffect
    {
        public string id;
        public string name;
        public int duration;
        public BattleEffectType effectType;
        public float magnitude;
        public int stacks = 1;

        public StatusEffect(string id, string name, int duration, BattleEffectType type, float magnitude)
        {
            this.id = id;
            this.name = name;
            this.duration = duration;
            this.effectType = type;
            this.magnitude = magnitude;
        }

        public void Tick()
        {
            duration = Mathf.Max(0, duration - 1);
        }

        public bool IsExpired => duration <= 0;
    }

    /// <summary>
    /// Companion ability definition
    /// KeeperNote: Integrates with Warbler for personality-driven battle quips
    /// </summary>
    [Serializable]
    public class CompanionAbility
    {
        [Header("Basic Info")]
        public string id;
        public string name;
        public string description;
        public Sprite icon;

        [Header("Battle Mechanics")]
        public int energyCost = 10;
        public int cooldown = 0;
        public BattleEffectType effectType = BattleEffectType.Damage;
        public TargetType targetType = TargetType.Enemy;
        public float basePower = 10f;
        public float archetypeBonus = 1.0f;

        [Header("Warbler Integration")]
        public List<string> battleQuips = new List<string>();

        public bool CanUse(CompanionBattleStats stats)
        {
            return stats.energy >= energyCost && cooldown <= 0;
        }

        public float GetEffectivePower(CompanionArchetype userArchetype)
        {
            // Apply archetype bonus if ability matches companion's role
            return basePower * (ShouldApplyArchetypeBonus(userArchetype) ? archetypeBonus : 1.0f);
        }

        private bool ShouldApplyArchetypeBonus(CompanionArchetype archetype)
        {
            // Simplified archetype-ability matching
            switch (effectType)
            {
                case BattleEffectType.Damage:
                    return archetype == CompanionArchetype.Striker;
                case BattleEffectType.Heal:
                case BattleEffectType.Buff:
                    return archetype == CompanionArchetype.Support;
                case BattleEffectType.Debuff:
                case BattleEffectType.Status:
                    return archetype == CompanionArchetype.Controller;
                default:
                    return archetype == CompanionArchetype.Hybrid;
            }
        }
    }
}