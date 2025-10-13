using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace TWG.TLDA.SpriteForge
{
    /// <summary>
    /// Enhanced modular sprite generator with dynamic part composition
    /// KeeperNote: Composes sprites from reusable part templates with advanced palette management
    /// </summary>
    public static class ModularSpriteGenerator
    {
        private static readonly Dictionary<CreatureArchetype, List<PartTemplate>> _partLibrary = new();
        private static bool _libraryInitialized = false;
        
        /// <summary>
        /// Generate a modular sprite with dynamic part composition
        /// </summary>
        public static ModularSpriteResult GenerateModularSprite(string seed, SpriteSpec spec)
        {
            EnsureLibraryInitialized();
            
            var random = new System.Random(seed.GetHashCode());
            var paletteManager = PaletteManager.Instance;
            var adaptivePalette = paletteManager.CreateAdaptivePalette(spec, seed);
            
            var result = new ModularSpriteResult
            {
                Seed = seed,
                Specification = spec,
                BoneStructure = RiggedAnimationExporter.GenerateBoneStructure(spec.Archetype)
            };
            
            // Select and generate parts
            var selectedParts = SelectPartsForSprite(spec, random);
            result.Parts = GeneratePartInstances(selectedParts, spec, random, adaptivePalette);
            
            // Compose final sprite
            if (spec.GenerateEvolutionChain)
            {
                result.CompositeTexture = GenerateEvolutionChainComposite(result.Parts, spec);
            }
            else
            {
                result.CompositeTexture = GenerateStandardComposite(result.Parts, spec);
            }
            
            return result;
        }
        
        /// <summary>
        /// Generate sprite with backwards compatibility to existing SpriteGenerator
        /// </summary>
        public static SpriteGenerationResult GenerateCompatibleSprite(string seed, SpriteSpec spec)
        {
            var modularResult = GenerateModularSprite(seed, spec);
            
            // Convert to compatible format
            return new SpriteGenerationResult
            {
                Seed = seed,
                GeneratedAt = DateTime.UtcNow,
                ProvenanceHash = GenerateProvenanceHash(seed, spec),
                SpriteSheet = modularResult.CompositeTexture,
                AnimationData = GenerateCompatibleAnimationData(spec, modularResult),
                TokenMetadata = GenerateNFTMetadata(spec, seed),
                SpriteSheetPath = $"Generated/Creatures/{spec.TokenId}/sheet.png",
                MetadataPath = $"Generated/Creatures/{spec.TokenId}/metadata.json"
            };
        }
        
        /// <summary>
        /// Generate rigged animation export from modular sprite
        /// </summary>
        public static object GenerateRiggedExport(ModularSpriteResult result, RiggedExportFormat format)
        {
            return format switch
            {
                RiggedExportFormat.Spine => RiggedAnimationExporter.ExportToSpine(result, result.Specification),
                RiggedExportFormat.DragonBones => RiggedAnimationExporter.ExportToDragonBones(result, result.Specification),
                _ => throw new ArgumentException($"Unsupported export format: {format}")
            };
        }
        
        /// <summary>
        /// Create a custom part template
        /// </summary>
        public static PartTemplate CreateCustomPart(string partId, PartType type, CreatureArchetype[] archetypes, GenreStyle[] genres)
        {
            return new PartTemplate
            {
                PartId = partId,
                PartName = partId.Replace("_", " ").ToTitleCase(),
                Type = type,
                Layer = GetDefaultLayer(type),
                CompatibleArchetypes = archetypes,
                CompatibleGenres = genres,
                GenerationMethod = PartGenerationMethod.Procedural,
                Size = new Vector2Int(24, 24),
                Variations = new PartVariation[0]
            };
        }
        
        /// <summary>
        /// Register a custom part template in the library
        /// </summary>
        public static void RegisterPartTemplate(PartTemplate template)
        {
            EnsureLibraryInitialized();
            
            foreach (var archetype in template.CompatibleArchetypes)
            {
                if (!_partLibrary.ContainsKey(archetype))
                    _partLibrary[archetype] = new List<PartTemplate>();
                    
                _partLibrary[archetype].Add(template);
            }
        }
        
        /// <summary>
        /// Get available parts for a specific archetype
        /// </summary>
        public static List<PartTemplate> GetAvailableParts(CreatureArchetype archetype, GenreStyle genre)
        {
            EnsureLibraryInitialized();
            
            if (!_partLibrary.ContainsKey(archetype))
                return new List<PartTemplate>();
            
            return _partLibrary[archetype]
                .Where(p => p.IsCompatibleWith(new SpriteSpec { Archetype = archetype, Genre = genre }))
                .ToList();
        }
        
        private static void EnsureLibraryInitialized()
        {
            if (_libraryInitialized) return;
            
            InitializePartLibrary();
            _libraryInitialized = true;
        }
        
        private static void InitializePartLibrary()
        {
            // Initialize part templates for each archetype
            InitializeFamiliarParts();
            InitializeGolemParts();
            InitializeWispParts();
            InitializeSentinelParts();
            InitializeHomunculusParts();
            InitializeAutomatonParts();
            InitializeDrifterParts();
            InitializeWarderParts();
        }
        
        private static void InitializeFamiliarParts()
        {
            var archetype = CreatureArchetype.Familiar;
            var allGenres = new[] { GenreStyle.Fantasy, GenreStyle.SciFi, GenreStyle.Steampunk, GenreStyle.Cyberpunk, GenreStyle.Mythic };
            var allStages = new[] { EvolutionStage.Egg, EvolutionStage.Hatchling, EvolutionStage.Juvenile, EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary };
            
            var parts = new[]
            {
                CreateBasePart("familiar_body", PartType.Body, archetype, allGenres, allStages),
                CreateBasePart("familiar_head", PartType.Head, archetype, allGenres, allStages),
                CreateBasePart("familiar_eyes", PartType.Eyes, archetype, allGenres, allStages),
                CreateBasePart("familiar_ears", PartType.Accessories, archetype, allGenres, new[] { EvolutionStage.Hatchling, EvolutionStage.Juvenile, EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary }),
                CreateBasePart("familiar_tail", PartType.Tail, archetype, allGenres, allStages),
                CreateBasePart("familiar_collar", PartType.Accessories, archetype, allGenres, new[] { EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary }),
                CreateBasePart("familiar_aura", PartType.Effects, archetype, allGenres, new[] { EvolutionStage.Elder, EvolutionStage.Legendary })
            };
            
            _partLibrary[archetype] = parts.ToList();
        }
        
        private static void InitializeGolemParts()
        {
            var archetype = CreatureArchetype.Golem;
            var allGenres = new[] { GenreStyle.Fantasy, GenreStyle.SciFi, GenreStyle.Steampunk, GenreStyle.Cyberpunk, GenreStyle.Mythic };
            var allStages = new[] { EvolutionStage.Egg, EvolutionStage.Hatchling, EvolutionStage.Juvenile, EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary };
            
            var parts = new[]
            {
                CreateBasePart("golem_torso", PartType.Body, archetype, allGenres, allStages),
                CreateBasePart("golem_head", PartType.Head, archetype, allGenres, allStages),
                CreateBasePart("golem_eyes", PartType.Eyes, archetype, allGenres, allStages),
                CreateBasePart("golem_arms", PartType.Limbs, archetype, allGenres, new[] { EvolutionStage.Juvenile, EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary }),
                CreateBasePart("golem_legs", PartType.Limbs, archetype, allGenres, new[] { EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary }),
                CreateBasePart("golem_armor", PartType.Accessories, archetype, allGenres, new[] { EvolutionStage.Elder, EvolutionStage.Legendary }),
                CreateBasePart("golem_crown", PartType.Accessories, archetype, allGenres, new[] { EvolutionStage.Legendary })
            };
            
            _partLibrary[archetype] = parts.ToList();
        }
        
        private static void InitializeWispParts()
        {
            var archetype = CreatureArchetype.Wisp;
            var allGenres = new[] { GenreStyle.Fantasy, GenreStyle.SciFi, GenreStyle.Steampunk, GenreStyle.Cyberpunk, GenreStyle.Mythic };
            var allStages = new[] { EvolutionStage.Egg, EvolutionStage.Hatchling, EvolutionStage.Juvenile, EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary };
            
            var parts = new[]
            {
                CreateBasePart("wisp_core", PartType.Body, archetype, allGenres, allStages),
                CreateBasePart("wisp_trail_1", PartType.Effects, archetype, allGenres, allStages),
                CreateBasePart("wisp_trail_2", PartType.Effects, archetype, allGenres, new[] { EvolutionStage.Juvenile, EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary }),
                CreateBasePart("wisp_energy_field", PartType.Effects, archetype, allGenres, new[] { EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary }),
                CreateBasePart("wisp_pulsing_core", PartType.Effects, archetype, allGenres, new[] { EvolutionStage.Elder, EvolutionStage.Legendary })
            };
            
            foreach (var part in parts)
            {
                part.IsAnimated = true;
                part.AnimationFrames = 6;
            }
            
            _partLibrary[archetype] = parts.ToList();
        }
        
        private static void InitializeSentinelParts()
        {
            var archetype = CreatureArchetype.Sentinel;
            var allGenres = new[] { GenreStyle.Fantasy, GenreStyle.SciFi, GenreStyle.Steampunk, GenreStyle.Cyberpunk, GenreStyle.Mythic };
            var allStages = new[] { EvolutionStage.Egg, EvolutionStage.Hatchling, EvolutionStage.Juvenile, EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary };
            
            var parts = new[]
            {
                CreateBasePart("sentinel_base", PartType.Body, archetype, allGenres, allStages),
                CreateBasePart("sentinel_torso", PartType.Body, archetype, allGenres, new[] { EvolutionStage.Juvenile, EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary }),
                CreateBasePart("sentinel_head", PartType.Head, archetype, allGenres, allStages),
                CreateBasePart("sentinel_weapons", PartType.Accessories, archetype, allGenres, new[] { EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary }),
                CreateBasePart("sentinel_divine_light", PartType.Effects, archetype, allGenres, new[] { EvolutionStage.Legendary })
            };
            
            _partLibrary[archetype] = parts.ToList();
        }
        
        private static void InitializeHomunculusParts()
        {
            // Similar to familiar but with alchemical theme
            var archetype = CreatureArchetype.Homunculus;
            var allGenres = new[] { GenreStyle.Fantasy, GenreStyle.SciFi, GenreStyle.Steampunk, GenreStyle.Cyberpunk, GenreStyle.Mythic };
            var allStages = new[] { EvolutionStage.Egg, EvolutionStage.Hatchling, EvolutionStage.Juvenile, EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary };
            
            var parts = new[]
            {
                CreateBasePart("homunculus_body", PartType.Body, archetype, allGenres, allStages),
                CreateBasePart("homunculus_head", PartType.Head, archetype, allGenres, allStages),
                CreateBasePart("homunculus_eyes", PartType.Eyes, archetype, allGenres, allStages),
                CreateBasePart("homunculus_flask", PartType.Accessories, archetype, allGenres, new[] { EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary }),
                CreateBasePart("homunculus_runes", PartType.Effects, archetype, allGenres, new[] { EvolutionStage.Elder, EvolutionStage.Legendary })
            };
            
            _partLibrary[archetype] = parts.ToList();
        }
        
        private static void InitializeAutomatonParts()
        {
            // Similar to golem but with mechanical theme
            var archetype = CreatureArchetype.Automaton;
            var allGenres = new[] { GenreStyle.Fantasy, GenreStyle.SciFi, GenreStyle.Steampunk, GenreStyle.Cyberpunk, GenreStyle.Mythic };
            var allStages = new[] { EvolutionStage.Egg, EvolutionStage.Hatchling, EvolutionStage.Juvenile, EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary };
            
            var parts = new[]
            {
                CreateBasePart("automaton_chassis", PartType.Body, archetype, allGenres, allStages),
                CreateBasePart("automaton_head", PartType.Head, archetype, allGenres, allStages),
                CreateBasePart("automaton_optics", PartType.Eyes, archetype, allGenres, allStages),
                CreateBasePart("automaton_gears", PartType.Accessories, archetype, allGenres, new[] { EvolutionStage.Juvenile, EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary }),
                CreateBasePart("automaton_steam", PartType.Effects, archetype, allGenres, new[] { EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary })
            };
            
            _partLibrary[archetype] = parts.ToList();
        }
        
        private static void InitializeDrifterParts()
        {
            // Similar to wisp but with ethereal theme
            var archetype = CreatureArchetype.Drifter;
            var allGenres = new[] { GenreStyle.Fantasy, GenreStyle.SciFi, GenreStyle.Steampunk, GenreStyle.Cyberpunk, GenreStyle.Mythic };
            var allStages = new[] { EvolutionStage.Egg, EvolutionStage.Hatchling, EvolutionStage.Juvenile, EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary };
            
            var parts = new[]
            {
                CreateBasePart("drifter_essence", PartType.Body, archetype, allGenres, allStages),
                CreateBasePart("drifter_manifestation", PartType.Head, archetype, allGenres, new[] { EvolutionStage.Juvenile, EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary }),
                CreateBasePart("drifter_whispers", PartType.Effects, archetype, allGenres, new[] { EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary }),
                CreateBasePart("drifter_portal", PartType.Effects, archetype, allGenres, new[] { EvolutionStage.Legendary })
            };
            
            foreach (var part in parts)
            {
                part.IsAnimated = true;
                part.AnimationFrames = 8;
            }
            
            _partLibrary[archetype] = parts.ToList();
        }
        
        private static void InitializeWarderParts()
        {
            // Similar to sentinel but with protective theme
            var archetype = CreatureArchetype.Warder;
            var allGenres = new[] { GenreStyle.Fantasy, GenreStyle.SciFi, GenreStyle.Steampunk, GenreStyle.Cyberpunk, GenreStyle.Mythic };
            var allStages = new[] { EvolutionStage.Egg, EvolutionStage.Hatchling, EvolutionStage.Juvenile, EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary };
            
            var parts = new[]
            {
                CreateBasePart("warder_core", PartType.Body, archetype, allGenres, allStages),
                CreateBasePart("warder_shield", PartType.Accessories, archetype, allGenres, new[] { EvolutionStage.Juvenile, EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary }),
                CreateBasePart("warder_barrier", PartType.Effects, archetype, allGenres, new[] { EvolutionStage.Adult, EvolutionStage.Elder, EvolutionStage.Legendary }),
                CreateBasePart("warder_sanctum", PartType.Effects, archetype, allGenres, new[] { EvolutionStage.Legendary })
            };
            
            _partLibrary[archetype] = parts.ToList();
        }
        
        private static PartTemplate CreateBasePart(string partId, PartType type, CreatureArchetype archetype, GenreStyle[] genres, EvolutionStage[] stages)
        {
            return new PartTemplate
            {
                PartId = partId,
                PartName = partId.Replace("_", " ").ToTitleCase(),
                Type = type,
                Layer = GetDefaultLayer(type),
                CompatibleArchetypes = new[] { archetype },
                CompatibleGenres = genres,
                CompatibleStages = stages,
                Size = new Vector2Int(24, 24),
                GenerationMethod = PartGenerationMethod.Procedural,
                Variations = new PartVariation[0]
            };
        }
        
        private static PartLayer GetDefaultLayer(PartType type)
        {
            return type switch
            {
                PartType.Background => PartLayer.Background,
                PartType.Body => PartLayer.Body,
                PartType.Head => PartLayer.Head,
                PartType.Eyes => PartLayer.Eyes,
                PartType.Limbs => PartLayer.Limbs,
                PartType.Wings => PartLayer.Limbs,
                PartType.Tail => PartLayer.BodyDetails,
                PartType.Accessories => PartLayer.Accessories,
                PartType.Effects => PartLayer.Effects,
                _ => PartLayer.Body
            };
        }
        
        private static List<PartTemplate> SelectPartsForSprite(SpriteSpec spec, System.Random random)
        {
            var availableParts = GetAvailableParts(spec.Archetype, spec.Genre);
            var selectedParts = new List<PartTemplate>();
            
            // Always include essential parts
            var essentialTypes = new[] { PartType.Body, PartType.Head, PartType.Eyes };
            foreach (var type in essentialTypes)
            {
                var essentialPart = availableParts.FirstOrDefault(p => p.Type == type);
                if (essentialPart != null)
                    selectedParts.Add(essentialPart);
            }
            
            // Add optional parts based on evolution stage
            if (spec.GenerateEvolutionChain)
            {
                // Include all compatible parts for evolution chain
                selectedParts.AddRange(availableParts.Where(p => !selectedParts.Contains(p)));
            }
            else
            {
                // Select random optional parts
                var optionalParts = availableParts.Where(p => !selectedParts.Contains(p)).ToList();
                var numOptional = random.Next(1, Math.Min(optionalParts.Count + 1, 4));
                
                for (int i = 0; i < numOptional && optionalParts.Count > 0; i++)
                {
                    var index = random.Next(optionalParts.Count);
                    selectedParts.Add(optionalParts[index]);
                    optionalParts.RemoveAt(index);
                }
            }
            
            return selectedParts;
        }
        
        private static List<PartInstance> GeneratePartInstances(List<PartTemplate> partTemplates, SpriteSpec spec, System.Random random, AdaptivePalette palette)
        {
            var instances = new List<PartInstance>();
            
            foreach (var template in partTemplates)
            {
                var instance = new PartInstance
                {
                    Template = template,
                    Position = template.Offset,
                    ZOrder = (int)template.Layer,
                    Tint = Color.white
                };
                
                // Generate texture for each evolution stage if needed
                if (spec.GenerateEvolutionChain)
                {
                    instance.Texture = GeneratePartTextureForEvolution(template, spec, random, palette);
                }
                else
                {
                    var stageColors = palette.GetPaletteForPart(template.Type, EvolutionStage.Adult);
                    instance.Texture = template.GeneratePartTexture(spec, random, PaletteManager.Instance, EvolutionStage.Adult);
                }
                
                instances.Add(instance);
            }
            
            return instances.OrderBy(p => p.ZOrder).ToList();
        }
        
        private static Texture2D GeneratePartTextureForEvolution(PartTemplate template, SpriteSpec spec, System.Random random, AdaptivePalette palette)
        {
            var stageCount = spec.EvolutionStages.Length;
            var frameCount = spec.FramesPerAnimation;
            var totalWidth = spec.Size.x * frameCount;
            var totalHeight = spec.Size.y * stageCount;
            
            var evolutionTexture = new Texture2D(totalWidth, totalHeight, TextureFormat.RGBA32, false)
            {
                filterMode = FilterMode.Point
            };
            
            // Generate each evolution stage
            for (int stageIndex = 0; stageIndex < stageCount; stageIndex++)
            {
                var stage = spec.EvolutionStages[stageIndex];
                
                for (int frame = 0; frame < frameCount; frame++)
                {
                    var frameTexture = template.GeneratePartTexture(spec, random, PaletteManager.Instance, stage);
                    
                    // Copy frame to evolution sheet
                    var offsetX = frame * spec.Size.x;
                    var offsetY = stageIndex * spec.Size.y;
                    
                    CopyTextureToSheet(evolutionTexture, frameTexture, offsetX, offsetY);
                }
            }
            
            evolutionTexture.Apply();
            return evolutionTexture;
        }
        
        private static Texture2D GenerateStandardComposite(List<PartInstance> parts, SpriteSpec spec)
        {
            var frameCount = GetFrameCount(spec);
            var sheetWidth = spec.Size.x * frameCount;
            var sheetHeight = spec.Size.y;
            
            var composite = new Texture2D(sheetWidth, sheetHeight, TextureFormat.RGBA32, false)
            {
                filterMode = FilterMode.Point
            };
            
            // Clear to transparent
            var clearPixels = new Color[sheetWidth * sheetHeight];
            for (int i = 0; i < clearPixels.Length; i++)
                clearPixels[i] = Color.clear;
            composite.SetPixels(clearPixels);
            
            // Composite parts in layer order
            foreach (var part in parts.OrderBy(p => p.ZOrder))
            {
                CompositePart(composite, part, spec);
            }
            
            composite.Apply();
            return composite;
        }
        
        private static Texture2D GenerateEvolutionChainComposite(List<PartInstance> parts, SpriteSpec spec)
        {
            var stageCount = spec.EvolutionStages.Length;
            var frameCount = spec.FramesPerAnimation;
            var sheetWidth = spec.Size.x * frameCount;
            var sheetHeight = spec.Size.y * stageCount;
            
            var composite = new Texture2D(sheetWidth, sheetHeight, TextureFormat.RGBA32, false)
            {
                filterMode = FilterMode.Point
            };
            
            // Clear to transparent
            var clearPixels = new Color[sheetWidth * sheetHeight];
            for (int i = 0; i < clearPixels.Length; i++)
                clearPixels[i] = Color.clear;
            composite.SetPixels(clearPixels);
            
            // Composite parts in layer order
            foreach (var part in parts.OrderBy(p => p.ZOrder))
            {
                CompositeEvolutionPart(composite, part, spec);
            }
            
            composite.Apply();
            return composite;
        }
        
        private static void CompositePart(Texture2D target, PartInstance part, SpriteSpec spec)
        {
            if (part.Texture == null) return;
            
            var frameCount = GetFrameCount(spec);
            
            for (int frame = 0; frame < frameCount; frame++)
            {
                var targetX = frame * spec.Size.x + part.Position.x;
                var targetY = part.Position.y;
                
                BlendTextures(target, part.Texture, targetX, targetY, part.Template.BlendMode, part.Tint);
            }
        }
        
        private static void CompositeEvolutionPart(Texture2D target, PartInstance part, SpriteSpec spec)
        {
            if (part.Texture == null) return;
            
            var stageCount = spec.EvolutionStages.Length;
            var frameCount = spec.FramesPerAnimation;
            
            for (int stage = 0; stage < stageCount; stage++)
            {
                for (int frame = 0; frame < frameCount; frame++)
                {
                    var sourceX = frame * spec.Size.x;
                    var sourceY = stage * spec.Size.y;
                    var targetX = frame * spec.Size.x + part.Position.x;
                    var targetY = stage * spec.Size.y + part.Position.y;
                    
                    BlendTextureRegion(target, part.Texture, sourceX, sourceY, targetX, targetY, spec.Size.x, spec.Size.y, part.Template.BlendMode, part.Tint);
                }
            }
        }
        
        private static void BlendTextures(Texture2D target, Texture2D source, int offsetX, int offsetY, BlendMode blendMode, Color tint)
        {
            var sourcePixels = source.GetPixels();
            var targetPixels = target.GetPixels();
            
            for (int y = 0; y < source.height; y++)
            {
                for (int x = 0; x < source.width; x++)
                {
                    var targetX = offsetX + x;
                    var targetY = offsetY + y;
                    
                    if (targetX >= 0 && targetX < target.width && targetY >= 0 && targetY < target.height)
                    {
                        var sourceIndex = y * source.width + x;
                        var targetIndex = targetY * target.width + targetX;
                        
                        var sourceColor = sourcePixels[sourceIndex] * tint;
                        var targetColor = targetPixels[targetIndex];
                        
                        targetPixels[targetIndex] = BlendColors(sourceColor, targetColor, blendMode);
                    }
                }
            }
            
            target.SetPixels(targetPixels);
        }
        
        private static void BlendTextureRegion(Texture2D target, Texture2D source, int sourceX, int sourceY, int targetX, int targetY, int width, int height, BlendMode blendMode, Color tint)
        {
            var sourcePixels = source.GetPixels(sourceX, sourceY, width, height);
            var targetPixels = target.GetPixels(targetX, targetY, width, height);
            
            for (int i = 0; i < sourcePixels.Length; i++)
            {
                var sourceColor = sourcePixels[i] * tint;
                var targetColor = targetPixels[i];
                
                targetPixels[i] = BlendColors(sourceColor, targetColor, blendMode);
            }
            
            target.SetPixels(targetX, targetY, width, height, targetPixels);
        }
        
        private static Color BlendColors(Color source, Color target, BlendMode blendMode)
        {
            if (source.a == 0) return target;
            if (target.a == 0) return source;
            
            return blendMode switch
            {
                BlendMode.Normal => Color.Lerp(target, source, source.a),
                BlendMode.Multiply => new Color(source.r * target.r, source.g * target.g, source.b * target.b, Mathf.Max(source.a, target.a)),
                BlendMode.Screen => new Color(1f - (1f - source.r) * (1f - target.r), 1f - (1f - source.g) * (1f - target.g), 1f - (1f - source.b) * (1f - target.b), Mathf.Max(source.a, target.a)),
                BlendMode.Add => new Color(Mathf.Min(source.r + target.r, 1f), Mathf.Min(source.g + target.g, 1f), Mathf.Min(source.b + target.b, 1f), Mathf.Max(source.a, target.a)),
                _ => Color.Lerp(target, source, source.a)
            };
        }
        
        private static void CopyTextureToSheet(Texture2D sheet, Texture2D source, int offsetX, int offsetY)
        {
            var pixels = source.GetPixels();
            sheet.SetPixels(offsetX, offsetY, source.width, source.height, pixels);
        }
        
        private static int GetFrameCount(SpriteSpec spec)
        {
            return spec.GenerateEvolutionChain ? spec.FramesPerAnimation : spec.AnimationSets.Length * 4; // 4 frames per animation set
        }
        
        private static string GenerateProvenanceHash(string seed, SpriteSpec spec)
        {
            var combined = $"{seed}{spec.Archetype}{spec.Genre}{spec.Faculty}{spec.Rarity}";
            return System.Security.Cryptography.MD5.Create()
                .ComputeHash(System.Text.Encoding.UTF8.GetBytes(combined))
                .Aggregate("", (s, b) => s + b.ToString("x2"));
        }
        
        private static SpriteAnimationData GenerateCompatibleAnimationData(SpriteSpec spec, ModularSpriteResult result)
        {
            var frameCount = GetFrameCount(spec);
            var frameRects = new Rect[frameCount];
            var frameDurations = new float[frameCount];
            
            for (int i = 0; i < frameCount; i++)
            {
                frameRects[i] = new Rect(i * spec.Size.x, 0, spec.Size.x, spec.Size.y);
                frameDurations[i] = 1f / 8f; // 8 FPS
            }
            
            return new SpriteAnimationData
            {
                AnimationType = spec.AnimationSets.Length > 0 ? spec.AnimationSets[0] : AnimationSet.Idle,
                FrameRects = frameRects,
                FrameDurations = frameDurations,
                Pivot = new Vector2(0.5f, 0f),
                LoopAnimation = true,
                EvolutionStages = spec.GenerateEvolutionChain ? spec.EvolutionStages.Select(s => s.ToString()).ToArray() : new string[0],
                FramesPerStage = spec.GenerateEvolutionChain ? spec.FramesPerAnimation : 1
            };
        }
        
        private static NFTMetadata GenerateNFTMetadata(SpriteSpec spec, string seed)
        {
            // Use existing metadata generation logic
            return new NFTMetadata
            {
                Name = $"{spec.Genre} {spec.Archetype}",
                Description = $"Modular {spec.Archetype} from the {spec.Genre} realm",
                Image = $"ipfs://placeholder/{spec.TokenId}/sheet.png",
                AnimationUrl = $"ipfs://placeholder/{spec.TokenId}/animation.mp4",
                Attributes = new List<Dictionary<string, object>>
                {
                    new() { { "trait_type", "Archetype" }, { "value", spec.Archetype.ToString() } },
                    new() { { "trait_type", "Genre" }, { "value", spec.Genre.ToString() } },
                    new() { { "trait_type", "Rarity" }, { "value", spec.Rarity.ToString() } },
                    new() { { "trait_type", "Modular" }, { "value", "Yes" } }
                }
            };
        }
    }
    
    /// <summary>
    /// Export format for rigged animations
    /// </summary>
    public enum RiggedExportFormat
    {
        Spine,
        DragonBones
    }
    
    /// <summary>
    /// Extension methods for string manipulation
    /// </summary>
    public static class StringExtensions
    {
        public static string ToTitleCase(this string input)
        {
            if (string.IsNullOrEmpty(input)) return string.Empty;
            
            var words = input.Split(' ');
            for (int i = 0; i < words.Length; i++)
            {
                if (words[i].Length > 0)
                {
                    words[i] = char.ToUpper(words[i][0]) + words[i].Substring(1).ToLower();
                }
            }
            
            return string.Join(" ", words);
        }
    }
}