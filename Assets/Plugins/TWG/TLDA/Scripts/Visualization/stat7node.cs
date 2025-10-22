using UnityEngine;
using System.Collections.Generic;
using System;
using UnityEngine.Serialization;

// Note: Newtonsoft.Json may need to be installed via Package Manager
// For now, we'll use Unity's built-in JsonUtility with a wrapper

/// <summary>
/// STAT7 Node represents a single entity in the Mind Castle visualization.
/// Implements the full LUCA entity schema with 7-dimensional addressing.
/// Based on schemas:
/// - STAT7_MUTABILITY_CONTRACT.json
/// - LUCA.json
/// - LUCA_ENTITY_SCHEMA.json
/// </summary>
[System.Serializable]
public class Stat7Node : MonoBehaviour
{
    [Header("Core Identity")]
    [SerializeField] private string entityId;
    [FormerlySerializedAs("entityType")] [SerializeField] private Stat7EType stat7eType;
    [SerializeField] private string createdAt;

    [Header("STAT7 Coordinates")]
    [SerializeField] private Stat7Coordinate coordinates;

    [Header("Visualization")]
    [SerializeField] private int luminosityLevel = 0;
    [SerializeField] private string realityBranch = "PRIMARY";
    [SerializeField] private bool isSelected = false;
    [SerializeField] private bool isHovered = false;

    [Header("State Data")]
    [SerializeField] private EntityState entityState;

    // Runtime data
    private Stat7Manifestation _currentManifestation;
    private List<Stat7Node> _adjacentNodes = new List<Stat7Node>();
    private List<EntanglementLink> _entanglementLinks = new List<EntanglementLink>();

    // Visualization components
    private Renderer _nodeRenderer;
    private Collider _nodeCollider;
    private Material _originalMaterial;
    private Material _hoverMaterial;
    private Material _selectedMaterial;

    #region Data Structures

    [System.Serializable]
    public enum Stat7EType
    {
        Concept,
        Artifact,
        Agent,
        Lineage,
        Adjacency,
        Horizon,
        Fragment
    }

    [System.Serializable]
    public enum Realm
    {
        Void,
        Data,
        Narrative,
        System,
        Faculty,
        Event,
        Pattern
    }

    [System.Serializable]
    public enum Horizon
    {
        Genesis,
        Emergence,
        Peak,
        Decay,
        Crystallization
    }

    [System.Serializable]
    public struct Stat7Coordinate
    {
        public Realm realm;
        public string lineage;
        public List<string> adjacency;
        public Horizon horizon;
        [Range(0f, 1f)] public float resonance;
        public float velocity;
        public float density;

        public string GetStat7Address()
        {
            string adjacencyHash = ComputeAdjacencyHash();
            return $"stat7://{realm}/{lineage}/{adjacencyHash}/{horizon}?r={resonance:F8}&v={velocity:F8}&d={density:F8}";
        }

        private string ComputeAdjacencyHash()
        {
            if (adjacency == null || adjacency.Count == 0)
                return "da39a3ee5e6b4b0d3255bfef95601890afd80709"; // Empty SHA-256

            var sorted = new List<string>(adjacency);
            sorted.Sort();
            string combined = string.Join("", sorted);
            using (var sha256 = System.Security.Cryptography.SHA256.Create())
            {
                byte[] hashBytes = sha256.ComputeHash(System.Text.Encoding.UTF8.GetBytes(combined));
                return BitConverter.ToString(hashBytes).Replace("-", "").Substring(0, 64);
            }
        }
    }

    [System.Serializable]
    public class EntityState
    {
        public string content;
        public string phase;
        public bool bootstrap;
        public Dictionary<string, object> CustomData = new Dictionary<string, object>();
    }

    [System.Serializable]
    public class EntanglementLink
    {
        public string targetIdentityCoreId;
        [Range(0f, 1f)] public float resonanceStrength;
        public EntanglementType entanglementType;
        [Range(0f, 1f)] public float confidence;
    }

    public enum EntanglementType
    {
        Causal,
        Semantic,
        Structural,
        Narrative
    }

    [System.Serializable]
    public class Stat7Manifestation
    {
        public string realityBranch;
        public string timestamp;
        public int luminosityLevel;
        public Stat7Coordinate coordinates;
        public string canonicalHash;
        public string stat7Address;
        public string chainIntegrityHash;
        public EntityState state;
        public List<EntanglementLink> entanglementLinks;
    }

    #endregion

    #region Unity Lifecycle

    void Awake()
    {
        InitializeComponents();
        GenerateIdentityIfMissing();
    }

    void Start()
    {
        InitializeVisualization();
        LoadOrCreateManifestation();
    }

    void Update()
    {
        UpdateVisualizationState();
        HandleUserInteractions();
    }

    #endregion

    #region Initialization

    void InitializeComponents()
    {
        _nodeRenderer = GetComponent<Renderer>();
        _nodeCollider = GetComponent<Collider>();

        if (_nodeRenderer == null)
        {
            Debug.LogWarning($"STAT7Node {entityId} missing Renderer component", this);
        }

        if (_nodeCollider == null)
        {
            Debug.LogWarning($"STAT7Node {entityId} missing Collider component", this);
        }
    }

    void GenerateIdentityIfMissing()
    {
        if (string.IsNullOrEmpty(entityId))
        {
            entityId = $"entity-{Guid.NewGuid().ToString().Substring(0, 8)}";
        }

        if (string.IsNullOrEmpty(createdAt))
        {
            createdAt = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffZ");
        }

        if (coordinates.realm == 0 && string.IsNullOrEmpty(coordinates.lineage))
        {
            // Default to void realm with lineage 0 (like LUCA)
            coordinates.realm = Realm.Void;
            coordinates.lineage = "0";
            if (coordinates.adjacency == null)
                coordinates.adjacency = new List<string>();
            coordinates.horizon = Horizon.Genesis;
            coordinates.resonance = 1.0f;
            coordinates.velocity = 0.0f;
            coordinates.density = 0.0f;
        }
    }

    void InitializeVisualization()
    {
        if (_nodeRenderer != null)
        {
            _originalMaterial = _nodeRenderer.material;

            // Create materials for different states
            _hoverMaterial = new Material(_originalMaterial);
            _hoverMaterial.color = Color.yellow;

            _selectedMaterial = new Material(_originalMaterial);
            _selectedMaterial.color = Color.cyan;
        }

        UpdateNodeScale();
        UpdateNodeColor();
    }

    void LoadOrCreateManifestation()
    {
        _currentManifestation = new Stat7Manifestation
        {
            realityBranch = realityBranch,
            timestamp = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffZ"),
            luminosityLevel = luminosityLevel,
            coordinates = coordinates,
            stat7Address = coordinates.GetStat7Address(),
            state = entityState ?? new EntityState(),
            entanglementLinks = _entanglementLinks
        };

        _currentManifestation.canonicalHash = ComputeCanonicalHash();
        _currentManifestation.chainIntegrityHash = ComputeChainIntegrityHash();
    }

    #endregion

    #region Visualization

    void UpdateVisualizationState()
    {
        UpdateNodeScale();
        UpdateNodeColor();
        UpdateAdjacencyLines();
    }

    void UpdateNodeScale()
    {
        // Scale based on luminosity (0-7)
        float baseScale = 1.0f;
        float luminosityScale = Mathf.Pow(1.2f, luminosityLevel);
        transform.localScale = Vector3.one * baseScale * luminosityScale;
    }

    void UpdateNodeColor()
    {
        if (_nodeRenderer == null) return;

        Color targetColor = GetColorForRealm(coordinates.realm);

        if (isSelected)
        {
            _nodeRenderer.material = _selectedMaterial;
        }
        else if (isHovered)
        {
            _nodeRenderer.material = _hoverMaterial;
        }
        else
        {
            _nodeRenderer.material.color = targetColor;
        }
    }

    Color GetColorForRealm(Realm realm)
    {
        switch (realm)
        {
            case Realm.Void: return Color.black;
            case Realm.Data: return Color.blue;
            case Realm.Narrative: return Color.green;
            case Realm.System: return Color.red;
            case Realm.Faculty: return Color.magenta;
            case Realm.Event: return Color.orange;
            case Realm.Pattern: return Color.white;
            default: return Color.gray;
        }
    }

    void UpdateAdjacencyLines()
    {
        // This 👀would render lines to adjacent nodes
        // Implementation depends on your line rendering system
    }

    #endregion

    #region User Interaction

    void HandleUserInteractions()
    {
        // Handle zoom-based detail level changes
        float scroll = Input.GetAxis("Mouse ScrollWheel");
        if (Mathf.Abs(scroll) > 0.01f && isSelected)
        {
            HandleZoomInteraction(scroll);
        }
    }

    void HandleZoomInteraction(float scrollDelta)
    {
        // Navigate through different levels of detail
        // This implements the zoom hierarchy mentioned in the original comment
        luminosityLevel = Mathf.Clamp(luminosityLevel + (scrollDelta > 0 ? 1 : -1), 0, 7);
        UpdateVisualizationState();
    }

    void OnMouseEnter()
    {
        isHovered = true;
    }

    void OnMouseExit()
    {
        isHovered = false;
    }

    void OnMouseDown()
    {
        isSelected = true;
        Debug.Log($"Selected STAT7 Node: {entityId} at {coordinates.GetStat7Address()}");
    }

    void OnMouseUp()
    {
        // Could implement drag release logic here
    }

    void OnMouseDrag()
    {
        if (isSelected)
        {
            // Implement node dragging in 3D space
            // This 👀would update coordinates based on mouse movement
        }
    }

    #endregion

    #region STAT7 Operations

    public void AddAdjacency(Stat7Node targetNode)
    {
        if (targetNode == null) return;

        if (!_adjacentNodes.Contains(targetNode))
        {
            _adjacentNodes.Add(targetNode);

            if (coordinates.adjacency == null)
                coordinates.adjacency = new List<string>();

            coordinates.adjacency.Add(targetNode.entityId);

            // Create entanglement link
            var link = new EntanglementLink
            {
                targetIdentityCoreId = targetNode.entityId,
                resonanceStrength = 0.5f,
                entanglementType = EntanglementType.Structural,
                confidence = 1.0f
            };

            if (_entanglementLinks == null)
                _entanglementLinks = new List<EntanglementLink>();

            _entanglementLinks.Add(link);

            UpdateManifestation();
        }
    }

    public void UpdateLuminosity(int newLevel)
    {
        luminosityLevel = Mathf.Clamp(newLevel, 0, 7);
        _currentManifestation.luminosityLevel = luminosityLevel;
        UpdateManifestation();
    }

    void UpdateResonance(float newResonance)
    {
        coordinates.resonance = Mathf.Clamp01(newResonance);
        UpdateManifestation();
    }

    void UpdateVelocity(float newVelocity)
    {
        coordinates.velocity = newVelocity;
        UpdateManifestation();
    }

    void UpdateDensity(float newDensity)
    {
        coordinates.density = newDensity;
        UpdateManifestation();
    }

    void AdvanceHorizon()
    {
        // Advance through horizon states
        if (coordinates.horizon < Horizon.Crystallization)
        {
            coordinates.horizon++;
            UpdateManifestation();
        }
    }

    #endregion

    #region Data Management

    void UpdateManifestation()
    {
        _currentManifestation.timestamp = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffZ");
        _currentManifestation.coordinates = coordinates;
        _currentManifestation.stat7Address = coordinates.GetStat7Address();
        _currentManifestation.canonicalHash = ComputeCanonicalHash();
        _currentManifestation.chainIntegrityHash = ComputeChainIntegrityHash();
    }

    string ComputeCanonicalHash()
    {
        // Create canonical string representation and hash it
        string canonicalString = $"{_currentManifestation.realityBranch}|{_currentManifestation.timestamp}|{_currentManifestation.luminosityLevel}|{_currentManifestation.stat7Address}";
        using (var sha256 = System.Security.Cryptography.SHA256.Create())
        {
            byte[] hashBytes = sha256.ComputeHash(System.Text.Encoding.UTF8.GetBytes(canonicalString));
            return BitConverter.ToString(hashBytes).Replace("-", "").ToLower();
        }
    }

    string ComputeChainIntegrityHash()
    {
        // 👀Simplified chain integrity hash
        // In full implementation, this would chain with previous events
        return ComputeCanonicalHash();
    }

    string SaveToJson()
    {
        var saveData = new Stat7SaveData
        {
            entityId = entityId,
            entityType = stat7eType.ToString(),
            createdAt = createdAt,
            coordinates = coordinates,
            luminosityLevel = luminosityLevel,
            realityBranch = realityBranch,
            entityState = entityState,
            position = transform.position,
            rotation = transform.rotation,
            scale = transform.localScale
        };

        return JsonUtility.ToJson(saveData, true);
    }

    void LoadFromJson(string json)
    {
        try
        {
            var saveData = JsonUtility.FromJson<Stat7SaveData>(json);
            if (saveData != null)
            {
                entityId = saveData.entityId;
                if (System.Enum.TryParse<Stat7EType>(saveData.entityType, out var parsedType))
                    stat7eType = parsedType;
                    createdAt = saveData.createdAt;
                    coordinates = saveData.coordinates;
                    luminosityLevel = saveData.luminosityLevel;
                    realityBranch = saveData.realityBranch;
                    entityState = saveData.entityState;

                    // Update Unity transform
                    transform.position = saveData.position;
                    transform.rotation = saveData.rotation;
                    transform.localScale = saveData.scale;

                    // Update manifestation
                    LoadOrCreateManifestation();
            }
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to load STAT7 node from JSON: {e.Message}", this);
        }
    }

    #endregion

    #region Cleanup

    void OnDestroy()
    {
        // Clean up materials
        if (_hoverMaterial != null) Destroy(_hoverMaterial);
        if (_selectedMaterial != null) Destroy(_selectedMaterial);
    }

    void OnTriggerEnter(Collider other)
    {
        Stat7Node otherNode = other.GetComponent<Stat7Node>();
        if (otherNode != null && otherNode != this)
        {
            // Could implement proximity-based interactions
            Debug.Log($"STAT7 Node {entityId} in proximity to {otherNode.entityId}");
        }
    }

    void OnTriggerExit(Collider other)
    {
        Stat7Node otherNode = other.GetComponent<Stat7Node>();
        if (otherNode != null && otherNode != this)
        {
            // Clean up proximity interactions
        }
    }

    #endregion

    #region Public API

    public string EntityId => entityId;
    public Stat7EType Stat7eType => stat7eType;
    public Stat7Coordinate Coordinates => coordinates;
    public int LuminosityLevel => luminosityLevel;
    public string RealityBranch => realityBranch;
    public bool IsSelected => isSelected;
    public List<Stat7Node> AdjacentNodes => _adjacentNodes;
    public string Stat7Address => coordinates.GetStat7Address();

    void SetSelected(bool selected)
    {
        isSelected = selected;
    }

    public void SetEntityState(EntityState newState)
    {
        entityState = newState;
        UpdateManifestation();
    }

    #endregion

    /// <summary>
    /// Serializable data structure for saving/loading STAT7 nodes
    /// </summary>
    [System.Serializable]
    public class Stat7SaveData
    {
        public string entityId;
        public string entityType;
        public string createdAt;
        public Stat7Node.Stat7Coordinate coordinates;
        public int luminosityLevel;
        public string realityBranch;
        public Stat7Node.EntityState entityState;
        public Vector3 position;
        public Quaternion rotation;
        public Vector3 scale;
    }
}
