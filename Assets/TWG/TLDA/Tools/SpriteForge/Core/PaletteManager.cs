using System;
using System.Collections.Generic;
using UnityEngine;

namespace TWG.TLDA.SpriteForge
{
    /// <summary>
    /// Advanced 3-color palette management system for modular sprites
    /// KeeperNote: Provides sophisticated color harmonies and adaptive palettes for different sprite parts
    /// </summary>
    public class PaletteManager
    {
        private static PaletteManager _instance;
        public static PaletteManager Instance => _instance ??= new PaletteManager();
        
        private readonly Dictionary<string, ThreeColorPalette> _basePalettes;
        private readonly Dictionary<string, Color[]> _genreColorSets;
        private readonly Dictionary<string, Color[]> _facultyColorSets;
        
        public PaletteManager()
        {
            _basePalettes = new Dictionary<string, ThreeColorPalette>();
            _genreColorSets = new Dictionary<string, Color[]>();
            _facultyColorSets = new Dictionary<string, Color[]>();
            
            InitializeBasePalettes();
            InitializeGenreColors();
            InitializeFacultyColors();
        }
        
        /// <summary>
        /// Get a 3-color palette for a specific part, genre, and evolution stage
        /// </summary>
        public Color[] GetPartPalette(PartType partType, GenreStyle genre, EvolutionStage stage = EvolutionStage.Adult)
        {
            var basePalette = GetGenreBasePalette(genre);
            var stagePalette = ApplyStageModifications(basePalette, stage);
            var partPalette = ApplyPartSpecialization(stagePalette, partType);
            
            return new Color[] { partPalette.Primary, partPalette.Secondary, partPalette.Accent };
        }
        
        /// <summary>
        /// Get a 3-color palette for faculty ultra-rares
        /// </summary>
        public Color[] GetFacultyPalette(FacultyRole faculty, PartType partType, EvolutionStage stage = EvolutionStage.Adult)
        {
            var basePalette = GetFacultyBasePalette(faculty);
            var stagePalette = ApplyStageModifications(basePalette, stage);
            var partPalette = ApplyPartSpecialization(stagePalette, partType);
            
            return new Color[] { partPalette.Primary, partPalette.Secondary, partPalette.Accent };
        }
        
        /// <summary>
        /// Generate a harmonious 3-color palette from a seed
        /// </summary>
        public ThreeColorPalette GenerateHarmoniousPalette(string seed, ColorHarmonyType harmonyType = ColorHarmonyType.Triadic)
        {
            var random = new System.Random(seed.GetHashCode());
            var baseHue = random.NextSingle() * 360f;
            
            return GenerateHarmonyFromHue(baseHue, harmonyType, random);
        }
        
        /// <summary>
        /// Create adaptive palette that changes based on context
        /// </summary>
        public AdaptivePalette CreateAdaptivePalette(SpriteSpec spec, string seed)
        {
            var basePalette = spec.Faculty != FacultyRole.None 
                ? GetFacultyBasePalette(spec.Faculty)
                : GetGenreBasePalette(spec.Genre);
            
            return new AdaptivePalette(basePalette, seed, spec);
        }
        
        /// <summary>
        /// Blend two palettes with a given weight
        /// </summary>
        public ThreeColorPalette BlendPalettes(ThreeColorPalette paletteA, ThreeColorPalette paletteB, float weight)
        {
            return new ThreeColorPalette
            {
                Primary = Color.Lerp(paletteA.Primary, paletteB.Primary, weight),
                Secondary = Color.Lerp(paletteA.Secondary, paletteB.Secondary, weight),
                Accent = Color.Lerp(paletteA.Accent, paletteB.Accent, weight)
            };
        }
        
        /// <summary>
        /// Apply color temperature shift to palette
        /// </summary>
        public ThreeColorPalette ApplyTemperatureShift(ThreeColorPalette palette, float temperature)
        {
            var shiftColor = temperature > 0 
                ? new Color(1f, 0.8f, 0.6f, 1f) // Warm
                : new Color(0.6f, 0.8f, 1f, 1f); // Cool
            
            var intensity = Mathf.Abs(temperature);
            
            return new ThreeColorPalette
            {
                Primary = Color.Lerp(palette.Primary, shiftColor, intensity * 0.2f),
                Secondary = Color.Lerp(palette.Secondary, shiftColor, intensity * 0.15f),
                Accent = Color.Lerp(palette.Accent, shiftColor, intensity * 0.1f)
            };
        }
        
        private void InitializeBasePalettes()
        {
            // Fantasy base palette
            _basePalettes["fantasy"] = new ThreeColorPalette
            {
                Primary = new Color(0.4f, 0.3f, 0.2f, 1f),   // Dark brown
                Secondary = new Color(0.6f, 0.4f, 0.2f, 1f), // Light brown  
                Accent = new Color(0.7f, 0.3f, 0.9f, 1f)     // Purple magic
            };
            
            // Sci-fi base palette
            _basePalettes["scifi"] = new ThreeColorPalette
            {
                Primary = new Color(0.2f, 0.2f, 0.3f, 1f),   // Dark blue
                Secondary = new Color(0.4f, 0.4f, 0.4f, 1f), // Gray
                Accent = new Color(0f, 1f, 0.5f, 1f)         // Green neon
            };
            
            // Steampunk base palette
            _basePalettes["steampunk"] = new ThreeColorPalette
            {
                Primary = new Color(0.4f, 0.3f, 0.2f, 1f),   // Dark brass
                Secondary = new Color(0.6f, 0.4f, 0.2f, 1f), // Brass
                Accent = new Color(0.8f, 0.6f, 0.3f, 1f)     // Gold
            };
            
            // Cyberpunk base palette
            _basePalettes["cyberpunk"] = new ThreeColorPalette
            {
                Primary = new Color(0.1f, 0.1f, 0.1f, 1f),   // Black
                Secondary = new Color(0.2f, 0.2f, 0.3f, 1f), // Dark blue
                Accent = new Color(1f, 0f, 1f, 1f)           // Magenta neon
            };
            
            // Mythic base palette (for Faculty)
            _basePalettes["mythic"] = new ThreeColorPalette
            {
                Primary = new Color(0.9f, 0.9f, 0.9f, 1f),   // Divine white
                Secondary = new Color(1f, 0.9f, 0.7f, 1f),   // Cream
                Accent = new Color(1f, 0.8f, 0.2f, 1f)       // Divine gold
            };
        }
        
        private void InitializeGenreColors()
        {
            _genreColorSets["fantasy"] = new[]
            {
                new Color(0.2f, 0.5f, 0.2f, 1f), // Forest green
                new Color(0.6f, 0.3f, 0.1f, 1f), // Earth brown
                new Color(0.8f, 0.7f, 0.4f, 1f), // Gold
                new Color(0.3f, 0.3f, 0.6f, 1f), // Deep blue
                new Color(0.7f, 0.2f, 0.2f, 1f)  // Ruby red
            };
            
            _genreColorSets["scifi"] = new[]
            {
                new Color(0.1f, 0.3f, 0.6f, 1f), // Tech blue
                new Color(0.5f, 0.5f, 0.5f, 1f), // Metal gray
                new Color(0.9f, 0.9f, 0.9f, 1f), // Chrome white
                new Color(0f, 0.8f, 0.4f, 1f),   // Matrix green
                new Color(0.8f, 0.4f, 0f, 1f)    // Warning orange
            };
            
            _genreColorSets["steampunk"] = new[]
            {
                new Color(0.5f, 0.3f, 0.1f, 1f), // Copper
                new Color(0.7f, 0.5f, 0.2f, 1f), // Brass
                new Color(0.3f, 0.2f, 0.1f, 1f), // Dark bronze
                new Color(0.8f, 0.7f, 0.5f, 1f), // Aged brass
                new Color(0.4f, 0.3f, 0.3f, 1f)  // Iron
            };
            
            _genreColorSets["cyberpunk"] = new[]
            {
                new Color(1f, 0f, 0.5f, 1f),     // Hot pink
                new Color(0f, 1f, 1f, 1f),       // Cyan
                new Color(0.5f, 0f, 1f, 1f),     // Electric purple
                new Color(1f, 1f, 0f, 1f),       // Neon yellow
                new Color(0f, 0.8f, 0.2f, 1f)    // Matrix green
            };
        }
        
        private void InitializeFacultyColors()
        {
            _facultyColorSets["warbler"] = new[]
            {
                new Color(0.2f, 0.4f, 0.8f, 1f), // Well-blue
                new Color(0.1f, 0.6f, 0.9f, 1f), // Light blue
                new Color(0.4f, 0.8f, 1f, 1f),   // Sky blue
                new Color(0.6f, 0.9f, 1f, 1f)    // Pale blue
            };
            
            _facultyColorSets["creator"] = new[]
            {
                new Color(1f, 0.9f, 0.7f, 1f),   // Divine cream
                new Color(1f, 0.8f, 0.2f, 1f),   // Divine gold
                new Color(0.9f, 0.7f, 0.1f, 1f), // Rich gold
                new Color(1f, 1f, 0.9f, 1f)      // Pure light
            };
            
            _facultyColorSets["sentinel"] = new[]
            {
                new Color(0.6f, 0.6f, 0.6f, 1f), // Steel gray
                new Color(0.4f, 0.4f, 0.5f, 1f), // Dark steel
                new Color(0.8f, 0.8f, 0.9f, 1f), // Light steel
                new Color(0.7f, 0.7f, 0.8f, 1f)  // Medium steel
            };
        }
        
        private ThreeColorPalette GetGenreBasePalette(GenreStyle genre)
        {
            var genreKey = genre.ToString().ToLower();
            return _basePalettes.ContainsKey(genreKey) 
                ? _basePalettes[genreKey] 
                : _basePalettes["fantasy"];
        }
        
        private ThreeColorPalette GetFacultyBasePalette(FacultyRole faculty)
        {
            if (faculty == FacultyRole.None)
                return _basePalettes["mythic"];
            
            var facultyKey = faculty.ToString().ToLower();
            if (_facultyColorSets.ContainsKey(facultyKey))
            {
                var colors = _facultyColorSets[facultyKey];
                return new ThreeColorPalette
                {
                    Primary = colors[0],
                    Secondary = colors[1],
                    Accent = colors[2]
                };
            }
            
            return _basePalettes["mythic"];
        }
        
        private ThreeColorPalette ApplyStageModifications(ThreeColorPalette basePalette, EvolutionStage stage)
        {
            var intensity = GetStageIntensity(stage);
            var brightness = GetStageBrightness(stage);
            
            return new ThreeColorPalette
            {
                Primary = ModifyColorIntensity(basePalette.Primary, intensity, brightness),
                Secondary = ModifyColorIntensity(basePalette.Secondary, intensity, brightness),
                Accent = ModifyColorIntensity(basePalette.Accent, intensity, brightness)
            };
        }
        
        private ThreeColorPalette ApplyPartSpecialization(ThreeColorPalette basePalette, PartType partType)
        {
            return partType switch
            {
                PartType.Eyes => new ThreeColorPalette
                {
                    Primary = basePalette.Accent,    // Eyes use accent color
                    Secondary = basePalette.Primary,
                    Accent = Color.white             // White highlights
                },
                PartType.Effects => new ThreeColorPalette
                {
                    Primary = basePalette.Accent,
                    Secondary = Color.Lerp(basePalette.Accent, Color.white, 0.5f),
                    Accent = Color.white
                },
                PartType.Accessories => new ThreeColorPalette
                {
                    Primary = Color.Lerp(basePalette.Secondary, basePalette.Accent, 0.3f),
                    Secondary = basePalette.Accent,
                    Accent = Color.Lerp(basePalette.Accent, Color.white, 0.3f)
                },
                _ => basePalette
            };
        }
        
        private float GetStageIntensity(EvolutionStage stage)
        {
            return stage switch
            {
                EvolutionStage.Egg => 0.3f,
                EvolutionStage.Hatchling => 0.5f,
                EvolutionStage.Juvenile => 0.7f,
                EvolutionStage.Adult => 1.0f,
                EvolutionStage.Elder => 1.3f,
                EvolutionStage.Legendary => 1.6f,
                _ => 1.0f
            };
        }
        
        private float GetStageBrightness(EvolutionStage stage)
        {
            return stage switch
            {
                EvolutionStage.Egg => 0.8f,
                EvolutionStage.Hatchling => 0.9f,
                EvolutionStage.Juvenile => 0.95f,
                EvolutionStage.Adult => 1.0f,
                EvolutionStage.Elder => 1.1f,
                EvolutionStage.Legendary => 1.3f,
                _ => 1.0f
            };
        }
        
        private Color ModifyColorIntensity(Color color, float intensity, float brightness)
        {
            Color.RGBToHSV(color, out float h, out float s, out float v);
            
            s *= intensity;
            v *= brightness;
            
            s = Mathf.Clamp01(s);
            v = Mathf.Clamp01(v);
            
            return Color.HSVToRGB(h, s, v);
        }
        
        private ThreeColorPalette GenerateHarmonyFromHue(float baseHue, ColorHarmonyType harmonyType, System.Random random)
        {
            var primaryHue = baseHue;
            var secondaryHue = primaryHue;
            var accentHue = primaryHue;
            
            switch (harmonyType)
            {
                case ColorHarmonyType.Triadic:
                    secondaryHue = (primaryHue + 120f) % 360f;
                    accentHue = (primaryHue + 240f) % 360f;
                    break;
                case ColorHarmonyType.Complementary:
                    secondaryHue = (primaryHue + 30f) % 360f;
                    accentHue = (primaryHue + 180f) % 360f;
                    break;
                case ColorHarmonyType.Analogous:
                    secondaryHue = (primaryHue + 30f) % 360f;
                    accentHue = (primaryHue + 60f) % 360f;
                    break;
                case ColorHarmonyType.Monochromatic:
                    secondaryHue = primaryHue;
                    accentHue = primaryHue;
                    break;
            }
            
            return new ThreeColorPalette
            {
                Primary = Color.HSVToRGB(primaryHue / 360f, 0.8f, 0.7f),
                Secondary = Color.HSVToRGB(secondaryHue / 360f, 0.6f, 0.8f),
                Accent = Color.HSVToRGB(accentHue / 360f, 0.9f, 0.9f)
            };
        }
    }
    
    /// <summary>
    /// Three-color palette structure
    /// </summary>
    [Serializable]
    public class ThreeColorPalette
    {
        public Color Primary;   // Main body color
        public Color Secondary; // Secondary features color
        public Color Accent;    // Highlight/detail color
        
        public Color[] ToArray() => new[] { Primary, Secondary, Accent };
    }
    
    /// <summary>
    /// Adaptive palette that changes based on context
    /// </summary>
    public class AdaptivePalette
    {
        private readonly ThreeColorPalette _basePalette;
        private readonly System.Random _random;
        private readonly SpriteSpec _spec;
        
        public AdaptivePalette(ThreeColorPalette basePalette, string seed, SpriteSpec spec)
        {
            _basePalette = basePalette;
            _random = new System.Random(seed.GetHashCode());
            _spec = spec;
        }
        
        public Color[] GetPaletteForPart(PartType partType, EvolutionStage stage)
        {
            var stagePalette = PaletteManager.Instance.GetPartPalette(partType, _spec.Genre, stage);
            
            // Add some variation based on the part
            var variation = _random.NextSingle() * 0.1f - 0.05f; // ±5% variation
            
            for (int i = 0; i < stagePalette.Length; i++)
            {
                Color.RGBToHSV(stagePalette[i], out float h, out float s, out float v);
                h = (h + variation) % 1f;
                stagePalette[i] = Color.HSVToRGB(h, s, v);
            }
            
            return stagePalette;
        }
    }
    
    /// <summary>
    /// Color harmony types for palette generation
    /// </summary>
    public enum ColorHarmonyType
    {
        Triadic,        // 120° apart
        Complementary,  // 180° apart
        Analogous,      // 30° apart
        Monochromatic   // Same hue, different saturation/value
    }
}