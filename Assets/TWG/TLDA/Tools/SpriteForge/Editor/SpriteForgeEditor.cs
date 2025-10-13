using System;
using System.IO;
using UnityEngine;
using UnityEditor;

namespace TWG.TLDA.SpriteForge.Editor
{
    /// <summary>
    /// Unity Editor window for SpriteForge testing and manual generation
    /// KeeperNote: Interactive tool for testing sprite generation and NFT workflow
    /// </summary>
    public class SpriteForgeEditor : EditorWindow
    {
        private string testSeed = "test_seed_12345";
        private SpriteSpec currentSpec = new SpriteSpec();
        private SpriteGenerationResult lastResult;
        private Vector2 scrollPosition;
        
        // Preview settings
        private bool showPreview = true;
        private float previewScale = 4f;
        
        [MenuItem("Tools/TWG/TLDA/SpriteForge Editor")]
        public static void ShowWindow()
        {
            var window = GetWindow<SpriteForgeEditor>("SpriteForge");
            window.minSize = new Vector2(400, 600);
            window.Show();
        }
        
        private void OnEnable()
        {
            InitializeDefaultSpec();
        }
        
        private void InitializeDefaultSpec()
        {
            currentSpec = new SpriteSpec
            {
                Archetype = CreatureArchetype.Familiar,
                Genre = GenreStyle.Fantasy,
                Faculty = FacultyRole.None,
                Size = new Vector2Int(24, 24),
                Rarity = RarityTier.Common,
                TokenId = "TEST-001",
                Description = "Test creature for SpriteForge development"
            };
        }
        
        private void OnGUI()
        {
            scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
            
            DrawHeader();
            DrawSeedSection();
            DrawSpecificationSection();
            DrawGenerationSection();
            DrawPreviewSection();
            DrawResultsSection();
            DrawTestingSection();
            
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
            
            EditorGUILayout.LabelField("🎨 SpriteForge NFT Generator", headerStyle);
            EditorGUILayout.LabelField("Pixel-art creature and location sprite generation for TLDA", EditorStyles.centeredGreyMiniLabel);
            
            EditorGUILayout.Space();
            EditorGUILayout.Separator();
        }
        
        private void DrawSeedSection()
        {
            EditorGUILayout.LabelField("🌱 Generation Seed", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginHorizontal();
            testSeed = EditorGUILayout.TextField("Seed", testSeed);
            
            if (GUILayout.Button("Random", GUILayout.Width(80)))
            {
                testSeed = System.Guid.NewGuid().ToString("N")[..12];
            }
            
            if (GUILayout.Button("TLDA", GUILayout.Width(60)))
            {
                testSeed = GenerateTLDASeed();
            }
            EditorGUILayout.EndHorizontal();
            
            EditorGUILayout.HelpBox("Seed determines all sprite characteristics. Same seed = identical sprite.", MessageType.Info);
            EditorGUILayout.Space();
        }
        
        private void DrawSpecificationSection()
        {
            EditorGUILayout.LabelField("⚙️ Sprite Specification", EditorStyles.boldLabel);
            
            // Core properties
            currentSpec.Archetype = (CreatureArchetype)EditorGUILayout.EnumPopup("Archetype", currentSpec.Archetype);
            currentSpec.Genre = (GenreStyle)EditorGUILayout.EnumPopup("Genre", currentSpec.Genre);
            currentSpec.Faculty = (FacultyRole)EditorGUILayout.EnumPopup("Faculty Role", currentSpec.Faculty);
            currentSpec.Rarity = (RarityTier)EditorGUILayout.EnumPopup("Rarity", currentSpec.Rarity);
            
            // Visual properties
            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Visual Properties", EditorStyles.miniBoldLabel);
            currentSpec.Size = EditorGUILayout.Vector2IntField("Sprite Size", currentSpec.Size);
            currentSpec.HasShaderEffects = EditorGUILayout.Toggle("Shader Effects", currentSpec.HasShaderEffects);
            
            // Evolution chain properties
            EditorGUILayout.Space();
            EditorGUILayout.LabelField("🧬 Evolution Chain", EditorStyles.miniBoldLabel);
            currentSpec.GenerateEvolutionChain = EditorGUILayout.Toggle("Generate Evolution Chain", currentSpec.GenerateEvolutionChain);
            
            if (currentSpec.GenerateEvolutionChain)
            {
                EditorGUILayout.HelpBox("Evolution chains create 6 stages (Egg → Hatchling → Juvenile → Adult → Elder → Legendary) in a grid layout.", MessageType.Info);
                
                currentSpec.FramesPerAnimation = EditorGUILayout.IntSlider("Frames Per Stage", currentSpec.FramesPerAnimation, 1, 12);
                
                EditorGUILayout.BeginHorizontal();
                EditorGUILayout.LabelField($"Total Grid Size: {currentSpec.FramesPerAnimation}×6", EditorStyles.miniLabel);
                EditorGUILayout.LabelField($"Sheet Size: {currentSpec.Size.x * currentSpec.FramesPerAnimation}×{currentSpec.Size.y * 6}", EditorStyles.miniLabel);
                EditorGUILayout.EndHorizontal();
                
                // Animation preview note
                if (currentSpec.FramesPerAnimation > 1)
                {
                    EditorGUILayout.HelpBox("🎬 Animated evolutions! Each stage gets smooth frame-by-frame animation.", MessageType.None);
                }
            }
            
            // Metadata
            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Metadata", EditorStyles.miniBoldLabel);
            currentSpec.TokenId = EditorGUILayout.TextField("Token ID", currentSpec.TokenId);
            currentSpec.Description = EditorGUILayout.TextArea(currentSpec.Description, GUILayout.Height(60));
            
            // Quick presets
            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Quick Presets", EditorStyles.miniBoldLabel);
            EditorGUILayout.BeginHorizontal();
            
            if (GUILayout.Button("Warbler 1/1"))
            {
                currentSpec = SpriteSpec.CreateFacultySpec(FacultyRole.Warbler, "FAC-WARBLER-001");
            }
            
            if (GUILayout.Button("Creator Apex"))
            {
                currentSpec = SpriteSpec.CreateFacultySpec(FacultyRole.Creator, "FAC-CREATOR-001");
            }
            
            if (GUILayout.Button("Fantasy Common"))
            {
                currentSpec = SpriteSpec.CreateGenreSpec(GenreStyle.Fantasy, CreatureArchetype.Familiar, RarityTier.Common);
                currentSpec.TokenId = "CRE-FANTASY-001";
            }
            
            if (GUILayout.Button("Cyberpunk Rare"))
            {
                currentSpec = SpriteSpec.CreateGenreSpec(GenreStyle.Cyberpunk, CreatureArchetype.Sentinel, RarityTier.Rare);
                currentSpec.TokenId = "CRE-CYBER-001";
            }
            
            EditorGUILayout.EndHorizontal();
            
            // Evolution chain presets
            EditorGUILayout.BeginHorizontal();
            
            if (GUILayout.Button("Evolution Chain"))
            {
                currentSpec = SpriteSpec.CreateEvolutionChainSpec(GenreStyle.Fantasy, CreatureArchetype.Familiar, RarityTier.Common);
                currentSpec.TokenId = "EVO-FAMILIAR-001";
            }
            
            if (GUILayout.Button("Animated Evolution"))
            {
                currentSpec = SpriteSpec.CreateAnimatedEvolutionSpec(GenreStyle.Cyberpunk, CreatureArchetype.Wisp, RarityTier.Rare);
                currentSpec.TokenId = "EVO-WISP-001";
            }
            
            if (GUILayout.Button("Reset Default"))
            {
                InitializeDefaultSpec();
            }
            
            EditorGUILayout.EndHorizontal();
            EditorGUILayout.Space();
        }
        
        private void DrawGenerationSection()
        {
            EditorGUILayout.LabelField("🎨 Generation", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginHorizontal();
            
            // Generate button
            var generateButtonStyle = new GUIStyle(GUI.skin.button)
            {
                fontSize = 14,
                fontStyle = FontStyle.Bold
            };
            
            if (GUILayout.Button("🎨 Generate Sprite", generateButtonStyle, GUILayout.Height(40)))
            {
                GenerateSprite();
            }
            
            // Clear button
            if (GUILayout.Button("Clear", GUILayout.Width(80), GUILayout.Height(40)))
            {
                ClearResults();
            }
            
            EditorGUILayout.EndHorizontal();
            
            // Generation status
            if (lastResult != null)
            {
                var statusMessage = lastResult.IsValid ? 
                    $"✅ Generated: {lastResult.TokenMetadata.name}" : 
                    "❌ Generation failed";
                var statusType = lastResult.IsValid ? MessageType.Info : MessageType.Error;
                
                EditorGUILayout.HelpBox(statusMessage, statusType);
            }
            
            EditorGUILayout.Space();
        }
        
        private void DrawPreviewSection()
        {
            if (lastResult == null || lastResult.SpriteSheet == null) return;
            
            EditorGUILayout.LabelField("🖼️ Preview", EditorStyles.boldLabel);
            
            showPreview = EditorGUILayout.Foldout(showPreview, "Show Sprite Preview");
            
            if (showPreview)
            {
                previewScale = EditorGUILayout.Slider("Preview Scale", previewScale, 1f, 8f);
                
                var spriteSize = new Vector2(lastResult.SpriteSheet.width, lastResult.SpriteSheet.height);
                var previewSize = spriteSize * previewScale;
                
                var rect = GUILayoutUtility.GetRect(previewSize.x, previewSize.y);
                rect.x = (EditorGUIUtility.currentViewWidth - previewSize.x) / 2; // Center
                
                // Draw sprite with pixel-perfect scaling
                var oldFilter = lastResult.SpriteSheet.filterMode;
                lastResult.SpriteSheet.filterMode = FilterMode.Point;
                GUI.DrawTexture(rect, lastResult.SpriteSheet, ScaleMode.ScaleToFit, false);
                lastResult.SpriteSheet.filterMode = oldFilter;
                
                // Frame breakdown
                EditorGUILayout.LabelField($"Frames: {lastResult.AnimationData.FrameRects.Length}", EditorStyles.miniLabel);
                EditorGUILayout.LabelField($"Size: {lastResult.SpriteSheet.width}x{lastResult.SpriteSheet.height}px", EditorStyles.miniLabel);
            }
            
            EditorGUILayout.Space();
        }
        
        private void DrawResultsSection()
        {
            if (lastResult == null) return;
            
            EditorGUILayout.LabelField("📊 Generation Results", EditorStyles.boldLabel);
            
            // Metadata summary
            if (lastResult.TokenMetadata != null)
            {
                EditorGUILayout.LabelField("Token Name", lastResult.TokenMetadata.name);
                EditorGUILayout.LabelField("Description", lastResult.TokenMetadata.description, EditorStyles.wordWrappedLabel);
                
                if (lastResult.TokenMetadata.attributes != null)
                {
                    EditorGUILayout.LabelField($"Attributes: {lastResult.TokenMetadata.attributes.Length}");
                    
                    EditorGUILayout.BeginVertical("box");
                    foreach (var attr in lastResult.TokenMetadata.attributes)
                    {
                        EditorGUILayout.LabelField($"• {attr.trait_type}: {attr.value}", EditorStyles.miniLabel);
                    }
                    EditorGUILayout.EndVertical();
                }
            }
            
            // Technical info
            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Technical Details", EditorStyles.miniBoldLabel);
            EditorGUILayout.LabelField("Seed", lastResult.Seed);
            EditorGUILayout.LabelField("Provenance Hash", lastResult.ProvenanceHash);
            EditorGUILayout.LabelField("Generated", lastResult.GeneratedAt.ToString("yyyy-MM-dd HH:mm:ss UTC"));
            
            EditorGUILayout.Space();
        }
        
        private void DrawTestingSection()
        {
            EditorGUILayout.LabelField("🧪 Testing & Export", EditorStyles.boldLabel);
            
            EditorGUILayout.BeginHorizontal();
            
            if (GUILayout.Button("Save to Assets"))
            {
                SaveSpriteToAssets();
            }
            
            if (GUILayout.Button("Test TLDA Bridge"))
            {
                TestTLDABridge();
            }
            
            if (GUILayout.Button("Export Metadata"))
            {
                ExportMetadata();
            }
            
            EditorGUILayout.EndHorizontal();
            
            if (GUILayout.Button("🚀 Generate Faculty Collection"))
            {
                GenerateFacultyCollection();
            }
            
            EditorGUILayout.Space();
            EditorGUILayout.HelpBox("Use these tools to test the NFT generation pipeline and export assets.", MessageType.Info);
        }
        
        private void GenerateSprite()
        {
            try
            {
                EditorUtility.DisplayProgressBar("SpriteForge", "Generating sprite...", 0.5f);
                
                lastResult = SpriteGenerator.GenerateSprite(testSeed, currentSpec);
                
                if (lastResult != null && lastResult.IsValid)
                {
                    Debug.Log($"[SpriteForgeEditor] Generated sprite: {lastResult.TokenMetadata.name}");
                }
                else
                {
                    Debug.LogError("[SpriteForgeEditor] Sprite generation failed");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[SpriteForgeEditor] Exception during generation: {ex.Message}");
            }
            finally
            {
                EditorUtility.ClearProgressBar();
            }
        }
        
        private void ClearResults()
        {
            lastResult = null;
        }
        
        private string GenerateTLDASeed()
        {
            // Simulate a TLDA fragment hash
            var timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
            var source = "SpriteForgeEditor";
            var text = "Testing sprite generation from editor";
            
            var combined = $"{source}{text}{timestamp}";
            var hash = System.Security.Cryptography.SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(combined));
            return Convert.ToHexString(hash)[..16].ToLower();
        }
        
        private void SaveSpriteToAssets()
        {
            if (lastResult?.SpriteSheet == null)
            {
                EditorUtility.DisplayDialog("Error", "No sprite to save. Generate a sprite first.", "OK");
                return;
            }
            
            var path = EditorUtility.SaveFilePanel("Save Sprite Sheet", "Assets", $"{currentSpec.TokenId}_sprite", "png");
            if (string.IsNullOrEmpty(path)) return;
            
            try
            {
                var bytes = lastResult.SpriteSheet.EncodeToPNG();
                File.WriteAllBytes(path, bytes);
                AssetDatabase.Refresh();
                
                Debug.Log($"[SpriteForgeEditor] Saved sprite to: {path}");
                EditorUtility.DisplayDialog("Success", $"Sprite saved to:\n{path}", "OK");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[SpriteForgeEditor] Failed to save sprite: {ex.Message}");
                EditorUtility.DisplayDialog("Error", $"Failed to save sprite:\n{ex.Message}", "OK");
            }
        }
        
        private void TestTLDABridge()
        {
            if (lastResult == null)
            {
                EditorUtility.DisplayDialog("Error", "Generate a sprite first to test the bridge.", "OK");
                return;
            }
            
            try
            {
                // Create a mock TLDA ritual event
                var ritualEvent = new TLDARitualEvent
                {
                    Id = "TEST-RITUAL-001",
                    Source = "SpriteForgeEditor",
                    Text = "Testing TLDA bridge integration",
                    RitualType = "scroll_integrity",
                    EmotionalWeight = 0.75f,
                    Tags = new[] { "test", "editor", "sprite_generation" },
                    UnixMillis = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
                    ProvenanceHash = lastResult.ProvenanceHash
                };
                
                var result = TLDANFTBridge.ProcessRitual(ritualEvent);
                
                if (result.Success)
                {
                    Debug.Log($"[SpriteForgeEditor] TLDA bridge test successful: {result.LedgerEntry.Id}");
                    EditorUtility.DisplayDialog("Success", 
                        $"TLDA bridge test successful!\n\nToken: {result.MintData.TokenId}\nLedger: {result.LedgerEntry.Id}", 
                        "OK");
                }
                else
                {
                    Debug.LogError($"[SpriteForgeEditor] TLDA bridge test failed: {result.ErrorMessage}");
                    EditorUtility.DisplayDialog("Error", $"TLDA bridge test failed:\n{result.ErrorMessage}", "OK");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[SpriteForgeEditor] TLDA bridge exception: {ex.Message}");
                EditorUtility.DisplayDialog("Error", $"TLDA bridge exception:\n{ex.Message}", "OK");
            }
        }
        
        private void ExportMetadata()
        {
            if (lastResult?.TokenMetadata == null)
            {
                EditorUtility.DisplayDialog("Error", "No metadata to export. Generate a sprite first.", "OK");
                return;
            }
            
            var path = EditorUtility.SaveFilePanel("Export Metadata", "Assets", $"{currentSpec.TokenId}_metadata", "json");
            if (string.IsNullOrEmpty(path)) return;
            
            try
            {
                var json = JsonUtility.ToJson(lastResult.TokenMetadata, true);
                File.WriteAllText(path, json);
                
                Debug.Log($"[SpriteForgeEditor] Exported metadata to: {path}");
                EditorUtility.DisplayDialog("Success", $"Metadata exported to:\n{path}", "OK");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[SpriteForgeEditor] Failed to export metadata: {ex.Message}");
                EditorUtility.DisplayDialog("Error", $"Failed to export metadata:\n{ex.Message}", "OK");
            }
        }
        
        private void GenerateFacultyCollection()
        {
            var facultyRoles = new[]
            {
                FacultyRole.Warbler,
                FacultyRole.Creator,
                FacultyRole.Sentinel,
                FacultyRole.Archivist,
                FacultyRole.Wrangler,
                FacultyRole.Scribe,
                FacultyRole.Oracle,
                FacultyRole.Keeper
            };
            
            var outputDir = Path.Combine(Application.dataPath, "TWG/TLDA/Tools/SpriteForge/Generated/Faculty");
            Directory.CreateDirectory(outputDir);
            
            var results = new List<SpriteGenerationResult>();
            
            try
            {
                for (int i = 0; i < facultyRoles.Length; i++)
                {
                    var role = facultyRoles[i];
                    if (role == FacultyRole.None) continue;
                    
                    EditorUtility.DisplayProgressBar("Faculty Collection", $"Generating {role}...", (float)i / facultyRoles.Length);
                    
                    var seed = $"faculty_{role.ToString().ToLower()}_{DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()}";
                    var spec = SpriteSpec.CreateFacultySpec(role, $"FAC-{role.ToString().ToUpper()}-001");
                    
                    var result = SpriteGenerator.GenerateSprite(seed, spec);
                    if (result != null && result.IsValid)
                    {
                        results.Add(result);
                        
                        // Save assets
                        var tokenDir = Path.Combine(outputDir, role.ToString());
                        Directory.CreateDirectory(tokenDir);
                        
                        var spriteBytes = result.SpriteSheet.EncodeToPNG();
                        File.WriteAllBytes(Path.Combine(tokenDir, "sprite.png"), spriteBytes);
                        
                        var metadataJson = JsonUtility.ToJson(result.TokenMetadata, true);
                        File.WriteAllText(Path.Combine(tokenDir, "metadata.json"), metadataJson);
                    }
                }
                
                AssetDatabase.Refresh();
                
                Debug.Log($"[SpriteForgeEditor] Generated {results.Count} Faculty tokens");
                EditorUtility.DisplayDialog("Success", 
                    $"Generated {results.Count} Faculty 1/1 tokens!\n\nSaved to: {outputDir}", 
                    "OK");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[SpriteForgeEditor] Faculty collection generation failed: {ex.Message}");
                EditorUtility.DisplayDialog("Error", $"Faculty collection generation failed:\n{ex.Message}", "OK");
            }
            finally
            {
                EditorUtility.ClearProgressBar();
            }
        }
    }
}