using UnityEngine;
using UnityEngine.UIElements;
using MobileGameTemplate.Core; // 🔧 Unity 2022.3 Compatibility Bridge
using System.Collections.Generic;
using System.Linq; // 🔧 C# 10 Compatibility

namespace MobileGameTemplate.Systems
{
    /// <summary>
    /// 🛒 INTENDED EXPANSION ZONE - Merchant and shop system
    /// Item purchasing, currency management, and shop rotation for mobile games
    /// Designed for monetization and progression in action mobile games
    /// 
    /// Sacred Vision: Transform shopping into engaging economic progression!
    /// </summary>
    public class ShopSystem : VisualElement
    {
        #region USS Class Names
        public static readonly string UssClassName = "shop-system";
        public static readonly string TabUssClassName = UssClassName + "__tab";
        public static readonly string TabActiveUssClassName = TabUssClassName + "--active";
        public static readonly string ContentUssClassName = UssClassName + "__content";
        public static readonly string CurrencyUssClassName = UssClassName + "__currency";
        public static readonly string ItemGridUssClassName = UssClassName + "__item-grid";
        public static readonly string ShopItemUssClassName = UssClassName + "__shop-item";
        #endregion
        
        #region Events
        public System.Action<ShopItem, CurrencyType> OnItemPurchased;
        public System.Action<ShopItem> OnItemDetailsRequested;
        public System.Action OnShopRefreshRequested;
        public System.Action<CurrencyType> OnCurrencyInfoRequested;
        #endregion
        
        #region Private Fields
        private VisualElement _headerContainer;
        private VisualElement _currencyContainer;
        private VisualElement _tabContainer;
        private VisualElement _contentContainer;
        
        // Currency displays
        private Label _goldLabel;
        private Label _gemsLabel;
        private Label _tokensLabel;
        private Button _buyGemsButton;
        
        // Shop tabs
        private Button _generalTab;
        private Button _weaponsTab;
        private Button _materialsTab;
        private Button _specialTab;
        
        // Content areas
        private ScrollView _shopGrid;
        private VisualElement _gridContainer;
        private VisualElement _refreshContainer;
        private Label _refreshTimeLabel;
        private Button _refreshButton;
        
        // Data
        private PlayerCurrency _playerCurrency;
        private List<ShopItem> _allShopItems = new List<ShopItem>();
        private List<ShopItem> _currentItems = new List<ShopItem>();
        private ShopCategory _activeCategory = ShopCategory.General;
        private System.DateTime _nextRefreshTime;
        
        // Configuration
        private int _itemsPerRow = 2;
        private float _itemWidth = 160f;
        private float _itemHeight = 200f;
        private float _itemSpacing = 8f;
        #endregion
        
        #region Constructor
        public ShopSystem()
        {
            AddToClassList(UssClassName);
            SetupShopStructure();
            SetupCurrencyDisplay();
            SetupTabs();
            SetupShopGrid();
            RegisterCallbacks();
        }
        #endregion
        
        #region Public API
        
        /// <summary>
        /// 🛒 Initialize shop with player currency and available items
        /// </summary>
        public void InitializeShop(PlayerCurrency currency, List<ShopItem> shopItems)
        {
            _playerCurrency = currency;
            _allShopItems = new List<ShopItem>(shopItems);
            UpdateCurrencyDisplay();
            RefreshShopItems();
        }
        
        /// <summary>
        /// 🛒 Update player currency display
        /// </summary>
        public void UpdateCurrency(PlayerCurrency currency)
        {
            _playerCurrency = currency;
            UpdateCurrencyDisplay();
            RefreshItemAffordability();
        }
        
        /// <summary>
        /// 🛒 Add new shop items (for daily rotation, events, etc.)
        /// </summary>
        public void UpdateShopItems(List<ShopItem> newItems, System.DateTime nextRefresh)
        {
            _allShopItems = new List<ShopItem>(newItems);
            _nextRefreshTime = nextRefresh;
            RefreshShopItems();
            UpdateRefreshDisplay();
        }
        
        /// <summary>
        /// 🛒 Purchase item if player has sufficient currency
        /// </summary>
        public bool PurchaseItem(ShopItem item, CurrencyType currencyType)
        {
            if (!CanAffordItem(item, currencyType))
                return false;
            
            // Deduct currency
            switch (currencyType)
            {
                case CurrencyType.Gold:
                    _playerCurrency.gold -= item.goldPrice;
                    break;
                case CurrencyType.Gems:
                    _playerCurrency.gems -= item.gemPrice;
                    break;
                case CurrencyType.Tokens:
                    _playerCurrency.tokens -= item.tokenPrice;
                    break;
            }
            
            // Remove from shop if limited quantity
            if (item.isLimited)
            {
                item.remainingQuantity--;
                if (item.remainingQuantity <= 0)
                {
                    _allShopItems.Remove(item);
                }
            }
            
            UpdateCurrencyDisplay();
            RefreshShopItems();
            OnItemPurchased?.Invoke(item, currencyType);
            return true;
        }
        
        /// <summary>
        /// 🛒 Switch to specific shop category
        /// </summary>
        public void SwitchToCategory(ShopCategory category)
        {
            SetActiveCategory(category);
        }
        
        #endregion
        
        #region Private Methods
        
        /// <summary>
        /// 🛒 Setup main shop UI structure
        /// </summary>
        private void SetupShopStructure()
        {
            style.width = Length.Percent(100);
            style.height = Length.Percent(100);
            style.flexDirection = FlexDirection.Column;
            
            // Header with currency and refresh info
            _headerContainer = new VisualElement();
            _headerContainer.style.paddingTop = 8;
            _headerContainer.style.paddingBottom = 8;
            _headerContainer.style.paddingLeft = 16;
            _headerContainer.style.paddingRight = 16;
            
            // Tab container
            _tabContainer = new VisualElement();
            _tabContainer.style.flexDirection = FlexDirection.Row;
            _tabContainer.style.height = 50;
            _tabContainer.style.backgroundColor = new Color(0.1f, 0.1f, 0.1f, 0.9f);
            _tabContainer.style.borderBottomWidth = 2;
            _tabContainer.style.borderBottomColor = new Color(0.3f, 0.3f, 0.3f, 0.8f);
            
            // Content container
            _contentContainer = new VisualElement();
            _contentContainer.AddToClassList(ContentUssClassName);
            _contentContainer.style.flexGrow = 1;
            _contentContainer.style.paddingTop = 8;
            _contentContainer.style.paddingBottom = 8;
            _contentContainer.style.paddingLeft = 8;
            _contentContainer.style.paddingRight = 8;
            
            Add(_headerContainer);
            Add(_tabContainer);
            Add(_contentContainer);
        }
        
        /// <summary>
        /// 🛒 Setup currency display in header
        /// </summary>
        private void SetupCurrencyDisplay()
        {
            _currencyContainer = new VisualElement();
            _currencyContainer.AddToClassList(CurrencyUssClassName);
            _currencyContainer.style.flexDirection = FlexDirection.Row;
            _currencyContainer.style.justifyContent = Justify.SpaceBetween;
            _currencyContainer.style.alignItems = Align.Center;
            _currencyContainer.style.marginBottom = 8;
            
            // Currency displays
            var currencyRow = new VisualElement();
            currencyRow.style.flexDirection = FlexDirection.Row;
            currencyRow.style.alignItems = Align.Center;
            
            // Gold
            var goldContainer = CreateCurrencyDisplay("🪙", "0", new Color(1f, 0.8f, 0f, 1f));
            _goldLabel = goldContainer.Q<Label>("amount");
            
            // Gems
            var gemContainer = CreateCurrencyDisplay("💎", "0", new Color(0.3f, 0.8f, 1f, 1f));
            _gemsLabel = gemContainer.Q<Label>("amount");
            
            // Tokens
            var tokenContainer = CreateCurrencyDisplay("🎫", "0", new Color(0.8f, 0.3f, 1f, 1f));
            _tokensLabel = tokenContainer.Q<Label>("amount");
            
            currencyRow.Add(goldContainer);
            currencyRow.Add(gemContainer);
            currencyRow.Add(tokenContainer);
            
            // Buy gems button
            _buyGemsButton = new Button(() => OnCurrencyInfoRequested?.Invoke(CurrencyType.Gems));
            _buyGemsButton.text = "BUY GEMS";
            _buyGemsButton.style.paddingLeft = 16;
            _buyGemsButton.style.paddingRight = 16;
            _buyGemsButton.style.paddingTop = 8;
            _buyGemsButton.style.paddingBottom = 8;
            _buyGemsButton.style.backgroundColor = new Color(0.3f, 0.8f, 1f, 0.9f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
// 🔧 LEGENDARY FIX: borderWidth not available in Unity 2022.3
            _buyGemsButton.style.color = Color.white;
            _buyGemsButton.style.fontSize = 12;
            
            _currencyContainer.Add(currencyRow);
            _currencyContainer.Add(_buyGemsButton);
            
            _headerContainer.Add(_currencyContainer);
        }
        
        /// <summary>
        /// 🛒 Create individual currency display
        /// </summary>
        private VisualElement CreateCurrencyDisplay(string icon, string amount, Color iconColor)
        {
            var container = new VisualElement();
            container.style.flexDirection = FlexDirection.Row;
            container.style.alignItems = Align.Center;
            container.style.backgroundColor = new Color(0.1f, 0.1f, 0.1f, 0.6f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
            container.style.paddingLeft = 12;
            container.style.paddingRight = 12;
            container.style.paddingTop = 8;
            container.style.paddingBottom = 8;
            container.style.marginRight = 8;
            
            var iconLabel = new Label(icon);
            iconLabel.style.fontSize = 16;
            iconLabel.style.marginRight = 6;
            
            var amountLabel = new Label(amount);
            amountLabel.name = "amount";
            amountLabel.style.fontSize = 14;
            amountLabel.style.color = Color.white;
            amountLabel.style.unityFontStyleAndWeight = FontStyle.Bold;
            
            container.Add(iconLabel);
            container.Add(amountLabel);
            
            return container;
        }
        
        /// <summary>
        /// 🛒 Setup shop category tabs
        /// </summary>
        private void SetupTabs()
        {
            _generalTab = CreateTab("General", ShopCategory.General);
            _weaponsTab = CreateTab("Weapons", ShopCategory.Weapons);
            _materialsTab = CreateTab("Materials", ShopCategory.Materials);
            _specialTab = CreateTab("Special", ShopCategory.Special);
            
            _tabContainer.Add(_generalTab);
            _tabContainer.Add(_weaponsTab);
            _tabContainer.Add(_materialsTab);
            _tabContainer.Add(_specialTab);
            
            SetActiveCategory(ShopCategory.General);
        }
        
        /// <summary>
        /// 🛒 Create individual shop tab
        /// </summary>
        private Button CreateTab(string label, ShopCategory category)
        {
            var button = new Button(() => SetActiveCategory(category));
            button.text = label;
            button.AddToClassList(TabUssClassName);
            button.style.flexGrow = 1;
            button.style.height = Length.Percent(100);
            button.style.backgroundColor = Color.clear;
// 🔧 LEGENDARY FIX: borderWidth not available in Unity 2022.3
            button.style.fontSize = 14;
            button.style.color = new Color(0.7f, 0.7f, 0.7f, 1f);
            
            return button;
        }
        
        /// <summary>
        /// 🛒 Setup shop item grid
        /// </summary>
        private void SetupShopGrid()
        {
            // Refresh info container
            _refreshContainer = new VisualElement();
            _refreshContainer.style.flexDirection = FlexDirection.Row;
            _refreshContainer.style.justifyContent = Justify.SpaceBetween;
            _refreshContainer.style.alignItems = Align.Center;
            _refreshContainer.style.marginBottom = 16;
            _refreshContainer.style.paddingLeft = 8;
            _refreshContainer.style.paddingRight = 8;
            
            _refreshTimeLabel = new Label();
            _refreshTimeLabel.style.fontSize = 12;
            _refreshTimeLabel.style.color = new Color(0.7f, 0.7f, 0.7f, 1f);
            
            _refreshButton = new Button(() => OnShopRefreshRequested?.Invoke());
            _refreshButton.text = "REFRESH";
            _refreshButton.style.paddingLeft = 12;
            _refreshButton.style.paddingRight = 12;
            _refreshButton.style.paddingTop = 6;
            _refreshButton.style.paddingBottom = 6;
            _refreshButton.style.backgroundColor = new Color(0.5f, 0.3f, 0.8f, 0.9f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
// 🔧 LEGENDARY FIX: borderWidth not available in Unity 2022.3
            _refreshButton.style.color = Color.white;
            _refreshButton.style.fontSize = 12;
            
            _refreshContainer.Add(_refreshTimeLabel);
            _refreshContainer.Add(_refreshButton);
            
            // Shop grid
            _shopGrid = new ScrollView(ScrollViewMode.Vertical);
            _shopGrid.AddToClassList(ItemGridUssClassName);
            _shopGrid.style.flexGrow = 1;
            
            _gridContainer = new VisualElement();
            _gridContainer.style.flexDirection = FlexDirection.Row;
            _gridContainer.style.flexWrap = Wrap.Wrap;
            _gridContainer.style.justifyContent = Justify.FlexStart;
            _gridContainer.style.paddingTop = 8;
            _gridContainer.style.paddingBottom = 8;
            
            _shopGrid.Add(_gridContainer);
            
            _contentContainer.Add(_refreshContainer);
            _contentContainer.Add(_shopGrid);
        }
        
        /// <summary>
        /// 🛒 Register UI event callbacks
        /// </summary>
        private void RegisterCallbacks()
        {
            // Start refresh time update loop
            schedule.Execute(UpdateRefreshDisplay).Every(1000); // Update every second
        }
        
        /// <summary>
        /// 🛒 Set active shop category and filter items
        /// </summary>
        private void SetActiveCategory(ShopCategory category)
        {
            // Update tab visual states
            _generalTab.RemoveFromClassList(TabActiveUssClassName);
            _weaponsTab.RemoveFromClassList(TabActiveUssClassName);
            _materialsTab.RemoveFromClassList(TabActiveUssClassName);
            _specialTab.RemoveFromClassList(TabActiveUssClassName);
            
            _activeCategory = category;
            
            switch (category)
            {
                case ShopCategory.General:
                    _generalTab.AddToClassList(TabActiveUssClassName);
                    break;
                case ShopCategory.Weapons:
                    _weaponsTab.AddToClassList(TabActiveUssClassName);
                    break;
                case ShopCategory.Materials:
                    _materialsTab.AddToClassList(TabActiveUssClassName);
                    break;
                case ShopCategory.Special:
                    _specialTab.AddToClassList(TabActiveUssClassName);
                    break;
            }
            
            UpdateTabStyles();
            RefreshShopItems();
        }
        
        /// <summary>
        /// 🛒 Update visual styles for active/inactive tabs
        /// </summary>
        private void UpdateTabStyles()
        {
            var tabs = new[] { _generalTab, _weaponsTab, _materialsTab, _specialTab };
            
            foreach (var tab in tabs)
            {
                if (tab.ClassListContains(TabActiveUssClassName))
                {
                    tab.style.backgroundColor = new Color(0.2f, 0.3f, 0.4f, 0.9f);
                    tab.style.color = Color.white;
                }
                else
                {
                    tab.style.backgroundColor = Color.clear;
                    tab.style.color = new Color(0.7f, 0.7f, 0.7f, 1f);
                }
            }
        }
        
        /// <summary>
        /// 🛒 Update currency display labels
        /// </summary>
        private void UpdateCurrencyDisplay()
        {
            if (_playerCurrency != null)
            {
                _goldLabel.text = FormatCurrency(_playerCurrency.gold);
                _gemsLabel.text = FormatCurrency(_playerCurrency.gems);
                _tokensLabel.text = FormatCurrency(_playerCurrency.tokens);
            }
        }
        
        /// <summary>
        /// 🛒 Format currency numbers for display
        /// </summary>
        private string FormatCurrency(int amount)
        {
            if (amount >= 1000000)
                return $"{amount / 1000000f:F1}M";
            else if (amount >= 1000)
                return $"{amount / 1000f:F1}K";
            else
                return amount.ToString();
        }
        
        /// <summary>
        /// 🛒 Refresh shop items based on active category
        /// </summary>
        private void RefreshShopItems()
        {
            // Filter items by category
            _currentItems = _allShopItems.Where(item => 
                _activeCategory == ShopCategory.All || item.category == _activeCategory).ToList();
            
            // Clear and rebuild grid
            _gridContainer.Clear();
            
            foreach (var item in _currentItems)
            {
                var itemCard = CreateShopItemCard(item);
                _gridContainer.Add(itemCard);
            }
            
            UpdateItemLayout();
        }
        
        /// <summary>
        /// 🛒 Update shop item layout based on screen size
        /// </summary>
        private void UpdateItemLayout()
        {
            float availableWidth = _shopGrid.resolvedStyle.width - 16;
            _itemsPerRow = Mathf.Max(1, Mathf.FloorToInt(availableWidth / (_itemWidth + _itemSpacing)));
            
            float actualItemWidth = (availableWidth - (_itemsPerRow - 1) * _itemSpacing) / _itemsPerRow;
            
            foreach (var child in _gridContainer.Children())
            {
                child.style.width = actualItemWidth;
                child.style.height = _itemHeight;
                child.style.marginLeft = _itemSpacing / 2;
                child.style.marginRight = _itemSpacing / 2;
                child.style.marginBottom = _itemSpacing;
            }
        }
        
        /// <summary>
        /// 🛒 Create visual card for shop item
        /// </summary>
        private VisualElement CreateShopItemCard(ShopItem item)
        {
            var card = new VisualElement();
            card.AddToClassList(ShopItemUssClassName);
            card.style.backgroundColor = new Color(0.15f, 0.15f, 0.15f, 0.8f);
            card.style.paddingTop = 12;
            card.style.paddingBottom = 12;
            card.style.paddingLeft = 12;
            card.style.paddingRight = 12;
            
            // Item image
            var itemImage = new VisualElement();
            itemImage.style.position = Position.Absolute;
            itemImage.style.top = 12;
            itemImage.style.left = 12;
            itemImage.style.right = 12;
            itemImage.style.height = 80;
            itemImage.style.backgroundColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
            
            if (item.itemData?.itemIcon != null)
            {
                itemImage.style.backgroundImage = new StyleBackground(item.itemData.itemIcon);
            }
            
            // Item name
            var itemName = new Label(item.itemData?.itemName ?? "Item");
            itemName.style.position = Position.Absolute;
            itemName.style.top = 100;
            itemName.style.left = 8;
            itemName.style.right = 8;
            itemName.style.fontSize = 12;
            itemName.style.color = Color.white;
            itemName.style.unityFontStyleAndWeight = FontStyle.Bold;
            itemName.style.unityTextAlign = TextAnchor.MiddleCenter;
            itemName.style.overflow = Overflow.Hidden;
            
            // Quantity/Limited indicator
            if (item.isLimited)
            {
                var limitedLabel = new Label($"Limited: {item.remainingQuantity}");
                limitedLabel.style.position = Position.Absolute;
                limitedLabel.style.top = 120;
                limitedLabel.style.left = 8;
                limitedLabel.style.right = 8;
                limitedLabel.style.fontSize = 10;
                limitedLabel.style.color = new Color(1f, 0.8f, 0f, 1f);
                limitedLabel.style.unityTextAlign = TextAnchor.MiddleCenter;
                card.Add(limitedLabel);
            }
            
            // Price buttons
            var priceContainer = new VisualElement();
            priceContainer.style.position = Position.Absolute;
            priceContainer.style.bottom = 8;
            priceContainer.style.left = 8;
            priceContainer.style.right = 8;
            priceContainer.style.flexDirection = FlexDirection.Column;
            
            // Create price buttons for available currencies
            if (item.goldPrice > 0)
            {
                // Create purchase buttons with proper method signature
                var goldButton = CreatePriceButton(item, CurrencyType.Gold, item.goldPrice);
                goldButton.text = $"🪙 {item.goldPrice}";
                priceContainer.Add(goldButton);
            }
            
            if (item.gemPrice > 0)
            {
                // Create purchase buttons with proper method signature
                var gemButton = CreatePriceButton(item, CurrencyType.Gems, item.gemPrice);
                gemButton.text = $"💎 {item.gemPrice}";
                priceContainer.Add(gemButton);
            }
            
            if (item.tokenPrice > 0)
            {
                // Create purchase buttons with proper method signature
                var tokenButton = CreatePriceButton(item, CurrencyType.Tokens, item.tokenPrice);
                tokenButton.text = $"🎫 {item.tokenPrice}";
                priceContainer.Add(tokenButton);
            }
            
            card.Add(itemImage);
            card.Add(itemName);
            card.Add(priceContainer);
            
            // Add click for details
            card.RegisterCallback<ClickEvent>(evt => OnItemDetailsRequested?.Invoke(item));
            
            return card;
        }
        
        /// <summary>
        /// 🛒 Create price button for specific currency
        /// </summary>
        private Button CreatePriceButton(ShopItem item, CurrencyType currencyType, int price)
        {
            var button = new Button(() => PurchaseItem(item, currencyType));
            button.style.flexDirection = FlexDirection.Row;
            button.style.justifyContent = Justify.Center;
            button.style.alignItems = Align.Center;
            button.style.height = 24;
            button.style.marginBottom = 2;
            button.style.backgroundColor = GetCurrencyColor(currencyType);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
// 🔧 LEGENDARY FIX: borderWidth not available in Unity 2022.3
            button.style.fontSize = 10;
            button.style.color = Color.white;
            
            // Check affordability
            bool canAfford = CanAffordItem(item, currencyType);
            button.SetEnabled(canAfford && (!item.isLimited || item.remainingQuantity > 0));
            
            if (!canAfford)
            {
                button.style.backgroundColor = new Color(0.3f, 0.3f, 0.3f, 0.8f);
            }
            
            return button;
        }
        
        /// <summary>
        /// 🛒 Check if player can afford item with specific currency
        /// </summary>
        private bool CanAffordItem(ShopItem item, CurrencyType currencyType)
        {
            if (_playerCurrency == null) return false;
            
            return currencyType switch
            {
                CurrencyType.Gold => _playerCurrency.gold >= item.goldPrice,
                CurrencyType.Gems => _playerCurrency.gems >= item.gemPrice,
                CurrencyType.Tokens => _playerCurrency.tokens >= item.tokenPrice,
                _ => false
            };
        }
        
        /// <summary>
        /// 🛒 Refresh item affordability without rebuilding entire grid
        /// </summary>
        private void RefreshItemAffordability()
        {
            // This would update existing item cards without full rebuild
            RefreshShopItems(); // Simplified for now
        }
        
        /// <summary>
        /// 🛒 Update refresh timer display
        /// </summary>
        private void UpdateRefreshDisplay()
        {
            if (_nextRefreshTime > System.DateTime.Now)
            {
                var timeRemaining = _nextRefreshTime - System.DateTime.Now;
                _refreshTimeLabel.text = $"Refresh in: {timeRemaining.Hours:D2}:{timeRemaining.Minutes:D2}:{timeRemaining.Seconds:D2}";
                _refreshButton.SetEnabled(false);
            }
            else
            {
                _refreshTimeLabel.text = "Shop refresh available";
                _refreshButton.SetEnabled(true);
            }
        }
        
        /// <summary>
        /// 🛒 Get color for item rarity
        /// </summary>
        private Color GetRarityColor(ItemRarity rarity)
        {
            return rarity switch
            {
                ItemRarity.Common => new Color(0.6f, 0.6f, 0.6f, 1f),
                ItemRarity.Rare => new Color(0.2f, 0.5f, 0.9f, 1f),
                ItemRarity.Epic => new Color(0.6f, 0.2f, 0.9f, 1f),
                ItemRarity.Legendary => new Color(1f, 0.8f, 0f, 1f),
                ItemRarity.Mythic => new Color(1f, 0.3f, 0.3f, 1f),
                _ => new Color(0.4f, 0.4f, 0.4f, 1f)
            };
        }
        
        /// <summary>
        /// 🛒 Get color for currency type
        /// </summary>
        private Color GetCurrencyColor(CurrencyType currencyType)
        {
            return currencyType switch
            {
                CurrencyType.Gold => new Color(1f, 0.8f, 0f, 0.9f),
                CurrencyType.Gems => new Color(0.3f, 0.8f, 1f, 0.9f),
                CurrencyType.Tokens => new Color(0.8f, 0.3f, 1f, 0.9f),
                _ => new Color(0.5f, 0.5f, 0.5f, 0.9f)
            };
        }
        
        #endregion
        
        #region Factory Methods
        
        public new class UxmlFactory : UxmlFactory<ShopSystem, UxmlTraits> { }
        
        public new class UxmlTraits : VisualElement.UxmlTraits
        {
            UxmlIntAttributeDescription _itemsPerRow = new UxmlIntAttributeDescription 
            { 
                name = "items-per-row", 
                defaultValue = 2 
            };
            
            UxmlFloatAttributeDescription _itemWidth = new UxmlFloatAttributeDescription 
            { 
                name = "item-width", 
                defaultValue = 160f 
            };
            
            UxmlFloatAttributeDescription _itemHeight = new UxmlFloatAttributeDescription 
            { 
                name = "item-height", 
                defaultValue = 200f 
            };
            
            public override void Init(VisualElement ve, IUxmlAttributes bag, CreationContext cc)
            {
                base.Init(ve, bag, cc);
                
                var shop = ve as ShopSystem;
                if (shop != null)
                {
                    shop._itemsPerRow = _itemsPerRow.GetValueFromBag(bag, cc);
                    shop._itemWidth = _itemWidth.GetValueFromBag(bag, cc);
                    shop._itemHeight = _itemHeight.GetValueFromBag(bag, cc);
                }
            }
        }
        
        #endregion
    }
}

/// <summary>
/// Data structures for shop system
/// </summary>
[System.Serializable]
public class PlayerCurrency
{
    public int gold = 1000;
    public int gems = 50;
    public int tokens = 10;
}

[System.Serializable]
public class ShopItem
{
    [Header("Shop Item Identity")]
    public string shopItemId = "";
    public string displayName = "";
    public string description = "";
    public ItemData itemData;
    
    [Header("Shop Properties")]
    public ShopCategory category = ShopCategory.General;
    public ItemRarity rarity = ItemRarity.Common;
    public bool isLimited = false;
    public int remainingQuantity = 1;
    public int maxQuantity = 1;
    
    [Header("Pricing")]
    public int goldPrice = 0;
    public int gemPrice = 0;
    public int tokenPrice = 0;
    
    [Header("Availability")]
    public bool isAvailable = true;
    public System.DateTime availableFrom = System.DateTime.Now;
    public System.DateTime availableUntil = System.DateTime.MaxValue;
    public int playerLevelRequired = 1;
    
    [Header("Shop Display")]
    public bool isFeatured = false;
    public bool isOnSale = false;
    public float discountPercentage = 0f;
    public string saleTag = "";
}

public enum ShopCategory
{
    All = -1,
    General = 0,
    Weapons = 1,
    Armor = 2,
    Materials = 3,
    Consumables = 4,
    Special = 5
}

public enum CurrencyType
{
    Gold = 0,
    Gems = 1,
    Tokens = 2
}
