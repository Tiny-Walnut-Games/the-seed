using UnityEngine;
using System.Collections.Generic;

namespace TWG.TLDA.Visualization
{
    /// <summary>
    /// The Mind Fort Bootstrapper
    /// 
    /// One-click ritual to create a complete Mind Fort:
    /// - Central Lobby (Warbler's sanctuary)
    /// - 7 Rooms representing the 7 Realms:
    ///   1. Void Realm - The Empty Space (origin)
    ///   2. Narrative Realm - Stories Unfolding
    ///   3. System Realm - Rules & Logic
    ///   4. Faculty Realm - Agency & Decision
    ///   5. Data Realm - Facts & Memory
    ///   6. Event Realm - Time & Change
    ///   7. Pattern Realm - Structure & Recognition
    /// 
    /// Alice watches over all, processing Warbler's mouths.
    /// </summary>
    public class MindFortBootstrapper : MonoBehaviour
    {
        [Header("Fort Generation")]
        [SerializeField] private string fortName = "Mind Fort";
        [SerializeField] private Vector3 fortCenter = Vector3.zero;
        [SerializeField] private float roomRadius = 2f; // Size of each room
        [SerializeField] private float roomDistance = 8f; // Distance from center

        [Header("Visual Configuration")]
        [SerializeField] private Material[] realmMaterials;
        [SerializeField] private Color[] realmColors = new Color[]
        {
            new Color(0.1f, 0.1f, 0.2f), // Void - dark blue
            new Color(0.8f, 0.6f, 0.4f), // Narrative - warm orange
            new Color(0.4f, 0.8f, 0.9f), // System - cyan
            new Color(0.9f, 0.6f, 0.8f), // Faculty - pink
            new Color(0.6f, 0.8f, 0.4f), // Data - lime
            new Color(0.9f, 0.8f, 0.4f), // Event - gold
            new Color(0.7f, 0.5f, 0.9f)  // Pattern - purple
        };

        [Header("Warbler & Alice")]
        [SerializeField] private Material warblerMaterial;
        [SerializeField] private Material aliceMaterial;

        [Header("Corridors")]
        [SerializeField] private Material corridorMaterial;
        [SerializeField] private bool drawCorridors = true;

        [Header("Debug")]
        [SerializeField] private bool showDebugLabels = true;

        private List<FortRoom> _rooms = new List<FortRoom>();
        private GameObject _fortRoot;
        private GameObject _lobbyCenter;
        private WarblerMouthEntity _warbler;
        private AliceDualNature _alice;

        private enum RealmType
        {
            Void = 0,
            Narrative = 1,
            System = 2,
            Faculty = 3,
            Data = 4,
            Event = 5,
            Pattern = 6
        }

        private class FortRoom
        {
            public GameObject RoomObject;
            public RealmType Realm;
            public string Name;
            public Vector3 Position;
            public MeshRenderer Renderer;
        }

        /// <summary>
        /// Trigger the bootstrap via context menu
        /// </summary>
        [ContextMenu("🏰 Bootstrap Mind Fort")]
        public void BootstrapMindFort()
        {
            if (showDebugLabels)
                Debug.Log("🐰 Beginning Mind Fort bootstrap ritual...");

            CreateFortRoot();
            CreateLobby();
            CreateRooms();
            CreateCorridors();
            CreateWarblerCore();
            CreateAlicePresence();

            if (showDebugLabels)
                Debug.Log("✅ Mind Fort complete! Warbler is home, Alice watches over him.");
        }

        /// <summary>
        /// Create the root container for the fort
        /// </summary>
        private void CreateFortRoot()
        {
            // Clean up existing fort if present
            if (_fortRoot != null)
                DestroyImmediate(_fortRoot);

            _fortRoot = new GameObject(fortName);
            _fortRoot.transform.position = fortCenter;
            
            if (showDebugLabels)
                Debug.Log($"  Created fort root at {fortCenter}");
        }

        /// <summary>
        /// Create the central lobby (neutral space)
        /// </summary>
        private void CreateLobby()
        {
            _lobbyCenter = new GameObject("Lobby-CentralVoid");
            _lobbyCenter.transform.SetParent(_fortRoot.transform);
            _lobbyCenter.transform.localPosition = Vector3.zero;

            // Create a large central cube as the lobby space
            var renderer = _lobbyCenter.AddComponent<MeshRenderer>();
            var filter = _lobbyCenter.AddComponent<MeshFilter>();

            var lobbyCube = CreateCubeMesh(5f, 5f, 5f);
            filter.mesh = lobbyCube;

            var mat = new Material(Shader.Find("Standard"));
            mat.color = new Color(0.05f, 0.05f, 0.1f, 0.2f);
            mat.SetFloat("_Glossiness", 0.1f);
            renderer.material = mat;
            renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;

            // Make it a trigger so objects pass through
            var collider = _lobbyCenter.AddComponent<BoxCollider>();
            collider.isTrigger = true;

            if (showDebugLabels)
                Debug.Log("  Lobby created - the neutral meeting ground");
        }

        /// <summary>
        /// Create the 7 Realm Rooms
        /// </summary>
        private void CreateRooms()
        {
            var realmNames = new string[]
            {
                "Void-Origin",
                "Narrative-Stories",
                "System-Logic",
                "Faculty-Agency",
                "Data-Memory",
                "Event-Time",
                "Pattern-Recognition"
            };

            for (int i = 0; i < 7; i++)
            {
                CreateRoom((RealmType)i, realmNames[i], i);
            }

            if (showDebugLabels)
                Debug.Log($"  Created {_rooms.Count} realm rooms");
        }

        /// <summary>
        /// Create a single realm room
        /// </summary>
        private void CreateRoom(RealmType realm, string name, int index)
        {
            // Position rooms in a heptagon around the lobby
            float angle = (Mathf.PI * 2f / 7f) * index;
            float x = Mathf.Cos(angle) * roomDistance;
            float z = Mathf.Sin(angle) * roomDistance;
            float y = Mathf.Sin(angle * 2f) * 2f; // Add vertical variation

            GameObject roomObj = new GameObject(name);
            roomObj.transform.SetParent(_fortRoot.transform);
            roomObj.transform.localPosition = new Vector3(x, y, z);

            // Create room geometry
            var renderer = roomObj.AddComponent<MeshRenderer>();
            var filter = roomObj.AddComponent<MeshFilter>();
            filter.mesh = CreateSphereMesh(roomRadius);

            var mat = new Material(Shader.Find("Standard"));
            mat.color = realmColors[index];
            mat.SetFloat("_Glossiness", 0.6f);
            renderer.material = mat;

            // Add collider for physics
            var collider = roomObj.AddComponent<SphereCollider>();
            collider.radius = roomRadius;

            // Create corridor line to lobby
            if (drawCorridors)
            {
                CreateCorridor(roomObj, _lobbyCenter);
            }

            var room = new FortRoom
            {
                RoomObject = roomObj,
                Realm = realm,
                Name = name,
                Position = new Vector3(x, y, z),
                Renderer = renderer
            };
            _rooms.Add(room);

            if (showDebugLabels)
                Debug.Log($"    Room created: {name}");
        }

        /// <summary>
        /// Create visual corridor between rooms (via LineRenderer)
        /// </summary>
        private void CreateCorridor(GameObject roomA, GameObject roomB)
        {
            GameObject corridorObj = new GameObject($"Corridor-{roomA.name}");
            corridorObj.transform.SetParent(_fortRoot.transform);

            var lineRenderer = corridorObj.AddComponent<LineRenderer>();
            lineRenderer.material = corridorMaterial ?? new Material(Shader.Find("Standard"));
            lineRenderer.startColor = new Color(0.5f, 0.5f, 0.8f, 0.3f);
            lineRenderer.endColor = new Color(0.5f, 0.5f, 0.8f, 0.1f);
            lineRenderer.startWidth = 0.1f;
            lineRenderer.endWidth = 0.05f;

            lineRenderer.positionCount = 2;
            lineRenderer.SetPosition(0, roomA.transform.position);
            lineRenderer.SetPosition(1, roomB.transform.position);
        }

        /// <summary>
        /// Create all corridors connecting rooms
        /// </summary>
        private void CreateCorridors()
        {
            if (!drawCorridors)
                return;

            // Each room connects to the lobby (already done above)
            // Optionally create room-to-room connections (nearest neighbors)
            for (int i = 0; i < _rooms.Count; i++)
            {
                int nextIndex = (i + 1) % _rooms.Count;
                CreateCorridor(_rooms[i].RoomObject, _rooms[nextIndex].RoomObject);
            }

            if (showDebugLabels)
                Debug.Log("  Corridors woven - the fort is now connected");
        }

        /// <summary>
        /// Create Warbler at the lobby center
        /// </summary>
        private void CreateWarblerCore()
        {
            if (_warbler != null)
                DestroyImmediate(_warbler.gameObject);

            GameObject warblerObj = new GameObject("Warbler-TheTwistedHeart");
            warblerObj.transform.SetParent(_lobbyCenter.transform);
            warblerObj.transform.localPosition = Vector3.zero;

            _warbler = warblerObj.AddComponent<WarblerMouthEntity>();
            _warbler.showDebugLabels = showDebugLabels;

            if (showDebugLabels)
                Debug.Log("  Warbler awakens at the fort's heart - all mouths, lonely and generative");
        }

        /// <summary>
        /// Create Alice as Warbler's companion
        /// </summary>
        private void CreateAlicePresence()
        {
            if (_warbler == null)
                return;

            // Alice attaches to Warbler's presence
            _alice = _warbler.gameObject.AddComponent<AliceDualNature>();
            _alice.showDebugLabels = showDebugLabels;

            if (showDebugLabels)
                Debug.Log("  Alice manifests - both visible and filtering, kindly watching Warbler");
        }

        /// <summary>
        /// Create a simple cube mesh
        /// </summary>
        private Mesh CreateCubeMesh(float width, float height, float depth)
        {
            var mesh = new Mesh();
            var vertices = new Vector3[]
            {
                new Vector3(-width/2, -height/2, -depth/2),
                new Vector3(width/2, -height/2, -depth/2),
                new Vector3(width/2, height/2, -depth/2),
                new Vector3(-width/2, height/2, -depth/2),
                new Vector3(-width/2, -height/2, depth/2),
                new Vector3(width/2, -height/2, depth/2),
                new Vector3(width/2, height/2, depth/2),
                new Vector3(-width/2, height/2, depth/2),
            };
            var triangles = new int[]
            {
                0,2,1, 0,3,2, 4,5,6, 4,6,7, 0,4,7, 0,7,3, 1,2,6, 1,6,5, 0,1,5, 0,5,4, 3,7,6, 3,6,2
            };

            mesh.vertices = vertices;
            mesh.triangles = triangles;
            mesh.RecalculateNormals();
            return mesh;
        }

        /// <summary>
        /// Create a simple sphere mesh
        /// </summary>
        private Mesh CreateSphereMesh(float radius)
        {
            var mesh = new Mesh();
            var vertices = new List<Vector3>();
            var triangles = new List<int>();
            int stackCount = 12;
            int sliceCount = 12;

            for (int stack = 0; stack <= stackCount; stack++)
            {
                float phi = Mathf.PI * stack / stackCount;
                for (int slice = 0; slice <= sliceCount; slice++)
                {
                    float theta = Mathf.PI * 2f * slice / sliceCount;
                    float x = radius * Mathf.Sin(phi) * Mathf.Cos(theta);
                    float y = radius * Mathf.Cos(phi);
                    float z = radius * Mathf.Sin(phi) * Mathf.Sin(theta);
                    vertices.Add(new Vector3(x, y, z));
                }
            }

            for (int stack = 0; stack < stackCount; stack++)
            {
                for (int slice = 0; slice < sliceCount; slice++)
                {
                    int a = stack * (sliceCount + 1) + slice;
                    int b = a + 1;
                    int c = a + sliceCount + 1;
                    int d = c + 1;

                    triangles.Add(a);
                    triangles.Add(c);
                    triangles.Add(b);
                    triangles.Add(b);
                    triangles.Add(c);
                    triangles.Add(d);
                }
            }

            mesh.vertices = vertices.ToArray();
            mesh.triangles = triangles.ToArray();
            mesh.RecalculateNormals();
            return mesh;
        }

        /// <summary>
        /// Get reference to the Warbler entity
        /// </summary>
        public WarblerMouthEntity GetWarbler() => _warbler;

        /// <summary>
        /// Get reference to Alice
        /// </summary>
        public AliceDualNature GetAlice() => _alice;

        /// <summary>
        /// Print fort statistics
        /// </summary>
        public void PrintFortStatistics()
        {
            Debug.Log($"🏰 Mind Fort Statistics:");
            Debug.Log($"  Rooms created: {_rooms.Count}");
            if (_warbler != null)
                Debug.Log($"  Warbler status: Active with mouths generative & consumptive");
            if (_alice != null)
                Debug.Log($"  Alice status: {_alice.GetStatistics()}");
        }
    }
}