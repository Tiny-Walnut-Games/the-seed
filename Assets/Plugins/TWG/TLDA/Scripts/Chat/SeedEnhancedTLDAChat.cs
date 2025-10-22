using System;
using UnityEngine;
using UnityEngine.UIElements;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Linq;
using TWG.Seed.Integration;
using TWG.Seed.Platform;
using UnityEngine.Serialization;

namespace TWG.TLDA.Chat
{
    /// <summary>
    /// Seed-enhanced TLDA chat interface with STAT7 addressing and Fractal-Chain integration
    /// Bridges conversations to spatial narrative entities and cross-platform data
    /// </summary>
    public class SeedEnhancedTldaChat : MonoBehaviour
    {
        [Header("Seed Integration")]
        [SerializeField] private SeedMindCastleBridge seedBridge;
        [SerializeField] private IPlatformBridge _platformBridge;
        // [SerializeField] private bool enableSpatialSearch = true;  // Reserved for 👀future expansion
        [SerializeField] private bool autoRegisterNarratives = true;
        [SerializeField] private bool enableCrossPlatformSync = true;

        [Header("Chat Configuration")]
        [SerializeField] private UIDocument chatUIDocument;
        // [SerializeField] private bool connectToWarbler = true;  // Reserved for 👀future expansion
        [FormerlySerializedAs("enableTLDLLogging")] [SerializeField] private bool enableTldlLogging = true;

        [Header("Visual Features")]
        [SerializeField] private bool highlightStat7Addresses = true;
        [SerializeField] private bool showRelatedEntities = true;
        [SerializeField] private bool enableNarrativeVisualization = true;

        private ScrollView _chatScrollView;
        private TextField _messageInput;
        private Button _sendButton;
        private Button _searchButton;
        private TextField _searchInput;
        private VisualElement _typingIndicator;
        private VisualElement _spatialResultsPanel;

        private List<SeedChatMessage> _messageHistory = new List<SeedChatMessage>();
        private WarblerChatBridge _warblerBridge;
        private string _currentSessionId;
        private string _userStat7Address;

        public class SeedChatMessage
        {
            public string Sender = string.Empty;
            public string Content = string.Empty;
            public System.DateTime Timestamp;
            public SeedChatMessageType Type;
            public string Stat7Address = string.Empty;
            public List<string> RelatedEntities = new List<string>();
            public Dictionary<string, object> Metadata = new Dictionary<string, object>();
            public Platform? SourcePlatform;
        }

        public enum SeedChatMessageType
        {
            User,
            Warbler,
            System,
            Code,
            Tldl,
            SeedEntity,
            SpatialSearch,
            PlatformEvent,
            NarrativeCompanion
        }

        void Start()
        {
            _currentSessionId = System.Guid.NewGuid().ToString();
            InitializeChatUI();
            SetupWarblerConnection();
            InitializeSeedIntegration();
            SetupPlatformIntegration();
        }

        void InitializeChatUI()
        {
            var root = chatUIDocument.rootVisualElement;

            _chatScrollView = root.Q<ScrollView>("chat-messages");
            _messageInput = root.Q<TextField>("message-input");
            _sendButton = root.Q<Button>("send-button");
            _typingIndicator = root.Q<VisualElement>("typing-indicator");
            _searchButton = root.Q<Button>("search-button");
            _searchInput = root.Q<TextField>("search-input");
            _spatialResultsPanel = root.Q<VisualElement>("spatial-results");

            _sendButton.clicked += SendMessage;
            _searchButton.clicked += PerformSpatialSearch;
            _messageInput.RegisterCallback<KeyDownEvent>(OnMessageInputKeyDown);
            _searchInput.RegisterCallback<KeyDownEvent>(OnSearchInputKeyDown);

            ApplyChatStyling();

            AddSystemMessage("🌱 Seed-enhanced TLDA Chat initialized! Connected to STAT7 addressing and Fractal-Chain system.");

            if (_platformBridge != null)
            {
                AddSystemMessage($"🎮 Connected to {_platformBridge.PlatformType} platform");
            }
        }

        void SetupWarblerConnection()
        {
            _warblerBridge = new WarblerChatBridge();
            _warblerBridge.OnResponseReceived += OnWarblerResponse;
            _warblerBridge.OnSystemEvent += OnSystemEvent;
        }

        async void InitializeSeedIntegration()
        {
            if (seedBridge != null)
            {
                try
                {
                    // Generate user's STAT7 address for this session
                    _userStat7Address = await GenerateUserStat7Address();
                    AddSystemMessage($"📍 Your session STAT7 address: {_userStat7Address}");
                }
                catch (System.Exception ex)
                {
                    Debug.LogError($"Failed to initialize Seed integration: {ex.Message}");
                    AddSystemMessage("⚠️ Seed integration unavailable");
                }
            }
        }

        async void SetupPlatformIntegration()
        {
            if (_platformBridge != null && enableCrossPlatformSync)
            {
                try
                {
                    var userIdentity = await _platformBridge.AuthenticateUser();
                    AddSystemMessage($"👤 Welcome {userIdentity.DisplayName}! Syncing platform data...");

                    // Sync platform achievements as narratives
                    await SyncPlatformAchievements(userIdentity);

                    // Sync platform companions
                    await SyncPlatformCompanions(userIdentity);

                    _platformBridge.OnPlatformEvent += OnPlatformEvent;
                    _platformBridge.OnNarrativeEvent += OnNarrativeEvent;
                }
                catch (System.Exception ex)
                {
                    Debug.LogError($"Failed to setup platform integration: {ex.Message}");
                    AddSystemMessage("⚠️ Platform integration unavailable");
                }
            }
        }

        void OnMessageInputKeyDown(KeyDownEvent evt)
        {
            if (evt.keyCode == KeyCode.Return && !evt.shiftKey)
            {
                SendMessage();
                evt.StopPropagation();
            }
        }

        void OnSearchInputKeyDown(KeyDownEvent evt)
        {
            if (evt.keyCode == KeyCode.Return)
            {
                PerformSpatialSearch();
                evt.StopPropagation();
            }
        }

        async void SendMessage()
        {
            var message = _messageInput.text.Trim();
            if (string.IsNullOrEmpty(message)) return;

            // Create enhanced chat message
            var chatMessage = new SeedChatMessage
            {
                Sender = "You",
                Content = message,
                Timestamp = System.DateTime.Now,
                Type = SeedChatMessageType.User,
                Stat7Address = await GenerateMessageStat7Address(message),
                SourcePlatform = _platformBridge?.PlatformType
            };

            _messageHistory.Add(chatMessage);
            AddMessageToUI(chatMessage);
            _messageInput.value = "";

            // Auto-register as narrative if enabled
            if (autoRegisterNarratives && seedBridge != null)
            {
                _ = Task.Run(async () =>
                {
                    try
                    {
                        await seedBridge.RegisterNewEntity(message, "narrative");
                        AddSystemMessage("📝 Message registered as narrative entity");
                    }
                    catch (System.Exception ex)
                    {
                        Debug.LogError($"Failed to register narrative: {ex.Message}");
                    }
                });
            }

            ShowTypingIndicator(true);

            try
            {
                await _warblerBridge.SendMessage(message);
            }
            catch (System.Exception e)
            {
                AddSystemMessage($"❌ Error: {e.Message}");
                ShowTypingIndicator(false);
            }
        }

        async void PerformSpatialSearch()
        {
            var query = _searchInput.text.Trim();
            if (string.IsNullOrEmpty(query) || seedBridge == null) return;

            AddSystemMessage($"🔍 Searching spatially for: {query}");
            ShowTypingIndicator(true);

            try
            {
                await seedBridge.SearchAndVisualize(query);

                var results = await seedBridge.SearchEntities(query);
                DisplaySpatialResults(results.Cast<object>(), query);

                AddSystemMessage($"✅ Found {results.Count()} spatial entities");
            }
            catch (System.Exception ex)
            {
                AddSystemMessage($"❌ Spatial search failed: {ex.Message}");
            }
            finally
            {
                ShowTypingIndicator(false);
            }
        }

        void OnWarblerResponse(string response, bool isDecision = false)
        {
            ShowTypingIndicator(false);

            var messageType = isDecision ? SeedChatMessageType.Warbler : SeedChatMessageType.User;
            var sender = isDecision ? "🧠 Warbler" : "🤖 Gemma3";

            var chatMessage = new SeedChatMessage
            {
                Sender = sender,
                Content = response,
                Timestamp = System.DateTime.Now,
                Type = messageType
            };

            _messageHistory.Add(chatMessage);
            AddMessageToUI(chatMessage);

            // Auto-scroll to bottom
            _chatScrollView.ScrollTo(_chatScrollView.contentContainer.Children().Last());
        }

        void OnSystemEvent(string eventMessage)
        {
            AddSystemMessage(eventMessage);

            if (enableTldlLogging && (eventMessage.Contains("Decision") || eventMessage.Contains("Error")))
            {
                _ = Task.Run(() => CreateTldlEntry(eventMessage));
            }
        }

        void OnPlatformEvent(PlatformEvent platformEvent)
        {
            var chatMessage = new SeedChatMessage
            {
                Sender = "🎮 Platform",
                Content = $"Platform event: {platformEvent.EventType}",
                Timestamp = platformEvent.Timestamp,
                Type = SeedChatMessageType.PlatformEvent,
                SourcePlatform = _platformBridge?.PlatformType,
                Metadata = platformEvent.Data
            };

            _messageHistory.Add(chatMessage);
            AddMessageToUI(chatMessage);
        }

        void OnNarrativeEvent(NarrativeEvent narrativeEvent)
        {
            var chatMessage = new SeedChatMessage
            {
                Sender = "🌱 Narrative",
                Content = $"Narrative event: {narrativeEvent.EventType}",
                Timestamp = narrativeEvent.Timestamp,
                Type = SeedChatMessageType.SeedEntity,
                Stat7Address = narrativeEvent.Stat7Address,
                Metadata = narrativeEvent.Data
            };

            _messageHistory.Add(chatMessage);
            AddMessageToUI(chatMessage);

            // Highlight in Mind Castle if visualization is enabled
            if (enableNarrativeVisualization && seedBridge != null)
            {
                _ = Task.Run(async () =>
                {
                    try
                    {
                        await seedBridge.SearchAndVisualize(narrativeEvent.Stat7Address);
                    }
                    catch (System.Exception ex)
                    {
                        Debug.LogError($"Failed to visualize narrative event: {ex.Message}");
                    }
                });
            }
        }

        void AddMessageToUI(SeedChatMessage message)
        {
            var messageElement = CreateEnhancedMessageElement(message);
            _chatScrollView.Add(messageElement);
        }

        void AddSystemMessage(string content)
        {
            var chatMessage = new SeedChatMessage
            {
                Sender = "System",
                Content = content,
                Timestamp = System.DateTime.Now,
                Type = SeedChatMessageType.System
            };

            _messageHistory.Add(chatMessage);
            AddMessageToUI(chatMessage);
        }

        VisualElement CreateEnhancedMessageElement(SeedChatMessage message)
        {
            var messageContainer = new VisualElement();
            messageContainer.AddToClassList("message-container");
            messageContainer.AddToClassList($"message-{message.Type.ToString().ToLower()}");

            // Header with sender, timestamp, and platform
            var headerText = $"{message.Sender} • {message.Timestamp:HH:mm}";
            if (message.SourcePlatform.HasValue)
            {
                headerText += $" • {message.SourcePlatform.Value}";
            }
            if (!string.IsNullOrEmpty(message.Stat7Address))
            {
                headerText += $" • {message.Stat7Address.Substring(0, 20)}...";
            }

            var header = new Label(headerText);
            header.AddToClassList("message-header");

            // Message content
            var content = new Label(message.Content);
            content.AddToClassList("message-content");

            // Highlight STAT7 addresses if enabled
            if (highlightStat7Addresses && message.Content.Contains("stat7://"))
            {
                content.AddToClassList("contains-stat7");
            }

            // Related entities section
            VisualElement relatedEntitiesContainer = null;
            if (showRelatedEntities && message.RelatedEntities.Count > 0)
            {
                relatedEntitiesContainer = new VisualElement();
                relatedEntitiesContainer.AddToClassList("related-entities");

                var relatedLabel = new Label("Related Entities:");
                relatedLabel.AddToClassList("related-label");
                relatedEntitiesContainer.Add(relatedLabel);

                foreach (var entityId in message.RelatedEntities)
                {
                    var entityLabel = new Label($"• {entityId}");
                    entityLabel.AddToClassList("related-entity");
                    relatedEntitiesContainer.Add(entityLabel);
                }
            }

            // Special styling for different message types
            switch (message.Type)
            {
                case SeedChatMessageType.Code:
                    content.AddToClassList("code-block");
                    break;
                case SeedChatMessageType.Warbler:
                    content.AddToClassList("warbler-decision");
                    break;
                case SeedChatMessageType.SeedEntity:
                    content.AddToClassList("seed-entity");
                    break;
                case SeedChatMessageType.SpatialSearch:
                    content.AddToClassList("spatial-search");
                    break;
                case SeedChatMessageType.PlatformEvent:
                    content.AddToClassList("platform-event");
                    break;
                case SeedChatMessageType.NarrativeCompanion:
                    content.AddToClassList("narrative-companion");
                    break;
                case SeedChatMessageType.System:
                    content.AddToClassList("system-message");
                    break;
            }

            messageContainer.Add(header);
            messageContainer.Add(content);

            if (relatedEntitiesContainer != null)
            {
                messageContainer.Add(relatedEntitiesContainer);
            }

            return messageContainer;
        }

        void DisplaySpatialResults(IEnumerable<object> results, string query)
        {
            _spatialResultsPanel.Clear();

            var resultsLabel = new Label($"Spatial Results for '{query}':");
            resultsLabel.AddToClassList("results-header");
            _spatialResultsPanel.Add(resultsLabel);

            foreach (var result in results.Take(10)) // Limit to 10 results
            {
                var resultElement = new Label(result.ToString());
                resultElement.AddToClassList("spatial-result");
                _spatialResultsPanel.Add(resultElement);
            }

            _spatialResultsPanel.style.display = DisplayStyle.Flex;
        }

        void ShowTypingIndicator(bool show)
        {
            _typingIndicator.style.display = show ? DisplayStyle.Flex : DisplayStyle.None;
        }

        void ApplyChatStyling()
        {
            var styleSheet = Resources.Load<StyleSheet>("SeedEnhancedChat");
            if (styleSheet != null)
            {
                chatUIDocument.rootVisualElement.styleSheets.Add(styleSheet);
            }
        }

        Task<string> GenerateUserStat7Address()
        {
            // Generate STAT7 address for user session
            var sessionId = _currentSessionId.GetHashCode();
            var resonance = (sessionId % 1000) / 1000.0;
            var velocity = ((sessionId / 1000) % 1000) / 1000.0;
            var density = ((sessionId / 1000000) % 1000) / 1000.0;

            return Task.FromResult($"stat7://user/{sessionId}/hash{sessionId:X8}?r={resonance:F3}&v={velocity:F3}&d={density:F3}");
        }

        Task<string> GenerateMessageStat7Address(string message)
        {
            // Generate STAT7 address for message
            var messageHash = message.GetHashCode();
            var resonance = Math.Abs(messageHash % 1000) / 1000.0;
            var velocity = Math.Abs((messageHash / 1000) % 1000) / 1000.0;
            var density = Math.Abs((messageHash / 1000000) % 1000) / 1000.0;

            return Task.FromResult($"stat7://message/{messageHash}/hash{messageHash:X8}?r={resonance:F3}&v={velocity:F3}&d={density:F3}");
        }

        async Task SyncPlatformAchievements(PlatformUserIdentity userIdentity)
        {
            if (_platformBridge == null) return;

            try
            {
                var achievements = await _platformBridge.GetAchievements();
                var unlockedCount = achievements.UnlockedCount;

                if (unlockedCount > 0)
                {
                    AddSystemMessage($"🏆 Synced {unlockedCount} platform achievements as narrative entities");

                    foreach (var achievement in achievements.UnlockedAchievements.Take(3))
                    {
                        var achievementMessage = new SeedChatMessage
                        {
                            Sender = "🏆 Achievement",
                            Content = $"{achievement.Name}: {achievement.Description}",
                            Timestamp = System.DateTime.Now,
                            Type = SeedChatMessageType.SeedEntity,
                            Stat7Address = achievement.Stat7Address,
                            SourcePlatform = _platformBridge.PlatformType
                        };

                        _messageHistory.Add(achievementMessage);
                        AddMessageToUI(achievementMessage);
                    }
                }
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"Failed to sync platform achievements: {ex.Message}");
            }
        }

        async Task SyncPlatformCompanions(PlatformUserIdentity userIdentity)
        {
            if (_platformBridge == null) return;

            try
            {
                var companions = await _platformBridge.GetNarrativeCompanions();

                if (companions.Count > 0)
                {
                    AddSystemMessage($"🐾 Synced {companions.Count} narrative companions");

                    foreach (var companion in companions.Take(3))
                    {
                        var companionMessage = new SeedChatMessage
                        {
                            Sender = "🐾 Companion",
                            Content = $"{companion.Name} (Level {companion.Level}): {companion.Personality}",
                            Timestamp = System.DateTime.Now,
                            Type = SeedChatMessageType.NarrativeCompanion,
                            Stat7Address = companion.Stat7Address,
                            SourcePlatform = _platformBridge.PlatformType
                        };

                        _messageHistory.Add(companionMessage);
                        AddMessageToUI(companionMessage);
                    }
                }
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"Failed to sync platform companions: {ex.Message}");
            }
        }

        async void CreateTldlEntry(string eventDescription)
        {
            var entry = $@"
# TLDL-{System.DateTime.Now:yyyy-MM-dd}-SeedEnhanced-ChatSession

## Metadata
- Entry ID: TLDL-{System.DateTime.Now:yyyy-MM-dd}-SeedEnhanced-ChatSession
- Author: Seed-enhanced TLDA Chat Interface
- Context: Interactive chat session with Warbler/Gemma3 + Seed integration
- Session ID: {_currentSessionId}
- User STAT7 Address: {_userStat7Address}
- Summary: {eventDescription}

## Chat History (Last 10 messages)
{string.Join("\n", _messageHistory.TakeLast(10).Select(m => $"- [{m.Type}] {m.Sender}: {m.Content}"))}

## Key Decisions
- {eventDescription}

## Seed Integration
- Messages Registered: {_messageHistory.Count(m => m.Type == SeedChatMessageType.User)}
- Spatial Searches: {_messageHistory.Count(m => m.Type == SeedChatMessageType.SpatialSearch)}
- Platform Events: {_messageHistory.Count(m => m.Type == SeedChatMessageType.PlatformEvent)}
- Narrative Events: {_messageHistory.Count(m => m.Type == SeedChatMessageType.SeedEntity)}
";

            AddMessage("📜 TLDL", "Enhanced entry created with Seed metadata", SeedChatMessageType.Tldl);

            await SaveTldlEntry(entry);
        }

        private void AddMessage(string tldl, string enhancedEntryCreatedWithSeedMetadata, SeedChatMessageType seedChatMessageType)
        {
            // TODO: Use 👀STAT7 Auth or a STAT7 valid anonymous address for the sender.
            // TODO: Implement this method to add a message to the UI or any other desired action.
            // It should auth the user via STAT7 authentication and then call the appropriate methods to interact with Seed.
            // You may need to implement additional logic here depending on how you want to handle these interactions.
            // For example, you might use the `seedBridge` instance to register narratives or perform spatial searches.
        }

        async Task SaveTldlEntry(string entry)
        {
            // Implementation would save to TLDL system with STAT7 addressing
            await Task.Delay(100);
        }

        // Public API for external systems
        public void AddNarrativeCompanionMessage(string companionName, string message, string companionStat7Address)
        {
            var companionMessage = new SeedChatMessage
            {
                Sender = $"🐾 {companionName}",
                Content = message,
                Timestamp = System.DateTime.Now,
                Type = SeedChatMessageType.NarrativeCompanion,
                Stat7Address = companionStat7Address
            };

            _messageHistory.Add(companionMessage);
            AddMessageToUI(companionMessage);
        }

        public async Task RegisterExternalNarrative(string content, string realm = "narrative")
        {
            if (seedBridge != null)
            {
                try
                {
                    await seedBridge.RegisterNewEntity(content, realm);
                    AddSystemMessage($"📝 External narrative registered in realm: {realm}");
                }
                catch (System.Exception ex)
                {
                    AddSystemMessage($"❌ Failed to register external narrative: {ex.Message}");
                }
            }
        }
    }

    // Enhanced Warbler bridge with Seed integration
    public class WarblerChatBridge
    {
        public System.Action<string, bool> OnResponseReceived = delegate { };
        public System.Action<string> OnSystemEvent = delegate { };

        public async Task SendMessage(string message)
        {
            OnSystemEvent?.Invoke($"Processing: {message}");

            // Simulate enhanced Warbler decision process with Seed context
            await Task.Delay(1000);

            if (message.Contains("decide") || message.Contains("choose"))
            {
                var decision = "After analyzing the context through STAT7 spatial mapping, I recommend Option A based on risk assessment and potential narrative impact.";
                OnResponseReceived?.Invoke(decision, true);
            }
            else if (message.Contains("search") || message.Contains("find"))
            {
                var response = "I'll search the spatial database for entities related to your query. The results will appear in the Mind Castle visualization.";
                OnResponseReceived?.Invoke(response, false);
            }
            else if (message.Contains("narrative") || message.Contains("story"))
            {
                var response = "I can help you create a narrative entity that will be registered in The Seed with its own STAT7 address and spatial coordinates.";
                OnResponseReceived?.Invoke(response, false);
            }
            else
            {
                var response = $"I understand you're asking about: {message}. Let me help you with that development task using the enhanced Seed architecture.";
                OnResponseReceived?.Invoke(response, false);
            }
        }
    }
}

// Missing type definitions to fix compilation
namespace TWG.Seed.Integration
{
    // SeedMindCastleBridge is defined in SeedMindCastleBridge.cs
}
