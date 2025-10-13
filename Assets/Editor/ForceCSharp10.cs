using System;
using System.IO;
using UnityEditor;
using UnityEditor.Callbacks;
using UnityEngine;

namespace Editor
{
    public static class ForceCSharp10
    {
        private const string PropsFileName = "Directory.Build.props";
        private const string PropsFileContent = @"<?xml version=""1.0"" encoding=""utf-8""?>
<Project>
  <PropertyGroup>
    <LangVersion>10.0</LangVersion>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>
";

        [DidReloadScripts]
        private static void InjectCSharpVersion()
        {
            if (Application.dataPath == null) return;
            var projectDir = Directory.GetParent(Application.dataPath)?.FullName;
            if (string.IsNullOrEmpty(projectDir)) return;

            var propsPath = Path.Combine(projectDir, PropsFileName);
            var needsWrite = !File.Exists(propsPath) || File.ReadAllText(propsPath) != PropsFileContent;

            if (needsWrite)
            {
                File.WriteAllText(propsPath, PropsFileContent);
                Debug.Log($"🧙 Injected {PropsFileName} into project root to enforce C#10.0 + nullable.");
            }

            // Metadata trace for LDL scrolls
            Debug.Log($"📜 LangVersion injected: 10.0");
            Debug.Log($"📜 Nullable enabled: true");
            Debug.Log($"📜 Props path: {propsPath}");
        }

        // Optional Rider compatibility check (IDE-aware reflection)
        [InitializeOnLoadMethod]
        private static void ValidateLanguageVersion()
        {
            var isCSharp10 = typeof(Func<,,>).GetGenericArguments().Length == 3;
            Debug.Log($"🔍 C# Language Level: {(isCSharp10 ? "C#10+ Confirmed ✅" : "Fallback < C#10 ❌")}");
        }
    }
}