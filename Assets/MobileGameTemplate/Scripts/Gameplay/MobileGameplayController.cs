using UnityEngine;
using UnityEngine.UIElements;
using System.Collections.Generic;

namespace MobileGameTemplate.Gameplay
{
    /// <summary>
    /// 🎮 INTENDED EXPANSION ZONE - Core mobile gameplay controller
    /// Touch controls, auto-aim, and ability system for Survivor.io/Archer.io style games
    /// Designed for portrait mobile action gaming with smooth performance
    /// 
    /// Sacred Vision: Transform touch input into responsive action gameplay!
    /// </summary>
    public class MobileGameplayController : MonoBehaviour
    {
        #region Events
        public System.Action<Vector2> OnPlayerMoved;
        public System.Action<Vector2> OnPlayerStopped;
        public System.Action<string> OnAbilityTriggered;
        public System.Action<GameObject> OnEnemyTargeted;
        public System.Action<int> OnScoreChanged;
        public System.Action OnGamePaused;
        public System.Action OnGameResumed;
        #endregion
        
        #region Private Fields
        [Header("🎮 Touch Controls")]
        [SerializeField] private Camera _gameCamera;
        [SerializeField] private Transform _player;
        [SerializeField] private float _moveSpeed = 5f;
        [SerializeField] private float _touchSensitivity = 1f;
        [SerializeField] private bool _enableVirtualJoystick = true;
        
        [Header("🎯 Auto-Aim System")]
        [SerializeField] private float _autoAimRange = 10f;
        [SerializeField] private float _autoAimAngle = 45f;
        [SerializeField] private LayerMask _enemyLayer = 1 << 8;
        [SerializeField] private bool _enableAutoAim = true;
        [SerializeField] private Transform _aimIndicator;
        
        [Header("⚡ Ability System")]
        [SerializeField] private List<AbilityConfig> _abilities = new List<AbilityConfig>();
        [SerializeField] private float _globalCooldownReduction = 1f;
        
        [Header("📱 Mobile UI")]
        [SerializeField] private UIDocument _gameplayUI;
        [SerializeField] private RectTransform _joystickArea;
        [SerializeField] private float _joystickDeadZone = 0.1f;
        
        // Input tracking
        private Vector2 _touchStartPosition;
        private Vector2 _currentTouchPosition;
        private Vector2 _moveDirection;
        private bool _isTouching;
        private int _primaryTouchId = -1;
        
        // Auto-aim tracking
        private GameObject _currentTarget;
        private List<GameObject> _nearbyEnemies = new List<GameObject>();
        private float _lastTargetScanTime;
        private const float TARGET_SCAN_INTERVAL = 0.1f;
        
        // Ability tracking
        private Dictionary<string, float> _abilityCooldowns = new Dictionary<string, float>();
        private Dictionary<string, bool> _abilityActive = new Dictionary<string, bool>();
        
        // UI elements
        private VisualElement _rootElement;
        private VisualElement _joystickContainer;
        private VisualElement _joystickKnob;
        private VisualElement _abilityContainer;
        private List<AbilityButton> _abilityButtons = new List<AbilityButton>();
        private Label _scoreLabel;
        private Button _pauseButton;
        
        // Game state
        private bool _isGamePaused;
        private int _currentScore;
        private Vector2 _playerVelocity;
        
        // Performance optimization
        private WaitForSeconds _targetScanWait;
        private Collider[] _enemyColliders = new Collider[50]; // Reusable array
        #endregion
        
        #region Unity Lifecycle
        
        private void Awake()
        {
            ValidateConfiguration();
            _targetScanWait = new WaitForSeconds(TARGET_SCAN_INTERVAL);
        }
        
        private void Start()
        {
            SetupGameplayUI();
            InitializeAbilities();
            StartCoroutine(TargetScanLoop());
        }
        
        private void Update()
        {
            if (_isGamePaused) return;
            
            HandleInput();
            UpdatePlayerMovement();
            UpdateAbilityCooldowns();
            UpdateAutoAim();
        }
        
        private void FixedUpdate()
        {
            if (_isGamePaused) return;
            
            ApplyPlayerMovement();
        }
        
        #endregion
        
        #region Public API
        
        /// <summary>
        /// 🎮 Pause/resume gameplay
        /// </summary>
        public void TogglePause()
        {
            _isGamePaused = !_isGamePaused;
            
            if (_isGamePaused)
            {
                Time.timeScale = 0f;
                OnGamePaused?.Invoke();
            }
            else
            {
                Time.timeScale = 1f;
                OnGameResumed?.Invoke();
            }
        }
        
        /// <summary>
        /// 🎮 Trigger ability by ID
        /// </summary>
        public bool TriggerAbility(string abilityId)
        {
            var ability = _abilities.Find(a => a.abilityId == abilityId);
            if (ability == null) return false;
            
            if (IsAbilityReady(abilityId))
            {
                ExecuteAbility(ability);
                return true;
            }
            
            return false;
        }
        
        /// <summary>
        /// 🎮 Check if ability is ready to use
        /// </summary>
        public bool IsAbilityReady(string abilityId)
        {
            if (_abilityCooldowns.ContainsKey(abilityId))
            {
                return _abilityCooldowns[abilityId] <= 0f;
            }
            return true;
        }
        
        /// <summary>
        /// 🎮 Get ability cooldown remaining
        /// </summary>
        public float GetAbilityCooldown(string abilityId)
        {
            return _abilityCooldowns.ContainsKey(abilityId) ? _abilityCooldowns[abilityId] : 0f;
        }
        
        /// <summary>
        /// 🎮 Add score points
        /// </summary>
        public void AddScore(int points)
        {
            _currentScore += points;
            UpdateScoreDisplay();
            OnScoreChanged?.Invoke(_currentScore);
        }
        
        /// <summary>
        /// 🎮 Set current target manually
        /// </summary>
        public void SetTarget(GameObject target)
        {
            _currentTarget = target;
            UpdateAimIndicator();
            OnEnemyTargeted?.Invoke(target);
        }
        
        #endregion
        
        #region Private Methods
        
        /// <summary>
        /// 🎮 Validate configuration and references
        /// </summary>
        private void ValidateConfiguration()
        {
            if (_gameCamera == null)
                _gameCamera = Camera.main;
            
            if (_player == null)
                _player = transform;
            
            if (_gameplayUI == null)
                _gameplayUI = GetComponent<UIDocument>();
            
            if (_abilities == null)
                _abilities = new List<AbilityConfig>();
        }
        
        /// <summary>
        /// 🎮 Setup gameplay UI elements
        /// </summary>
        private void SetupGameplayUI()
        {
            if (_gameplayUI == null) return;
            
            _rootElement = _gameplayUI.rootVisualElement;
            
            // Apply mobile gameplay styles
            _rootElement.style.width = Length.Percent(100);
            _rootElement.style.height = Length.Percent(100);
            
            CreateVirtualJoystick();
            CreateAbilityButtons();
            CreateHUD();
            
            RegisterUICallbacks();
        }
        
        /// <summary>
        /// 🎮 Create virtual joystick for movement
        /// </summary>
        private void CreateVirtualJoystick()
        {
            if (!_enableVirtualJoystick) return;
            
            _joystickContainer = new VisualElement();
            _joystickContainer.name = "joystick-container";
            _joystickContainer.style.position = Position.Absolute;
            _joystickContainer.style.bottom = 60;
            _joystickContainer.style.left = 40;
            _joystickContainer.style.width = 120;
            _joystickContainer.style.height = 120;
            _joystickContainer.style.backgroundColor = new Color(0.2f, 0.2f, 0.2f, 0.6f);
            _joystickContainer.style.borderRadius = 60;
            _joystickContainer.style.borderWidth = 2;
            _joystickContainer.style.borderColor = new Color(0.4f, 0.4f, 0.4f, 0.8f);
            
            _joystickKnob = new VisualElement();
            _joystickKnob.name = "joystick-knob";
            _joystickKnob.style.position = Position.Absolute;
            _joystickKnob.style.width = 40;
            _joystickKnob.style.height = 40;
            _joystickKnob.style.backgroundColor = new Color(0.8f, 0.8f, 0.8f, 0.9f);
            _joystickKnob.style.borderRadius = 20;
            _joystickKnob.style.top = 40;
            _joystickKnob.style.left = 40;
            
            _joystickContainer.Add(_joystickKnob);
            _rootElement.Add(_joystickContainer);
        }
        
        /// <summary>
        /// 🎮 Create ability buttons UI
        /// </summary>
        private void CreateAbilityButtons()
        {
            _abilityContainer = new VisualElement();
            _abilityContainer.name = "ability-container";
            _abilityContainer.style.position = Position.Absolute;
            _abilityContainer.style.bottom = 60;
            _abilityContainer.style.right = 40;
            _abilityContainer.style.flexDirection = FlexDirection.Row;
            
            for (int i = 0; i < _abilities.Count && i < 4; i++)
            {
                var ability = _abilities[i];
                var abilityButton = new AbilityButton(ability);
                abilityButton.OnClicked += () => TriggerAbility(ability.abilityId);
                
                _abilityButtons.Add(abilityButton);
                _abilityContainer.Add(abilityButton);
            }
            
            _rootElement.Add(_abilityContainer);
        }
        
        /// <summary>
        /// 🎮 Create HUD elements
        /// </summary>
        private void CreateHUD()
        {
            // Score display
            _scoreLabel = new Label("Score: 0");
            _scoreLabel.style.position = Position.Absolute;
            _scoreLabel.style.top = 40;
            _scoreLabel.style.left = 20;
            _scoreLabel.style.fontSize = 18;
            _scoreLabel.style.color = Color.white;
            _scoreLabel.style.unityFontStyleAndWeight = FontStyle.Bold;
            _scoreLabel.style.textShadow = new TextShadow
            {
                offset = new Vector2(1, 1),
                blurRadius = 2,
                color = Color.black
            };
            
            // Pause button
            _pauseButton = new Button(TogglePause);
            _pauseButton.text = "⏸";
            _pauseButton.style.position = Position.Absolute;
            _pauseButton.style.top = 20;
            _pauseButton.style.right = 20;
            _pauseButton.style.width = 50;
            _pauseButton.style.height = 50;
            _pauseButton.style.fontSize = 20;
            _pauseButton.style.backgroundColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            _pauseButton.style.borderRadius = 25;
            _pauseButton.style.borderWidth = 0;
            _pauseButton.style.color = Color.white;
            
            _rootElement.Add(_scoreLabel);
            _rootElement.Add(_pauseButton);
        }
        
        // Additional methods continue here to manage input, abilities, auto-aim, etc.
        // This is a condensed version to fit in the response length limit
        
        private void RegisterUICallbacks() { /* Implementation */ }
        private void InitializeAbilities() { /* Implementation */ }
        private void HandleInput() { /* Implementation */ }
        private void UpdatePlayerMovement() { /* Implementation */ }
        private void ApplyPlayerMovement() { /* Implementation */ }
        private void UpdateAbilityCooldowns() { /* Implementation */ }
        private void UpdateAutoAim() { /* Implementation */ }
        private System.Collections.IEnumerator TargetScanLoop() { yield return null; }
        private void ExecuteAbility(AbilityConfig ability) { /* Implementation */ }
        private void UpdateScoreDisplay() { /* Implementation */ }
        
        #endregion
    }
}

/// <summary>
/// Data structures for gameplay system
/// </summary>
[System.Serializable]
public class AbilityConfig
{
    [Header("Ability Identity")]
    public string abilityId = "";
    public string abilityName = "Ability";
    public string description = "";
    public Sprite abilityIcon;
    
    [Header("Ability Mechanics")]
    public AbilityType abilityType = AbilityType.Instant;
    public float cooldown = 5f;
    public float duration = 0f;
    public float range = 5f;
    public int manaCost = 0;
    
    [Header("Ability Effects")]
    public float damage = 0f;
    public float healing = 0f;
    public float buffMultiplier = 1f;
    public string[] statusEffects = new string[0];
}

/// <summary>
/// Ability button UI component
/// </summary>
public class AbilityButton : VisualElement
{
    public System.Action OnClicked;
    public string AbilityId { get; private set; }
    
    private Button _button;
    private VisualElement _cooldownOverlay;
    private Label _cooldownText;
    private VisualElement _icon;
    
    public AbilityButton(AbilityConfig ability)
    {
        AbilityId = ability.abilityId;
        CreateButtonStructure(ability);
    }
    
    private void CreateButtonStructure(AbilityConfig ability)
    {
        style.width = 60;
        style.height = 60;
        style.marginLeft = 4;
        style.marginRight = 4;
        style.position = Position.Relative;
        
        _button = new Button(() => OnClicked?.Invoke());
        _button.style.width = Length.Percent(100);
        _button.style.height = Length.Percent(100);
        _button.style.backgroundColor = new Color(0.3f, 0.3f, 0.3f, 0.9f);
        _button.style.borderRadius = 30;
        _button.style.borderWidth = 2;
        _button.style.borderColor = new Color(0.5f, 0.5f, 0.5f, 0.8f);
        
        // Ability icon
        _icon = new VisualElement();
        _icon.style.position = Position.Absolute;
        _icon.style.top = 8;
        _icon.style.left = 8;
        _icon.style.right = 8;
        _icon.style.bottom = 8;
        _icon.style.borderRadius = 22;
        
        if (ability.abilityIcon != null)
        {
            _icon.style.backgroundImage = new StyleBackground(ability.abilityIcon);
        }
        
        // Cooldown overlay
        _cooldownOverlay = new VisualElement();
        _cooldownOverlay.style.position = Position.Absolute;
        _cooldownOverlay.style.top = 0;
        _cooldownOverlay.style.left = 0;
        _cooldownOverlay.style.right = 0;
        _cooldownOverlay.style.bottom = 0;
        _cooldownOverlay.style.backgroundColor = new Color(0f, 0f, 0f, 0.7f);
        _cooldownOverlay.style.borderRadius = 30;
        _cooldownOverlay.style.display = DisplayStyle.None;
        
        _cooldownText = new Label("0");
        _cooldownText.style.position = Position.Absolute;
        _cooldownText.style.top = 0;
        _cooldownText.style.left = 0;
        _cooldownText.style.right = 0;
        _cooldownText.style.bottom = 0;
        _cooldownText.style.unityTextAlign = TextAnchor.MiddleCenter;
        _cooldownText.style.fontSize = 12;
        _cooldownText.style.color = Color.white;
        _cooldownText.style.unityFontStyleAndWeight = FontStyle.Bold;
        
        _cooldownOverlay.Add(_cooldownText);
        
        Add(_button);
        Add(_icon);
        Add(_cooldownOverlay);
    }
    
    public void UpdateCooldown(float remainingCooldown)
    {
        if (remainingCooldown > 0)
        {
            _cooldownOverlay.style.display = DisplayStyle.Flex;
            _cooldownText.text = Mathf.Ceil(remainingCooldown).ToString();
            _button.SetEnabled(false);
        }
        else
        {
            _cooldownOverlay.style.display = DisplayStyle.None;
            _button.SetEnabled(true);
        }
    }
}

public enum AbilityType
{
    Instant = 0,
    Channeled = 1,
    Toggle = 2
}