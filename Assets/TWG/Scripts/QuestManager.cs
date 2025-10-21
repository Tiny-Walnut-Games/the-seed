using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace TWG.TLDA
{
    /// <summary>
    /// ??? PROTECTED CORE - Complete quest management system
    /// Provides full quest functionality for customer game projects
    /// </summary>
    public class QuestManager : MonoBehaviour
    {
        public static QuestManager Instance { get; private set; }

        [Header("Quest Configuration")]
        [SerializeField] private List<Quest> availableQuests = new List<Quest>();
        [SerializeField] private List<Quest> activeQuests = new List<Quest>();
        [SerializeField] private List<Quest> completedQuests = new List<Quest>();
        [SerializeField] private int maxActiveQuests = 10;

        // Events
        public event Action<Quest> OnQuestStarted = delegate { };
        public event Action<Quest> OnQuestCompleted = delegate { };
        public event Action<Quest> OnQuestFailed = delegate { };
        public event Action<Quest, QuestObjective> OnObjectiveCompleted = delegate { };

        void Awake()
        {
            // Singleton pattern
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeQuestSystem();
            }
            else
            {
                Destroy(gameObject);
            }
        }

        private void InitializeQuestSystem()
        {
            // Initialize with some default quests if none are configured
            if (availableQuests.Count == 0)
            {
                CreateDefaultQuests();
            }

            Debug.Log($"QuestManager initialized with {availableQuests.Count} available quests");
        }

        private void CreateDefaultQuests()
        {
            // Tutorial quest
            var tutorialQuest = new Quest
            {
                questId = "tutorial_001",
                title = "Getting Started",
                description = "Learn the basics of the game",
                questType = QuestType.Main,
                experienceReward = 50,
                objectives = new List<QuestObjective>
                {
                    new QuestObjective
                    {
                        objectiveId = "move_around",
                        description = "Move your character",
                        objectiveType = ObjectiveType.Action,
                        targetValue = 1,
                        isCompleted = false
                    }
                }
            };
            availableQuests.Add(tutorialQuest);

            // Exploration quest
            var explorationQuest = new Quest
            {
                questId = "explore_001",
                title = "Explore the World",
                description = "Visit different locations",
                questType = QuestType.Side,
                experienceReward = 100,
                objectives = new List<QuestObjective>
                {
                    new QuestObjective
                    {
                        objectiveId = "visit_locations",
                        description = "Visit 3 different locations",
                        objectiveType = ObjectiveType.Collection,
                        targetValue = 3,
                        currentValue = 0,
                        isCompleted = false
                    }
                }
            };
            availableQuests.Add(explorationQuest);
        }

        /// <summary>
        /// Start a quest by ID
        /// </summary>
        public bool StartQuest(string questId)
        {
            if (activeQuests.Count >= maxActiveQuests)
            {
                Debug.LogWarning("Cannot start quest - maximum active quests reached");
                return false;
            }

            var quest = availableQuests.FirstOrDefault(q => q.questId == questId);
            if (quest == null)
            {
                Debug.LogWarning($"Quest not found: {questId}");
                return false;
            }

            if (activeQuests.Any(q => q.questId == questId))
            {
                Debug.LogWarning($"Quest already active: {questId}");
                return false;
            }

            // Create a copy for the active quest to avoid modifying the template
            var activeQuest = quest.CreateCopy();
            activeQuest.startTime = DateTime.Now;
            activeQuest.status = QuestStatus.Active;

            activeQuests.Add(activeQuest);
            OnQuestStarted?.Invoke(activeQuest);

            Debug.Log($"Quest started: {activeQuest.title}");
            return true;
        }

        /// <summary>
        /// Complete a quest objective
        /// </summary>
        public void CompleteObjective(string questId, string objectiveId)
        {
            var quest = activeQuests.FirstOrDefault(q => q.questId == questId);
            if (quest == null) return;

            var objective = quest.objectives.FirstOrDefault(o => o.objectiveId == objectiveId);
            if (objective == null) return;

            if (!objective.isCompleted)
            {
                objective.isCompleted = true;
                objective.completionTime = DateTime.Now;
                OnObjectiveCompleted?.Invoke(quest, objective);

                Debug.Log($"Objective completed: {objective.description}");

                // Check if quest is complete
                if (quest.objectives.All(o => o.isCompleted))
                {
                    CompleteQuest(questId);
                }
            }
        }

        /// <summary>
        /// Update objective progress (for collection/kill count objectives)
        /// </summary>
        public void UpdateObjectiveProgress(string questId, string objectiveId, int amount = 1)
        {
            var quest = activeQuests.FirstOrDefault(q => q.questId == questId);
            if (quest == null) return;

            var objective = quest.objectives.FirstOrDefault(o => o.objectiveId == objectiveId);
            if (objective == null || objective.isCompleted) return;

            objective.currentValue += amount;

            if (objective.currentValue >= objective.targetValue)
            {
                CompleteObjective(questId, objectiveId);
            }
            else
            {
                Debug.Log($"Objective progress: {objective.description} ({objective.currentValue}/{objective.targetValue})");
            }
        }

        /// <summary>
        /// Complete a quest
        /// </summary>
        public void CompleteQuest(string questId)
        {
            var quest = activeQuests.FirstOrDefault(q => q.questId == questId);
            if (quest == null) return;

            quest.status = QuestStatus.Completed;
            quest.completionTime = DateTime.Now;

            activeQuests.Remove(quest);
            completedQuests.Add(quest);

            // Give rewards
            if (quest.experienceReward > 0 && GameManager.Instance != null)
            {
                GameManager.Instance.AddExperience(quest.experienceReward);
            }

            OnQuestCompleted?.Invoke(quest);
            Debug.Log($"Quest completed: {quest.title} (XP: {quest.experienceReward})");
        }

        /// <summary>
        /// Fail a quest
        /// </summary>
        public void FailQuest(string questId)
        {
            var quest = activeQuests.FirstOrDefault(q => q.questId == questId);
            if (quest == null) return;

            quest.status = QuestStatus.Failed;
            quest.completionTime = DateTime.Now;

            activeQuests.Remove(quest);
            OnQuestFailed?.Invoke(quest);

            Debug.Log($"Quest failed: {quest.title}");
        }

        /// <summary>
        /// Get active quest information for Warbler integration
        /// </summary>
        public List<string> GetActiveQuests()
        {
            return activeQuests.Select(q => $"{q.title}: {q.GetProgressSummary()}").ToList();
        }

        /// <summary>
        /// Get quest by ID from any list
        /// </summary>
        public Quest GetQuest(string questId)
        {
            return activeQuests.FirstOrDefault(q => q.questId == questId) ??
                   completedQuests.FirstOrDefault(q => q.questId == questId) ??
                   availableQuests.FirstOrDefault(q => q.questId == questId);
        }

        /// <summary>
        /// Check if a quest is available to start
        /// </summary>
        public bool IsQuestAvailable(string questId)
        {
            return availableQuests.Any(q => q.questId == questId) &&
                   !activeQuests.Any(q => q.questId == questId) &&
                   !completedQuests.Any(q => q.questId == questId);
        }

        /// <summary>
        /// Get quests by type
        /// </summary>
        public List<Quest> GetQuestsByType(QuestType questType)
        {
            return activeQuests.Where(q => q.questType == questType).ToList();
        }

        /// <summary>
        /// Add a new quest template
        /// </summary>
        public void AddQuestTemplate(Quest questTemplate)
        {
            if (!availableQuests.Any(q => q.questId == questTemplate.questId))
            {
                availableQuests.Add(questTemplate);
                Debug.Log($"Quest template added: {questTemplate.title}");
            }
        }

        /// <summary>
        /// Save quest progress
        /// </summary>
        public void SaveQuestProgress()
        {
            var saveData = new QuestSaveData
            {
                activeQuestIds = activeQuests.Select(q => q.questId).ToList(),
                completedQuestIds = completedQuests.Select(q => q.questId).ToList(),
                questObjectiveStates = new Dictionary<string, Dictionary<string, ObjectiveSaveData>>()
            };

            // Save objective states for active quests
            foreach (var quest in activeQuests)
            {
                saveData.questObjectiveStates[quest.questId] = new Dictionary<string, ObjectiveSaveData>();
                foreach (var objective in quest.objectives)
                {
                    saveData.questObjectiveStates[quest.questId][objective.objectiveId] = new ObjectiveSaveData
                    {
                        currentValue = objective.currentValue,
                        isCompleted = objective.isCompleted
                    };
                }
            }

            var json = JsonUtility.ToJson(saveData);
            PlayerPrefs.SetString("QuestProgress", json);
            PlayerPrefs.Save();

            Debug.Log("Quest progress saved");
        }

        /// <summary>
        /// Load quest progress
        /// </summary>
        public void LoadQuestProgress()
        {
            if (!PlayerPrefs.HasKey("QuestProgress")) return;

            try
            {
                var json = PlayerPrefs.GetString("QuestProgress");
                var saveData = JsonUtility.FromJson<QuestSaveData>(json);

                // Restore active quests
                foreach (var questId in saveData.activeQuestIds)
                {
                    if (StartQuest(questId))
                    {
                        var quest = activeQuests.First(q => q.questId == questId);

                        // Restore objective states
                        if (saveData.questObjectiveStates.ContainsKey(questId))
                        {
                            foreach (var objectiveState in saveData.questObjectiveStates[questId])
                            {
                                var objective = quest.objectives.FirstOrDefault(o => o.objectiveId == objectiveState.Key);
                                if (objective != null)
                                {
                                    objective.currentValue = objectiveState.Value.currentValue;
                                    objective.isCompleted = objectiveState.Value.isCompleted;
                                }
                            }
                        }
                    }
                }

                // Restore completed quests
                foreach (var questId in saveData.completedQuestIds)
                {
                    var questTemplate = availableQuests.FirstOrDefault(q => q.questId == questId);
                    if (questTemplate != null)
                    {
                        var completedQuest = questTemplate.CreateCopy();
                        completedQuest.status = QuestStatus.Completed;
                        completedQuests.Add(completedQuest);
                    }
                }

                Debug.Log("Quest progress loaded");
            }
            catch (Exception e)
            {
                Debug.LogError($"Failed to load quest progress: {e.Message}");
            }
        }
    }

    [Serializable]
    public class Quest
    {
        public string questId = "";
        public string title = "";
        public string description = "";
        public QuestType questType;
        public QuestStatus status;
        public List<QuestObjective> objectives = new List<QuestObjective>();
        public int experienceReward;
        public DateTime startTime;
        public DateTime completionTime;

        public Quest CreateCopy()
        {
            var copy = new Quest
            {
                questId = this.questId,
                title = this.title,
                description = this.description,
                questType = this.questType,
                status = QuestStatus.Available,
                experienceReward = this.experienceReward,
                objectives = new List<QuestObjective>()
            };

            foreach (var objective in this.objectives)
            {
                copy.objectives.Add(objective.CreateCopy());
            }

            return copy;
        }

        public string GetProgressSummary()
        {
            var completedObjectives = objectives.Count(o => o.isCompleted);
            return $"{completedObjectives}/{objectives.Count} objectives";
        }
    }

    [Serializable]
    public class QuestObjective
    {
        public string objectiveId = "";
        public string description = "";
        public ObjectiveType objectiveType;
        public int targetValue = 1;
        public int currentValue = 0;
        public bool isCompleted = false;
        public DateTime completionTime;

        public QuestObjective CreateCopy()
        {
            return new QuestObjective
            {
                objectiveId = this.objectiveId,
                description = this.description,
                objectiveType = this.objectiveType,
                targetValue = this.targetValue,
                currentValue = 0,
                isCompleted = false
            };
        }
    }

    public enum QuestType
    {
        Main,
        Side,
        Daily,
        Achievement
    }

    public enum QuestStatus
    {
        Available,
        Active,
        Completed,
        Failed
    }

    public enum ObjectiveType
    {
        Action,        // Single action (talk to NPC, enter area)
        Collection,    // Collect X items
        Kill,          // Kill X enemies
        Delivery,      // Deliver item to NPC
        Exploration    // Visit X locations
    }

    [Serializable]
    public class QuestSaveData
    {
        public List<string> activeQuestIds = new List<string>();
        public List<string> completedQuestIds = new List<string>();
        public Dictionary<string, Dictionary<string, ObjectiveSaveData>> questObjectiveStates = new Dictionary<string, Dictionary<string, ObjectiveSaveData>>();
    }

    [Serializable]
    public class ObjectiveSaveData
    {
        public int currentValue;
        public bool isCompleted;
    }
}
