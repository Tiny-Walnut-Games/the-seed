#if UNITY_EDITOR
using System;
using TinyWalnutGames.TLDA.Editor.Unity.Editor;
using TinyWalnutGames.TLDA.Editor.Unity;

// 🔥 WARBLER CORE COMPATIBILITY - Explicit namespace alias to avoid ML-Agents conflicts
using UnityDebug = TinyWalnutGames.TLDA.Editor.Unity.Debug;

namespace TinyWalnutGames.TLDA.Editor
{
    /// <summary>
    /// Legacy TLDL Scribe Window (Kaiju Edition) – replaced by modular ScribeCore system.
    /// This thin wrapper exists ONLY for backward compatibility with existing menu items,
    /// reflection-based opens, and historical scripts calling TLDLScribeWindow.ShowWindow().
    /// </summary>
    [Obsolete("TLDLScribeWindow has been modularized. Use ScribeCore instead.")]
    public class TLDLScribeWindow : EditorWindow
    {
        const string LegacyNotice = "This is a legacy compatibility stub. The new modular ScribeCore window has been opened.";
        bool _openedNew;

        [MenuItem("Tools/Living Dev Agent/The Scribe")]        // preserved original entry
        public static void OpenScribe()
        {
            ScribeCore.OpenScribe();
        }

        [MenuItem("Tools/Living Dev Agent/TLDL Wizard (Deprecated)")] // preserved deprecated entry
        public static void OpenDeprecated()
        {
            ScribeCore.OpenScribe();
        }

        // Historical entry point
        public static void ShowWindow()
        {
            ScribeCore.OpenScribe();
        }

        public override void OnEnable()
        {
            // Immediately spawn the new window on enable
            TrySpawnNew();
        }

        public override void OnGUI()
        {
            // Safety net in case spawning failed earlier (domain reload timing, etc.)
            if (!_openedNew)
                TrySpawnNew();

            EditorGUILayout.HelpBox(LegacyNotice, MessageType.Info);
            if (GUILayout.Button("Open New Scribe Window"))
            {
                TrySpawnNew(true);
            }
        }

        void TrySpawnNew(bool force = false)
        {
            if (_openedNew && !force) return;
            try
            {
                ScribeCore.OpenScribe();
                _openedNew = true;
            }
            catch (Exception ex)
            {
                UnityDebug.LogError($"[TLDLScribeWindow Legacy] Failed to open ScribeCore: {ex}");
            }
        }
    }
}
#endif
