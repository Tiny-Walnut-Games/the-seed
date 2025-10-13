using UnityEngine;
using UnityEngine.UIElements;
using System.Collections.Generic;
using MobileGameTemplate.Core; // 🔧 LEGENDARY FIX: Import compatibility bridge

namespace MobileGameTemplate.UI
{
    /// <summary>
    /// 🎠 INTENDED EXPANSION ZONE - Mobile carousel level selector
    /// Touch-enabled horizontal scrolling with smooth animations
    /// Designed for Survivor.io/Archer.io style level progression
    /// 
    /// Sacred Vision: Transform level selection into smooth, engaging carousel experience!
    /// </summary>
    public class LevelCarousel : VisualElement
    {
        #region USS Class Names
        public static readonly string UssClassName = "level-carousel";
        public static readonly string ContainerUssClassName = UssClassName + "__container";
        public static readonly string ViewportUssClassName = UssClassName + "__viewport";
        public static readonly string ContentUssClassName = UssClassName + "__content";
        public static readonly string ItemUssClassName = UssClassName + "__item";
        public static readonly string ItemActiveUssClassName = ItemUssClassName + "--active";
        public static readonly string ItemLockedUssClassName = ItemUssClassName + "--locked";
        public static readonly string ItemCompletedUssClassName = ItemUssClassName + "--completed";
        #endregion
        
        #region Events
        public System.Action<LevelData> OnLevelSelected;
        public System.Action<LevelData> OnLevelDetailsRequested;
        #endregion
        
        #region Private Fields
        private VisualElement _viewport;
        private VisualElement _content;
        private List<LevelCarouselItem> _levelItems = new List<LevelCarouselItem>();
        private List<LevelData> _levelData = new List<LevelData>();
        
        // Touch and scroll handling
        private Vector2 _lastPointerPosition;
        private Vector2 _velocity;
        private bool _isDragging;
        private float _scrollPosition;
        private float _targetScrollPosition;
        private int _currentIndex = 0;
        
        // Configuration
        private float _itemWidth = 200f;
        private float _itemSpacing = 20f;
        private float _snapThreshold = 0.3f;
        private float _scrollDamping = 0.85f;
        private float _animationSpeed = 8f;
        private bool _enableHapticFeedback = true;
        #endregion
        
        #region Constructor
        public LevelCarousel()
        {
            AddToClassList(UssClassName);
            SetupCarouselStructure();
            RegisterCallbacks();
        }
        #endregion
        
        #region Public API
        
        /// <summary>
        /// 🎠 Initialize carousel with level data
        /// </summary>
        public void SetLevelData(List<LevelData> levels)
        {
            _levelData = levels;
            CreateLevelItems();
            SnapToLevel(0, false);
        }
        
        /// <summary>
        /// 🎠 Navigate to specific level with animation
        /// </summary>
        public void NavigateToLevel(int levelIndex, bool animated = true)
        {
            if (levelIndex < 0 || levelIndex >= _levelData.Count)
            {
                Debug.LogWarning($"🎠 Level index {levelIndex} out of range!");
                return;
            }
            
            SnapToLevel(levelIndex, animated);
            
            if (_enableHapticFeedback)
            {
                TriggerHapticFeedback();
            }
        }
        
        /// <summary>
        /// 🎠 Get currently visible level index
        /// </summary>
        public int GetCurrentLevelIndex()
        {
            return _currentIndex;
        }
        
        /// <summary>
        /// 🎠 Get level data for current selection
        /// </summary>
        public LevelData GetCurrentLevel()
        {
            if (_currentIndex >= 0 && _currentIndex < _levelData.Count)
            {
                return _levelData[_currentIndex];
            }
            return null;
        }
        
        #endregion
        
        #region Private Methods
        
        /// <summary>
        /// 🎠 Setup carousel DOM structure
        /// </summary>
        private void SetupCarouselStructure()
        {
            // Main container
            AddToClassList(ContainerUssClassName);
            
            // Viewport (visible area)
            _viewport = new VisualElement();
            _viewport.AddToClassList(ViewportUssClassName);
            _viewport.style.overflow = Overflow.Hidden;
            _viewport.style.width = Length.Percent(100);
            _viewport.style.height = 300;
            
            // Content container (scrollable)
            _content = new VisualElement();
            _content.AddToClassList(ContentUssClassName);
            _content.style.flexDirection = FlexDirection.Row;
            _content.style.position = Position.Relative;
            _content.style.height = Length.Percent(100);
            
            _viewport.Add(_content);
            Add(_viewport);
        }
        
        /// <summary>
        /// 🎠 Register touch and pointer callbacks
        /// </summary>
        private void RegisterCallbacks()
        {
            RegisterCallback<PointerDownEvent>(OnPointerDown);
            RegisterCallback<PointerMoveEvent>(OnPointerMove);
            RegisterCallback<PointerUpEvent>(OnPointerUp);
            RegisterCallback<WheelEvent>(OnWheel);
            
            // Update loop for smooth scrolling
            schedule.Execute(UpdateScrolling).Every(16); // ~60 FPS
        }
        
        /// <summary>
        /// 🎠 Create visual items for each level
        /// </summary>
        private void CreateLevelItems()
        {
            // Clear existing items
            _content.Clear();
            _levelItems.Clear();
            
            // Create level items
            for (int i = 0; i < _levelData.Count; i++)
            {
                var levelData = _levelData[i];
                var levelItem = new LevelCarouselItem(levelData, i);
                
                levelItem.OnClicked += (data, index) => {
                    NavigateToLevel(index);
                    OnLevelSelected?.Invoke(data);
                };
                
                levelItem.OnDetailsRequested += (data, index) => {
                    OnLevelDetailsRequested?.Invoke(data);
                };
                
                _content.Add(levelItem);
                _levelItems.Add(levelItem);
            }
            
            UpdateContentWidth();
        }
        
        /// <summary>
        /// 🎠 Update content container width based on items
        /// </summary>
        private void UpdateContentWidth()
        {
            if (_levelItems.Count > 0)
            {
                float totalWidth = (_itemWidth + _itemSpacing) * _levelItems.Count;
                _content.style.width = totalWidth;
            }
        }
        
        /// <summary>
        /// 🎠 Snap to specific level position
        /// </summary>
        private void SnapToLevel(int levelIndex, bool animated = true)
        {
            if (levelIndex < 0 || levelIndex >= _levelItems.Count)
                return;
            
            float targetPosition = CalculatePositionForLevel(levelIndex);
            
            if (animated)
            {
                _targetScrollPosition = targetPosition;
            }
            else
            {
                _scrollPosition = targetPosition;
                _targetScrollPosition = targetPosition;
                ApplyScrollPosition();
            }
            
            UpdateActiveLevel(levelIndex);
        }
        
        /// <summary>
        /// 🎠 Calculate scroll position for specific level
        /// </summary>
        private float CalculatePositionForLevel(int levelIndex)
        {
            float viewportWidth = _viewport.resolvedStyle.width;
            float itemPosition = levelIndex * (_itemWidth + _itemSpacing);
            
            // Center the item in viewport
            float centeredPosition = itemPosition - (viewportWidth / 2) + (_itemWidth / 2);
            
            // Clamp to valid scroll range
            float maxScroll = Mathf.Max(0, _content.resolvedStyle.width - viewportWidth);
            return Mathf.Clamp(centeredPosition, 0, maxScroll);
        }
        
        /// <summary>
        /// 🎠 Update visual state for active level
        /// </summary>
        private void UpdateActiveLevel(int newIndex)
        {
            if (newIndex == _currentIndex)
                return;
            
            // Remove active state from previous item
            if (_currentIndex >= 0 && _currentIndex < _levelItems.Count)
            {
                _levelItems[_currentIndex].SetActive(false);
            }
            
            // Add active state to new item
            _currentIndex = newIndex;
            if (_currentIndex >= 0 && _currentIndex < _levelItems.Count)
            {
                _levelItems[_currentIndex].SetActive(true);
            }
        }
        
        /// <summary>
        /// 🎠 Apply current scroll position to content
        /// </summary>
        private void ApplyScrollPosition()
        {
            _content.style.left = -_scrollPosition;
        }
        
        /// <summary>
        /// 🎠 Update scrolling animation and physics
        /// </summary>
        private void UpdateScrolling()
        {
            // Smooth scrolling towards target
            if (!_isDragging)
            {
                float difference = _targetScrollPosition - _scrollPosition;
                
                if (Mathf.Abs(difference) > 0.1f)
                {
                    _scrollPosition += difference * _animationSpeed * Time.unscaledDeltaTime;
                    ApplyScrollPosition();
                }
                else
                {
                    _scrollPosition = _targetScrollPosition;
                    ApplyScrollPosition();
                }
            }
            
            // Apply velocity damping
            _velocity *= _scrollDamping;
        }
        
        /// <summary>
        /// 🎠 Find closest level to current scroll position
        /// </summary>
        private int FindClosestLevel()
        {
            float viewportCenter = _scrollPosition + (_viewport.resolvedStyle.width / 2);
            int closestIndex = 0;
            float closestDistance = float.MaxValue;
            
            for (int i = 0; i < _levelItems.Count; i++)
            {
                float itemCenter = i * (_itemWidth + _itemSpacing) + (_itemWidth / 2);
                float distance = Mathf.Abs(itemCenter - viewportCenter);
                
                if (distance < closestDistance)
                {
                    closestDistance = distance;
                    closestIndex = i;
                }
            }
            
            return closestIndex;
        }
        
        private void TriggerHapticFeedback()
        {
            // Platform-specific haptic feedback implementation
            #if UNITY_ANDROID && !UNITY_EDITOR
            // Android haptic feedback
            #elif UNITY_IOS && !UNITY_EDITOR
            // iOS haptic feedback
            #endif
        }
        
        #endregion
        
        #region Event Handlers
        
        private void OnPointerDown(PointerDownEvent evt)
        {
            _lastPointerPosition = new Vector2(evt.position.x, evt.position.y); // 🔧 LEGENDARY FIX: Direct Vector2 conversion
            _isDragging = true;
            _velocity = Vector2.zero;
            evt.StopPropagation();
        }
        
        private void OnPointerMove(PointerMoveEvent evt)
        {
            if (!_isDragging)
                return;
            
            Vector2 currentPos = new Vector2(evt.position.x, evt.position.y); // 🔧 LEGENDARY FIX: Direct Vector2 conversion
            Vector2 delta = currentPos - _lastPointerPosition;
            _velocity = delta;
            
            // Apply horizontal scrolling
            _scrollPosition -= delta.x;
            
            // Clamp scroll position
            float maxScroll = Mathf.Max(0, _content.resolvedStyle.width - _viewport.resolvedStyle.width);
            _scrollPosition = Mathf.Clamp(_scrollPosition, 0, maxScroll);
            
            ApplyScrollPosition();
            _lastPointerPosition = currentPos;
            
            evt.StopPropagation();
        }
        
        private void OnPointerUp(PointerUpEvent evt)
        {
            if (!_isDragging)
                return;
            
            _isDragging = false;
            
            // Apply momentum scrolling
            float momentum = _velocity.x * 0.5f;
            
            // Find closest level and snap to it
            int targetLevel = FindClosestLevel();
            
            // Check if we should snap based on velocity threshold
            if (Mathf.Abs(_velocity.x) > 100f) // Minimum swipe velocity
            {
                if (_velocity.x > 0 && targetLevel > 0)
                {
                    targetLevel--;
                }
                else if (_velocity.x < 0 && targetLevel < _levelItems.Count - 1)
                {
                    targetLevel++;
                }
            }
            
            NavigateToLevel(targetLevel, true);
            evt.StopPropagation();
        }
        
        private void OnWheel(WheelEvent evt)
        {
            // Handle mouse wheel scrolling (for editor testing)
            float scrollDelta = evt.delta.y * 50f;
            _scrollPosition += scrollDelta;
            
            float maxScroll = Mathf.Max(0, _content.resolvedStyle.width - _viewport.resolvedStyle.width);
            _scrollPosition = Mathf.Clamp(_scrollPosition, 0, maxScroll);
            
            int targetLevel = FindClosestLevel();
            SnapToLevel(targetLevel, true);
            
            evt.StopPropagation();
        }
        
        #endregion
        
        #region Factory Methods
        
        public new class UxmlFactory : UxmlFactory<LevelCarousel, UxmlTraits> { }
        
        public new class UxmlTraits : VisualElement.UxmlTraits
        {
            UxmlFloatAttributeDescription _itemWidth = new UxmlFloatAttributeDescription 
            { 
                name = "item-width", 
                defaultValue = 200f 
            };
            
            UxmlFloatAttributeDescription _itemSpacing = new UxmlFloatAttributeDescription 
            { 
                name = "item-spacing", 
                defaultValue = 20f 
            };
            
            UxmlBoolAttributeDescription _enableHapticFeedback = new UxmlBoolAttributeDescription 
            { 
                name = "enable-haptic-feedback", 
                defaultValue = true 
            };
            
            public override void Init(VisualElement ve, IUxmlAttributes bag, CreationContext cc)
            {
                base.Init(ve, bag, cc);
                
                var carousel = ve as LevelCarousel;
                if (carousel != null)
                {
                    carousel._itemWidth = _itemWidth.GetValueFromBag(bag, cc);
                    carousel._itemSpacing = _itemSpacing.GetValueFromBag(bag, cc);
                    carousel._enableHapticFeedback = _enableHapticFeedback.GetValueFromBag(bag, cc);
                }
            }
        }
        
        #endregion
    }
    
    /// <summary>
    /// Individual level item in the carousel (Unity 2022.3 Compatible)
    /// </summary>
    public class LevelCarouselItem : VisualElement
    {
        public System.Action<LevelData, int> OnClicked;
        public System.Action<LevelData, int> OnDetailsRequested;
        
        private LevelData _levelData;
        private int _levelIndex;
        private VisualElement _background;
        private Label _levelNumber;
        private Label _levelName;
        private VisualElement _starsContainer;
        private VisualElement _lockIcon;
        private Button _playButton;
        private Button _detailsButton;
        
        public LevelCarouselItem(LevelData levelData, int index)
        {
            _levelData = levelData;
            _levelIndex = index;
            
            AddToClassList(LevelCarousel.ItemUssClassName);
            CreateItemStructure();
            UpdateVisualState();
        }
        
        private void CreateItemStructure()
        {
            style.width = 200;
            style.height = 280;
            style.marginLeft = 10;
            style.marginRight = 10;
            
            // Background - Unity 2022.3 Compatible
            _background = new VisualElement();
            _background.style.width = Length.Percent(100);
            _background.style.height = Length.Percent(100);
            _background.style.backgroundColor = new Color(0.1f, 0.1f, 0.1f, 0.8f);
            
            // Level number
            _levelNumber = new Label(_levelData.levelNumber.ToString());
            _levelNumber.style.fontSize = 24;
            _levelNumber.style.color = Color.white;
            _levelNumber.style.unityTextAlign = TextAnchor.MiddleCenter;
            _levelNumber.style.position = Position.Absolute;
            _levelNumber.style.top = 20;
            _levelNumber.style.left = 0;
            _levelNumber.style.right = 0;
            
            // Level name
            _levelName = new Label(_levelData.levelName);
            _levelName.style.fontSize = 14;
            _levelName.style.color = Color.white;
            _levelName.style.unityTextAlign = TextAnchor.MiddleCenter;
            _levelName.style.position = Position.Absolute;
            _levelName.style.top = 60;
            _levelName.style.left = 10;
            _levelName.style.right = 10;
            
            // Stars container
            _starsContainer = new VisualElement();
            _starsContainer.style.flexDirection = FlexDirection.Row;
            _starsContainer.style.justifyContent = Justify.Center;
            _starsContainer.style.position = Position.Absolute;
            _starsContainer.style.top = 100;
            _starsContainer.style.left = 0;
            _starsContainer.style.right = 0;
            
            CreateStars();
            
            // Lock icon - Unity 2022.3 Compatible
            _lockIcon = new VisualElement();
            _lockIcon.style.width = 40;
            _lockIcon.style.height = 40;
            _lockIcon.style.position = Position.Absolute;
            _lockIcon.style.top = 120;
            _lockIcon.style.left = 80;
            _lockIcon.style.backgroundColor = new Color(0.5f, 0.5f, 0.5f, 0.8f);
            
            // Play button
            _playButton = new Button(() => OnClicked?.Invoke(_levelData, _levelIndex));
            _playButton.text = "PLAY";
            _playButton.style.position = Position.Absolute;
            _playButton.style.bottom = 60;
            _playButton.style.left = 40;
            _playButton.style.right = 40;
            _playButton.style.height = 40;
            _playButton.style.backgroundColor = new Color(0.3f, 0.7f, 0.3f, 0.9f);
            _playButton.style.fontSize = 14;
            _playButton.style.color = Color.white;
            
            // Details button - Unity 2022.3 Compatible
            _detailsButton = new Button(() => OnDetailsRequested?.Invoke(_levelData, _levelIndex));
            _detailsButton.text = "...";
            _detailsButton.style.position = Position.Absolute;
            _detailsButton.style.bottom = 20;
            _detailsButton.style.right = 20;
            _detailsButton.style.width = 30;
            _detailsButton.style.height = 30;
            _detailsButton.style.backgroundColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            _detailsButton.style.fontSize = 12;
            _detailsButton.style.color = Color.white;
            
            Add(_background);
            Add(_levelNumber);
            Add(_levelName);
            Add(_starsContainer);
            Add(_lockIcon);
            Add(_playButton);
            Add(_detailsButton);
        }
        
        private void CreateStars()
        {
            for (int i = 0; i < 3; i++)
            {
                var star = new VisualElement();
                star.style.width = 20;
                star.style.height = 20;
                star.style.marginLeft = 2;
                star.style.marginRight = 2;
                star.style.backgroundColor = i < _levelData.starsEarned ? 
                    new Color(1f, 0.8f, 0f, 1f) : 
                    new Color(0.3f, 0.3f, 0.3f, 0.8f);
                // 🔧 LEGENDARY FIX: Use compatibility extension
                _starsContainer.Add(star);
            }
        }
        
        private void UpdateVisualState()
        {
            // Update based on level state
            if (_levelData.isLocked)
            {
                AddToClassList(LevelCarousel.ItemLockedUssClassName);
                _lockIcon.style.display = DisplayStyle.Flex;
                _playButton.style.display = DisplayStyle.None;
                _playButton.SetEnabled(false);
            }
            else if (_levelData.isCompleted)
            {
                AddToClassList(LevelCarousel.ItemCompletedUssClassName);
                _lockIcon.style.display = DisplayStyle.None;
                _playButton.style.display = DisplayStyle.Flex;
                _playButton.SetEnabled(true);
            }
            else
            {
                _lockIcon.style.display = DisplayStyle.None;
                _playButton.style.display = DisplayStyle.Flex;
                _playButton.SetEnabled(true);
            }
        }
        
        public void SetActive(bool active)
        {
            if (active)
            {
                AddToClassList(LevelCarousel.ItemActiveUssClassName);
                style.scale = new Scale(Vector3.one * 1.1f);
            }
            else
            {
                RemoveFromClassList(LevelCarousel.ItemActiveUssClassName);
                style.scale = new Scale(Vector3.one);
                UpdateVisualState();
            }
        }
    }
}

/// <summary>
/// Data structure for level information
/// </summary>
[System.Serializable]
public class LevelData
{
    [Header("Level Identity")]
    public int levelNumber = 1;
    public string levelId = "";
    public string levelName = "Level 1";
    public string description = "";
    
    [Header("Level State")]
    public bool isLocked = false;
    public bool isCompleted = false;
    public int starsEarned = 0;
    public float bestTime = 0f;
    public int highScore = 0;
    
    [Header("Level Configuration")]
    public string sceneName = "";
    public Sprite thumbnailImage;
    public LevelDifficulty difficulty = LevelDifficulty.Easy;
    public LevelType levelType = LevelType.Standard;
    
    [Header("Rewards")]
    public int coinReward = 100;
    public int expReward = 50;
    public string[] unlockItems = new string[0];
}

public enum LevelDifficulty
{
    Easy,
    Medium,
    Hard,
    Expert
}

public enum LevelType
{
    Standard,
    Boss,
    Survival,
    Challenge,
    Daily
}
