using System;
using System.Collections.Generic;
using UnityEngine;

namespace TWG.TLDA.SpriteForge
{
    // ===== SHARED STRUCTURES =====
    
    /// <summary>
    /// Bone structure for skeletal animation
    /// </summary>
    [Serializable]
    public class BoneStructure
    {
        public List<Bone> Bones = new List<Bone>();
    }
    
    /// <summary>
    /// Individual bone definition
    /// </summary>
    [Serializable]
    public class Bone
    {
        public string Name;
        public string Parent;
        public Vector2 Position;
        public float Rotation;
        public Vector2 Scale = Vector2.one;
        public float Length = 10f;
    }
    
    /// <summary>
    /// Animation sequence data
    /// </summary>
    [Serializable]
    public class AnimationSequence
    {
        public string Name;
        public float Duration;
        public bool Loop;
        public List<BoneKeyframe> Keyframes = new List<BoneKeyframe>();
    }
    
    /// <summary>
    /// Keyframe for bone animation
    /// </summary>
    [Serializable]
    public class BoneKeyframe
    {
        public string BoneName;
        public float Time;
        public Vector2 Position;
        public float Rotation;
        public Vector2 Scale;
    }
    
    /// <summary>
    /// Part instance in a modular sprite
    /// </summary>
    [Serializable]
    public class PartInstance
    {
        public PartTemplate Template;
        public Texture2D Texture;
        public Vector2Int Position;
        public int ZOrder;
        public Color Tint = Color.white;
    }
    
    /// <summary>
    /// Result of modular sprite generation
    /// </summary>
    [Serializable]
    public class ModularSpriteResult
    {
        public List<PartInstance> Parts = new List<PartInstance>();
        public Texture2D CompositeTexture;
        public BoneStructure BoneStructure;
        public string Seed;
        public SpriteSpec Specification;
    }
    
    // ===== SPINE STRUCTURES =====
    
    /// <summary>
    /// Spine animation data structure
    /// </summary>
    [Serializable]
    public class SpineAnimationData
    {
        public string Version;
        public string Hash;
        public SpineSkeleton Skeleton;
        public List<SpineBone> Bones;
        public List<SpineSlot> Slots;
        public Dictionary<string, SpineSkin> Skins;
        public Dictionary<string, SpineAnimation> Animations;
    }
    
    [Serializable]
    public class SpineSkeleton
    {
        public string Hash;
        public string Spine;
        public float X;
        public float Y;
        public float Width;
        public float Height;
        public string Images;
        public string Audio;
    }
    
    [Serializable]
    public class SpineBone
    {
        public string Name;
        public string Parent;
        public float X;
        public float Y;
        public float Rotation;
        public float ScaleX = 1f;
        public float ScaleY = 1f;
        public float Length;
    }
    
    [Serializable]
    public class SpineSlot
    {
        public string Name;
        public string Bone;
        public string Attachment;
        public string Color = "ffffffff";
        public string Blend = "normal";
    }
    
    [Serializable]
    public class SpineSkin
    {
        public Dictionary<string, Dictionary<string, SpineAttachment>> Attachments;
    }
    
    [Serializable]
    public class SpineAttachment
    {
        public string Type = "region";
        public float X;
        public float Y;
        public float Width;
        public float Height;
        public float ScaleX = 1f;
        public float ScaleY = 1f;
        public float Rotation;
    }
    
    [Serializable]
    public class SpineAnimation
    {
        public Dictionary<string, SpineSlotAnimation> Slots;
        public Dictionary<string, SpineBoneAnimation> Bones;
    }
    
    [Serializable]
    public class SpineSlotAnimation
    {
        public List<SpineKeyframe> Attachment;
        public List<SpineColorKeyframe> Color;
    }
    
    [Serializable]
    public class SpineBoneAnimation
    {
        public List<SpineRotateKeyframe> Rotate;
        public List<SpineTranslateKeyframe> Translate;
        public List<SpineScaleKeyframe> Scale;
    }
    
    [Serializable]
    public class SpineKeyframe
    {
        public float Time;
        public string Name;
    }
    
    [Serializable]
    public class SpineColorKeyframe
    {
        public float Time;
        public string Color;
    }
    
    [Serializable]
    public class SpineRotateKeyframe
    {
        public float Time;
        public float Value;
    }
    
    [Serializable]
    public class SpineTranslateKeyframe
    {
        public float Time;
        public float X;
        public float Y;
    }
    
    [Serializable]
    public class SpineScaleKeyframe
    {
        public float Time;
        public float X;
        public float Y;
    }
    
    // ===== DRAGONBONES STRUCTURES =====
    
    /// <summary>
    /// DragonBones animation data structure
    /// </summary>
    [Serializable]
    public class DragonBonesData
    {
        public string Version;
        public string Name;
        public int FrameRate;
        public DragonBonesArmature[] Armatures;
    }
    
    [Serializable]
    public class DragonBonesArmature
    {
        public string Name;
        public string Type;
        public int FrameRate;
        public List<DragonBonesBone> Bones;
        public List<DragonBonesSlot> Slots;
        public List<DragonBonesSkin> Skins;
        public List<DragonBonesAnimation> Animations;
    }
    
    [Serializable]
    public class DragonBonesBone
    {
        public string Name;
        public string Parent;
        public DragonBonesTransform Transform;
    }
    
    [Serializable]
    public class DragonBonesSlot
    {
        public string Name;
        public string Parent;
        public int ZOrder;
        public string BlendMode = "normal";
    }
    
    [Serializable]
    public class DragonBonesSkin
    {
        public string Name;
        public List<DragonBonesSlotSkin> Slots;
    }
    
    [Serializable]
    public class DragonBonesSlotSkin
    {
        public string Name;
        public List<DragonBonesDisplay> Displays;
    }
    
    [Serializable]
    public class DragonBonesDisplay
    {
        public string Name;
        public string Type;
        public DragonBonesTransform Transform;
    }
    
    [Serializable]
    public class DragonBonesAnimation
    {
        public string Name;
        public float Duration;
        public int PlayTimes;
        public List<DragonBonesBoneAnimation> Bones;
    }
    
    [Serializable]
    public class DragonBonesBoneAnimation
    {
        public string Name;
        public List<DragonBonesTranslateFrame> TranslateFrames;
        public List<DragonBonesRotateFrame> RotateFrames;
        public List<DragonBonesScaleFrame> ScaleFrames;
    }
    
    [Serializable]
    public class DragonBonesTransform
    {
        public float X;
        public float Y;
        public float SkX; // Skew X (rotation)
        public float SkY; // Skew Y (rotation)
        public float ScX = 1f; // Scale X
        public float ScY = 1f; // Scale Y
    }
    
    [Serializable]
    public class DragonBonesTranslateFrame
    {
        public int Duration;
        public float X;
        public float Y;
        public string Curve;
    }
    
    [Serializable]
    public class DragonBonesRotateFrame
    {
        public int Duration;
        public float Rotate;
        public string Curve;
    }
    
    [Serializable]
    public class DragonBonesScaleFrame
    {
        public int Duration;
        public float X;
        public float Y;
        public string Curve;
    }
}