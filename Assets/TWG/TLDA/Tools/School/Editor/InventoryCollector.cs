using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEngine;
using UnityEditor;

namespace TWG.TLDA.School.Editor
{
    /// <summary>
    /// Unity Editor window for School experiment inventory collection
    /// KeeperNote: Stage 0 - Inventory collector for faculty surfaces enumeration
    /// </summary>
    public class InventoryCollector : EditorWindow
    {
        private Vector2 scrollPosition;
        private InventoryData lastInventory;
        private bool isScanning = false;
        private string scanProgress = "";
        private DateTime lastScanTime;
        
        // Output settings
        private const string OUTPUT_PATH = "assets/experiments/school/inventory.json";
        
        [MenuItem("Tools/School/Generate Inventory")]
        public static void ShowWindow()
        {
            var window = GetWindow<InventoryCollector>("School Inventory");
            window.minSize = new Vector2(500, 600);
            window.Show();
        }
        
        private void OnGUI()
        {
            scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
            
            DrawHeader();
            DrawScanSection();
            DrawResultsSection();
            DrawOutputSection();
            
            EditorGUILayout.EndScrollView();
        }
        
        private void DrawHeader()
        {
            EditorGUILayout.Space();
            
            var headerStyle = new GUIStyle(EditorStyles.boldLabel)
            {
                fontSize = 18,
                alignment = TextAnchor.MiddleCenter
            };
            
            EditorGUILayout.LabelField("🏫 School Experiment - Stage 0", headerStyle);
            EditorGUILayout.LabelField("Faculty Surfaces Inventory Collector", EditorStyles.centeredGreyMiniLabel);
            
            EditorGUILayout.Space();
            EditorGUILayout.Separator();
        }
        
        private void DrawScanSection()
        {
            EditorGUILayout.LabelField("📊 Asset Discovery", EditorStyles.boldLabel);
            
            EditorGUI.BeginDisabledGroup(isScanning);
            
            if (GUILayout.Button("🔍 Scan Faculty Surfaces", GUILayout.Height(30)))
            {
                GenerateInventory();
            }
            
            EditorGUI.EndDisabledGroup();
            
            if (isScanning)
            {
                EditorGUILayout.HelpBox($"Scanning... {scanProgress}", MessageType.Info);
                EditorUtility.DisplayProgressBar("Faculty Surface Scan", scanProgress, 0.5f);
            }
            
            if (lastScanTime != default)
            {
                EditorGUILayout.LabelField($"Last scan: {lastScanTime:yyyy-MM-dd HH:mm:ss}");
            }
            
            EditorGUILayout.Space();
        }
        
        private void DrawResultsSection()
        {
            if (lastInventory == null) return;
            
            EditorGUILayout.LabelField("📋 Inventory Results", EditorStyles.boldLabel);
            
            EditorGUILayout.LabelField($"Total Faculty Surfaces: {lastInventory.FacultySurfaces.Count}");
            EditorGUILayout.LabelField($"Inventory Hash: {lastInventory.Hash}");
            EditorGUILayout.LabelField($"Generated: {lastInventory.Timestamp}");
            
            EditorGUILayout.Space();
            
            // Surface type breakdown
            EditorGUILayout.LabelField("📈 Surface Type Breakdown", EditorStyles.boldLabel);
            
            var typeGroups = lastInventory.FacultySurfaces.GroupBy(s => s.Type).ToList();
            foreach (var group in typeGroups)
            {
                EditorGUILayout.LabelField($"  {group.Key}: {group.Count()}");
            }
            
            EditorGUILayout.Space();
            
            // Faculty surfaces list
            EditorGUILayout.LabelField("📝 Faculty Surfaces", EditorStyles.boldLabel);
            
            foreach (var surface in lastInventory.FacultySurfaces.Take(10))
            {
                EditorGUILayout.BeginHorizontal();
                EditorGUILayout.LabelField($"  {surface.Type}", GUILayout.Width(80));
                EditorGUILayout.LabelField(surface.Path, EditorStyles.miniLabel);
                EditorGUILayout.EndHorizontal();
            }
            
            if (lastInventory.FacultySurfaces.Count > 10)
            {
                EditorGUILayout.LabelField($"  ... and {lastInventory.FacultySurfaces.Count - 10} more");
            }
            
            EditorGUILayout.Space();
        }
        
        private void DrawOutputSection()
        {
            EditorGUILayout.LabelField("💾 Output", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginHorizontal();
            EditorGUILayout.LabelField($"Output Path: {OUTPUT_PATH}");
            if (GUILayout.Button("📂 Show", GUILayout.Width(60)))
            {
                EditorUtility.RevealInFinder(Path.GetFullPath(OUTPUT_PATH));
            }
            EditorGUILayout.EndHorizontal();
            
            var outputExists = File.Exists(OUTPUT_PATH);
            if (outputExists)
            {
                var fileInfo = new FileInfo(OUTPUT_PATH);
                EditorGUILayout.LabelField($"File size: {fileInfo.Length} bytes");
                EditorGUILayout.LabelField($"Modified: {fileInfo.LastWriteTime:yyyy-MM-dd HH:mm:ss}");
            }
            else
            {
                EditorGUILayout.HelpBox("Output file not found. Run inventory scan to generate.", MessageType.Warning);
            }
        }
        
        /// <summary>
        /// Main inventory generation method - scans repo for faculty surfaces
        /// </summary>
        public static void GenerateInventory()
        {
            var window = GetWindow<InventoryCollector>();
            window.PerformInventoryScan();
        }
        
        private async void PerformInventoryScan()
        {
            try
            {
                isScanning = true;
                scanProgress = "Initializing...";
                Repaint();
                
                var inventory = new InventoryData
                {
                    Timestamp = DateTime.UtcNow.ToString("O"),
                    UnityVersion = Application.unityVersion,
                    ProjectPath = Application.dataPath,
                    FacultySurfaces = new List<FacultySurface>()
                };
                
                // Scan Unity assets using AssetDatabase
                await ScanUnityAssets(inventory);
                
                // Scan scripts and code files
                await ScanScriptFiles(inventory);
                
                // Scan prefabs and ScriptableObjects
                await ScanPrefabsAndData(inventory);
                
                // Calculate hash
                scanProgress = "Calculating hash...";
                Repaint();
                
                inventory.Hash = CalculateInventoryHash(inventory);
                
                // Save to JSON
                scanProgress = "Saving inventory...";
                Repaint();
                
                await SaveInventoryJson(inventory);
                
                lastInventory = inventory;
                lastScanTime = DateTime.Now;
                
                Debug.Log($"[InventoryCollector] Faculty surface inventory complete: {inventory.FacultySurfaces.Count} surfaces found");
                EditorUtility.DisplayDialog("Inventory Complete", 
                    $"Found {inventory.FacultySurfaces.Count} faculty surfaces.\nInventory saved to {OUTPUT_PATH}", 
                    "OK");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[InventoryCollector] Inventory scan failed: {ex.Message}");
                EditorUtility.DisplayDialog("Scan Failed", $"Inventory scan failed:\n{ex.Message}", "OK");
            }
            finally
            {
                isScanning = false;
                EditorUtility.ClearProgressBar();
                Repaint();
            }
        }
        
        private async System.Threading.Tasks.Task ScanUnityAssets(InventoryData inventory)
        {
            scanProgress = "Scanning Unity assets...";
            Repaint();
            
            // Find all assets in the project
            var assetGuids = AssetDatabase.FindAssets("", new[] { "Assets" });
            
            for (int i = 0; i < assetGuids.Length; i++)
            {
                var guid = assetGuids[i];
                var assetPath = AssetDatabase.GUIDToAssetPath(guid);
                var assetType = AssetDatabase.GetMainAssetTypeAtPath(assetPath);
                
                if (assetType == null) continue;
                
                // Determine if this is a faculty surface
                var surfaceType = ClassifyAsset(assetPath, assetType);
                if (surfaceType != null)
                {
                    var surface = new FacultySurface
                    {
                        Path = assetPath,
                        Type = surfaceType,
                        Guid = guid,
                        AssetType = assetType.Name,
                        FileSize = GetFileSize(assetPath),
                        LastModified = GetLastModified(assetPath)
                    };
                    
                    inventory.FacultySurfaces.Add(surface);
                }
                
                // Update progress every 100 assets
                if (i % 100 == 0)
                {
                    scanProgress = $"Scanning Unity assets... {i}/{assetGuids.Length}";
                    Repaint();
                    await System.Threading.Tasks.Task.Yield();
                }
            }
        }
        
        private async System.Threading.Tasks.Task ScanScriptFiles(InventoryData inventory)
        {
            scanProgress = "Scanning script files...";
            Repaint();
            
            var scriptPaths = Directory.GetFiles(Application.dataPath, "*.cs", SearchOption.AllDirectories);
            
            foreach (var scriptPath in scriptPaths)
            {
                var relativePath = "Assets" + scriptPath.Substring(Application.dataPath.Length);
                
                var surface = new FacultySurface
                {
                    Path = relativePath,
                    Type = "Script",
                    AssetType = "MonoScript",
                    FileSize = GetFileSize(scriptPath),
                    LastModified = GetLastModified(scriptPath)
                };
                
                // Check for special script types
                var content = File.ReadAllText(scriptPath);
                if (content.Contains("EditorWindow"))
                    surface.Tags.Add("EditorTool");
                if (content.Contains("MonoBehaviour"))
                    surface.Tags.Add("Component");
                if (content.Contains("ScriptableObject"))
                    surface.Tags.Add("DataAsset");
                
                inventory.FacultySurfaces.Add(surface);
            }
            
            await System.Threading.Tasks.Task.Yield();
        }
        
        private async System.Threading.Tasks.Task ScanPrefabsAndData(InventoryData inventory)
        {
            scanProgress = "Scanning prefabs and data assets...";
            Repaint();
            
            // Find prefabs
            var prefabGuids = AssetDatabase.FindAssets("t:Prefab");
            foreach (var guid in prefabGuids)
            {
                var assetPath = AssetDatabase.GUIDToAssetPath(guid);
                var surface = new FacultySurface
                {
                    Path = assetPath,
                    Type = "Prefab",
                    Guid = guid,
                    AssetType = "GameObject",
                    FileSize = GetFileSize(assetPath),
                    LastModified = GetLastModified(assetPath)
                };
                
                // Analyze prefab components
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(assetPath);
                if (prefab != null)
                {
                    var components = prefab.GetComponentsInChildren<Component>();
                    surface.Tags.Add($"Components:{components.Length}");
                }
                
                inventory.FacultySurfaces.Add(surface);
            }
            
            // Find ScriptableObjects
            var scriptableObjectGuids = AssetDatabase.FindAssets("t:ScriptableObject");
            foreach (var guid in scriptableObjectGuids)
            {
                var assetPath = AssetDatabase.GUIDToAssetPath(guid);
                var surface = new FacultySurface
                {
                    Path = assetPath,
                    Type = "ScriptableObject",
                    Guid = guid,
                    AssetType = "ScriptableObject",
                    FileSize = GetFileSize(assetPath),
                    LastModified = GetLastModified(assetPath)
                };
                
                inventory.FacultySurfaces.Add(surface);
            }
            
            await System.Threading.Tasks.Task.Yield();
        }
        
        private string ClassifyAsset(string assetPath, Type assetType)
        {
            if (assetType == typeof(GameObject)) return "Prefab";
            if (assetType.IsSubclassOf(typeof(ScriptableObject))) return "ScriptableObject";
            if (assetPath.EndsWith(".cs")) return "Script";
            if (assetPath.EndsWith(".shader")) return "Shader";
            if (assetPath.EndsWith(".mat")) return "Material";
            if (assetPath.EndsWith(".prefab")) return "Prefab";
            if (assetPath.EndsWith(".unity")) return "Scene";
            if (assetType == typeof(Texture2D)) return "Texture";
            if (assetType == typeof(AudioClip)) return "Audio";
            if (assetType == typeof(Mesh)) return "Mesh";
            
            return null; // Not a faculty surface
        }
        
        private long GetFileSize(string path)
        {
            try
            {
                var fullPath = path.StartsWith("Assets") ? 
                    Path.Combine(Application.dataPath, path.Substring(7)) : path;
                return new FileInfo(fullPath).Length;
            }
            catch
            {
                return 0;
            }
        }
        
        private string GetLastModified(string path)
        {
            try
            {
                var fullPath = path.StartsWith("Assets") ? 
                    Path.Combine(Application.dataPath, path.Substring(7)) : path;
                return File.GetLastWriteTime(fullPath).ToString("O");
            }
            catch
            {
                return DateTime.MinValue.ToString("O");
            }
        }
        
        private string CalculateInventoryHash(InventoryData inventory)
        {
            // Create deterministic hash from all faculty surfaces
            var hashData = new StringBuilder();
            
            foreach (var surface in inventory.FacultySurfaces.OrderBy(s => s.Path))
            {
                hashData.AppendLine($"{surface.Path}:{surface.Type}:{surface.FileSize}:{surface.LastModified}");
            }
            
            using (var sha256 = SHA256.Create())
            {
                var bytes = Encoding.UTF8.GetBytes(hashData.ToString());
                var hash = sha256.ComputeHash(bytes);
                return Convert.ToBase64String(hash);
            }
        }
        
        private async System.Threading.Tasks.Task SaveInventoryJson(InventoryData inventory)
        {
            var outputDir = Path.GetDirectoryName(OUTPUT_PATH);
            if (!Directory.Exists(outputDir))
            {
                Directory.CreateDirectory(outputDir);
            }
            
            var json = JsonUtility.ToJson(inventory, true);
            await File.WriteAllTextAsync(OUTPUT_PATH, json);
            
            Debug.Log($"[InventoryCollector] Inventory saved to {OUTPUT_PATH}");
        }
    }
    
    /// <summary>
    /// Data structure for inventory output
    /// </summary>
    [Serializable]
    public class InventoryData
    {
        public string Timestamp { get; set; }
        public string Hash { get; set; }
        public string UnityVersion { get; set; }
        public string ProjectPath { get; set; }
        public List<FacultySurface> FacultySurfaces { get; set; } = new List<FacultySurface>();
    }
    
    /// <summary>
    /// Individual faculty surface (asset, script, prefab, etc.)
    /// </summary>
    [Serializable]
    public class FacultySurface
    {
        public string Path { get; set; }
        public string Type { get; set; }
        public string Guid { get; set; }
        public string AssetType { get; set; }
        public long FileSize { get; set; }
        public string LastModified { get; set; }
        public List<string> Tags { get; set; } = new List<string>();
    }
}