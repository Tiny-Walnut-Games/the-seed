using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace TWG.Seed.Platform
{
    /// <summary>
    /// Interface for cross-platform integration with major gaming ecosystems
    /// Bridges platform-specific APIs to The Seed's Fractal-Chain system
    /// </summary>
    public interface IPlatformBridge
    {
        Platform PlatformType { get; }
        bool IsInitialized { get; }

        // Authentication
        Task<PlatformUserIdentity> AuthenticateUser();
        Task<bool> ValidateSession();
        Task SignOutUser();

        // User Data
        Task<PlatformInventory> GetUserInventory();
        Task<PlatformAchievements> GetAchievements();
        Task<PlatformFriends> GetSocialGraph();
        Task<PlatformStats> GetPlayerStats();

        // Narrative Integration
        Task<bool> RegisterNarrativeCompanion(string companionId, NarrativeCompanionData companion);
        Task<bool> UpdateNarrativeProgress(string companionId, NarrativeProgress progress);
        Task<List<NarrativeCompanionData>> GetNarrativeCompanions();

        // Store Integration
        Task<List<PlatformStoreItem>> GetStoreItems();
        Task<bool> PurchaseItem(string itemId);
        Task<bool> ConsumeItem(string itemId);

        // Events
        event Action<PlatformEvent> OnPlatformEvent;
        event Action<NarrativeEvent> OnNarrativeEvent;
    }

    public enum Platform
    {
        Steam,
        EpicGames,
        XboxLive,
        NintendoSwitch,
        UnityGamingServices,
        Standalone
    }

    public class PlatformUserIdentity
    {
        public string PlatformUserId { get; set; } = string.Empty;
        public string Username { get; set; } = string.Empty;
        public string DisplayName { get; set; } = string.Empty;
        public string AvatarUrl { get; set; } = string.Empty;
        public string CountryCode { get; set; } = string.Empty;
        public DateTime SessionStart { get; set; }
        public Dictionary<string, object> PlatformSpecificData { get; set; } = new Dictionary<string, object>();
    }

    public class PlatformInventory
    {
        public List<InventoryItem> Items { get; set; } = new List<InventoryItem>();
        public int MaxSlots { get; set; }
        public int UsedSlots { get; set; }
        public string Currency { get; set; } = string.Empty;
        public decimal Balance { get; set; }
    }

    public class InventoryItem
    {
        public string ItemId { get; set; } = string.Empty;
        public string ItemName { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public int Quantity { get; set; }
        public string ItemType { get; set; } = string.Empty;
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
        public DateTime AcquiredDate { get; set; }
        public string Stat7Address { get; set; } = string.Empty; // Fractal-Chain address
    }

    public class PlatformAchievements
    {
        public List<Achievement> UnlockedAchievements { get; set; } = new List<Achievement>();
        public List<Achievement> LockedAchievements { get; set; } = new List<Achievement>();
        public int TotalAchievements { get; set; }
        public int UnlockedCount { get; set; }
        public float CompletionPercentage { get; set; }
    }

    public class Achievement
    {
        public string AchievementId { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public bool IsUnlocked { get; set; }
        public DateTime? UnlockDate { get; set; }
        public float Progress { get; set; }
        public string IconUrl { get; set; } = string.Empty;
        public int Points { get; set; }
        public string Stat7Address { get; set; } = string.Empty;
        public NarrativeStory AchievementStory { get; set; }
    }

    public class NarrativeStory
    {
        public string Title { get; set; } = string.Empty;
        public string Content { get; set; } = string.Empty;
        public string Theme { get; set; } = string.Empty;
        public List<string> RelatedEntities { get; set; } = new List<string>();
        public string Stat7Address { get; set; } = string.Empty;
    }

    public class PlatformFriends
    {
        public List<Friend> Friends { get; set; } = new List<Friend>();
        public List<FriendRequest> PendingRequests { get; set; } = new List<FriendRequest>();
        public int MaxFriends { get; set; }
    }

    public class Friend
    {
        public string FriendId { get; set; } = string.Empty;
        public string Username { get; set; } = string.Empty;
        public string DisplayName { get; set; } = string.Empty;
        public FriendStatus Status { get; set; }
        public DateTime? LastSeen { get; set; }
        public string CurrentGame { get; set; } = string.Empty;
        public List<SharedNarrative> SharedNarratives { get; set; } = new List<SharedNarrative>();
    }

    public enum FriendStatus
    {
        Offline,
        Online,
        Away,
        Busy,
        InGame
    }

    public class SharedNarrative
    {
        public string NarrativeId { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public DateTime SharedDate { get; set; }
        public string Stat7Address { get; set; } = string.Empty;
    }

    public class FriendRequest
    {
        public string RequestId { get; set; } = string.Empty;
        public string FromUserId { get; set; } = string.Empty;
        public string FromUsername { get; set; } = string.Empty;
        public DateTime RequestDate { get; set; }
        public string Message { get; set; } = string.Empty;
    }

    public class PlatformStats
    {
        public TimeSpan TotalPlayTime { get; set; }
        public int SessionsPlayed { get; set; }
        public DateTime LastSession { get; set; }
        public Dictionary<string, double> GameStats { get; set; } = new Dictionary<string, double>();
        public List<NarrativeStat> NarrativeStats { get; set; } = new List<NarrativeStat>();
    }

    public class NarrativeStat
    {
        public string StatName { get; set; } = string.Empty;
        public double Value { get; set; }
        public string Stat7Address { get; set; } = string.Empty;
        public DateTime LastUpdated { get; set; }
    }

    public class NarrativeCompanionData
    {
        public string CompanionId { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Species { get; set; } = string.Empty;
        public string Personality { get; set; } = string.Empty;
        public int Level { get; set; }
        public double Experience { get; set; }
        public string Stat7Address { get; set; } = string.Empty;
        public List<string> Abilities { get; set; } = new List<string>();
        public Dictionary<string, object> Appearance { get; set; } = new Dictionary<string, object>();
        public NarrativeCore Narrative { get; set; }
        public DateTime CreatedDate { get; set; }
        public DateTime LastInteraction { get; set; }
    }

    public class NarrativeCore
    {
        public string CoreTheme { get; set; } = string.Empty;
        public string Backstory { get; set; } = string.Empty;
        public List<string> MemoryFragments { get; set; } = new List<string>();
        public string CurrentMood { get; set; } = string.Empty;
        public List<NarrativeGoal> Goals { get; set; } = new List<NarrativeGoal>();
    }

    public class NarrativeGoal
    {
        public string GoalId { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public bool IsCompleted { get; set; }
        public double Progress { get; set; }
        public string Stat7Address { get; set; } = string.Empty;
    }

    public class NarrativeProgress
    {
        public string CompanionId { get; set; } = string.Empty;
        public double ExperienceGained { get; set; }
        public string NewAbility { get; set; } = string.Empty;
        public string MemoryFragment { get; set; } = string.Empty;
        public string MoodChange { get; set; } = string.Empty;
        public Dictionary<string, object> CustomData { get; set; } = new Dictionary<string, object>();
    }

    public class PlatformStoreItem
    {
        public string ItemId { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public decimal Price { get; set; }
        public string Currency { get; set; } = string.Empty;
        public string ItemType { get; set; } = string.Empty;
        public string IconUrl { get; set; } = string.Empty;
        public bool IsConsumable { get; set; }
        public Dictionary<string, object> PlatformSpecificData { get; set; } = new Dictionary<string, object>();
        public string Stat7Address { get; set; } = string.Empty;
    }

    public class PlatformEvent
    {
        public string EventType { get; set; } = string.Empty;
        public DateTime Timestamp { get; set; }
        public Dictionary<string, object> Data { get; set; } = new Dictionary<string, object>();
        public string UserId { get; set; } = string.Empty;
    }

    public class NarrativeEvent
    {
        public string EventType { get; set; } = string.Empty;
        public string EntityId { get; set; } = string.Empty;
        public string Stat7Address { get; set; } = string.Empty;
        public DateTime Timestamp { get; set; }
        public Dictionary<string, object> Data { get; set; } = new Dictionary<string, object>();
    }
}
