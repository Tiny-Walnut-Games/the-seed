using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEngine;

namespace TWG.TLDA.SpriteForge
{
    /// <summary>
    /// Core sprite generation engine
    /// KeeperNote: Deterministic pixel-art generation based on TLDA seeds
    /// </summary>
    public static class SpriteGenerator
    {
        private const int DefaultSpriteSize = 24;
        private const int FacultySpriteSize = 32;
        
        /// <summary>
        /// Generate a sprite from TLDA seed and specification
        /// KeeperNote: Main entry point for deterministic sprite generation
        /// </summary>
        public static SpriteGenerationResult GenerateSprite(string seed, SpriteSpec spec)
        {
            try
            {
                var random = CreateSeededRandom(seed);
                var result = new SpriteGenerationResult
                {
                    Seed = seed,
                    GeneratedAt = DateTime.UtcNow,
                    ProvenanceHash = GenerateProvenanceHash(seed, spec)
                };
                
                // Generate sprite sheet
                result.SpriteSheet = GenerateSpriteSheet(spec, random);
                
                // Generate animation data
                result.AnimationData = GenerateAnimationData(spec, random);
                
                // Generate NFT metadata
                result.TokenMetadata = GenerateNFTMetadata(spec, result.ProvenanceHash);
                
                // Set file paths (will be written by save system)
                result.SpriteSheetPath = $"Generated/Creatures/{spec.TokenId}/sheet.png";
                result.MetadataPath = $"Generated/Creatures/{spec.TokenId}/metadata.json";
                
                return result;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[SpriteGenerator] Failed to generate sprite: {ex.Message}");
                return null;
            }
        }
        
        /// <summary>
        /// Generate sprite sheet texture with all animation frames
        /// KeeperNote: Creates pixel-art using deterministic algorithms. Supports evolution chains.
        /// </summary>
        private static Texture2D GenerateSpriteSheet(SpriteSpec spec, System.Random random)
        {
            if (spec.GenerateEvolutionChain)
            {
                return GenerateEvolutionSpriteSheet(spec, random);
            }
            else
            {
                return GenerateStandardSpriteSheet(spec, random);
            }
        }
        
        /// <summary>
        /// Generate standard sprite sheet (original behavior)
        /// </summary>
        private static Texture2D GenerateStandardSpriteSheet(SpriteSpec spec, System.Random random)
        {
            var frameCount = GetFrameCount(spec);
            var frameSize = spec.Size;
            var sheetWidth = frameSize.x * frameCount;
            var sheetHeight = frameSize.y;
            
            var texture = new Texture2D(sheetWidth, sheetHeight, TextureFormat.RGBA32, false);
            texture.filterMode = FilterMode.Point; // Pixel-perfect
            
            // Generate each animation frame
            for (int frame = 0; frame < frameCount; frame++)
            {
                var frameTexture = GenerateFrame(spec, frame, random);
                CopyFrameToSheet(texture, frameTexture, frame, frameSize);
            }
            
            texture.Apply();
            return texture;
        }
        
        /// <summary>
        /// Generate evolution chain sprite sheet (6 stages × N frames per stage)
        /// KeeperNote: Each row represents one evolution stage with multiple animation frames
        /// </summary>
        private static Texture2D GenerateEvolutionSpriteSheet(SpriteSpec spec, System.Random random)
        {
            var stages = spec.EvolutionStages;
            var framesPerStage = spec.FramesPerAnimation;
            var frameSize = spec.Size;
            
            var sheetWidth = frameSize.x * framesPerStage;
            var sheetHeight = frameSize.y * stages.Length;
            
            var texture = new Texture2D(sheetWidth, sheetHeight, TextureFormat.RGBA32, false);
            texture.filterMode = FilterMode.Point; // Pixel-perfect
            
            // Generate each evolution stage (row)
            for (int stageIndex = 0; stageIndex < stages.Length; stageIndex++)
            {
                var stage = stages[stageIndex];
                
                // Generate frames for this evolution stage
                for (int frameIndex = 0; frameIndex < framesPerStage; frameIndex++)
                {
                    var frameTexture = GenerateEvolutionFrame(spec, stage, frameIndex, random);
                    CopyEvolutionFrameToSheet(texture, frameTexture, stageIndex, frameIndex, frameSize);
                }
            }
            
            texture.Apply();
            return texture;
        }
        
        /// <summary>
        /// Generate a single animation frame
        /// KeeperNote: Core pixel-art generation algorithm
        /// </summary>
        private static Texture2D GenerateFrame(SpriteSpec spec, int frameIndex, System.Random random)
        {
            var size = spec.Size;
            var texture = new Texture2D(size.x, size.y, TextureFormat.RGBA32, false);
            
            // Get genre-specific palette
            var palette = GetGenrePalette(spec.Genre, spec.Faculty);
            
            // Generate base silhouette
            var silhouette = GenerateSilhouette(spec.Archetype, size, random);
            
            // Apply genre styling
            ApplyGenreStyling(texture, silhouette, spec, palette, frameIndex, random);
            
            // Add Faculty-specific effects for ultra-rares
            if (spec.Faculty != FacultyRole.None)
            {
                ApplyFacultyEffects(texture, spec.Faculty, frameIndex, random);
            }
            
            texture.Apply();
            return texture;
        }
        
        /// <summary>
        /// Generate a single evolution frame
        /// KeeperNote: Creates pixel-art for specific evolution stage with animation
        /// </summary>
        private static Texture2D GenerateEvolutionFrame(SpriteSpec spec, EvolutionStage stage, int frameIndex, System.Random random)
        {
            var size = spec.Size;
            var texture = new Texture2D(size.x, size.y, TextureFormat.RGBA32, false);
            
            // Get genre-specific palette
            var palette = GetGenrePalette(spec.Genre, spec.Faculty);
            
            // Generate evolution-specific silhouette
            var silhouette = GenerateEvolutionSilhouette(spec.Archetype, stage, size, frameIndex, random);
            
            // Apply genre styling with evolution modifications
            ApplyEvolutionStyling(texture, silhouette, spec, stage, palette, frameIndex, random);
            
            // Add stage-specific effects
            ApplyEvolutionEffects(texture, stage, frameIndex, random);
            
            texture.Apply();
            return texture;
        }
        
        /// <summary>
        /// Copy evolution frame to the correct position in sprite sheet
        /// KeeperNote: Places frame at (stageIndex, frameIndex) in grid layout
        /// </summary>
        private static void CopyEvolutionFrameToSheet(Texture2D sheet, Texture2D frame, int stageIndex, int frameIndex, Vector2Int frameSize)
        {
            var startX = frameIndex * frameSize.x;
            var startY = stageIndex * frameSize.y;
            
            var pixels = frame.GetPixels();
            sheet.SetPixels(startX, startY, frameSize.x, frameSize.y, pixels);
        }
        
        /// <summary>
        /// Generate base creature silhouette
        /// KeeperNote: Creates the fundamental shape based on archetype
        /// </summary>
        private static bool[,] GenerateSilhouette(CreatureArchetype archetype, Vector2Int size, System.Random random)
        {
            var silhouette = new bool[size.x, size.y];
            var centerX = size.x / 2;
            var centerY = size.y / 2;
            
            switch (archetype)
            {
                case CreatureArchetype.Familiar:
                    GenerateFamiliarShape(silhouette, size, random);
                    break;
                    
                case CreatureArchetype.Wisp:
                    GenerateWispShape(silhouette, size, random);
                    break;
                    
                case CreatureArchetype.Golem:
                    GenerateGolemShape(silhouette, size, random);
                    break;
                    
                case CreatureArchetype.Sentinel:
                    GenerateSentinelShape(silhouette, size, random);
                    break;
                    
                default:
                    // Default to familiar shape
                    GenerateFamiliarShape(silhouette, size, random);
                    break;
            }
            
            return silhouette;
        }
        
        /// <summary>
        /// Generate small companion creature shape
        /// </summary>
        private static void GenerateFamiliarShape(bool[,] silhouette, Vector2Int size, System.Random random)
        {
            var width = size.x;
            var height = size.y;
            var centerX = width / 2;
            var centerY = height / 2;
            
            // Body (oval)
            for (int y = centerY - 3; y <= centerY + 2; y++)
            {
                for (int x = centerX - 2; x <= centerX + 2; x++)
                {
                    if (x >= 0 && x < width && y >= 0 && y < height)
                    {
                        silhouette[x, y] = true;
                    }
                }
            }
            
            // Head (smaller oval above body)
            for (int y = centerY + 3; y <= centerY + 5; y++)
            {
                for (int x = centerX - 1; x <= centerX + 1; x++)
                {
                    if (x >= 0 && x < width && y >= 0 && y < height)
                    {
                        silhouette[x, y] = true;
                    }
                }
            }
            
            // Ears (random chance)
            if (random.NextDouble() > 0.5)
            {
                if (centerY + 6 < height)
                {
                    if (centerX - 2 >= 0) silhouette[centerX - 2, centerY + 6] = true;
                    if (centerX + 2 < width) silhouette[centerX + 2, centerY + 6] = true;
                }
            }
        }
        
        /// <summary>
        /// Generate energy-based wisp shape
        /// </summary>
        private static void GenerateWispShape(bool[,] silhouette, Vector2Int size, System.Random random)
        {
            var width = size.x;
            var height = size.y;
            var centerX = width / 2;
            var centerY = height / 2;
            
            // Core energy ball
            var radius = Math.Min(width, height) / 4;
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    var dx = x - centerX;
                    var dy = y - centerY;
                    var distance = Math.Sqrt(dx * dx + dy * dy);
                    
                    if (distance <= radius + random.NextDouble() - 0.5)
                    {
                        silhouette[x, y] = true;
                    }
                }
            }
            
            // Energy trails
            for (int i = 0; i < 3; i++)
            {
                var angle = random.NextDouble() * Math.PI * 2;
                var trailLength = radius + random.Next(2, 5);
                
                for (int j = 1; j <= trailLength; j++)
                {
                    var x = centerX + (int)(Math.Cos(angle) * j);
                    var y = centerY + (int)(Math.Sin(angle) * j);
                    
                    if (x >= 0 && x < width && y >= 0 && y < height && random.NextDouble() > 0.3)
                    {
                        silhouette[x, y] = true;
                    }
                }
            }
        }
        
        /// <summary>
        /// Generate constructed golem shape
        /// </summary>
        private static void GenerateGolemShape(bool[,] silhouette, Vector2Int size, System.Random random)
        {
            var width = size.x;
            var height = size.y;
            var centerX = width / 2;
            
            // Rectangular body structure
            for (int y = 2; y < height - 2; y++)
            {
                for (int x = centerX - 3; x <= centerX + 3; x++)
                {
                    if (x >= 0 && x < width)
                    {
                        silhouette[x, y] = true;
                    }
                }
            }
            
            // Head block
            for (int y = height - 4; y < height; y++)
            {
                for (int x = centerX - 2; x <= centerX + 2; x++)
                {
                    if (x >= 0 && x < width && y >= 0)
                    {
                        silhouette[x, y] = true;
                    }
                }
            }
            
            // Arms (simple rectangles)
            var armY = height - 8;
            if (armY >= 0)
            {
                // Left arm
                if (centerX - 5 >= 0) silhouette[centerX - 5, armY] = true;
                if (centerX - 4 >= 0) silhouette[centerX - 4, armY] = true;
                
                // Right arm
                if (centerX + 4 < width) silhouette[centerX + 4, armY] = true;
                if (centerX + 5 < width) silhouette[centerX + 5, armY] = true;
            }
        }
        
        /// <summary>
        /// Generate guardian sentinel shape
        /// </summary>
        private static void GenerateSentinelShape(bool[,] silhouette, Vector2Int size, System.Random random)
        {
            var width = size.x;
            var height = size.y;
            var centerX = width / 2;
            
            // Tall, imposing figure
            for (int y = 1; y < height - 1; y++)
            {
                var bodyWidth = Math.Max(1, 4 - Math.Abs(y - height / 2) / 3);
                for (int x = centerX - bodyWidth; x <= centerX + bodyWidth; x++)
                {
                    if (x >= 0 && x < width)
                    {
                        silhouette[x, y] = true;
                    }
                }
            }
            
            // Cape/wings
            for (int y = height / 2; y < height - 2; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    if ((x < centerX - 4 || x > centerX + 4) && random.NextDouble() > 0.4)
                    {
                        silhouette[x, y] = true;
                    }
                }
            }
        }
        
        /// <summary>
        /// Apply genre-specific styling to the silhouette
        /// </summary>
        private static void ApplyGenreStyling(Texture2D texture, bool[,] silhouette, SpriteSpec spec, Color[] palette, int frameIndex, System.Random random)
        {
            var width = texture.width;
            var height = texture.height;
            
            // Clear texture
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    texture.SetPixel(x, y, Color.clear);
                }
            }
            
            // Apply base colors from silhouette
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    if (silhouette[x, y])
                    {
                        var colorIndex = random.Next(0, Math.Min(3, palette.Length)); // Use first 3 colors for base
                        var color = palette[colorIndex];
                        
                        // Add subtle animation variation
                        if (frameIndex > 0 && random.NextDouble() > 0.8)
                        {
                            color = Color.Lerp(color, palette[(colorIndex + 1) % palette.Length], 0.3f);
                        }
                        
                        texture.SetPixel(x, y, color);
                    }
                }
            }
            
            // Add genre-specific details
            ApplyGenreDetails(texture, spec.Genre, palette, frameIndex, random);
        }
        
        /// <summary>
        /// Add genre-specific visual details
        /// </summary>
        private static void ApplyGenreDetails(Texture2D texture, GenreStyle genre, Color[] palette, int frameIndex, System.Random random)
        {
            switch (genre)
            {
                case GenreStyle.SciFi:
                    ApplySciFiDetails(texture, palette, frameIndex, random);
                    break;
                case GenreStyle.Cyberpunk:
                    ApplyCyberpunkDetails(texture, palette, frameIndex, random);
                    break;
                case GenreStyle.Steampunk:
                    ApplySteampunkDetails(texture, palette, frameIndex, random);
                    break;
                case GenreStyle.Fantasy:
                    ApplyFantasyDetails(texture, palette, frameIndex, random);
                    break;
                case GenreStyle.Mythic:
                    ApplyMythicDetails(texture, palette, frameIndex, random);
                    break;
            }
        }
        
        /// <summary>
        /// Apply sci-fi technological details
        /// </summary>
        private static void ApplySciFiDetails(Texture2D texture, Color[] palette, int frameIndex, System.Random random)
        {
            var width = texture.width;
            var height = texture.height;
            var glowColor = palette.Length > 3 ? palette[3] : Color.cyan;
            
            // Add glowing circuits (simple lines)
            for (int i = 0; i < 3; i++)
            {
                var x = random.Next(0, width);
                var y = random.Next(0, height);
                
                if (texture.GetPixel(x, y).a > 0) // Only on existing pixels
                {
                    texture.SetPixel(x, y, Color.Lerp(texture.GetPixel(x, y), glowColor, 0.5f));
                }
            }
        }
        
        /// <summary>
        /// Apply cyberpunk neon details
        /// </summary>
        private static void ApplyCyberpunkDetails(Texture2D texture, Color[] palette, int frameIndex, System.Random random)
        {
            var width = texture.width;
            var height = texture.height;
            var neonColor = palette.Length > 4 ? palette[4] : Color.magenta;
            
            // Animated neon glow effect
            var pulseIntensity = 0.5f + 0.3f * Mathf.Sin(frameIndex * 0.5f);
            
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    var pixel = texture.GetPixel(x, y);
                    if (pixel.a > 0 && random.NextDouble() > 0.9)
                    {
                        var glowPixel = Color.Lerp(pixel, neonColor, pulseIntensity);
                        texture.SetPixel(x, y, glowPixel);
                    }
                }
            }
        }
        
        /// <summary>
        /// Apply steampunk brass and gear details
        /// </summary>
        private static void ApplySteampunkDetails(Texture2D texture, Color[] palette, int frameIndex, System.Random random)
        {
            var width = texture.width;
            var height = texture.height;
            var brassColor = palette.Length > 2 ? palette[2] : new Color(0.8f, 0.6f, 0.2f);
            
            // Add metallic highlights
            for (int i = 0; i < 5; i++)
            {
                var x = random.Next(0, width);
                var y = random.Next(0, height);
                
                if (texture.GetPixel(x, y).a > 0)
                {
                    texture.SetPixel(x, y, Color.Lerp(texture.GetPixel(x, y), brassColor, 0.3f));
                }
            }
        }
        
        /// <summary>
        /// Apply fantasy magical details
        /// </summary>
        private static void ApplyFantasyDetails(Texture2D texture, Color[] palette, int frameIndex, System.Random random)
        {
            var width = texture.width;
            var height = texture.height;
            var magicColor = palette.Length > 3 ? palette[3] : new Color(0.7f, 0.3f, 0.9f);
            
            // Subtle magical sparkles
            for (int i = 0; i < 2; i++)
            {
                var x = random.Next(0, width);
                var y = random.Next(0, height);
                
                if (random.NextDouble() > 0.8)
                {
                    texture.SetPixel(x, y, magicColor);
                }
            }
        }
        
        /// <summary>
        /// Apply mythic Faculty-specific details
        /// </summary>
        private static void ApplyMythicDetails(Texture2D texture, Color[] palette, int frameIndex, System.Random random)
        {
            var width = texture.width;
            var height = texture.height;
            var mythicColor = palette.Length > 4 ? palette[4] : new Color(1f, 0.9f, 0.3f, 0.8f);
            
            // Divine aura effect
            var auraIntensity = 0.3f + 0.2f * Mathf.Sin(frameIndex * 0.3f);
            
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    var pixel = texture.GetPixel(x, y);
                    if (pixel.a > 0)
                    {
                        var distance = Vector2.Distance(new Vector2(x, y), new Vector2(width / 2, height / 2));
                        var normalizedDistance = distance / (width / 2);
                        var auraAlpha = auraIntensity * (1f - normalizedDistance);
                        
                        if (auraAlpha > 0)
                        {
                            var auraPixel = Color.Lerp(pixel, mythicColor, auraAlpha);
                            texture.SetPixel(x, y, auraPixel);
                        }
                    }
                }
            }
        }
        
        /// <summary>
        /// Apply Faculty-specific special effects
        /// </summary>
        private static void ApplyFacultyEffects(Texture2D texture, FacultyRole faculty, int frameIndex, System.Random random)
        {
            switch (faculty)
            {
                case FacultyRole.Warbler:
                    ApplyWarblerEffects(texture, frameIndex, random);
                    break;
                case FacultyRole.Creator:
                    ApplyCreatorEffects(texture, frameIndex, random);
                    break;
                // Add other Faculty effects as needed
            }
        }
        
        /// <summary>
        /// Apply Warbler song and echo effects
        /// </summary>
        private static void ApplyWarblerEffects(Texture2D texture, int frameIndex, System.Random random)
        {
            var width = texture.width;
            var height = texture.height;
            var songColor = new Color(0.3f, 0.7f, 1f, 0.6f); // Well-blue
            
            // Animated sound waves
            var wavePhase = frameIndex * 0.4f;
            
            for (int x = 0; x < width; x++)
            {
                var wave = Mathf.Sin(x * 0.5f + wavePhase) * 2f;
                var y = (int)(height / 2 + wave);
                
                if (y >= 0 && y < height)
                {
                    texture.SetPixel(x, y, Color.Lerp(texture.GetPixel(x, y), songColor, 0.4f));
                }
            }
        }
        
        /// <summary>
        /// Apply Creator apex effects
        /// </summary>
        private static void ApplyCreatorEffects(Texture2D texture, int frameIndex, System.Random random)
        {
            var width = texture.width;
            var height = texture.height;
            var creatorColor = new Color(1f, 0.8f, 0f, 0.8f); // Golden
            
            // Multi-phase animation (idle → awaken → cast)
            var phase = (frameIndex / 8) % 3; // 8 frames per phase
            var phaseFrame = frameIndex % 8;
            
            switch (phase)
            {
                case 0: // Idle - subtle glow
                    ApplySubtleGlow(texture, creatorColor, 0.2f);
                    break;
                case 1: // Awaken - growing intensity
                    ApplySubtleGlow(texture, creatorColor, 0.2f + phaseFrame * 0.1f);
                    break;
                case 2: // Cast - full power burst
                    ApplyPowerBurst(texture, creatorColor, phaseFrame);
                    break;
            }
        }
        
        /// <summary>
        /// Apply subtle glow effect
        /// </summary>
        private static void ApplySubtleGlow(Texture2D texture, Color glowColor, float intensity)
        {
            var width = texture.width;
            var height = texture.height;
            var center = new Vector2(width / 2, height / 2);
            
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    var pixel = texture.GetPixel(x, y);
                    if (pixel.a > 0)
                    {
                        var distance = Vector2.Distance(new Vector2(x, y), center);
                        var normalizedDistance = distance / (width / 2);
                        var glowIntensity = intensity * (1f - normalizedDistance);
                        
                        if (glowIntensity > 0)
                        {
                            var glowPixel = Color.Lerp(pixel, glowColor, glowIntensity);
                            texture.SetPixel(x, y, glowPixel);
                        }
                    }
                }
            }
        }
        
        /// <summary>
        /// Apply power burst effect
        /// </summary>
        private static void ApplyPowerBurst(Texture2D texture, Color burstColor, int frameIndex)
        {
            var width = texture.width;
            var height = texture.height;
            var center = new Vector2(width / 2, height / 2);
            var burstRadius = frameIndex * 2f; // Expanding burst
            
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    var distance = Vector2.Distance(new Vector2(x, y), center);
                    
                    if (Math.Abs(distance - burstRadius) < 1.5f) // Ring effect
                    {
                        var burstIntensity = 1f - Math.Abs(distance - burstRadius) / 1.5f;
                        var currentPixel = texture.GetPixel(x, y);
                        var burstPixel = Color.Lerp(currentPixel, burstColor, burstIntensity * 0.8f);
                        texture.SetPixel(x, y, burstPixel);
                    }
                }
            }
        }
        
        /// <summary>
        /// Get genre-specific color palette
        /// </summary>
        private static Color[] GetGenrePalette(GenreStyle genre, FacultyRole faculty)
        {
            // Faculty override palettes
            if (faculty != FacultyRole.None)
            {
                return faculty switch
                {
                    FacultyRole.Warbler => new[] { 
                        new Color(0.2f, 0.4f, 0.8f), // Well-blue
                        new Color(0.1f, 0.6f, 0.9f), // Light blue
                        new Color(0.4f, 0.8f, 1f),   // Sky blue
                        new Color(0.3f, 0.7f, 1f, 0.6f) // Translucent blue
                    },
                    FacultyRole.Creator => new[] {
                        new Color(1f, 0.8f, 0f),     // Gold
                        new Color(0.9f, 0.7f, 0.1f), // Dark gold
                        new Color(1f, 0.9f, 0.3f),   // Light gold
                        new Color(1f, 1f, 0.8f),     // Pale gold
                        new Color(1f, 0.8f, 0f, 0.8f) // Translucent gold
                    },
                    _ => GetGenrePalette(GenreStyle.Mythic, FacultyRole.None)
                };
            }
            
            // Standard genre palettes
            return genre switch
            {
                GenreStyle.SciFi => new[] {
                    new Color(0.2f, 0.2f, 0.3f), // Dark gray
                    new Color(0.4f, 0.4f, 0.5f), // Medium gray
                    new Color(0.7f, 0.7f, 0.8f), // Light gray
                    new Color(0f, 1f, 1f),       // Cyan glow
                    new Color(0.5f, 0.8f, 1f)    // Blue glow
                },
                GenreStyle.Fantasy => new[] {
                    new Color(0.3f, 0.2f, 0.1f), // Brown
                    new Color(0.5f, 0.3f, 0.2f), // Light brown
                    new Color(0.2f, 0.4f, 0.2f), // Green
                    new Color(0.7f, 0.3f, 0.9f), // Purple magic
                    new Color(1f, 0.9f, 0.7f)    // Cream
                },
                GenreStyle.Steampunk => new[] {
                    new Color(0.4f, 0.3f, 0.2f), // Dark brass
                    new Color(0.6f, 0.4f, 0.2f), // Brass
                    new Color(0.8f, 0.6f, 0.2f), // Bright brass
                    new Color(0.3f, 0.2f, 0.1f), // Dark leather
                    new Color(0.9f, 0.8f, 0.6f)  // Steam white
                },
                GenreStyle.Cyberpunk => new[] {
                    new Color(0.1f, 0.1f, 0.1f), // Black
                    new Color(0.2f, 0.2f, 0.3f), // Dark blue
                    new Color(0.4f, 0.4f, 0.4f), // Gray
                    new Color(1f, 0f, 1f),       // Magenta neon
                    new Color(0f, 1f, 0.5f)      // Green neon
                },
                GenreStyle.Mythic => new[] {
                    new Color(0.9f, 0.9f, 1f),   // Pure white
                    new Color(0.8f, 0.8f, 0.9f), // Light gray
                    new Color(0.6f, 0.6f, 0.8f), // Blue-gray
                    new Color(1f, 0.9f, 0.3f),   // Divine gold
                    new Color(1f, 1f, 1f, 0.8f)  // Translucent white
                },
                _ => new[] {
                    Color.gray, Color.white, Color.black, Color.blue
                }
            };
        }
        
        /// <summary>
        /// Generate animation data for sprite sheets
        /// </summary>
        private static SpriteAnimationData GenerateAnimationData(SpriteSpec spec, System.Random random)
        {
            if (spec.GenerateEvolutionChain)
            {
                return GenerateEvolutionAnimationData(spec, random);
            }
            else
            {
                return GenerateStandardAnimationData(spec, random);
            }
        }
        
        /// <summary>
        /// Generate standard animation data (original behavior)
        /// </summary>
        private static SpriteAnimationData GenerateStandardAnimationData(SpriteSpec spec, System.Random random)
        {
            var frameCount = GetFrameCount(spec);
            var frameSize = spec.Size;
            
            return new SpriteAnimationData
            {
                AnimationType = spec.AnimationSets[0], // Primary animation
                FrameRects = GenerateFrameRects(frameCount, frameSize),
                FrameDurations = GenerateFrameDurations(frameCount, spec),
                Pivot = new Vector2(0.5f, 0f), // Bottom-center
                LoopAnimation = true
            };
        }
        
        /// <summary>
        /// Generate evolution chain animation data with per-stage frame definitions
        /// </summary>
        private static SpriteAnimationData GenerateEvolutionAnimationData(SpriteSpec spec, System.Random random)
        {
            var stages = spec.EvolutionStages;
            var framesPerStage = spec.FramesPerAnimation;
            var frameSize = spec.Size;
            var totalFrames = stages.Length * framesPerStage;
            
            var frameRects = new Rect[totalFrames];
            var frameDurations = new float[totalFrames];
            var baseDuration = 0.2f;
            
            // Generate frame rectangles for evolution grid layout
            for (int stageIndex = 0; stageIndex < stages.Length; stageIndex++)
            {
                for (int frameIndex = 0; frameIndex < framesPerStage; frameIndex++)
                {
                    var rectIndex = stageIndex * framesPerStage + frameIndex;
                    
                    frameRects[rectIndex] = new Rect(
                        frameIndex * frameSize.x,    // X position (column)
                        stageIndex * frameSize.y,    // Y position (row)
                        frameSize.x,                 // Width
                        frameSize.y                  // Height
                    );
                    
                    // Evolution stages have varying animation speeds
                    frameDurations[rectIndex] = stages[stageIndex] switch
                    {
                        EvolutionStage.Egg => 0.5f,        // Slow breathing
                        EvolutionStage.Hatchling => 0.3f,   // Moderate movement
                        EvolutionStage.Juvenile => 0.25f,   // Active movement
                        EvolutionStage.Adult => 0.2f,       // Standard speed
                        EvolutionStage.Elder => 0.15f,      // Graceful movement
                        EvolutionStage.Legendary => 0.1f,   // Majestic flow
                        _ => baseDuration
                    };
                }
            }
            
            return new SpriteAnimationData
            {
                AnimationType = AnimationSet.Idle, // Evolution chains use idle animation
                FrameRects = frameRects,
                FrameDurations = frameDurations,
                Pivot = new Vector2(0.5f, 0f), // Bottom-center
                LoopAnimation = true,
                EvolutionStages = stages.Select(s => s.ToString()).ToArray(),
                FramesPerStage = framesPerStage
            };
        }
        
        /// <summary>
        /// Generate NFT metadata
        /// </summary>
        private static NFTMetadata GenerateNFTMetadata(SpriteSpec spec, string provenanceHash)
        {
            var metadata = new NFTMetadata
            {
                name = GenerateTokenName(spec),
                description = GenerateTokenDescription(spec),
                image = $"ipfs://placeholder/{spec.TokenId}/sheet.png",
                animation_url = $"ipfs://placeholder/{spec.TokenId}/sheet.mp4"
            };
            
            // Add core attributes
            metadata.AddAttribute("Category", GetCategoryName(spec));
            metadata.AddAttribute("Archetype", spec.Archetype.ToString());
            metadata.AddAttribute("Genre", spec.Genre.ToString());
            metadata.AddAttribute("Rarity", spec.Rarity.ToString());
            metadata.AddAttribute("Provenance Hash", provenanceHash);
            
            // Faculty-specific attributes
            if (spec.Faculty != FacultyRole.None)
            {
                metadata.AddAttribute("Faculty Role", spec.Faculty.ToString());
                metadata.AddAttribute("Uniqueness", "1/1");
            }
            
            // Add custom traits
            foreach (var trait in spec.CustomTraits)
            {
                metadata.AddAttribute(trait.Key, trait.Value);
            }
            
            return metadata;
        }
        
        /// <summary>
        /// Helper methods for metadata generation
        /// </summary>
        private static string GenerateTokenName(SpriteSpec spec)
        {
            if (spec.Faculty != FacultyRole.None)
            {
                return $"{spec.Faculty} • {spec.Archetype} of the {GetGenreAdjective(spec.Genre)}";
            }
            
            return $"{GetGenreAdjective(spec.Genre)} {spec.Archetype}";
        }
        
        private static string GenerateTokenDescription(SpriteSpec spec)
        {
            if (spec.Faculty != FacultyRole.None)
            {
                return $"Faculty ultra-rare 1/1. Forged from TLDA verdicts and {spec.Faculty.ToString().ToLower()} rituals.";
            }
            
            return $"{spec.Rarity} {spec.Genre.ToString().ToLower()} creature. Generated from the TLDA mythos.";
        }
        
        private static string GetCategoryName(SpriteSpec spec)
        {
            return spec.Faculty != FacultyRole.None ? "Faculty" : "Creature";
        }
        
        private static string GetGenreAdjective(GenreStyle genre)
        {
            return genre switch
            {
                GenreStyle.SciFi => "Stellar",
                GenreStyle.Fantasy => "Mystical",
                GenreStyle.Steampunk => "Clockwork",
                GenreStyle.Cyberpunk => "Neural",
                GenreStyle.Mythic => "Divine",
                _ => "Unknown"
            };
        }
        
        /// <summary>
        /// Utility methods
        /// </summary>
        private static System.Random CreateSeededRandom(string seed)
        {
            using var sha256 = SHA256.Create();
            var hashBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(seed));
            var seedInt = BitConverter.ToInt32(hashBytes, 0);
            return new System.Random(seedInt);
        }
        
        private static string GenerateProvenanceHash(string seed, SpriteSpec spec)
        {
            var combined = $"{seed}{spec.Archetype}{spec.Genre}{spec.Faculty}{spec.Rarity}";
            using var sha256 = SHA256.Create();
            var hashBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(combined));
            return BitConverter.ToString(hashBytes).Replace("-", "").ToLower().ToLower();
        }
        
        private static int GetFrameCount(SpriteSpec spec)
        {
            // Evolution chains use a different frame counting system
            if (spec.GenerateEvolutionChain)
            {
                return spec.FramesPerAnimation; // Frames per stage (horizontal)
            }
            
            // Faculty ultra-rares get more frames
            if (spec.Faculty != FacultyRole.None)
            {
                return spec.Faculty == FacultyRole.Creator ? 24 : 12; // Creator gets multi-phase animation
            }
            
            return spec.Rarity switch
            {
                RarityTier.Legendary => 8,
                RarityTier.Epic => 6,
                RarityTier.Rare => 4,
                _ => 4
            };
        }
        
        private static Rect[] GenerateFrameRects(int frameCount, Vector2Int frameSize)
        {
            var rects = new Rect[frameCount];
            for (int i = 0; i < frameCount; i++)
            {
                rects[i] = new Rect(i * frameSize.x, 0, frameSize.x, frameSize.y);
            }
            return rects;
        }
        
        private static float[] GenerateFrameDurations(int frameCount, SpriteSpec spec)
        {
            var baseDuration = spec.Faculty != FacultyRole.None ? 0.15f : 0.2f; // Faculty animations are smoother
            var durations = new float[frameCount];
            
            for (int i = 0; i < frameCount; i++)
            {
                durations[i] = baseDuration;
            }
            
            return durations;
        }
        
        private static void CopyFrameToSheet(Texture2D sheet, Texture2D frame, int frameIndex, Vector2Int frameSize)
        {
            var offsetX = frameIndex * frameSize.x;
            
            for (int y = 0; y < frameSize.y; y++)
            {
                for (int x = 0; x < frameSize.x; x++)
                {
                    var pixel = frame.GetPixel(x, y);
                    sheet.SetPixel(offsetX + x, y, pixel);
                }
            }
        }
        
        /// <summary>
        /// Generate evolution-specific silhouette based on stage
        /// KeeperNote: Each stage has progressively more complex and larger forms
        /// </summary>
        private static bool[,] GenerateEvolutionSilhouette(CreatureArchetype archetype, EvolutionStage stage, Vector2Int size, int frameIndex, System.Random random)
        {
            var silhouette = new bool[size.x, size.y];
            
            // Base size multiplier for each evolution stage
            var sizeMultiplier = stage switch
            {
                EvolutionStage.Egg => 0.3f,
                EvolutionStage.Hatchling => 0.5f,
                EvolutionStage.Juvenile => 0.7f,
                EvolutionStage.Adult => 0.9f,
                EvolutionStage.Elder => 1.1f,
                EvolutionStage.Legendary => 1.3f,
                _ => 1.0f
            };
            
            // Generate base shape for the archetype
            switch (archetype)
            {
                case CreatureArchetype.Familiar:
                    GenerateEvolutionFamiliarShape(silhouette, size, stage, sizeMultiplier, frameIndex, random);
                    break;
                    
                case CreatureArchetype.Wisp:
                    GenerateEvolutionWispShape(silhouette, size, stage, sizeMultiplier, frameIndex, random);
                    break;
                    
                case CreatureArchetype.Golem:
                    GenerateEvolutionGolemShape(silhouette, size, stage, sizeMultiplier, frameIndex, random);
                    break;
                    
                case CreatureArchetype.Sentinel:
                    GenerateEvolutionSentinelShape(silhouette, size, stage, sizeMultiplier, frameIndex, random);
                    break;
                    
                default:
                    GenerateEvolutionFamiliarShape(silhouette, size, stage, sizeMultiplier, frameIndex, random);
                    break;
            }
            
            return silhouette;
        }
        
        /// <summary>
        /// Generate evolution-specific familiar shapes
        /// </summary>
        private static void GenerateEvolutionFamiliarShape(bool[,] silhouette, Vector2Int size, EvolutionStage stage, float sizeMultiplier, int frameIndex, System.Random random)
        {
            var width = size.x;
            var height = size.y;
            var centerX = width / 2;
            var centerY = height / 2;
            
            // Animation offset for breathing/floating effect
            var animOffset = Mathf.Sin(frameIndex * 0.5f) * 0.5f;
            
            switch (stage)
            {
                case EvolutionStage.Egg:
                    // Simple oval egg shape
                    for (int y = centerY - 3; y <= centerY + 3; y++)
                    {
                        for (int x = centerX - 2; x <= centerX + 2; x++)
                        {
                            if (x >= 0 && x < width && y >= 0 && y < height)
                            {
                                var dx = x - centerX;
                                var dy = y - centerY;
                                if (dx * dx / 4.0 + dy * dy / 9.0 <= 1.0)
                                {
                                    silhouette[x, y] = true;
                                }
                            }
                        }
                    }
                    break;
                    
                case EvolutionStage.Hatchling:
                    // Small creature emerging from egg
                    GenerateFamiliarShape(silhouette, new Vector2Int((int)(width * 0.6f), (int)(height * 0.6f)), random);
                    break;
                    
                case EvolutionStage.Juvenile:
                    // Standard familiar shape
                    GenerateFamiliarShape(silhouette, size, random);
                    break;
                    
                case EvolutionStage.Adult:
                    // Larger familiar with more details
                    GenerateFamiliarShape(silhouette, size, random);
                    // Add accessories (collar, markings)
                    if (centerY + 2 < height && centerX - 3 >= 0 && centerX + 3 < width)
                    {
                        silhouette[centerX - 3, centerY + 2] = true;
                        silhouette[centerX + 3, centerY + 2] = true;
                    }
                    break;
                    
                case EvolutionStage.Elder:
                    // Majestic familiar with flowing features
                    GenerateFamiliarShape(silhouette, size, random);
                    // Add flowing elements
                    for (int i = 0; i < 3; i++)
                    {
                        var angle = (frameIndex + i) * 0.3f;
                        var flowX = centerX + (int)(Math.Cos(angle) * 4);
                        var flowY = centerY + (int)(Math.Sin(angle) * 2);
                        if (flowX >= 0 && flowX < width && flowY >= 0 && flowY < height)
                        {
                            silhouette[flowX, flowY] = true;
                        }
                    }
                    break;
                    
                case EvolutionStage.Legendary:
                    // Awe-inspiring final form
                    GenerateFamiliarShape(silhouette, size, random);
                    // Add radiant aura
                    var radius = 8;
                    for (int y = 0; y < height; y++)
                    {
                        for (int x = 0; x < width; x++)
                        {
                            var dx = x - centerX;
                            var dy = y - centerY;
                            var distance = Math.Sqrt(dx * dx + dy * dy);
                            
                            if (distance >= radius - 1 && distance <= radius + 1 && random.NextDouble() > 0.6)
                            {
                                silhouette[x, y] = true;
                            }
                        }
                    }
                    break;
            }
        }
        
        /// <summary>
        /// Generate evolution-specific wisp shapes
        /// </summary>
        private static void GenerateEvolutionWispShape(bool[,] silhouette, Vector2Int size, EvolutionStage stage, float sizeMultiplier, int frameIndex, System.Random random)
        {
            var width = size.x;
            var height = size.y;
            var centerX = width / 2;
            var centerY = height / 2;
            
            var coreRadius = (int)(Math.Min(width, height) / 4 * sizeMultiplier);
            
            // Pulsing core
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    var dx = x - centerX;
                    var dy = y - centerY;
                    var distance = Math.Sqrt(dx * dx + dy * dy);
                    
                    var pulseOffset = Math.Sin(frameIndex * 0.4f) * 0.5f;
                    if (distance <= coreRadius + pulseOffset)
                    {
                        silhouette[x, y] = true;
                    }
                }
            }
            
            // Stage-specific energy patterns
            var trailCount = stage switch
            {
                EvolutionStage.Egg => 0,
                EvolutionStage.Hatchling => 2,
                EvolutionStage.Juvenile => 3,
                EvolutionStage.Adult => 4,
                EvolutionStage.Elder => 6,
                EvolutionStage.Legendary => 8,
                _ => 3
            };
            
            for (int i = 0; i < trailCount; i++)
            {
                var angle = (i * 2 * Math.PI / trailCount) + (frameIndex * 0.1f);
                var trailLength = coreRadius + (int)(stage >= EvolutionStage.Elder ? 6 : 4);
                
                for (int j = 1; j <= trailLength; j++)
                {
                    var x = centerX + (int)(Math.Cos(angle) * j);
                    var y = centerY + (int)(Math.Sin(angle) * j);
                    
                    if (x >= 0 && x < width && y >= 0 && y < height && random.NextDouble() > 0.4)
                    {
                        silhouette[x, y] = true;
                    }
                }
            }
        }
        
        /// <summary>
        /// Generate evolution-specific golem shapes
        /// </summary>
        private static void GenerateEvolutionGolemShape(bool[,] silhouette, Vector2Int size, EvolutionStage stage, float sizeMultiplier, int frameIndex, System.Random random)
        {
            var width = size.x;
            var height = size.y;
            var centerX = width / 2;
            
            var bodyWidth = (int)(3 * sizeMultiplier);
            var bodyHeight = (int)((height - 4) * sizeMultiplier);
            
            // Body structure based on evolution
            for (int y = 2; y < 2 + bodyHeight && y < height - 2; y++)
            {
                for (int x = centerX - bodyWidth; x <= centerX + bodyWidth; x++)
                {
                    if (x >= 0 && x < width)
                    {
                        silhouette[x, y] = true;
                    }
                }
            }
            
            // Head - grows with evolution
            var headSize = stage switch
            {
                EvolutionStage.Egg => 1,
                EvolutionStage.Hatchling => 1,
                EvolutionStage.Juvenile => 2,
                EvolutionStage.Adult => 2,
                EvolutionStage.Elder => 3,
                EvolutionStage.Legendary => 3,
                _ => 2
            };
            
            for (int y = height - 4; y < height; y++)
            {
                for (int x = centerX - headSize; x <= centerX + headSize; x++)
                {
                    if (x >= 0 && x < width && y >= 0)
                    {
                        silhouette[x, y] = true;
                    }
                }
            }
            
            // Add stage-specific features
            if (stage >= EvolutionStage.Adult)
            {
                // Shoulder spikes
                var spikeY = height - 6;
                if (spikeY >= 0)
                {
                    if (centerX - bodyWidth - 1 >= 0) silhouette[centerX - bodyWidth - 1, spikeY] = true;
                    if (centerX + bodyWidth + 1 < width) silhouette[centerX + bodyWidth + 1, spikeY] = true;
                }
            }
            
            if (stage >= EvolutionStage.Legendary)
            {
                // Crown/crest
                for (int x = centerX - 2; x <= centerX + 2; x++)
                {
                    if (x >= 0 && x < width && height - 1 >= 0)
                    {
                        silhouette[x, height - 1] = true;
                    }
                }
            }
        }
        
        /// <summary>
        /// Generate evolution-specific sentinel shapes
        /// </summary>
        private static void GenerateEvolutionSentinelShape(bool[,] silhouette, Vector2Int size, EvolutionStage stage, float sizeMultiplier, int frameIndex, System.Random random)
        {
            var width = size.x;
            var height = size.y;
            var centerX = width / 2;
            
            // Base sentinel shape with evolution scaling
            for (int y = 1; y < height - 1; y++)
            {
                var bodyWidth = (int)(Math.Max(1, 4 - Math.Abs(y - height / 2) / 3) * sizeMultiplier);
                for (int x = centerX - bodyWidth; x <= centerX + bodyWidth; x++)
                {
                    if (x >= 0 && x < width)
                    {
                        silhouette[x, y] = true;
                    }
                }
            }
            
            // Stage-specific enhancements
            if (stage >= EvolutionStage.Adult)
            {
                // Weapons/staff
                var weaponX = centerX + 4;
                if (weaponX < width)
                {
                    for (int y = height / 2; y < height - 2; y++)
                    {
                        if (y >= 0) silhouette[weaponX, y] = true;
                    }
                }
            }
            
            if (stage >= EvolutionStage.Elder)
            {
                // Armor plates
                for (int y = height / 2 - 2; y <= height / 2 + 2; y++)
                {
                    if (y >= 0 && y < height)
                    {
                        if (centerX - 3 >= 0) silhouette[centerX - 3, y] = true;
                        if (centerX + 3 < width) silhouette[centerX + 3, y] = true;
                    }
                }
            }
            
            if (stage == EvolutionStage.Legendary)
            {
                // Divine aura
                for (int i = 0; i < 4; i++)
                {
                    var angle = (i * Math.PI / 2) + (frameIndex * 0.1f);
                    var auraX = centerX + (int)(Math.Cos(angle) * 6);
                    var auraY = height / 2 + (int)(Math.Sin(angle) * 3);
                    
                    if (auraX >= 0 && auraX < width && auraY >= 0 && auraY < height)
                    {
                        silhouette[auraX, auraY] = true;
                    }
                }
            }
        }
        
        /// <summary>
        /// Apply evolution-specific styling to sprite
        /// </summary>
        private static void ApplyEvolutionStyling(Texture2D texture, bool[,] silhouette, SpriteSpec spec, EvolutionStage stage, Color[] palette, int frameIndex, System.Random random)
        {
            // Start with base genre styling
            ApplyGenreStyling(texture, silhouette, spec, palette, frameIndex, random);
            
            // Add evolution-specific color modifications
            var evolutionIntensity = stage switch
            {
                EvolutionStage.Egg => 0.3f,
                EvolutionStage.Hatchling => 0.5f,
                EvolutionStage.Juvenile => 0.7f,
                EvolutionStage.Adult => 0.9f,
                EvolutionStage.Elder => 1.1f,
                EvolutionStage.Legendary => 1.3f,
                _ => 1.0f
            };
            
            // Enhance colors based on evolution stage
            var pixels = texture.GetPixels();
            for (int i = 0; i < pixels.Length; i++)
            {
                if (pixels[i].a > 0) // Non-transparent pixel
                {
                    // Increase saturation and brightness for higher evolution stages
                    Color.RGBToHSV(pixels[i], out float h, out float s, out float v);
                    s = Mathf.Clamp01(s * evolutionIntensity);
                    v = Mathf.Clamp01(v * (0.8f + evolutionIntensity * 0.3f));
                    pixels[i] = Color.HSVToRGB(h, s, v);
                    pixels[i].a = pixels[i].a; // Preserve alpha
                }
            }
            texture.SetPixels(pixels);
        }
        
        /// <summary>
        /// Apply stage-specific visual effects
        /// </summary>
        private static void ApplyEvolutionEffects(Texture2D texture, EvolutionStage stage, int frameIndex, System.Random random)
        {
            var size = new Vector2Int(texture.width, texture.height);
            
            switch (stage)
            {
                case EvolutionStage.Egg:
                    // Subtle shell pattern
                    ApplyShellPattern(texture, frameIndex);
                    break;
                    
                case EvolutionStage.Elder:
                    // Wisdom aura
                    ApplyWisdomAura(texture, frameIndex, random);
                    break;
                    
                case EvolutionStage.Legendary:
                    // Divine radiance
                    ApplyDivineRadiance(texture, frameIndex, random);
                    break;
            }
        }
        
        /// <summary>
        /// Apply shell pattern for egg stage
        /// </summary>
        private static void ApplyShellPattern(Texture2D texture, int frameIndex)
        {
            var centerX = texture.width / 2;
            var centerY = texture.height / 2;
            
            // Add subtle crack lines that animate
            var crackProgress = frameIndex * 0.1f;
            for (int y = 0; y < texture.height; y++)
            {
                for (int x = 0; x < texture.width; x++)
                {
                    var pixel = texture.GetPixel(x, y);
                    if (pixel.a > 0)
                    {
                        // Add shell texture
                        var pattern = Mathf.Sin((x + y) * 0.5f + crackProgress) * 0.1f;
                        var newColor = new Color(
                            Mathf.Clamp01(pixel.r + pattern),
                            Mathf.Clamp01(pixel.g + pattern),
                            Mathf.Clamp01(pixel.b + pattern),
                            pixel.a
                        );
                        texture.SetPixel(x, y, newColor);
                    }
                }
            }
        }
        
        /// <summary>
        /// Apply wisdom aura for elder stage
        /// </summary>
        private static void ApplyWisdomAura(Texture2D texture, int frameIndex, System.Random random)
        {
            var centerX = texture.width / 2;
            var centerY = texture.height / 2;
            
            // Gentle glowing effect
            for (int y = 0; y < texture.height; y++)
            {
                for (int x = 0; x < texture.width; x++)
                {
                    var dx = x - centerX;
                    var dy = y - centerY;
                    var distance = Mathf.Sqrt(dx * dx + dy * dy);
                    
                    if (distance >= 8 && distance <= 10 && random.NextDouble() > 0.8)
                    {
                        var glowIntensity = 0.3f * Mathf.Sin(frameIndex * 0.3f);
                        var glowColor = new Color(0.8f, 0.9f, 1.0f, glowIntensity);
                        texture.SetPixel(x, y, glowColor);
                    }
                }
            }
        }
        
        /// <summary>
        /// Apply divine radiance for legendary stage
        /// </summary>
        private static void ApplyDivineRadiance(Texture2D texture, int frameIndex, System.Random random)
        {
            var centerX = texture.width / 2;
            var centerY = texture.height / 2;
            
            // Bright radial bursts
            for (int i = 0; i < 8; i++)
            {
                var angle = (i * Math.PI / 4) + (frameIndex * 0.2f);
                var rayLength = 12;
                
                for (int j = 8; j < rayLength; j++)
                {
                    var x = centerX + (int)(Math.Cos(angle) * j);
                    var y = centerY + (int)(Math.Sin(angle) * j);
                    
                    if (x >= 0 && x < texture.width && y >= 0 && y < texture.height && random.NextDouble() > 0.7)
                    {
                        var intensity = 1.0f - (j / (float)rayLength);
                        var radianceColor = new Color(1.0f, 0.9f, 0.6f, intensity * 0.8f);
                        texture.SetPixel(x, y, Color.Lerp(texture.GetPixel(x, y), radianceColor, 0.5f));
                    }
                }
            }
        }
    }
}