using UnityEngine;

using System.Collections.Generic; // 🔧 C# 10 Compatibility
namespace MobileGameTemplate.Systems
{
    /// <summary>
    /// Data structures and platform wrappers for ads system
    /// </summary>
    
    [System.Serializable]
    public class AdRewardConfig
    {
        [Header("Ad Configuration")]
        public AdType adType = AdType.RewardedVideo;
        public string rewardContext = "";
        
        [Header("Reward Configuration")]
        public AdRewardType rewardType = AdRewardType.Currency;
        public int quantity = 10;
        public string itemId = "";
        public string description = "Watch ad for reward";
    }
    
    [System.Serializable]
    public class AdReward
    {
        public AdRewardType rewardType = AdRewardType.Currency;
        public int quantity = 10;
        public string itemId = "";
        public string description = "";
    }
    
    public enum AdType
    {
        RewardedVideo = 0,
        Interstitial = 1,
        Banner = 2
    }
    
    public enum AdRewardType
    {
        Currency = 0,
        Gems = 1,
        Experience = 2,
        Item = 3,
        DoubleReward = 4,
        LivesRefill = 5,
        TimeSkip = 6,
        Boost = 7
    }
    
    public enum AdMediationPlatform
    {
        UnityAds = 0,
        AdMob = 1,
        IronSource = 2,
        AppLovin = 3,
        Vungle = 4,
        Mock = 99 // For testing
    }
    
    /// <summary>
    /// Interface for ad mediation platform wrappers
    /// </summary>
    public interface IAdMediationPlatform
    {
        System.Action<AdType, AdReward> OnAdRewardGranted { get; set; }
        System.Action<AdType> OnAdWatched { get; set; }
        System.Action<AdType, string> OnAdFailed { get; set; }
        System.Action<AdType> OnAdClosed { get; set; }
        System.Action OnInitialized { get; set; }
        
        void Initialize(bool testMode);
        bool IsAdReady(AdType adType);
        void ShowAd(AdType adType, string rewardContext);
        void LoadAd(AdType adType);
    }
    
    /// <summary>
    /// 📺 Unity Ads wrapper implementation
    /// </summary>
    public class UnityAdsWrapper : IAdMediationPlatform
    {
        public System.Action<AdType, AdReward> OnAdRewardGranted { get; set; }
        public System.Action<AdType> OnAdWatched { get; set; }
        public System.Action<AdType, string> OnAdFailed { get; set; }
        public System.Action<AdType> OnAdClosed { get; set; }
        public System.Action OnInitialized { get; set; }
        
        private const string GAME_ID_ANDROID = "1234567";
        private const string GAME_ID_IOS = "7654321";
        private const string REWARDED_PLACEMENT = "rewardedVideo";
        private const string INTERSTITIAL_PLACEMENT = "video";
        private const string BANNER_PLACEMENT = "banner";
        
        public void Initialize(bool testMode)
        {
            #if UNITY_ADS && !UNITY_EDITOR
            string gameId = Application.platform == RuntimePlatform.Android ? GAME_ID_ANDROID : GAME_ID_IOS;
            UnityEngine.Advertisements.Advertisement.Initialize(gameId, testMode, this);
            #else
            // Mock initialization for editor/testing
            OnInitialized?.Invoke();
            Debug.Log("📺 Unity Ads: Mock initialization (not in build with Unity Ads)");
            #endif
        }
        
        public bool IsAdReady(AdType adType)
        {
            #if UNITY_ADS && !UNITY_EDITOR
            string placementId = GetPlacementId(adType);
            return UnityEngine.Advertisements.Advertisement.IsReady(placementId);
            #else
            // Mock availability for testing
            return true;
            #endif
        }
        
        public void ShowAd(AdType adType, string rewardContext)
        {
            #if UNITY_ADS && !UNITY_EDITOR
            string placementId = GetPlacementId(adType);
            var options = new UnityEngine.Advertisements.ShowOptions
            {
                resultCallback = (result) => HandleAdResult(adType, result)
            };
            UnityEngine.Advertisements.Advertisement.Show(placementId, options);
            #else
            // Mock ad showing for testing
            Debug.Log($"📺 Unity Ads: Mock showing {adType} ad");
            HandleMockAdResult(adType);
            #endif
        }
        
        public void LoadAd(AdType adType)
        {
            #if UNITY_ADS && !UNITY_EDITOR
            string placementId = GetPlacementId(adType);
            UnityEngine.Advertisements.Advertisement.Load(placementId);
            #else
            Debug.Log($"📺 Unity Ads: Mock loading {adType} ad");
            #endif
        }
        
        private string GetPlacementId(AdType adType)
        {
            return adType switch
            {
                AdType.RewardedVideo => REWARDED_PLACEMENT,
                AdType.Interstitial => INTERSTITIAL_PLACEMENT,
                AdType.Banner => BANNER_PLACEMENT,
                _ => REWARDED_PLACEMENT
            };
        }
        
        #if UNITY_ADS && !UNITY_EDITOR
        private void HandleAdResult(AdType adType, UnityEngine.Advertisements.ShowResult result)
        {
            switch (result)
            {
                case UnityEngine.Advertisements.ShowResult.Finished:
                    OnAdWatched?.Invoke(adType);
                    if (adType == AdType.RewardedVideo)
                    {
                        var reward = new AdReward
                        {
                            rewardType = AdRewardType.Currency,
                            quantity = 10,
                            description = "Unity Ads reward"
                        };
                        OnAdRewardGranted?.Invoke(adType, reward);
                    }
                    break;
                case UnityEngine.Advertisements.ShowResult.Skipped:
                    OnAdClosed?.Invoke(adType);
                    break;
                case UnityEngine.Advertisements.ShowResult.Failed:
                    OnAdFailed?.Invoke(adType, "Unity Ads failed to show");
                    break;
            }
        }
        #endif
        
        private void HandleMockAdResult(AdType adType)
        {
            // Simulate successful ad watch
            OnAdWatched?.Invoke(adType);
            
            if (adType == AdType.RewardedVideo)
            {
                var reward = new AdReward
                {
                    rewardType = AdRewardType.Currency,
                    quantity = 10,
                    description = "Mock Unity Ads reward"
                };
                OnAdRewardGranted?.Invoke(adType, reward);
            }
        }
    }
    
    /// <summary>
    /// 📺 AdMob wrapper implementation
    /// </summary>
    public class AdMobWrapper : IAdMediationPlatform
    {
        public System.Action<AdType, AdReward> OnAdRewardGranted { get; set; }
        public System.Action<AdType> OnAdWatched { get; set; }
        public System.Action<AdType, string> OnAdFailed { get; set; }
        public System.Action<AdType> OnAdClosed { get; set; }
        public System.Action OnInitialized { get; set; }
        
        private const string APP_ID = "ca-app-pub-1234567890123456~1234567890";
        private const string REWARDED_UNIT_ID = "ca-app-pub-1234567890123456/1234567890";
        private const string INTERSTITIAL_UNIT_ID = "ca-app-pub-1234567890123456/0987654321";
        private const string BANNER_UNIT_ID = "ca-app-pub-1234567890123456/1122334455";
        
        public void Initialize(bool testMode)
        {
            #if GOOGLE_MOBILE_ADS && !UNITY_EDITOR
            GoogleMobileAds.Api.MobileAds.Initialize(initStatus => {
                OnInitialized?.Invoke();
            });
            #else
            OnInitialized?.Invoke();
            Debug.Log("📺 AdMob: Mock initialization (not in build with AdMob)");
            #endif
        }
        
        public bool IsAdReady(AdType adType)
        {
            #if GOOGLE_MOBILE_ADS && !UNITY_EDITOR
            // AdMob-specific ready check implementation
            return true; // Simplified for example
            #else
            return true;
            #endif
        }
        
        public void ShowAd(AdType adType, string rewardContext)
        {
            #if GOOGLE_MOBILE_ADS && !UNITY_EDITOR
            // AdMob-specific show implementation
            Debug.Log($"📺 AdMob: Showing {adType} ad");
            #else
            Debug.Log($"📺 AdMob: Mock showing {adType} ad");
            HandleMockAdResult(adType);
            #endif
        }
        
        public void LoadAd(AdType adType)
        {
            #if GOOGLE_MOBILE_ADS && !UNITY_EDITOR
            // AdMob-specific load implementation
            #else
            Debug.Log($"📺 AdMob: Mock loading {adType} ad");
            #endif
        }
        
        private void HandleMockAdResult(AdType adType)
        {
            OnAdWatched?.Invoke(adType);
            
            if (adType == AdType.RewardedVideo)
            {
                var reward = new AdReward
                {
                    rewardType = AdRewardType.Currency,
                    quantity = 15,
                    description = "Mock AdMob reward"
                };
                OnAdRewardGranted?.Invoke(adType, reward);
            }
        }
    }
    
    /// <summary>
    /// 📺 IronSource wrapper implementation
    /// </summary>
    public class IronSourceWrapper : IAdMediationPlatform
    {
        public System.Action<AdType, AdReward> OnAdRewardGranted { get; set; }
        public System.Action<AdType> OnAdWatched { get; set; }
        public System.Action<AdType, string> OnAdFailed { get; set; }
        public System.Action<AdType> OnAdClosed { get; set; }
        public System.Action OnInitialized { get; set; }
        
        private const string APP_KEY = "1234567890";
        
        public void Initialize(bool testMode)
        {
            #if IRONSOURCE && !UNITY_EDITOR
            IronSource.Agent.init(APP_KEY);
            OnInitialized?.Invoke();
            #else
            OnInitialized?.Invoke();
            Debug.Log("📺 IronSource: Mock initialization (not in build with IronSource)");
            #endif
        }
        
        public bool IsAdReady(AdType adType)
        {
            #if IRONSOURCE && !UNITY_EDITOR
            return adType switch
            {
                AdType.RewardedVideo => IronSource.Agent.isRewardedVideoAvailable(),
                AdType.Interstitial => IronSource.Agent.isInterstitialReady(),
                _ => false
            };
            #else
            return true;
            #endif
        }
        
        public void ShowAd(AdType adType, string rewardContext)
        {
            #if IRONSOURCE && !UNITY_EDITOR
            switch (adType)
            {
                case AdType.RewardedVideo:
                    IronSource.Agent.showRewardedVideo();
                    break;
                case AdType.Interstitial:
                    IronSource.Agent.showInterstitial();
                    break;
            }
            #else
            Debug.Log($"📺 IronSource: Mock showing {adType} ad");
            HandleMockAdResult(adType);
            #endif
        }
        
        public void LoadAd(AdType adType)
        {
            #if IRONSOURCE && !UNITY_EDITOR
            if (adType == AdType.Interstitial)
            {
                IronSource.Agent.loadInterstitial();
            }
            #else
            Debug.Log($"📺 IronSource: Mock loading {adType} ad");
            #endif
        }
        
        private void HandleMockAdResult(AdType adType)
        {
            OnAdWatched?.Invoke(adType);
            
            if (adType == AdType.RewardedVideo)
            {
                var reward = new AdReward
                {
                    rewardType = AdRewardType.Currency,
                    quantity = 12,
                    description = "Mock IronSource reward"
                };
                OnAdRewardGranted?.Invoke(adType, reward);
            }
        }
    }
    
    /// <summary>
    /// 📺 AppLovin wrapper implementation
    /// </summary>
    public class AppLovinWrapper : IAdMediationPlatform
    {
        public System.Action<AdType, AdReward> OnAdRewardGranted { get; set; }
        public System.Action<AdType> OnAdWatched { get; set; }
        public System.Action<AdType, string> OnAdFailed { get; set; }
        public System.Action<AdType> OnAdClosed { get; set; }
        public System.Action OnInitialized { get; set; }
        
        public void Initialize(bool testMode)
        {
            OnInitialized?.Invoke();
            Debug.Log("📺 AppLovin: Mock initialization");
        }
        
        public bool IsAdReady(AdType adType) => true;
        
        public void ShowAd(AdType adType, string rewardContext)
        {
            Debug.Log($"📺 AppLovin: Mock showing {adType} ad");
            HandleMockAdResult(adType);
        }
        
        public void LoadAd(AdType adType)
        {
            Debug.Log($"📺 AppLovin: Mock loading {adType} ad");
        }
        
        private void HandleMockAdResult(AdType adType)
        {
            OnAdWatched?.Invoke(adType);
            
            if (adType == AdType.RewardedVideo)
            {
                var reward = new AdReward
                {
                    rewardType = AdRewardType.Gems,
                    quantity = 5,
                    description = "Mock AppLovin reward"
                };
                OnAdRewardGranted?.Invoke(adType, reward);
            }
        }
    }
    
    /// <summary>
    /// 📺 Vungle wrapper implementation
    /// </summary>
    public class VungleWrapper : IAdMediationPlatform
    {
        public System.Action<AdType, AdReward> OnAdRewardGranted { get; set; }
        public System.Action<AdType> OnAdWatched { get; set; }
        public System.Action<AdType, string> OnAdFailed { get; set; }
        public System.Action<AdType> OnAdClosed { get; set; }
        public System.Action OnInitialized { get; set; }
        
        public void Initialize(bool testMode)
        {
            OnInitialized?.Invoke();
            Debug.Log("📺 Vungle: Mock initialization");
        }
        
        public bool IsAdReady(AdType adType) => true;
        
        public void ShowAd(AdType adType, string rewardContext)
        {
            Debug.Log($"📺 Vungle: Mock showing {adType} ad");
            HandleMockAdResult(adType);
        }
        
        public void LoadAd(AdType adType)
        {
            Debug.Log($"📺 Vungle: Mock loading {adType} ad");
        }
        
        private void HandleMockAdResult(AdType adType)
        {
            OnAdWatched?.Invoke(adType);
            
            if (adType == AdType.RewardedVideo)
            {
                var reward = new AdReward
                {
                    rewardType = AdRewardType.Experience,
                    quantity = 100,
                    description = "Mock Vungle reward"
                };
                OnAdRewardGranted?.Invoke(adType, reward);
            }
        }
    }
    
    /// <summary>
    /// 📺 Mock ad platform for testing and development
    /// </summary>
    public class MockAdPlatform : IAdMediationPlatform
    {
        public System.Action<AdType, AdReward> OnAdRewardGranted { get; set; }
        public System.Action<AdType> OnAdWatched { get; set; }
        public System.Action<AdType, string> OnAdFailed { get; set; }
        public System.Action<AdType> OnAdClosed { get; set; }
        public System.Action OnInitialized { get; set; }
        
        private System.Collections.Generic.Dictionary<AdType, bool> _adAvailability = 
            new System.Collections.Generic.Dictionary<AdType, bool>();
        
        public void Initialize(bool testMode)
        {
            // Mock all ad types as available
            _adAvailability[AdType.RewardedVideo] = true;
            _adAvailability[AdType.Interstitial] = true;
            _adAvailability[AdType.Banner] = true;
            
            OnInitialized?.Invoke();
            Debug.Log("📺 Mock Ad Platform: Initialized for testing");
        }
        
        public bool IsAdReady(AdType adType)
        {
            return _adAvailability.ContainsKey(adType) && _adAvailability[adType];
        }
        
        public void ShowAd(AdType adType, string rewardContext)
        {
            Debug.Log($"📺 Mock Ad Platform: Showing {adType} ad with context '{rewardContext}'");
            
            // Simulate ad watch delay
            var delay = adType == AdType.RewardedVideo ? 3f : 1f;
            
            MonoBehaviour.FindObjectOfType<AdsSystem>().StartCoroutine(
                SimulateAdWatch(adType, delay));
        }
        
        public void LoadAd(AdType adType)
        {
            Debug.Log($"📺 Mock Ad Platform: Loading {adType} ad");
            _adAvailability[adType] = true;
        }
        
        private System.Collections.IEnumerator SimulateAdWatch(AdType adType, float delay)
        {
            yield return new WaitForSeconds(delay);
            
            OnAdWatched?.Invoke(adType);
            
            if (adType == AdType.RewardedVideo)
            {
                var reward = new AdReward
                {
                    rewardType = AdRewardType.Currency,
                    quantity = 20,
                    description = "Mock ad reward"
                };
                OnAdRewardGranted?.Invoke(adType, reward);
            }
            
            // Simulate cooldown by temporarily making ad unavailable
            _adAvailability[adType] = false;
            
            yield return new WaitForSeconds(5f); // 5 second cooldown for testing
            
            _adAvailability[adType] = true;
        }
    }
    
    /// <summary>
    /// 📺 Ad placement helper for common scenarios
    /// </summary>
    public static class AdPlacements
    {
        // Common reward contexts
        public const string DOUBLE_COINS = "double_coins";
        public const string EXTRA_LIVES = "extra_lives";
        public const string CONTINUE_GAME = "continue_game";
        public const string BONUS_CHEST = "bonus_chest";
        public const string SKIP_WAIT = "skip_wait";
        public const string UNLOCK_FEATURE = "unlock_feature";
        
        // Interstitial placements
        public const string LEVEL_COMPLETE = "level_complete";
        public const string GAME_OVER = "game_over";
        public const string APP_LAUNCH = "app_launch";
        public const string MENU_NAVIGATION = "menu_navigation";
        
        /// <summary>
        /// Get recommended reward for placement context
        /// </summary>
        public static AdReward GetRecommendedReward(string context)
        {
            return context switch
            {
                DOUBLE_COINS => new AdReward { rewardType = AdRewardType.DoubleReward, quantity = 1, description = "Double your coins!" },
                EXTRA_LIVES => new AdReward { rewardType = AdRewardType.LivesRefill, quantity = 1, description = "Refill your lives!" },
                CONTINUE_GAME => new AdReward { rewardType = AdRewardType.Currency, quantity = 0, description = "Continue playing!" },
                BONUS_CHEST => new AdReward { rewardType = AdRewardType.Item, quantity = 1, description = "Bonus reward chest!" },
                SKIP_WAIT => new AdReward { rewardType = AdRewardType.TimeSkip, quantity = 1, description = "Skip waiting time!" },
                UNLOCK_FEATURE => new AdReward { rewardType = AdRewardType.Item, quantity = 1, description = "Unlock premium feature!" },
                _ => new AdReward { rewardType = AdRewardType.Currency, quantity = 10, description = "Thank you for watching!" }
            };
        }
        
        /// <summary>
        /// Check if context should show rewarded video vs interstitial
        /// </summary>
        public static AdType GetRecommendedAdType(string context)
        {
            return context switch
            {
                DOUBLE_COINS or EXTRA_LIVES or CONTINUE_GAME or BONUS_CHEST or SKIP_WAIT or UNLOCK_FEATURE => AdType.RewardedVideo,
                LEVEL_COMPLETE or GAME_OVER or APP_LAUNCH or MENU_NAVIGATION => AdType.Interstitial,
                _ => AdType.RewardedVideo
            };
        }
    }
}