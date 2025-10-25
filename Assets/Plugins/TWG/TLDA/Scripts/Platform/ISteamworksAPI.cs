using System;
using System.Threading.Tasks;

namespace TWG.Seed.Platform
{
    /// <summary>
    /// Unity-compatible Steamworks API interface
    /// Provides abstraction layer for Steam functionality
    /// </summary>
    public interface ISteamworksAPI
    {
        bool IsInitialized { get; }
        bool IsSteamAvailable { get; }

        Task<bool> Initialize();
        void Shutdown();

        // User methods
        string GetSteamID();
        string GetPersonaName();
        string GetIPCountry();
        bool IsLoggedOn();

        // Friends methods
        int GetFriendCount(int friendFlags);
        string GetFriendByIndex(int index, int friendFlags);
        string GetFriendPersonaName(string steamId);
        int GetFriendPersonaState(string steamId);
        int GetMaxFriends();

        // Stats methods
        void RequestCurrentStats();
        float GetStatFloat(string statName);
        int GetStatInt(string statName);
        void SetStatFloat(string statName, float value);
        void SetStatInt(string statName, int value);
        bool StoreStats();

        // Utils methods
        ulong GetAppID();
    }

    /// <summary>
    /// Mock Steamworks implementation for development
    /// </summary>
    public class MockSteamworksAPI : ISteamworksAPI
    {
        public bool IsInitialized { get; private set; }
        public bool IsSteamAvailable => false;

        public Task<bool> Initialize()
        {
            IsInitialized = true;
            return Task.FromResult(true);
        }

        public void Shutdown()
        {
            IsInitialized = false;
        }

        public string GetSteamID() => "76561197960287930";
        public string GetPersonaName() => "TestUser";
        public string GetIPCountry() => "US";
        public bool IsLoggedOn() => true;

        public int GetFriendCount(int friendFlags) => 2;
        public string GetFriendByIndex(int index, int friendFlags) => index == 0 ? "76561197960287931" : "76561197960287932";
        public string GetFriendPersonaName(string steamId) => steamId == "76561197960287931" ? "TestFriend1" : "TestFriend2";
        public int GetFriendPersonaState(string steamId) => 1; // Online
        public int GetMaxFriends() => 250;

        public void RequestCurrentStats() { }
        public float GetStatFloat(string statName) => 0f;
        public int GetStatInt(string statName) => 0;
        public void SetStatFloat(string statName, float value) { }
        public void SetStatInt(string statName, int value) { }
        public bool StoreStats() => true;

        public ulong GetAppID() => 480; // Space War test app
    }
}
