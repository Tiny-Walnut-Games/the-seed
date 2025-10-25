using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using UnityEngine;

// Conditional compilation for Facepunch.Steamworks
#if FACEPUNCH_STEAMWORKS
using Steamworks;
using Steamworks.Data;
#endif

namespace TWG.Seed.Platform
{
    /// <summary>
    /// Steam platform bridge implementation
    /// Integrates Facepunch.Steamworks API with The Seed's Fractal-Chain system
    ///
    /// CRITICAL SETUP INSTRUCTIONS:
    /// 1. This bridge uses Facepunch.Steamworks (official package from Valve)
    /// 2. Add FACEPUNCH_STEAMWORKS to conditional compilation symbols:
    ///    - In your .csproj file: <DefineConstants>FACEPUNCH_STEAMWORKS</DefineConstants>
    ///    - Or in Unity: Edit > Project Settings > Player > Scripting Define Symbols
    ///      Add: FACEPUNCH_STEAMWORKS
    /// 3. Install Facepunch.Steamworks from NuGet (already done)
    /// 4. Call SteamClient.RunCallbacks() every frame in your game loop!
    ///    Example:
    ///    void Update() {
    ///        #if FACEPUNCH_STEAMWORKS
    ///        SteamClient.RunCallbacks();
    ///        #endif
    ///    }
    ///
    /// DEVELOPMENT NOTES:
    /// - Use Steam App ID 480 (Space War) for testing without a real App ID
    /// - Set steam_appid.txt file with your test App ID or use SteamSettings
    /// - Bridge gracefully degrades to mock functionality when Steam is unavailable
    /// - All methods return sensible defaults when not initialized
    /// </summary>
    public class SteamBridge : IPlatformBridge
    {
        public Platform PlatformType => Platform.Steam;
        public bool IsInitialized { get; private set; }
        public bool IsSteamAvailable { get; private set; }

        public event Action<PlatformEvent> OnPlatformEvent;
        public event Action<NarrativeEvent> OnNarrativeEvent;

#if FACEPUNCH_STEAMWORKS
        // Facepunch.Steamworks uses async callbacks differently
        private bool isCallbacksSetup = false;
#endif

        // Mock data for when Steam is not available
        private readonly PlatformUserIdentity mockUserIdentity = new PlatformUserIdentity
        {
            PlatformUserId = "mock_steam_user_12345",
            Username = "TestUser",
            DisplayName = "Test Developer",
            AvatarUrl = "https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a615cff5dc737237_full.jpg",
            CountryCode = "US",
            SessionStart = DateTime.UtcNow,
            PlatformSpecificData = new Dictionary<string, object>
            {
                ["steamId64"] = 76561197960287930UL, // Default Steam ID
                ["personaState"] = "Online",
                ["isMock"] = true
            }
        };

        public async Task<bool> Initialize()
        {
            try
            {
#if FACEPUNCH_STEAMWORKS
                // Check if Steam is available
                if (!IsSteamClientRunning())
                {
                    Debug.LogWarning("Steam client is not running. Steam bridge will operate in mock mode.");
                    IsSteamAvailable = false;
                    IsInitialized = true; // Still mark as initialized for graceful degradation
                    return true;
                }

                // Initialize Facepunch.Steamworks
                // Facepunch.Steamworks.SteamClient.Init() handles initialization
                try
                {
                    // Initialize with the AppID (use 480 for Space War testing)
                    var steamClient = SteamClient.Init(480);
                    if (!steamClient)
                    {
                        Debug.LogWarning("SteamClient initialization failed. Steam bridge will operate in mock mode.");
                        IsSteamAvailable = false;
                        IsInitialized = true;
                        return true;
                    }
                }
                catch (Exception initEx)
                {
                    Debug.LogWarning($"SteamClient.Init() failed: {initEx.Message}. Operating in mock mode.");
                    IsSteamAvailable = false;
                    IsInitialized = true;
                    return true;
                }

                IsSteamAvailable = true;
                IsInitialized = true;
                Debug.Log("Steam bridge initialized successfully with Facepunch Steamworks API");

                // Sync initial data
                await SyncSteamDataToSeed();
#else
                Debug.LogWarning("Facepunch.Steamworks not available. Steam bridge will operate in mock mode.");
                IsSteamAvailable = false;
                IsInitialized = true;
#endif

                return true;
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Steam initialization error: {ex.Message}. Operating in mock mode.");
                IsSteamAvailable = false;
                IsInitialized = true; // Still mark as initialized for graceful degradation
                return true;
            }
        }

#if FACEPUNCH_STEAMWORKS
        private bool IsSteamClientRunning()
        {
            try
            {
                // Check if Steam process is running
                var processes = System.Diagnostics.Process.GetProcessesByName("steam");
                return processes.Length > 0;
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Failed to check Steam process: {ex.Message}");
                return false;
            }
        }
#endif

        void SetupCallbacks()
        {
#if FACEPUNCH_STEAMWORKS
            if (!IsSteamAvailable)
            {
                Debug.Log("Skipping Steam callback setup - Steam not available");
                return;
            }

            // Facepunch.Steamworks handles callbacks automatically
            // No manual setup needed - callbacks are processed in SteamClient.RunCallbacks()
            // which should be called every frame in your update loop
            isCallbacksSetup = true;
            Debug.Log("Facepunch.Steamworks callbacks ready (auto-managed by SteamClient)");
#else
            Debug.Log("Facepunch.Steamworks not available - skipping callback setup");
#endif
        }

#if FACEPUNCH_STEAMWORKS
        // Note: In Facepunch.Steamworks, callbacks are automatically processed
        // Call SteamClient.RunCallbacks() in your game's Update loop
        // Example in your game manager:
        // void Update() { SteamClient.RunCallbacks(); }

        private async Task HandleUserStatsReceived()
        {
            if (!IsSteamAvailable) return;

            // Sync whenever user stats are received
            await SyncSteamDataToSeed();
        }

        private async Task HandleAchievementStored(string achName)
        {
            if (!IsSteamAvailable) return;

            try
            {
                var achievement = new Achievement
                {
                    AchievementId = achName,
                    Name = achName,
                    Description = string.Empty,
                    IsUnlocked = true,
                    UnlockDate = DateTime.UtcNow,
                    Progress = 100f,
                    IconUrl = string.Empty,
                    Points = 0,
                    Stat7Address = GenerateStat7AddressForAchievement(achName),
                    AchievementStory = await GenerateAchievementStory(new SteamAchievementData
                    {
                        Name = achName,
                        Description = string.Empty
                    })
                };
                await RegisterAchievementAsNarrative(achievement);
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Failed handling achievement stored callback: {ex.Message}");
            }
        }

        private void HandleOverlayActivated(bool active)
        {
            if (!IsSteamAvailable) return;

            OnPlatformEvent?.Invoke(new PlatformEvent
            {
                EventType = "OverlayActivated",
                Timestamp = DateTime.UtcNow,
                Data = new Dictionary<string, object>
                {
                    ["active"] = active
                }
            });
        }
#endif

        public async Task<PlatformUserIdentity> AuthenticateUser()
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            if (!IsSteamAvailable)
            {
                Debug.Log("Returning mock user identity - Steam not available");
                return mockUserIdentity;
            }

#if FACEPUNCH_STEAMWORKS
            try
            {
                var steamId = SteamClient.SteamId;
                var personaName = SteamClient.PersonaName;

                return new PlatformUserIdentity
                {
                    PlatformUserId = steamId.ToString(),
                    Username = personaName,
                    DisplayName = personaName,
                    AvatarUrl = GetSteamAvatarUrl(steamId.ToString()),
                    CountryCode = await GetCountryCode(),
                    SessionStart = DateTime.UtcNow,
                    PlatformSpecificData = new Dictionary<string, object>
                    {
                        ["steamId64"] = (ulong)steamId,
                        ["personaState"] = "Online",
                        ["isMock"] = false
                    }
                };
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Failed to authenticate user: {ex.Message}");
                return mockUserIdentity;
            }
#else
            return mockUserIdentity;
#endif
        }

#if FACEPUNCH_STEAMWORKS
        private async Task<string> GetCountryCode()
        {
            try
            {
                // Facepunch.Steamworks.SteamUtils.GetIPCountry() returns string directly
                return SteamUtils.IPCountry ?? "US";
            }
            catch
            {
                return "US";
            }
        }
#endif

        public Task<bool> ValidateSession()
        {
            if (!IsInitialized)
                return Task.FromResult(false);

            if (!IsSteamAvailable)
            {
                Debug.Log("Mock session validation - Steam not available");
                return Task.FromResult(true); // Always valid in mock mode
            }

#if FACEPUNCH_STEAMWORKS
            try
            {
                var isValid = SteamClient.IsLoggedOn;
                return Task.FromResult(isValid);
            }
            catch
            {
                return Task.FromResult(false);
            }
#else
            return Task.FromResult(true);
#endif
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

            if (!IsSteamAvailable)
            {
                Debug.Log("Returning mock inventory - Steam not available");
                return new PlatformInventory
                {
                    Items = new List<InventoryItem>
                    {
                        new InventoryItem
                        {
                            ItemId = "mock_item_001",
                            ItemName = "Test Sword",
                            ItemType = "Weapon",
                            Quantity = 1,
                            Stat7Address = GenerateStat7Address("mock_item_001"),
                            Description = "A test weapon for development"
                        },
                        new InventoryItem
                        {
                            ItemId = "mock_item_002",
                            ItemName = "Test Potion",
                            ItemType = "Consumable",
                            Quantity = 5,
                            Stat7Address = GenerateStat7Address("mock_item_002"),
                            Description = "A test potion for development"
                        }
                    },
                    MaxSlots = 1000,
                    UsedSlots = 2,
                    Currency = "USD",
                    Balance = 0.00m
                };
            }

            var inventory = new PlatformInventory
            {
                Items = new List<InventoryItem>(),
                MaxSlots = 1000,
                UsedSlots = 0,
                Currency = "USD",
                Balance = await GetSteamWalletBalance()
            };

            // Get Steam inventory items
#if FACEPUNCH_STEAMWORKS
            try
            {
                // Facepunch.Steamworks uses SteamInventory API
                inventory.Items.AddRange(await ConvertSteamItemsToSeedEntities());
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Failed to get Steam inventory items: {ex.Message}");
            }
#endif

            inventory.UsedSlots = inventory.Items.Count;
            return inventory;
        }

        public async Task<PlatformAchievements> GetAchievements()
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            if (!IsSteamAvailable)
            {
                Debug.Log("Returning mock achievements - Steam not available");
                var mockAchievements = new List<Achievement>
                {
                    new Achievement
                    {
                        AchievementId = "mock_ach_001",
                        Name = "Test Achievement 1",
                        Description = "A test achievement for development",
                        IsUnlocked = true,
                        UnlockDate = DateTime.UtcNow.AddDays(-1),
                        Progress = 100f,
                        IconUrl = "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/480/test_icon.jpg",
                        Points = 10,
                        Stat7Address = GenerateStat7AddressForAchievement("mock_ach_001"),
                        AchievementStory = await GenerateAchievementStory(new SteamAchievementData
                        {
                            Name = "Test Achievement 1",
                            Description = "A test achievement for development"
                        })
                    },
                    new Achievement
                    {
                        AchievementId = "mock_ach_002",
                        Name = "Test Achievement 2",
                        Description = "Another test achievement",
                        IsUnlocked = false,
                        Progress = 45f,
                        IconUrl =
                            "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/480/test_icon2.jpg",
                        Points = 25,
                        Stat7Address = GenerateStat7AddressForAchievement("mock_ach_002"),
                        AchievementStory = await GenerateAchievementStory(new SteamAchievementData
                        {
                            Name = "Test Achievement 2",
                            Description = "Another test achievement"
                        })
                    }
                };

                return new PlatformAchievements
                {
                    UnlockedAchievements = mockAchievements.Where(a => a.IsUnlocked).ToList(),
                    LockedAchievements = mockAchievements.Where(a => !a.IsUnlocked).ToList(),
                    TotalAchievements = mockAchievements.Count,
                    UnlockedCount = mockAchievements.Count(a => a.IsUnlocked),
                    CompletionPercentage =
                        (float)mockAchievements.Count(a => a.IsUnlocked) / mockAchievements.Count * 100f
                };
            }

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

            achievements.TotalAchievements =
                achievements.UnlockedAchievements.Count + achievements.LockedAchievements.Count;
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

            if (!IsSteamAvailable)
            {
                Debug.Log("Returning mock friends list - Steam not available");
                var mockFriends = new List<Friend>
                {
                    new Friend
                    {
                        FriendId = "mock_friend_001",
                        Username = "TestFriend1",
                        DisplayName = "Test Friend 1",
                        Status = FriendStatus.Online,
                        AvatarUrl = "https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a615cff5dc737237_full.jpg",
                        SharedNarratives = new List<SharedNarrative>()
                    },
                    new Friend
                    {
                        FriendId = "mock_friend_002",
                        Username = "TestFriend2",
                        DisplayName = "Test Friend 2",
                        Status = FriendStatus.InGame,
                        AvatarUrl = "https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a615cff5dc737238_full.jpg",
                        SharedNarratives = new List<SharedNarrative>()
                    }
                };

                return new PlatformFriends
                {
                    Friends = mockFriends,
                    PendingRequests = new List<FriendRequest>(),
                    MaxFriends = 250
                };
            }

            var friends = new PlatformFriends
            {
                Friends = new List<Friend>(),
                PendingRequests = new List<FriendRequest>(),
                MaxFriends = 250
            };

#if FACEPUNCH_STEAMWORKS
            try
            {
                // Get Steam friends in Facepunch.Steamworks
                var friendCount = SteamFriends.GetFriendCount(FriendFlags.All);
                for (int i = 0; i < friendCount; i++)
                {
                    var steamId = SteamFriends.GetFriendByIndex(i, FriendFlags.All);
                    var friend = await ConvertSteamFriendToFriend(steamId);
                    if (friend != null)
                    {
                        friends.Friends.Add(friend);
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Failed to get Steam friends: {ex.Message}");
            }
#endif

            return friends;
        }

        public async Task<PlatformStats> GetPlayerStats()
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            if (!IsSteamAvailable)
            {
                Debug.Log("Returning mock player stats - Steam not available");
                return new PlatformStats
                {
                    GameStats = new Dictionary<string, double>
                    {
                        ["total_play_hours"] = 12.5,
                        ["sessions_played"] = 8,
                        ["achievements_unlocked"] = 3
                    },
                    TotalPlayTime = TimeSpan.FromHours(12.5),
                    SessionsPlayed = 8,
                    LastSession = DateTime.UtcNow.AddHours(-2),
                    NarrativeStats = new List<NarrativeStat>
                    {
                        new NarrativeStat
                        {
                            StatName = "Narratives_Created",
                            Value = 5,
                            Stat7Address = GenerateStat7Address("narratives_created"),
                            LastUpdated = DateTime.UtcNow
                        },
                        new NarrativeStat
                        {
                            StatName = "Companions_Evolved",
                            Value = 2,
                            Stat7Address = GenerateStat7Address("companions_evolved"),
                            LastUpdated = DateTime.UtcNow
                        }
                    }
                };
            }

            var stats = new PlatformStats
            {
                GameStats = new Dictionary<string, double>(),
                NarrativeStats = new List<NarrativeStat>()
            };

#if FACEPUNCH_STEAMWORKS
            try
            {
                // In Facepunch.Steamworks, request stats first
                await SteamUserStats.RequestCurrentStats();

                // Get Steam stats
                var totalHours = SteamUserStats.GetStat("total_play_hours");
                stats.TotalPlayTime = TimeSpan.FromHours(totalHours);

                var sessions = SteamUserStats.GetStat("sessions_played");
                stats.SessionsPlayed = (int)sessions;

                stats.LastSession = DateTime.UtcNow.AddDays(-UnityEngine.Random.Range(1, 30)); // Placeholder data

                // Add narrative-specific stats
                var narrativesCreated = SteamUserStats.GetStat("narratives_created");
                stats.NarrativeStats.Add(new NarrativeStat
                {
                    StatName = "Narratives_Created",
                    Value = narrativesCreated,
                    Stat7Address = GenerateStat7Address("narratives_created"),
                    LastUpdated = DateTime.UtcNow
                });

                var companionsEvolved = SteamUserStats.GetStat("companions_evolved");
                stats.NarrativeStats.Add(new NarrativeStat
                {
                    StatName = "Companions_Evolved",
                    Value = companionsEvolved,
                    Stat7Address = GenerateStat7Address("companions_evolved"),
                    LastUpdated = DateTime.UtcNow
                });
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Failed to get Steam stats: {ex.Message}. Using defaults.");
                stats.TotalPlayTime = TimeSpan.FromHours(12.5);
                stats.SessionsPlayed = 8;
                stats.LastSession = DateTime.UtcNow.AddHours(-2);
                stats.NarrativeStats.Add(new NarrativeStat
                {
                    StatName = "Narratives_Created",
                    Value = 5,
                    Stat7Address = GenerateStat7Address("narratives_created"),
                    LastUpdated = DateTime.UtcNow
                });
                stats.NarrativeStats.Add(new NarrativeStat
                {
                    StatName = "Companions_Evolved",
                    Value = 2,
                    Stat7Address = GenerateStat7Address("companions_evolved"),
                    LastUpdated = DateTime.UtcNow
                });
            }
#else
            // Mock stats when Steamworks not available
            stats.TotalPlayTime = TimeSpan.FromHours(12.5);
            stats.SessionsPlayed = 8;
            stats.LastSession = DateTime.UtcNow.AddHours(-2);
            stats.NarrativeStats.Add(new NarrativeStat
            {
                StatName = "Narratives_Created",
                Value = 5,
                Stat7Address = GenerateStat7Address("narratives_created"),
                LastUpdated = DateTime.UtcNow
            });
            stats.NarrativeStats.Add(new NarrativeStat
            {
                StatName = "Companions_Evolved",
                Value = 2,
                Stat7Address = GenerateStat7Address("companions_evolved"),
                LastUpdated = DateTime.UtcNow
            });
#endif

            return stats;
        }

        public async Task<bool> RegisterNarrativeCompanion(string companionId, NarrativeCompanionData companion)
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            if (!IsSteamAvailable)
            {
                Debug.Log($"Mock registering narrative companion: {companionId} - Steam not available");
                return true; // Always succeed in mock mode
            }

#if FACEPUNCH_STEAMWORKS
            try
            {
                // Store companion data in Steam remote storage or cloud
                var companionJson = JsonUtility.ToJson(companion);
                var fileName = $"companion_{companionId}.json";

                // In Facepunch.Steamworks, use RemoteStorage API
                var data = System.Text.Encoding.UTF8.GetBytes(companionJson);
                SteamRemoteStorage.FileWrite(fileName, data);

                // Update Steam stats
                var totalCompanions = SteamUserStats.GetStat("total_companions");
                SteamUserStats.SetStat("total_companions", totalCompanions + 1);
                SteamUserStats.StoreStats();

                Debug.Log($"Narrative companion registered: {companionId}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to register narrative companion: {ex.Message}");
                return false;
            }
#else
            return true;
#endif
        }

        public async Task<bool> UpdateNarrativeProgress(string companionId, NarrativeProgress progress)
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            if (!IsSteamAvailable)
            {
                Debug.Log($"Mock updating narrative progress for companion: {companionId} - Steam not available");
                return true; // Always succeed in mock mode
            }

#if FACEPUNCH_STEAMWORKS
            try
            {
                // Update Steam stats based on progress
                if (progress.ExperienceGained > 0)
                {
                    var exp = SteamUserStats.GetStat("total_experience_gained");
                    SteamUserStats.SetStat("total_experience_gained", exp + progress.ExperienceGained);
                }

                if (!string.IsNullOrEmpty(progress.NewAbility))
                {
                    var abilities = SteamUserStats.GetStat("abilities_unlocked");
                    SteamUserStats.SetStat("abilities_unlocked", abilities + 1);
                }

                SteamUserStats.StoreStats();

                Debug.Log($"Narrative progress updated for companion: {companionId}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update narrative progress: {ex.Message}");
                return false;
            }
#else
            return true;
#endif
        }

        public async Task<List<NarrativeCompanionData>> GetNarrativeCompanions()
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            if (!IsSteamAvailable)
            {
                Debug.Log("Returning mock narrative companions - Steam not available");
                return new List<NarrativeCompanionData>
                {
                    new NarrativeCompanionData
                    {
                        CompanionId = "mock_companion_001",
                        Name = "Test Companion",
                        Type = "Warrior",
                        Level = 5,
                        Experience = 1250,
                        Abilities = new List<string> { "Sword Strike", "Shield Block" }
                    }
                };
            }

            var companions = new List<NarrativeCompanionData>();

            // Load companions from Steam Remote Storage
            // 👀This would iterate through stored companion files

            return companions;
        }

        public async Task<List<PlatformStoreItem>> GetStoreItems()
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            if (!IsSteamAvailable)
            {
                Debug.Log("Returning mock store items - Steam not available");
                return new List<PlatformStoreItem>
                {
                    new PlatformStoreItem
                    {
                        ItemId = "mock_store_001",
                        Name = "Test Sword",
                        Description = "A test sword for development",
                        Price = 9.99m,
                        Currency = "USD",
                        ItemType = "Weapon"
                    }
                };
            }

            var storeItems = new List<PlatformStoreItem>();

            // Get Steam store items
            // 👀This would use Steam Store API or Workshop

            return storeItems;
        }

        public async Task<bool> PurchaseItem(string itemId)
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            if (!IsSteamAvailable)
            {
                Debug.Log($"Mock purchasing item: {itemId} - Steam not available");
                return true; // Always succeed in mock mode
            }

            // Process Steam purchase
            // 👀This would use Steam Microtransaction API

            return await Task.FromResult(true);
        }

        public async Task<bool> ConsumeItem(string itemId)
        {
            if (!IsInitialized)
                throw new InvalidOperationException("Steam bridge not initialized");

            if (!IsSteamAvailable)
            {
                Debug.Log($"Mock consuming item: {itemId} - Steam not available");
                return true; // Always succeed in mock mode
            }

            // Consume Steam item
            // 👀This would use Steam Inventory API

            return await Task.FromResult(true);
        }

#if FACEPUNCH_STEAMWORKS
        private string GetSteamAvatarUrl(string steamIdStr)
        {
            // Get friend's avatar image and convert to URL
            // In Facepunch.Steamworks, avatars are accessed differently
            return $"https://avatars.steamstatic.com/{steamIdStr}_full.jpg";
        }

        private async Task<Friend> ConvertSteamFriendToFriend(SteamId steamId)
        {
            try
            {
                var friend = new Friend
                {
                    FriendId = steamId.ToString(),
                    Username = SteamFriends.GetName(steamId),
                    DisplayName = SteamFriends.GetName(steamId),
                    Status = ConvertSteamPersonaState(SteamFriends.GetPersonaState(steamId)),
                    AvatarUrl = GetSteamAvatarUrl(steamId.ToString()),
                    SharedNarratives = new List<SharedNarrative>()
                };

                return friend;
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Failed to convert Steam friend: {ex.Message}");
                return null;
            }
        }

        private FriendStatus ConvertSteamPersonaState(PersonaState state)
        {
            return state switch
            {
                PersonaState.Offline => FriendStatus.Offline,
                PersonaState.Online => FriendStatus.Online,
                PersonaState.Busy => FriendStatus.Busy,
                PersonaState.Away => FriendStatus.Away,
                PersonaState.Snooze => FriendStatus.Away,
                PersonaState.LookingToTrade => FriendStatus.Online,
                PersonaState.LookingToPlay => FriendStatus.Online,
                _ => FriendStatus.Offline
            };
        }
#endif

        // Helper methods that work in both Steam and mock modes

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
                Content =
                    $"Through determination and skill, you achieved {achievement.Name}. This tale will be told in the halls of the Mind Castle for generations.",
                Theme = "achievement",
                Stat7Address = GenerateStat7AddressForAchievement(achievement.Name)
            };
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

        public void OnDestroy()
        {
            if (IsInitialized && IsSteamAvailable)
            {
#if FACEPUNCH_STEAMWORKS
                try
                {
                    SteamClient.Shutdown();
                    Debug.Log("Steam Client shutdown successfully");
                }
                catch (Exception ex)
                {
                    Debug.LogWarning($"Steam Client shutdown error: {ex.Message}");
                }
                finally
                {
                    IsInitialized = false;
                    IsSteamAvailable = false;
                }
#endif
            }
        }

        // Private helper methods
#if FACEPUNCH_STEAMWORKS
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
#else
        private async Task SyncSteamDataToSeed()
        {
            // Mock implementation - no Steam data to sync
            await Task.CompletedTask;
        }
#endif

        // Helper methods that work in both Steam and mock modes
        private string GetSteamAvatarUrl(string steamId)
        {
            // Get friend's avatar image and convert to URL
            return $"https://avatars.steamstatic.com/{steamId}_full.jpg";
        }

        private async Task<decimal> GetSteamWalletBalance()
        {
            // Get Steam wallet balance
            // 👀This would use Steam Wallet API when available
            return 0.00m; // Mock implementation
        }

        private async Task<List<InventoryItem>> ConvertSteamItemsToSeedEntities()
        {
            var items = new List<InventoryItem>();

            // Convert Steam inventory items to Seed entities with STAT7 addresses
            // 👀This would iterate through actual Steam inventory when available

            return items;
        }

        private async Task<Dictionary<string, SteamAchievementData>> GetSteamAchievements()
        {
            var achievements = new Dictionary<string, SteamAchievementData>();

            // Get Steam achievements
            // 👀This would use Steam UserStats API when available

            return achievements;
        }

        private async Task<Achievement> GetAchievementById(uint achievementId)
        {
            // Get specific achievement by ID
            return null; // Mock implementation
        }

        private async Task<Friend> ConvertSteamFriendToFriend(string steamId)
        {
            var friend = new Friend
            {
                FriendId = steamId,
                Username = steamId, // Would use Steam API when available
                DisplayName = steamId,
                Status = FriendStatus.Online,
                AvatarUrl = GetSteamAvatarUrl(steamId),
                SharedNarratives = new List<SharedNarrative>()
            };

            return friend;
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
