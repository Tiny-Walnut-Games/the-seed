using UnityEngine;
using UnityEngine.UIElements;
using MobileGameTemplate.Core; // 🔧 Unity 2022.3 Compatibility Bridge
using System.Collections.Generic;
using System.Linq; // 🔧 C# 10 Compatibility

namespace MobileGameTemplate.Systems
{
    /// <summary>
    /// 🏰 INTENDED EXPANSION ZONE - Guild system with roster and chat
    /// Social features for mobile games including guild management and communication
    /// Designed for community building in action mobile games
    /// 
    /// Sacred Vision: Transform solo gaming into collaborative guild adventures!
    /// </summary>
    public class GuildSystem : VisualElement
    {
        #region USS Class Names
        public static readonly string UssClassName = "guild-system";
        public static readonly string TabUssClassName = UssClassName + "__tab";
        public static readonly string TabActiveUssClassName = TabUssClassName + "--active";
        public static readonly string ContentUssClassName = UssClassName + "__content";
        public static readonly string RosterUssClassName = UssClassName + "__roster";
        public static readonly string ChatUssClassName = UssClassName + "__chat";
        public static readonly string InfoUssClassName = UssClassName + "__info";
        #endregion
        
        #region Events
        public System.Action<GuildData> OnGuildJoined;
        public System.Action OnGuildLeft;
        public System.Action<GuildMember> OnMemberPromoted;
        public System.Action<GuildMember> OnMemberKicked;
        public System.Action<string> OnChatMessageSent;
        public System.Action<GuildInvite> OnInviteSent;
        #endregion
        
        #region Private Fields
        private VisualElement _tabContainer;
        private VisualElement _contentContainer;
        
        // Tabs
        private Button _infoTab;
        private Button _rosterTab;
        private Button _chatTab;
        private Button _settingsTab;
        
        // Content panels
        private GuildInfoPanel _infoPanel;
        private GuildRosterPanel _rosterPanel;
        private GuildChatPanel _chatPanel;
        private GuildSettingsPanel _settingsPanel;
        
        private GuildData _currentGuild;
        private GuildMember _playerMember;
        private GuildTab _activeTab = GuildTab.Info;
        #endregion
        
        #region Constructor
        public GuildSystem()
        {
            AddToClassList(UssClassName);
            SetupGuildStructure();
            SetupTabs();
            SetupContentPanels();
            RegisterCallbacks();
            ShowNoGuildState();
        }
        #endregion
        
        #region Public API
        
        /// <summary>
        /// 🏰 Initialize guild system with current guild data
        /// </summary>
        public void InitializeGuild(GuildData guild, GuildMember playerMember)
        {
            _currentGuild = guild;
            _playerMember = playerMember;
            
            if (guild != null)
            {
                ShowGuildContent();
                RefreshAllPanels();
            }
            else
            {
                ShowNoGuildState();
            }
        }
        
        /// <summary>
        /// 🏰 Join a guild
        /// </summary>
        public void JoinGuild(GuildData guild, GuildMember playerMember)
        {
            _currentGuild = guild;
            _playerMember = playerMember;
            ShowGuildContent();
            RefreshAllPanels();
            OnGuildJoined?.Invoke(guild);
        }
        
        /// <summary>
        /// 🏰 Leave current guild
        /// </summary>
        public void LeaveGuild()
        {
            _currentGuild = null;
            _playerMember = null;
            ShowNoGuildState();
            OnGuildLeft?.Invoke();
        }
        
        /// <summary>
        /// 🏰 Update guild data
        /// </summary>
        public void UpdateGuild(GuildData updatedGuild)
        {
            _currentGuild = updatedGuild;
            RefreshAllPanels();
        }
        
        /// <summary>
        /// 🏰 Add chat message
        /// </summary>
        public void AddChatMessage(ChatMessage message)
        {
            _chatPanel?.AddMessage(message);
        }
        
        /// <summary>
        /// 🏰 Switch to specific tab
        /// </summary>
        public void SwitchToTab(GuildTab tab)
        {
            SetActiveTab(tab);
        }
        
        #endregion
        
        #region Private Methods
        
        /// <summary>
        /// 🏰 Setup main guild UI structure
        /// </summary>
        private void SetupGuildStructure()
        {
            style.width = Length.Percent(100);
            style.height = Length.Percent(100);
            style.flexDirection = FlexDirection.Column;
            
            // Tab container
            _tabContainer = new VisualElement();
            _tabContainer.style.flexDirection = FlexDirection.Row;
            _tabContainer.style.height = 50;
            _tabContainer.style.backgroundColor = new Color(0.1f, 0.1f, 0.1f, 0.9f);
            _tabContainer.style.borderBottomWidth = 2;
            _tabContainer.style.borderBottomColor = new Color(0.3f, 0.3f, 0.3f, 0.8f);
            
            // Content container
            _contentContainer = new VisualElement();
            _contentContainer.AddToClassList(ContentUssClassName);
            _contentContainer.style.flexGrow = 1;
            _contentContainer.style.paddingTop = 8;
            _contentContainer.style.paddingBottom = 8;
            _contentContainer.style.paddingLeft = 8;
            _contentContainer.style.paddingRight = 8;
            
            Add(_tabContainer);
            Add(_contentContainer);
        }
        
        /// <summary>
        /// 🏰 Setup tab navigation
        /// </summary>
        private void SetupTabs()
        {
            _infoTab = CreateTab("Info", GuildTab.Info);
            _rosterTab = CreateTab("Roster", GuildTab.Roster);
            _chatTab = CreateTab("Chat", GuildTab.Chat);
            _settingsTab = CreateTab("Settings", GuildTab.Settings);
            
            _tabContainer.Add(_infoTab);
            _tabContainer.Add(_rosterTab);
            _tabContainer.Add(_chatTab);
            _tabContainer.Add(_settingsTab);
            
            SetActiveTab(GuildTab.Info);
        }
        
        /// <summary>
        /// 🏰 Create individual tab button
        /// </summary>
        private Button CreateTab(string label, GuildTab tab)
        {
            var button = new Button(() => SetActiveTab(tab));
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
        /// 🏰 Setup content panels for each tab
        /// </summary>
        private void SetupContentPanels()
        {
            _infoPanel = new GuildInfoPanel();
            _infoPanel.OnJoinRequested += HandleJoinRequest;
            _infoPanel.OnCreateRequested += HandleCreateRequest;
            
            _rosterPanel = new GuildRosterPanel();
            _rosterPanel.OnMemberPromoted += (member) => OnMemberPromoted?.Invoke(member);
            _rosterPanel.OnMemberKicked += (member) => OnMemberKicked?.Invoke(member);
            _rosterPanel.OnInviteSent += (invite) => OnInviteSent?.Invoke(invite);
            
            _chatPanel = new GuildChatPanel();
            _chatPanel.OnMessageSent += (message) => OnChatMessageSent?.Invoke(message);
            
            _settingsPanel = new GuildSettingsPanel();
            _settingsPanel.OnLeaveRequested += LeaveGuild;
            _settingsPanel.OnSettingsChanged += HandleSettingsChanged;
            
            _contentContainer.Add(_infoPanel);
            _contentContainer.Add(_rosterPanel);
            _contentContainer.Add(_chatPanel);
            _contentContainer.Add(_settingsPanel);
        }
        
        /// <summary>
        /// 🏰 Register UI event callbacks
        /// </summary>
        private void RegisterCallbacks()
        {
            // Tab callbacks are registered in CreateTab method
        }
        
        /// <summary>
        /// 🏰 Set active tab and show corresponding content
        /// </summary>
        private void SetActiveTab(GuildTab tab)
        {
            // Update tab visual states
            _infoTab.RemoveFromClassList(TabActiveUssClassName);
            _rosterTab.RemoveFromClassList(TabActiveUssClassName);
            _chatTab.RemoveFromClassList(TabActiveUssClassName);
            _settingsTab.RemoveFromClassList(TabActiveUssClassName);
            
            // Hide all panels
            _infoPanel.style.display = DisplayStyle.None;
            _rosterPanel.style.display = DisplayStyle.None;
            _chatPanel.style.display = DisplayStyle.None;
            _settingsPanel.style.display = DisplayStyle.None;
            
            // Show selected tab and panel
            _activeTab = tab;
            
            switch (tab)
            {
                case GuildTab.Info:
                    _infoTab.AddToClassList(TabActiveUssClassName);
                    _infoPanel.style.display = DisplayStyle.Flex;
                    break;
                case GuildTab.Roster:
                    _rosterTab.AddToClassList(TabActiveUssClassName);
                    _rosterPanel.style.display = DisplayStyle.Flex;
                    break;
                case GuildTab.Chat:
                    _chatTab.AddToClassList(TabActiveUssClassName);
                    _chatPanel.style.display = DisplayStyle.Flex;
                    break;
                case GuildTab.Settings:
                    _settingsTab.AddToClassList(TabActiveUssClassName);
                    _settingsPanel.style.display = DisplayStyle.Flex;
                    break;
            }
            
            // Update tab button styles
            UpdateTabStyles();
        }
        
        /// <summary>
        /// 🏰 Update visual styles for active/inactive tabs
        /// </summary>
        private void UpdateTabStyles()
        {
            var tabs = new[] { _infoTab, _rosterTab, _chatTab, _settingsTab };
            
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
        /// 🏰 Show guild content when player is in a guild
        /// </summary>
        private void ShowGuildContent()
        {
            _tabContainer.style.display = DisplayStyle.Flex;
            _contentContainer.style.display = DisplayStyle.Flex;
        }
        
        /// <summary>
        /// 🏰 Show no guild state when player is not in a guild
        /// </summary>
        private void ShowNoGuildState()
        {
            _tabContainer.style.display = DisplayStyle.None;
            _contentContainer.Clear();
            
            var noGuildPanel = new VisualElement();
            noGuildPanel.style.alignItems = Align.Center;
            noGuildPanel.style.justifyContent = Justify.Center;
            noGuildPanel.style.flexGrow = 1;
            
            var titleLabel = new Label("No Guild");
            titleLabel.style.fontSize = 24;
            titleLabel.style.color = Color.white;
            titleLabel.style.marginBottom = 16;
            
            var descLabel = new Label("Join or create a guild to unlock social features");
            descLabel.style.fontSize = 14;
            descLabel.style.color = new Color(0.7f, 0.7f, 0.7f, 1f);
            descLabel.style.marginBottom = 32;
            descLabel.style.unityTextAlign = TextAnchor.MiddleCenter;
            
            var buttonContainer = new VisualElement();
            buttonContainer.style.flexDirection = FlexDirection.Row;
            buttonContainer.style.justifyContent = Justify.Center;
            
            var joinButton = new Button(() => HandleJoinRequest());
            joinButton.text = "JOIN GUILD";
            joinButton.style.marginRight = 8;
            joinButton.style.paddingLeft = 20;
            joinButton.style.paddingRight = 20;
            joinButton.style.paddingTop = 12;
            joinButton.style.paddingBottom = 12;
            joinButton.style.backgroundColor = new Color(0.3f, 0.7f, 0.3f, 0.9f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
// 🔧 LEGENDARY FIX: borderWidth not available in Unity 2022.3
            joinButton.style.color = Color.white;
            
            var createButton = new Button(() => HandleCreateRequest());
            createButton.text = "CREATE GUILD";
            createButton.style.marginLeft = 8;
            createButton.style.paddingLeft = 20;
            createButton.style.paddingRight = 20;
            createButton.style.paddingTop = 12;
            createButton.style.paddingBottom = 12;
            createButton.style.backgroundColor = new Color(0.3f, 0.5f, 0.7f, 0.9f);
// 🔧 LEGENDARY FIX: borderRadius not available in Unity 2022.3
// 🔧 LEGENDARY FIX: borderWidth not available in Unity 2022.3
            createButton.style.color = Color.white;
            
            buttonContainer.Add(joinButton);
            buttonContainer.Add(createButton);
            
            noGuildPanel.Add(titleLabel);
            noGuildPanel.Add(descLabel);
            noGuildPanel.Add(buttonContainer);
            
            _contentContainer.Add(noGuildPanel);
        }
        
        /// <summary>
        /// 🏰 Refresh all panel data
        /// </summary>
        private void RefreshAllPanels()
        {
            if (_currentGuild == null) return;
            
            _infoPanel.SetGuild(_currentGuild);
            _rosterPanel.SetGuild(_currentGuild, _playerMember);
            _chatPanel.SetGuild(_currentGuild);
            _settingsPanel.SetGuild(_currentGuild, _playerMember);
        }
        
        #endregion
        
        #region Event Handlers
        
        private void HandleJoinRequest()
        {
            // This would typically open a guild search/browser dialog
            Debug.Log("🏰 Guild join requested - implement guild browser");
        }
        
        private void HandleCreateRequest()
        {
            // This would typically open a guild creation dialog
            Debug.Log("🏰 Guild creation requested - implement guild creation form");
        }
        
        private void HandleSettingsChanged(GuildSettings settings)
        {
            if (_currentGuild != null)
            {
                _currentGuild.settings = settings;
                RefreshAllPanels();
            }
        }
        
        #endregion
        
        #region Factory Methods
        
        public new class UxmlFactory : UxmlFactory<GuildSystem, UxmlTraits> { }
        
        public new class UxmlTraits : VisualElement.UxmlTraits
        {
            public override void Init(VisualElement ve, IUxmlAttributes bag, CreationContext cc)
            {
                base.Init(ve, bag, cc);
            }
        }
        
        #endregion
    }
    
    public enum GuildTab
    {
        Info = 0,
        Roster = 1,
        Chat = 2,
        Settings = 3
    }
}

/// <summary>
/// Data structures for guild system
/// </summary>
[System.Serializable]
public class GuildData
{
    [Header("Guild Identity")]
    public string guildId = "";
    public string guildName = "Guild";
    public string guildTag = "GUILD";
    public string description = "";
    public Sprite guildEmblem;
    
    [Header("Guild Stats")]
    public int level = 1;
    public int experience = 0;
    public int memberCount = 1;
    public int maxMembers = 30;
    public System.DateTime createdDate = System.DateTime.Now;
    
    [Header("Guild Members")]
    public List<GuildMember> members = new List<GuildMember>();
    
    [Header("Guild Settings")]
    public GuildSettings settings = new GuildSettings();
    
    [Header("Guild Activities")]
    public List<GuildActivity> recentActivities = new List<GuildActivity>();
    public List<ChatMessage> chatHistory = new List<ChatMessage>();
}

[System.Serializable]
public class GuildMember
{
    public string playerId = "";
    public string playerName = "Player";
    public GuildRole role = GuildRole.Member;
    public int level = 1;
    public int powerRating = 1000;
    public System.DateTime joinDate = System.DateTime.Now;
    public System.DateTime lastOnline = System.DateTime.Now;
    public bool isOnline = false;
    public int contributionPoints = 0;
}

[System.Serializable]
public class GuildSettings
{
    public GuildJoinPolicy joinPolicy = GuildJoinPolicy.Open;
    public int minimumLevel = 1;
    public int minimumPower = 0;
    public bool allowInvites = true;
    public bool chatEnabled = true;
    public GuildChatPolicy chatPolicy = GuildChatPolicy.All;
}

[System.Serializable]
public class GuildActivity
{
    public string activityId = "";
    public GuildActivityType type = GuildActivityType.MemberJoined;
    public string description = "";
    public string playerId = "";
    public string playerName = "";
    public System.DateTime timestamp = System.DateTime.Now;
}

[System.Serializable]
public class ChatMessage
{
    public string messageId = "";
    public string senderId = "";
    public string senderName = "";
    public string content = "";
    public ChatMessageType type = ChatMessageType.Normal;
    public System.DateTime timestamp = System.DateTime.Now;
}

[System.Serializable]
public class GuildInvite
{
    public string inviteId = "";
    public string guildId = "";
    public string guildName = "";
    public string senderId = "";
    public string senderName = "";
    public string targetPlayerId = "";
    public string targetPlayerName = "";
    public System.DateTime expiryDate = System.DateTime.Now.AddDays(7);
}

public enum GuildRole
{
    Member = 0,
    Officer = 1,
    Leader = 2
}

public enum GuildJoinPolicy
{
    Open = 0,
    Approval = 1,
    InviteOnly = 2,
    Closed = 3
}

public enum GuildChatPolicy
{
    All = 0,
    OfficersOnly = 1,
    LeaderOnly = 2,
    Disabled = 3
}

public enum GuildActivityType
{
    MemberJoined = 0,
    MemberLeft = 1,
    MemberPromoted = 2,
    MemberDemoted = 3,
    GuildLevelUp = 4,
    Achievement = 5
}

public enum ChatMessageType
{
    Normal = 0,
    System = 1,
    Achievement = 2,
    Welcome = 3
}
