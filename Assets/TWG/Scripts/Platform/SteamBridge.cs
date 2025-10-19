using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;

namespace TWG.Seed.Platform
{
    /// <summary>
    /// Steam platform bridge implementation
    /// Integrates Steamworks API with The Seed's Fractal-Chain system
    /// </summary>
    public class SteamBridge : IPlatformBridge
    {
        public Platform PlatformType => Platform.Steam;
        public bool IsInitialized { get; private set; }

        public event Action<PlatformEvent> OnPlatformEvent;
        public event Action<NarrativeEvent> OnNarrativeEvent;

        private Steamworks.Callback<Steamworks.UserStatsReceived_t> userStatsCallback;
        private Steamworks.Callback<Steamworks.UserAchievementStored_t> achievementCallback;
        private Steamworks.Callback<Steamworks.GameOverlayActivated_t> overlayCallback;

        public async Task<bool> Initialize()
        {
            try
            {
                // Initialize Steamworks
                if (!Steamworks.SteamAPI.Init())
                {
                    Debug.LogError("SteamAPI initialization failed");
                    return false;
                }

                // Setup callbacks
                SetupCallbacks();

                IsInitialized = true;
                Debug.Log("Steam bridge initialized successfully");

                // Sync initial data
                await SyncSteamDataToSeed();

                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Steam initialization error: {ex.Message}");
                return false;
            }
        }

        void SetupCallbacks()
        {
            userStatsCallback = Steamworks.Callback<Steamworks.UserStatsReceived_t>.Create(OnUserStatsReceived);
            achievementCallback = Steamworks.Callback<Steamworks.UserAchievementStored_t>.Create(OnAchievementStored);
            overlayCallback = Steamworks.Callback<Steamworks.GameOverlayActivated_t>.Create(OnOverlayActivated);
        }

        void OnUserStatsReceived(Steamworks.UserStatsReceived_t callback)
        {
            if (callback.m_nGameID == Steamworks.SteamUtils.GetAppID())
            {
                _ = Task.Run(async () => await SyncSteamDataToSeed());
            }
        }

        void OnAchievementStored(Steamworks.UserAchievementStored_t callback)
        {
            _ = Task.Run(async () =>
            {
                var achievement = await GetAchievementById(callback.m_nGameProgress);
                if (achievement != null)
                {
                    await RegisterAchievementAsNarrative(achievement);
                }
            });
        }

        void OnOverlayActivated(Steamworks.GameOverlayActivated_t callback)
        {
            OnPlatformEvent?.Invoke(new PlatformEvent
            {
                EventType = "OverlayActivated",
                Timestamp = DateTime.UtcNow,
                Data = new Dictionary<string, object>
                {
                    ["active"] = callback.m_bActive > 0
                }
            });
        }

        public async Task<PlatformUserIdentity> AuthenticateUser()
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            var steamId = Steamworks.SteamUser.GetSteamID();
            var personaName = Steamworks.SteamFriends.GetPersonaName();

            return new PlatformUserIdentity
            {
                PlatformUserId = steamId.m_SteamID.ToString(),
                Username = personaName,
                DisplayName = personaName,
                AvatarUrl = GetSteamAvatarUrl(steamId),
                CountryCode = Steamworks.SteamUtils.GetIPCountry(),
                SessionStart = DateTime.UtcNow,
                PlatformSpecificData = new Dictionary<string, object>
                {
                    ["steamId64"] = steamId.m_SteamID,
                    ["personaState"] = Steamworks.SteamFriends.GetPersonaState().ToString()
                }
            };
        }

        public Task<bool> ValidateSession()
        {
            if (!IsInitialized)
                return Task.FromResult(false);

            var isValid = Steamworks.SteamUser.BLoggedOn();
            return Task.FromResult(isValid);
        }

        public Task SignOutUser()
        {
            // Steam doesn't have explicit sign out - just disable
            IsInitialized = false;
            return Task.CompletedTask;
        }

        public async Task<PlatformInventory> GetUserInventory()
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            var inventory = new PlatformInventory
            {
                Items = new List<InventoryItem>(),
                MaxSlots = 1000,
                UsedSlots = 0,
                Currency = "USD",
                Balance = await GetSteamWalletBalance()
            };

            // Get Steam inventory items
            var steamInventory = Steamworks.SteamInventory();
            if (steamInventory != null)
            {
                // This would need proper Steam inventory implementation
                // For now, add some mock items with STAT7 addresses
                inventory.Items.AddRange(await ConvertSteamItemsToSeedEntities());
            }

            inventory.UsedSlots = inventory.Items.Count;
            return inventory;
        }

        public async Task<PlatformAchievements> GetAchievements()
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            var achievements = new PlatformAchievements
            {
                UnlockedAchievements = new List<Achievement>(),
                LockedAchievements = new List<Achievement>()
            };

            // Get Steam achievements
            var steamAchievements = await GetSteamAchievements();
            foreach (var steamAchievement in steamAchievements)
            {
                var achievement = new Achievement
                {
                    AchievementId = steamAchievement.Key,
                    Name = steamAchievement.Value.Name,
                    Description = steamAchievement.Value.Description,
                    IsUnlocked = steamAchievement.Value.IsUnlocked,
                    UnlockDate = steamAchievement.Value.UnlockTime,
                    Progress = steamAchievement.Value.Progress,
                    IconUrl = steamAchievement.Value.IconUrl,
                    Points = steamAchievement.Value.Points,
                    Stat7Address = GenerateStat7AddressForAchievement(steamAchievement.Key),
                    AchievementStory = await GenerateAchievementStory(steamAchievement.Value)
                };

                if (achievement.IsUnlocked)
                {
                    achievements.UnlockedAchievements.Add(achievement);
                }
                else
                {
                    achievements.LockedAchievements.Add(achievement);
                }
            }

            achievements.TotalAchievements = achievements.UnlockedAchievements.Count + achievements.LockedAchievements.Count;
            achievements.UnlockedCount = achievements.UnlockedAchievements.Count;
            achievements.CompletionPercentage = achievements.TotalAchievements > 0
                ? (float)achievements.UnlockedCount / achievements.TotalAchievements * 100f
                : 0f;

            return achievements;
        }

        public async Task<PlatformFriends> GetSocialGraph()
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            var friends = new PlatformFriends
            {
                Friends = new List<Friend>(),
                PendingRequests = new List<FriendRequest>(),
                MaxFriends = Steamworks.SteamFriends.GetMaxFriends()
            };

            // Get Steam friends
            var friendCount = Steamworks.SteamFriends.GetFriendCount(Steamworks.EFriendFlags.k_EFriendFlagAll);
            for (int i = 0; i < friendCount; i++)
            {
                var steamId = Steamworks.SteamFriends.GetFriendByIndex(i, Steamworks.EFriendFlags.k_EFriendFlagAll);
                var friend = await ConvertSteamFriendToFriend(steamId);
                if (friend != null)
                {
                    friends.Friends.Add(friend);
                }
            }

            return friends;
        }

        public async Task<PlatformStats> GetPlayerStats()
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            var stats = new PlatformStats
            {
                GameStats = new Dictionary<string, double>(),
                NarrativeStats = new List<NarrativeStat>()
            };

            // Get Steam stats
            Steamworks.SteamUserStats.RequestCurrentStats();

            // Example stats - would need proper implementation
            stats.TotalPlayTime = TimeSpan.FromHours(Steamworks.SteamUserStats.GetStatFloat("total_play_hours"));
            stats.SessionsPlayed = (int)Steamworks.SteamUserStats.GetStatInt("sessions_played");
            stats.LastSession = DateTime.UtcNow.AddDays(-Random.Range(1, 30)); // Mock data

            // Add narrative-specific stats
            stats.NarrativeStats.Add(new NarrativeStat
            {
                StatName = "Narratives_Created",
                Value = Steamworks.SteamUserStats.GetStatFloat("narratives_created"),
                Stat7Address = GenerateStat7Address("narratives_created"),
                LastUpdated = DateTime.UtcNow
            });

            stats.NarrativeStats.Add(new NarrativeStat
            {
                StatName = "Companions_Evolved",
                Value = Steamworks.SteamUserStats.GetStatFloat("companions_evolved"),
                Stat7Address = GenerateStat7Address("companions_evolved"),
                LastUpdated = DateTime.UtcNow
            });

            return stats;
        }

        public async Task<bool> RegisterNarrativeCompanion(string companionId, NarrativeCompanionData companion)
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            try
            {
                // Store companion data in Steam remote storage or cloud
                var companionJson = JsonUtility.ToJson(companion);
                var fileName = $"companion_{companionId}.json";

                // This would use Steam Remote Storage API
                // Steamworks.SteamRemoteStorage.FileWrite(fileName, companionJson, companionJson.Length);

                // Update Steam stats
                Steamworks.SteamUserStats.SetStatInt("total_companions",
                    Steamworks.SteamUserStats.GetStatInt("total_companions") + 1);
                Steamworks.SteamUserStats.StoreStats();

                Debug.Log($"Narrative companion registered: {companionId}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to register narrative companion: {ex.Message}");
                return false;
            }
        }

        public async Task<bool> UpdateNarrativeProgress(string companionId, NarrativeProgress progress)
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            try
            {
                // Update Steam stats based on progress
                if (progress.ExperienceGained > 0)
                {
                    Steamworks.SteamUserStats.SetStatFloat("total_experience_gained",
                        Steamworks.SteamUserStats.GetStatFloat("total_experience_gained") + (float)progress.ExperienceGained);
                }

                if (!string.IsNullOrEmpty(progress.NewAbility))
                {
                    Steamworks.SteamUserStats.SetStatInt("abilities_unlocked",
                        Steamworks.SteamUserStats.GetStatInt("abilities_unlocked") + 1);
                }

                Steamworks.SteamUserStats.StoreStats();

                Debug.Log($"Narrative progress updated for companion: {companionId}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update narrative progress: {ex.Message}");
                return false;
            }
        }

        public async Task<List<NarrativeCompanionData>> GetNarrativeCompanions()
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            var companions = new List<NarrativeCompanionData>();

            // Load companions from Steam Remote Storage
            // This would iterate through stored companion files

            return companions;
        }

        public async Task<List<PlatformStoreItem>> GetStoreItems()
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            var storeItems = new List<PlatformStoreItem>();

            // Get Steam store items
            // This would use Steam Store API or Workshop

            return storeItems;
        }

        public async Task<bool> PurchaseItem(string itemId)
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            // Process Steam purchase
            // This would use Steam Microtransaction API

            return await Task.FromResult(true);
        }

        public async Task<bool> ConsumeItem(string itemId)
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            // Consume Steam item
            // This would use Steam Inventory API

            return await Task.FromResult(true);
        }

        // Private helper methods
        private async Task SyncSteamDataToSeed()
        {
            try
            {
                var achievements = await GetAchievements();
                foreach (var achievement in achievements.UnlockedAchievements)
                {
                    await RegisterAchievementAsNarrative(achievement);
                }

                var inventory = await GetUserInventory();
                foreach (var item in inventory.Items)
                {
                    await RegisterInventoryItemAsNarrative(item);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to sync Steam data to Seed: {ex.Message}");
            }
        }

        private async Task RegisterAchievementAsNarrative(Achievement achievement)
        {
            OnNarrativeEvent?.Invoke(new NarrativeEvent
            {
                EventType = "AchievementUnlocked",
                EntityId = achievement.AchievementId,
                Stat7Address = achievement.Stat7Address,
                Timestamp = DateTime.UtcNow,
                Data = new Dictionary<string, object>
                {
                    ["achievementName"] = achievement.Name,
                    ["description"] = achievement.Description,
                    ["points"] = achievement.Points,
                    ["story"] = achievement.AchievementStory
                }
            });
        }

        private async Task RegisterInventoryItemAsNarrative(InventoryItem item)
        {
            OnNarrativeEvent?.Invoke(new NarrativeEvent
            {
                EventType = "InventoryItemAcquired",
                EntityId = item.ItemId,
                Stat7Address = item.Stat7Address,
                Timestamp = DateTime.UtcNow,
                Data = new Dictionary<string, object>
                {
                    ["itemName"] = item.ItemName,
                    ["itemType"] = item.ItemType,
                    ["quantity"] = item.Quantity
                }
            });
        }

        private string GetSteamAvatarUrl(Steamworks.CSteamID steamId)
        {
            // Get friend's avatar image and convert to URL
            // This would need proper Steam API implementation
            return $"https://avatars.steamstatic.com/{steamId.m_SteamID}_full.jpg";
        }

        private async Task<decimal> GetSteamWalletBalance()
        {
            // Get Steam wallet balance
            // This would use Steam Wallet API
            return 0.00m; // Mock implementation
        }

        private async Task<List<InventoryItem>> ConvertSteamItemsToSeedEntities()
        {
            var items = new List<InventoryItem>();

            // Convert Steam inventory items to Seed entities with STAT7 addresses
            // This would iterate through actual Steam inventory

            return items;
        }

        private async Task<Dictionary<string, SteamAchievementData>> GetSteamAchievements()
        {
            var achievements = new Dictionary<string, SteamAchievementData>();

            // Get Steam achievements
            // This would use Steam UserStats API

            return achievements;
        }

        private async Task<Achievement> GetAchievementById(uint achievementId)
        {
            // Get specific achievement by ID
            return null; // Mock implementation
        }

        private async Task<Friend> ConvertSteamFriendToFriend(Steamworks.CSteamID steamId)
        {
            var friend = new Friend
            {
                FriendId = steamId.m_SteamID.ToString(),
                Username = Steamworks.SteamFriends.GetFriendPersonaName(steamId),
                DisplayName = Steamworks.SteamFriends.GetFriendPersonaName(steamId),
                Status = ConvertSteamPersonaState(Steamworks.SteamFriends.GetFriendPersonaState(steamId)),
                AvatarUrl = GetSteamAvatarUrl(steamId),
                SharedNarratives = new List<SharedNarrative>()
            };

            return friend;
        }

        private FriendStatus ConvertSteamPersonaState(Steamworks.EPersonaState state)
        {
            return state switch
            {
                Steamworks.EPersonaState.k_EPersonaStateOffline => FriendStatus.Offline,
                Steamworks.EPersonaState.k_EPersonaStateOnline => FriendStatus.Online,
                Steamworks.EPersonaState.k_EPersonaStateAway => FriendStatus.Away,
                Steamworks.EPersonaState.k_EPersonaStateBusy => FriendStatus.Busy,
                Steamworks.EPersonaState.k_EPersonaStateInGame => FriendStatus.InGame,
                _ => FriendStatus.Offline
            };
        }

        private string GenerateStat7AddressForAchievement(string achievementId)
        {
            return $"stat7://achievement/{achievementId}/hash{achievementId.GetHashCode():X8}?r=0.8&v=0.5&d=0.3";
        }

        private string GenerateStat7Address(string statName)
        {
            return $"stat7://stat/{statName}/hash{statName.GetHashCode():X8}?r=0.6&v=0.4&d=0.2";
        }

        private async Task<NarrativeStory> GenerateAchievementStory(SteamAchievementData achievement)
        {
            // Generate narrative story based on achievement
            return new NarrativeStory
            {
                Title = $"The Legend of {achievement.Name}",
                Content = $"Through determination and skill, you achieved {achievement.Name}. This tale will be told in the halls of the Mind Castle for generations.",
                Theme = "achievement",
                Stat7Address = GenerateStat7AddressForAchievement(achievement.Name)
            };
        }

        public void OnDestroy()
        {
            if (IsInitialized)
            {
                Steamworks.SteamAPI.Shutdown();
                IsInitialized = false;
            }
        }
    }

    // Helper class for Steam achievement data
    public class SteamAchievementData
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public bool IsUnlocked { get; set; }
        public DateTime UnlockTime { get; set; }
        public float Progress { get; set; }
        public string IconUrl { get; set; } = string.Empty;
        public int Points { get; set; }
    }
}
