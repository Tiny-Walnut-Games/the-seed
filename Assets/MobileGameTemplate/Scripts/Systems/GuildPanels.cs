using UnityEngine;
using UnityEngine.UIElements;
using MobileGameTemplate.Core; // 🔧 Unity 2022.3 Compatibility Bridge
using System.Collections.Generic;
using System.Linq; // 🔧 C# 10 Compatibility

namespace MobileGameTemplate.Systems
{
    /// <summary>
    /// 🏰 Guild information panel showing guild details and stats
    /// </summary>
    public class GuildInfoPanel : VisualElement
    {
        public System.Action OnJoinRequested;
        public System.Action OnCreateRequested;
        
        private Label _guildName;
        private Label _guildTag;
        private Label _guildDescription;
        private Label _guildLevel;
        private Label _memberCount;
        private Label _createdDate;
        private VisualElement _guildEmblem;
        private ProgressBar _experienceBar;
        private VisualElement _activitiesContainer;
        
        public GuildInfoPanel()
        {
            CreateInfoStructure();
        }
        
        private void CreateInfoStructure()
        {
            style.width = Length.Percent(100);
            style.height = Length.Percent(100);
            style.paddingTop = 16;
            style.paddingBottom = 16;
            style.paddingLeft = 16;
            style.paddingRight = 16;
            
            // Header section
            var headerContainer = new VisualElement();
            headerContainer.style.flexDirection = FlexDirection.Row;
            headerContainer.style.marginBottom = 24;
            headerContainer.style.alignItems = Align.Center;
            
            // Guild emblem
            _guildEmblem = new VisualElement();
            _guildEmblem.style.width = 80;
            _guildEmblem.style.height = 80;
            _guildEmblem.style.backgroundColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
            _guildEmblem.style.marginRight = 16;
            
            // Guild info
            var infoContainer = new VisualElement();
            infoContainer.style.flexGrow = 1;
            
            _guildName = new Label();
            _guildName.style.fontSize = 20;
            _guildName.style.color = Color.white;
            _guildName.style.unityFontStyleAndWeight = FontStyle.Bold;
            _guildName.style.marginBottom = 4;
            
            _guildTag = new Label();
            _guildTag.style.fontSize = 14;
            _guildTag.style.color = new Color(0.7f, 0.7f, 0.7f, 1f);
            _guildTag.style.marginBottom = 8;
            
            var statsContainer = new VisualElement();
            statsContainer.style.flexDirection = FlexDirection.Row;
            statsContainer.style.marginBottom = 4;
            
            _guildLevel = new Label();
            _guildLevel.style.fontSize = 12;
            _guildLevel.style.color = new Color(1f, 0.8f, 0f, 1f);
            _guildLevel.style.marginRight = 16;
            
            _memberCount = new Label();
            _memberCount.style.fontSize = 12;
            _memberCount.style.color = new Color(0.8f, 0.8f, 0.8f, 1f);
            
            statsContainer.Add(_guildLevel);
            statsContainer.Add(_memberCount);
            
            infoContainer.Add(_guildName);
            infoContainer.Add(_guildTag);
            infoContainer.Add(statsContainer);
            
            headerContainer.Add(_guildEmblem);
            headerContainer.Add(infoContainer);
            
            // Description section
            var descTitle = new Label("Description");
            descTitle.style.fontSize = 16;
            descTitle.style.color = Color.white;
            descTitle.style.unityFontStyleAndWeight = FontStyle.Bold;
            descTitle.style.marginBottom = 8;
            
            _guildDescription = new Label();
            _guildDescription.style.fontSize = 14;
            _guildDescription.style.color = new Color(0.8f, 0.8f, 0.8f, 1f);
            _guildDescription.style.whiteSpace = WhiteSpace.Normal;
            _guildDescription.style.marginBottom = 24;
            
            // Experience section
            var expTitle = new Label("Guild Experience");
            expTitle.style.fontSize = 16;
            expTitle.style.color = Color.white;
            expTitle.style.unityFontStyleAndWeight = FontStyle.Bold;
            expTitle.style.marginBottom = 8;
            
            _experienceBar = new ProgressBar();
            _experienceBar.style.height = 20;
            _experienceBar.style.marginBottom = 24;
            
            // Recent activities
            var activitiesTitle = new Label("Recent Activities");
            activitiesTitle.style.fontSize = 16;
            activitiesTitle.style.color = Color.white;
            activitiesTitle.style.unityFontStyleAndWeight = FontStyle.Bold;
            activitiesTitle.style.marginBottom = 8;
            
            _activitiesContainer = new VisualElement();
            _activitiesContainer.style.backgroundColor = new Color(0.05f, 0.05f, 0.05f, 0.8f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
            _activitiesContainer.style.paddingTop = 12;
            _activitiesContainer.style.paddingBottom = 12;
            _activitiesContainer.style.paddingLeft = 16;
            _activitiesContainer.style.paddingRight = 16;
            _activitiesContainer.style.maxHeight = 200;
            
            // Created date
            _createdDate = new Label();
            _createdDate.style.fontSize = 10;
            _createdDate.style.color = new Color(0.6f, 0.6f, 0.6f, 1f);
            _createdDate.style.position = Position.Absolute;
            _createdDate.style.bottom = 8;
            _createdDate.style.right = 8;
            
            Add(headerContainer);
            Add(descTitle);
            Add(_guildDescription);
            Add(expTitle);
            Add(_experienceBar);
            Add(activitiesTitle);
            Add(_activitiesContainer);
            Add(_createdDate);
        }
        
        public void SetGuild(GuildData guild)
        {
            _guildName.text = guild.guildName;
            _guildTag.text = $"[{guild.guildTag}]";
            _guildDescription.text = guild.description;
            _guildLevel.text = $"Level {guild.level}";
            _memberCount.text = $"{guild.memberCount}/{guild.maxMembers} Members";
            _createdDate.text = $"Created: {guild.createdDate:yyyy/MM/dd}";
            
            // Set guild emblem if available
            if (guild.guildEmblem != null)
            {
                _guildEmblem.style.backgroundImage = new StyleBackground(guild.guildEmblem);
            }
            
            // Update experience bar
            // This would typically calculate experience to next level
            _experienceBar.value = guild.experience % 1000 / 10f; // Simplified calculation
            
            UpdateRecentActivities(guild.recentActivities);
        }
        
        private void UpdateRecentActivities(List<GuildActivity> activities)
        {
            _activitiesContainer.Clear();
            
            if (activities == null || activities.Count == 0)
            {
                var noActivitiesLabel = new Label("No recent activities");
                noActivitiesLabel.style.fontSize = 12;
                noActivitiesLabel.style.color = new Color(0.6f, 0.6f, 0.6f, 1f);
                noActivitiesLabel.style.unityTextAlign = TextAnchor.MiddleCenter;
                _activitiesContainer.Add(noActivitiesLabel);
                return;
            }
            
            foreach (var activity in activities.Take(5)) // Show last 5 activities
            {
                var activityRow = new VisualElement();
                activityRow.style.flexDirection = FlexDirection.Row;
                activityRow.style.marginBottom = 8;
                activityRow.style.alignItems = Align.Center;
                
                var activityIcon = new VisualElement();
                activityIcon.style.width = 16;
                activityIcon.style.height = 16;
                activityIcon.style.backgroundColor = GetActivityColor(activity.type);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
                activityIcon.style.marginRight = 8;
                
                var activityText = new Label(activity.description);
                activityText.style.fontSize = 12;
                activityText.style.color = new Color(0.8f, 0.8f, 0.8f, 1f);
                activityText.style.flexGrow = 1;
                
                var activityTime = new Label(FormatActivityTime(activity.timestamp));
                activityTime.style.fontSize = 10;
                activityTime.style.color = new Color(0.6f, 0.6f, 0.6f, 1f);
                
                activityRow.Add(activityIcon);
                activityRow.Add(activityText);
                activityRow.Add(activityTime);
                
                _activitiesContainer.Add(activityRow);
            }
        }
        
        private Color GetActivityColor(GuildActivityType type)
        {
            return type switch
            {
                GuildActivityType.MemberJoined => new Color(0.3f, 0.7f, 0.3f, 1f),
                GuildActivityType.MemberLeft => new Color(0.7f, 0.3f, 0.3f, 1f),
                GuildActivityType.MemberPromoted => new Color(1f, 0.8f, 0f, 1f),
                GuildActivityType.GuildLevelUp => new Color(0.8f, 0.3f, 0.8f, 1f),
                GuildActivityType.Achievement => new Color(0.3f, 0.5f, 0.9f, 1f),
                _ => new Color(0.5f, 0.5f, 0.5f, 1f)
            };
        }
        
        private string FormatActivityTime(System.DateTime timestamp)
        {
            var timeDiff = System.DateTime.Now - timestamp;
            
            if (timeDiff.TotalMinutes < 1)
                return "Now";
            else if (timeDiff.TotalMinutes < 60)
                return $"{(int)timeDiff.TotalMinutes}m ago";
            else if (timeDiff.TotalHours < 24)
                return $"{(int)timeDiff.TotalHours}h ago";
            else
                return $"{(int)timeDiff.TotalDays}d ago";
        }
    }
    
    /// <summary>
    /// 🏰 Guild roster panel showing member list with management options
    /// </summary>
    public class GuildRosterPanel : VisualElement
    {
        public System.Action<GuildMember> OnMemberPromoted;
        public System.Action<GuildMember> OnMemberKicked;
        public System.Action<GuildInvite> OnInviteSent;
        
        private ScrollView _membersList;
        private DropdownField _sortFilter;
        private Button _inviteButton;
        private Label _memberCountLabel;
        
        private GuildData _currentGuild;
        private GuildMember _playerMember;
        private List<GuildMember> _sortedMembers = new List<GuildMember>();
        
        public GuildRosterPanel()
        {
            CreateRosterStructure();
        }
        
        private void CreateRosterStructure()
        {
            style.width = Length.Percent(100);
            style.height = Length.Percent(100);
            
            // Header with controls
            var headerContainer = new VisualElement();
            headerContainer.style.flexDirection = FlexDirection.Row;
            headerContainer.style.justifyContent = Justify.SpaceBetween;
            headerContainer.style.alignItems = Align.Center;
            headerContainer.style.marginBottom = 16;
            headerContainer.style.paddingLeft = 16;
            headerContainer.style.paddingRight = 16;
            headerContainer.style.paddingTop = 8;
            
            var leftControls = new VisualElement();
            leftControls.style.flexDirection = FlexDirection.Row;
            leftControls.style.alignItems = Align.Center;
            
            _memberCountLabel = new Label();
            _memberCountLabel.style.fontSize = 14;
            _memberCountLabel.style.color = Color.white;
            _memberCountLabel.style.marginRight = 16;
            
            _sortFilter = new DropdownField("Sort by");
            _sortFilter.style.width = 120;
            _sortFilter.choices = new List<string> { "Name", "Role", "Level", "Power", "Online", "Join Date" };
            _sortFilter.SetValueWithoutNotify("Role");
            _sortFilter.RegisterValueChangedCallback(OnSortChanged);
            
            leftControls.Add(_memberCountLabel);
            leftControls.Add(_sortFilter);
            
            _inviteButton = new Button(() => HandleInviteRequest());
            _inviteButton.text = "INVITE";
            _inviteButton.style.paddingLeft = 16;
            _inviteButton.style.paddingRight = 16;
            _inviteButton.style.paddingTop = 8;
            _inviteButton.style.paddingBottom = 8;
            _inviteButton.style.backgroundColor = new Color(0.3f, 0.5f, 0.7f, 0.9f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
// 🔧 LEGENDARY FIX: borderWidth not available in Unity 2022.3
            _inviteButton.style.color = Color.white;
            
            headerContainer.Add(leftControls);
            headerContainer.Add(_inviteButton);
            
            // Members list
            _membersList = new ScrollView(ScrollViewMode.Vertical);
            _membersList.style.flexGrow = 1;
            _membersList.style.marginLeft = 8;
            _membersList.style.marginRight = 8;
            
            Add(headerContainer);
            Add(_membersList);
        }
        
        public void SetGuild(GuildData guild, GuildMember playerMember)
        {
            _currentGuild = guild;
            _playerMember = playerMember;
            
            _memberCountLabel.text = $"{guild.memberCount}/{guild.maxMembers} Members";
            
            // Enable/disable invite button based on permissions
            bool canInvite = playerMember.role != GuildRole.Member && guild.settings.allowInvites;
            _inviteButton.SetEnabled(canInvite);
            
            RefreshMembersList();
        }
        
        private void RefreshMembersList()
        {
            if (_currentGuild == null) return;
            
            _membersList.Clear();
            SortMembers();
            
            foreach (var member in _sortedMembers)
            {
                var memberCard = CreateMemberCard(member);
                _membersList.Add(memberCard);
            }
        }
        
        private void SortMembers()
        {
            _sortedMembers = new List<GuildMember>(_currentGuild.members);
            
            switch (_sortFilter.value)
            {
                case "Name":
                    _sortedMembers = _sortedMembers.OrderBy(m => m.playerName).ToList();
                    break;
                case "Role":
                    _sortedMembers = _sortedMembers.OrderByDescending(m => (int)m.role).ThenBy(m => m.playerName).ToList();
                    break;
                case "Level":
                    _sortedMembers = _sortedMembers.OrderByDescending(m => m.level).ToList();
                    break;
                case "Power":
                    _sortedMembers = _sortedMembers.OrderByDescending(m => m.powerRating).ToList();
                    break;
                case "Online":
                    _sortedMembers = _sortedMembers.OrderByDescending(m => m.isOnline).ThenBy(m => m.lastOnline).ToList();
                    break;
                case "Join Date":
                    _sortedMembers = _sortedMembers.OrderBy(m => m.joinDate).ToList();
                    break;
            }
        }
        
        private VisualElement CreateMemberCard(GuildMember member)
        {
            var card = new VisualElement();
            card.style.backgroundColor = new Color(0.1f, 0.1f, 0.1f, 0.6f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
            card.style.marginBottom = 8;
            card.style.paddingTop = 12;
            card.style.paddingBottom = 12;
            card.style.paddingLeft = 16;
            card.style.paddingRight = 16;
            
            var mainRow = new VisualElement();
            mainRow.style.flexDirection = FlexDirection.Row;
            mainRow.style.alignItems = Align.Center;
            
            // Online status indicator
            var statusDot = new VisualElement();
            statusDot.style.width = 8;
            statusDot.style.height = 8;
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
            statusDot.style.backgroundColor = member.isOnline ? 
                new Color(0.3f, 0.7f, 0.3f, 1f) : 
                new Color(0.5f, 0.5f, 0.5f, 1f);
            statusDot.style.marginRight = 12;
            
            // Member info
            var infoContainer = new VisualElement();
            infoContainer.style.flexGrow = 1;
            
            var nameRoleRow = new VisualElement();
            nameRoleRow.style.flexDirection = FlexDirection.Row;
            nameRoleRow.style.alignItems = Align.Center;
            nameRoleRow.style.marginBottom = 4;
            
            var nameLabel = new Label(member.playerName);
            nameLabel.style.fontSize = 14;
            nameLabel.style.color = Color.white;
            nameLabel.style.unityFontStyleAndWeight = FontStyle.Bold;
            nameLabel.style.marginRight = 8;
            
            var roleLabel = new Label(member.role.ToString());
            roleLabel.style.fontSize = 12;
            roleLabel.style.color = GetRoleColor(member.role);
            roleLabel.style.backgroundColor = new Color(0f, 0f, 0f, 0.3f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
            roleLabel.style.paddingLeft = 6;
            roleLabel.style.paddingRight = 6;
            roleLabel.style.paddingTop = 2;
            roleLabel.style.paddingBottom = 2;
            
            nameRoleRow.Add(nameLabel);
            nameRoleRow.Add(roleLabel);
            
            var statsRow = new VisualElement();
            statsRow.style.flexDirection = FlexDirection.Row;
            
            var levelLabel = new Label($"Lv.{member.level}");
            levelLabel.style.fontSize = 12;
            levelLabel.style.color = new Color(0.8f, 0.8f, 0.8f, 1f);
            levelLabel.style.marginRight = 16;
            
            var powerLabel = new Label($"Power: {member.powerRating:N0}");
            powerLabel.style.fontSize = 12;
            powerLabel.style.color = new Color(0.8f, 0.8f, 0.8f, 1f);
            powerLabel.style.marginRight = 16;
            
            var lastOnlineLabel = new Label(member.isOnline ? "Online" : FormatLastOnline(member.lastOnline));
            lastOnlineLabel.style.fontSize = 10;
            lastOnlineLabel.style.color = new Color(0.6f, 0.6f, 0.6f, 1f);
            
            statsRow.Add(levelLabel);
            statsRow.Add(powerLabel);
            statsRow.Add(lastOnlineLabel);
            
            infoContainer.Add(nameRoleRow);
            infoContainer.Add(statsRow);
            
            // Action buttons (if player has permissions)
            var actionsContainer = new VisualElement();
            actionsContainer.style.flexDirection = FlexDirection.Row;
            
            bool canManage = _playerMember.role != GuildRole.Member && 
                           member.playerId != _playerMember.playerId &&
                           (int)_playerMember.role > (int)member.role;
            
            if (canManage)
            {
                if (member.role == GuildRole.Member)
                {
                    var promoteButton = new Button(() => OnMemberPromoted?.Invoke(member));
                    promoteButton.text = "↑";
                    promoteButton.style.width = 24;
                    promoteButton.style.height = 24;
                    promoteButton.style.backgroundColor = new Color(0f, 0.5f, 0.8f, 0.9f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
// 🔧 LEGENDARY FIX: borderWidth not available in Unity 2022.3
                    promoteButton.style.fontSize = 12;
                    promoteButton.style.color = Color.white;
                    promoteButton.style.marginLeft = 4;
                    actionsContainer.Add(promoteButton);
                }
                
                if (_playerMember.role == GuildRole.Leader)
                {
                    var kickButton = new Button(() => OnMemberKicked?.Invoke(member));
                    kickButton.text = "X";
                    kickButton.style.width = 24;
                    kickButton.style.height = 24;
                    kickButton.style.backgroundColor = new Color(0.8f, 0.3f, 0.3f, 0.9f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
// 🔧 LEGENDARY FIX: borderWidth not available in Unity 2022.3
                    kickButton.style.fontSize = 12;
                    kickButton.style.color = Color.white;
                    kickButton.style.marginLeft = 4;
                    actionsContainer.Add(kickButton);
                }
            }
            
            mainRow.Add(statusDot);
            mainRow.Add(infoContainer);
            mainRow.Add(actionsContainer);
            
            card.Add(mainRow);
            return card;
        }
        
        private Color GetRoleColor(GuildRole role)
        {
            return role switch
            {
                GuildRole.Leader => new Color(1f, 0.8f, 0f, 1f),
                GuildRole.Officer => new Color(0.8f, 0.3f, 0.8f, 1f),
                GuildRole.Member => new Color(0.6f, 0.6f, 0.6f, 1f),
                _ => Color.white
            };
        }
        
        private string FormatLastOnline(System.DateTime lastOnline)
        {
            var timeDiff = System.DateTime.Now - lastOnline;
            
            if (timeDiff.TotalMinutes < 60)
                return $"{(int)timeDiff.TotalMinutes}m ago";
            else if (timeDiff.TotalHours < 24)
                return $"{(int)timeDiff.TotalHours}h ago";
            else if (timeDiff.TotalDays < 7)
                return $"{(int)timeDiff.TotalDays}d ago";
            else
                return lastOnline.ToString("MM/dd");
        }
        
        private void OnSortChanged(ChangeEvent<string> evt)
        {
            RefreshMembersList();
        }
        
        private void HandleInviteRequest()
        {
            // This would typically open a player search dialog
            Debug.Log("🏰 Member invite requested - implement player search");
        }
    }
    
    /// <summary>
    /// 🏰 Guild chat panel with message history and input
    /// </summary>
    public class GuildChatPanel : VisualElement
    {
        public System.Action<string> OnMessageSent;
        
        private ScrollView _chatHistory;
        private TextField _messageInput;
        private Button _sendButton;
        
        private GuildData _currentGuild;
        private List<ChatMessage> _messages = new List<ChatMessage>();
        
        public GuildChatPanel()
        {
            CreateChatStructure();
        }
        
        private void CreateChatStructure()
        {
            style.width = Length.Percent(100);
            style.height = Length.Percent(100);
            style.flexDirection = FlexDirection.Column;
            
            // Chat history
            _chatHistory = new ScrollView(ScrollViewMode.Vertical);
            _chatHistory.style.flexGrow = 1;
            _chatHistory.style.marginLeft = 8;
            _chatHistory.style.marginRight = 8;
            _chatHistory.style.marginTop = 8;
            _chatHistory.style.marginBottom = 8;
            _chatHistory.style.backgroundColor = new Color(0.05f, 0.05f, 0.05f, 0.8f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
            _chatHistory.style.paddingTop = 8;
            _chatHistory.style.paddingBottom = 8;
            
            // Input area
            var inputContainer = new VisualElement();
            inputContainer.style.flexDirection = FlexDirection.Row;
            inputContainer.style.paddingLeft = 8;
            inputContainer.style.paddingRight = 8;
            inputContainer.style.paddingBottom = 8;
            inputContainer.style.alignItems = Align.Center;
            
            _messageInput = new TextField();
            _messageInput.style.flexGrow = 1;
            _messageInput.style.height = 36;
            _messageInput.style.marginRight = 8;
            _messageInput.SetValueWithoutNotify("Type a message...");
            
            _sendButton = new Button(SendMessage);
            _sendButton.text = "SEND";
            _sendButton.style.width = 60;
            _sendButton.style.height = 36;
            _sendButton.style.backgroundColor = new Color(0.3f, 0.7f, 0.3f, 0.9f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
// 🔧 LEGENDARY FIX: borderWidth not available in Unity 2022.3
            _sendButton.style.color = Color.white;
            
            inputContainer.Add(_messageInput);
            inputContainer.Add(_sendButton);
            
            Add(_chatHistory);
            Add(inputContainer);
            
            // Register Enter key for sending messages
            _messageInput.RegisterCallback<KeyDownEvent>(OnMessageInputKeyDown);
        }
        
        public void SetGuild(GuildData guild)
        {
            _currentGuild = guild;
            
            if (guild.chatHistory != null)
            {
                _messages = new List<ChatMessage>(guild.chatHistory);
                RefreshChatHistory();
            }
            
            // Enable/disable chat based on permissions
            bool canChat = guild.settings.chatEnabled && 
                          (guild.settings.chatPolicy == GuildChatPolicy.All);
            
            _messageInput.SetEnabled(canChat);
            _sendButton.SetEnabled(canChat);
            
            if (!canChat)
            {
                _messageInput.SetValueWithoutNotify("Chat disabled");
            }
        }
        
        public void AddMessage(ChatMessage message)
        {
            _messages.Add(message);
            
            // Keep only recent messages to prevent memory issues
            if (_messages.Count > 100)
            {
                _messages.RemoveRange(0, _messages.Count - 100);
            }
            
            AddMessageToHistory(message);
            ScrollToBottom();
        }
        
        private void RefreshChatHistory()
        {
            _chatHistory.Clear();
            
            foreach (var message in _messages)
            {
                AddMessageToHistory(message);
            }
            
            ScrollToBottom();
        }
        
        private void AddMessageToHistory(ChatMessage message)
        {
            var messageContainer = new VisualElement();
            messageContainer.style.paddingLeft = 12;
            messageContainer.style.paddingRight = 12;
            messageContainer.style.paddingTop = 4;
            messageContainer.style.paddingBottom = 4;
            messageContainer.style.marginBottom = 4;
            
            // Message header with sender and timestamp
            var headerContainer = new VisualElement();
            headerContainer.style.flexDirection = FlexDirection.Row;
            headerContainer.style.justifyContent = Justify.SpaceBetween;
            headerContainer.style.marginBottom = 2;
            
            var senderLabel = new Label(message.senderName);
            senderLabel.style.fontSize = 12;
            senderLabel.style.color = GetMessageTypeColor(message.type);
            senderLabel.style.unityFontStyleAndWeight = FontStyle.Bold;
            
            var timestampLabel = new Label(message.timestamp.ToString("HH:mm"));
            timestampLabel.style.fontSize = 10;
            timestampLabel.style.color = new Color(0.6f, 0.6f, 0.6f, 1f);
            
            headerContainer.Add(senderLabel);
            headerContainer.Add(timestampLabel);
            
            // Message content
            var contentLabel = new Label(message.content);
            contentLabel.style.fontSize = 14;
            contentLabel.style.color = message.type == ChatMessageType.System ? 
                new Color(0.8f, 0.8f, 0.3f, 1f) : 
                new Color(0.9f, 0.9f, 0.9f, 1f);
            contentLabel.style.whiteSpace = WhiteSpace.Normal;
            
            messageContainer.Add(headerContainer);
            messageContainer.Add(contentLabel);
            
            _chatHistory.Add(messageContainer);
        }
        
        private Color GetMessageTypeColor(ChatMessageType type)
        {
            return type switch
            {
                ChatMessageType.System => new Color(0.8f, 0.8f, 0.3f, 1f),
                ChatMessageType.Achievement => new Color(1f, 0.8f, 0f, 1f),
                ChatMessageType.Welcome => new Color(0.3f, 0.7f, 0.3f, 1f),
                _ => Color.white
            };
        }
        
        private void SendMessage()
        {
            string message = _messageInput.value;
            
            if (string.IsNullOrWhiteSpace(message) || message == "Type a message...")
                return;
            
            OnMessageSent?.Invoke(message);
            _messageInput.SetValueWithoutNotify("");
            _messageInput.Focus();
        }
        
        private void ScrollToBottom()
        {
            // Schedule scroll to bottom after layout
            schedule.Execute(() =>
            {
                _chatHistory.scrollOffset = new Vector2(0, _chatHistory.contentContainer.layout.height);
            }).ExecuteLater(50);
        }
        
        private void OnMessageInputKeyDown(KeyDownEvent evt)
        {
            if (evt.keyCode == KeyCode.Return || evt.keyCode == KeyCode.KeypadEnter)
            {
                SendMessage();
                evt.StopPropagation();
            }
        }
    }
    
    /// <summary>
    /// 🏰 Guild settings panel for management options
    /// </summary>
    public class GuildSettingsPanel : VisualElement
    {
        public System.Action OnLeaveRequested;
        public System.Action<GuildSettings> OnSettingsChanged;
        
        private DropdownField _joinPolicyDropdown;
        private IntegerField _minimumLevelField;
        private IntegerField _minimumPowerField;
        private Toggle _allowInvitesToggle;
        private Toggle _chatEnabledToggle;
        private DropdownField _chatPolicyDropdown;
        private Button _leaveGuildButton;
        
        private GuildData _currentGuild;
        private GuildMember _playerMember;
        
        public GuildSettingsPanel()
        {
            CreateSettingsStructure();
        }
        
        private void CreateSettingsStructure()
        {
            style.width = Length.Percent(100);
            style.height = Length.Percent(100);
            style.paddingTop = 16;
            style.paddingBottom = 16;
            style.paddingLeft = 16;
            style.paddingRight = 16;
            
            // Settings section
            var settingsTitle = new Label("Guild Settings");
            settingsTitle.style.fontSize = 18;
            settingsTitle.style.color = Color.white;
            settingsTitle.style.unityFontStyleAndWeight = FontStyle.Bold;
            settingsTitle.style.marginBottom = 16;
            
            // Join policy
            _joinPolicyDropdown = new DropdownField("Join Policy");
            _joinPolicyDropdown.style.marginBottom = 12;
            _joinPolicyDropdown.choices = System.Enum.GetNames(typeof(GuildJoinPolicy)).ToList();
            
            // Level requirements
            _minimumLevelField = new IntegerField("Minimum Level");
            _minimumLevelField.style.marginBottom = 12;
            
            _minimumPowerField = new IntegerField("Minimum Power");
            _minimumPowerField.style.marginBottom = 12;
            
            // Invite settings
            _allowInvitesToggle = new Toggle("Allow Member Invites");
            _allowInvitesToggle.style.marginBottom = 12;
            
            // Chat settings
            _chatEnabledToggle = new Toggle("Enable Guild Chat");
            _chatEnabledToggle.style.marginBottom = 12;
            
            _chatPolicyDropdown = new DropdownField("Chat Policy");
            _chatPolicyDropdown.style.marginBottom = 24;
            _chatPolicyDropdown.choices = System.Enum.GetNames(typeof(GuildChatPolicy)).ToList();
            
            // Leave guild button
            _leaveGuildButton = new Button(() => OnLeaveRequested?.Invoke());
            _leaveGuildButton.text = "LEAVE GUILD";
            _leaveGuildButton.style.backgroundColor = new Color(0.8f, 0.3f, 0.3f, 0.9f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
// 🔧 LEGENDARY FIX: borderWidth not available in Unity 2022.3
            _leaveGuildButton.style.color = Color.white;
            _leaveGuildButton.style.height = 40;
            _leaveGuildButton.style.marginTop = 32;
            
            Add(settingsTitle);
            Add(_joinPolicyDropdown);
            Add(_minimumLevelField);
            Add(_minimumPowerField);
            Add(_allowInvitesToggle);
            Add(_chatEnabledToggle);
            Add(_chatPolicyDropdown);
            Add(_leaveGuildButton);
            
            RegisterSettingsCallbacks();
        }
        
        private void RegisterSettingsCallbacks()
        {
            _joinPolicyDropdown.RegisterValueChangedCallback(OnSettingChanged);
            _minimumLevelField.RegisterValueChangedCallback(OnSettingChanged);
            _minimumPowerField.RegisterValueChangedCallback(OnSettingChanged);
            _allowInvitesToggle.RegisterValueChangedCallback(OnSettingChanged);
            _chatEnabledToggle.RegisterValueChangedCallback(OnSettingChanged);
            _chatPolicyDropdown.RegisterValueChangedCallback(OnSettingChanged);
        }
        
        public void SetGuild(GuildData guild, GuildMember playerMember)
        {
            _currentGuild = guild;
            _playerMember = playerMember;
            
            // Update field values
            _joinPolicyDropdown.SetValueWithoutNotify(guild.settings.joinPolicy.ToString());
            _minimumLevelField.SetValueWithoutNotify(guild.settings.minimumLevel);
            _minimumPowerField.SetValueWithoutNotify(guild.settings.minimumPower);
            _allowInvitesToggle.SetValueWithoutNotify(guild.settings.allowInvites);
            _chatEnabledToggle.SetValueWithoutNotify(guild.settings.chatEnabled);
            _chatPolicyDropdown.SetValueWithoutNotify(guild.settings.chatPolicy.ToString());
            
            // Enable/disable fields based on permissions
            bool canManageSettings = playerMember.role != GuildRole.Member;
            
            _joinPolicyDropdown.SetEnabled(canManageSettings);
            _minimumLevelField.SetEnabled(canManageSettings);
            _minimumPowerField.SetEnabled(canManageSettings);
            _allowInvitesToggle.SetEnabled(canManageSettings);
            _chatEnabledToggle.SetEnabled(canManageSettings);
            _chatPolicyDropdown.SetEnabled(canManageSettings);
        }
        
        private void OnSettingChanged<T>(ChangeEvent<T> evt)
        {
            if (_currentGuild == null || _playerMember?.role == GuildRole.Member)
                return;
            
            // Update settings object
            var settings = _currentGuild.settings;
            
            if (System.Enum.TryParse<GuildJoinPolicy>(_joinPolicyDropdown.value, out var joinPolicy))
                settings.joinPolicy = joinPolicy;
                
            settings.minimumLevel = _minimumLevelField.value;
            settings.minimumPower = _minimumPowerField.value;
            settings.allowInvites = _allowInvitesToggle.value;
            settings.chatEnabled = _chatEnabledToggle.value;
            
            if (System.Enum.TryParse<GuildChatPolicy>(_chatPolicyDropdown.value, out var chatPolicy))
                settings.chatPolicy = chatPolicy;
            
            OnSettingsChanged?.Invoke(settings);
        }
    }
}
