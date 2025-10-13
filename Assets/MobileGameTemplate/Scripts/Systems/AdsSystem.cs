using UnityEngine;
using UnityEngine.UIElements;
using MobileGameTemplate.Core; // 🔧 Unity 2022.3 Compatibility
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
        [SerializeField] private bool _enableAds = true;
        [SerializeField] private bool _enableTestMode = true;
        [SerializeField] private AdMediationPlatform _mediationPlatform = AdMediationPlatform.UnityAds;
        
        [Header("Ad Placement IDs")]
        [SerializeField] private string _rewardedVideoPlacementId = "rewardedVideo";
        [SerializeField] private string _interstitialPlacementId = "interstitial";
        [SerializeField] private string _bannerPlacementId = "banner";
        
        [Header("Ad Rewards")]
        [SerializeField] private List<AdRewardConfig> _adRewards = new List<AdRewardConfig>();
        
        [Header("Ad Frequency")]
        [SerializeField] private float _interstitialCooldown = 120f; // 2 minutes
        [SerializeField] private int _maxRewardedAdsPerDay = 20;
        [SerializeField] private int _maxInterstitialsPerSession = 5;
        
        // State tracking
        private Dictionary<AdType, System.DateTime> _lastAdShown = new Dictionary<AdType, System.DateTime>();
        private Dictionary<AdType, int> _adsShownThisSession = new Dictionary<AdType, int>();
        private Dictionary<AdType, int> _adsShownToday = new Dictionary<AdType, int>();
        
        // Mediation platform wrapper
        private IAdMediationPlatform _adPlatform;
        private bool _isInitialized = false;
        #endregion
        
        #region Unity Lifecycle
        
        private void Awake()
        {
            // Ensure only one ads system exists
            if (FindObjectsOfType<AdsSystem>().Length > 1)
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
            
            // Create mediation platform wrapper
            _adPlatform = CreateAdPlatform(_mediationPlatform);
            
            if (_adPlatform != null)
            {
                _adPlatform.OnAdRewardGranted += HandleAdRewardGranted;
                _adPlatform.OnAdWatched += HandleAdWatched;
                _adPlatform.OnAdFailed += HandleAdFailed;
                _adPlatform.OnAdClosed += HandleAdClosed;
                _adPlatform.OnInitialized += HandleAdMediationInitialized;
                
                _adPlatform.Initialize(_enableTestMode);
            }
            else
            {
                Debug.LogError("📺 Failed to create ad mediation platform");
            }
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
        
        /// <summary>
        /// 📺 Check daily ad limit
        /// </summary>
        private bool CheckDailyLimit(AdType adType)
        {
            int dailyLimit = GetDailyLimit(adType);
            int watchedToday = GetAdsWatchedToday(adType);
            return watchedToday < dailyLimit;
        }
        
        /// <summary>
        /// 📺 Check session ad limit
        /// </summary>
        private bool CheckSessionLimit(AdType adType)
        {
            if (adType == AdType.Interstitial)
            {
                int sessionCount = _adsShownThisSession.ContainsKey(adType) ? _adsShownThisSession[adType] : 0;
                return sessionCount < _maxInterstitialsPerSession;
            }
            
            return true; // No session limit for other ad types
        }
        
        /// <summary>
        /// 📺 Check ad cooldown
        /// </summary>
        private bool CheckCooldown(AdType adType)
        {
            if (!_lastAdShown.ContainsKey(adType))
                return true;
            
            var timeSinceLastAd = System.DateTime.Now - _lastAdShown[adType];
            var cooldown = GetCooldownForAdType(adType);
            
            return timeSinceLastAd.TotalSeconds >= cooldown;
        }
        
        /// <summary>
        /// 📺 Get daily limit for ad type
        /// </summary>
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
        
        /// <summary>
        /// 📺 Get cooldown for ad type
        /// </summary>
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
        
        /// <summary>
        /// 📺 Load ad statistics from storage
        /// </summary>
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
        
        /// <summary>
        /// 📺 Save ad statistics to storage
        /// </summary>
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
    /// 📺 Ad button component for UI integration (Simplified for Unity compatibility)
    /// </summary>
    public class AdButton : VisualElement
    {
        private AdsSystem _adsSystem;
        private AdType _adType;
        private string _rewardContext;
        private Button _watchButton;
        private Label _rewardLabel;
        private Label _cooldownLabel;
        private VisualElement _rewardIcon;
        
        public System.Action<AdReward> OnAdRewardReceived;
        
        // 🔧 LEGENDARY FIX: Add parameterless constructor for UxmlFactory
        public AdButton() : this(AdType.RewardedVideo, "")
        {
        }
        
        public AdButton(AdType adType, string rewardContext = "")
        {
            _adType = adType;
            _rewardContext = rewardContext;
            
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
            
            // 🔧 LEGENDARY FIX: Use compatible style properties
            // Note: borderRadius, borderWidth, borderColor may not be available in older Unity versions
            // Using background color and padding for visual distinction instead
            
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
            _watchButton = new Button(WatchAd);
            _watchButton.text = "WATCH AD";
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
            // 🔧 LEGENDARY FIX: Find AdsSystem in scene instead of using FindObjectOfType in constructor
            if (_adsSystem == null)
            {
                _adsSystem = Object.FindObjectOfType<AdsSystem>();
            }
            
            if (_adsSystem != null)
            {
                _adsSystem.OnAdRewardGranted += OnAdRewardGranted;
                _adsSystem.OnAdFailed += OnAdFailed;
            }
        }
        
        private void UpdateButtonState()
        {
            if (_adsSystem == null)
            {
                // Try to find AdsSystem again
                _adsSystem = Object.FindObjectOfType<AdsSystem>();
                if (_adsSystem == null) return;
                RegisterCallbacks();
            }
            
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
                // 🔧 Note: borderColor not available in older Unity versions
                // style.borderColor = new Color(0.3f, 0.7f, 0.3f, 0.8f);
            }
            else if (timeUntilAvailable.TotalSeconds > 0)
            {
                _watchButton.style.backgroundColor = new Color(0.5f, 0.5f, 0.5f, 0.9f);
                _watchButton.text = "COOLDOWN";
                _cooldownLabel.text = FormatCooldownTime(timeUntilAvailable);
                _cooldownLabel.style.display = DisplayStyle.Flex;
                // style.borderColor = new Color(0.5f, 0.5f, 0.5f, 0.8f);
            }
            else
            {
                _watchButton.style.backgroundColor = new Color(0.7f, 0.3f, 0.3f, 0.9f);
                _watchButton.text = "UNAVAILABLE";
                _cooldownLabel.style.display = DisplayStyle.None;
                // style.borderColor = new Color(0.7f, 0.3f, 0.3f, 0.8f);
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
                
                // Visual feedback - using available style properties
                style.backgroundColor = new Color(1f, 0.8f, 0f, 0.5f);
                schedule.Execute(() => UpdateButtonState()).ExecuteLater(2000);
            }
        }
        
        private void OnAdFailed(AdType adType, string error)
        {
            if (adType == _adType)
            {
                // Show error feedback
                style.backgroundColor = new Color(1f, 0.3f, 0.3f, 0.5f);
                schedule.Execute(() => UpdateButtonState()).ExecuteLater(2000);
            }
        }
        
        // 🔧 LEGENDARY FIX: Simplified UxmlFactory without traits for compatibility
        public new class UxmlFactory : UxmlFactory<AdButton> { }
    }
}
