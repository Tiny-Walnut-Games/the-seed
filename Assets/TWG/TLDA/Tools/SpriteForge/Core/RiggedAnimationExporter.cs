using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace TWG.TLDA.SpriteForge
{
    /// <summary>
    /// Rigged animation exporter for Spine and DragonBones compatibility
    /// KeeperNote: Exports sprite parts with bone structure for skeletal animation
    /// </summary>
    public static class RiggedAnimationExporter
    {
        /// <summary>
        /// Export sprite parts as rigged animation data compatible with Spine
        /// </summary>
        public static SpineAnimationData ExportToSpine(ModularSpriteResult spriteResult, SpriteSpec spec)
        {
            var spineData = new SpineAnimationData
            {
                Version = "4.1",
                Hash = GenerateSpineHash(spriteResult),
                Skeleton = CreateSpineSkeleton(spec),
                Bones = CreateSpineBones(spec.Archetype),
                Slots = CreateSpineSlots(spriteResult.Parts),
                Skins = CreateSpineSkins(spriteResult.Parts),
                Animations = CreateSpineAnimations(spriteResult, spec)
            };
            
            return spineData;
        }
        
        /// <summary>
        /// Export sprite parts as rigged animation data compatible with DragonBones
        /// </summary>
        public static DragonBonesData ExportToDragonBones(ModularSpriteResult spriteResult, SpriteSpec spec)
        {
            var dragonBonesData = new DragonBonesData
            {
                Version = "5.6",
                Name = $"{spec.Archetype}_{spec.Genre}",
                FrameRate = 24,
                Armatures = new[]
                {
                    CreateDragonBonesArmature(spriteResult, spec)
                }
            };
            
            return dragonBonesData;
        }
        
        /// <summary>
        /// Generate bone structure based on creature archetype
        /// </summary>
        public static BoneStructure GenerateBoneStructure(CreatureArchetype archetype)
        {
            return archetype switch
            {
                CreatureArchetype.Familiar => CreateFamiliarBones(),
                CreatureArchetype.Golem => CreateGolemBones(),
                CreatureArchetype.Wisp => CreateWispBones(),
                CreatureArchetype.Sentinel => CreateSentinelBones(),
                CreatureArchetype.Homunculus => CreateHomunculusBones(),
                CreatureArchetype.Automaton => CreateAutomatonBones(),
                CreatureArchetype.Drifter => CreateDrifterBones(),
                CreatureArchetype.Warder => CreateWarderBones(),
                _ => CreateFamiliarBones()
            };
        }
        
        /// <summary>
        /// Create animation sequences for different animation sets
        /// </summary>
        public static List<AnimationSequence> CreateAnimationSequences(ModularSpriteResult spriteResult, SpriteSpec spec)
        {
            var sequences = new List<AnimationSequence>();
            
            foreach (var animSet in spec.AnimationSets)
            {
                var sequence = CreateAnimationSequence(animSet, spriteResult, spec);
                sequences.Add(sequence);
            }
            
            return sequences;
        }
        
        private static string GenerateSpineHash(ModularSpriteResult spriteResult)
        {
            var combined = string.Join("", spriteResult.Parts.Select(p => p.PartId));
            return System.Security.Cryptography.MD5.Create()
                .ComputeHash(System.Text.Encoding.UTF8.GetBytes(combined))
                .Aggregate("", (s, b) => s + b.ToString("x2"));
        }
        
        private static SpineSkeleton CreateSpineSkeleton(SpriteSpec spec)
        {
            return new SpineSkeleton
            {
                Hash = spec.TokenId.GetHashCode().ToString(),
                Spine = "4.1.23",
                X = -spec.Size.x / 2f,
                Y = -spec.Size.y / 2f,
                Width = spec.Size.x,
                Height = spec.Size.y,
                Images = "./images/",
                Audio = "./audio/"
            };
        }
        
        private static List<SpineBone> CreateSpineBones(CreatureArchetype archetype)
        {
            var boneStructure = GenerateBoneStructure(archetype);
            var spineBones = new List<SpineBone>();
            
            foreach (var bone in boneStructure.Bones)
            {
                spineBones.Add(new SpineBone
                {
                    Name = bone.Name,
                    Parent = bone.Parent,
                    X = bone.Position.x,
                    Y = bone.Position.y,
                    Rotation = bone.Rotation,
                    ScaleX = bone.Scale.x,
                    ScaleY = bone.Scale.y,
                    Length = bone.Length
                });
            }
            
            return spineBones;
        }
        
        private static List<SpineSlot> CreateSpineSlots(List<PartInstance> parts)
        {
            var slots = new List<SpineSlot>();
            
            foreach (var part in parts.OrderBy(p => (int)p.Template.Layer))
            {
                slots.Add(new SpineSlot
                {
                    Name = $"slot_{part.Template.PartId}",
                    Bone = GetBoneForPart(part.Template.Type),
                    Attachment = part.Template.PartId,
                    Color = ColorToHex(Color.white),
                    Blend = ConvertBlendMode(part.Template.BlendMode)
                });
            }
            
            return slots;
        }
        
        private static Dictionary<string, SpineSkin> CreateSpineSkins(List<PartInstance> parts)
        {
            var defaultSkin = new SpineSkin
            {
                Attachments = new Dictionary<string, Dictionary<string, SpineAttachment>>()
            };
            
            foreach (var part in parts)
            {
                var slotName = $"slot_{part.Template.PartId}";
                if (!defaultSkin.Attachments.ContainsKey(slotName))
                {
                    defaultSkin.Attachments[slotName] = new Dictionary<string, SpineAttachment>();
                }
                
                defaultSkin.Attachments[slotName][part.Template.PartId] = new SpineAttachment
                {
                    Type = "region",
                    X = part.Template.Offset.x,
                    Y = part.Template.Offset.y,
                    Width = part.Template.Size.x,
                    Height = part.Template.Size.y,
                    ScaleX = 1f,
                    ScaleY = 1f,
                    Rotation = 0f
                };
            }
            
            return new Dictionary<string, SpineSkin> { { "default", defaultSkin } };
        }
        
        private static Dictionary<string, SpineAnimation> CreateSpineAnimations(ModularSpriteResult spriteResult, SpriteSpec spec)
        {
            var animations = new Dictionary<string, SpineAnimation>();
            
            foreach (var animSet in spec.AnimationSets)
            {
                var animation = CreateSpineAnimation(animSet, spriteResult, spec);
                animations[animSet.ToString().ToLower()] = animation;
            }
            
            return animations;
        }
        
        private static SpineAnimation CreateSpineAnimation(AnimationSet animSet, ModularSpriteResult spriteResult, SpriteSpec spec)
        {
            var animation = new SpineAnimation
            {
                Slots = new Dictionary<string, SpineSlotAnimation>(),
                Bones = new Dictionary<string, SpineBoneAnimation>()
            };
            
            // Create slot animations for texture swapping
            foreach (var part in spriteResult.Parts.Where(p => p.Template.IsAnimated))
            {
                var slotName = $"slot_{part.Template.PartId}";
                animation.Slots[slotName] = CreateSlotAnimation(part, animSet);
            }
            
            // Create bone animations for movement
            var boneStructure = GenerateBoneStructure(spec.Archetype);
            foreach (var bone in boneStructure.Bones)
            {
                if (ShouldAnimateBone(bone, animSet))
                {
                    animation.Bones[bone.Name] = CreateBoneAnimation(bone, animSet);
                }
            }
            
            return animation;
        }
        
        private static SpineSlotAnimation CreateSlotAnimation(PartInstance part, AnimationSet animSet)
        {
            var slotAnimation = new SpineSlotAnimation
            {
                Attachment = new List<SpineKeyframe>()
            };
            
            var frameDuration = 1f / part.Template.AnimationSpeed;
            
            for (int i = 0; i < part.Template.AnimationFrames; i++)
            {
                slotAnimation.Attachment.Add(new SpineKeyframe
                {
                    Time = i * frameDuration,
                    Name = $"{part.Template.PartId}_frame_{i}"
                });
            }
            
            return slotAnimation;
        }
        
        private static SpineBoneAnimation CreateBoneAnimation(Bone bone, AnimationSet animSet)
        {
            var boneAnimation = new SpineBoneAnimation();
            
            // Add animations based on animation set
            switch (animSet)
            {
                case AnimationSet.Idle:
                    boneAnimation = CreateIdleAnimation(bone);
                    break;
                case AnimationSet.Walk:
                    boneAnimation = CreateWalkAnimation(bone);
                    break;
                case AnimationSet.Cast:
                    boneAnimation = CreateCastAnimation(bone);
                    break;
                case AnimationSet.Emote:
                    boneAnimation = CreateEmoteAnimation(bone);
                    break;
            }
            
            return boneAnimation;
        }
        
        private static DragonBonesArmature CreateDragonBonesArmature(ModularSpriteResult spriteResult, SpriteSpec spec)
        {
            var boneStructure = GenerateBoneStructure(spec.Archetype);
            
            return new DragonBonesArmature
            {
                Name = $"{spec.Archetype}_armature",
                Type = "Armature",
                FrameRate = 24,
                Bones = boneStructure.Bones.Select(CreateDragonBone).ToList(),
                Slots = spriteResult.Parts.Select(CreateDragonSlot).ToList(),
                Skins = new List<DragonBonesSkin>
                {
                    CreateDragonSkin(spriteResult.Parts)
                },
                Animations = spec.AnimationSets.Select(a => CreateDragonAnimation(a, boneStructure)).ToList()
            };
        }
        
        private static DragonBonesBone CreateDragonBone(Bone bone)
        {
            return new DragonBonesBone
            {
                Name = bone.Name,
                Parent = bone.Parent,
                Transform = new DragonBonesTransform
                {
                    X = bone.Position.x,
                    Y = bone.Position.y,
                    SkX = bone.Rotation,
                    SkY = bone.Rotation,
                    ScX = bone.Scale.x,
                    ScY = bone.Scale.y
                }
            };
        }
        
        private static DragonBonesSlot CreateDragonSlot(PartInstance part)
        {
            return new DragonBonesSlot
            {
                Name = $"slot_{part.Template.PartId}",
                Parent = GetBoneForPart(part.Template.Type),
                ZOrder = (int)part.Template.Layer,
                BlendMode = ConvertBlendModeToDragonBones(part.Template.BlendMode)
            };
        }
        
        private static DragonBonesSkin CreateDragonSkin(List<PartInstance> parts)
        {
            return new DragonBonesSkin
            {
                Name = "default",
                Slots = parts.Select(p => new DragonBonesSlotSkin
                {
                    Name = $"slot_{p.Template.PartId}",
                    Displays = new List<DragonBonesDisplay>
                    {
                        new DragonBonesDisplay
                        {
                            Name = p.Template.PartId,
                            Type = "image",
                            Transform = new DragonBonesTransform
                            {
                                X = p.Template.Offset.x,
                                Y = p.Template.Offset.y,
                                ScX = 1f,
                                ScY = 1f
                            }
                        }
                    }
                }).ToList()
            };
        }
        
        private static DragonBonesAnimation CreateDragonAnimation(AnimationSet animSet, BoneStructure boneStructure)
        {
            return new DragonBonesAnimation
            {
                Name = animSet.ToString().ToLower(),
                Duration = GetAnimationDuration(animSet),
                PlayTimes = animSet == AnimationSet.Idle ? 0 : 1, // 0 = loop
                Bones = boneStructure.Bones
                    .Where(b => ShouldAnimateBone(b, animSet))
                    .Select(b => CreateDragonBoneAnimation(b, animSet))
                    .ToList()
            };
        }
        
        private static DragonBonesBoneAnimation CreateDragonBoneAnimation(Bone bone, AnimationSet animSet)
        {
            return new DragonBonesBoneAnimation
            {
                Name = bone.Name,
                TranslateFrames = CreateTranslateFrames(bone, animSet),
                RotateFrames = CreateRotateFrames(bone, animSet),
                ScaleFrames = CreateScaleFrames(bone, animSet)
            };
        }
        
        // Bone structure creation methods
        private static BoneStructure CreateFamiliarBones()
        {
            return new BoneStructure
            {
                Bones = new List<Bone>
                {
                    new Bone { Name = "root", Position = Vector2.zero, Parent = null },
                    new Bone { Name = "body", Position = new Vector2(0, 6), Parent = "root" },
                    new Bone { Name = "head", Position = new Vector2(0, 18), Parent = "body" },
                    new Bone { Name = "tail", Position = new Vector2(0, -6), Parent = "body" },
                    new Bone { Name = "left_ear", Position = new Vector2(-4, 4), Parent = "head" },
                    new Bone { Name = "right_ear", Position = new Vector2(4, 4), Parent = "head" }
                }
            };
        }
        
        private static BoneStructure CreateGolemBones()
        {
            return new BoneStructure
            {
                Bones = new List<Bone>
                {
                    new Bone { Name = "root", Position = Vector2.zero, Parent = null },
                    new Bone { Name = "torso", Position = new Vector2(0, 12), Parent = "root" },
                    new Bone { Name = "head", Position = new Vector2(0, 8), Parent = "torso" },
                    new Bone { Name = "left_arm", Position = new Vector2(-8, 6), Parent = "torso" },
                    new Bone { Name = "right_arm", Position = new Vector2(8, 6), Parent = "torso" },
                    new Bone { Name = "left_leg", Position = new Vector2(-4, -6), Parent = "root" },
                    new Bone { Name = "right_leg", Position = new Vector2(4, -6), Parent = "root" }
                }
            };
        }
        
        private static BoneStructure CreateWispBones()
        {
            return new BoneStructure
            {
                Bones = new List<Bone>
                {
                    new Bone { Name = "root", Position = Vector2.zero, Parent = null },
                    new Bone { Name = "core", Position = new Vector2(0, 12), Parent = "root" },
                    new Bone { Name = "trail_1", Position = new Vector2(-6, -3), Parent = "core" },
                    new Bone { Name = "trail_2", Position = new Vector2(6, -3), Parent = "core" },
                    new Bone { Name = "energy_field", Position = Vector2.zero, Parent = "core" }
                }
            };
        }
        
        private static BoneStructure CreateSentinelBones()
        {
            return new BoneStructure
            {
                Bones = new List<Bone>
                {
                    new Bone { Name = "root", Position = Vector2.zero, Parent = null },
                    new Bone { Name = "torso", Position = new Vector2(0, 16), Parent = "root" },
                    new Bone { Name = "head", Position = new Vector2(0, 12), Parent = "torso" },
                    new Bone { Name = "left_shoulder", Position = new Vector2(-6, 8), Parent = "torso" },
                    new Bone { Name = "right_shoulder", Position = new Vector2(6, 8), Parent = "torso" },
                    new Bone { Name = "left_weapon", Position = new Vector2(-4, 0), Parent = "left_shoulder" },
                    new Bone { Name = "right_weapon", Position = new Vector2(4, 0), Parent = "right_shoulder" },
                    new Bone { Name = "base", Position = new Vector2(0, -8), Parent = "root" }
                }
            };
        }
        
        private static BoneStructure CreateHomunculusBones()
        {
            return CreateFamiliarBones(); // Similar structure to familiar
        }
        
        private static BoneStructure CreateAutomatonBones()
        {
            return CreateGolemBones(); // Similar structure to golem
        }
        
        private static BoneStructure CreateDrifterBones()
        {
            return CreateWispBones(); // Similar structure to wisp
        }
        
        private static BoneStructure CreateWarderBones()
        {
            return CreateSentinelBones(); // Similar structure to sentinel
        }
        
        // Animation creation helpers
        private static SpineBoneAnimation CreateIdleAnimation(Bone bone)
        {
            return new SpineBoneAnimation
            {
                Rotate = new List<SpineRotateKeyframe>
                {
                    new SpineRotateKeyframe { Time = 0f, Value = 0f },
                    new SpineRotateKeyframe { Time = 1f, Value = 2f },
                    new SpineRotateKeyframe { Time = 2f, Value = 0f }
                }
            };
        }
        
        private static SpineBoneAnimation CreateWalkAnimation(Bone bone)
        {
            return new SpineBoneAnimation
            {
                Rotate = new List<SpineRotateKeyframe>
                {
                    new SpineRotateKeyframe { Time = 0f, Value = 0f },
                    new SpineRotateKeyframe { Time = 0.25f, Value = 5f },
                    new SpineRotateKeyframe { Time = 0.5f, Value = 0f },
                    new SpineRotateKeyframe { Time = 0.75f, Value = -5f },
                    new SpineRotateKeyframe { Time = 1f, Value = 0f }
                }
            };
        }
        
        private static SpineBoneAnimation CreateCastAnimation(Bone bone)
        {
            return new SpineBoneAnimation
            {
                Rotate = new List<SpineRotateKeyframe>
                {
                    new SpineRotateKeyframe { Time = 0f, Value = 0f },
                    new SpineRotateKeyframe { Time = 0.3f, Value = 15f },
                    new SpineRotateKeyframe { Time = 0.7f, Value = 15f },
                    new SpineRotateKeyframe { Time = 1f, Value = 0f }
                }
            };
        }
        
        private static SpineBoneAnimation CreateEmoteAnimation(Bone bone)
        {
            return new SpineBoneAnimation
            {
                Scale = new List<SpineScaleKeyframe>
                {
                    new SpineScaleKeyframe { Time = 0f, X = 1f, Y = 1f },
                    new SpineScaleKeyframe { Time = 0.2f, X = 1.2f, Y = 1.2f },
                    new SpineScaleKeyframe { Time = 1f, X = 1f, Y = 1f }
                }
            };
        }
        
        // Helper methods
        private static string GetBoneForPart(PartType partType)
        {
            return partType switch
            {
                PartType.Head => "head",
                PartType.Eyes => "head",
                PartType.Body => "body",
                PartType.Limbs => "body",
                PartType.Wings => "body",
                PartType.Tail => "tail",
                PartType.Accessories => "head",
                PartType.Effects => "core",
                _ => "root"
            };
        }
        
        private static string ConvertBlendMode(BlendMode blendMode)
        {
            return blendMode switch
            {
                BlendMode.Normal => "normal",
                BlendMode.Multiply => "multiply",
                BlendMode.Screen => "screen",
                BlendMode.Add => "additive",
                _ => "normal"
            };
        }
        
        private static string ConvertBlendModeToDragonBones(BlendMode blendMode)
        {
            return blendMode switch
            {
                BlendMode.Normal => "normal",
                BlendMode.Add => "add",
                _ => "normal"
            };
        }
        
        private static string ColorToHex(Color color)
        {
            return $"{(int)(color.r * 255):x2}{(int)(color.g * 255):x2}{(int)(color.b * 255):x2}{(int)(color.a * 255):x2}";
        }
        
        private static bool ShouldAnimateBone(Bone bone, AnimationSet animSet)
        {
            return animSet switch
            {
                AnimationSet.Idle => bone.Name.Contains("tail") || bone.Name.Contains("ear") || bone.Name.Contains("trail"),
                AnimationSet.Walk => bone.Name.Contains("leg") || bone.Name.Contains("arm") || bone.Name.Contains("body"),
                AnimationSet.Cast => bone.Name.Contains("arm") || bone.Name.Contains("head") || bone.Name.Contains("weapon"),
                AnimationSet.Emote => bone.Name.Contains("head") || bone.Name.Contains("core"),
                _ => false
            };
        }
        
        private static float GetAnimationDuration(AnimationSet animSet)
        {
            return animSet switch
            {
                AnimationSet.Idle => 2f,
                AnimationSet.Walk => 1f,
                AnimationSet.Cast => 1.5f,
                AnimationSet.Emote => 1f,
                _ => 1f
            };
        }
        
        private static List<DragonBonesTranslateFrame> CreateTranslateFrames(Bone bone, AnimationSet animSet)
        {
            // TODO: Create translation keyframes based on animation set
            return new List<DragonBonesTranslateFrame>();
        }
        
        private static List<DragonBonesRotateFrame> CreateRotateFrames(Bone bone, AnimationSet animSet)
        {
            // TODO: Create rotation keyframes based on animation set
            return new List<DragonBonesRotateFrame>();
        }
        
        private static List<DragonBonesScaleFrame> CreateScaleFrames(Bone bone, AnimationSet animSet)
        {
            // TODO: Create scale keyframes based on animation set
            return new List<DragonBonesScaleFrame>();
        }
    }
}