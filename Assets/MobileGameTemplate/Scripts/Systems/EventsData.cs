using UnityEngine;
using System.Collections.Generic;

using System.Linq; // 🔧 C# 10 Compatibility
/// <summary>
/// Data structures for the events system
/// </summary>

[System.Serializable]
public class GameEvent
{
    [Header("Event Identity")]
    public string eventId = "";
    public string eventName = "Event";
    public string description = "";
    public Sprite eventIcon;
    
    [Header("Event Classification")]
    public EventType eventType = EventType.Daily;
    public EventPriority priority = EventPriority.Medium;
    public string eventCategory = "General";
    
    [Header("Event Timing")]
    public System.DateTime startDate = System.DateTime.Now;
    public System.DateTime endDate = System.DateTime.Now.AddDays(1);
    public bool hasStarted = false;
    public bool isCompleted = false;
    public System.DateTime completedDate;
    
    [Header("Event Progress")]
    public List<EventObjective> objectives = new List<EventObjective>();
    public List<EventReward> rewards = new List<EventReward>();
    public bool rewardsClaimed = false;
    
    [Header("Event Settings")]
    public int playerLevelRequired = 1;
    public bool isRepeatable = false;
    public int maxCompletions = 1;
    public int currentCompletions = 0;
    
    /// <summary>
    /// Check if event is currently active
    /// </summary>
    public bool IsActive()
    {
        var now = System.DateTime.Now;
        return now >= startDate && now <= endDate && !IsExpired();
    }
    
    /// <summary>
    /// Check if event has expired
    /// </summary>
    public bool IsExpired()
    {
        return System.DateTime.Now > endDate;
    }
    
    /// <summary>
    /// Check if all objectives are completed
    /// </summary>
    public bool AreAllObjectivesCompleted()
    {
        return objectives.Count > 0 && objectives.TrueForAll(obj => obj.isCompleted);
    }
    
    /// <summary>
    /// Get overall completion percentage
    /// </summary>
    public float GetCompletionPercentage()
    {
        if (objectives.Count == 0) return 0f;
        
        float totalProgress = 0f;
        foreach (var objective in objectives)
        {
            totalProgress += (float)objective.currentValue / objective.targetValue;
        }
        
        return Mathf.Clamp01(totalProgress / objectives.Count);
    }
    
    /// <summary>
    /// Update objective progress
    /// </summary>
    public void UpdateObjectiveProgress(string objectiveId, int newValue)
    {
        var objective = objectives.Find(obj => obj.objectiveId == objectiveId);
        if (objective != null)
        {
            objective.currentValue = newValue;
            objective.isCompleted = objective.currentValue >= objective.targetValue;
            
            // Check if event is completed
            if (AreAllObjectivesCompleted() && !isCompleted)
            {
                isCompleted = true;
                completedDate = System.DateTime.Now;
            }
        }
    }
}

[System.Serializable]
public class EventObjective
{
    [Header("Objective Identity")]
    public string objectiveId = "";
    public string description = "";
    public string shortDescription = "";
    
    [Header("Objective Progress")]
    public int currentValue = 0;
    public int targetValue = 1;
    public bool isCompleted = false;
    
    [Header("Objective Type")]
    public ObjectiveType objectiveType = ObjectiveType.Count;
    public string targetData = ""; // What to count/collect/defeat
    
    [Header("Objective Rewards")]
    public List<EventReward> objectiveRewards = new List<EventReward>();
    public bool rewardsClaimed = false;
    
    /// <summary>
    /// Get progress as percentage
    /// </summary>
    public float GetProgressPercentage()
    {
        if (targetValue == 0) return 0f;
        return Mathf.Clamp01((float)currentValue / targetValue);
    }
}

[System.Serializable]
public class EventReward
{
    [Header("Reward Identity")]
    public string rewardId = "";
    public string displayName = "";
    public string description = "";
    
    [Header("Reward Content")]
    public RewardType rewardType = RewardType.Gold;
    public int quantity = 1;
    public string itemId = ""; // For item rewards
    public ItemRarity itemRarity = ItemRarity.Common;
    
    [Header("Reward Constraints")]
    public bool isGuaranteed = true;
    public float dropChance = 1.0f; // 0.0 to 1.0
    public int maxClaims = 1;
    public int currentClaims = 0;
}

[System.Serializable]
public class NotificationSettings
{
    [Header("Event Notifications")]
    public bool enableEventNotifications = true;
    public bool enableRewardNotifications = true;
    public bool enableDailyReminders = true;
    public bool enableSeasonalAlerts = true;
    
    [Header("Notification Timing")]
    public int dailyReminderHour = 18; // 6 PM
    public int eventStartReminderMinutes = 30;
    public bool enableSoundEffects = true;
    public bool enableVibration = true;
    
    [Header("Notification Filters")]
    public List<EventType> enabledEventTypes = new List<EventType>();
    public EventPriority minimumPriority = EventPriority.Low;
    public bool onlyShowClaimableRewards = false;
}

[System.Serializable]
public class EventSchedule
{
    [Header("Schedule Identity")]
    public string scheduleId = "";
    public string scheduleName = "";
    
    [Header("Schedule Configuration")]
    public List<ScheduledEvent> scheduledEvents = new List<ScheduledEvent>();
    public bool isActive = true;
    public System.DateTime scheduleStartDate = System.DateTime.Now;
    public System.DateTime scheduleEndDate = System.DateTime.MaxValue;
}

[System.Serializable]
public class ScheduledEvent
{
    [Header("Scheduled Event")]
    public string eventTemplateId = "";
    public System.DateTime scheduledStart = System.DateTime.Now;
    public System.TimeSpan duration = System.TimeSpan.FromDays(1);
    
    [Header("Repeat Settings")]
    public bool isRepeating = false;
    public RepeatType repeatType = RepeatType.None;
    public int repeatInterval = 1; // Days/weeks/months
    public int maxRepeats = -1; // -1 for infinite
    public int currentRepeats = 0;
}

public enum EventType
{
    Daily = 0,
    Weekly = 1,
    Seasonal = 2,
    LimitedTime = 3,
    Achievement = 4,
    Special = 5
}

public enum EventPriority
{
    Low = 0,
    Medium = 1,
    High = 2,
    Critical = 3
}

public enum ObjectiveType
{
    Count = 0,        // Count actions (kill 10 enemies)
    Collect = 1,      // Collect items
    Reach = 2,        // Reach a value (level, score)
    Survive = 3,      // Survive for time
    Complete = 4,     // Complete specific content
    Use = 5,          // Use items/abilities
    Win = 6,          // Win matches/battles
    Social = 7        // Social objectives (guild, friends)
}

public enum RewardType
{
    Gold = 0,
    Gems = 1,
    Experience = 2,
    Item = 3,
    Hero = 4,
    Currency = 5,
    Cosmetic = 6,
    Unlock = 7
}

public enum RepeatType
{
    None = 0,
    Daily = 1,
    Weekly = 2,
    Monthly = 3,
    Custom = 4
}

/// <summary>
/// Event manager for handling event lifecycle and notifications
/// </summary>
public class EventManager : MonoBehaviour
{
    [Header("Event Configuration")]
    [SerializeField] private List<GameEvent> _activeEvents = new List<GameEvent>();
    [SerializeField] private NotificationSettings _notificationSettings = new NotificationSettings();
    [SerializeField] private EventSchedule _eventSchedule = new EventSchedule();
    
    [Header("Event Prefabs")]
    [SerializeField] private GameObject _eventNotificationPrefab;
    [SerializeField] private AudioClip _eventStartSound;
    [SerializeField] private AudioClip _rewardClaimSound;
    
    // Events
    public System.Action<GameEvent> OnEventStarted;
    public System.Action<GameEvent> OnEventCompleted;
    public System.Action<GameEvent> OnEventExpired;
    public System.Action<GameEvent, EventReward> OnRewardClaimed;
    
    private void Start()
    {
        InitializeEventSystem();
        StartCoroutine(EventUpdateLoop());
    }
    
    /// <summary>
    /// Initialize event system with saved data
    /// </summary>
    private void InitializeEventSystem()
    {
        // Load saved events from persistent storage
        LoadEventsFromStorage();
        
        // Initialize notification settings
        LoadNotificationSettings();
        
        // Check for expired events and start new ones
        ProcessEventSchedule();
    }
    
    /// <summary>
    /// Main event update loop
    /// </summary>
    private System.Collections.IEnumerator EventUpdateLoop()
    {
        while (true)
        {
            yield return new WaitForSeconds(60f); // Update every minute
            
            foreach (var gameEvent in _activeEvents.ToArray())
            {
                UpdateEventProgress(gameEvent);
                CheckEventCompletion(gameEvent);
                CheckEventExpiration(gameEvent);
            }
            
            ProcessEventSchedule();
        }
    }
    
    /// <summary>
    /// Update event progress based on game state
    /// </summary>
    private void UpdateEventProgress(GameEvent gameEvent)
    {
        // This would be implemented based on specific game mechanics
        // Examples:
        // - Check player stats for kill counts
        // - Check inventory for collected items
        // - Check player level for progression objectives
        
        foreach (var objective in gameEvent.objectives)
        {
            if (!objective.isCompleted)
            {
                // Update objective based on type
                UpdateObjectiveProgress(gameEvent, objective);
            }
        }
    }
    
    /// <summary>
    /// Update specific objective progress
    /// </summary>
    private void UpdateObjectiveProgress(GameEvent gameEvent, EventObjective objective)
    {
        switch (objective.objectiveType)
        {
            case ObjectiveType.Count:
                // Example: Count player kills, level ups, etc.
                break;
            case ObjectiveType.Collect:
                // Example: Check inventory for specific items
                break;
            case ObjectiveType.Reach:
                // Example: Check player level, score, etc.
                break;
            case ObjectiveType.Survive:
                // Example: Check survival time in game modes
                break;
            case ObjectiveType.Complete:
                // Example: Check if specific levels/quests are completed
                break;
            case ObjectiveType.Use:
                // Example: Track item/ability usage
                break;
            case ObjectiveType.Win:
                // Example: Track battle/match wins
                break;
            case ObjectiveType.Social:
                // Example: Check guild membership, friend invites
                break;
        }
    }
    
    /// <summary>
    /// Check if event is completed
    /// </summary>
    private void CheckEventCompletion(GameEvent gameEvent)
    {
        if (!gameEvent.isCompleted && gameEvent.AreAllObjectivesCompleted())
        {
            gameEvent.isCompleted = true;
            gameEvent.completedDate = System.DateTime.Now;
            OnEventCompleted?.Invoke(gameEvent);
            
            if (_notificationSettings.enableRewardNotifications)
            {
                ShowEventNotification(gameEvent, "Event completed! Claim your rewards!");
            }
        }
    }
    
    /// <summary>
    /// Check if event has expired
    /// </summary>
    private void CheckEventExpiration(GameEvent gameEvent)
    {
        if (gameEvent.IsExpired() && !gameEvent.isCompleted)
        {
            OnEventExpired?.Invoke(gameEvent);
            _activeEvents.Remove(gameEvent);
        }
    }
    
    /// <summary>
    /// Process scheduled events
    /// </summary>
    private void ProcessEventSchedule()
    {
        if (!_eventSchedule.isActive) return;
        
        var currentTime = System.DateTime.Now;
        
        foreach (var scheduledEvent in _eventSchedule.scheduledEvents)
        {
            if (ShouldStartScheduledEvent(scheduledEvent, currentTime))
            {
                StartScheduledEvent(scheduledEvent);
            }
        }
    }
    
    /// <summary>
    /// Check if scheduled event should start
    /// </summary>
    private bool ShouldStartScheduledEvent(ScheduledEvent scheduledEvent, System.DateTime currentTime)
    {
        // Check if it's time to start the event
        if (currentTime >= scheduledEvent.scheduledStart)
        {
            // Check if event is already active
            bool isAlreadyActive = _activeEvents.Any(e => e.eventId == scheduledEvent.eventTemplateId);
            
            if (!isAlreadyActive)
            {
                return true;
            }
        }
        
        return false;
    }
    
    /// <summary>
    /// Start a scheduled event
    /// </summary>
    private void StartScheduledEvent(ScheduledEvent scheduledEvent)
    {
        // Create event from template
        var newEvent = CreateEventFromTemplate(scheduledEvent.eventTemplateId);
        if (newEvent != null)
        {
            newEvent.startDate = scheduledEvent.scheduledStart;
            newEvent.endDate = scheduledEvent.scheduledStart + scheduledEvent.duration;
            
            _activeEvents.Add(newEvent);
            OnEventStarted?.Invoke(newEvent);
            
            if (_notificationSettings.enableEventNotifications)
            {
                ShowEventNotification(newEvent, "New event started!");
            }
            
            // Update repeat schedule if applicable
            if (scheduledEvent.isRepeating)
            {
                UpdateRepeatSchedule(scheduledEvent);
            }
        }
    }
    
    /// <summary>
    /// Create event from template
    /// </summary>
    private GameEvent CreateEventFromTemplate(string templateId)
    {
        // This would load event templates from resources
        // For now, return a basic event
        return new GameEvent
        {
            eventId = System.Guid.NewGuid().ToString(),
            eventName = "Daily Quest",
            description = "Complete daily objectives",
            eventType = EventType.Daily,
            priority = EventPriority.Medium
        };
    }
    
    /// <summary>
    /// Update repeat schedule for repeating events
    /// </summary>
    private void UpdateRepeatSchedule(ScheduledEvent scheduledEvent)
    {
        if (scheduledEvent.maxRepeats > 0 && scheduledEvent.currentRepeats >= scheduledEvent.maxRepeats)
        {
            return; // Max repeats reached
        }
        
        System.TimeSpan interval = scheduledEvent.repeatType switch
        {
            RepeatType.Daily => System.TimeSpan.FromDays(scheduledEvent.repeatInterval),
            RepeatType.Weekly => System.TimeSpan.FromDays(7 * scheduledEvent.repeatInterval),
            RepeatType.Monthly => System.TimeSpan.FromDays(30 * scheduledEvent.repeatInterval),
            _ => System.TimeSpan.FromDays(scheduledEvent.repeatInterval)
        };
        
        scheduledEvent.scheduledStart += interval;
        scheduledEvent.currentRepeats++;
    }
    
    /// <summary>
    /// Show event notification
    /// </summary>
    private void ShowEventNotification(GameEvent gameEvent, string message)
    {
        // Platform-specific notification implementation
        Debug.Log($"🎉 Event Notification: {gameEvent.eventName} - {message}");
        
        // Play sound if enabled
        if (_notificationSettings.enableSoundEffects && _eventStartSound != null)
        {
            AudioSource.PlayClipAtPoint(_eventStartSound, Camera.main.transform.position);
        }
        
        // Trigger haptic feedback if enabled
        if (_notificationSettings.enableVibration)
        {
            #if UNITY_ANDROID && !UNITY_EDITOR
            // Android haptic feedback
            #elif UNITY_IOS && !UNITY_EDITOR
            // iOS haptic feedback
            #endif
        }
    }
    
    /// <summary>
    /// Claim event rewards
    /// </summary>
    public void ClaimEventRewards(GameEvent gameEvent)
    {
        if (!gameEvent.isCompleted || gameEvent.rewardsClaimed)
            return;
        
        foreach (var reward in gameEvent.rewards)
        {
            if (UnityEngine.Random.value <= reward.dropChance)
            {
                GrantReward(reward);
                OnRewardClaimed?.Invoke(gameEvent, reward);
            }
        }
        
        gameEvent.rewardsClaimed = true;
        
        if (_notificationSettings.enableSoundEffects && _rewardClaimSound != null)
        {
            AudioSource.PlayClipAtPoint(_rewardClaimSound, Camera.main.transform.position);
        }
    }
    
    /// <summary>
    /// Grant reward to player
    /// </summary>
    private void GrantReward(EventReward reward)
    {
        switch (reward.rewardType)
        {
            case RewardType.Gold:
                // Add gold to player currency
                break;
            case RewardType.Gems:
                // Add gems to player currency
                break;
            case RewardType.Experience:
                // Add experience to player
                break;
            case RewardType.Item:
                // Add item to player inventory
                break;
            case RewardType.Hero:
                // Add hero to player collection
                break;
            case RewardType.Currency:
                // Add special currency
                break;
        }
    }
    
    #region Data Persistence
    
    private void LoadEventsFromStorage()
    {
        // Load events from PlayerPrefs, file system, or cloud storage
        string eventsJson = PlayerPrefs.GetString("ActiveEvents", "[]");
        try
        {
            var eventsList = JsonUtility.FromJson<SerializableEventsList>(eventsJson);
            _activeEvents = eventsList?.events ?? new List<GameEvent>();
        }
        catch
        {
            _activeEvents = new List<GameEvent>();
        }
    }
    
    private void SaveEventsToStorage()
    {
        var eventsList = new SerializableEventsList { events = _activeEvents };
        string eventsJson = JsonUtility.ToJson(eventsList);
        PlayerPrefs.SetString("ActiveEvents", eventsJson);
    }
    
    private void LoadNotificationSettings()
    {
        string settingsJson = PlayerPrefs.GetString("NotificationSettings", "");
        if (!string.IsNullOrEmpty(settingsJson))
        {
            try
            {
                _notificationSettings = JsonUtility.FromJson<NotificationSettings>(settingsJson);
            }
            catch
            {
                _notificationSettings = new NotificationSettings();
            }
        }
    }
    
    private void SaveNotificationSettings()
    {
        string settingsJson = JsonUtility.ToJson(_notificationSettings);
        PlayerPrefs.SetString("NotificationSettings", settingsJson);
    }
    
    private void OnApplicationPause(bool pauseStatus)
    {
        if (pauseStatus)
        {
            SaveEventsToStorage();
            SaveNotificationSettings();
        }
    }
    
    #endregion
}

[System.Serializable]
public class SerializableEventsList
{
    public List<GameEvent> events = new List<GameEvent>();
}