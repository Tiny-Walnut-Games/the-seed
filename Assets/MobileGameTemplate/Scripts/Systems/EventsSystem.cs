using UnityEngine;
using UnityEngine.UIElements;
using MobileGameTemplate.Core; // 🔧 Unity 2022.3 Compatibility Bridge
using System.Collections.Generic;
using System.Linq; // 🔧 C# 10 Compatibility

namespace MobileGameTemplate.Systems
{
    /// <summary>
    /// 🎉 INTENDED EXPANSION ZONE - Events system with notifications
    /// Time-based events, daily quests, seasonal activities for mobile games
    /// Designed for player engagement and retention in action mobile games
    /// 
    /// Sacred Vision: Transform gameplay into engaging event-driven adventures!
    /// </summary>
    public class EventsSystem : VisualElement
    {
        #region USS Class Names
        public static readonly string UssClassName = "events-system";
        public static readonly string TabUssClassName = UssClassName + "__tab";
        public static readonly string TabActiveUssClassName = TabUssClassName + "--active";
        public static readonly string ContentUssClassName = UssClassName + "__content";
        public static readonly string EventCardUssClassName = UssClassName + "__event-card";
        public static readonly string EventActiveUssClassName = EventCardUssClassName + "--active";
        public static readonly string EventCompletedUssClassName = EventCardUssClassName + "--completed";
        public static readonly string EventExpiredUssClassName = EventCardUssClassName + "--expired";
        #endregion
        
        #region Events
        public System.Action<GameEvent> OnEventStarted;
        public System.Action<GameEvent> OnEventCompleted;
        public System.Action<GameEvent> OnEventClaimRewards;
        public System.Action<GameEvent> OnEventDetailsRequested;
        public System.Action<NotificationSettings> OnNotificationSettingsChanged;
        #endregion
        
        #region Private Fields
        private VisualElement _tabContainer;
        private VisualElement _contentContainer;
        
        // Tabs
        private Button _activeTab;
        private Button _dailyTab;
        private Button _seasonalTab;
        private Button _achievementsTab;
        
        // Content panels
        private ScrollView _eventsScrollView;
        private VisualElement _eventsContainer;
        private VisualElement _notificationPanel;
        
        // Data
        private List<GameEvent> _allEvents = new List<GameEvent>();
        private List<GameEvent> _filteredEvents = new List<GameEvent>();
        private EventCategory _activeCategory = EventCategory.Active;
        private NotificationSettings _notificationSettings = new NotificationSettings();
        
        // Notification badge
        private VisualElement _notificationBadge;
        private Label _notificationCount;
        #endregion
        
        #region Constructor
        public EventsSystem()
        {
            AddToClassList(UssClassName);
            SetupEventsStructure();
            SetupTabs();
            SetupContentArea();
            SetupNotificationPanel();
            RegisterCallbacks();
            
            // Start update loop for timers
            schedule.Execute(UpdateEventTimers).Every(1000); // Update every second
        }
        #endregion
        
        #region Public API
        
        /// <summary>
        /// 🎉 Initialize events system with current events
        /// </summary>
        public void InitializeEvents(List<GameEvent> events, NotificationSettings settings)
        {
            _allEvents = new List<GameEvent>(events);
            _notificationSettings = settings;
            RefreshEventsList();
            UpdateNotificationBadge();
        }
        
        /// <summary>
        /// 🎉 Add new event to the system
        /// </summary>
        public void AddEvent(GameEvent gameEvent)
        {
            _allEvents.Add(gameEvent);
            RefreshEventsList();
            UpdateNotificationBadge();
            
            // Trigger notification if enabled
            if (_notificationSettings.enableEventNotifications)
            {
                TriggerEventNotification(gameEvent, "New event available!");
            }
        }
        
        /// <summary>
        /// 🎉 Update existing event
        /// </summary>
        public void UpdateEvent(GameEvent updatedEvent)
        {
            var existingEvent = _allEvents.FirstOrDefault(e => e.eventId == updatedEvent.eventId);
            if (existingEvent != null)
            {
                int index = _allEvents.IndexOf(existingEvent);
                _allEvents[index] = updatedEvent;
                RefreshEventsList();
                UpdateNotificationBadge();
            }
        }
        
        /// <summary>
        /// 🎉 Complete event and trigger rewards
        /// </summary>
        public void CompleteEvent(string eventId)
        {
            var gameEvent = _allEvents.FirstOrDefault(e => e.eventId == eventId);
            if (gameEvent != null && !gameEvent.isCompleted)
            {
                gameEvent.isCompleted = true;
                gameEvent.completedDate = System.DateTime.Now;
                RefreshEventsList();
                OnEventCompleted?.Invoke(gameEvent);
                
                if (_notificationSettings.enableRewardNotifications)
                {
                    TriggerEventNotification(gameEvent, "Event completed! Claim your rewards!");
                }
            }
        }
        
        /// <summary>
        /// 🎉 Switch to specific event category
        /// </summary>
        public void SwitchToCategory(EventCategory category)
        {
            SetActiveCategory(category);
        }
        
        /// <summary>
        /// 🎉 Get count of available events with rewards
        /// </summary>
        public int GetClaimableEventsCount()
        {
            return _allEvents.Count(e => e.isCompleted && !e.rewardsClaimed);
        }
        
        #endregion
        
        #region Private Methods
        
        /// <summary>
        /// 🎉 Setup main events UI structure
        /// </summary>
        private void SetupEventsStructure()
        {
            style.width = Length.Percent(100);
            style.height = Length.Percent(100);
            style.flexDirection = FlexDirection.Column;
            
            // Tab container with notification badge
            var headerContainer = new VisualElement();
            headerContainer.style.position = Position.Relative;
            
            _tabContainer = new VisualElement();
            _tabContainer.style.flexDirection = FlexDirection.Row;
            _tabContainer.style.height = 50;
            _tabContainer.style.backgroundColor = new Color(0.1f, 0.1f, 0.1f, 0.9f);
            _tabContainer.style.borderBottomWidth = 2;
            _tabContainer.style.borderBottomColor = new Color(0.3f, 0.3f, 0.3f, 0.8f);
            
            // Notification badge
            _notificationBadge = new VisualElement();
            _notificationBadge.style.position = Position.Absolute;
            _notificationBadge.style.top = 5;
            _notificationBadge.style.right = 10;
            _notificationBadge.style.width = 20;
            _notificationBadge.style.height = 20;
            _notificationBadge.style.backgroundColor = new Color(1f, 0.3f, 0.3f, 1f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
            _notificationBadge.style.alignItems = Align.Center;
            _notificationBadge.style.justifyContent = Justify.Center;
            _notificationBadge.style.display = DisplayStyle.None;
            
            _notificationCount = new Label("0");
            _notificationCount.style.fontSize = 10;
            _notificationCount.style.color = Color.white;
            _notificationCount.style.unityFontStyleAndWeight = FontStyle.Bold;
            
            _notificationBadge.Add(_notificationCount);
            
            headerContainer.Add(_tabContainer);
            headerContainer.Add(_notificationBadge);
            
            // Content container
            _contentContainer = new VisualElement();
            _contentContainer.AddToClassList(ContentUssClassName);
            _contentContainer.style.flexGrow = 1;
            _contentContainer.style.paddingTop = 8;
            _contentContainer.style.paddingBottom = 8;
            _contentContainer.style.paddingLeft = 8;
            _contentContainer.style.paddingRight = 8;
            
            Add(headerContainer);
            Add(_contentContainer);
        }
        
        /// <summary>
        /// 🎉 Setup event category tabs
        /// </summary>
        private void SetupTabs()
        {
            _activeTab = CreateTab("Active", EventCategory.Active);
            _dailyTab = CreateTab("Daily", EventCategory.Daily);
            _seasonalTab = CreateTab("Seasonal", EventCategory.Seasonal);
            _achievementsTab = CreateTab("Achievements", EventCategory.Achievement);
            
            _tabContainer.Add(_activeTab);
            _tabContainer.Add(_dailyTab);
            _tabContainer.Add(_seasonalTab);
            _tabContainer.Add(_achievementsTab);
            
            SetActiveCategory(EventCategory.Active);
        }
        
        /// <summary>
        /// 🎉 Create individual event tab
        /// </summary>
        private Button CreateTab(string label, EventCategory category)
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
        /// 🎉 Setup main content area with events list
        /// </summary>
        private void SetupContentArea()
        {
            _eventsScrollView = new ScrollView(ScrollViewMode.Vertical);
            _eventsScrollView.style.flexGrow = 1;
            
            _eventsContainer = new VisualElement();
            _eventsContainer.style.paddingTop = 8;
            _eventsContainer.style.paddingBottom = 8;
            
            _eventsScrollView.Add(_eventsContainer);
            _contentContainer.Add(_eventsScrollView);
        }
        
        /// <summary>
        /// 🎉 Setup notification settings panel
        /// </summary>
        private void SetupNotificationPanel()
        {
            _notificationPanel = new VisualElement();
            _notificationPanel.style.backgroundColor = new Color(0.1f, 0.1f, 0.1f, 0.9f);
            _notificationPanel.style.paddingTop = 12;
            _notificationPanel.style.paddingBottom = 12;
            _notificationPanel.style.paddingLeft = 12;
            _notificationPanel.style.paddingRight = 12;
            _notificationPanel.style.marginTop = 16;
            _notificationPanel.style.display = DisplayStyle.None;
            
            var notificationTitle = new Label("Notification Settings");
            notificationTitle.style.fontSize = 16;
            notificationTitle.style.color = Color.white;
            notificationTitle.style.unityFontStyleAndWeight = FontStyle.Bold;
            notificationTitle.style.marginBottom = 12;
            
            var eventNotificationsToggle = new Toggle("Event Start Notifications");
            eventNotificationsToggle.style.marginBottom = 8;
            eventNotificationsToggle.SetValueWithoutNotify(_notificationSettings.enableEventNotifications);
            eventNotificationsToggle.RegisterValueChangedCallback(evt => {
                _notificationSettings.enableEventNotifications = evt.newValue;
                OnNotificationSettingsChanged?.Invoke(_notificationSettings);
            });
            
            var rewardNotificationsToggle = new Toggle("Reward Notifications");
            rewardNotificationsToggle.style.marginBottom = 8;
            rewardNotificationsToggle.SetValueWithoutNotify(_notificationSettings.enableRewardNotifications);
            rewardNotificationsToggle.RegisterValueChangedCallback(evt => {
                _notificationSettings.enableRewardNotifications = evt.newValue;
                OnNotificationSettingsChanged?.Invoke(_notificationSettings);
            });
            
            var dailyReminderToggle = new Toggle("Daily Quest Reminders");
            dailyReminderToggle.style.marginBottom = 8;
            dailyReminderToggle.SetValueWithoutNotify(_notificationSettings.enableDailyReminders);
            dailyReminderToggle.RegisterValueChangedCallback(evt => {
                _notificationSettings.enableDailyReminders = evt.newValue;
                OnNotificationSettingsChanged?.Invoke(_notificationSettings);
            });
            
            _notificationPanel.Add(notificationTitle);
            _notificationPanel.Add(eventNotificationsToggle);
            _notificationPanel.Add(rewardNotificationsToggle);
            _notificationPanel.Add(dailyReminderToggle);
            
            _contentContainer.Add(_notificationPanel);
        }
        
        /// <summary>
        /// 🎉 Register UI event callbacks
        /// </summary>
        private void RegisterCallbacks()
        {
            // Long press on notification badge to show settings
            _notificationBadge.RegisterCallback<PointerDownEvent>(evt => {
                if (evt.button == 0) // Left click
                {
                    ToggleNotificationPanel();
                }
            });
        }
        
        /// <summary>
        /// 🎉 Set active event category and filter events
        /// </summary>
        private void SetActiveCategory(EventCategory category)
        {
            // Update tab visual states
            _activeTab.RemoveFromClassList(TabActiveUssClassName);
            _dailyTab.RemoveFromClassList(TabActiveUssClassName);
            _seasonalTab.RemoveFromClassList(TabActiveUssClassName);
            _achievementsTab.RemoveFromClassList(TabActiveUssClassName);
            
            _activeCategory = category;
            
            switch (category)
            {
                case EventCategory.Active:
                    _activeTab.AddToClassList(TabActiveUssClassName);
                    break;
                case EventCategory.Daily:
                    _dailyTab.AddToClassList(TabActiveUssClassName);
                    break;
                case EventCategory.Seasonal:
                    _seasonalTab.AddToClassList(TabActiveUssClassName);
                    break;
                case EventCategory.Achievement:
                    _achievementsTab.AddToClassList(TabActiveUssClassName);
                    break;
            }
            
            UpdateTabStyles();
            RefreshEventsList();
        }
        
        /// <summary>
        /// 🎉 Update visual styles for active/inactive tabs
        /// </summary>
        private void UpdateTabStyles()
        {
            var tabs = new[] { _activeTab, _dailyTab, _seasonalTab, _achievementsTab };
            
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
        /// 🎉 Refresh events list based on active category
        /// </summary>
        private void RefreshEventsList()
        {
            // Filter events by category and status
            _filteredEvents = _allEvents.Where(e => FilterEventByCategory(e, _activeCategory)).ToList();
            
            // Sort events by priority and time
            _filteredEvents = _filteredEvents.OrderBy(e => e.isCompleted)
                                           .ThenBy(e => e.endDate)
                                           .ThenByDescending(e => (int)e.priority)
                                           .ToList();
            
            // Clear and rebuild events list
            _eventsContainer.Clear();
            
            if (_filteredEvents.Count == 0)
            {
                ShowEmptyState();
            }
            else
            {
                foreach (var gameEvent in _filteredEvents)
                {
                    var eventCard = CreateEventCard(gameEvent);
                    _eventsContainer.Add(eventCard);
                }
            }
        }
        
        /// <summary>
        /// 🎉 Filter event by category
        /// </summary>
        private bool FilterEventByCategory(GameEvent gameEvent, EventCategory category)
        {
            switch (category)
            {
                case EventCategory.Active:
                    return gameEvent.IsActive() && !gameEvent.isCompleted;
                case EventCategory.Daily:
                    return gameEvent.eventType == EventType.Daily;
                case EventCategory.Seasonal:
                    return gameEvent.eventType == EventType.Seasonal || gameEvent.eventType == EventType.LimitedTime;
                case EventCategory.Achievement:
                    return gameEvent.eventType == EventType.Achievement;
                default:
                    return true;
            }
        }
        
        /// <summary>
        /// 🎉 Create visual card for game event
        /// </summary>
        private VisualElement CreateEventCard(GameEvent gameEvent)
        {
            var card = new VisualElement();
            card.AddToClassList(EventCardUssClassName);
            card.style.backgroundColor = GetEventTypeColor(gameEvent.eventType);
            card.style.paddingTop = 12;
            card.style.paddingBottom = 12;
            card.style.paddingLeft = 12;
            card.style.paddingRight = 12;
            // 🔧 LEGENDARY FIX: borderRadius, borderWidth, borderColor not available in Unity 2022.3
            
            // Event header
            var headerContainer = new VisualElement();
            headerContainer.style.flexDirection = FlexDirection.Row;
            headerContainer.style.justifyContent = Justify.SpaceBetween;
            headerContainer.style.alignItems = Align.Center;
            headerContainer.style.marginBottom = 12;
            
            var titleContainer = new VisualElement();
            titleContainer.style.flexGrow = 1;
            
            var eventTitle = new Label(gameEvent.eventName);
            eventTitle.style.fontSize = 16;
            eventTitle.style.color = Color.white;
            eventTitle.style.unityFontStyleAndWeight = FontStyle.Bold;
            eventTitle.style.marginBottom = 4;
            
            var eventCategory = new Label(gameEvent.eventType.ToString());
            eventCategory.style.fontSize = 12;
            eventCategory.style.color = GetEventTypeColor(gameEvent.eventType);
            eventCategory.style.backgroundColor = new Color(0f, 0f, 0f, 0.3f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
            eventCategory.style.paddingLeft = 6;
            eventCategory.style.paddingRight = 6;
            eventCategory.style.paddingTop = 2;
            eventCategory.style.paddingBottom = 2;
            
            titleContainer.Add(eventTitle);
            titleContainer.Add(eventCategory);
            
            // Timer/Status display
            var statusContainer = new VisualElement();
            statusContainer.style.alignItems = Align.FlexEnd;
            
            var timeLabel = new Label();
            timeLabel.name = $"timer-{gameEvent.eventId}";
            timeLabel.style.fontSize = 12;
            timeLabel.style.color = new Color(0.8f, 0.8f, 0.8f, 1f);
            timeLabel.style.marginBottom = 4;
            
            var priorityIndicator = new VisualElement();
            priorityIndicator.style.width = 8;
            priorityIndicator.style.height = 8;
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
            priorityIndicator.style.backgroundColor = GetPriorityColor(gameEvent.priority);
            
            statusContainer.Add(timeLabel);
            statusContainer.Add(priorityIndicator);
            
            headerContainer.Add(titleContainer);
            headerContainer.Add(statusContainer);
            
            // Event description
            var description = new Label(gameEvent.description);
            description.style.fontSize = 14;
            description.style.color = new Color(0.8f, 0.8f, 0.8f, 1f);
            description.style.whiteSpace = WhiteSpace.Normal;
            description.style.marginBottom = 12;
            
            // Progress section
            var progressContainer = CreateProgressSection(gameEvent);
            
            // Rewards section
            var rewardsContainer = CreateRewardsSection(gameEvent);
            
            // Action buttons
            var actionsContainer = CreateActionsSection(gameEvent);
            
            card.Add(headerContainer);
            card.Add(description);
            card.Add(progressContainer);
            card.Add(rewardsContainer);
            card.Add(actionsContainer);
            
            // Update timer display
            UpdateEventTimer(gameEvent, timeLabel);
            
            return card;
        }
        
        /// <summary>
        /// 🎉 Create progress section for event
        /// </summary>
        private VisualElement CreateProgressSection(GameEvent gameEvent)
        {
            var container = new VisualElement();
            container.style.marginBottom = 12;
            
            if (gameEvent.objectives.Count > 0)
            {
                var progressTitle = new Label("Progress");
                progressTitle.style.fontSize = 14;
                progressTitle.style.color = Color.white;
                progressTitle.style.unityFontStyleAndWeight = FontStyle.Bold;
                progressTitle.style.marginBottom = 6;
                
                container.Add(progressTitle);
                
                foreach (var objective in gameEvent.objectives)
                {
                    var objectiveRow = new VisualElement();
                    objectiveRow.style.flexDirection = FlexDirection.Row;
                    objectiveRow.style.justifyContent = Justify.SpaceBetween;
                    objectiveRow.style.alignItems = Align.Center;
                    objectiveRow.style.marginBottom = 4;
                    
                    var objectiveText = new Label(objective.description);
                    objectiveText.style.fontSize = 12;
                    objectiveText.style.color = objective.isCompleted ? 
                        new Color(0.3f, 0.7f, 0.3f, 1f) : 
                        new Color(0.8f, 0.8f, 0.8f, 1f);
                    objectiveText.style.flexGrow = 1;
                    
                    var progressText = new Label($"{objective.currentValue}/{objective.targetValue}");
                    progressText.style.fontSize = 12;
                    progressText.style.color = new Color(0.7f, 0.7f, 0.7f, 1f);
                    
                    var checkIcon = new Label(objective.isCompleted ? "✓" : "");
                    checkIcon.style.fontSize = 14;
                    checkIcon.style.color = new Color(0.3f, 0.7f, 0.3f, 1f);
                    checkIcon.style.width = 20;
                    checkIcon.style.unityTextAlign = TextAnchor.MiddleCenter;
                    
                    objectiveRow.Add(objectiveText);
                    objectiveRow.Add(progressText);
                    objectiveRow.Add(checkIcon);
                    
                    container.Add(objectiveRow);
                }
            }
            
            return container;
        }
        
        /// <summary>
        /// 🎉 Create rewards section for event
        /// </summary>
        private VisualElement CreateRewardsSection(GameEvent gameEvent)
        {
            var container = new VisualElement();
            container.style.marginBottom = 12;
            
            if (gameEvent.rewards.Count > 0)
            {
                var rewardsTitle = new Label("Rewards");
                rewardsTitle.style.fontSize = 14;
                rewardsTitle.style.color = Color.white;
                rewardsTitle.style.unityFontStyleAndWeight = FontStyle.Bold;
                rewardsTitle.style.marginBottom = 6;
                
                var rewardsRow = new VisualElement();
                rewardsRow.style.flexDirection = FlexDirection.Row;
                rewardsRow.style.flexWrap = Wrap.Wrap;
                
                foreach (var reward in gameEvent.rewards)
                {
                    var rewardChip = new VisualElement();
                    rewardChip.style.flexDirection = FlexDirection.Row;
                    rewardChip.style.alignItems = Align.Center;
                    rewardChip.style.backgroundColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
                    rewardChip.style.paddingLeft = 8;
                    rewardChip.style.paddingRight = 8;
                    rewardChip.style.paddingTop = 4;
                    rewardChip.style.paddingBottom = 4;
                    rewardChip.style.marginRight = 6;
                    rewardChip.style.marginBottom = 4;
                    
                    var rewardIcon = new Label(GetRewardIcon(reward.rewardType));
                    rewardIcon.style.fontSize = 12;
                    rewardIcon.style.marginRight = 4;
                    
                    var rewardText = new Label($"{reward.quantity}");
                    rewardText.style.fontSize = 12;
                    rewardText.style.color = Color.white;
                    
                    rewardChip.Add(rewardIcon);
                    rewardChip.Add(rewardText);
                    rewardsRow.Add(rewardChip);
                }
                
                container.Add(rewardsTitle);
                container.Add(rewardsRow);
            }
            
            return container;
        }
        
        /// <summary>
        /// 🎉 Create actions section for event
        /// </summary>
        private VisualElement CreateActionsSection(GameEvent gameEvent)
        {
            var container = new VisualElement();
            container.style.flexDirection = FlexDirection.Row;
            container.style.justifyContent = Justify.SpaceBetween;
            
            var leftActions = new VisualElement();
            leftActions.style.flexDirection = FlexDirection.Row;
            
            // Start/Join button
            if (!gameEvent.hasStarted && gameEvent.IsActive())
            {
                var startButton = new Button(() => OnEventStarted?.Invoke(gameEvent));
                startButton.text = "START";
                startButton.style.paddingLeft = 16;
                startButton.style.paddingRight = 16;
                startButton.style.paddingTop = 8;
                startButton.style.paddingBottom = 8;
                startButton.style.backgroundColor = new Color(0.3f, 0.7f, 0.3f, 0.9f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
// 🔧 LEGENDARY FIX: borderWidth not available in Unity 2022.3
                startButton.style.color = Color.white;
                startButton.style.marginRight = 8;
                leftActions.Add(startButton);
            }
            
            // Claim rewards button
            if (gameEvent.isCompleted && !gameEvent.rewardsClaimed)
            {
                var claimButton = new Button(() => OnEventClaimRewards?.Invoke(gameEvent));
                claimButton.text = "CLAIM REWARDS";
                claimButton.style.paddingLeft = 16;
                claimButton.style.paddingRight = 16;
                claimButton.style.paddingTop = 8;
                claimButton.style.paddingBottom = 8;
                claimButton.style.backgroundColor = new Color(1f, 0.8f, 0f, 0.9f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
// 🔧 LEGENDARY FIX: borderWidth not available in Unity 2022.3
                claimButton.style.color = Color.black;
                claimButton.style.marginRight = 8;
                leftActions.Add(claimButton);
            }
            
            // Details button
            var detailsButton = new Button(() => OnEventDetailsRequested?.Invoke(gameEvent));
            detailsButton.text = "DETAILS";
            detailsButton.style.paddingLeft = 12;
            detailsButton.style.paddingRight = 12;
            detailsButton.style.paddingTop = 8;
            detailsButton.style.paddingBottom = 8;
            detailsButton.style.backgroundColor = new Color(0.3f, 0.5f, 0.7f, 0.9f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
// 🔧 LEGENDARY FIX: borderWidth not available in Unity 2022.3
            detailsButton.style.color = Color.white;
            
            container.Add(leftActions);
            container.Add(detailsButton);
            
            return container;
        }
        
        /// <summary>
        /// 🎉 Show empty state when no events available
        /// </summary>
        private void ShowEmptyState()
        {
            var emptyContainer = new VisualElement();
            emptyContainer.style.alignItems = Align.Center;
            emptyContainer.style.justifyContent = Justify.Center;
            emptyContainer.style.paddingTop = 60;
            emptyContainer.style.paddingBottom = 60;
            
            var emptyIcon = new Label("🎉");
            emptyIcon.style.fontSize = 40;
            emptyIcon.style.marginBottom = 16;
            
            var emptyTitle = new Label("No Events Available");
            emptyTitle.style.fontSize = 18;
            emptyTitle.style.color = Color.white;
            emptyTitle.style.unityFontStyleAndWeight = FontStyle.Bold;
            emptyTitle.style.marginBottom = 8;
            
            var emptyDesc = new Label("Check back later for new events and activities!");
            emptyDesc.style.fontSize = 14;
            emptyDesc.style.color = new Color(0.7f, 0.7f, 0.7f, 1f);
            emptyDesc.style.unityTextAlign = TextAnchor.MiddleCenter;
            
            emptyContainer.Add(emptyIcon);
            emptyContainer.Add(emptyTitle);
            emptyContainer.Add(emptyDesc);
            
            _eventsContainer.Add(emptyContainer);
        }
        
        /// <summary>
        /// 🎉 Update notification badge count
        /// </summary>
        private void UpdateNotificationBadge()
        {
            int claimableCount = GetClaimableEventsCount();
            
            if (claimableCount > 0)
            {
                _notificationBadge.style.display = DisplayStyle.Flex;
                _notificationCount.text = claimableCount.ToString();
            }
            else
            {
                _notificationBadge.style.display = DisplayStyle.None;
            }
        }
        
        /// <summary>
        /// 🎉 Update event timers display
        /// </summary>
        private void UpdateEventTimers()
        {
            foreach (var gameEvent in _filteredEvents)
            {
                var timerLabel = _eventsContainer.Q<Label>($"timer-{gameEvent.eventId}");
                if (timerLabel != null)
                {
                    UpdateEventTimer(gameEvent, timerLabel);
                }
            }
        }
        
        /// <summary>
        /// 🎉 Update individual event timer
        /// </summary>
        private void UpdateEventTimer(GameEvent gameEvent, Label timerLabel)
        {
            if (gameEvent.isCompleted)
            {
                timerLabel.text = "Completed";
                timerLabel.style.color = new Color(0.3f, 0.7f, 0.3f, 1f);
            }
            else if (gameEvent.IsExpired())
            {
                timerLabel.text = "Expired";
                timerLabel.style.color = new Color(0.7f, 0.3f, 0.3f, 1f);
            }
            else if (gameEvent.IsActive())
            {
                var timeRemaining = gameEvent.endDate - System.DateTime.Now;
                timerLabel.text = FormatTimeRemaining(timeRemaining);
                timerLabel.style.color = timeRemaining.TotalHours < 24 ? 
                    new Color(1f, 0.8f, 0f, 1f) : 
                    new Color(0.8f, 0.8f, 0.8f, 1f);
            }
            else
            {
                var timeUntilStart = gameEvent.startDate - System.DateTime.Now;
                timerLabel.text = $"Starts in {FormatTimeRemaining(timeUntilStart)}";
                timerLabel.style.color = new Color(0.7f, 0.7f, 0.7f, 1f);
            }
        }
        
        /// <summary>
        /// 🎉 Format time remaining for display
        /// </summary>
        private string FormatTimeRemaining(System.TimeSpan timeSpan)
        {
            if (timeSpan.TotalDays >= 1)
                return $"{(int)timeSpan.TotalDays}d {timeSpan.Hours}h";
            else if (timeSpan.TotalHours >= 1)
                return $"{(int)timeSpan.TotalHours}h {timeSpan.Minutes}m";
            else if (timeSpan.TotalMinutes >= 1)
                return $"{(int)timeSpan.TotalMinutes}m";
            else
                return "< 1m";
        }
        
        /// <summary>
        /// 🎉 Toggle notification settings panel
        /// </summary>
        private void ToggleNotificationPanel()
        {
            bool isVisible = _notificationPanel.style.display == DisplayStyle.Flex;
            _notificationPanel.style.display = isVisible ? DisplayStyle.None : DisplayStyle.Flex;
        }
        
        /// <summary>
        /// 🎉 Trigger platform-specific notification
        /// </summary>
        private void TriggerEventNotification(GameEvent gameEvent, string message)
        {
            // This would integrate with platform notification systems
            Debug.Log($"🎉 Event Notification: {gameEvent.eventName} - {message}");
            
            // Platform-specific implementation would go here
            #if UNITY_ANDROID && !UNITY_EDITOR
            // Android notification implementation
            #elif UNITY_IOS && !UNITY_EDITOR
            // iOS notification implementation
            #endif
        }
        
        #region Helper Methods
        
        private Color GetEventStatusColor(GameEvent gameEvent)
        {
            if (gameEvent.isCompleted && !gameEvent.rewardsClaimed)
                return new Color(1f, 0.8f, 0f, 1f); // Gold for claimable
            else if (gameEvent.isCompleted)
                return new Color(0.3f, 0.7f, 0.3f, 1f); // Green for completed
            else if (gameEvent.IsExpired())
                return new Color(0.7f, 0.3f, 0.3f, 1f); // Red for expired
            else if (gameEvent.IsActive())
                return new Color(0.3f, 0.5f, 0.9f, 1f); // Blue for active
            else
                return new Color(0.5f, 0.5f, 0.5f, 1f); // Gray for upcoming
        }
        
        private Color GetEventTypeColor(EventType eventType)
        {
            return eventType switch
            {
                EventType.Daily => new Color(0.3f, 0.7f, 0.3f, 1f),
                EventType.Seasonal => new Color(0.8f, 0.3f, 0.8f, 1f),
                EventType.LimitedTime => new Color(1f, 0.8f, 0f, 1f),
                EventType.Achievement => new Color(0.3f, 0.5f, 0.9f, 1f),
                _ => new Color(0.6f, 0.6f, 0.6f, 1f)
            };
        }
        
        private Color GetPriorityColor(EventPriority priority)
        {
            return priority switch
            {
                EventPriority.Low => new Color(0.6f, 0.6f, 0.6f, 1f),
                EventPriority.Medium => new Color(1f, 0.8f, 0f, 1f),
                EventPriority.High => new Color(1f, 0.5f, 0f, 1f),
                EventPriority.Critical => new Color(1f, 0.3f, 0.3f, 1f),
                _ => new Color(0.5f, 0.5f, 0.5f, 1f)
            };
        }
        
        private string GetRewardIcon(RewardType rewardType)
        {
            return rewardType switch
            {
                RewardType.Gold => "🪙",
                RewardType.Gems => "💎",
                RewardType.Experience => "⭐",
                RewardType.Item => "📦",
                RewardType.Hero => "👤",
                RewardType.Currency => "🎫",
                _ => "🎁"
            };
        }
        
        #endregion
        
        #region Factory Methods
        
        public new class UxmlFactory : UxmlFactory<EventsSystem, UxmlTraits> { }
        
        public new class UxmlTraits : VisualElement.UxmlTraits
        {
            public override void Init(VisualElement ve, IUxmlAttributes bag, CreationContext cc)
            {
                base.Init(ve, bag, cc);
            }
        }
        
        #endregion
    }
    
    public enum EventCategory
    {
        Active = 0,
        Daily = 1,
        Seasonal = 2,
        Achievement = 3
    }
}
#endregion
// Continue with data structures in next part due to length...
