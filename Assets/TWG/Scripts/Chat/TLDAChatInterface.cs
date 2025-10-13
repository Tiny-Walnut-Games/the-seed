using UnityEngine;
using UnityEngine.UIElements;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Linq;

namespace TWG.TLDA.Chat
{
    /// <summary>
    /// Unity UI Toolkit-based chat interface for TLDA/Warbler/Gemma3 interaction
    /// Provides rich chat with code highlighting, TLDL integration, and visual feedback
    /// </summary>
    public class TLDAChatInterface : MonoBehaviour
    {
        [Header("Chat Configuration")]
        [SerializeField] private UIDocument chatUIDocument;
        [SerializeField] private bool connectToWarbler = true;
        [SerializeField] private bool enableTLDLLogging = true;

        private ScrollView chatScrollView;
        private TextField messageInput;
        private Button sendButton;
        private VisualElement typingIndicator;

        private List<ChatMessage> messageHistory = new List<ChatMessage>();
        private WarblerChatBridge warblerBridge;

        public class ChatMessage
        {
            public string sender = string.Empty;
            public string content = string.Empty;
            public System.DateTime timestamp;
            public ChatMessageType type;
        }

        public enum ChatMessageType
        {
            User,
            Warbler,
            System,
            Code,
            TLDL
        }

        void Start()
        {
            InitializeChatUI();
            SetupWarblerConnection();
        }

        void InitializeChatUI()
        {
            var root = chatUIDocument.rootVisualElement;

            chatScrollView = root.Q<ScrollView>("chat-messages");
            messageInput = root.Q<TextField>("message-input");
            sendButton = root.Q<Button>("send-button");
            typingIndicator = root.Q<VisualElement>("typing-indicator");

            sendButton.clicked += SendMessage;
            messageInput.RegisterCallback<KeyDownEvent>(OnMessageInputKeyDown);

            // Style the chat interface
            ApplyChatStyling();

            // Welcome message
            AddSystemMessage("🧙‍♂️ TLDA Chat Interface initialized! Connected to Warbler cognitive architecture and Gemma3 AI.");
        }

        void SetupWarblerConnection()
        {
            warblerBridge = new WarblerChatBridge();
            warblerBridge.OnResponseReceived += OnWarblerResponse;
            warblerBridge.OnSystemEvent += OnSystemEvent;
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
            var message = messageInput.text.Trim();
            if (string.IsNullOrEmpty(message)) return;

            // Add user message to chat
            AddMessage("You", message, ChatMessageType.User);
            messageInput.value = "";

            // Show typing indicator
            ShowTypingIndicator(true);

            try
            {
                // Send to Warbler for processing
                await warblerBridge.SendMessage(message);
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
            chatScrollView.ScrollTo(chatScrollView.contentContainer.Children().Last());
        }

        void OnSystemEvent(string eventMessage)
        {
            AddSystemMessage(eventMessage);

            // Create TLDL entry for significant events
            if (enableTLDLLogging && (eventMessage.Contains("Decision") || eventMessage.Contains("Error")))
            {
                CreateTLDLEntry(eventMessage);
            }
        }

        void AddMessage(string sender, string content, ChatMessageType type)
        {
            var message = new ChatMessage
            {
                sender = sender,
                content = content,
                timestamp = System.DateTime.Now,
                type = type
            };

            messageHistory.Add(message);

            // Create visual message element
            var messageElement = CreateMessageElement(message);
            chatScrollView.Add(messageElement);
        }

        void AddSystemMessage(string content)
        {
            AddMessage("System", content, ChatMessageType.System);
        }

        VisualElement CreateMessageElement(ChatMessage message)
        {
            var messageContainer = new VisualElement();
            messageContainer.AddToClassList("message-container");
            messageContainer.AddToClassList($"message-{message.type.ToString().ToLower()}");

            // Sender and timestamp
            var header = new Label($"{message.sender} • {message.timestamp:HH:mm}");
            header.AddToClassList("message-header");

            // Message content
            var content = new Label(message.content);
            content.AddToClassList("message-content");

            // Special handling for different message types
            switch (message.type)
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
            typingIndicator.style.display = show ? DisplayStyle.Flex : DisplayStyle.None;
        }

        void ApplyChatStyling()
        {
            var styleSheet = Resources.Load<StyleSheet>("ChatInterface");
            if (styleSheet != null)
            {
                chatUIDocument.rootVisualElement.styleSheets.Add(styleSheet);
            }
        }

        async void CreateTLDLEntry(string eventDescription)
        {
            var entry = $@"
# TLDL-{System.DateTime.Now:yyyy-MM-dd}-ChatSession

## Metadata
- Entry ID: TLDL-{System.DateTime.Now:yyyy-MM-dd}-ChatSession
- Author: TLDA Chat Interface
- Context: Interactive chat session with Warbler/Gemma3
- Summary: {eventDescription}

## Chat History
{string.Join("\n", messageHistory.TakeLast(5).Select(m => $"- {m.sender}: {m.content}"))}

## Key Decisions
- {eventDescription}
";

            AddMessage("📜 TLDL", "Entry created for this conversation", ChatMessageType.TLDL);

            // Save to TLDL system
            await SaveTLDLEntry(entry);
        }

        async Task SaveTLDLEntry(string entry)
        {
            // Implementation would save to TLDL system
            await Task.Delay(100); // Placeholder
        }
    }

    public class WarblerChatBridge
    {
        public System.Action<string, bool>? OnResponseReceived;
        public System.Action<string>? OnSystemEvent;

        public async Task SendMessage(string message)
        {
            OnSystemEvent?.Invoke($"Processing: {message}");

            // Simulate Warbler decision process
            await Task.Delay(1000);

            if (message.Contains("decide") || message.Contains("choose"))
            {
                var decision = "After analyzing the context, I recommend Option A based on risk assessment and potential impact.";
                OnResponseReceived?.Invoke(decision, true);
            }
            else
            {
                var response = $"I understand you're asking about: {message}. Let me help you with that development task.";
                OnResponseReceived?.Invoke(response, false);
            }
        }
    }
}
