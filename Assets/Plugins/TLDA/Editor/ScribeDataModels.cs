#if UNITY_EDITOR
using System;
using System.Collections.Generic;

namespace TinyWalnutGames.TLDA.Editor
{
    /// <summary>
    /// Data models for the TLDL Scribe system
    /// </summary>
    
    [Serializable]
    public class Discovery
    {
        public string Category = "";
        public string KeyFinding = "";
        public string Impact = "";
        public string Evidence = "";
        public string RootCause = "";
        public string PatternRecognition = "";
        public bool Foldout = true;
    }

    [Serializable]
    public class ActionItem
    {
        public string Name = "";
        public string What = "";
        public string Why = "";
        public string How = "";
        public string Result = "";
        public string FilesChanged = "";
        public string Validation = "";
        public bool Foldout = true;
    }

    public class TemplateInfo
    {
        public string Key;
        public string Title;
        public string File;
        public string AbsPath;
    }

    public enum Complexity { Low, Medium, High }
    public enum Impact { Low, Medium, High, Critical }
    public enum Status { Draft, InProgress, Complete, Archived }

    /// <summary>
    /// Holds all form data for the TLDL Scribe
    /// </summary>
    [Serializable]
    public class ScribeFormData
    {
        // Header fields
        public string Title = "";
        public string Author = "@copilot";
        public string Context = "";
        public string Summary = "";
        public string TagsCsv = "";

        // Section toggles
        public bool IncludeDiscoveries = true;
        public bool IncludeActions = true;
        public bool IncludeTechnicalDetails = true;
        public bool IncludeDependencies = true;
        public bool IncludeLessons = true;
        public bool IncludeNextSteps = true;
        public bool IncludeReferences = true;
        public bool IncludeDevTimeTravel = true;
        public bool IncludeMetadata = true;
        public bool IncludeTerminalProof = false;
        public bool IncludeImages = false;

        // Dynamic lists
        public List<Discovery> Discoveries = new() { new Discovery { Category = "Discovery Category 1" } };
        public List<ActionItem> Actions = new() { new ActionItem { Name = "Action 1" } };

        // Technical details
        public string CodeChanges = "";
        public string ConfigUpdates = "";
        public string TerminalProof = "";

        // Dependencies
        public string DepsAdded = "";
        public string DepsRemoved = "";
        public string DepsUpdated = "";

        // Lessons learned
        public string LessonsWorked = "";
        public string LessonsImprove = "";
        public string LessonsGaps = "";

        // Next steps
        public string NextImmediate = "";
        public string NextMedium = "";
        public string NextLong = "";

        // References
        public string InternalLinks = "";
        public string ExternalResources = "";
        public List<string> ReferencePaths = new();

        // DevTimeTravel
        public string SnapshotId = "";
        public string Branch = "";
        public string CommitHash = "";
        public string Environment = "development";

        // Metadata
        public Complexity Complexity = Complexity.Medium;
        public Impact Impact = Impact.Critical;
        public string TeamMembers = "";
        public string Duration = "";
        public Status Status = Status.Draft;

        // Images
        public List<string> ImagePaths = new();
    }

    /// <summary>
    /// Centralized configuration for allowed file extensions
    /// </summary>
    public static class ScribeFileFilters
    {
        public static readonly HashSet<string> AllowedExts = new(StringComparer.OrdinalIgnoreCase)
        {
            ".md", ".markdown", ".txt", ".log", ".xml",
            // Image types (for navigator visibility)
            ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tga"
        };
        
        public static readonly HashSet<string> ImageExts = new(StringComparer.OrdinalIgnoreCase)
        {
            ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tga"
        };
    }
}
#endif
