using UnityEngine;
using UnityEngine.UIElements;
using System.Collections.Generic;

namespace MobileGameTemplate.Core
{
    /// <summary>
    /// 🧿 CORE ALGORITHM - Central mobile UI management system
    /// Handles screen navigation, responsive layout, and UI Toolkit integration
    /// Portrait-first design with touch optimization for Survivor.io/Archer.io style games
    /// 
    /// Sacred Vision: Transform mobile UI chaos into smooth, responsive navigation!
    /// </summary>
    public class MobileUIManager : MonoBehaviour
    {
        [Header("🎮 Mobile UI Configuration")]
        [SerializeField] private UIDocument _uiDocument;
        [SerializeField] private float _touchTargetMinSize = 44f; // Apple HIG minimum
        [SerializeField] private float _transitionDuration = 0.3f;
        [SerializeField] private bool _enableHapticFeedback = true;
        
        [Header("📱 Screen Management")]
        [SerializeField] private ScreenConfig[] _screenConfigs;
        
        // Core UI elements
        private VisualElement _rootElement;
        private VisualElement _screenContainer;
        private VisualElement _headerContainer;
        private VisualElement _navigationContainer;
        private Label _headerTitle;
        private Button _backButton;
        
        // Screen management
        private Dictionary<string, VisualElement> _screens = new Dictionary<string, VisualElement>();
        private Stack<string> _navigationStack = new Stack<string>();
        private string _currentScreen;
        
        // Events
        public System.Action<string> OnScreenChanged;
        public System.Action<string> OnNavigationRequested;
        
        #region Unity Lifecycle
        
        private void Awake()
        {
            ValidateConfiguration();
            InitializeUI();
        }
        
        private void Start()
        {
            SetupInitialScreen();
        }
        
        private void OnEnable()
        {
            RegisterInputHandlers();
        }
        
        private void OnDisable()
        {
            UnregisterInputHandlers();
        }
        
        #endregion
        
        #region UI Initialization
        
        /// <summary>
        /// 🧿 CORE ALGORITHM - Initialize mobile UI framework
        /// Sets up responsive portrait layout with proper touch targets
        /// </summary>
        private void InitializeUI()
        {
            if (_uiDocument == null)
            {
                Debug.LogError("🧿 MobileUIManager: UIDocument is null! Please assign in inspector.");
                return;
            }
            
            _rootElement = _uiDocument.rootVisualElement;
            SetupMobileLayout();
            CreateNavigationStructure();
            ApplyMobileStyles();
            InitializeScreens();
        }
        
        /// <summary>
        /// 🧿 CORE ALGORITHM - Setup mobile-optimized layout structure
        /// Portrait-first design with safe area handling
        /// </summary>
        private void SetupMobileLayout()
        {
            // Apply mobile-specific styles
            _rootElement.style.flexDirection = FlexDirection.Column;
            _rootElement.style.width = Length.Percent(100);
            _rootElement.style.height = Length.Percent(100);
            
            // Handle safe areas for notched devices
            var safeArea = Screen.safeArea;
            var screenSize = new Vector2(Screen.width, Screen.height);
            
            _rootElement.style.paddingTop = (safeArea.y / screenSize.y) * 100;
            _rootElement.style.paddingBottom = ((screenSize.y - safeArea.height - safeArea.y) / screenSize.y) * 100;
        }
        
        /// <summary>
        /// 🧿 CORE ALGORITHM - Create navigation structure
        /// Header, content area, and optional bottom navigation
        /// </summary>
        private void CreateNavigationStructure()
        {
            // Header container
            _headerContainer = new VisualElement();
            _headerContainer.name = "header-container";
            _headerContainer.AddToClassList("mobile-header");
            
            // Header title
            _headerTitle = new Label("Mobile Game");
            _headerTitle.name = "header-title";
            _headerTitle.AddToClassList("header-title");
            
            // Back button
            _backButton = new Button(() => NavigateBack());
            _backButton.name = "back-button";
            _backButton.text = "←";
            _backButton.AddToClassList("back-button");
            _backButton.style.display = DisplayStyle.None;
            
            _headerContainer.Add(_backButton);
            _headerContainer.Add(_headerTitle);
            
            // Screen container (main content area)
            _screenContainer = new VisualElement();
            _screenContainer.name = "screen-container";
            _screenContainer.AddToClassList("screen-container");
            
            // Navigation container (optional bottom navigation)
            _navigationContainer = new VisualElement();
            _navigationContainer.name = "navigation-container";
            _navigationContainer.AddToClassList("navigation-container");
            
            _rootElement.Add(_headerContainer);
            _rootElement.Add(_screenContainer);
            _rootElement.Add(_navigationContainer);
        }
        
        /// <summary>
        /// 🧿 CORE ALGORITHM - Apply mobile-optimized styles
        /// Touch targets, spacing, and responsive behavior
        /// </summary>
        private void ApplyMobileStyles()
        {
            // Header styles
            _headerContainer.style.height = 60;
            _headerContainer.style.backgroundColor = new Color(0.1f, 0.1f, 0.1f, 0.95f);
            _headerContainer.style.flexDirection = FlexDirection.Row;
            _headerContainer.style.alignItems = Align.Center;
            _headerContainer.style.paddingLeft = 16;
            _headerContainer.style.paddingRight = 16;
            
            // Back button styles
            _backButton.style.width = _touchTargetMinSize;
            _backButton.style.height = _touchTargetMinSize;
            _backButton.style.fontSize = 24;
            _backButton.style.backgroundColor = Color.clear;
            _backButton.style.borderTopWidth = 0;
            _backButton.style.borderBottomWidth = 0;
            _backButton.style.borderLeftWidth = 0;
            _backButton.style.borderRightWidth = 0;
            
            // Title styles
            _headerTitle.style.fontSize = 18;
            _headerTitle.style.color = Color.white;
            _headerTitle.style.unityTextAlign = TextAnchor.MiddleLeft;
            _headerTitle.style.marginLeft = 8;
            _headerTitle.style.flexGrow = 1;
            
            // Screen container styles
            _screenContainer.style.flexGrow = 1;
            _screenContainer.style.overflow = Overflow.Hidden;
            
            // Navigation container styles
            _navigationContainer.style.height = 80;
            _navigationContainer.style.backgroundColor = new Color(0.05f, 0.05f, 0.05f, 0.95f);
        }
        
        #endregion
        
        #region Screen Management
        
        /// <summary>
        /// 📱 Navigate to specified screen with optional data
        /// Handles transition animations and navigation stack
        /// </summary>
        public void NavigateToScreen(string screenId, object data = null)
        {
            if (string.IsNullOrEmpty(screenId) || !_screens.ContainsKey(screenId))
            {
                Debug.LogWarning($"🧿 Screen '{screenId}' not found!");
                return;
            }
            
            // Add current screen to navigation stack
            if (!string.IsNullOrEmpty(_currentScreen))
            {
                _navigationStack.Push(_currentScreen);
                _backButton.style.display = DisplayStyle.Flex;
            }
            
            ShowScreen(screenId, data);
            
            if (_enableHapticFeedback)
            {
                TriggerHapticFeedback();
            }
        }
        
        /// <summary>
        /// 📱 Navigate back to previous screen
        /// </summary>
        public void NavigateBack()
        {
            if (_navigationStack.Count == 0)
            {
                _backButton.style.display = DisplayStyle.None;
                return;
            }
            
            string previousScreen = _navigationStack.Pop();
            
            if (_navigationStack.Count == 0)
            {
                _backButton.style.display = DisplayStyle.None;
            }
            
            ShowScreen(previousScreen);
            
            if (_enableHapticFeedback)
            {
                TriggerHapticFeedback();
            }
        }
        
        /// <summary>
        /// 📱 Show specific screen with data
        /// </summary>
        private void ShowScreen(string screenId, object data = null)
        {
            // Hide current screen
            if (!string.IsNullOrEmpty(_currentScreen) && _screens.ContainsKey(_currentScreen))
            {
                _screens[_currentScreen].style.display = DisplayStyle.None;
            }
            
            // Show new screen
            var newScreen = _screens[screenId];
            newScreen.style.display = DisplayStyle.Flex;
            _currentScreen = screenId;
            
            // Update header title
            var config = GetScreenConfig(screenId);
            if (config != null)
            {
                _headerTitle.text = config.displayName;
            }
            
            // Notify listeners
            OnScreenChanged?.Invoke(screenId);
            
            // Pass data to screen if applicable
            var screenComponent = newScreen.userData as IMobileScreen;
            screenComponent?.OnScreenShown(data);
        }
        
        /// <summary>
        /// 📱 Initialize all configured screens
        /// </summary>
        private void InitializeScreens()
        {
            foreach (var config in _screenConfigs)
            {
                if (config.screenPrefab != null)
                {
                    var screenElement = CreateScreenFromPrefab(config);
                    _screens[config.screenId] = screenElement;
                    _screenContainer.Add(screenElement);
                    screenElement.style.display = DisplayStyle.None;
                }
            }
        }
        
        /// <summary>
        /// 📱 Create screen element from prefab configuration
        /// </summary>
        private VisualElement CreateScreenFromPrefab(ScreenConfig config)
        {
            var screenElement = new VisualElement();
            screenElement.name = $"screen-{config.screenId}";
            screenElement.AddToClassList("mobile-screen");
            
            // Apply screen-specific styles
            screenElement.style.width = Length.Percent(100);
            screenElement.style.height = Length.Percent(100);
            screenElement.style.position = Position.Absolute;
            
            return screenElement;
        }
        
        #endregion
        
        #region Helper Methods
        
        private void ValidateConfiguration()
        {
            if (_uiDocument == null)
            {
                _uiDocument = GetComponent<UIDocument>();
            }
            
            if (_screenConfigs == null || _screenConfigs.Length == 0)
            {
                Debug.LogWarning("🧿 No screen configurations found! Please configure screens in inspector.");
            }
        }
        
        private void SetupInitialScreen()
        {
            if (_screenConfigs.Length > 0)
            {
                string initialScreen = _screenConfigs[0].screenId;
                ShowScreen(initialScreen);
            }
        }
        
        private void RegisterInputHandlers()
        {
            // Handle Android back button
            if (Application.platform == RuntimePlatform.Android)
            {
                // Input handling for Android back button would go here
                // This requires additional input system setup
            }
        }
        
        private void UnregisterInputHandlers()
        {
            // Cleanup input handlers
        }
        
        private void TriggerHapticFeedback()
        {
            // Platform-specific haptic feedback
            #if UNITY_ANDROID && !UNITY_EDITOR
            // Android haptic feedback implementation
            #elif UNITY_IOS && !UNITY_EDITOR
            // iOS haptic feedback implementation
            #endif
        }
        
        private ScreenConfig GetScreenConfig(string screenId)
        {
            foreach (var config in _screenConfigs)
            {
                if (config.screenId == screenId)
                    return config;
            }
            return null;
        }
        
        #endregion
    }
    
    /// <summary>
    /// Configuration for mobile game screens
    /// </summary>
    [System.Serializable]
    public class ScreenConfig
    {
        [Header("Screen Identity")]
        public string screenId;
        public string displayName;
        
        [Header("Screen Configuration")]
        public GameObject screenPrefab;
        public bool allowBackNavigation = true;
        public bool showInNavigation = true;
        
        [Header("Transition Settings")]
        public float transitionDuration = 0.3f;
        public AnimationCurve transitionCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);
    }
    
    /// <summary>
    /// Interface for mobile screen components
    /// </summary>
    public interface IMobileScreen
    {
        void OnScreenShown(object data = null);
        void OnScreenHidden();
        void OnBackPressed();
    }
}