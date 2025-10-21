using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace LivingDevAgent.Runtime.CompanionBattler
{
    /// <summary>
    /// Companion Battle UI system handling collection, team building, and battle interface
    /// KeeperNote: Complete UI suite for companion battler experience
    /// </summary>
    public class CompanionBattleUI : MonoBehaviour
    {
        [Header("Main UI Panels")]
        [SerializeField] private GameObject collectionPanel;
        [SerializeField] private GameObject teamBuildingPanel;
        [SerializeField] private GameObject battlePanel;
        [SerializeField] private GameObject evolutionPanel;

        [Header("Collection UI")]
        [SerializeField] private Transform companionGrid;
        [SerializeField] private GameObject companionCardPrefab;
        [SerializeField] private TextMeshProUGUI collectionTitle;

        [Header("Team Building UI")]
        [SerializeField] private Transform teamSlots;
        [SerializeField] private Button startBattleButton;
        [SerializeField] private TextMeshProUGUI teamPowerLevel;

        [Header("Battle UI")]
        [SerializeField] private Transform playerTeamDisplay;
        [SerializeField] private Transform enemyTeamDisplay;
        [SerializeField] private Transform abilityButtons;
        [SerializeField] private GameObject abilityButtonPrefab;
        [SerializeField] private TextMeshProUGUI turnIndicator;
        [SerializeField] private TextMeshProUGUI battleLog;
        [SerializeField] private Button endTurnButton;

        [Header("Battle HUD")]
        [SerializeField] private Slider playerHealthBar;
        [SerializeField] private Slider playerEnergyBar;
        [SerializeField] private TextMeshProUGUI playerStatsText;
        [SerializeField] private Image playerElementIcon;
        [SerializeField] private TextMeshProUGUI battleQuipText;

        [Header("Evolution UI")]
        [SerializeField] private Image evolutionCompanionImage;
        [SerializeField] private TextMeshProUGUI evolutionText;
        [SerializeField] private Button confirmEvolutionButton;
        [SerializeField] private ParticleSystem evolutionEffects;

        // UI state
        private List<Companion> availableCompanions = new();
        private readonly List<Companion> selectedTeam = new();
        private Companion activePlayerCompanion;
        private Coroutine quipDisplayCoroutine;

        // UI events
        public System.Action<List<Companion>> OnTeamSelected;
        public System.Action<Companion, CompanionAbility, Companion> OnAbilitySelected;
        public System.Action OnBattleStartRequested;

        private void Start()
        {
            InitializeUI();
        }

        private void InitializeUI()
        {
            // Setup button listeners
            if (startBattleButton != null)
                startBattleButton.onClick.AddListener(() => OnBattleStartRequested?.Invoke());

            if (endTurnButton != null)
                endTurnButton.onClick.AddListener(EndPlayerTurn);

            if (confirmEvolutionButton != null)
                confirmEvolutionButton.onClick.AddListener(ConfirmEvolution);

            // Initialize with collection view
            ShowCollectionPanel();
        }

        #region Panel Management

        public void ShowCollectionPanel()
        {
            SetActivePanel(collectionPanel);
            RefreshCompanionCollection();
        }

        public void ShowTeamBuildingPanel()
        {
            SetActivePanel(teamBuildingPanel);
            RefreshTeamBuilding();
        }

        public void ShowBattlePanel()
        {
            SetActivePanel(battlePanel);
        }

        public void ShowEvolutionPanel(Companion companion)
        {
            SetActivePanel(evolutionPanel);
            SetupEvolutionCeremony(companion);
        }

        private void SetActivePanel(GameObject activePanel)
        {
            if (collectionPanel != null)
                collectionPanel.SetActive(collectionPanel == activePanel);
            if (teamBuildingPanel != null)
                teamBuildingPanel.SetActive(teamBuildingPanel == activePanel);
            if (battlePanel != null)
                battlePanel.SetActive(battlePanel == activePanel);
            if (evolutionPanel != null)
                evolutionPanel.SetActive(evolutionPanel == activePanel);
        }

        #endregion

        #region Collection UI

        /// <summary>
        /// Refresh companion collection display
        /// KeeperNote: Loads from badge pet system and displays with battle readiness
        /// </summary>
        private void RefreshCompanionCollection()
        {
            if (companionGrid == null)
                return;

            // Clear existing cards
            foreach (Transform child in companionGrid)
            {
                Destroy(child.gameObject);
            }

            // Create companion cards
            foreach (var companion in availableCompanions)
            {
                CreateCompanionCard(companion);
            }

            // Update collection title
            if (collectionTitle != null)
            {
                collectionTitle.text = $"Companion Collection ({availableCompanions.Count})";
            }
        }

        private void CreateCompanionCard(Companion companion)
        {
            if (companionCardPrefab == null)
                return;

            GameObject cardObj = Instantiate(companionCardPrefab, companionGrid);

            if (cardObj.TryGetComponent<CompanionCard>(out var card))
            {
                card.SetupCard(companion);
                card.OnCardSelected += OnCompanionCardSelected;
            }
        }

        private void OnCompanionCardSelected(Companion companion)
        {
            Debug.Log($"[CompanionUI] Selected companion: {companion.Name}");

            // Add to team if there's space
            if (selectedTeam.Count < 3 && !selectedTeam.Contains(companion))
            {
                selectedTeam.Add(companion);
                RefreshTeamBuilding();
            }
        }

        #endregion

        #region Team Building UI

        private void RefreshTeamBuilding()
        {
            if (teamSlots == null)
                return;

            // Update team slots
            for (int i = 0; i < teamSlots.childCount && i < 3; i++)
            {
                Transform slot = teamSlots.GetChild(i);
                bool hasCompanion = i < selectedTeam.Count;

                // Show/hide companion in slot
                slot.gameObject.SetActive(hasCompanion);

                if (hasCompanion)
                {
                    UpdateTeamSlot(slot, selectedTeam[i]);
                }
            }

            // Update team power level
            UpdateTeamPowerLevel();

            // Enable/disable start battle button
            if (startBattleButton != null)
            {
                startBattleButton.interactable = selectedTeam.Count > 0;
            }
        }

        private void UpdateTeamSlot(Transform slot, Companion companion)
        {
            // Update slot with companion info
            var nameText = slot.GetComponentInChildren<TextMeshProUGUI>();
            if (nameText != null)
            {
                nameText.text = companion.Name;
            }

            var image = slot.GetComponentInChildren<Image>();
            if (image != null && companion.GetComponent<SpriteRenderer>() != null)
            {
                image.sprite = companion.GetComponent<SpriteRenderer>().sprite;
            }
        }

        private void UpdateTeamPowerLevel()
        {
            if (teamPowerLevel == null)
                return;

            int totalPower = 0;
            foreach (var companion in selectedTeam)
            {
                totalPower += companion.BattleStats.attack + companion.BattleStats.defense + companion.BattleStats.speed;
            }

            teamPowerLevel.text = $"Team Power: {totalPower}";
        }

        #endregion

        #region Battle UI

        /// <summary>
        /// Initialize battle UI with team displays
        /// KeeperNote: Sets up real-time battle interface with ability buttons
        /// </summary>
        public void InitializeBattleUI(List<Companion> playerTeam, List<Companion> enemyTeam)
        {
            // Setup team displays
            SetupTeamDisplay(playerTeamDisplay, playerTeam);
            SetupTeamDisplay(enemyTeamDisplay, enemyTeam);

            // Clear battle log
            if (battleLog != null)
            {
                battleLog.text = "Battle begins!\n";
            }

            ShowBattlePanel();
        }

        private void SetupTeamDisplay(Transform teamDisplay, List<Companion> team)
        {
            if (teamDisplay == null)
                return;

            // Clear existing displays
            foreach (Transform child in teamDisplay)
            {
                Destroy(child.gameObject);
            }

            // Create companion status displays
            foreach (var companion in team)
            {
                CreateCompanionStatusDisplay(teamDisplay, companion);
            }
        }

        private void CreateCompanionStatusDisplay(Transform parent, Companion companion)
        {
            GameObject statusObj = new($"{companion.Name}_Status");
            statusObj.transform.SetParent(parent);

            // Add companion status UI components - these are needed for proper UI layering
            var _ = statusObj.AddComponent<Canvas>();
            var _1 = statusObj.AddComponent<CanvasGroup>();

            // Health bar
            var healthBar = CreateStatusBar(statusObj.transform, "Health", Color.red);
            var energyBar = CreateStatusBar(statusObj.transform, "Energy", Color.blue);

            // Update status display
            UpdateCompanionStatusDisplay(companion, healthBar, energyBar);
        }

        private Slider CreateStatusBar(Transform parent, string name, Color color)
        {
            GameObject barObj = new($"{name}Bar");
            barObj.transform.SetParent(parent);

            var slider = barObj.AddComponent<Slider>();
            slider.minValue = 0f;
            slider.maxValue = 1f;
            slider.value = 1f;

            // Add visual components
            var background = new GameObject("Background");
            background.transform.SetParent(barObj.transform);
            var bgImage = background.AddComponent<Image>();
            bgImage.color = Color.gray;

            var fill = new GameObject("Fill");
            fill.transform.SetParent(barObj.transform);
            var fillImage = fill.AddComponent<Image>();
            fillImage.color = color;

            slider.fillRect = fillImage.rectTransform;

            return slider;
        }

        public void UpdateCompanionStatus(Companion companion)
        {
            // Find and update companion's status display
            Transform statusDisplay = FindCompanionStatusDisplay(companion);
            if (statusDisplay != null)
            {
                var healthBar = statusDisplay.GetComponentInChildren<Slider>();
                if (healthBar != null)
                {
                    healthBar.value = companion.BattleStats.HealthPercentage;
                }
            }
        }

        private Transform FindCompanionStatusDisplay(Companion companion)
        {
            // Search both team displays for companion status
            Transform found = null;
            if (playerTeamDisplay != null)
                found = playerTeamDisplay.Find($"{companion.Name}_Status");
            if (found == null && enemyTeamDisplay != null)
                found = enemyTeamDisplay.Find($"{companion.Name}_Status");
            return found;
        }

        private void UpdateCompanionStatusDisplay(Companion companion, Slider healthBar, Slider energyBar)
        {
            if (healthBar != null)
                healthBar.value = companion.BattleStats.HealthPercentage;
            if (energyBar != null)
                energyBar.value = companion.BattleStats.EnergyPercentage;
        }

        /// <summary>
        /// Enable player controls for active companion
        /// KeeperNote: Shows available abilities and handles player input
        /// </summary>
        public void EnablePlayerControls(Companion companion)
        {
            activePlayerCompanion = companion;

            // Update turn indicator
            if (turnIndicator != null)
            {
                turnIndicator.text = $"{companion.Name}'s Turn";
            }

            // Update player HUD
            UpdatePlayerHUD(companion);

            // Setup ability buttons
            SetupAbilityButtons(companion);

            // Enable end turn button
            if (endTurnButton != null)
            {
                endTurnButton.interactable = true;
            }
        }

        private void UpdatePlayerHUD(Companion companion)
        {
            if (playerHealthBar != null)
                playerHealthBar.value = companion.BattleStats.HealthPercentage;

            if (playerEnergyBar != null)
                playerEnergyBar.value = companion.BattleStats.EnergyPercentage;

            if (playerStatsText != null)
            {
                playerStatsText.text = $"{companion.Name}\nHP: {companion.BattleStats.health}/{companion.BattleStats.maxHealth}\n" +
                                     $"Energy: {companion.BattleStats.energy}/{companion.BattleStats.maxEnergy}";
            }

            // Update element icon based on companion element
            if (playerElementIcon != null)
            {
                playerElementIcon.color = GetElementColor(companion.Element);
            }
        }

        private Color GetElementColor(CompanionElement element)
        {
            return element switch
            {
                CompanionElement.Logic => Color.blue,
                CompanionElement.Creativity => Color.magenta,
                CompanionElement.Order => Color.white,
                CompanionElement.Chaos => Color.red,
                CompanionElement.Balance => Color.gray,
                _ => Color.white,
            };
        }

        private void SetupAbilityButtons(Companion companion)
        {
            if (abilityButtons == null)
                return;

            // Clear existing buttons
            foreach (Transform child in abilityButtons)
            {
                Destroy(child.gameObject);
            }

            // Create ability buttons
            foreach (var ability in companion.Abilities)
            {
                CreateAbilityButton(ability, companion);
            }
        }

        private void CreateAbilityButton(CompanionAbility ability, Companion user)
        {
            if (abilityButtonPrefab == null)
                return;

            GameObject buttonObj = Instantiate(abilityButtonPrefab, abilityButtons);
            Button button = buttonObj.GetComponent<Button>();
            TextMeshProUGUI buttonText = buttonObj.GetComponentInChildren<TextMeshProUGUI>();

            if (buttonText != null)
            {
                buttonText.text = $"{ability.name}\n({ability.energyCost} Energy)";
            }

            if (button != null)
            {
                button.interactable = ability.CanUse(user.BattleStats);
                button.onClick.AddListener(() => OnAbilityButtonClicked(ability, user));
            }
        }

        private void OnAbilityButtonClicked(CompanionAbility ability, Companion user)
        {
            // For simplicity, auto-select target based on ability type
            Companion target = SelectAbilityTarget(ability);
            OnAbilitySelected?.Invoke(user, ability, target);
        }

        private Companion SelectAbilityTarget(CompanionAbility ability)
        {
            // Simplified target selection - could be enhanced with target selection UI
            return ability.targetType switch
            {
                TargetType.Self => activePlayerCompanion,
                TargetType.Enemy => null,// Select first living enemy
                                         // 👀This would need reference to enemy team from battle manager
                                         // Placeholder
                _ => null,
            };
        }

        private void EndPlayerTurn()
        {
            if (endTurnButton != null)
            {
                endTurnButton.interactable = false;
            }

            // Disable ability buttons
            if (abilityButtons != null)
            {
                foreach (Transform child in abilityButtons)
                {
                    if (child.TryGetComponent<Button>(out var button))
                        button.interactable = false;
                }
            }
        }

        public void ShowAbilityEffect(Companion user, CompanionAbility ability)
        {
            // Log ability use
            if (battleLog != null)
            {
                battleLog.text += $"{user.Name} used {ability.name}!\n";
            }

            // Could add visual effects here
        }

        public void ShowBattleQuip(Companion speaker, string quip)
        {
            if (battleQuipText != null)
            {
                if (quipDisplayCoroutine != null)
                {
                    StopCoroutine(quipDisplayCoroutine);
                }
                quipDisplayCoroutine = StartCoroutine(DisplayQuip(speaker, quip));
            }
        }

        private IEnumerator DisplayQuip(Companion speaker, string quip)
        {
            battleQuipText.text = $"{speaker.Name}: \"{quip}\"";
            battleQuipText.gameObject.SetActive(true);

            yield return new WaitForSeconds(3f);

            battleQuipText.gameObject.SetActive(false);
        }

        #endregion

        #region Evolution UI

        /// <summary>
        /// Setup evolution ceremony interface
        /// KeeperNote: Handles companion evolution with narrative triggers
        /// </summary>
        private void SetupEvolutionCeremony(Companion companion)
        {
            if (evolutionCompanionImage != null)
            {
                if (companion.TryGetComponent<SpriteRenderer>(out var spriteRenderer))
                {
                    evolutionCompanionImage.sprite = spriteRenderer.sprite;
                }
            }

            if (evolutionText != null)
            {
                evolutionText.text = $"{companion.Name} is ready to evolve!\n" +
                                   $"Bond Level: {companion.BondLevel}\n" +
                                   $"Battles Won: {companion.BattleStats.battlesWon}\n" +
                                   $"New abilities and enhanced stats await!";
            }

            if (evolutionEffects != null)
            {
                evolutionEffects.Play();
            }
        }

        private void ConfirmEvolution()
        {
            // Trigger evolution ceremony
            Debug.Log("[CompanionUI] Evolution ceremony confirmed!");

            // Close evolution panel
            SetActivePanel(collectionPanel);
        }

        #endregion

        #region Public Interface

        public void LoadCompanionCollection(List<Companion> companions)
        {
            availableCompanions = companions;
            RefreshCompanionCollection();
        }

        public List<Companion> GetSelectedTeam()
        {
            return new List<Companion>(selectedTeam);
        }

        public void ClearSelectedTeam()
        {
            selectedTeam.Clear();
            RefreshTeamBuilding();
        }

        #endregion
    }

    /// <summary>
    /// Individual companion card component for collection UI
    /// KeeperNote: Displays companion info with battle readiness indicators
    /// </summary>
    public class CompanionCard : MonoBehaviour
    {
        [Header("Card Components")]
        [SerializeField] private Image companionImage;
        [SerializeField] private TextMeshProUGUI nameText;
        [SerializeField] private TextMeshProUGUI statsText;
        [SerializeField] private Image elementIcon;
        [SerializeField] private Button selectButton;

        private Companion companion;
        public System.Action<Companion> OnCardSelected;

        private void Start()
        {
            if (selectButton != null)
            {
                selectButton.onClick.AddListener(() => OnCardSelected?.Invoke(companion));
            }
        }

        public void SetupCard(Companion companion)
        {
            this.companion = companion;

            if (nameText != null)
            {
                nameText.text = companion.Name;
            }

            if (statsText != null)
            {
                statsText.text = $"Level: {companion.BondLevel}\n" +
                               $"Wins: {companion.BattleStats.battlesWon}\n" +
                               $"Element: {companion.Element}";
            }

            if (companionImage != null)
            {
                if (companion.TryGetComponent<SpriteRenderer>(out var spriteRenderer))
                {
                    companionImage.sprite = spriteRenderer.sprite;
                }
            }

            if (elementIcon != null)
            {
                elementIcon.color = GetElementColor(companion.Element);
            }
        }

        private Color GetElementColor(CompanionElement element)
        {
            return element switch
            {
                CompanionElement.Logic => Color.blue,
                CompanionElement.Creativity => Color.magenta,
                CompanionElement.Order => Color.white,
                CompanionElement.Chaos => Color.red,
                CompanionElement.Balance => Color.gray,
                _ => Color.white,
            };
        }
    }
}
