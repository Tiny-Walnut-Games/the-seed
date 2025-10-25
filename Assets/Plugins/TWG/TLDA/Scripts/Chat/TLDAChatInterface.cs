using UnityEngine;
using UnityEngine.UIElements;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Linq;
using UnityEngine.Serialization;

namespace TWG.TLDA.Chat
{
    /// <summary>
    /// Unity UI Toolkit-based chat interface for TLDA/Warbler/Gemma3 interaction
    /// Provides rich chat with code highlighting, TLDL integration, and visual feedback
    /// </summary>
    public class TldaChatInterface : MonoBehaviour
    {
        [Header("Chat Configuration")]
        [SerializeField] private UIDocument chatUIDocument;
        // [SerializeField] private bool connectToWarbler = true;  // Reserved for 👀future expansion
        [FormerlySerializedAs("enableTLDLLogging")] [SerializeField] private bool enableTldlLogging = true;

        private ScrollView _chatScrollView;
        private TextField _messageInput;
        private Button _sendButton;
        private VisualElement _typingIndicator;

        private List<ChatMessage> _messageHistory = new List<ChatMessage>();
        private WarblerChatBridge _warblerBridge;

        public class ChatMessage
        {
            public string Sender = string.Empty;
            public string Content = string.Empty;
            public System.DateTime Timestamp;
            public ChatMessageType Type;
        }

        public enum ChatMessageType
        {
            User,
            Warbler,
            System,
            Code,
            Tldl
        }

        void Start()
        {
            InitializeChatUI();
            SetupWarblerConnection();
        }

        void InitializeChatUI()
        {
            var root = chatUIDocument.rootVisualElement;

            _chatScrollView = root.Q<ScrollView>("chat-messages");
            _messageInput = root.Q<TextField>("message-input");
            _sendButton = root.Q<Button>("send-button");
            _typingIndicator = root.Q<VisualElement>("typing-indicator");

            _sendButton.clicked += SendMessage;
            _messageInput.RegisterCallback<KeyDownEvent>(OnMessageInputKeyDown);

            // Style the chat interface
            ApplyChatStyling();

            // Welcome message
            AddSystemMessage("🧙‍♂️ TLDA Chat Interface initialized! Connected to Warbler cognitive architecture and Gemma3 AI.");
        }

        void SetupWarblerConnection()
        {
            _warblerBridge = new WarblerChatBridge();
            _warblerBridge.OnResponseReceived += OnWarblerResponse;
            _warblerBridge.OnSystemEvent += OnSystemEvent;
        }

        void OnMessageInputKeyDown(KeyDownEvent evt)
        {
            if (evt.keyCode == KeyCode.Return && !evt.shiftKey)
            {
                SendMessage();
                evt.StopPropagation();
            }
        }

        async void SendMessage()
        {
            var message = _messageInput.text.Trim();
            if (string.IsNullOrEmpty(message)) return;

            // Add user message to chat
            AddMessage("You", message, ChatMessageType.User);
            _messageInput.value = "";

            // Show typing indicator
            ShowTypingIndicator(true);

            try
            {
                // Send to Warbler for processing
                await _warblerBridge.SendMessage(message);
            }
            catch (System.Exception e)
            {
                AddSystemMessage($"❌ Error: {e.Message}");
                ShowTypingIndicator(false);
            }
        }

        void OnWarblerResponse(string response, bool isDecision = false)
        {
            ShowTypingIndicator(false);

            if (isDecision)
            {
                AddMessage("🧠 Warbler", response, ChatMessageType.Warbler);
            }
            else
            {
                AddMessage("🤖 Gemma3", response, ChatMessageType.User);
            }

            // Auto-scroll to bottom
            _chatScrollView.ScrollTo(_chatScrollView.contentContainer.Children().Last());
        }

        void OnSystemEvent(string eventMessage)
        {
            AddSystemMessage(eventMessage);

            // Create TLDL entry for significant events
            if (enableTldlLogging && (eventMessage.Contains("Decision") || eventMessage.Contains("Error")))
            {
                CreateTldlEntry(eventMessage);
            }
        }

        void AddMessage(string sender, string content, ChatMessageType type)
        {
            var message = new ChatMessage
            {
                Sender = sender,
                Content = content,
                Timestamp = System.DateTime.Now,
                Type = type
            };

            _messageHistory.Add(message);

            // Create visual message element
            var messageElement = CreateMessageElement(message);
            _chatScrollView.Add(messageElement);
        }

        void AddSystemMessage(string content)
        {
            AddMessage("System", content, ChatMessageType.System);
        }

        VisualElement CreateMessageElement(ChatMessage message)
        {
            var messageContainer = new VisualElement();
            messageContainer.AddToClassList("message-container");
            messageContainer.AddToClassList($"message-{message.Type.ToString().ToLower()}");

            // Sender and timestamp
            var header = new Label($"{message.Sender} • {message.Timestamp:HH:mm}");
            header.AddToClassList("message-header");

            // Message content
            var content = new Label(message.Content);
            content.AddToClassList("message-content");

            // Special handling for different message types
            switch (message.Type)
            {
                case ChatMessageType.Code:
                    content.AddToClassList("code-block");
                    break;
                case ChatMessageType.Warbler:
                    content.AddToClassList("warbler-decision");
                    break;
                case ChatMessageType.System:
                    content.AddToClassList("system-message");
                    break;
            }

            messageContainer.Add(header);
            messageContainer.Add(content);

            return messageContainer;
        }

        void ShowTypingIndicator(bool show)
        {
            _typingIndicator.style.display = show ? DisplayStyle.Flex : DisplayStyle.None;
        }

        void ApplyChatStyling()
        {
            var styleSheet = Resources.Load<StyleSheet>("ChatInterface");
            if (styleSheet != null)
            {
                chatUIDocument.rootVisualElement.styleSheets.Add(styleSheet);
            }
        }

        async void CreateTldlEntry(string eventDescription)
        {
            var entry = $@"
# TLDL-{System.DateTime.Now:yyyy-MM-dd}-ChatSession

## Metadata
- Entry ID: TLDL-{System.DateTime.Now:yyyy-MM-dd}-ChatSession
- Author: TLDA Chat Interface
- Context: Interactive chat session with Warbler/Gemma3
- Summary: {eventDescription}

## Chat History
{string.Join("\n", _messageHistory.TakeLast(5).Select(m => $"- {m.Sender}: {m.Content}"))}

## Key Decisions
- {eventDescription}
";

            AddMessage("📜 TLDL", "Entry created for this conversation", ChatMessageType.Tldl);

            // Save to TLDL system
            await SaveTldlEntry(entry);
        }

        async Task SaveTldlEntry(string entry)
        {
            // Implementation would save to TLDL system
            await Task.Delay(100); // Placeholder
        }
    }
}
