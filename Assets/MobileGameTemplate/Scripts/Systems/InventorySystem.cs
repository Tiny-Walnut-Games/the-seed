using UnityEngine;
using UnityEngine.UIElements;
using System.Collections.Generic;
using System.Linq;

namespace MobileGameTemplate.Systems
{
    /// <summary>
    /// 🎒 INTENDED EXPANSION ZONE - Mobile inventory system with drag-drop
    /// Touch-optimized item management with sorting, filtering, and quick-use
    /// Designed for action mobile games with equipment and consumable items
    /// 
    /// Sacred Vision: Transform inventory chaos into smooth item management!
    /// </summary>
    public class InventorySystem : VisualElement
    {
        #region USS Class Names
        public static readonly string UssClassName = "inventory-system";
        public static readonly string GridUssClassName = UssClassName + "__grid";
        public static readonly string SlotUssClassName = UssClassName + "__slot";
        public static readonly string SlotEmptyUssClassName = SlotUssClassName + "--empty";
        public static readonly string SlotEquippedUssClassName = SlotUssClassName + "--equipped";
        public static readonly string SlotDragPreviewUssClassName = SlotUssClassName + "--drag-preview";
        public static readonly string FilterUssClassName = UssClassName + "__filter";
        public static readonly string DetailsUssClassName = UssClassName + "__details";
        #endregion
        
        #region Events
        public System.Action<ItemData> OnItemSelected;
        public System.Action<ItemData> OnItemUsed;
        public System.Action<ItemData> OnItemEquipped;
        public System.Action<ItemData> OnItemSold;
        public System.Action<ItemData, int> OnItemMoved;
        #endregion
        
        #region Private Fields
        private ScrollView _inventoryGrid;
        private VisualElement _gridContainer;
        private VisualElement _equipmentPanel;
        private VisualElement _detailsPanel;
        private DropdownField _categoryFilter;
        private DropdownField _sortFilter;
        private TextField _searchField;
        private Button _sortButton;
        
        private readonly List<InventorySlot> _inventorySlots = new();
        private readonly List<EquipmentSlot> _equipmentSlots = new();
        private readonly Dictionary<string, ItemData> _allItems = new();
        private List<InventoryItem> _playerInventory = new();
        private Dictionary<string, InventoryItem> _equippedItems = new();
        
        private ItemData _selectedItem;
        private InventorySlot _draggedSlot;
        private VisualElement _dragPreview;
        private bool _isDragging;
        
        // Configuration
        private readonly int _slotsPerRow = 6;
        private readonly int _totalSlots = 48;
        private readonly float _slotSize = 60f; // @copilot, value is never used. Needs an interesting use.
        private readonly float _slotSpacing = 4f;
        private ItemCategory _currentCategoryFilter = ItemCategory.All;
        private ItemSortMode _currentSortMode = ItemSortMode.Type;
        #endregion
        
        #region Constructor
        public InventorySystem()
        {
            AddToClassList(UssClassName);
            SetupInventoryStructure();
            SetupEquipmentPanel();
            SetupFilters();
            InitializeSlots();
            RegisterCallbacks();
        }
        #endregion
        
        #region Public API
        
        /// <summary>
        /// 🎒 Initialize inventory with player data
        /// </summary>
        public void InitializeInventory(List<InventoryItem> items, Dictionary<string, InventoryItem> equipped)
        {
            _playerInventory = new List<InventoryItem>(items);
            _equippedItems = new Dictionary<string, InventoryItem>(equipped);
            RefreshInventoryDisplay();
            RefreshEquipmentDisplay();
        }
        
        /// <summary>
        /// 🎒 Add item to inventory
        /// </summary>
        public bool AddItem(ItemData item, int quantity = 1)
        {
            // Check if item is stackable and already exists
            if (item.isStackable)
            {
                var existingItem = _playerInventory.FirstOrDefault(i => i.itemId == item.itemId);
                if (existingItem != null)
                {
                    existingItem.quantity += quantity;
                    RefreshInventoryDisplay();
                    return true;
                }
            }
            
            // Find empty slot
            int emptySlotIndex = FindEmptySlotIndex();
            if (emptySlotIndex >= 0)
            {
                var newItem = new InventoryItem
                {
                    itemId = item.itemId,
                    quantity = quantity,
                    slotIndex = emptySlotIndex
                };
                _playerInventory.Add(newItem);
                RefreshInventoryDisplay();
                return true;
            }
            
            return false; // Inventory full
        }
        
        /// <summary>
        /// 🎒 Remove item from inventory
        /// </summary>
        public bool RemoveItem(string itemId, int quantity = 1)
        {
            var item = _playerInventory.FirstOrDefault(i => i.itemId == itemId);
            if (item != null)
            {
                item.quantity -= quantity;
                if (item.quantity <= 0)
                {
                    _playerInventory.Remove(item);
                }
                RefreshInventoryDisplay();
                return true;
            }
            return false;
        }
        
        /// <summary>
        /// 🎒 Equip item to specific slot
        /// </summary>
        public bool EquipItem(string itemId, EquipmentSlotType slotType)
        {
            var inventoryItem = _playerInventory.FirstOrDefault(i => i.itemId == itemId);
            if (inventoryItem == null) return false;
            
            var itemData = GetItemData(itemId);
            if (itemData == null || itemData.equipSlotType != slotType) return false;
            
            // Unequip current item in slot if any
            string slotKey = slotType.ToString();
            if (_equippedItems.ContainsKey(slotKey))
            {
                UnequipItem(slotType);
            }
            
            // Equip new item
            _equippedItems[slotKey] = inventoryItem;
            _playerInventory.Remove(inventoryItem);
            
            RefreshInventoryDisplay();
            RefreshEquipmentDisplay();
            OnItemEquipped?.Invoke(itemData);
            return true;
        }
        
        /// <summary>
        /// 🎒 Unequip item from specific slot
        /// </summary>
        public bool UnequipItem(EquipmentSlotType slotType)
        {
            string slotKey = slotType.ToString();
            if (_equippedItems.ContainsKey(slotKey))
            {
                var equippedItem = _equippedItems[slotKey];
                _equippedItems.Remove(slotKey);
                
                // Find empty inventory slot
                int emptySlotIndex = FindEmptySlotIndex();
                if (emptySlotIndex >= 0)
                {
                    equippedItem.slotIndex = emptySlotIndex;
                    _playerInventory.Add(equippedItem);
                }
                
                RefreshInventoryDisplay();
                RefreshEquipmentDisplay();
                return true;
            }
            return false;
        }
        
        /// <summary>
        /// 🎒 Use consumable item
        /// </summary>
        public bool UseItem(string itemId, int quantity = 1)
        {
            var item = _playerInventory.FirstOrDefault(i => i.itemId == itemId);
            if (item == null) return false;
            
            var itemData = GetItemData(itemId);
            if (itemData == null || itemData.itemType != ItemType.Consumable) return false;
            
            if (RemoveItem(itemId, quantity))
            {
                OnItemUsed?.Invoke(itemData);
                return true;
            }
            return false;
        }
        
        #endregion
        
        #region Private Methods
        
        /// <summary>
        /// 🎒 Setup main inventory UI structure
        /// </summary>
        private void SetupInventoryStructure()
        {
            style.width = Length.Percent(100);
            style.height = Length.Percent(100);
            style.flexDirection = FlexDirection.Column;
            
            // Main content area
            var contentArea = new VisualElement();
            contentArea.style.flexDirection = FlexDirection.Row;
            contentArea.style.flexGrow = 1;
            
            // Left panel - inventory grid
            var leftPanel = new VisualElement();
            leftPanel.style.width = Length.Percent(60);
            leftPanel.style.height = Length.Percent(100);
            leftPanel.style.paddingLeft = 8;
            leftPanel.style.paddingRight = 4;
            
            _inventoryGrid = new ScrollView(ScrollViewMode.Vertical);
            _inventoryGrid.AddToClassList(GridUssClassName);
            _inventoryGrid.style.width = Length.Percent(100);
            _inventoryGrid.style.height = Length.Percent(100);
            
            _gridContainer = new VisualElement();
            _gridContainer.style.flexDirection = FlexDirection.Row;
            _gridContainer.style.flexWrap = Wrap.Wrap;
            _gridContainer.style.paddingTop = 8;
            _gridContainer.style.paddingBottom = 8;
            
            _inventoryGrid.Add(_gridContainer);
            leftPanel.Add(_inventoryGrid);
            
            // Right panel - equipment and details
            var rightPanel = new VisualElement();
            rightPanel.style.width = Length.Percent(40);
            rightPanel.style.height = Length.Percent(100);
            rightPanel.style.paddingLeft = 4;
            rightPanel.style.paddingRight = 8;
            rightPanel.style.flexDirection = FlexDirection.Column;
            
            contentArea.Add(leftPanel);
            contentArea.Add(rightPanel);
            Add(contentArea);
        }
        
        /// <summary>
        /// 🎒 Setup equipment panel for worn items
        /// </summary>
        private void SetupEquipmentPanel()
        {
            var rightPanel = Children().Last();
            
            var equipmentTitle = new Label("Equipment");
            equipmentTitle.style.fontSize = 16;
            equipmentTitle.style.color = Color.white;
            equipmentTitle.style.unityFontStyleAndWeight = FontStyle.Bold;
            equipmentTitle.style.marginBottom = 8;
            
            _equipmentPanel = new VisualElement();
            _equipmentPanel.style.backgroundColor = new Color(0.05f, 0.05f, 0.05f, 0.8f);
            //_equipmentPanel.style.borderTopLeftRadius = 12;
            //_equipmentPanel.style.borderTopRightRadius = 12;
            //_equipmentPanel.style.borderBottomLeftRadius = 12;
            //_equipmentPanel.style.borderBottomRightRadius = 12;
            //_equipmentPanel.style.borderTopWidth = 1;
            //_equipmentPanel.style.borderBottomWidth = 1;
            //_equipmentPanel.style.borderLeftWidth = 1;
            //_equipmentPanel.style.borderRightWidth = 1;
            _equipmentPanel.style.borderTopColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            _equipmentPanel.style.borderBottomColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            _equipmentPanel.style.borderLeftColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            _equipmentPanel.style.borderRightColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            _equipmentPanel.style.paddingTop = 16;
            _equipmentPanel.style.paddingBottom = 16;
            _equipmentPanel.style.paddingLeft = 16;
            _equipmentPanel.style.paddingRight = 16;
            _equipmentPanel.style.marginBottom = 16;
            _equipmentPanel.style.height = 200;
            
            CreateEquipmentSlots();
            
            // Details panel
            var detailsTitle = new Label("Item Details");
            detailsTitle.style.fontSize = 16;
            detailsTitle.style.color = Color.white;
            detailsTitle.style.unityFontStyleAndWeight = FontStyle.Bold;
            detailsTitle.style.marginBottom = 8;
            
            _detailsPanel = new VisualElement();
            _detailsPanel.style.backgroundColor = new Color(0.05f, 0.05f, 0.05f, 0.8f);
            //_detailsPanel.style.borderTopLeftRadius = 12;
            //_detailsPanel.style.borderTopRightRadius = 12;
            //_detailsPanel.style.borderBottomLeftRadius = 12;
            //_detailsPanel.style.borderBottomRightRadius = 12;
            //_detailsPanel.style.borderTopWidth = 1;
            //_detailsPanel.style.borderBottomWidth = 1;
            //_detailsPanel.style.borderLeftWidth = 1;
            //_detailsPanel.style.borderRightWidth = 1;
            _detailsPanel.style.borderTopColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            _detailsPanel.style.borderBottomColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            _detailsPanel.style.borderLeftColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            _detailsPanel.style.borderRightColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            _detailsPanel.style.paddingTop = 16;
            _detailsPanel.style.paddingBottom = 16;
            _detailsPanel.style.paddingLeft = 16;
            _detailsPanel.style.paddingRight = 16;
            _detailsPanel.style.flexGrow = 1;
            
            var emptyDetailsLabel = new Label("Select an item to view details");
            emptyDetailsLabel.style.fontSize = 12;
            emptyDetailsLabel.style.color = new Color(0.6f, 0.6f, 0.6f, 1f);
            emptyDetailsLabel.style.unityTextAlign = TextAnchor.MiddleCenter;
            _detailsPanel.Add(emptyDetailsLabel);
            
            rightPanel.Add(equipmentTitle);
            rightPanel.Add(_equipmentPanel);
            rightPanel.Add(detailsTitle);
            rightPanel.Add(_detailsPanel);
        }
        
        /// <summary>
        /// 🎒 Create equipment slots for different item types
        /// </summary>
        private void CreateEquipmentSlots()
        {
            var equipmentLayout = new VisualElement();
            equipmentLayout.style.flexDirection = FlexDirection.Column;
            equipmentLayout.style.height = Length.Percent(100);
            
            // Top row - helmet, armor, boots
            var topRow = new VisualElement();
            topRow.style.flexDirection = FlexDirection.Row;
            topRow.style.justifyContent = Justify.SpaceBetween;
            topRow.style.marginBottom = 8;
            
            var helmetSlot = CreateEquipmentSlot(EquipmentSlotType.Helmet);
            var armorSlot = CreateEquipmentSlot(EquipmentSlotType.Armor);
            var bootsSlot = CreateEquipmentSlot(EquipmentSlotType.Boots);
            
            topRow.Add(helmetSlot);
            topRow.Add(armorSlot);
            topRow.Add(bootsSlot);
            
            // Middle row - weapon and shield
            var middleRow = new VisualElement();
            middleRow.style.flexDirection = FlexDirection.Row;
            middleRow.style.justifyContent = Justify.SpaceAround;
            middleRow.style.marginBottom = 8;
            
            var weaponSlot = CreateEquipmentSlot(EquipmentSlotType.Weapon);
            var shieldSlot = CreateEquipmentSlot(EquipmentSlotType.Shield);
            
            middleRow.Add(weaponSlot);
            middleRow.Add(shieldSlot);
            
            // Bottom row - accessories
            var bottomRow = new VisualElement();
            bottomRow.style.flexDirection = FlexDirection.Row;
            bottomRow.style.justifyContent = Justify.SpaceBetween;
            
            var accessory1Slot = CreateEquipmentSlot(EquipmentSlotType.Accessory1);
            var accessory2Slot = CreateEquipmentSlot(EquipmentSlotType.Accessory2);
            var accessory3Slot = CreateEquipmentSlot(EquipmentSlotType.Accessory3);
            
            bottomRow.Add(accessory1Slot);
            bottomRow.Add(accessory2Slot);
            bottomRow.Add(accessory3Slot);
            
            equipmentLayout.Add(topRow);
            equipmentLayout.Add(middleRow);
            equipmentLayout.Add(bottomRow);
            
            _equipmentPanel.Add(equipmentLayout);
        }
        
        /// <summary>
        /// 🎒 Create individual equipment slot
        /// </summary>
        private EquipmentSlot CreateEquipmentSlot(EquipmentSlotType slotType)
        {
            var slot = new EquipmentSlot(slotType);
            slot.OnItemDropped += HandleEquipmentDrop;
            slot.OnItemClicked += HandleEquipmentClick;
            _equipmentSlots.Add(slot);
            return slot;
        }
        
        /// <summary>
        /// 🎒 Setup filter and sorting controls
        /// </summary>
        private void SetupFilters()
        {
            var filterContainer = new VisualElement();
            filterContainer.AddToClassList(FilterUssClassName);
            filterContainer.style.flexDirection = FlexDirection.Row;
            filterContainer.style.height = 40;
            filterContainer.style.paddingLeft = 8;
            filterContainer.style.paddingRight = 8;
            filterContainer.style.paddingTop = 8;
            filterContainer.style.paddingBottom = 8;
            filterContainer.style.alignItems = Align.Center;
            filterContainer.style.backgroundColor = new Color(0.05f, 0.05f, 0.05f, 0.8f);
            
            // Search field
            _searchField = new TextField();
            _searchField.style.width = 120;
            _searchField.style.marginRight = 8;
            _searchField.SetValueWithoutNotify("Search...");
            
            // Category filter
            _categoryFilter = new DropdownField("Category");
            _categoryFilter.style.width = 100;
            _categoryFilter.style.marginRight = 8;
            _categoryFilter.choices = System.Enum.GetNames(typeof(ItemCategory)).ToList();
            _categoryFilter.SetValueWithoutNotify(ItemCategory.All.ToString());
            
            // Sort filter
            _sortFilter = new DropdownField("Sort");
            _sortFilter.style.width = 100;
            _sortFilter.style.marginRight = 8;
            _sortFilter.choices = System.Enum.GetNames(typeof(ItemSortMode)).ToList();
            _sortFilter.SetValueWithoutNotify(ItemSortMode.Type.ToString());

            // Quick sort button
            _sortButton = new Button(ToggleQuickSort)
            {
                text = "A-Z"
            };
            _sortButton.style.width = 60;
            
            filterContainer.Add(_searchField);
            filterContainer.Add(_categoryFilter);
            filterContainer.Add(_sortFilter);
            filterContainer.Add(_sortButton);
            
            Insert(0, filterContainer);
        }
        
        /// <summary>
        /// 🎒 Initialize all inventory slots
        /// </summary>
        private void InitializeSlots()
        {
            for (int i = 0; i < _totalSlots; i++)
            {
                var slot = new InventorySlot(i);
                slot.OnItemClicked += HandleSlotClick;
                slot.OnDragStarted += HandleDragStart;
                slot.OnDragEnded += HandleDragEnd;
                slot.OnItemDropped += HandleSlotDrop;
                
                _inventorySlots.Add(slot);
                _gridContainer.Add(slot);
            }
            
            UpdateSlotLayout();
        }
        
        /// <summary>
        /// 🎒 Update slot sizes and spacing
        /// </summary>
        private void UpdateSlotLayout()
        {
            float availableWidth = _inventoryGrid.resolvedStyle.width - 16;
            
            // Use configured slot size as base, but adapt to available space
            float targetSlotSize = _slotSize;
            float totalSlotsWidth = _slotsPerRow * targetSlotSize + (_slotsPerRow - 1) * _slotSpacing;
            
            // If target size doesn't fit, scale down proportionally
            float actualSlotSize = totalSlotsWidth > availableWidth 
                ? (availableWidth - (_slotsPerRow - 1) * _slotSpacing) / _slotsPerRow
                : targetSlotSize;
            
            foreach (var slot in _inventorySlots)
            {
                slot.style.width = actualSlotSize;
                slot.style.height = actualSlotSize;
                slot.style.marginLeft = _slotSpacing / 2;
                slot.style.marginRight = _slotSpacing / 2;
                slot.style.marginBottom = _slotSpacing;
            }
        }
        
        /// <summary>
        /// 🎒 Register UI event callbacks
        /// </summary>
        private void RegisterCallbacks()
        {
            _searchField.RegisterValueChangedCallback(OnSearchChanged);
            _categoryFilter.RegisterValueChangedCallback(OnCategoryFilterChanged);
            _sortFilter.RegisterValueChangedCallback(OnSortFilterChanged);
            
            RegisterCallback<PointerMoveEvent>(OnPointerMove);
            RegisterCallback<PointerUpEvent>(OnPointerUp);
        }
        
        /// <summary>
        /// 🎒 Refresh inventory slot display
        /// </summary>
        private void RefreshInventoryDisplay()
        {
            // Clear all slots
            foreach (var slot in _inventorySlots)
            {
                slot.ClearItem();
            }
            
            // Apply filters and sorting
            var filteredItems = ApplyFiltersAndSort();
            
            // Fill slots with filtered items
            for (int i = 0; i < filteredItems.Count && i < _inventorySlots.Count; i++)
            {
                var item = filteredItems[i];
                var itemData = GetItemData(item.itemId);
                if (itemData != null)
                {
                    _inventorySlots[i].SetItem(item, itemData);
                }
            }
        }
        
        /// <summary>
        /// 🎒 Refresh equipment slot display
        /// </summary>
        private void RefreshEquipmentDisplay()
        {
            foreach (var slot in _equipmentSlots)
            {
                slot.ClearItem();
                
                string slotKey = slot.SlotType.ToString();
                if (_equippedItems.ContainsKey(slotKey))
                {
                    var equippedItem = _equippedItems[slotKey];
                    var itemData = GetItemData(equippedItem.itemId);
                    if (itemData != null)
                    {
                        slot.SetItem(equippedItem, itemData);
                    }
                }
            }
        }
        
        /// <summary>
        /// 🎒 Apply current filters and sorting to inventory
        /// </summary>
        private List<InventoryItem> ApplyFiltersAndSort()
        {
            var filtered = _playerInventory.Where(item =>
            {
                var itemData = GetItemData(item.itemId);
                if (itemData == null) return false;
                
                // Category filter
                if (_currentCategoryFilter != ItemCategory.All)
                {
                    if (itemData.category != _currentCategoryFilter) return false;
                }
                
                // Search filter
                if (!string.IsNullOrEmpty(_searchField.value) && _searchField.value != "Search...")
                {
                    if (!itemData.itemName.ToLower().Contains(_searchField.value.ToLower())) return false;
                }
                
                return true;
            }).ToList();
            
            // Apply sorting
            return _currentSortMode switch
            {
                ItemSortMode.Name => filtered.OrderBy(i => GetItemData(i.itemId)?.itemName).ToList(),
                ItemSortMode.Type => filtered.OrderBy(i => GetItemData(i.itemId)?.itemType).ToList(),
                ItemSortMode.Rarity => filtered.OrderByDescending(i => GetItemData(i.itemId)?.rarity).ToList(),
                ItemSortMode.Quantity => filtered.OrderByDescending(i => i.quantity).ToList(),
                _ => filtered
            };
        }
        
        /// <summary>
        /// 🎒 Find next empty slot index
        /// </summary>
        private int FindEmptySlotIndex()
        {
            for (int i = 0; i < _totalSlots; i++)
            {
                if (!_playerInventory.Any(item => item.slotIndex == i))
                {
                    return i;
                }
            }
            return -1;
        }
        
        /// <summary>
        /// 🎒 Get item data by ID
        /// </summary>
        private ItemData GetItemData(string itemId)
        {
            _allItems.TryGetValue(itemId, out ItemData itemData);
            return itemData;
        }
        
        /// <summary>
        /// 🎒 Toggle quick sort mode
        /// </summary>
        private void ToggleQuickSort()
        {
            // Cycle through quick sort options
            if (_sortButton.text == "A-Z")
            {
                _currentSortMode = ItemSortMode.Name;
                _sortButton.text = "Rarity";
            }
            else if (_sortButton.text == "Rarity")
            {
                _currentSortMode = ItemSortMode.Rarity;
                _sortButton.text = "Qty";
            }
            else
            {
                _currentSortMode = ItemSortMode.Quantity;
                _sortButton.text = "A-Z";
            }
            
            RefreshInventoryDisplay();
        }
        
        #endregion
        
        #region Event Handlers
        
        private void OnSearchChanged(ChangeEvent<string> evt)
        {
            RefreshInventoryDisplay();
        }
        
        private void OnCategoryFilterChanged(ChangeEvent<string> evt)
        {
            if (System.Enum.TryParse<ItemCategory>(evt.newValue, out ItemCategory category))
            {
                _currentCategoryFilter = category;
                RefreshInventoryDisplay();
            }
        }
        
        private void OnSortFilterChanged(ChangeEvent<string> evt)
        {
            if (System.Enum.TryParse<ItemSortMode>(evt.newValue, out ItemSortMode sortMode))
            {
                _currentSortMode = sortMode;
                RefreshInventoryDisplay();
            }
        }
        
        private void HandleSlotClick(InventorySlot slot, InventoryItem item, ItemData itemData)
        {
            _selectedItem = itemData;
            ShowItemDetails(itemData);
            OnItemSelected?.Invoke(itemData);
        }
        
        private void HandleDragStart(InventorySlot slot)
        {
            if (slot.HasItem)
            {
                _draggedSlot = slot;
                _isDragging = true;
                CreateDragPreview(slot);
            }
        }
        
        private void HandleDragEnd(InventorySlot slot)
        {
            _isDragging = false;
            _draggedSlot = null;
            
            if (_dragPreview != null)
            {
                _dragPreview.RemoveFromHierarchy();
                _dragPreview = null;
            }
        }
        
        private void HandleSlotDrop(InventorySlot targetSlot, InventorySlot sourceSlot)
        {
            if (sourceSlot != null && targetSlot != sourceSlot)
            {
                SwapSlotContents(sourceSlot, targetSlot);
            }
        }
        
        private void HandleEquipmentDrop(EquipmentSlot equipSlot, InventorySlot sourceSlot)
        {
            if (sourceSlot?.HasItem == true)
            {
                var itemData = sourceSlot.GetItemData();
                if (itemData?.equipSlotType == equipSlot.SlotType)
                {
                    EquipItem(sourceSlot.GetInventoryItem().itemId, equipSlot.SlotType);
                }
            }
        }
        
        private void HandleEquipmentClick(EquipmentSlot equipSlot, InventoryItem item, ItemData itemData)
        {
            _selectedItem = itemData;
            ShowItemDetails(itemData);
            OnItemSelected?.Invoke(itemData);
        }
        
        private void OnPointerMove(PointerMoveEvent evt)
        {
            if (_isDragging && _dragPreview != null)
            {
                _dragPreview.style.left = evt.position.x - 30;
                _dragPreview.style.top = evt.position.y - 30;
            }
        }
        
        private void OnPointerUp(PointerUpEvent evt)
        {
            if (_isDragging)
            {
                HandleDragEnd(_draggedSlot);
            }
        }
        
        #endregion
        
        #region Helper Methods
        
        private void CreateDragPreview(InventorySlot slot)
        {
            _dragPreview = new VisualElement();
            _dragPreview.AddToClassList(SlotDragPreviewUssClassName);
            _dragPreview.style.position = Position.Absolute;
            _dragPreview.style.width = 60;
            _dragPreview.style.height = 60;
            _dragPreview.style.backgroundColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            //_dragPreview.style.borderTopLeftRadius = 8;
            //_dragPreview.style.borderTopRightRadius = 8;
            //_dragPreview.style.borderBottomLeftRadius = 8;
            //_dragPreview.style.borderBottomRightRadius = 8;
            //_dragPreview.style.borderTopWidth = 2;
            //_dragPreview.style.borderBottomWidth = 2;
            //_dragPreview.style.borderLeftWidth = 2;
            //_dragPreview.style.borderRightWidth = 2;
            _dragPreview.style.borderTopColor = Color.white;
            _dragPreview.style.borderBottomColor = Color.white;
            _dragPreview.style.borderLeftColor = Color.white;
            _dragPreview.style.borderRightColor = Color.white;

            var itemData = slot.GetItemData();
            if (itemData?.itemIcon != null)
            {
                _dragPreview.style.backgroundImage = new StyleBackground(itemData.itemIcon);
            }
            
            parent.Add(_dragPreview);
        }
        
        private void SwapSlotContents(InventorySlot slot1, InventorySlot slot2)
        {
            var item1 = slot1.GetInventoryItem();
            var item2 = slot2.GetInventoryItem();
            
            if (item1 != null) item1.slotIndex = slot2.SlotIndex;
            if (item2 != null) item2.slotIndex = slot1.SlotIndex;
            
            RefreshInventoryDisplay();
            OnItemMoved?.Invoke(slot1.GetItemData(), slot2.SlotIndex);
        }
        
        private void ShowItemDetails(ItemData itemData)
        {
            _detailsPanel.Clear();
            
            if (itemData == null)
            {
                var emptyLabel = new Label("Select an item to view details");
                emptyLabel.style.fontSize = 12;
                emptyLabel.style.color = new Color(0.6f, 0.6f, 0.6f, 1f);
                emptyLabel.style.unityTextAlign = TextAnchor.MiddleCenter;
                _detailsPanel.Add(emptyLabel);
                return;
            }
            
            // Item name and rarity
            var nameLabel = new Label(itemData.itemName);
            nameLabel.style.fontSize = 16;
            nameLabel.style.color = GetRarityColor(itemData.rarity);
            nameLabel.style.unityFontStyleAndWeight = FontStyle.Bold;
            nameLabel.style.marginBottom = 8;
            
            // Item description
            var descLabel = new Label(itemData.description);
            descLabel.style.fontSize = 12;
            descLabel.style.color = new Color(0.8f, 0.8f, 0.8f, 1f);
            descLabel.style.whiteSpace = WhiteSpace.Normal;
            descLabel.style.marginBottom = 12;
            
            // Action buttons
            VisualElement buttonContainer = new();
            buttonContainer.style.flexDirection = FlexDirection.Column;
            
            if (itemData.itemType == ItemType.Consumable)
            {
                Button useButton = new(() => UseItem(itemData.itemId))
                {
                    text = "USE"
                };
                useButton.style.marginBottom = 4;
                buttonContainer.Add(useButton);
            }
            else if (itemData.itemType == ItemType.Equipment)
            {
                Button equipButton = new(() => EquipItem(itemData.itemId, itemData.equipSlotType))
                {
                    text = "EQUIP"
                };
                equipButton.style.marginBottom = 4;
                buttonContainer.Add(equipButton);
            }

            Button sellButton = new(() => OnItemSold?.Invoke(itemData))
            {
                text = $"SELL ({itemData.sellValue})"
            };
            buttonContainer.Add(sellButton);
            
            _detailsPanel.Add(nameLabel);
            _detailsPanel.Add(descLabel);
            _detailsPanel.Add(buttonContainer);
        }
        
        private Color GetRarityColor(ItemRarity rarity)
        {
            return rarity switch
            {
                ItemRarity.Common => new Color(0.6f, 0.6f, 0.6f, 1f),
                ItemRarity.Rare => new Color(0.2f, 0.5f, 0.9f, 1f),
                ItemRarity.Epic => new Color(0.6f, 0.2f, 0.9f, 1f),
                ItemRarity.Legendary => new Color(1f, 0.8f, 0f, 1f),
                ItemRarity.Mythic => new Color(1f, 0.3f, 0.3f, 1f),
                _ => Color.white
            };
        }
        
        #endregion
    }
}

// Continue in next part due to length...
