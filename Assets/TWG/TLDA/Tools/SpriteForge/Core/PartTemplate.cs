using System;
using System.Collections.Generic;
using UnityEngine;

namespace TWG.TLDA.SpriteForge
{
    /// <summary>
    /// Modular part template for sprite composition
    /// KeeperNote: Enables dynamic sprite assembly from reusable components
    /// </summary>
    [Serializable]
    public class PartTemplate
    {
        [Header("Part Identity")]
        public string PartId;
        public string PartName;
        public PartType Type;
        public PartLayer Layer;
        
        [Header("Visual Properties")]
        public Vector2Int Size = new(24, 24);
        public Vector2Int Offset = Vector2Int.zero;
        public float Opacity = 1f;
        public BlendMode BlendMode = BlendMode.Normal;
        
        [Header("Compatibility")]
        public CreatureArchetype[] CompatibleArchetypes;
        public GenreStyle[] CompatibleGenres;
        public EvolutionStage[] CompatibleStages;
        
        [Header("Animation")]
        public bool IsAnimated = false;
        public int AnimationFrames = 1;
        public float AnimationSpeed = 8f; // FPS
        
        [Header("Procedural Generation")]
        public PartGenerationMethod GenerationMethod = PartGenerationMethod.Procedural;
        public string AssetPath = ""; // For asset-based parts
        public PartVariation[] Variations;
        
        /// <summary>
        /// Check if this part is compatible with the given specification
        /// </summary>
        public bool IsCompatibleWith(SpriteSpec spec)
        {
            if (CompatibleArchetypes.Length > 0 && !Array.Exists(CompatibleArchetypes, a => a == spec.Archetype))
                return false;
                
            if (CompatibleGenres.Length > 0 && !Array.Exists(CompatibleGenres, g => g == spec.Genre))
                return false;
                
            // Check evolution stage compatibility if generating evolution chain
            if (spec.GenerateEvolutionChain && CompatibleStages.Length > 0)
            {
                bool hasCompatibleStage = false;
                foreach (var stage in spec.EvolutionStages)
                {
                    if (Array.Exists(CompatibleStages, s => s == stage))
                    {
                        hasCompatibleStage = true;
                        break;
                    }
                }
                if (!hasCompatibleStage)
                    return false;
            }
            
            return true;
        }
        
        /// <summary>
        /// Generate the visual representation of this part
        /// </summary>
        public Texture2D GeneratePartTexture(SpriteSpec spec, System.Random random, PaletteManager palette, EvolutionStage stage = EvolutionStage.Adult)
        {
            switch (GenerationMethod)
            {
                case PartGenerationMethod.Procedural:
                    return GenerateProceduralPart(spec, random, palette, stage);
                case PartGenerationMethod.Asset:
                    return LoadAssetPart(spec, stage);
                case PartGenerationMethod.Hybrid:
                    var basePart = LoadAssetPart(spec, stage);
                    return ModifyWithProcedural(basePart, spec, random, palette, stage);
                default:
                    return GenerateProceduralPart(spec, random, palette, stage);
            }
        }
        
        private Texture2D GenerateProceduralPart(SpriteSpec spec, System.Random random, PaletteManager palette, EvolutionStage stage)
        {
            var texture = new Texture2D(Size.x, Size.y, TextureFormat.RGBA32, false)
            {
                filterMode = FilterMode.Point
            };
            
            var colors = new Color[Size.x * Size.y];
            var paletteColors = palette.GetPartPalette(Type, spec.Genre, stage);
            
            // Generate part based on type and archetype
            GeneratePartPattern(colors, Size, Type, spec.Archetype, random, paletteColors, stage);
            
            texture.SetPixels(colors);
            texture.Apply();
            
            return texture;
        }
        
        private void GeneratePartPattern(Color[] colors, Vector2Int size, PartType partType, CreatureArchetype archetype, System.Random random, Color[] palette, EvolutionStage stage)
        {
            // Clear to transparent
            for (int i = 0; i < colors.Length; i++)
                colors[i] = Color.clear;
            
            // Generate pattern based on part type and archetype
            switch (partType)
            {
                case PartType.Body:
                    GenerateBodyPattern(colors, size, archetype, random, palette, stage);
                    break;
                case PartType.Head:
                    GenerateHeadPattern(colors, size, archetype, random, palette, stage);
                    break;
                case PartType.Eyes:
                    GenerateEyesPattern(colors, size, archetype, random, palette, stage);
                    break;
                case PartType.Accessories:
                    GenerateAccessoryPattern(colors, size, archetype, random, palette, stage);
                    break;
                case PartType.Effects:
                    GenerateEffectPattern(colors, size, archetype, random, palette, stage);
                    break;
            }
        }
        
        private void GenerateBodyPattern(Color[] colors, Vector2Int size, CreatureArchetype archetype, System.Random random, Color[] palette, EvolutionStage stage)
        {
            var centerX = size.x / 2;
            var centerY = size.y / 2;
            var radius = Mathf.Min(size.x, size.y) / 3;
            
            // Scale based on evolution stage
            var stageScale = GetStageScale(stage);
            radius = Mathf.RoundToInt(radius * stageScale);
            
            // Generate basic body shape based on archetype
            switch (archetype)
            {
                case CreatureArchetype.Familiar:
                    GenerateOvalBody(colors, size, centerX, centerY, radius, palette[0]);
                    break;
                case CreatureArchetype.Golem:
                    GenerateBlockyBody(colors, size, centerX, centerY, radius, palette[0]);
                    break;
                case CreatureArchetype.Wisp:
                    GenerateWispyBody(colors, size, centerX, centerY, radius, palette[0], random);
                    break;
                default:
                    GenerateOvalBody(colors, size, centerX, centerY, radius, palette[0]);
                    break;
            }
        }
        
        private void GenerateHeadPattern(Color[] colors, Vector2Int size, CreatureArchetype archetype, System.Random random, Color[] palette, EvolutionStage stage)
        {
            var centerX = size.x / 2;
            var centerY = size.y * 3 / 4; // Head is in upper portion
            var radius = Mathf.Min(size.x, size.y) / 4;
            
            GenerateCircle(colors, size, centerX, centerY, radius, palette[1]);
        }
        
        private void GenerateEyesPattern(Color[] colors, Vector2Int size, CreatureArchetype archetype, System.Random random, Color[] palette, EvolutionStage stage)
        {
            var centerY = size.y * 3 / 4;
            var eyeRadius = 2;
            
            // Left eye
            GenerateCircle(colors, size, size.x / 3, centerY, eyeRadius, palette[2]);
            // Right eye
            GenerateCircle(colors, size, size.x * 2 / 3, centerY, eyeRadius, palette[2]);
        }
        
        private void GenerateAccessoryPattern(Color[] colors, Vector2Int size, CreatureArchetype archetype, System.Random random, Color[] palette, EvolutionStage stage)
        {
            // Accessories vary by evolution stage
            if (stage >= EvolutionStage.Adult)
            {
                // Add crown or collar based on archetype
                var centerX = size.x / 2;
                var topY = size.y - 3;
                
                for (int x = centerX - 2; x <= centerX + 2; x++)
                {
                    if (x >= 0 && x < size.x)
                        colors[topY * size.x + x] = palette[1];
                }
            }
        }
        
        private void GenerateEffectPattern(Color[] colors, Vector2Int size, CreatureArchetype archetype, System.Random random, Color[] palette, EvolutionStage stage)
        {
            // Effects increase with evolution stage
            if (stage >= EvolutionStage.Elder)
            {
                // Add glow effect around creature
                var centerX = size.x / 2;
                var centerY = size.y / 2;
                var effectRadius = Mathf.Min(size.x, size.y) / 2;
                
                for (int y = 0; y < size.y; y++)
                {
                    for (int x = 0; x < size.x; x++)
                    {
                        var distance = Vector2.Distance(new Vector2(x, y), new Vector2(centerX, centerY));
                        if (distance > effectRadius - 2 && distance < effectRadius)
                        {
                            var alpha = 0.3f;
                            var effectColor = palette[2];
                            effectColor.a = alpha;
                            colors[y * size.x + x] = effectColor;
                        }
                    }
                }
            }
        }
        
        private float GetStageScale(EvolutionStage stage)
        {
            return stage switch
            {
                EvolutionStage.Egg => 0.5f,
                EvolutionStage.Hatchling => 0.7f,
                EvolutionStage.Juvenile => 0.8f,
                EvolutionStage.Adult => 1.0f,
                EvolutionStage.Elder => 1.2f,
                EvolutionStage.Legendary => 1.5f,
                _ => 1.0f
            };
        }
        
        private void GenerateOvalBody(Color[] colors, Vector2Int size, int centerX, int centerY, int radius, Color color)
        {
            for (int y = 0; y < size.y; y++)
            {
                for (int x = 0; x < size.x; x++)
                {
                    var dx = x - centerX;
                    var dy = (y - centerY) * 1.5f; // Make it oval
                    var distance = Mathf.Sqrt(dx * dx + dy * dy);
                    
                    if (distance <= radius)
                        colors[y * size.x + x] = color;
                }
            }
        }
        
        private void GenerateBlockyBody(Color[] colors, Vector2Int size, int centerX, int centerY, int radius, Color color)
        {
            var left = centerX - radius;
            var right = centerX + radius;
            var top = centerY + radius;
            var bottom = centerY - radius;
            
            for (int y = bottom; y <= top && y < size.y; y++)
            {
                for (int x = left; x <= right && x < size.x; x++)
                {
                    if (x >= 0 && y >= 0)
                        colors[y * size.x + x] = color;
                }
            }
        }
        
        private void GenerateWispyBody(Color[] colors, Vector2Int size, int centerX, int centerY, int radius, Color color, System.Random random)
        {
            // Generate wispy, energy-like patterns
            for (int y = 0; y < size.y; y++)
            {
                for (int x = 0; x < size.x; x++)
                {
                    var dx = x - centerX;
                    var dy = y - centerY;
                    var distance = Mathf.Sqrt(dx * dx + dy * dy);
                    
                    if (distance <= radius)
                    {
                        var noiseValue = Mathf.PerlinNoise(x * 0.3f, y * 0.3f);
                        if (noiseValue > 0.4f)
                        {
                            var alpha = (radius - distance) / radius * noiseValue;
                            var wispColor = color;
                            wispColor.a = alpha;
                            colors[y * size.x + x] = wispColor;
                        }
                    }
                }
            }
        }
        
        private void GenerateCircle(Color[] colors, Vector2Int size, int centerX, int centerY, int radius, Color color)
        {
            for (int y = 0; y < size.y; y++)
            {
                for (int x = 0; x < size.x; x++)
                {
                    var distance = Vector2.Distance(new Vector2(x, y), new Vector2(centerX, centerY));
                    if (distance <= radius)
                        colors[y * size.x + x] = color;
                }
            }
        }
        
        private Texture2D LoadAssetPart(SpriteSpec spec, EvolutionStage stage)
        {
            // TODO: Load from asset path - for now return procedural
            return GenerateProceduralPart(spec, new System.Random(spec.TokenId.GetHashCode()), 
                PaletteManager.Instance, stage);
        }
        
        private Texture2D ModifyWithProcedural(Texture2D basePart, SpriteSpec spec, System.Random random, PaletteManager palette, EvolutionStage stage)
        {
            // TODO: Apply procedural modifications to asset-based part
            return basePart;
        }
    }
    
    /// <summary>
    /// Type of sprite part for modular composition
    /// </summary>
    public enum PartType
    {
        Body,        // Main body of the creature
        Head,        // Head/face region
        Eyes,        // Eyes and facial features
        Limbs,       // Arms, legs, tentacles
        Wings,       // Wings for flying creatures
        Tail,        // Tail appendage
        Accessories, // Collars, crowns, armor
        Effects,     // Magical auras, glows, particles
        Background   // Environmental elements
    }
    
    /// <summary>
    /// Rendering layer for part composition
    /// </summary>
    public enum PartLayer
    {
        Background = 0,
        Body = 10,
        BodyDetails = 15,
        Limbs = 20,
        Head = 30,
        Eyes = 40,
        Accessories = 50,
        Effects = 60,
        Foreground = 70
    }
    
    /// <summary>
    /// Blend mode for part composition
    /// </summary>
    public enum BlendMode
    {
        Normal,
        Multiply,
        Screen,
        Overlay,
        SoftLight,
        HardLight,
        ColorDodge,
        ColorBurn,
        LinearBurn,
        Add
    }
    
    /// <summary>
    /// Method for generating part visuals
    /// </summary>
    public enum PartGenerationMethod
    {
        Procedural,  // Fully procedural generation
        Asset,       // Load from asset files
        Hybrid       // Asset base with procedural modifications
    }
    
    /// <summary>
    /// Variation definition for a part
    /// </summary>
    [Serializable]
    public class PartVariation
    {
        public string VariationId;
        public string Name;
        public float Weight = 1f; // Probability weight
        public Color[] ColorOverrides;
        public Vector2Int SizeModifier = Vector2Int.zero;
        public Dictionary<string, object> Parameters = new();
    }
}