using System;

namespace TWG.TLDA.SpriteForge
{
    /// <summary>
    /// Genre styles for sprite generation
    /// KeeperNote: Four canonical genres from the TLDA mythos
    /// </summary>
    public enum GenreStyle
    {
        Mythic,      // Special genre for Faculty ultra-rares
        SciFi,       // Technological, cybernetic aesthetics
        Fantasy,     // Magical, medieval aesthetics
        Steampunk,   // Brass, gears, Victorian aesthetics
        Cyberpunk    // Neon, digital, dystopian aesthetics
    }

    /// <summary>
    /// Creature archetypes across all genres
    /// KeeperNote: Base forms that adapt to genre styling
    /// </summary>
    public enum CreatureArchetype
    {
        Familiar,    // Small companion creatures
        Golem,       // Constructed beings
        Homunculus,  // Artificial life forms
        Sentinel,    // Guardian entities
        Wisp,        // Energy-based beings
        Automaton,   // Mechanical constructs
        Drifter,     // Wandering spirits
        Warder       // Protective guardians
    }

    /// <summary>
    /// Faculty roles for ultra-rare 1/1 tokens
    /// KeeperNote: Each Faculty member gets one unique token
    /// </summary>
    public enum FacultyRole
    {
        None,        // Not a Faculty token
        Warbler,     // Song and echo specialist
        Creator,     // Apex 1/1 with multi-phase animation
        Sentinel,    // Guardian and protector
        Archivist,   // Knowledge keeper
        Wrangler,    // Beast master
        Scribe,      // Documentation specialist
        Oracle,      // Future sight advisor
        Keeper       // Vault guardian
    }

    /// <summary>
    /// Animation sets for sprite sheets
    /// KeeperNote: Standard animation patterns across all creatures
    /// </summary>
    public enum AnimationSet
    {
        Idle,        // Basic standing/floating animation
        Walk,        // Movement animation
        Cast,        // Action/casting animation
        Emote,       // Emotional expression
        Ambient      // Environmental effects (locations only)
    }

    /// <summary>
    /// Evolution stages for creature development
    /// KeeperNote: Mirrors the pet system evolution stages
    /// </summary>
    public enum EvolutionStage
    {
        Egg,         // Initial form (0 XP)
        Hatchling,   // First evolution (0-500 XP)
        Juvenile,    // Second evolution (500-1500 XP)
        Adult,       // Third evolution (1500-5000 XP)
        Elder,       // Fourth evolution (5000-15000 XP)
        Legendary    // Final evolution (15000+ XP, NFT ready)
    }

    /// <summary>
    /// Token rarity tiers
    /// KeeperNote: Affects supply limits and special effects
    /// </summary>
    public enum RarityTier
    {
        OneOfOne,    // Faculty and Creator ultra-rares (supply = 1)
        Legendary,   // Supply = 4
        Epic,        // Supply = 16
        Rare,        // Supply = 64
        Uncommon,    // Supply = 256
        Common       // Supply = 512
    }
}