using UnityEngine;
using UnityEngine.UIElements;
using System.Collections.Generic;
using System.Linq;

namespace MobileGameTemplate.Systems
{
    /// <summary>
    /// 🧿 INTENDED EXPANSION ZONE - Hero collection and management system
    /// Grid-based layout with evolution, rarity, and stats management
    /// Designed for collectible hero mechanics in mobile action games
    /// 
    /// Sacred Vision: Transform hero collection into engaging progression system!
    /// </summary>
    public class HeroCollectionSystem : VisualElement
    {
        #region USS Class Names
        public static readonly string UssClassName = "hero-collection";
        public static readonly string GridUssClassName = UssClassName + "__grid";
        public static readonly string FilterUssClassName = UssClassName + "__filter";
        public static readonly string DetailsUssClassName = UssClassName + "__details";
        public static readonly string CardUssClassName = UssClassName + "__card";
        public static readonly string CardSelectedUssClassName = CardUssClassName + "--selected";
        public static readonly string CardOwnedUssClassName = CardUssClassName + "--owned";
        public static readonly string CardLockedUssClassName = CardUssClassName + "--locked";
        #endregion
        
        #region Events
        public System.Action<HeroData> OnHeroSelected;
        public System.Action<HeroData> OnHeroEvolutionRequested;
        public System.Action<HeroData> OnHeroUpgradeRequested;
        public System.Action<HeroData> OnHeroEquipRequested;
        #endregion
        
        #region Private Fields
        private ScrollView _heroGrid;
        private VisualElement _gridContainer;
        private VisualElement _detailsPanel;
        private DropdownField _rarityFilter;
        private DropdownField _typeFilter;
        private Button _sortButton;
        private TextField _searchField;
        
        private List<HeroData> _allHeroes = new();
        private List<HeroData> _filteredHeroes = new();
        private readonly List<HeroCollectionCard> _heroCards = new();
        private HeroData _selectedHero;
        private HeroDetailsView _detailsView;
        
        private HeroSortMode _currentSortMode = HeroSortMode.Rarity;
        private HeroRarity _currentRarityFilter = HeroRarity.All;
        private HeroType _currentTypeFilter = HeroType.All;
        private string _currentSearchText = "";
        
        // Grid configuration
        private int _itemsPerRow = 3;
        private readonly float _cardWidth = 100f;
        private readonly float _cardHeight = 120f;
        private readonly float _cardSpacing = 8f;
        #endregion
        
        #region Constructor
        public HeroCollectionSystem()
        {
            AddToClassList(UssClassName);
            SetupCollectionStructure();
            SetupFilters();
            RegisterCallbacks();
        }
        #endregion
        
        #region Public API
        
        /// <summary>
        /// 🧿 Initialize hero collection with data
        /// </summary>
        public void InitializeCollection(List<HeroData> heroes)
        {
            _allHeroes = new List<HeroData>(heroes);
            RefreshCollection();
        }
        
        /// <summary>
        /// 🧿 Add new hero to collection
        /// </summary>
        public void AddHero(HeroData hero)
        {
            if (!_allHeroes.Any(h => h.heroId == hero.heroId))
            {
                _allHeroes.Add(hero);
                RefreshCollection();
            }
        }
        
        /// <summary>
        /// 🧿 Update hero data and refresh display
        /// </summary>
        public void UpdateHero(HeroData updatedHero)
        {
            var existingHero = _allHeroes.FirstOrDefault(h => h.heroId == updatedHero.heroId);
            if (existingHero != null)
            {
                int index = _allHeroes.IndexOf(existingHero);
                _allHeroes[index] = updatedHero;
                RefreshCollection();
                
                if (_selectedHero?.heroId == updatedHero.heroId)
                {
                    SelectHero(updatedHero);
                }
            }
        }
        
        /// <summary>
        /// 🧿 Select specific hero and show details
        /// </summary>
        public void SelectHero(HeroData hero)
        {
            _selectedHero = hero;
            UpdateHeroSelection();
            ShowHeroDetails(hero);
            OnHeroSelected?.Invoke(hero);
        }
        
        /// <summary>
        /// 🧿 Get currently selected hero
        /// </summary>
        public HeroData GetSelectedHero()
        {
            return _selectedHero;
        }
        
        #endregion
        
        #region Private Methods
        
        /// <summary>
        /// 🧿 Setup main collection UI structure
        /// </summary>
        private void SetupCollectionStructure()
        {
            style.width = Length.Percent(100);
            style.height = Length.Percent(100);
            style.flexDirection = FlexDirection.Row;
            
            // Left panel - hero grid
            var leftPanel = new VisualElement();
            leftPanel.style.width = Length.Percent(60);
            leftPanel.style.height = Length.Percent(100);
            leftPanel.style.paddingTop = 8;
            leftPanel.style.paddingBottom = 8;
            leftPanel.style.paddingLeft = 8;
            leftPanel.style.paddingRight = 4;
            
            // Hero grid scroll view
            _heroGrid = new ScrollView(ScrollViewMode.Vertical);
            _heroGrid.AddToClassList(GridUssClassName);
            _heroGrid.style.width = Length.Percent(100);
            _heroGrid.style.height = Length.Percent(100);
            
            _gridContainer = new VisualElement();
            _gridContainer.style.flexDirection = FlexDirection.Row;
            _gridContainer.style.flexWrap = Wrap.Wrap;
            _gridContainer.style.justifyContent = Justify.FlexStart;
            _gridContainer.style.paddingTop = 8;
            _gridContainer.style.paddingBottom = 8;
            
            _heroGrid.Add(_gridContainer);
            leftPanel.Add(_heroGrid);
            
            // Right panel - hero details
            _detailsPanel = new VisualElement();
            _detailsPanel.AddToClassList(DetailsUssClassName);
            _detailsPanel.style.width = Length.Percent(40);
            _detailsPanel.style.height = Length.Percent(100);
            _detailsPanel.style.paddingTop = 8;
            _detailsPanel.style.paddingBottom = 8;
            _detailsPanel.style.paddingLeft = 4;
            _detailsPanel.style.paddingRight = 8;
            _detailsPanel.style.backgroundColor = new Color(0.05f, 0.05f, 0.05f, 0.8f);
            //_detailsPanel.style.borderTopLeftRadius = 12;
            //_detailsPanel.style.borderTopRightRadius = 12;
            //_detailsPanel.style.borderBottomLeftRadius = 12;
            //_detailsPanel.style.borderBottomRightRadius = 12;
            //_detailsPanel.style.borderTopWidth = 1;
            //_detailsPanel.style.borderRightWidth = 1;
            //_detailsPanel.style.borderLeftWidth = 1;
            //_detailsPanel.style.borderBottomWidth = 1;
            //_detailsPanel.style.borderTopColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            //_detailsPanel.style.borderRightColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            //_detailsPanel.style.borderBottomColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            //_detailsPanel.style.borderLeftColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);

            CreateDetailsView();
            
            Add(leftPanel);
            Add(_detailsPanel);
        }
        
        /// <summary>
        /// 🧿 Setup filter and search controls
        /// </summary>
        private void SetupFilters()
        {
            var filterContainer = new VisualElement();
            filterContainer.AddToClassList(FilterUssClassName);
            filterContainer.style.flexDirection = FlexDirection.Row;
            filterContainer.style.height = 40;
            filterContainer.style.marginBottom = 8;
            filterContainer.style.paddingLeft = 8;
            filterContainer.style.paddingRight = 8;
            filterContainer.style.alignItems = Align.Center;
            
            // Search field
            _searchField = new TextField();
            _searchField.style.width = 120;
            _searchField.style.marginRight = 8;
            _searchField.SetValueWithoutNotify("Search...");
            
            // Rarity filter
            _rarityFilter = new DropdownField("Rarity");
            _rarityFilter.style.width = 100;
            _rarityFilter.style.marginRight = 8;
            _rarityFilter.choices = System.Enum.GetNames(typeof(HeroRarity)).ToList();
            _rarityFilter.SetValueWithoutNotify(HeroRarity.All.ToString());
            
            // Type filter
            _typeFilter = new DropdownField("Type");
            _typeFilter.style.width = 100;
            _typeFilter.style.marginRight = 8;
            _typeFilter.choices = System.Enum.GetNames(typeof(HeroType)).ToList();
            _typeFilter.SetValueWithoutNotify(HeroType.All.ToString());

            // Sort button
            _sortButton = new Button(CycleSortMode)
            {
                text = _currentSortMode.ToString()
            };
            _sortButton.style.width = 80;
            
            filterContainer.Add(_searchField);
            filterContainer.Add(_rarityFilter);
            filterContainer.Add(_typeFilter);
            filterContainer.Add(_sortButton);
            
            // Insert filter container at the top
            Insert(0, filterContainer);
        }
        
        /// <summary>
        /// 🧿 Create hero details view panel
        /// </summary>
        private void CreateDetailsView()
        {
            _detailsView = new HeroDetailsView();
            _detailsView.OnEvolutionRequested += (hero) => OnHeroEvolutionRequested?.Invoke(hero);
            _detailsView.OnUpgradeRequested += (hero) => OnHeroUpgradeRequested?.Invoke(hero);
            _detailsView.OnEquipRequested += (hero) => OnHeroEquipRequested?.Invoke(hero);
            
            _detailsPanel.Add(_detailsView);
        }
        
        /// <summary>
        /// 🧿 Register UI event callbacks
        /// </summary>
        private void RegisterCallbacks()
        {
            _searchField.RegisterValueChangedCallback(OnSearchChanged);
            _rarityFilter.RegisterValueChangedCallback(OnRarityFilterChanged);
            _typeFilter.RegisterValueChangedCallback(OnTypeFilterChanged);
        }
        
        /// <summary>
        /// 🧿 Refresh entire collection display
        /// </summary>
        private void RefreshCollection()
        {
            ApplyFilters();
            CreateHeroCards();
            UpdateLayout();
        }
        
        /// <summary>
        /// 🧿 Apply current filters to hero list
        /// </summary>
        private void ApplyFilters()
        {
            _filteredHeroes.Clear();
            
            foreach (var hero in _allHeroes)
            {
                bool passesFilter = true;
                
                // Rarity filter
                if (_currentRarityFilter != HeroRarity.All && hero.rarity != _currentRarityFilter)
                {
                    passesFilter = false;
                }
                
                // Type filter
                if (_currentTypeFilter != HeroType.All && hero.heroType != _currentTypeFilter)
                {
                    passesFilter = false;
                }
                
                // Search filter
                if (!string.IsNullOrEmpty(_currentSearchText) && _currentSearchText != "Search...")
                {
                    bool nameMatch = hero.heroName.ToLower().Contains(_currentSearchText.ToLower());
                    bool descMatch = hero.description.ToLower().Contains(_currentSearchText.ToLower());
                    if (!nameMatch && !descMatch)
                    {
                        passesFilter = false;
                    }
                }
                
                if (passesFilter)
                {
                    _filteredHeroes.Add(hero);
                }
            }
            
            // Apply sorting
            SortHeroes();
        }
        
        /// <summary>
        /// 🧿 Sort filtered heroes based on current sort mode
        /// </summary>
        private void SortHeroes()
        {
            switch (_currentSortMode)
            {
                case HeroSortMode.Name:
                    _filteredHeroes = _filteredHeroes.OrderBy(h => h.heroName).ToList();
                    break;
                case HeroSortMode.Rarity:
                    _filteredHeroes = _filteredHeroes.OrderByDescending(h => (int)h.rarity).ToList();
                    break;
                case HeroSortMode.Level:
                    _filteredHeroes = _filteredHeroes.OrderByDescending(h => h.level).ToList();
                    break;
                case HeroSortMode.Power:
                    _filteredHeroes = _filteredHeroes.OrderByDescending(h => h.CalculateTotalPower()).ToList();
                    break;
                case HeroSortMode.Owned:
                    _filteredHeroes = _filteredHeroes.OrderByDescending(h => h.isOwned).ThenBy(h => h.heroName).ToList();
                    break;
            }
        }
        
        /// <summary>
        /// 🧿 Create visual cards for filtered heroes
        /// </summary>
        private void CreateHeroCards()
        {
            // Clear existing cards
            _gridContainer.Clear();
            _heroCards.Clear();
            
            // Create new cards
            foreach (var hero in _filteredHeroes)
            {
                var card = new HeroCollectionCard(hero);
                card.OnClicked += SelectHero;
                
                _heroCards.Add(card);
                _gridContainer.Add(card);
            }
        }
        
        /// <summary>
        /// 🧿 Update grid layout based on screen size
        /// </summary>
        private void UpdateLayout()
        {
            // Calculate items per row based on available width
            float availableWidth = _heroGrid.resolvedStyle.width - 16; // Account for padding
            _itemsPerRow = Mathf.Max(2, Mathf.FloorToInt(availableWidth / (_cardWidth + _cardSpacing)));
            
            // Update card sizes if needed
            float actualCardWidth = (availableWidth - (_itemsPerRow - 1) * _cardSpacing) / _itemsPerRow;
            
            foreach (var card in _heroCards)
            {
                card.style.width = actualCardWidth;
                card.style.height = _cardHeight;
                card.style.marginLeft = _cardSpacing / 2;
                card.style.marginRight = _cardSpacing / 2;
                card.style.marginBottom = _cardSpacing;
            }
        }
        
        /// <summary>
        /// 🧿 Update visual selection state of hero cards
        /// </summary>
        private void UpdateHeroSelection()
        {
            foreach (var card in _heroCards)
            {
                card.SetSelected(card.HeroData?.heroId == _selectedHero?.heroId);
            }
        }
        
        /// <summary>
        /// 🧿 Show detailed information for selected hero
        /// </summary>
        private void ShowHeroDetails(HeroData hero)
        {
            _detailsView.ShowHero(hero);
        }
        
        /// <summary>
        /// 🧿 Cycle through sort modes
        /// </summary>
        private void CycleSortMode()
        {
            int currentIndex = (int)_currentSortMode;
            int nextIndex = (currentIndex + 1) % System.Enum.GetValues(typeof(HeroSortMode)).Length;
            _currentSortMode = (HeroSortMode)nextIndex;
            _sortButton.text = _currentSortMode.ToString();
            RefreshCollection();
        }
        
        #endregion
        
        #region Event Handlers
        
        private void OnSearchChanged(ChangeEvent<string> evt)
        {
            _currentSearchText = evt.newValue;
            RefreshCollection();
        }
        
        private void OnRarityFilterChanged(ChangeEvent<string> evt)
        {
            if (System.Enum.TryParse<HeroRarity>(evt.newValue, out HeroRarity rarity))
            {
                _currentRarityFilter = rarity;
                RefreshCollection();
            }
        }
        
        private void OnTypeFilterChanged(ChangeEvent<string> evt)
        {
            if (System.Enum.TryParse<HeroType>(evt.newValue, out HeroType type))
            {
                _currentTypeFilter = type;
                RefreshCollection();
            }
        }
        
        #endregion
        
        #region Factory Methods
        
        //public new class UxmlFactory : UxmlFactory<HeroCollectionSystem, UxmlTraits> { }
        
        //public new class UxmlTraits : VisualElement.UxmlTraits
        //{
        //    readonly UxmlIntAttributeDescription _itemsPerRow = new()
        //    { 
        //        name = "items-per-row", 
        //        defaultValue = 3 
        //    };

        //    readonly UxmlFloatAttributeDescription _cardWidth = new()
        //    { 
        //        name = "card-width", 
        //        defaultValue = 100f 
        //    };

        //    readonly UxmlFloatAttributeDescription _cardHeight = new()
        //    { 
        //        name = "card-height", 
        //        defaultValue = 120f 
        //    };
            
        //    public override void Init(VisualElement ve, IUxmlAttributes bag, CreationContext cc)
        //    {
        //        base.Init(ve, bag, cc);

        //        if (ve is HeroCollectionSystem collection)
        //        {
        //            collection._itemsPerRow = _itemsPerRow.GetValueFromBag(bag, cc);
        //            collection._cardWidth = _cardWidth.GetValueFromBag(bag, cc);
        //            collection._cardHeight = _cardHeight.GetValueFromBag(bag, cc);
        //        }
        //    }
        //}
        
        #endregion
    }
    
    /// <summary>
    /// Individual hero card in the collection grid
    /// </summary>
    public class HeroCollectionCard : VisualElement
    {
        public System.Action<HeroData> OnClicked;
        public HeroData HeroData { get; private set; }
        
        private VisualElement _background;
        private VisualElement _heroImage;
        private Label _heroName;
        private Label _heroLevel;
        private readonly VisualElement _rarityBorder; // 👀 - Needs a valid use
        private VisualElement _ownedIndicator;
        private VisualElement _lockIcon;
        
        public HeroCollectionCard(HeroData heroData)
        {
            HeroData = heroData;
            AddToClassList(HeroCollectionSystem.CardUssClassName);
            CreateCardStructure();
            UpdateVisualState();
            RegisterCallbacks();
        }
        
        private void CreateCardStructure()
        {
            style.width = 100;
            style.height = 120;
            style.marginLeft = 4;
            style.marginRight = 4;
            style.marginBottom = 8;
            style.cursor = StyleKeyword.Auto;
            
            // Background with rarity border
            _background = new VisualElement();
            _background.style.width = Length.Percent(100);
            _background.style.height = Length.Percent(100);
            _background.style.backgroundColor = new Color(0.1f, 0.1f, 0.1f, 0.9f);
            //_background.style.borderTopLeftRadius = 8;
            //_background.style.borderTopRightRadius = 8;
            //_background.style.borderBottomLeftRadius = 8;
            //_background.style.borderBottomRightRadius = 8;
            //_background.style.borderTopWidth = 2;
            //_background.style.borderRightWidth = 2;
            //_background.style.borderBottomWidth = 2;
            //_background.style.borderLeftWidth = 2;

            // Hero image placeholder
            _heroImage = new VisualElement();
            _heroImage.style.position = Position.Absolute;
            _heroImage.style.top = 8;
            _heroImage.style.left = 16;
            _heroImage.style.right = 16;
            _heroImage.style.height = 60;
            _heroImage.style.backgroundColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            //_heroImage.style.borderTopLeftRadius = 6;
            //_heroImage.style.borderTopRightRadius = 6;
            //_heroImage.style.borderBottomLeftRadius = 6;
            //_heroImage.style.borderBottomRightRadius = 6;

            // Hero name
            _heroName = new Label(HeroData.heroName);
            _heroName.style.position = Position.Absolute;
            _heroName.style.bottom = 20;
            _heroName.style.left = 4;
            _heroName.style.right = 4;
            _heroName.style.fontSize = 10;
            _heroName.style.color = Color.white;
            _heroName.style.unityTextAlign = TextAnchor.MiddleCenter;
            _heroName.style.overflow = Overflow.Hidden;
            
            // Hero level
            _heroLevel = new Label($"Lv.{HeroData.level}");
            _heroLevel.style.position = Position.Absolute;
            _heroLevel.style.bottom = 4;
            _heroLevel.style.left = 4;
            _heroLevel.style.right = 4;
            _heroLevel.style.fontSize = 8;
            _heroLevel.style.color = new Color(0.8f, 0.8f, 0.8f, 1f);
            _heroLevel.style.unityTextAlign = TextAnchor.MiddleCenter;
            
            // Owned indicator
            _ownedIndicator = new VisualElement();
            _ownedIndicator.style.position = Position.Absolute;
            _ownedIndicator.style.top = 4;
            _ownedIndicator.style.right = 4;
            _ownedIndicator.style.width = 12;
            _ownedIndicator.style.height = 12;
            _ownedIndicator.style.backgroundColor = new Color(0.3f, 0.7f, 0.3f, 1f);
            //_ownedIndicator.style.borderTopLeftRadius = 6;
            //_ownedIndicator.style.borderTopRightRadius = 6;
            //_ownedIndicator.style.borderBottomLeftRadius = 6;
            //_ownedIndicator.style.borderBottomRightRadius = 6;

            // Lock icon
            _lockIcon = new VisualElement();
            _lockIcon.style.position = Position.Absolute;
            _lockIcon.style.top = 30;
            _lockIcon.style.left = 35;
            _lockIcon.style.width = 30;
            _lockIcon.style.height = 30;
            _lockIcon.style.backgroundColor = new Color(0.5f, 0.5f, 0.5f, 0.9f);
            //_lockIcon.style.borderTopLeftRadius = 15;
            //_lockIcon.style.borderTopRightRadius = 15;
            //_lockIcon.style.borderBottomLeftRadius = 15;
            //_lockIcon.style.borderBottomRightRadius = 15;

            Add(_background);
            Add(_heroImage);
            Add(_heroName);
            Add(_heroLevel);
            Add(_ownedIndicator);
            Add(_lockIcon);
        }
        
        private void UpdateVisualState()
        {
            // Update rarity border color
            // Color rarityColor = GetRarityColor(HeroData.rarity);
            // Replace this line in HeroCollectionCard.UpdateVisualState():
            // _background.style.borderColor = rarityColor;

            // With the following lines to set all four border colors:
            //_background.style.borderTopColor = rarityColor;
            //_background.style.borderRightColor = rarityColor;
            //_background.style.borderBottomColor = rarityColor;
            //_background.style.borderLeftColor = rarityColor;
            
            // Update owned state
            if (HeroData.isOwned)
            {
                AddToClassList(HeroCollectionSystem.CardOwnedUssClassName);
                _ownedIndicator.style.display = DisplayStyle.Flex;
                _lockIcon.style.display = DisplayStyle.None;
                
                // Update level display
                _heroLevel.text = $"Lv.{HeroData.level}";
                if (HeroData.level >= HeroData.maxLevel)
                {
                    _heroLevel.style.color = new Color(1f, 0.8f, 0f, 1f); // Gold for max level
                }
            }
            else if (HeroData.isUnlocked)
            {
                RemoveFromClassList(HeroCollectionSystem.CardLockedUssClassName);
                _ownedIndicator.style.display = DisplayStyle.None;
                _lockIcon.style.display = DisplayStyle.None;
                _heroLevel.text = "Available";
                _heroLevel.style.color = new Color(0.3f, 0.7f, 0.3f, 1f);
            }
            else
            {
                AddToClassList(HeroCollectionSystem.CardLockedUssClassName);
                _ownedIndicator.style.display = DisplayStyle.None;
                _lockIcon.style.display = DisplayStyle.Flex;
                _heroLevel.text = "Locked";
                _heroLevel.style.color = new Color(0.5f, 0.5f, 0.5f, 1f);
                _background.style.backgroundColor = new Color(0.05f, 0.05f, 0.05f, 0.9f);
            }
            
            // Set hero image if available
            if (HeroData.heroIcon != null)
            {
                _heroImage.style.backgroundImage = new StyleBackground(HeroData.heroIcon);
            }
        }
        
        private Color GetRarityColor(HeroRarity rarity)
        {
            return rarity switch
            {
                HeroRarity.Common => new Color(0.6f, 0.6f, 0.6f, 1f),
                HeroRarity.Rare => new Color(0.2f, 0.5f, 0.9f, 1f),
                HeroRarity.Epic => new Color(0.6f, 0.2f, 0.9f, 1f),
                HeroRarity.Legendary => new Color(1f, 0.8f, 0f, 1f),
                HeroRarity.Mythic => new Color(1f, 0.3f, 0.3f, 1f),
                _ => new Color(0.4f, 0.4f, 0.4f, 1f)
            };
        }
        
        public void SetSelected(bool selected)
        {
            if (selected)
            {
                AddToClassList(HeroCollectionSystem.CardSelectedUssClassName);
                style.scale = new Scale(Vector3.one * 1.05f);
                _background.style.backgroundColor = new Color(0.2f, 0.3f, 0.4f, 1f);
            }
            else
            {
                RemoveFromClassList(HeroCollectionSystem.CardSelectedUssClassName);
                style.scale = new Scale(Vector3.one);
                UpdateVisualState();
            }
        }
        
        private void RegisterCallbacks()
        {
            RegisterCallback<ClickEvent>(OnCardClicked);
        }
        
        private void OnCardClicked(ClickEvent evt)
        {
            OnClicked?.Invoke(HeroData);
            evt.StopPropagation();
        }
    }
}

/// <summary>
/// Data structure for hero information
/// </summary>
[System.Serializable]
public class HeroData
{
    [Header("Hero Identity")]
    public string heroId = "";
    public string heroName = "Hero";
    public string description = "";
    public Sprite heroIcon;
    public Sprite heroPortrait;
    
    [Header("Hero Classification")]
    public HeroRarity rarity = HeroRarity.Common;
    public HeroType heroType = HeroType.Warrior;
    public HeroClass heroClass = HeroClass.Melee;
    
    [Header("Hero State")]
    public bool isOwned = false;
    public bool isUnlocked = true;
    public int level = 1;
    public int maxLevel = 30;
    public int evolutionStage = 0;
    public int maxEvolutionStage = 3;
    
    [Header("Hero Stats")]
    public int baseAttack = 100;
    public int baseDefense = 80;
    public int baseHealth = 500;
    public int baseSpeed = 100;
    public float criticalRate = 0.05f;
    public float criticalDamage = 1.5f;
    
    [Header("Hero Skills")]
    public string[] skillIds = new string[0];
    public string passiveSkillId = "";
    public string ultimateSkillId = "";
    
    [Header("Evolution Requirements")]
    public int evolutionCost = 1000;
    public string[] evolutionMaterials = new string[0];
    public int[] evolutionMaterialCounts = new int[0];
    
    [Header("Equipment")]
    public string equippedWeapon = "";
    public string equippedArmor = "";
    public string[] equippedAccessories = new string[3];
    
    /// <summary>
    /// Calculate total power rating for sorting
    /// </summary>
    public int CalculateTotalPower()
    {
        float levelMultiplier = 1f + (level - 1) * 0.1f;
        float evolutionMultiplier = 1f + evolutionStage * 0.25f;
        
        int totalStats = baseAttack + baseDefense + baseHealth / 5 + baseSpeed;
        return Mathf.RoundToInt(totalStats * levelMultiplier * evolutionMultiplier);
    }
    
    /// <summary>
    /// Get current stats with level and evolution bonuses
    /// </summary>
    public HeroStats GetCurrentStats()
    {
        float levelMultiplier = 1f + (level - 1) * 0.1f;
        float evolutionMultiplier = 1f + evolutionStage * 0.15f;
        
        return new HeroStats
        {
            attack = Mathf.RoundToInt(baseAttack * levelMultiplier * evolutionMultiplier),
            defense = Mathf.RoundToInt(baseDefense * levelMultiplier * evolutionMultiplier),
            health = Mathf.RoundToInt(baseHealth * levelMultiplier * evolutionMultiplier),
            speed = Mathf.RoundToInt(baseSpeed * levelMultiplier * evolutionMultiplier),
            criticalRate = criticalRate,
            criticalDamage = criticalDamage
        };
    }
    
    /// <summary>
    /// Check if hero can be evolved
    /// </summary>
    public bool CanEvolve()
    {
        return evolutionStage < maxEvolutionStage && level >= maxLevel;
    }
}

[System.Serializable]
public struct HeroStats
{
    public int attack;
    public int defense;
    public int health;
    public int speed;
    public float criticalRate;
    public float criticalDamage;
}

public enum HeroRarity
{
    All = -1,
    Common = 0,
    Rare = 1,
    Epic = 2,
    Legendary = 3,
    Mythic = 4
}

public enum HeroType
{
    All = -1,
    Warrior = 0,
    Mage = 1,
    Archer = 2,
    Rogue = 3,
    Support = 4,
    Tank = 5
}

public enum HeroClass
{
    Melee = 0,
    Ranged = 1,
    Magic = 2,
    Hybrid = 3
}

public enum HeroSortMode
{
    Name = 0,
    Rarity = 1,
    Level = 2,
    Power = 3,
    Owned = 4
}
