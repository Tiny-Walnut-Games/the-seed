using UnityEngine;
using UnityEngine.UIElements;
using System.Collections.Generic;

namespace MobileGameTemplate.Systems
{
    /// <summary>
    /// 📺 INTENDED EXPANSION ZONE - Advertisement integration system
    /// Rewarded and interstitial ads with mediation platform support
    /// Designed for mobile monetization in action games
    /// 
    /// Sacred Vision: Transform ad viewing into rewarding experiences!
    /// </summary>
    public class AdsSystem : MonoBehaviour
    {
        #region Events
        public System.Action<AdType, AdReward> OnAdRewardGranted;
        public System.Action<AdType> OnAdWatched;
        public System.Action<AdType, string> OnAdFailed;
        public System.Action<AdType> OnAdClosed;
        public System.Action OnAdMediationInitialized;
        #endregion
        
        #region Private Fields
        [Header("Ad Configuration")]
        private readonly bool _enableAds = true;
        private readonly bool _enableTestMode = true;
        private readonly AdMediationPlatform _mediationPlatform = AdMediationPlatform.UnityAds;
        
        [Header("Ad Placement IDs")]
        [SerializeField] private string _rewardedVideoPlacementId = "rewardedVideo"; // Used in ad mediation platform setup
        [SerializeField] private string _interstitialPlacementId = "interstitial"; // Used in ad mediation platform setup  
        [SerializeField] private string _bannerPlacementId = "banner"; // Used in ad mediation platform setup

        [Header("Ad Rewards")]
        private readonly List<AdRewardConfig> _adRewards = new();
        
        [Header("Ad Frequency")]
        private readonly float _interstitialCooldown = 120f; // 2 minutes
        private readonly int _maxRewardedAdsPerDay = 20;
        private readonly int _maxInterstitialsPerSession = 5;
        
        // State tracking
        private readonly Dictionary<AdType, System.DateTime> _lastAdShown = new();
        private readonly Dictionary<AdType, int> _adsShownThisSession = new();
        private readonly Dictionary<AdType, int> _adsShownToday = new();
        
        // Mediation platform wrapper
        private IAdMediationPlatform _adPlatform;
        private bool _isInitialized = false;
        #endregion
        
        #region Unity Lifecycle
        
        private void Awake()
        {
            // Ensure only one ads system exists
            if (FindObjectsByType<AdsSystem>(FindObjectsSortMode.None).Length > 1)
            {
                Destroy(gameObject);
                return;
            }
            
            DontDestroyOnLoad(gameObject);
            InitializeAdSystem();
        }
        
        private void Start()
        {
            LoadAdStatistics();
        }
        
        private void OnApplicationPause(bool pauseStatus)
        {
            if (pauseStatus)
            {
                SaveAdStatistics();
            }
        }
        
        #endregion
        
        #region Public API
        
        /// <summary>
        /// 📺 Check if ad is available for the specified type
        /// </summary>
        public bool IsAdAvailable(AdType adType)
        {
            if (!_enableAds || !_isInitialized)
                return false;
            
            // Check daily limits
            if (!CheckDailyLimit(adType))
                return false;
            
            // Check session limits
            if (!CheckSessionLimit(adType))
                return false;
            
            // Check cooldown
            if (!CheckCooldown(adType))
                return false;
            
            // Check with mediation platform
            return _adPlatform?.IsAdReady(adType) ?? false;
        }
        
        /// <summary>
        /// 📺 Show ad with specified type and optional reward context
        /// </summary>
        public void ShowAd(AdType adType, string rewardContext = "")
        {
            if (!IsAdAvailable(adType))
            {
                OnAdFailed?.Invoke(adType, "Ad not available");
                return;
            }
            
            // Track ad showing
            _lastAdShown[adType] = System.DateTime.Now;
            
            if (!_adsShownThisSession.ContainsKey(adType))
                _adsShownThisSession[adType] = 0;
            _adsShownThisSession[adType]++;
            
            if (!_adsShownToday.ContainsKey(adType))
                _adsShownToday[adType] = 0;
            _adsShownToday[adType]++;
            
            // Show ad through mediation platform
            _adPlatform?.ShowAd(adType, rewardContext);
        }
        
        /// <summary>
        /// 📺 Get reward configuration for ad type and context
        /// </summary>
        public AdReward GetAdReward(AdType adType, string rewardContext)
        {
            var config = _adRewards.Find(r => r.adType == adType && r.rewardContext == rewardContext);
            if (config != null)
            {
                return new AdReward
                {
                    rewardType = config.rewardType,
                    quantity = config.quantity,
                    itemId = config.itemId,
                    description = config.description
                };
            }
            
            // Default reward for watching ads
            return new AdReward
            {
                rewardType = AdRewardType.Currency,
                quantity = 10,
                description = "Thank you for watching!"
            };
        }
        
        /// <summary>
        /// 📺 Get time until next ad is available
        /// </summary>
        public System.TimeSpan GetTimeUntilAdAvailable(AdType adType)
        {
            if (!_lastAdShown.ContainsKey(adType))
                return System.TimeSpan.Zero;
            
            var lastShown = _lastAdShown[adType];
            var cooldown = GetCooldownForAdType(adType);
            var nextAvailable = lastShown.AddSeconds(cooldown);
            var timeUntilAvailable = nextAvailable - System.DateTime.Now;
            
            return timeUntilAvailable.TotalSeconds > 0 ? timeUntilAvailable : System.TimeSpan.Zero;
        }
        
        /// <summary>
        /// 📺 Get ads watched today count
        /// </summary>
        public int GetAdsWatchedToday(AdType adType)
        {
            return _adsShownToday.ContainsKey(adType) ? _adsShownToday[adType] : 0;
        }
        
        /// <summary>
        /// 📺 Get remaining ads for today
        /// </summary>
        public int GetRemainingAdsToday(AdType adType)
        {
            int maxAds = GetDailyLimit(adType);
            int watchedToday = GetAdsWatchedToday(adType);
            return Mathf.Max(0, maxAds - watchedToday);
        }
        
        #endregion
        
        #region Private Methods
        
        /// <summary>
        /// 📺 Initialize ad mediation system
        /// </summary>
        private void InitializeAdSystem()
        {
            if (!_enableAds)
            {
                Debug.Log("📺 Ads disabled in configuration");
                return;
            }
            
            // Create mediation platform wrapper with placement IDs
            _adPlatform = CreateAdPlatform(_mediationPlatform);
            
            if (_adPlatform != null)
            {
                _adPlatform.OnAdRewardGranted += HandleAdRewardGranted;
                _adPlatform.OnAdWatched += HandleAdWatched;
                _adPlatform.OnAdFailed += HandleAdFailed;
                _adPlatform.OnAdClosed += HandleAdClosed;
                _adPlatform.OnInitialized += HandleAdMediationInitialized;
                
                // Initialize with placement IDs and test mode
                _adPlatform.Initialize(_enableTestMode);
                SetupPlacementIds();
            }
            else
            {
                Debug.LogError("📺 Failed to create ad mediation platform");
            }
        }

        /// <summary>
        /// Setup placement IDs for the selected ad platform
        /// </summary>
        private void SetupPlacementIds()
        {
            Debug.Log($"📺 Setting up placement IDs - Rewarded: {_rewardedVideoPlacementId}, Interstitial: {_interstitialPlacementId}, Banner: {_bannerPlacementId}");
            
            // Configure placement IDs based on platform
            switch (_mediationPlatform)
            {
                case AdMediationPlatform.UnityAds:
                    ConfigureUnityAdsPlacement();
                    break;
                case AdMediationPlatform.AdMob:
                    ConfigureAdMobPlacement();
                    break;
                default:
                    Debug.Log("📺 Using default placement configuration");
                    break;
            }
        }

        /// <summary>
        /// Configure Unity Ads specific placement IDs
        /// </summary>
        private void ConfigureUnityAdsPlacement()
        {
            // Unity Ads uses these placement IDs for different ad types
            Debug.Log($"📺 Unity Ads configured with placements - Video: {_rewardedVideoPlacementId}, Interstitial: {_interstitialPlacementId}, Banner: {_bannerPlacementId}");
        }

        /// <summary>
        /// Configure AdMob specific placement IDs
        /// </summary>
        private void ConfigureAdMobPlacement()
        {
            // AdMob uses different format for placement IDs
            Debug.Log($"📺 AdMob configured with ad unit IDs - Video: {_rewardedVideoPlacementId}, Interstitial: {_interstitialPlacementId}, Banner: {_bannerPlacementId}");
        }
        
        /// <summary>
        /// 📺 Create ad platform wrapper based on configuration
        /// </summary>
        private IAdMediationPlatform CreateAdPlatform(AdMediationPlatform platform)
        {
            return platform switch
            {
                AdMediationPlatform.UnityAds => new UnityAdsWrapper(),
                AdMediationPlatform.AdMob => new AdMobWrapper(),
                AdMediationPlatform.IronSource => new IronSourceWrapper(),
                AdMediationPlatform.AppLovin => new AppLovinWrapper(),
                AdMediationPlatform.Vungle => new VungleWrapper(),
                _ => new MockAdPlatform() // Fallback for testing
            };
        }
        
        private bool CheckDailyLimit(AdType adType)
        {
            int dailyLimit = GetDailyLimit(adType);
            int watchedToday = GetAdsWatchedToday(adType);
            return watchedToday < dailyLimit;
        }
        
        private bool CheckSessionLimit(AdType adType)
        {
            if (adType == AdType.Interstitial)
            {
                int sessionCount = _adsShownThisSession.ContainsKey(adType) ? _adsShownThisSession[adType] : 0;
                return sessionCount < _maxInterstitialsPerSession;
            }
            
            return true; // No session limit for other ad types
        }
        
        private bool CheckCooldown(AdType adType)
        {
            if (!_lastAdShown.ContainsKey(adType))
                return true;
            
            var timeSinceLastAd = System.DateTime.Now - _lastAdShown[adType];
            var cooldown = GetCooldownForAdType(adType);
            
            return timeSinceLastAd.TotalSeconds >= cooldown;
        }
        
        private int GetDailyLimit(AdType adType)
        {
            return adType switch
            {
                AdType.RewardedVideo => _maxRewardedAdsPerDay,
                AdType.Interstitial => 999, // No daily limit for interstitials
                AdType.Banner => 999, // No daily limit for banners
                _ => 10
            };
        }
        
        private float GetCooldownForAdType(AdType adType)
        {
            return adType switch
            {
                AdType.Interstitial => _interstitialCooldown,
                AdType.RewardedVideo => 0f, // No cooldown for rewarded
                AdType.Banner => 0f, // No cooldown for banners
                _ => 30f
            };
        }
        
        private void LoadAdStatistics()
        {
            // Load today's ad counts
            string today = System.DateTime.Now.ToString("yyyy-MM-dd");
            string savedDate = PlayerPrefs.GetString("AdStatsDate", "");
            
            if (savedDate == today)
            {
                // Load today's stats
                foreach (AdType adType in System.Enum.GetValues(typeof(AdType)))
                {
                    string key = $"AdsWatched_{adType}_{today}";
                    _adsShownToday[adType] = PlayerPrefs.GetInt(key, 0);
                }
            }
            else
            {
                // Reset daily counters for new day
                _adsShownToday.Clear();
                PlayerPrefs.SetString("AdStatsDate", today);
            }
        }
        
        private void SaveAdStatistics()
        {
            string today = System.DateTime.Now.ToString("yyyy-MM-dd");
            
            foreach (var kvp in _adsShownToday)
            {
                string key = $"AdsWatched_{kvp.Key}_{today}";
                PlayerPrefs.SetInt(key, kvp.Value);
            }
            
            PlayerPrefs.Save();
        }
        
        #endregion
        
        #region Event Handlers
        
        private void HandleAdRewardGranted(AdType adType, AdReward reward)
        {
            OnAdRewardGranted?.Invoke(adType, reward);
        }
        
        private void HandleAdWatched(AdType adType)
        {
            OnAdWatched?.Invoke(adType);
        }
        
        private void HandleAdFailed(AdType adType, string error)
        {
            OnAdFailed?.Invoke(adType, error);
        }
        
        private void HandleAdClosed(AdType adType)
        {
            OnAdClosed?.Invoke(adType);
        }
        
        private void HandleAdMediationInitialized()
        {
            _isInitialized = true;
            OnAdMediationInitialized?.Invoke();
            Debug.Log("📺 Ad mediation platform initialized successfully");
        }
        
        #endregion
    }
    
    /// <summary>
    /// 📺 Ad button component for UI integration
    /// </summary>
    public class AdButton : VisualElement
    {
        private readonly AdsSystem _adsSystem;
        private readonly AdType _adType;
        private readonly string _rewardContext;
        private Button _watchButton;
        private Label _rewardLabel;
        private Label _cooldownLabel;
        private VisualElement _rewardIcon;
        
        public System.Action<AdReward> OnAdRewardReceived;
        
        public AdButton() : this(AdType.RewardedVideo, "")
        {
        }
        
        public AdButton(AdType adType, string rewardContext = "")
        {
            _adType = adType;
            _rewardContext = rewardContext;
            _adsSystem = Object.FindFirstObjectByType<AdsSystem>();
            
            CreateButtonStructure();
            RegisterCallbacks();
            UpdateButtonState();
            
            // Update button state periodically
            schedule.Execute(UpdateButtonState).Every(1000);
        }
        
        private void CreateButtonStructure()
        {
            style.flexDirection = FlexDirection.Column;
            style.alignItems = Align.Center;
            style.paddingTop = 8;
            style.paddingBottom = 8;
            style.paddingLeft = 12;
            style.paddingRight = 12;
            style.backgroundColor = new Color(0.1f, 0.1f, 0.1f, 0.9f);
            
            // Reward icon
            _rewardIcon = new VisualElement();
            _rewardIcon.style.width = 32;
            _rewardIcon.style.height = 32;
            _rewardIcon.style.backgroundColor = new Color(1f, 0.8f, 0f, 1f);
            _rewardIcon.style.marginBottom = 8;
            
            // Reward description
            _rewardLabel = new Label();
            _rewardLabel.style.fontSize = 12;
            _rewardLabel.style.color = Color.white;
            _rewardLabel.style.unityTextAlign = TextAnchor.MiddleCenter;
            _rewardLabel.style.marginBottom = 8;

            // Watch button
            _watchButton = new Button(WatchAd)
            {
                text = "WATCH AD"
            };
            _watchButton.style.paddingLeft = 16;
            _watchButton.style.paddingRight = 16;
            _watchButton.style.paddingTop = 8;
            _watchButton.style.paddingBottom = 8;
            _watchButton.style.backgroundColor = new Color(0.3f, 0.7f, 0.3f, 0.9f);
            _watchButton.style.color = Color.white;
            _watchButton.style.fontSize = 12;
            
            // Cooldown label
            _cooldownLabel = new Label();
            _cooldownLabel.style.fontSize = 10;
            _cooldownLabel.style.color = new Color(0.7f, 0.7f, 0.7f, 1f);
            _cooldownLabel.style.unityTextAlign = TextAnchor.MiddleCenter;
            _cooldownLabel.style.display = DisplayStyle.None;
            
            Add(_rewardIcon);
            Add(_rewardLabel);
            Add(_watchButton);
            Add(_cooldownLabel);
        }
        
        private void RegisterCallbacks()
        {
            if (_adsSystem != null)
            {
                _adsSystem.OnAdRewardGranted += OnAdRewardGranted;
                _adsSystem.OnAdFailed += OnAdFailed;
            }
        }
        
        private void UpdateButtonState()
        {
            if (_adsSystem == null) return;
            
            bool isAvailable = _adsSystem.IsAdAvailable(_adType);
            var timeUntilAvailable = _adsSystem.GetTimeUntilAdAvailable(_adType);
            var reward = _adsSystem.GetAdReward(_adType, _rewardContext);
            
            // Update reward display
            _rewardLabel.text = GetRewardDisplayText(reward);
            
            // Update button availability
            _watchButton.SetEnabled(isAvailable);
            
            if (isAvailable)
            {
                _watchButton.style.backgroundColor = new Color(0.3f, 0.7f, 0.3f, 0.9f);
                _watchButton.text = "WATCH AD";
                _cooldownLabel.style.display = DisplayStyle.None;
            }
            else if (timeUntilAvailable.TotalSeconds > 0)
            {
                _watchButton.style.backgroundColor = new Color(0.5f, 0.5f, 0.5f, 0.9f);
                _watchButton.text = "COOLDOWN";
                _cooldownLabel.text = FormatCooldownTime(timeUntilAvailable);
                _cooldownLabel.style.display = DisplayStyle.Flex;
            }
            else
            {
                _watchButton.style.backgroundColor = new Color(0.7f, 0.3f, 0.3f, 0.9f);
                _watchButton.text = "UNAVAILABLE";
                _cooldownLabel.style.display = DisplayStyle.None;
            }
        }
        
        private string GetRewardDisplayText(AdReward reward)
        {
            return reward.rewardType switch
            {
                AdRewardType.Currency => $"+{reward.quantity} Coins",
                AdRewardType.Gems => $"+{reward.quantity} Gems",
                AdRewardType.Experience => $"+{reward.quantity} XP",
                AdRewardType.Item => $"Free {reward.itemId}",
                AdRewardType.DoubleReward => "2x Rewards",
                AdRewardType.LivesRefill => "Refill Lives",
                _ => reward.description
            };
        }
        
        private string FormatCooldownTime(System.TimeSpan timeSpan)
        {
            if (timeSpan.TotalMinutes >= 1)
                return $"{(int)timeSpan.TotalMinutes}m {timeSpan.Seconds}s";
            else
                return $"{timeSpan.Seconds}s";
        }
        
        private void WatchAd()
        {
            if (_adsSystem != null)
            {
                _adsSystem.ShowAd(_adType, _rewardContext);
            }
        }
        
        private void OnAdRewardGranted(AdType adType, AdReward reward)
        {
            if (adType == _adType)
            {
                OnAdRewardReceived?.Invoke(reward);
                // Note: borderColor not available - visual feedback removed
                schedule.Execute(() => UpdateButtonState()).ExecuteLater(2000);
            }
        }
        
        private void OnAdFailed(AdType adType, string error)
        {
            if (adType == _adType)
            {
                // Note: borderColor not available - visual feedback removed
                schedule.Execute(() => UpdateButtonState()).ExecuteLater(2000);
            }
        }
        
        //public new class UxmlFactory : UxmlFactory<AdButton, UxmlTraits> { }
        
        //public new class UxmlTraits : VisualElement.UxmlTraits
        //{
        //    public override void Init(VisualElement ve, IUxmlAttributes bag, CreationContext cc)
        //    {
        //        base.Init(ve, bag, cc);
        //    }
        //} 
        // Note: UxmlFactory pattern was used in older UI Toolkit versions but is now handled differently
    }
}

/// <summary>
/// 📺 Ad mediation platform interface for different ad networks
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
}

/// <summary>
/// 📺 Unity Ads mediation wrapper
/// </summary>
public class UnityAdsWrapper : IAdMediationPlatform
{
    public System.Action<AdType, AdReward> OnAdRewardGranted { get; set; }
    public System.Action<AdType> OnAdWatched { get; set; }
    public System.Action<AdType, string> OnAdFailed { get; set; }
    public System.Action<AdType> OnAdClosed { get; set; }
    public System.Action OnInitialized { get; set; }
    
    public void Initialize(bool testMode)
    {
        // Initialize Unity Ads SDK
        Debug.Log($"📺 Initializing Unity Ads (Test Mode: {testMode})");
        OnInitialized?.Invoke();
    }
    
    public bool IsAdReady(AdType adType)
    {
        // Check Unity Ads readiness
        return true; // Mock implementation
    }
    
    public void ShowAd(AdType adType, string rewardContext)
    {
        // Show Unity Ad
        Debug.Log($"📺 Showing Unity Ad: {adType}");
        
        // Simulate ad completion
        OnAdWatched?.Invoke(adType);
        
        if (adType == AdType.RewardedVideo)
        {
            var reward = new AdReward
            {
                rewardType = AdRewardType.Currency,
                quantity = 100,
                description = "Unity Ads reward"
            };
            OnAdRewardGranted?.Invoke(adType, reward);
        }
        
        OnAdClosed?.Invoke(adType);
    }
}

/// <summary>
/// 📺 AdMob mediation wrapper
/// </summary>
public class AdMobWrapper : IAdMediationPlatform
{
    public System.Action<AdType, AdReward> OnAdRewardGranted { get; set; }
    public System.Action<AdType> OnAdWatched { get; set; }
    public System.Action<AdType, string> OnAdFailed { get; set; }
    public System.Action<AdType> OnAdClosed { get; set; }
    public System.Action OnInitialized { get; set; }
    
    public void Initialize(bool testMode)
    {
        Debug.Log($"📺 Initializing AdMob (Test Mode: {testMode})");
        OnInitialized?.Invoke();
    }
    
    public bool IsAdReady(AdType adType)
    {
        return true; // Mock implementation
    }
    
    public void ShowAd(AdType adType, string rewardContext)
    {
        Debug.Log($"📺 Showing AdMob Ad: {adType}");
        OnAdWatched?.Invoke(adType);
        OnAdClosed?.Invoke(adType);
    }
}

/// <summary>
/// 📺 IronSource mediation wrapper
/// </summary>
public class IronSourceWrapper : IAdMediationPlatform
{
    public System.Action<AdType, AdReward> OnAdRewardGranted { get; set; }
    public System.Action<AdType> OnAdWatched { get; set; }
    public System.Action<AdType, string> OnAdFailed { get; set; }
    public System.Action<AdType> OnAdClosed { get; set; }
    public System.Action OnInitialized { get; set; }
    
    public void Initialize(bool testMode)
    {
        Debug.Log($"📺 Initializing IronSource (Test Mode: {testMode})");
        OnInitialized?.Invoke();
    }
    
    public bool IsAdReady(AdType adType)
    {
        return true; // Mock implementation
    }
    
    public void ShowAd(AdType adType, string rewardContext)
    {
        Debug.Log($"📺 Showing IronSource Ad: {adType}");
        OnAdWatched?.Invoke(adType);
        OnAdClosed?.Invoke(adType);
    }
}

/// <summary>
/// 📺 AppLovin mediation wrapper
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
        Debug.Log($"📺 Initializing AppLovin (Test Mode: {testMode})");
        OnInitialized?.Invoke();
    }
    
    public bool IsAdReady(AdType adType)
    {
        return true; // Mock implementation
    }
    
    public void ShowAd(AdType adType, string rewardContext)
    {
        Debug.Log($"📺 Showing AppLovin Ad: {adType}");
        OnAdWatched?.Invoke(adType);
        OnAdClosed?.Invoke(adType);
    }
}

/// <summary>
/// 📺 Vungle mediation wrapper
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
        Debug.Log($"📺 Initializing Vungle (Test Mode: {testMode})");
        OnInitialized?.Invoke();
    }
    
    public bool IsAdReady(AdType adType)
    {
        return true; // Mock implementation
    }
    
    public void ShowAd(AdType adType, string rewardContext)
    {
        Debug.Log($"📺 Showing Vungle Ad: {adType}");
        OnAdWatched?.Invoke(adType);
        OnAdClosed?.Invoke(adType);
    }
}

/// <summary>
/// 📺 Mock ad platform for testing
/// </summary>
public class MockAdPlatform : IAdMediationPlatform
{
    public System.Action<AdType, AdReward> OnAdRewardGranted { get; set; }
    public System.Action<AdType> OnAdWatched { get; set; }
    public System.Action<AdType, string> OnAdFailed { get; set; }
    public System.Action<AdType> OnAdClosed { get; set; }
    public System.Action OnInitialized { get; set; }
    
    public void Initialize(bool testMode)
    {
        Debug.Log("📺 Initializing Mock Ad Platform for testing");
        OnInitialized?.Invoke();
    }
    
    public bool IsAdReady(AdType adType)
    {
        return true; // Always ready for testing
    }
    
    public void ShowAd(AdType adType, string rewardContext)
    {
        Debug.Log($"📺 Showing Mock Ad: {adType}");
        OnAdWatched?.Invoke(adType);
        
        if (adType == AdType.RewardedVideo)
        {
            var reward = new AdReward
            {
                rewardType = AdRewardType.Currency,
                quantity = 50,
                description = "Mock ad reward"
            };
            OnAdRewardGranted?.Invoke(adType, reward);
        }
        
        OnAdClosed?.Invoke(adType);
    }
}

/// <summary>
/// 📺 Ad system data structures
/// </summary>
public enum AdType
{
    RewardedVideo = 0,
    Interstitial = 1,
    Banner = 2
}

public enum AdMediationPlatform
{
    UnityAds = 0,
    AdMob = 1,
    IronSource = 2,
    AppLovin = 3,
    Vungle = 4
}

public enum AdRewardType
{
    Currency = 0,
    Gems = 1,
    Experience = 2,
    Item = 3,
    DoubleReward = 4,
    LivesRefill = 5
}

[System.Serializable]
public class AdReward
{
    public AdRewardType rewardType;
    public int quantity;
    public string itemId;
    public string description;
}

[System.Serializable]
public class AdRewardConfig
{
    public AdType adType;
    public string rewardContext;
    public AdRewardType rewardType;
    public int quantity;
    public string itemId;
    public string description;
}
