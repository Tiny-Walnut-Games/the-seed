using System;
using System.Collections.Generic;
using UnityEngine;

namespace TWG.TLDA
{
    /// <summary>
    /// ??? PROTECTED CORE - Essential game management singleton
    /// Provides core game state management for customer projects
    /// </summary>
    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        [Header("Player Progress")]
        [SerializeField] private int playerLevel = 1;
        [SerializeField] private int playerExperience = 0;
        [SerializeField] private int experienceToNextLevel = 100;

        [Header("Game State")]
        [SerializeField] private GameState currentGameState = GameState.MainMenu;
        [SerializeField] private TimeOfDay currentTimeOfDay = TimeOfDay.Morning;
        [SerializeField] private float gameTime = 0f;
        [SerializeField] private float dayDuration = 300f; // 5 minutes per day

        [Header("Scene Management")]
        [SerializeField] private string currentSceneName = "";
        [SerializeField] private Vector3 lastPlayerPosition = Vector3.zero;

        // Properties for external access
        public int PlayerLevel => playerLevel;
        public int PlayerExperience => playerExperience;
        public GameState CurrentGameState => currentGameState;
        public TimeOfDay CurrentTimeOfDay => currentTimeOfDay;
        public float GameTime => gameTime;
        public string CurrentSceneName => currentSceneName;
        public Vector3 LastPlayerPosition => lastPlayerPosition;

        // Events
        public event Action<int> OnPlayerLevelChanged = delegate { };
        public event Action<GameState, GameState> OnGameStateChanged = delegate { };
        public event Action<TimeOfDay> OnTimeOfDayChanged = delegate { };
        public event Action<string> OnSceneChanged = delegate { };

        private Dictionary<string, object> gameData = new Dictionary<string, object>();
        private List<string> gameFlags = new List<string>();

        public enum GameState
        {
            MainMenu,
            Playing,
            Paused,
            Inventory,
            Dialogue,
            Combat,
            GameOver
        }

        public enum TimeOfDay
        {
            Morning,
            Afternoon,
            Evening,
            Night
        }

        void Awake()
        {
            // Singleton pattern
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeGame();
            }
            else
            {
                Destroy(gameObject);
            }
        }

        void Update()
        {
            UpdateGameTime();
        }

        private void InitializeGame()
        {
            // Initialize core game systems
            currentSceneName = UnityEngine.SceneManagement.SceneManager.GetActiveScene().name;

            // Set up default game data
            gameData["initialized"] = true;
            gameData["startTime"] = DateTime.Now;
            gameData["version"] = Application.version;

            Debug.Log($"GameManager initialized - Scene: {currentSceneName}, Level: {playerLevel}");
        }

        private void UpdateGameTime()
        {
            if (currentGameState == GameState.Playing)
            {
                gameTime += Time.deltaTime;

                // Update time of day
                var dayProgress = (gameTime % dayDuration) / dayDuration;
                var newTimeOfDay = GetTimeOfDayFromProgress(dayProgress);

                if (newTimeOfDay != currentTimeOfDay)
                {
                    currentTimeOfDay = newTimeOfDay;
                    OnTimeOfDayChanged?.Invoke(currentTimeOfDay);
                }
            }
        }

        private TimeOfDay GetTimeOfDayFromProgress(float progress)
        {
            if (progress < 0.25f) return TimeOfDay.Morning;
            if (progress < 0.5f) return TimeOfDay.Afternoon;
            if (progress < 0.75f) return TimeOfDay.Evening;
            return TimeOfDay.Night;
        }

        /// <summary>
        /// Change game state with event notification
        /// </summary>
        public void SetGameState(GameState newState)
        {
            if (newState != currentGameState)
            {
                var previousState = currentGameState;
                currentGameState = newState;
                OnGameStateChanged?.Invoke(previousState, newState);

                Debug.Log($"Game state changed: {previousState} -> {newState}");
            }
        }

        /// <summary>
        /// Add experience and handle level progression
        /// </summary>
        public void AddExperience(int amount)
        {
            playerExperience += amount;

            while (playerExperience >= experienceToNextLevel)
            {
                LevelUp();
            }
        }

        private void LevelUp()
        {
            playerExperience -= experienceToNextLevel;
            playerLevel++;
            experienceToNextLevel = Mathf.RoundToInt(experienceToNextLevel * 1.2f); // 20% increase per level

            OnPlayerLevelChanged?.Invoke(playerLevel);
            Debug.Log($"Player leveled up! New level: {playerLevel}");
        }

        /// <summary>
        /// Store arbitrary game data
        /// </summary>
        public void SetGameData(string key, object value)
        {
            gameData[key] = value;
        }

        /// <summary>
        /// Retrieve game data
        /// </summary>
        public T GetGameData<T>(string key, T defaultValue = default!)
        {
            if (gameData.ContainsKey(key))
            {
                try
                {
                    return (T)gameData[key];
                }
                catch
                {
                    return defaultValue;
                }
            }
            return defaultValue;
        }

        /// <summary>
        /// Set a game flag
        /// </summary>
        public void SetFlag(string flagName)
        {
            if (!gameFlags.Contains(flagName))
            {
                gameFlags.Add(flagName);
                Debug.Log($"Game flag set: {flagName}");
            }
        }

        /// <summary>
        /// Check if a game flag is set
        /// </summary>
        public bool HasFlag(string flagName)
        {
            return gameFlags.Contains(flagName);
        }

        /// <summary>
        /// Remove a game flag
        /// </summary>
        public void ClearFlag(string flagName)
        {
            if (gameFlags.Remove(flagName))
            {
                Debug.Log($"Game flag cleared: {flagName}");
            }
        }

        /// <summary>
        /// Update player position for save/load functionality
        /// </summary>
        public void UpdatePlayerPosition(Vector3 position)
        {
            lastPlayerPosition = position;
        }

        /// <summary>
        /// Get current world state for Warbler integration
        /// </summary>
        public Dictionary<string, object> GetWorldState()
        {
            return new Dictionary<string, object>
            {
                {"playerLevel", playerLevel},
                {"timeOfDay", currentTimeOfDay.ToString()},
                {"gameState", currentGameState.ToString()},
                {"gameTime", gameTime},
                {"sceneName", currentSceneName},
                {"playerPosition", lastPlayerPosition.ToString()},
                {"flags", new List<string>(gameFlags)}
            };
        }

        /// <summary>
        /// Scene change notification
        /// </summary>
        public void OnSceneLoaded(string sceneName)
        {
            currentSceneName = sceneName;
            OnSceneChanged?.Invoke(sceneName);
            Debug.Log($"Scene loaded: {sceneName}");
        }

        /// <summary>
        /// Pause/unpause game
        /// </summary>
        public void SetPaused(bool paused)
        {
            if (paused && currentGameState == GameState.Playing)
            {
                SetGameState(GameState.Paused);
                Time.timeScale = 0f;
            }
            else if (!paused && currentGameState == GameState.Paused)
            {
                SetGameState(GameState.Playing);
                Time.timeScale = 1f;
            }
        }

        /// <summary>
        /// Save game state to PlayerPrefs (basic implementation)
        /// </summary>
        public void SaveGame()
        {
            PlayerPrefs.SetInt("PlayerLevel", playerLevel);
            PlayerPrefs.SetInt("PlayerExperience", playerExperience);
            PlayerPrefs.SetFloat("GameTime", gameTime);
            PlayerPrefs.SetString("CurrentScene", currentSceneName);
            PlayerPrefs.SetString("PlayerPosition", JsonUtility.ToJson(lastPlayerPosition));
            PlayerPrefs.SetString("GameFlags", string.Join(",", gameFlags));

            PlayerPrefs.Save();
            Debug.Log("Game saved");
        }

        /// <summary>
        /// Load game state from PlayerPrefs
        /// </summary>
        public void LoadGame()
        {
            if (PlayerPrefs.HasKey("PlayerLevel"))
            {
                playerLevel = PlayerPrefs.GetInt("PlayerLevel", 1);
                playerExperience = PlayerPrefs.GetInt("PlayerExperience", 0);
                gameTime = PlayerPrefs.GetFloat("GameTime", 0f);
                currentSceneName = PlayerPrefs.GetString("CurrentScene", "");

                var positionJson = PlayerPrefs.GetString("PlayerPosition", "");
                if (!string.IsNullOrEmpty(positionJson))
                {
                    lastPlayerPosition = JsonUtility.FromJson<Vector3>(positionJson);
                }

                var flagsString = PlayerPrefs.GetString("GameFlags", "");
                if (!string.IsNullOrEmpty(flagsString))
                {
                    gameFlags = new List<string>(flagsString.Split(','));
                }

                Debug.Log("Game loaded");
            }
        }
    }
}
