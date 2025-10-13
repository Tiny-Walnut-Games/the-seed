using UnityEngine;
using UnityEngine.UIElements;

namespace MobileGameTemplate.Systems
{
    /// <summary>
    /// 🧿 INTENDED EXPANSION ZONE - Hero details view with evolution and upgrade options
    /// Detailed stats display, evolution preview, and action buttons
    /// Part of the hero collection system for mobile action games
    /// 
    /// Sacred Vision: Transform hero information into engaging progression interface!
    /// </summary>
    public class HeroDetailsView : VisualElement
    {
        #region Events
        public System.Action<HeroData> OnEvolutionRequested;
        public System.Action<HeroData> OnUpgradeRequested;
        public System.Action<HeroData> OnEquipRequested;
        #endregion
        
        #region Private Fields
        private HeroData _currentHero;
        
        // Header elements
        private VisualElement _heroPortrait;
        private Label _heroName;
        private Label _heroLevel;
        private VisualElement _rarityIndicator;
        private Label _heroPower;
        
        // Stats display
        private VisualElement _statsContainer;
        private Label _attackStat;
        private Label _defenseStat;
        private Label _healthStat;
        private Label _speedStat;
        private Label _critRateStat;
        private Label _critDamageStat;
        
        // Evolution panel
        private VisualElement _evolutionPanel;
        private VisualElement _evolutionStars;
        private Button _evolutionButton;
        private Label _evolutionCost;
        private VisualElement _evolutionMaterials;
        
        // Action buttons
        private Button _upgradeButton;
        private Button _equipButton;
        private Button _skillsButton;
        
        // Skills display
        private VisualElement _skillsContainer;
        
        // Empty state
        private Label _emptyStateLabel;
        #endregion
        
        #region Constructor
        public HeroDetailsView()
        {
            CreateDetailsStructure();
            ShowEmptyState();
        }
        #endregion
        
        #region Public API
        
        /// <summary>
        /// 🧿 Display detailed information for selected hero
        /// </summary>
        public void ShowHero(HeroData hero)
        {
            _currentHero = hero;
            
            if (hero == null)
            {
                ShowEmptyState();
                return;
            }
            
            HideEmptyState();
            UpdateHeroDisplay();
            UpdateStatsDisplay();
            UpdateEvolutionPanel();
            UpdateActionButtons();
            UpdateSkillsDisplay();
        }
        
        /// <summary>
        /// 🧿 Clear display and show empty state
        /// </summary>
        public void ClearDisplay()
        {
            _currentHero = null;
            ShowEmptyState();
        }
        
        #endregion
        
        #region Private Methods
        
        /// <summary>
        /// 🧿 Create the main details UI structure
        /// </summary>
        private void CreateDetailsStructure()
        {
            style.width = Length.Percent(100);
            style.height = Length.Percent(100);
            style.paddingTop = 16;
            style.paddingBottom = 16;
            style.paddingLeft = 16;
            style.paddingRight = 16;
            
            CreateHeader();
            CreateStatsSection();
            CreateEvolutionSection();
            CreateActionButtons();
            CreateSkillsSection();
            CreateEmptyState();
        }
        
        /// <summary>
        /// 🧿 Create hero header with portrait and basic info
        /// </summary>
        private void CreateHeader()
        {
            var headerContainer = new VisualElement();
            headerContainer.style.marginBottom = 16;
            headerContainer.style.alignItems = Align.Center;
            
            // Hero portrait
            _heroPortrait = new VisualElement();
            _heroPortrait.style.width = 100;
            _heroPortrait.style.height = 100;
            _heroPortrait.style.backgroundColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            _heroPortrait.style.borderRadius = 12;
            _heroPortrait.style.marginBottom = 8;
            
            // Hero name
            _heroName = new Label();
            _heroName.style.fontSize = 18;
            _heroName.style.color = Color.white;
            _heroName.style.unityTextAlign = TextAnchor.MiddleCenter;
            _heroName.style.unityFontStyleAndWeight = FontStyle.Bold;
            _heroName.style.marginBottom = 4;
            
            // Hero level and power
            var levelPowerContainer = new VisualElement();
            levelPowerContainer.style.flexDirection = FlexDirection.Row;
            levelPowerContainer.style.justifyContent = Justify.SpaceBetween;
            levelPowerContainer.style.width = Length.Percent(100);
            levelPowerContainer.style.marginBottom = 8;
            
            _heroLevel = new Label();
            _heroLevel.style.fontSize = 14;
            _heroLevel.style.color = new Color(0.8f, 0.8f, 0.8f, 1f);
            
            _heroPower = new Label();
            _heroPower.style.fontSize = 14;
            _heroPower.style.color = new Color(1f, 0.8f, 0f, 1f);
            _heroPower.style.unityFontStyleAndWeight = FontStyle.Bold;
            
            levelPowerContainer.Add(_heroLevel);
            levelPowerContainer.Add(_heroPower);
            
            // Rarity indicator
            _rarityIndicator = new VisualElement();
            _rarityIndicator.style.width = 120;
            _rarityIndicator.style.height = 4;
            _rarityIndicator.style.borderRadius = 2;
            _rarityIndicator.style.marginBottom = 8;
            
            headerContainer.Add(_heroPortrait);
            headerContainer.Add(_heroName);
            headerContainer.Add(levelPowerContainer);
            headerContainer.Add(_rarityIndicator);
            
            Add(headerContainer);
        }
        
        /// <summary>
        /// 🧿 Create stats display section
        /// </summary>
        private void CreateStatsSection()
        {
            var sectionTitle = new Label("Stats");
            sectionTitle.style.fontSize = 16;
            sectionTitle.style.color = Color.white;
            sectionTitle.style.unityFontStyleAndWeight = FontStyle.Bold;
            sectionTitle.style.marginBottom = 8;
            sectionTitle.style.marginTop = 8;
            
            _statsContainer = new VisualElement();
            _statsContainer.style.backgroundColor = new Color(0.1f, 0.1f, 0.1f, 0.6f);
            _statsContainer.style.borderRadius = 8;
            _statsContainer.style.paddingTop = 12;
            _statsContainer.style.paddingBottom = 12;
            _statsContainer.style.paddingLeft = 16;
            _statsContainer.style.paddingRight = 16;
            _statsContainer.style.marginBottom = 16;
            
            // Create stat displays
            _attackStat = CreateStatRow("Attack", "0");
            _defenseStat = CreateStatRow("Defense", "0");
            _healthStat = CreateStatRow("Health", "0");
            _speedStat = CreateStatRow("Speed", "0");
            _critRateStat = CreateStatRow("Crit Rate", "0%");
            _critDamageStat = CreateStatRow("Crit Damage", "0%");
            
            _statsContainer.Add(_attackStat);
            _statsContainer.Add(_defenseStat);
            _statsContainer.Add(_healthStat);
            _statsContainer.Add(_speedStat);
            _statsContainer.Add(_critRateStat);
            _statsContainer.Add(_critDamageStat);
            
            Add(sectionTitle);
            Add(_statsContainer);
        }
        
        /// <summary>
        /// 🧿 Create evolution section with stars and requirements
        /// </summary>
        private void CreateEvolutionSection()
        {
            var sectionTitle = new Label("Evolution");
            sectionTitle.style.fontSize = 16;
            sectionTitle.style.color = Color.white;
            sectionTitle.style.unityFontStyleAndWeight = FontStyle.Bold;
            sectionTitle.style.marginBottom = 8;
            
            _evolutionPanel = new VisualElement();
            _evolutionPanel.style.backgroundColor = new Color(0.1f, 0.1f, 0.1f, 0.6f);
            _evolutionPanel.style.borderRadius = 8;
            _evolutionPanel.style.paddingTop = 12;
            _evolutionPanel.style.paddingBottom = 12;
            _evolutionPanel.style.paddingLeft = 16;
            _evolutionPanel.style.paddingRight = 16;
            _evolutionPanel.style.marginBottom = 16;
            
            // Evolution stars
            _evolutionStars = new VisualElement();
            _evolutionStars.style.flexDirection = FlexDirection.Row;
            _evolutionStars.style.justifyContent = Justify.Center;
            _evolutionStars.style.marginBottom = 12;
            
            // Evolution button and cost
            var evolutionControls = new VisualElement();
            evolutionControls.style.flexDirection = FlexDirection.Row;
            evolutionControls.style.justifyContent = Justify.SpaceBetween;
            evolutionControls.style.alignItems = Align.Center;
            
            _evolutionButton = new Button(() => OnEvolutionRequested?.Invoke(_currentHero));
            _evolutionButton.text = "EVOLVE";
            _evolutionButton.style.width = 80;
            _evolutionButton.style.height = 32;
            _evolutionButton.style.backgroundColor = new Color(0.8f, 0.3f, 0.8f, 0.9f);
            _evolutionButton.style.borderRadius = 16;
            _evolutionButton.style.borderWidth = 0;
            _evolutionButton.style.fontSize = 12;
            _evolutionButton.style.color = Color.white;
            
            _evolutionCost = new Label();
            _evolutionCost.style.fontSize = 12;
            _evolutionCost.style.color = new Color(1f, 0.8f, 0f, 1f);
            
            evolutionControls.Add(_evolutionButton);
            evolutionControls.Add(_evolutionCost);
            
            // Evolution materials
            _evolutionMaterials = new VisualElement();
            _evolutionMaterials.style.flexDirection = FlexDirection.Row;
            _evolutionMaterials.style.flexWrap = Wrap.Wrap;
            _evolutionMaterials.style.marginTop = 8;
            
            _evolutionPanel.Add(_evolutionStars);
            _evolutionPanel.Add(evolutionControls);
            _evolutionPanel.Add(_evolutionMaterials);
            
            Add(sectionTitle);
            Add(_evolutionPanel);
        }
        
        /// <summary>
        /// 🧿 Create action buttons for upgrade, equip, skills
        /// </summary>
        private void CreateActionButtons()
        {
            var buttonContainer = new VisualElement();
            buttonContainer.style.flexDirection = FlexDirection.Row;
            buttonContainer.style.justifyContent = Justify.SpaceBetween;
            buttonContainer.style.marginBottom = 16;
            
            _upgradeButton = new Button(() => OnUpgradeRequested?.Invoke(_currentHero));
            _upgradeButton.text = "UPGRADE";
            _upgradeButton.style.flexGrow = 1;
            _upgradeButton.style.height = 40;
            _upgradeButton.style.marginRight = 4;
            _upgradeButton.style.backgroundColor = new Color(0.3f, 0.7f, 0.3f, 0.9f);
            _upgradeButton.style.borderRadius = 20;
            _upgradeButton.style.borderWidth = 0;
            _upgradeButton.style.fontSize = 14;
            _upgradeButton.style.color = Color.white;
            
            _equipButton = new Button(() => OnEquipRequested?.Invoke(_currentHero));
            _equipButton.text = "EQUIP";
            _equipButton.style.flexGrow = 1;
            _equipButton.style.height = 40;
            _equipButton.style.marginLeft = 2;
            _equipButton.style.marginRight = 2;
            _equipButton.style.backgroundColor = new Color(0.3f, 0.5f, 0.7f, 0.9f);
            _equipButton.style.borderRadius = 20;
            _equipButton.style.borderWidth = 0;
            _equipButton.style.fontSize = 14;
            _equipButton.style.color = Color.white;
            
            _skillsButton = new Button(ToggleSkillsDisplay);
            _skillsButton.text = "SKILLS";
            _skillsButton.style.flexGrow = 1;
            _skillsButton.style.height = 40;
            _skillsButton.style.marginLeft = 4;
            _skillsButton.style.backgroundColor = new Color(0.7f, 0.5f, 0.3f, 0.9f);
            _skillsButton.style.borderRadius = 20;
            _skillsButton.style.borderWidth = 0;
            _skillsButton.style.fontSize = 14;
            _skillsButton.style.color = Color.white;
            
            buttonContainer.Add(_upgradeButton);
            buttonContainer.Add(_equipButton);
            buttonContainer.Add(_skillsButton);
            
            Add(buttonContainer);
        }
        
        /// <summary>
        /// 🧿 Create skills display section
        /// </summary>
        private void CreateSkillsSection()
        {
            _skillsContainer = new VisualElement();
            _skillsContainer.style.backgroundColor = new Color(0.1f, 0.1f, 0.1f, 0.6f);
            _skillsContainer.style.borderRadius = 8;
            _skillsContainer.style.paddingTop = 12;
            _skillsContainer.style.paddingBottom = 12;
            _skillsContainer.style.paddingLeft = 16;
            _skillsContainer.style.paddingRight = 16;
            _skillsContainer.style.display = DisplayStyle.None;
            
            Add(_skillsContainer);
        }
        
        /// <summary>
        /// 🧿 Create empty state display
        /// </summary>
        private void CreateEmptyState()
        {
            _emptyStateLabel = new Label("Select a hero to view details");
            _emptyStateLabel.style.fontSize = 16;
            _emptyStateLabel.style.color = new Color(0.6f, 0.6f, 0.6f, 1f);
            _emptyStateLabel.style.unityTextAlign = TextAnchor.MiddleCenter;
            _emptyStateLabel.style.position = Position.Absolute;
            _emptyStateLabel.style.top = Length.Percent(50);
            _emptyStateLabel.style.left = 0;
            _emptyStateLabel.style.right = 0;
            _emptyStateLabel.style.transform = TransformOrigin.Initial;
            _emptyStateLabel.transform.position = new Vector3(0, -10, 0);
            
            Add(_emptyStateLabel);
        }
        
        /// <summary>
        /// 🧿 Create individual stat row display
        /// </summary>
        private Label CreateStatRow(string statName, string statValue)
        {
            var statRow = new VisualElement();
            statRow.style.flexDirection = FlexDirection.Row;
            statRow.style.justifyContent = Justify.SpaceBetween;
            statRow.style.marginBottom = 4;
            
            var nameLabel = new Label(statName);
            nameLabel.style.fontSize = 12;
            nameLabel.style.color = new Color(0.8f, 0.8f, 0.8f, 1f);
            
            var valueLabel = new Label(statValue);
            valueLabel.style.fontSize = 12;
            valueLabel.style.color = Color.white;
            valueLabel.style.unityFontStyleAndWeight = FontStyle.Bold;
            
            statRow.Add(nameLabel);
            statRow.Add(valueLabel);
            
            return valueLabel; // Return value label for easy updates
        }
        
        /// <summary>
        /// 🧿 Update hero header information
        /// </summary>
        private void UpdateHeroDisplay()
        {
            _heroName.text = _currentHero.heroName;
            _heroLevel.text = $"Level {_currentHero.level}";
            _heroPower.text = $"Power: {_currentHero.CalculateTotalPower()}";
            
            // Update rarity indicator color
            _rarityIndicator.style.backgroundColor = GetRarityColor(_currentHero.rarity);
            
            // Update portrait if available
            if (_currentHero.heroPortrait != null)
            {
                _heroPortrait.style.backgroundImage = new StyleBackground(_currentHero.heroPortrait);
            }
            else if (_currentHero.heroIcon != null)
            {
                _heroPortrait.style.backgroundImage = new StyleBackground(_currentHero.heroIcon);
            }
        }
        
        /// <summary>
        /// 🧿 Update stats display with current hero stats
        /// </summary>
        private void UpdateStatsDisplay()
        {
            var stats = _currentHero.GetCurrentStats();
            
            _attackStat.text = stats.attack.ToString();
            _defenseStat.text = stats.defense.ToString();
            _healthStat.text = stats.health.ToString();
            _speedStat.text = stats.speed.ToString();
            _critRateStat.text = $"{(stats.criticalRate * 100):F1}%";
            _critDamageStat.text = $"{(stats.criticalDamage * 100):F0}%";
        }
        
        /// <summary>
        /// 🧿 Update evolution panel with current stage and requirements
        /// </summary>
        private void UpdateEvolutionPanel()
        {
            // Update evolution stars
            _evolutionStars.Clear();
            for (int i = 0; i < _currentHero.maxEvolutionStage; i++)
            {
                var star = new VisualElement();
                star.style.width = 20;
                star.style.height = 20;
                star.style.marginLeft = 2;
                star.style.marginRight = 2;
                star.style.backgroundColor = i < _currentHero.evolutionStage ? 
                    new Color(1f, 0.3f, 0.8f, 1f) : 
                    new Color(0.3f, 0.3f, 0.3f, 0.8f);
                star.style.borderRadius = 10;
                _evolutionStars.Add(star);
            }
            
            // Update evolution button and cost
            bool canEvolve = _currentHero.CanEvolve();
            _evolutionButton.SetEnabled(canEvolve && _currentHero.isOwned);
            _evolutionCost.text = $"Cost: {_currentHero.evolutionCost}";
            
            if (!canEvolve)
            {
                if (_currentHero.evolutionStage >= _currentHero.maxEvolutionStage)
                {
                    _evolutionButton.text = "MAX";
                    _evolutionCost.text = "Fully Evolved";
                }
                else
                {
                    _evolutionButton.text = "LOCKED";
                    _evolutionCost.text = $"Requires Level {_currentHero.maxLevel}";
                }
            }
            
            // Update evolution materials
            _evolutionMaterials.Clear();
            if (canEvolve && _currentHero.evolutionMaterials.Length > 0)
            {
                for (int i = 0; i < _currentHero.evolutionMaterials.Length; i++)
                {
                    var materialSlot = new VisualElement();
                    materialSlot.style.width = 30;
                    materialSlot.style.height = 30;
                    materialSlot.style.backgroundColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
                    materialSlot.style.borderRadius = 4;
                    materialSlot.style.marginRight = 4;
                    
                    var countLabel = new Label(_currentHero.evolutionMaterialCounts[i].ToString());
                    countLabel.style.position = Position.Absolute;
                    countLabel.style.bottom = -2;
                    countLabel.style.right = -2;
                    countLabel.style.fontSize = 8;
                    countLabel.style.color = Color.white;
                    countLabel.style.backgroundColor = new Color(0f, 0f, 0f, 0.8f);
                    countLabel.style.borderRadius = 6;
                    countLabel.style.paddingLeft = 3;
                    countLabel.style.paddingRight = 3;
                    
                    materialSlot.Add(countLabel);
                    _evolutionMaterials.Add(materialSlot);
                }
            }
        }
        
        /// <summary>
        /// 🧿 Update action button states
        /// </summary>
        private void UpdateActionButtons()
        {
            bool isOwned = _currentHero.isOwned;
            
            _upgradeButton.SetEnabled(isOwned && _currentHero.level < _currentHero.maxLevel);
            _equipButton.SetEnabled(isOwned);
            _skillsButton.SetEnabled(isOwned);
            
            if (!isOwned)
            {
                _upgradeButton.text = "NOT OWNED";
                _equipButton.text = "NOT OWNED";
                _skillsButton.text = "NOT OWNED";
            }
            else
            {
                _upgradeButton.text = _currentHero.level >= _currentHero.maxLevel ? "MAX LEVEL" : "UPGRADE";
                _equipButton.text = "EQUIP";
                _skillsButton.text = "SKILLS";
            }
        }
        
        /// <summary>
        /// 🧿 Update skills display
        /// </summary>
        private void UpdateSkillsDisplay()
        {
            _skillsContainer.Clear();
            
            if (_currentHero.skillIds.Length > 0)
            {
                var skillsTitle = new Label("Skills");
                skillsTitle.style.fontSize = 14;
                skillsTitle.style.color = Color.white;
                skillsTitle.style.unityFontStyleAndWeight = FontStyle.Bold;
                skillsTitle.style.marginBottom = 8;
                _skillsContainer.Add(skillsTitle);
                
                foreach (var skillId in _currentHero.skillIds)
                {
                    var skillRow = new VisualElement();
                    skillRow.style.flexDirection = FlexDirection.Row;
                    skillRow.style.marginBottom = 4;
                    
                    var skillIcon = new VisualElement();
                    skillIcon.style.width = 24;
                    skillIcon.style.height = 24;
                    skillIcon.style.backgroundColor = new Color(0.3f, 0.3f, 0.7f, 0.8f);
                    skillIcon.style.borderRadius = 4;
                    skillIcon.style.marginRight = 8;
                    
                    var skillName = new Label(skillId);
                    skillName.style.fontSize = 12;
                    skillName.style.color = Color.white;
                    skillName.style.flexGrow = 1;
                    
                    skillRow.Add(skillIcon);
                    skillRow.Add(skillName);
                    _skillsContainer.Add(skillRow);
                }
            }
            else
            {
                var noSkillsLabel = new Label("No skills available");
                noSkillsLabel.style.fontSize = 12;
                noSkillsLabel.style.color = new Color(0.6f, 0.6f, 0.6f, 1f);
                noSkillsLabel.style.unityTextAlign = TextAnchor.MiddleCenter;
                _skillsContainer.Add(noSkillsLabel);
            }
        }
        
        /// <summary>
        /// 🧿 Show empty state when no hero is selected
        /// </summary>
        private void ShowEmptyState()
        {
            _emptyStateLabel.style.display = DisplayStyle.Flex;
            SetChildrenDisplay(DisplayStyle.None);
        }
        
        /// <summary>
        /// 🧿 Hide empty state when hero is displayed
        /// </summary>
        private void HideEmptyState()
        {
            _emptyStateLabel.style.display = DisplayStyle.None;
            SetChildrenDisplay(DisplayStyle.Flex);
        }
        
        /// <summary>
        /// 🧿 Set display state for all child elements except empty state
        /// </summary>
        private void SetChildrenDisplay(DisplayStyle displayStyle)
        {
            foreach (var child in Children())
            {
                if (child != _emptyStateLabel)
                {
                    child.style.display = displayStyle;
                }
            }
        }
        
        /// <summary>
        /// 🧿 Toggle skills display visibility
        /// </summary>
        private void ToggleSkillsDisplay()
        {
            bool isVisible = _skillsContainer.style.display == DisplayStyle.Flex;
            _skillsContainer.style.display = isVisible ? DisplayStyle.None : DisplayStyle.Flex;
            _skillsButton.text = isVisible ? "SKILLS" : "HIDE SKILLS";
        }
        
        /// <summary>
        /// 🧿 Get color for hero rarity
        /// </summary>
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
        
        #endregion
    }
}