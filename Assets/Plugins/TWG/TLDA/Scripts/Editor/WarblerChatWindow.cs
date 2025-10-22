using System.Linq;
using System.Threading.Tasks;
using TWG.TLDA.Chat;
using UnityEditor;
using UnityEngine;
using UnityEngine.UIElements;

namespace TWG.Scripts.Editor
{
    // Simple EditorWindow wrapper to host the TLDA Chat Interface in the Editor
    public class WarblerChatWindow : EditorWindow
    {
        [MenuItem("TLDA/💬 Warbler Chat")]
        public static void ShowWindow()
        {
            var window = GetWindow<WarblerChatWindow>("Warbler Chat");
            window.minSize = new Vector2(500, 400);
            window.Show();
        }

        private VisualTreeAsset _chatUxml = null;
        private StyleSheet _chatUss = null;

        private ScrollView _messages = null;
        private TextField _input = null;
        private Button _send = null;
        private VisualElement _typing = null;
        private WarblerChatBridge _bridge = null;

        private void OnEnable()
        {
            // Load UXML and USS from Resources/Assets pathing
            _chatUxml = AssetDatabase.LoadAssetAtPath<VisualTreeAsset>(
                "Assets/TWG/UI/ChatInterface.uxml");
            _chatUss = AssetDatabase.LoadAssetAtPath<StyleSheet>(
                "Assets/TWG/UI/ChatInterface.uss");
        }

        private void CreateGUI()
        {
            rootVisualElement.Clear();
            if (_chatUxml != null)
            {
                var root = _chatUxml.CloneTree();
                if (_chatUss != null)
                {
                    root.styleSheets.Add(_chatUss);
                }

                root.StretchToParentSize();
                rootVisualElement.Add(root);

                _messages = root.Q<ScrollView>("chat-messages");
                _input = root.Q<TextField>("message-input");
                _send = root.Q<Button>("send-button");
                _typing = root.Q<VisualElement>("typing-indicator");

                if (_send != null) _send.clicked += OnSend;
                if (_input != null) _input.RegisterCallback<KeyDownEvent>(OnKeyDown);

                // Bridge wiring
                _bridge = new WarblerChatBridge();
                _bridge.OnResponseReceived += (response, isDecision) =>
                {
                    SetTyping(false);
                    AddMessage(isDecision ? "🧠 Warbler" : "🤖 Gemma3", response);
                };
                _bridge.OnSystemEvent += (evt) =>
                {
                    AddSystem(evt);
                };

                AddSystem("🧙‍♂️ Warbler Chat ready in Editor");
            }
            else
            {
                rootVisualElement.Add(new Label("Chat UI not found. Ensure ChatInterface.uxml exists."));
            }
        }

        private void OnKeyDown(KeyDownEvent evt)
        {
            if (evt.keyCode == KeyCode.Return && !evt.shiftKey)
            {
                OnSend();
                evt.StopPropagation();
            }
        }

        private async void OnSend()
        {
            var text = _input?.text?.Trim();
            if (string.IsNullOrEmpty(text)) return;

            AddMessage("You", text);
            if (_input != null) _input.value = string.Empty;
            SetTyping(true);

            if (_bridge != null)
            {
                try
                {
                    await _bridge.SendMessage(text ?? string.Empty);
                }
                catch (System.Exception ex)
                {
                    SetTyping(false);
                    AddSystem($"❌ Error: {ex.Message}");
                }
            }
            else
            {
                // Fallback
                await Task.Delay(300);
                SetTyping(false);
                AddMessage("🤖 Gemma3", $"Echo: {text}");
            }
        }

        private void AddMessage(string sender, string? content)
        {
            content ??= string.Empty;
            var container = new VisualElement();
            container.AddToClassList("message-container");
            container.AddToClassList(sender == "You" ? "message-user" : "message-system");

            var header = new Label($"{sender} • {System.DateTime.Now:HH:mm}");
            header.AddToClassList("message-header");
            var body = new Label(content);
            body.AddToClassList("message-content");

            container.Add(header);
            container.Add(body);
            _messages?.Add(container);
            ScrollToBottom();
        }

        private void AddSystem(string? content) => AddMessage("System", content);

        private void SetTyping(bool show)
        {
            if (_typing != null)
            {
                _typing.style.display = show ? DisplayStyle.Flex : DisplayStyle.None;
            }
        }

        private void ScrollToBottom()
        {
            if (_messages != null && _messages.contentContainer?.Children()?.Any() == true)
            {
                _messages.ScrollTo(_messages.contentContainer.ElementAt(_messages.contentContainer.childCount - 1));
            }
        }
    }
}
