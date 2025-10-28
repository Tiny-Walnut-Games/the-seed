using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;
using System.Linq;
using System;
using UnityEngine.Serialization;
using Random = UnityEngine.Random;

/// <summary>
/// Complete MindCastle Scene Setup Script
/// Automatically creates a fully functional STAT7 entity visualization environment
/// Press play and everything works immediately - no manual setup required
/// </summary>
public class MindCastleSceneSetup : MonoBehaviour
{
    [Header("Scene Configuration")]
    [SerializeField] private bool autoSetupOnStart = true;
    [SerializeField] private bool createSampleEntities = true;
    [SerializeField] private int numberOfSampleEntities = 12;
    [SerializeField] private float spawnRadius = 10f;

    [Header("Visualization Settings")]
    [SerializeField] private Material nodeMaterial;
    [SerializeField] private Material lineMaterial;
    [SerializeField] private Color backgroundColor = new Color(0.05f, 0.05f, 0.1f);

    [Header("Camera Settings")]
    [SerializeField] private Vector3 cameraPosition = new Vector3(0, 5, -15);
    [SerializeField] private Vector3 cameraRotation = new Vector3(15, 0, 0);

    // Runtime references
    private Camera _mainCamera;
    private Light _mainLight;
    private GameObject _lineRendererParent;
    private List<Stat7Node> _allNodes = new List<Stat7Node>();
    private List<LineRenderer> _adjacencyLines = new List<LineRenderer>();

    // Entity templates for sample generation
    private EntityTemplate[] _entityTemplates;

    private void Start()
    {
        InitializeEntityTemplates();

        if (autoSetupOnStart)
        {
            SetupCompleteScene();
        }
    }

    private void InitializeEntityTemplates()
    {
        _entityTemplates = new EntityTemplate[]
        {
            new EntityTemplate("LUCA", Stat7Node.Stat7EType.Fragment, Stat7Node.Realm.Void, Vector3.zero),
            new EntityTemplate("Seed-Concept", Stat7Node.Stat7EType.Concept, Stat7Node.Realm.Narrative, new Vector3(-3, 0, 3)),
            new EntityTemplate("STAT7-Engine", Stat7Node.Stat7EType.Artifact, Stat7Node.Realm.System, new Vector3(3, 0, 3)),
            new EntityTemplate("Dev-Agent", Stat7Node.Stat7EType.Agent, Stat7Node.Realm.Faculty, new Vector3(0, 0, 5)),
            new EntityTemplate("Data-Store", Stat7Node.Stat7EType.Artifact, Stat7Node.Realm.Data, new Vector3(-5, 0, 0)),
            new EntityTemplate("Event-Log", Stat7Node.Stat7EType.Artifact, Stat7Node.Realm.Event, new Vector3(5, 0, 0)),
            new EntityTemplate("Pattern-Node", Stat7Node.Stat7EType.Concept, Stat7Node.Realm.Pattern, new Vector3(0, 0, -5)),
            new EntityTemplate("Lineage-Tracker", Stat7Node.Stat7EType.Lineage, Stat7Node.Realm.System, new Vector3(-3, 0, -3)),
            new EntityTemplate("Adjacency-Map", Stat7Node.Stat7EType.Adjacency, Stat7Node.Realm.Data, new Vector3(3, 0, -3)),
            new EntityTemplate("Horizon-Monitor", Stat7Node.Stat7EType.Horizon, Stat7Node.Realm.Faculty, new Vector3(-6, 0, 2)),
            new EntityTemplate("Resonance-Core", Stat7Node.Stat7EType.Concept, Stat7Node.Realm.Void, new Vector3(6, 0, 2)),
            new EntityTemplate("Velocity-Field", Stat7Node.Stat7EType.Artifact, Stat7Node.Realm.Pattern, new Vector3(0, 0, 7))
        };
    }

    /// <summary>
    /// Sets up the entire MindCastle scene with all necessary components
    /// </summary>
    [ContextMenu("Setup Complete MindCastle Scene")]
    public void SetupCompleteScene()
    {
        Debug.Log("🏰 Setting up MindCastle Scene...");

        // Clean up any existing setup
        CleanupExistingSetup();

        // Setup core scene components
        SetupCamera();
        SetupLighting();
        SetupEnvironment();

        // Create visualization infrastructure
        CreateLineRendererParent();

        // Create entities
        if (createSampleEntities)
        {
            CreateSampleEntities();
        }

        // Create relationships
        CreateEntityRelationships();

        // Setup UI controls
        SetupUIControls();

        // Finalize scene
        FinalizeScene();

        Debug.Log($"✅ MindCastle Scene Setup Complete! Created {_allNodes.Count} entities with {_adjacencyLines.Count} relationships");
    }

    #region Scene Setup

    private void CleanupExistingSetup()
    {
        // Find and destroy existing MindCastle objects
        var existingNodes = FindObjectsByType<Stat7Node>(FindObjectsSortMode.None);
        foreach (var node in existingNodes)
        {
            if (node.gameObject.name.StartsWith("MindCastle_"))
            {
                DestroyImmediate(node.gameObject);
            }
        }

        var existingLineRenderers = FindObjectsByType<LineRenderer>(FindObjectsSortMode.None);
        foreach (var line in existingLineRenderers)
        {
            if (line.gameObject.name.StartsWith("AdjacencyLine_"))
            {
                DestroyImmediate(line.gameObject);
            }
        }

        var existingSetup = FindFirstObjectByType<MindCastleSceneSetup>();
        if (existingSetup != null && existingSetup != this)
        {
            DestroyImmediate(existingSetup.gameObject);
        }

        _allNodes.Clear();
        _adjacencyLines.Clear();
    }

    private void SetupCamera()
    {
        // Find or create main camera
        _mainCamera = Camera.main;
        if (_mainCamera == null)
        {
            var cameraObj = new GameObject("Main Camera");
            _mainCamera = cameraObj.AddComponent<Camera>();
            cameraObj.tag = "MainCamera";
        }

        // Position camera for optimal viewing
        _mainCamera.transform.position = cameraPosition;
        _mainCamera.transform.rotation = Quaternion.Euler(cameraRotation);

        // Configure camera settings
        _mainCamera.backgroundColor = backgroundColor;
        _mainCamera.farClipPlane = 100f;

        // Add camera controller for interaction
        if (_mainCamera.GetComponent<CameraController>() == null)
        {
            _mainCamera.gameObject.AddComponent<CameraController>();
        }
    }

    private void SetupLighting()
    {
        // Setup main directional light
        _mainLight = FindFirstObjectByType<Light>();
        if (_mainLight == null)
        {
            var lightObj = new GameObject("Main Light");
            _mainLight = lightObj.AddComponent<Light>();
            _mainLight.type = LightType.Directional;
        }

        _mainLight.transform.rotation = Quaternion.Euler(50, -30, 0);
        _mainLight.intensity = 1.2f;
        _mainLight.color = Color.white;

        // Add ambient lighting
        RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
        RenderSettings.ambientLight = new Color(0.3f, 0.3f, 0.4f);
    }

    private void SetupEnvironment()
    {
        // Create ground plane for reference
        var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ground.name = "MindCastle_Ground";
        ground.transform.position = Vector3.zero;
        ground.transform.localScale = Vector3.one * 5f;

        // Make ground semi-transparent and non-interactive
        var groundRenderer = ground.GetComponent<Renderer>();
        var groundMaterial = new Material(Shader.Find("Standard"));
        groundMaterial.color = new Color(0.1f, 0.1f, 0.2f, 0.3f);
        groundMaterial.SetFloat("_Metallic", 0.2f);
        groundMaterial.SetFloat("_Glossiness", 0.3f);
        groundRenderer.material = groundMaterial;

        // Remove collider from ground to prevent interference
        var groundCollider = ground.GetComponent<Collider>();
        if (groundCollider != null)
        {
            DestroyImmediate(groundCollider);
        }
    }

    private void CreateLineRendererParent()
    {
        _lineRendererParent = new GameObject("MindCastle_AdjacencyLines");
        _lineRendererParent.transform.SetParent(transform);
    }

    #endregion

    #region Entity Creation

    private void CreateSampleEntities()
    {
        Debug.Log("🎭 Creating sample entities...");

        // Create LUCA first (the root entity)
        var lucaTemplate = _entityTemplates[0];
        var lucaNode = CreateEntityNode(lucaTemplate);
        SetupLucaEntity(lucaNode);
        _allNodes.Add(lucaNode);

        // Create other entities
        for (int i = 1; i < Mathf.Min(numberOfSampleEntities, _entityTemplates.Length); i++)
        {
            var template = _entityTemplates[i];
            var node = CreateEntityNode(template);
            SetupSampleEntity(node, template);
            _allNodes.Add(node);
        }

        // Create additional random entities if needed
        for (int i = _entityTemplates.Length; i < numberOfSampleEntities; i++)
        {
            var template = GenerateRandomTemplate(i);
            var node = CreateEntityNode(template);
            SetupSampleEntity(node, template);
            _allNodes.Add(node);
        }
    }

    private Stat7Node CreateEntityNode(EntityTemplate template)
    {
        // Create game object
        var entityObj = new GameObject($"MindCastle_{template.name}");
        entityObj.transform.SetParent(transform);

        // Add mesh and collider
        var meshFilter = entityObj.AddComponent<MeshFilter>();
        var meshRenderer = entityObj.AddComponent<MeshRenderer>();
        var sphere = entityObj.AddComponent<SphereCollider>();

        // Create sphere mesh
        var sphereMesh = CreateSphereMesh(0.5f);
        if (sphereMesh != null)
        {
            meshFilter.mesh = sphereMesh;
        }

        // Setup material
        var material = nodeMaterial != null ? new Material(nodeMaterial) : new Material(Shader.Find("Standard"));
        if (material != null)
        {
            meshRenderer.material = material;
        }

        // Add STAT7 node component
        var stat7Node = entityObj.AddComponent<Stat7Node>();

        // Position the entity
        entityObj.transform.position = template.position;

        return stat7Node;
    }

    private void SetupLucaEntity(Stat7Node lucaNode)
    {
        // LUCA is the primordial entity - special setup
        if (lucaNode == null)
        {
            Debug.LogError("LUCA node is null!");
            return;
        }

        var entityState = new Stat7Node.EntityState
        {
            content = "seed",
            phase = "emergence",
            bootstrap = true
        };

        lucaNode.SetEntityState(entityState);
        lucaNode.UpdateLuminosity(0); // LUCA starts at minimum luminosity

        Debug.Log($"🌱 Created LUCA entity: {lucaNode.EntityId}");
    }

    private void SetupSampleEntity(Stat7Node node, EntityTemplate template)
    {
        if (node == null)
        {
            Debug.LogError($"Sample node is null for template: {template.name}");
            return;
        }

        // Setup entity state based on template
        var entityState = new Stat7Node.EntityState
        {
            content = template.name.ToLower().Replace("-", " "),
            phase = "emergence",
            bootstrap = false
        };

        // Add custom data based on entity type
        if (entityState.CustomData == null)
            entityState.CustomData = new Dictionary<string, object>();

        entityState.CustomData["template_name"] = template.name;
        entityState.CustomData["realm"] = template.realm.ToString();
        entityState.CustomData["created_by"] = "MindCastleSceneSetup";

        node.SetEntityState(entityState);

        // Set random luminosity for visual variety
        int randomLuminosity = Random.Range(1, 6);
        node.UpdateLuminosity(randomLuminosity);

        Debug.Log($"🎭 Created entity: {template.name} ({template.stat7EType})");
    }

    private EntityTemplate GenerateRandomTemplate(int index)
    {
        var names = new[] { "Node", "Entity", "Core", "Hub", "Link", "Gate", "Portal", "Nexus" };
        var types = System.Enum.GetValues(typeof(Stat7Node.Stat7EType)).Cast<Stat7Node.Stat7EType>().ToArray();
        var realms = System.Enum.GetValues(typeof(Stat7Node.Realm)).Cast<Stat7Node.Realm>().ToArray();

        var randomName = $"{names[Random.Range(0, names.Length)]}-{index:000}";
        var randomType = types[Random.Range(0, types.Length)];
        var randomRealm = realms[Random.Range(0, realms.Length)];
        var randomPosition = Random.insideUnitSphere * spawnRadius;
        randomPosition.y = 0; // Keep on ground plane

        return new EntityTemplate(randomName, randomType, randomRealm, randomPosition);
    }

    private Mesh CreateSphereMesh(float radius)
    {
        try
        {
            var tempSphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            var mesh = tempSphere.GetComponent<MeshFilter>().mesh;

            if (mesh != null)
            {
                // Create a new mesh instance to avoid sharing
                var newMesh = new Mesh();
                newMesh.vertices = mesh.vertices;
                newMesh.triangles = mesh.triangles;
                newMesh.uv = mesh.uv;
                newMesh.normals = mesh.normals;
                newMesh.RecalculateBounds();

                DestroyImmediate(tempSphere);
                return newMesh;
            }

            DestroyImmediate(tempSphere);
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to create sphere mesh: {e.Message}");
        }

        // Fallback: create a simple cube mesh
        var cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
        var cubeMesh = cube.GetComponent<MeshFilter>().mesh;
        DestroyImmediate(cube);
        return cubeMesh;
    }

    #endregion

    #region Relationship Creation

    private void CreateEntityRelationships()
    {
        Debug.Log("🔗 Creating entity relationships...");

        // LUCA connects to all first-generation entities
        if (_allNodes.Count > 0)
        {
            var lucaNode = _allNodes[0];
            for (int i = 1; i < Mathf.Min(5, _allNodes.Count); i++)
            {
                CreateAdjacency(lucaNode, _allNodes[i]);
            }
        }

        // Create additional relationships
        for (int i = 1; i < _allNodes.Count; i++)
        {
            var currentNode = _allNodes[i];

            // Connect to 1-3 other entities
            int connectionCount = Random.Range(1, Mathf.Min(4, _allNodes.Count - 1));
            for (int j = 0; j < connectionCount; j++)
            {
                int targetIndex = Random.Range(1, _allNodes.Count);
                if (targetIndex != i)
                {
                    CreateAdjacency(currentNode, _allNodes[targetIndex]);
                }
            }
        }

        Debug.Log($"🔗 Created {_adjacencyLines.Count} adjacency relationships");
    }

    private void CreateAdjacency(Stat7Node sourceNode, Stat7Node targetNode)
    {
        if (sourceNode == null || targetNode == null)
        {
            Debug.LogWarning("Cannot create adjacency - one or both nodes are null");
            return;
        }

        // Add adjacency to nodes
        sourceNode.AddAdjacency(targetNode);

        // Create visual line
        CreateAdjacencyLine(sourceNode.transform.position, targetNode.transform.position);
    }

    private void CreateAdjacencyLine(Vector3 start, Vector3 end)
    {
        if (_lineRendererParent == null)
        {
            Debug.LogError("LineRenderer parent is null!");
            return;
        }

        var lineObj = new GameObject($"AdjacencyLine_{_adjacencyLines.Count}");
        lineObj.transform.SetParent(_lineRendererParent.transform);

        var lineRenderer = lineObj.AddComponent<LineRenderer>();
        var material = lineMaterial != null ? lineMaterial : CreateDefaultLineMaterial();

        if (material != null)
        {
            lineRenderer.material = material;
        }

        lineRenderer.startWidth = 0.05f;
        lineRenderer.endWidth = 0.05f;
        lineRenderer.positionCount = 2;
        lineRenderer.SetPosition(0, start + Vector3.up * 0.5f);
        lineRenderer.SetPosition(1, end + Vector3.up * 0.5f);

        _adjacencyLines.Add(lineRenderer);
    }

    private Material CreateDefaultLineMaterial()
    {
        var material = new Material(Shader.Find("Sprites/Default"));
        material.color = new Color(0.5f, 0.8f, 1.0f, 0.6f);
        return material;
    }

    #endregion

    #region UI Controls

    private void SetupUIControls()
    {
        // Create UI Canvas
        var canvasObj = new GameObject("MindCastle_UI");
        canvasObj.transform.SetParent(transform);

        var canvas = canvasObj.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.sortingOrder = 1000;

        var canvasScaler = canvasObj.AddComponent<CanvasScaler>();
        canvasScaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        canvasScaler.referenceResolution = new Vector2(1920, 1080);

        canvasObj.AddComponent<GraphicRaycaster>();

        // Create control panel
        CreateControlPanel(canvasObj);
    }

    private void CreateControlPanel(GameObject canvas)
    {
        var panelObj = new GameObject("ControlPanel");
        panelObj.transform.SetParent(canvas.transform, false);

        var panel = panelObj.AddComponent<Image>();
        panel.color = new Color(0, 0, 0, 0.8f);

        var rectTransform = panelObj.GetComponent<RectTransform>();
        rectTransform.anchorMin = new Vector2(0, 1);
        rectTransform.anchorMax = new Vector2(0, 1);
        rectTransform.pivot = new Vector2(0, 1);
        rectTransform.anchoredPosition = new Vector2(10, -10);
        rectTransform.sizeDelta = new Vector2(300, 200);

        // Add title
        CreateUIText(panelObj.transform, "MindCastle Controls", new Vector2(150, -20), 16, Color.white);

        // Add info text
        var infoText = CreateUIText(panelObj.transform, $"Entities: {_allNodes.Count}\nRelationships: {_adjacencyLines.Count}\n\nClick nodes to select\nScroll to zoom selected",
                                   new Vector2(150, -60), 12, Color.cyan);
        if (infoText != null)
        {
            var infoRect = infoText.GetComponent<RectTransform>();
            if (infoRect != null) infoRect.sizeDelta = new Vector2(280, 100);
        }
    }

    private Text CreateUIText(Transform parent, string text, Vector2 position, int fontSize, Color color)
    {
        var textObj = new GameObject("Text");
        textObj.transform.SetParent(parent, false);

        var textComponent = textObj.AddComponent<Text>();
        textComponent.text = text;
        textComponent.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
        textComponent.fontSize = fontSize;
        textComponent.color = color;
        textComponent.alignment = TextAnchor.UpperLeft;

        var rectTransform = textObj.GetComponent<RectTransform>();
        rectTransform.anchoredPosition = position;
        rectTransform.sizeDelta = new Vector2(280, 30);

        return textComponent;
    }

    #endregion

    #region Scene Finalization

    private void FinalizeScene()
    {
        // Update all adjacency lines to current positions
        RefreshAdjacencyLines();

        // Log scene summary
        Debug.Log("🏰 MindCastle Scene Summary:");
        Debug.Log($"   📊 Entities: {_allNodes.Count}");
        Debug.Log($"   🔗 Relationships: {_adjacencyLines.Count}");
        Debug.Log($"   🎮 Ready for interaction!");
        Debug.Log("   📝 Controls: Click to select, scroll to zoom, drag to move");
    }

    private void RefreshAdjacencyLines()
    {
        for (int i = 0; i < _adjacencyLines.Count; i++)
        {
            var line = _adjacencyLines[i];
            if (line != null)
            {
                // Update line positions based on current node positions
                // This is a simplified version - in practice you'd track which nodes connect to which lines
                var start = line.GetPosition(0);
                var end = line.GetPosition(1);
                line.SetPosition(0, start);
                line.SetPosition(1, end);
            }
        }
    }

    #endregion

    #region Utility Classes

    [System.Serializable]
    private class EntityTemplate
    {
        public string name;
        [FormerlySerializedAs("entityType")] public Stat7Node.Stat7EType stat7EType;
        public Stat7Node.Realm realm;
        public Vector3 position;

        public EntityTemplate(string name, Stat7Node.Stat7EType stat7EType, Stat7Node.Realm realm, Vector3 position)
        {
            this.name = name;
            this.stat7EType = stat7EType;
            this.realm = realm;
            this.position = position;
        }
    }

    #endregion

    #region Public API

    /// <summary>
    /// Gets all STAT7 nodes in the scene
    /// </summary>
    public List<Stat7Node> GetAllNodes() => _allNodes;

    /// <summary>
    /// Gets a specific node by entity ID
    /// </summary>
    public Stat7Node GetNodeById(string entityId) => _allNodes.FirstOrDefault(n => n.EntityId == entityId);

    /// <summary>
    /// Refreshes all visual connections
    /// </summary>
    [ContextMenu("Refresh Connections")]
    public void RefreshConnections()
    {
        RefreshAdjacencyLines();
    }

    #endregion
}

/// <summary>
/// Simple camera controller for MindCastle navigation
/// </summary>
public class CameraController : MonoBehaviour
{
    [Header("Movement Settings")]
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float rotationSpeed = 2f;
    [SerializeField] private float zoomSpeed = 2f;

    private Vector3 _lastMousePosition;
    private bool _isRotating = false;

    private void Update()
    {
        HandleMovement();
        HandleRotation();
        HandleZoom();
    }

    private void HandleMovement()
    {
        Vector3 movement = Vector3.zero;

        // WASD movement
        if (Input.GetKey(KeyCode.W)) movement += transform.forward;
        if (Input.GetKey(KeyCode.S)) movement -= transform.forward;
        if (Input.GetKey(KeyCode.A)) movement -= transform.right;
        if (Input.GetKey(KeyCode.D)) movement += transform.right;

        // Apply movement
        if (movement != Vector3.zero)
        {
            transform.position += movement * moveSpeed * Time.deltaTime;
        }
    }

    private void HandleRotation()
    {
        // Right mouse button rotation
        if (Input.GetMouseButtonDown(1))
        {
            _isRotating = true;
            _lastMousePosition = Input.mousePosition;
        }
        else if (Input.GetMouseButtonUp(1))
        {
            _isRotating = false;
        }

        if (_isRotating)
        {
            Vector3 deltaMouse = Input.mousePosition - _lastMousePosition;
            transform.Rotate(Vector3.up, deltaMouse.x * rotationSpeed, Space.World);
            transform.Rotate(Vector3.right, -deltaMouse.y * rotationSpeed, Space.Self);
            _lastMousePosition = Input.mousePosition;
        }
    }

    private void HandleZoom()
    {
        float scroll = Input.GetAxis("Mouse ScrollWheel");
        if (Mathf.Abs(scroll) > 0.01f)
        {
            transform.position += transform.forward * scroll * zoomSpeed;
        }
    }
}
