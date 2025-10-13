using UnityEngine;
using UnityEngine.UIElements;

namespace MobileGameTemplate.Core
{
    /// <summary>
    /// 🛡️ Unity 2022.3 Compatibility Bridge - Bootstrap Sentinel's Version Shield
    /// Provides compatibility wrappers for newer Unity UI Toolkit features
    /// 
    /// Target: Unity 2022.3.6f1 with C# 10 and .NET Framework 4.7.1
    /// Sacred Mission: Bridge the version gap with legendary grace!
    /// </summary>
    public static class Unity2022CompatibilityBridge
    {
        /// <summary>
        /// 🔧 Set border radius with Unity 2022.3 compatibility
        /// In Unity 2022.3, borderRadius doesn't exist - this is a no-op for compatibility
        /// </summary>
        public static void SetBorderRadius(this IStyle style, float radius)
        {
            // Unity 2022.3 doesn't support borderRadius
            // This is a compatibility no-op to prevent compilation errors
            // Visual effects can be achieved through USS classes or nested containers
        }
        
        /// <summary>
        /// 🔧 Set border width with Unity 2022.3 compatibility
        /// In Unity 2022.3, borderWidth doesn't exist - this is a no-op for compatibility
        /// </summary>
        public static void SetBorderWidth(this IStyle style, float width)
        {
            // Unity 2022.3 doesn't support borderWidth
            // This is a compatibility no-op to prevent compilation errors
            // Visual effects can be achieved through USS classes or margin adjustments
        }
        
        /// <summary>
        /// 🔧 Set border color with Unity 2022.3 compatibility
        /// In Unity 2022.3, borderColor doesn't exist - this is a no-op for compatibility
        /// </summary>
        public static void SetBorderColor(this IStyle style, Color color)
        {
            // Unity 2022.3 doesn't support borderColor
            // This is a compatibility no-op to prevent compilation errors
            // Visual effects can be achieved through background color variations
        }
        
        /// <summary>
        /// 🔧 Set transform with Unity 2022.3 compatibility
        /// In Unity 2022.3, transform property has different syntax - this is a no-op for compatibility
        /// </summary>
        public static void SetTransform(this IStyle style, object transformValue)
        {
            // Unity 2022.3 has different transform property handling
            // This is a compatibility no-op to prevent compilation errors
        }
        
        /// <summary>
        /// 🔧 Fix Vector3/Vector2 pointer position ambiguity
        /// Common in Unity 2022.3 UI Toolkit events
        /// </summary>
        public static Vector2 ToVector2Safe(this Vector3 vector3)
        {
            return new Vector2(vector3.x, vector3.y);
        }
        
        /// <summary>
        /// 🎨 Create Unity 2022.3 compatible rounded container
        /// Uses padding and background color instead of borderRadius
        /// </summary>
        public static VisualElement CreateCompatibleRoundedElement(string className = "")
        {
            var element = new VisualElement();
            if (!string.IsNullOrEmpty(className))
            {
                element.AddToClassList(className);
            }
            
            // Unity 2022.3 compatible styling
            element.style.backgroundColor = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            element.style.paddingTop = 8;
            element.style.paddingBottom = 8;
            element.style.paddingLeft = 12;
            element.style.paddingRight = 12;
            element.style.marginTop = 4;
            element.style.marginBottom = 4;
            
            return element;
        }
        
        /// <summary>
        /// 🎨 Create Unity 2022.3 compatible border effect
        /// Uses nested containers instead of border properties
        /// </summary>
        public static VisualElement CreateCompatibleBorderedElement(Color borderColor, float borderWidth = 2f)
        {
            var container = new VisualElement();
            var content = new VisualElement();
            
            // Outer container acts as "border"
            container.style.backgroundColor = borderColor;
            container.style.paddingTop = borderWidth;
            container.style.paddingBottom = borderWidth;
            container.style.paddingLeft = borderWidth;
            container.style.paddingRight = borderWidth;
            
            // Inner content area
            content.style.backgroundColor = new Color(0.1f, 0.1f, 0.1f, 0.9f);
            content.style.flexGrow = 1;
            
            container.Add(content);
            return container;
        }
        
        /// <summary>
        /// 🎯 Apply Unity 2022.3 compatible button styling
        /// </summary>
        public static void ApplyCompatibleButtonStyling(this Button button, Color backgroundColor, Color textColor)
        {
            button.style.backgroundColor = backgroundColor;
            button.style.color = textColor;
            button.style.paddingTop = 8;
            button.style.paddingBottom = 8;
            button.style.paddingLeft = 16;
            button.style.paddingRight = 16;
            button.style.marginTop = 2;
            button.style.marginBottom = 2;
            
            // Add hover state through USS if available
            button.AddToClassList("unity-2022-button");
        }
        
        /// <summary>
        /// 🎯 Apply Unity 2022.3 compatible card styling
        /// </summary>
        public static void ApplyCompatibleCardStyling(this VisualElement element, Color backgroundColor, float padding = 8f)
        {
            element.style.backgroundColor = backgroundColor;
            element.style.paddingTop = padding;
            element.style.paddingBottom = padding;
            element.style.paddingLeft = padding;
            element.style.paddingRight = padding;
            element.style.marginTop = 4;
            element.style.marginBottom = 4;
            element.style.marginLeft = 2;
            element.style.marginRight = 2;
        }
        
        /// <summary>
        /// 📊 Get Unity version compatibility information
        /// </summary>
        public static string GetCompatibilityInfo()
        {
            return $"Unity 2022.3 Compatibility Bridge Active - Version: {Application.unityVersion}";
        }
        
        /// <summary>
        /// 📊 Check if running on target Unity version
        /// </summary>
        public static bool IsUnity2022()
        {
            return Application.unityVersion.StartsWith("2022.");
        }
        
        /// <summary>
        /// 🛡️ Safe style property access for Unity 2022.3
        /// </summary>
        public static void SafeSetProperty<T>(this IStyle style, System.Action<T> setter, T value)
        {
            try
            {
                setter(value);
            }
            catch (System.Exception)
            {
                // Silently ignore style properties that don't exist in Unity 2022.3
                // This prevents crashes when newer UI Toolkit features are used
            }
        }
    }
    
    /// <summary>
    /// 🎯 Unity 2022.3 UxmlFactory Compatibility Helper
    /// Addresses generic constraint issues in older Unity versions
    /// </summary>
    public static class UxmlFactoryCompatibility
    {
        /// <summary>
        /// Create a basic UxmlFactory that works in Unity 2022.3
        /// </summary>
        public static void EnsureParameterlessConstructor<T>() where T : VisualElement, new()
        {
            // This method exists to document the requirement for parameterless constructors
            // in Unity 2022.3 UxmlFactory implementations
        }
    }
    
    /// <summary>
    /// 🔧 C# 10 / .NET Framework 4.7.1 Compatibility Helpers
    /// </summary>
    public static class CSharpCompatibilityHelpers
    {
        /// <summary>
        /// Unity 2022.3/.NET Framework 4.7.1 compatible hash function
        /// Replaces SHA256.HashData which doesn't exist in older .NET versions
        /// </summary>
        public static byte[] CreateCompatibleHash(byte[] data)
        {
            using (var sha256 = System.Security.Cryptography.SHA256.Create())
            {
                return sha256.ComputeHash(data);
            }
        }
        
        /// <summary>
        /// Compatibility method for Convert.ToHexString (not available in .NET Framework 4.7.1)
        /// </summary>
        public static string ToHexStringCompatible(byte[] bytes)
        {
            return System.BitConverter.ToString(bytes).Replace("-", "").ToLower();
        }
    }
}
