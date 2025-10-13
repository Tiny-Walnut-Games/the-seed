using UnityEngine;
using UnityEngine.UIElements;
using System.Collections.Generic;
using System.Linq;
using System;

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
        private readonly float _moveSpeed = 5f;
        private readonly float _touchSensitivity = 1f; // Enhanced touch responsiveness multiplier
        private readonly bool _enableVirtualJoystick = true;
        
        [Header("🎯 Auto-Aim System")]
        private readonly float _autoAimRange = 10f;
        private readonly float _autoAimAngle = 45f;
        [SerializeField] private LayerMask _enemyLayer = 1 << 8;
        private readonly bool _enableAutoAim = true;
        [SerializeField] private Transform _aimIndicator; // Visual target indicator for enhanced UX

        [Header("⚡ Ability System")]
        [SerializeField] private List<AbilityConfig> _abilities = new();
        private readonly float _globalCooldownReduction = 1f;
        
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
        private readonly List<GameObject> _nearbyEnemies = new();
        private float _lastTargetScanTime;
        private const float TARGET_SCAN_INTERVAL = 0.1f;
        
        // Ability tracking
        private readonly Dictionary<string, float> _abilityCooldowns = new();
        private readonly Dictionary<string, bool> _abilityActive = new();
        
        // UI elements
        private VisualElement _rootElement;
        private VisualElement _joystickContainer;
        private VisualElement _joystickKnob;
        private VisualElement _abilityContainer;
        private readonly List<AbilityButton> _abilityButtons = new();
        private Label _scoreLabel;
        private Button _pauseButton;
        
        // Game state
        private bool _isGamePaused;
        private int _currentScore;
        private Vector2 _playerVelocity;
        
        // Performance optimization
        private WaitForSeconds _targetScanWait;
        private readonly Collider [ ] _enemyColliders = new Collider[50]; // Reusable array
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

        private void UpdateAimIndicator()
        {
            if (_aimIndicator == null || _currentTarget == null) return;
            
            // Position aim indicator at current target
            _aimIndicator.position = _currentTarget.transform.position;
            _aimIndicator.gameObject.SetActive(true);
            
            // Point indicator towards target
            Vector3 directionToTarget = (_currentTarget.transform.position - _player.position).normalized;
            _aimIndicator.rotation = Quaternion.LookRotation(directionToTarget);
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
            
            _abilities ??= new List<AbilityConfig>();
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

            _joystickContainer = new VisualElement
            {
                name = "joystick-container"
            };

            _joystickContainer.style.position = Position.Absolute;
            _joystickContainer.style.bottom = 60;
            _joystickContainer.style.left = 40;
            _joystickContainer.style.width = 120;
            _joystickContainer.style.height = 120;
            _joystickContainer.style.backgroundColor = new Color(0.2f, 0.2f, 0.2f, 0.6f);

            _joystickKnob = new VisualElement
            {
                name = "joystick-knob"
            };
            _joystickKnob.style.position = Position.Absolute;
            _joystickKnob.style.width = 40;
            _joystickKnob.style.height = 40;
            _joystickKnob.style.backgroundColor = new Color(0.8f, 0.8f, 0.8f, 0.9f);
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
            _abilityContainer = new VisualElement
            {
                name = "ability-container"
            };
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

            // Pause button
            _pauseButton = new Button(TogglePause)
            {
                text = "⏸"
            };
            _pauseButton.style.position = Position.Absolute;
            _pauseButton.style.top = 20;
            _pauseButton.style.right = 20;
            _pauseButton.style.width = 50;
            _pauseButton.style.height = 50;
            _pauseButton.style.fontSize = 20;
            _pauseButton.style.backgroundColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            _pauseButton.style.color = Color.white;
            
            _rootElement.Add(_scoreLabel);
            _rootElement.Add(_pauseButton);
        }
        
        private void RegisterUICallbacks() 
        { 
            // Register touch/mouse callbacks for virtual joystick
            if (_joystickContainer != null)
            {
                _joystickContainer.RegisterCallback<PointerDownEvent>(OnJoystickPointerDown);
                _joystickContainer.RegisterCallback<PointerMoveEvent>(OnJoystickPointerMove);
                _joystickContainer.RegisterCallback<PointerUpEvent>(OnJoystickPointerUp);
            }
        }
        
        private void InitializeAbilities() 
        { 
            // Initialize ability cooldowns and state
            foreach (var ability in _abilities)
            {
                if (!string.IsNullOrEmpty(ability.abilityId))
                {
                    _abilityCooldowns[ability.abilityId] = 0f;
                    _abilityActive[ability.abilityId] = false;
                }
            }
        }
        
        private void HandleInput() 
        { 
            // Handle touch input for mobile
            if (Input.touchCount > 0)
            {
                var touch = Input.GetTouch(0);
                
                switch (touch.phase)
                {
                    case TouchPhase.Began:
                        _touchStartPosition = touch.position;
                        _currentTouchPosition = touch.position;
                        _isTouching = true;
                        _primaryTouchId = touch.fingerId;
                        break;
                        
                    case TouchPhase.Moved:
                        if (touch.fingerId == _primaryTouchId)
                        {
                            _currentTouchPosition = touch.position;
                            UpdateMovementFromTouch();
                        }
                        break;
                        
                    case TouchPhase.Ended:
                    case TouchPhase.Canceled:
                        if (touch.fingerId == _primaryTouchId)
                        {
                            _isTouching = false;
                            _moveDirection = Vector2.zero;
                            _primaryTouchId = -1;
                        }
                        break;
                }
            }
            
            // Handle mouse input for desktop testing
            if (Input.GetMouseButtonDown(0))
            {
                _touchStartPosition = Input.mousePosition;
                _currentTouchPosition = Input.mousePosition;
                _isTouching = true;
            }
            else if (Input.GetMouseButton(0) && _isTouching)
            {
                _currentTouchPosition = Input.mousePosition;
                UpdateMovementFromTouch();
            }
            else if (Input.GetMouseButtonUp(0))
            {
                _isTouching = false;
                _moveDirection = Vector2.zero;
            }
        }
        
        private void UpdatePlayerMovement() 
        { 
            // Convert screen movement to world movement
            if (_isTouching && _moveDirection.magnitude > _joystickDeadZone)
            {
                Vector3 worldMovement = _gameCamera.ScreenToWorldPoint(new Vector3(_moveDirection.x, _moveDirection.y, _gameCamera.nearClipPlane));
                _playerVelocity = new Vector2(worldMovement.x, worldMovement.z).normalized * _moveSpeed;
                
                OnPlayerMoved?.Invoke(_playerVelocity);
            }
            else
            {
                _playerVelocity = Vector2.zero;
                OnPlayerStopped?.Invoke(_playerVelocity);
            }
        }
        
        private void ApplyPlayerMovement() 
        { 
            // Apply movement to player transform
            if (_player != null && _playerVelocity.magnitude > 0)
            {
                Vector3 movement = new Vector3(_playerVelocity.x, 0, _playerVelocity.y) * Time.fixedDeltaTime;
                _player.position += movement;
            }
        }
        
        private void UpdateAbilityCooldowns() 
        { 
            // Update all ability cooldowns
            var keys = _abilityCooldowns.Keys.ToList();
            foreach (var abilityId in keys)
            {
                if (_abilityCooldowns[abilityId] > 0)
                {
                    _abilityCooldowns[abilityId] -= Time.deltaTime;
                    
                    // Update UI button if available
                    var button = _abilityButtons.Find(b => b.AbilityId == abilityId);
                    button?.UpdateCooldown(_abilityCooldowns[abilityId]);
                }
            }
        }
        
        private void UpdateAutoAim() 
        { 
            // Update auto-aim system if enabled
            if (!_enableAutoAim) return;
            
            if (Time.time - _lastTargetScanTime >= TARGET_SCAN_INTERVAL)
            {
                _lastTargetScanTime = Time.time;
                ScanForTargets();
            }
            
            // Update aim indicator if we have a target
            if (_currentTarget != null)
            {
                UpdateAimIndicator();
            }
        }
        
        private System.Collections.IEnumerator TargetScanLoop() 
        { 
            while (true)
            {
                if (_enableAutoAim)
                {
                    ScanForTargets();
                }
                yield return _targetScanWait;
            }
        }
        
        private void ExecuteAbility(AbilityConfig ability) 
        { 
            // Execute the ability based on its type
            switch (ability.abilityType)
            {
                case AbilityType.Instant:
                    ExecuteInstantAbility(ability);
                    break;
                case AbilityType.Channeled:
                    StartCoroutine(ExecuteChanneledAbility(ability));
                    break;
                case AbilityType.Toggle:
                    ToggleAbility(ability);
                    break;
            }
            
            // Set cooldown
            _abilityCooldowns[ability.abilityId] = ability.cooldown * _globalCooldownReduction;
            
            OnAbilityTriggered?.Invoke(ability.abilityId);
        }
        
        private void UpdateScoreDisplay() 
        { 
            if (_scoreLabel != null)
            {
                _scoreLabel.text = $"Score: {_currentScore:N0}";
            }
        }
        
        private void UpdateMovementFromTouch()
        {
            Vector2 delta = _currentTouchPosition - _touchStartPosition;
            
            // Apply touch sensitivity for responsive controls
            Vector2 adjustedDelta = delta * _touchSensitivity;
            _moveDirection = adjustedDelta.normalized;
            
            // Update virtual joystick position if available
            UpdateVirtualJoystickVisuals(adjustedDelta);
        }
        
        private void UpdateVirtualJoystickVisuals(Vector2 delta)
        {
            if (_joystickKnob == null) return;
            
            // Constrain delta to joystick area
            float maxDistance = 40f; // Half of joystick container size
            Vector2 constrainedDelta = Vector2.ClampMagnitude(delta * 0.1f, maxDistance);
            
            // Update knob position
            _joystickKnob.style.left = 40 + constrainedDelta.x; // Center position + offset
            _joystickKnob.style.top = 40 + constrainedDelta.y;
        }
        
        private void ScanForTargets()
        {
            if (_player == null) return;
            
            // Use Physics.OverlapSphereNonAlloc for performance
            int hitCount = Physics.OverlapSphereNonAlloc(
                _player.position, 
                _autoAimRange, 
                _enemyColliders, 
                _enemyLayer
            );
            
            _nearbyEnemies.Clear();
            GameObject bestTarget = null;
            float closestDistance = float.MaxValue;
            
            for (int i = 0; i < hitCount; i++)
            {
                var enemy = _enemyColliders[i].gameObject;
                _nearbyEnemies.Add(enemy);
                
                // Find closest enemy within aim angle
                Vector3 directionToEnemy = (enemy.transform.position - _player.position).normalized;
                Vector3 playerForward = _player.forward;
                
                float angle = Vector3.Angle(playerForward, directionToEnemy);
                if (angle <= _autoAimAngle * 0.5f)
                {
                    float distance = Vector3.Distance(_player.position, enemy.transform.position);
                    if (distance < closestDistance)
                    {
                        closestDistance = distance;
                        bestTarget = enemy;
                    }
                }
            }
            
            // Update current target
            if (bestTarget != _currentTarget)
            {
                _currentTarget = bestTarget;
                OnEnemyTargeted?.Invoke(_currentTarget);
            }
        }
        
        private void ExecuteInstantAbility(AbilityConfig ability)
        {
            // Instant effect ability (e.g., heal, damage boost)
            Debug.Log($"Executed instant ability: {ability.abilityName}");
            
            // Apply instant effects based on ability configuration
            if (ability.healing > 0)
            {
                // Apply healing
                Debug.Log($"Healing for {ability.healing}");
            }
            
            if (ability.damage > 0 && _currentTarget != null)
            {
                // Apply damage to current target
                Debug.Log($"Dealing {ability.damage} damage to {_currentTarget.name}");
            }
        }
        
        private System.Collections.IEnumerator ExecuteChanneledAbility(AbilityConfig ability)
        {
            // Channeled ability that lasts for a duration
            _abilityActive[ability.abilityId] = true;
            
            float timeRemaining = ability.duration;
            while (timeRemaining > 0 && _abilityActive[ability.abilityId])
            {
                // Apply channeled effects each frame
                timeRemaining -= Time.deltaTime;
                yield return null;
            }
            
            _abilityActive[ability.abilityId] = false;
        }
        
        private void ToggleAbility(AbilityConfig ability)
        {
            // Toggle ability on/off
            _abilityActive[ability.abilityId] = !_abilityActive[ability.abilityId];
            
            if (_abilityActive[ability.abilityId])
            {
                Debug.Log($"Activated toggle ability: {ability.abilityName}");
            }
            else
            {
                Debug.Log($"Deactivated toggle ability: {ability.abilityName}");
            }
        }
        
        private void OnJoystickPointerDown(PointerDownEvent evt)
        {
            _touchStartPosition = evt.position;
            _currentTouchPosition = evt.position;
            _isTouching = true;
        }
        
        private void OnJoystickPointerMove(PointerMoveEvent evt)
        {
            if (_isTouching)
            {
                _currentTouchPosition = evt.position;
                UpdateMovementFromTouch();
            }
        }
        
        private void OnJoystickPointerUp(PointerUpEvent evt)
        {
            _isTouching = false;
            _moveDirection = Vector2.zero;
            
            // Reset joystick knob to center
            if (_joystickKnob != null)
            {
                _joystickKnob.style.left = 40;
                _joystickKnob.style.top = 40;
            }
        }
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
        
        // Ability icon
        _icon = new VisualElement();
        _icon.style.position = Position.Absolute;
        _icon.style.top = 8;
        _icon.style.left = 8;
        _icon.style.right = 8;
        _icon.style.bottom = 8;
        
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
