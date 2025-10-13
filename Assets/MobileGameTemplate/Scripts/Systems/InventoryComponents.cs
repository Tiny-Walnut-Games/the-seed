using UnityEngine;
using UnityEngine.UIElements;
using MobileGameTemplate.Core; // 🔧 Unity 2022.3 Compatibility Bridge
using System.Collections.Generic;
using System.Linq; // 🔧 C# 10 Compatibility

namespace MobileGameTemplate.Systems
{
    /// <summary>
    /// 🎒 Individual inventory slot with drag-drop support
    /// </summary>
    public class InventorySlot : VisualElement
    {
        public System.Action<InventorySlot, InventoryItem, ItemData> OnItemClicked;
        public System.Action<InventorySlot> OnDragStarted;
        public System.Action<InventorySlot> OnDragEnded;
        public System.Action<InventorySlot, InventorySlot> OnItemDropped;
        
        public int SlotIndex { get; private set; }
        public bool HasItem => _inventoryItem != null;
        
        private InventoryItem _inventoryItem;
        private ItemData _itemData;
        private VisualElement _itemIcon;
        private Label _quantityLabel;
        private VisualElement _rarityBorder;
        
        public InventorySlot(int slotIndex)
        {
            SlotIndex = slotIndex;
            AddToClassList(InventorySystem.SlotUssClassName);
            CreateSlotStructure();
            RegisterCallbacks();
        }
        
        private void CreateSlotStructure()
        {
            style.width = 60;
            style.height = 60;
            style.backgroundColor = new Color(0.1f, 0.1f, 0.1f, 0.6f);
            // 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
            // 🔧 LEGENDARY FIX: borderWidth not available in Unity 2022.3
            // 🔧 LEGENDARY FIX: borderColor not available in Unity 2022.3
            style.position = Position.Relative;
            
            // Item icon
            _itemIcon = new VisualElement();
            _itemIcon.style.position = Position.Absolute;
            _itemIcon.style.top = 4;
            _itemIcon.style.left = 4;
            _itemIcon.style.right = 4;
            _itemIcon.style.bottom = 16;
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
            
            // Quantity label
            _quantityLabel = new Label();
            _quantityLabel.style.position = Position.Absolute;
            _quantityLabel.style.bottom = 2;
            _quantityLabel.style.right = 2;
            _quantityLabel.style.fontSize = 10;
            _quantityLabel.style.color = Color.white;
            _quantityLabel.style.backgroundColor = new Color(0f, 0f, 0f, 0.8f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
            _quantityLabel.style.paddingLeft = 2;
            _quantityLabel.style.paddingRight = 2;
            _quantityLabel.style.display = DisplayStyle.None;
            
            Add(_itemIcon);
            Add(_quantityLabel);
            
            SetEmpty();
        }
        
        private void RegisterCallbacks()
        {
            RegisterCallback<ClickEvent>(OnSlotClicked);
            RegisterCallback<PointerDownEvent>(OnPointerDown);
            RegisterCallback<PointerUpEvent>(OnPointerUp);
        }
        
        public void SetItem(InventoryItem item, ItemData itemData)
        {
            _inventoryItem = item;
            _itemData = itemData;
            
            RemoveFromClassList(InventorySystem.SlotEmptyUssClassName);
            
            // Set item icon
            if (itemData.itemIcon != null)
            {
                _itemIcon.style.backgroundImage = new StyleBackground(itemData.itemIcon);
            }
            
            // Set quantity
            if (item.quantity > 1)
            {
                _quantityLabel.text = item.quantity.ToString();
                _quantityLabel.style.display = DisplayStyle.Flex;
            }
            else
            {
                _quantityLabel.style.display = DisplayStyle.None;
            }
            
            // Set rarity border
            // 🔧 LEGENDARY FIX: borderColor not available in Unity 2022.3
        }
        
        public void ClearItem()
        {
            _inventoryItem = null;
            _itemData = null;
            SetEmpty();
        }
        
        private void SetEmpty()
        {
            AddToClassList(InventorySystem.SlotEmptyUssClassName);
            _itemIcon.style.backgroundImage = null;
            _quantityLabel.style.display = DisplayStyle.None;
            // 🔧 LEGENDARY FIX: borderColor not available in Unity 2022.3
        }
        
        public InventoryItem GetInventoryItem() => _inventoryItem;
        public ItemData GetItemData() => _itemData;
        
        private void OnSlotClicked(ClickEvent evt)
        {
            if (HasItem)
            {
                OnItemClicked?.Invoke(this, _inventoryItem, _itemData);
            }
            evt.StopPropagation();
        }
        
        private void OnPointerDown(PointerDownEvent evt)
        {
            if (HasItem)
            {
                OnDragStarted?.Invoke(this);
            }
        }
        
        private void OnPointerUp(PointerUpEvent evt)
        {
            OnDragEnded?.Invoke(this);
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
                _ => new Color(0.4f, 0.4f, 0.4f, 1f)
            };
        }
    }
    
    /// <summary>
    /// 🎒 Equipment slot for worn items
    /// </summary>
    public class EquipmentSlot : VisualElement
    {
        public System.Action<EquipmentSlot, InventorySlot> OnItemDropped;
        public System.Action<EquipmentSlot, InventoryItem, ItemData> OnItemClicked;
        
        public EquipmentSlotType SlotType { get; private set; }
        public bool HasItem => _inventoryItem != null;
        
        private InventoryItem _inventoryItem;
        private ItemData _itemData;
        private VisualElement _itemIcon;
        private Label _slotLabel;
        
        public EquipmentSlot(EquipmentSlotType slotType)
        {
            SlotType = slotType;
            CreateSlotStructure();
            RegisterCallbacks();
        }
        
        private void CreateSlotStructure()
        {
            style.width = 50;
            style.height = 50;
            style.backgroundColor = new Color(0.15f, 0.15f, 0.15f, 0.8f);
            // 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
            // 🔧 LEGENDARY FIX: borderWidth not available in Unity 2022.3
            // 🔧 LEGENDARY FIX: borderColor not available in Unity 2022.3
            style.position = Position.Relative;
            
            // Slot label
            _slotLabel = new Label(GetSlotDisplayName());
            _slotLabel.style.position = Position.Absolute;
            _slotLabel.style.bottom = -18;
            _slotLabel.style.left = 0;
            _slotLabel.style.right = 0;
            _slotLabel.style.fontSize = 8;
            _slotLabel.style.color = new Color(0.7f, 0.7f, 0.7f, 1f);
            _slotLabel.style.unityTextAlign = TextAnchor.MiddleCenter;
            
            // Item icon
            _itemIcon = new VisualElement();
            _itemIcon.style.position = Position.Absolute;
            _itemIcon.style.top = 4;
            _itemIcon.style.left = 4;
            _itemIcon.style.right = 4;
            _itemIcon.style.bottom = 4;
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
            
            Add(_itemIcon);
            Add(_slotLabel);
        }
        
        private string GetSlotDisplayName()
        {
            return SlotType switch
            {
                EquipmentSlotType.Helmet => "Head",
                EquipmentSlotType.Armor => "Body",
                EquipmentSlotType.Boots => "Feet",
                EquipmentSlotType.Weapon => "Weapon",
                EquipmentSlotType.Shield => "Shield",
                EquipmentSlotType.Accessory1 => "Ring 1",
                EquipmentSlotType.Accessory2 => "Ring 2",
                EquipmentSlotType.Accessory3 => "Neck",
                _ => "Item"
            };
        }
        
        private void RegisterCallbacks()
        {
            RegisterCallback<ClickEvent>(OnSlotClicked);
        }
        
        public void SetItem(InventoryItem item, ItemData itemData)
        {
            _inventoryItem = item;
            _itemData = itemData;
            
            // Set item icon
            if (itemData.itemIcon != null)
            {
                _itemIcon.style.backgroundImage = new StyleBackground(itemData.itemIcon);
            }
            
            // Set equipped border
            // 🔧 LEGENDARY FIX: borderColor not available in Unity 2022.3
        }
        
        public void ClearItem()
        {
            _inventoryItem = null;
            _itemData = null;
            _itemIcon.style.backgroundImage = null;
            // 🔧 LEGENDARY FIX: borderColor not available in Unity 2022.3
        }
        
        private void OnSlotClicked(ClickEvent evt)
        {
            if (HasItem)
            {
                OnItemClicked?.Invoke(this, _inventoryItem, _itemData);
            }
            evt.StopPropagation();
        }
    }
}

/// <summary>
/// Data structures for inventory system
/// </summary>
[System.Serializable]
public class ItemData
{
    [Header("Item Identity")]
    public string itemId = "";
    public string itemName = "Item";
    public string description = "";
    public Sprite itemIcon;
    
    [Header("Item Classification")]
    public ItemType itemType = ItemType.Miscellaneous;
    public ItemCategory category = ItemCategory.General;
    public ItemRarity rarity = ItemRarity.Common;
    
    [Header("Item Properties")]
    public bool isStackable = false;
    public int maxStackSize = 99;
    public int sellValue = 10;
    public int buyValue = 20;
    
    [Header("Equipment Properties")]
    public EquipmentSlotType equipSlotType = EquipmentSlotType.None;
    public int attackBonus = 0;
    public int defenseBonus = 0;
    public int healthBonus = 0;
    public int speedBonus = 0;
    
    [Header("Consumable Properties")]
    public int healAmount = 0;
    public int manaAmount = 0;
    public float buffDuration = 0f;
    public string[] buffEffects = new string[0];
}

[System.Serializable]
public class InventoryItem
{
    public string itemId = "";
    public int quantity = 1;
    public int slotIndex = 0;
    public System.DateTime acquiredDate = System.DateTime.Now;
}

public enum ItemType
{
    Equipment = 0,
    Consumable = 1,
    Material = 2,
    Quest = 3,
    Miscellaneous = 4
}

public enum ItemCategory
{
    All = -1,
    General = 0,
    Weapons = 1,
    Armor = 2,
    Consumables = 3,
    Materials = 4,
    Quest = 5
}

public enum ItemRarity
{
    Common = 0,
    Rare = 1,
    Epic = 2,
    Legendary = 3,
    Mythic = 4
}

public enum ItemSortMode
{
    Name = 0,
    Type = 1,
    Rarity = 2,
    Quantity = 3
}

public enum EquipmentSlotType
{
    None = -1,
    Helmet = 0,
    Armor = 1,
    Boots = 2,
    Weapon = 3,
    Shield = 4,
    Accessory1 = 5,
    Accessory2 = 6,
    Accessory3 = 7
}
