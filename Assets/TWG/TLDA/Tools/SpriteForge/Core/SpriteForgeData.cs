using System;
using System.Collections.Generic;
using UnityEngine;

namespace TWG.TLDA.SpriteForge
{
    /// <summary>
    /// Sprite generation specification
    /// KeeperNote: Complete parameters for deterministic sprite generation
    /// </summary>
    [Serializable]
    public class SpriteSpec
    {
        [Header("Core Properties")]
        public CreatureArchetype Archetype = CreatureArchetype.Familiar;
        public GenreStyle Genre = GenreStyle.Fantasy;
        public FacultyRole Faculty = FacultyRole.None;
        
        [Header("Visual Properties")]
        public Vector2Int Size = new(24, 24);
        public string PaletteId = "default";
        public AnimationSet[] AnimationSets = { AnimationSet.Idle, AnimationSet.Walk };
        
        [Header("Evolution Properties")]
        public bool GenerateEvolutionChain = false;
        public EvolutionStage[] EvolutionStages = new EvolutionStage[0];
        public int FramesPerAnimation = 6;  // For 6x6 layout
        
        [Header("Rarity Properties")]
        public RarityTier Rarity = RarityTier.Common;
        public string[] SpecialTraits = new string[0];
        public bool HasShaderEffects = false;
        
        [Header("Metadata")]
        public string TokenId = "";
        public string Description = "";
        public Dictionary<string, object> CustomTraits = new();
        
        /// <summary>
        /// Create a Faculty ultra-rare specification
        /// </summary>
        public static SpriteSpec CreateFacultySpec(FacultyRole faculty, string tokenId)
        {
            var spec = new SpriteSpec
            {
                Faculty = faculty,
                Genre = GenreStyle.Mythic,
                Rarity = RarityTier.OneOfOne,
                TokenId = tokenId,
                Size = new Vector2Int(32, 32), // Larger for ultra-rares
                HasShaderEffects = true,
                AnimationSets = new [ ] { AnimationSet.Idle, AnimationSet.Walk, AnimationSet.Cast, AnimationSet.Emote },
                // Set archetype based on faculty role
                Archetype = faculty switch
                {
                    FacultyRole.Warbler => CreatureArchetype.Wisp,
                    FacultyRole.Creator => CreatureArchetype.Sentinel,
                    FacultyRole.Sentinel => CreatureArchetype.Warder,
                    FacultyRole.Archivist => CreatureArchetype.Homunculus,
                    FacultyRole.Wrangler => CreatureArchetype.Familiar,
                    FacultyRole.Scribe => CreatureArchetype.Automaton,
                    FacultyRole.Oracle => CreatureArchetype.Drifter,
                    FacultyRole.Keeper => CreatureArchetype.Golem,
                    _ => CreatureArchetype.Familiar
                }
            };

            return spec;
        }
        
        /// <summary>
        /// Create a genre creature specification
        /// </summary>
        public static SpriteSpec CreateGenreSpec(GenreStyle genre, CreatureArchetype archetype, RarityTier rarity)
        {
            return new SpriteSpec
            {
                Genre = genre,
                Archetype = archetype,
                Rarity = rarity,
                Faculty = FacultyRole.None,
                Size = new Vector2Int(24, 24),
                AnimationSets = new[] { AnimationSet.Idle, AnimationSet.Walk }
            };
        }
        
        /// <summary>
        /// Create an evolution chain specification for genre creatures
        /// KeeperNote: Generates all 6 evolution stages in a single sprite sheet
        /// </summary>
        public static SpriteSpec CreateEvolutionChainSpec(GenreStyle genre, CreatureArchetype archetype, RarityTier rarity)
        {
            return new SpriteSpec
            {
                Genre = genre,
                Archetype = archetype,
                Rarity = rarity,
                Faculty = FacultyRole.None,
                Size = new Vector2Int(24, 24),
                AnimationSets = new[] { AnimationSet.Idle },
                GenerateEvolutionChain = true,
                EvolutionStages = new[] { 
                    EvolutionStage.Egg, 
                    EvolutionStage.Hatchling, 
                    EvolutionStage.Juvenile, 
                    EvolutionStage.Adult, 
                    EvolutionStage.Elder, 
                    EvolutionStage.Legendary 
                },
                FramesPerAnimation = 6
            };
        }
        
        /// <summary>
        /// Create an animated evolution chain specification
        /// KeeperNote: Includes multiple animation sets for each evolution stage
        /// </summary>
        public static SpriteSpec CreateAnimatedEvolutionSpec(GenreStyle genre, CreatureArchetype archetype, RarityTier rarity)
        {
            return new SpriteSpec
            {
                Genre = genre,
                Archetype = archetype,
                Rarity = rarity,
                Faculty = FacultyRole.None,
                Size = new Vector2Int(24, 24),
                AnimationSets = new[] { AnimationSet.Idle, AnimationSet.Walk },
                GenerateEvolutionChain = true,
                EvolutionStages = new[] { 
                    EvolutionStage.Egg, 
                    EvolutionStage.Hatchling, 
                    EvolutionStage.Juvenile, 
                    EvolutionStage.Adult, 
                    EvolutionStage.Elder, 
                    EvolutionStage.Legendary 
                },
                FramesPerAnimation = 6,
                HasShaderEffects = true
            };
        }
    }
    
    /// <summary>
    /// Result of sprite generation
    /// KeeperNote: Contains all generated assets and metadata
    /// </summary>
    [Serializable]
    public class SpriteGenerationResult
    {
        [Header("Generated Assets")]
        public Texture2D SpriteSheet;
        public string SpriteSheetPath;
        public string MetadataPath;
        
        [Header("Animation Data")]
        public SpriteAnimationData AnimationData;
        
        [Header("NFT Metadata")]
        public NFTMetadata TokenMetadata;
        
        [Header("Generation Info")]
        public string Seed;
        public DateTime GeneratedAt;
        public string ProvenanceHash;
        
        public bool IsValid => SpriteSheet != null && TokenMetadata != null;
    }
    
    /// <summary>
    /// Animation frame data for Unity sprite slicing
    /// KeeperNote: Compatible with Unity's SpriteRenderer and Animator
    /// </summary>
    [Serializable]
    public class SpriteAnimationData
    {
        public AnimationSet AnimationType;
        public Rect[] FrameRects;
        public float[] FrameDurations;
        public Vector2 Pivot = new(0.5f, 0f); // Bottom-center
        public bool LoopAnimation = true;
        
        [Header("Evolution Chain Data")]
        public string[] EvolutionStages = new string[0];
        public int FramesPerStage = 1;
        
        /// <summary>
        /// Check if this is an evolution chain animation
        /// </summary>
        public bool IsEvolutionChain => EvolutionStages.Length > 1;
        
        /// <summary>
        /// Get frame rectangles for a specific evolution stage
        /// </summary>
        public Rect[] GetStageFrameRects(int stageIndex)
        {
            if (!IsEvolutionChain || stageIndex < 0 || stageIndex >= EvolutionStages.Length)
                return FrameRects;
            
            var stageFrames = new Rect[FramesPerStage];
            var startIndex = stageIndex * FramesPerStage;
            
            for (int i = 0; i < FramesPerStage && startIndex + i < FrameRects.Length; i++)
            {
                stageFrames[i] = FrameRects[startIndex + i];
            }
            
            return stageFrames;
        }
        
        /// <summary>
        /// Generate Unity animation clip data
        /// </summary>
        public AnimationClip ToAnimationClip(Sprite[] sprites)
        {
            var clip = new AnimationClip
            {
                name = $"{AnimationType}_Animation",
                frameRate = 8f // 8 FPS for pixel art
            };

            // Animation implementation would go here
            // This is a placeholder for the Unity animation system

            return clip;
        }
    }
    
    /// <summary>
    /// NFT metadata structure compatible with OpenSea and other marketplaces
    /// KeeperNote: Follows ERC-721 and ERC-1155 metadata standards
    /// </summary>
    [Serializable]
    public class NFTMetadata
    {
        public string name;
        public string description;
        public string image;
        public string animation_url;
        public NFTAttribute[] attributes;
        
        [Serializable]
        public class NFTAttribute
        {
            public string trait_type;
            public object value;
            public string display_type; // Optional for numeric traits
            
            public NFTAttribute(string traitType, object val, string displayType = null)
            {
                trait_type = traitType;
                value = val;
                display_type = displayType;
            }
        }
        
        public void AddAttribute(string traitType, object value, string displayType = null)
        {
            var attrList = new List<NFTAttribute>(attributes ?? new NFTAttribute[0]);
            attrList.Add(new NFTAttribute(traitType, value, displayType));
            attributes = attrList.ToArray();
        }
    }
}