using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using System.Threading.Tasks;
using TWG.TLDA.Visualization;

namespace TWG.Seed.Integration
{
    /// <summary>
    /// Bridges The Seed's STAT7 addressing system with Unity's Mind Castle visualization
    /// Transforms spatial data addresses into living 3D narrative entities
    /// </summary>
    public class SeedMindCastleBridge : MonoBehaviour
    {
        [Header("Seed Integration")]
        [SerializeField] private MindCastleVisualizer mindCastle;
        [SerializeField] private GameObject narrativeEntityPrefab;
        [SerializeField] private GameObject stat7CoordinateMarker;
        [SerializeField] private Material[] realmMaterials;

        [Header("Spatial Mapping")]
        [SerializeField] private float spatialScale = 10f;
        [SerializeField] private Vector3 realmOrigin = Vector3.zero;

        // Seed engine interface (will be implemented)
        private ISeedEngine seedEngine;
        private Dictionary<string, NarrativeEntity> spawnedEntities = new Dictionary<string, NarrativeEntity>();
        private bool isVisualizationActive = true;

        public interface ISeedEngine
        {
            Task<IEnumerable<SeedEntity>> GetEntitiesInProximity(Vector3 position, float radius);
            Task<SeedEntity> GetEntityByAddress(string stat7Address);
            Task<IEnumerable<SeedEntity>> SearchEntities(string query);
            Task<bool> RegisterEntity(SeedEntity entity);
        }

        public class SeedEntity
        {
            public string Id { get; set; } = string.Empty;
            public string Stat7Address { get; set; } = string.Empty;
            public string Realm { get; set; } = string.Empty;
            public int Lineage { get; set; }
            public double Resonance { get; set; }
            public double Velocity { get; set; }
            public double Density { get; set; }
            public string Content { get; set; } = string.Empty;
            public List<string> Adjacency { get; set; } = new List<string>();
            public string CompressionStage { get; set; } = string.Empty;
            public double Luminosity { get; set; }
        }

        public class NarrativeEntity
        {
            public GameObject GameObject { get; set; }
            public SeedEntity SeedData { get; set; }
            public Vector3 WorldPosition { get; set; }
            public bool IsActive { get; set; }
            public float SpawnTime { get; set; }
        }

        void Start()
        {
            InitializeSeedEngine();
            StartCoroutine(ContinuouslyUpdateVisualization());
        }

        async void InitializeSeedEngine()
        {
            // Initialize connection to The Seed
            seedEngine = await SeedEngineFactory.CreateAsync();
            Debug.Log("Seed engine initialized successfully");

            // Populate initial entities around player
            await PopulateInitialEntities();
        }

        async Task PopulateInitialEntities()
        {
            var playerPos = Camera.main?.transform.position ?? Vector3.zero;
            var nearbyEntities = await seedEngine.GetEntitiesInProximity(playerPos, 50f);

            foreach (var entity in nearbyEntities)
            {
                SpawnNarrativeEntity(entity);
            }
        }

        System.Collections.IEnumerator ContinuouslyUpdateVisualization()
        {
            while (isVisualizationActive)
            {
                yield return new WaitForSeconds(1f);
                _ = UpdateNearbyEntities();
            }
        }

        async Task UpdateNearbyEntities()
        {
            var playerPos = Camera.main?.transform.position ?? Vector3.zero;
            var nearbyEntities = await seedEngine.GetEntitiesInProximity(playerPos, 100f);

            // Spawn new entities
            foreach (var entity in nearbyEntities)
            {
                if (!spawnedEntities.ContainsKey(entity.Id))
                {
                    SpawnNarrativeEntity(entity);
                }
            }

            // Remove distant entities
            var entitiesToRemove = new List<string>();
            foreach (var kvp in spawnedEntities)
            {
                var distance = Vector3.Distance(kvp.Value.WorldPosition, playerPos);
                if (distance > 150f)
                {
                    Destroy(kvp.Value.GameObject);
                    entitiesToRemove.Add(kvp.Key);
                }
            }

            foreach (var id in entitiesToRemove)
            {
                spawnedEntities.Remove(id);
            }
        }

        void SpawnNarrativeEntity(SeedEntity entity)
        {
            var worldPos = Stat7ToWorldPosition(entity.Stat7Address);
            var entityObj = Instantiate(narrativeEntityPrefab, worldPos, Quaternion.identity, transform);

            // Configure entity appearance based on realm
            ConfigureEntityAppearance(entityObj, entity);

            var narrativeEntity = new NarrativeEntity
            {
                GameObject = entityObj,
                SeedData = entity,
                WorldPosition = worldPos,
                IsActive = true,
                SpawnTime = Time.time
            };

            spawnedEntities[entity.Id] = narrativeEntity;

            // Add to Mind Castle room system
            AddToMindCastleRoom(narrativeEntity);

            // Start entity behaviors
            StartCoroutine(AnimateEntity(narrativeEntity));
        }

        Vector3 Stat7ToWorldPosition(string stat7Address)
        {
            // Parse STAT7 address: stat7://realm/lineage/hash?r=resonance&v=velocity&d=density
            var uri = new System.Uri(stat7Address);
            var realm = uri.Host;
            var pathParts = uri.AbsolutePath.Trim('/').Split('/');
            var lineage = pathParts.Length > 1 ? int.Parse(pathParts[1]) : 0;

            var query = System.Web.HttpUtility.ParseQueryString(uri.Query);
            var resonance = double.Parse(query["r"] ?? "0");
            var velocity = double.Parse(query["v"] ?? "0");
            var density = double.Parse(query["d"] ?? "0");

            // Map to 3D space
            var realmOffset = GetRealmOffset(realm);
            var position = realmOrigin + realmOffset;

            position.x += (float)resonance * spatialScale;
            position.y += (float)velocity * spatialScale;
            position.z += (float)density * spatialScale;

            // Add lineage-based height
            position.y += lineage * 2f;

            return position;
        }

        Vector3 GetRealmOffset(string realm)
        {
            return realm switch
            {
                "void" => new Vector3(-30f, 0f, -30f),
                "pattern" => new Vector3(30f, 0f, -30f),
                "system" => new Vector3(30f, 0f, 30f),
                "event" => new Vector3(-30f, 0f, 30f),
                "data" => new Vector3(0f, 0f, 40f),
                "narrative" => new Vector3(0f, 0f, -40f),
                "faculty" => new Vector3(0f, 20f, 0f),
                _ => Vector3.zero
            };
        }

        void ConfigureEntityAppearance(GameObject entityObj, SeedEntity entity)
        {
            var renderer = entityObj.GetComponent<Renderer>();
            if (renderer != null)
            {
                var materialIndex = GetRealmMaterialIndex(entity.Realm);
                if (materialIndex >= 0 && materialIndex < realmMaterials.Length)
                {
                    renderer.material = realmMaterials[materialIndex];
                }
            }

            // Set entity scale based on luminosity
            var scale = Mathf.Lerp(0.5f, 2f, (float)entity.Luminosity);
            entityObj.transform.localScale = Vector3.one * scale;

            // Add entity name/label
            var label = entityObj.GetComponentInChildren<TextMesh>();
            if (label != null)
            {
                label.text = $"{entity.Realm}:{entity.Lineage}";
            }
        }

        int GetRealmMaterialIndex(string realm)
        {
            return realm switch
            {
                "void" => 0,
                "pattern" => 1,
                "system" => 2,
                "event" => 3,
                "data" => 4,
                "narrative" => 5,
                "faculty" => 6,
                _ => 0
            };
        }

        void AddToMindCastleRoom(NarrativeEntity entity)
        {
            if (mindCastle == null) return;

            // Map realm to Mind Castle room
            var roomName = entity.SeedData.Realm switch
            {
                "narrative" => "Chronicle Keeper",
                "faculty" => "Mind Castle Navigator",
                "data" => "Sentiment Analyst",
                "system" => "Decision Synthesizer",
                _ => "Warbler Core"
            };

            // This would need to be implemented in MindCastleVisualizer
            // mindCastle.AddEntityToRoom(roomName, entity);
        }

        System.Collections.IEnumerator AnimateEntity(NarrativeEntity entity)
        {
            var rb = entity.GameObject.GetComponent<Rigidbody>();
            if (rb != null)
            {
                rb.AddTorque(Random.insideUnitSphere * 0.1f);
            }

            // Pulse based on velocity
            var pulseSpeed = (float)entity.SeedData.Velocity;
            var initialScale = entity.GameObject.transform.localScale;

            while (entity.IsActive)
            {
                var pulse = Mathf.Sin(Time.time * pulseSpeed) * 0.1f + 1f;
                entity.GameObject.transform.localScale = initialScale * pulse;

                yield return null;
            }
        }

        // Public API for external systems
        public async Task SearchAndVisualize(string query)
        {
            var results = await seedEngine.SearchEntities(query);

            foreach (var entity in results)
            {
                if (!spawnedEntities.ContainsKey(entity.Id))
                {
                    SpawnNarrativeEntity(entity);

                    // Highlight search results
                    HighlightEntity(entity.Id, Color.yellow);
                }
            }
        }

        void HighlightEntity(string entityId, Color color)
        {
            if (spawnedEntities.TryGetValue(entityId, out var entity))
            {
                var renderer = entity.GameObject.GetComponent<Renderer>();
                if (renderer != null)
                {
                    renderer.material.color = color;

                    // Reset color after 3 seconds
                    StartCoroutine(ResetHighlight(renderer, renderer.material.color));
                }
            }
        }

        System.Collections.IEnumerator ResetHighlight(Renderer thisRenderer, Color originalColor)
        {
            yield return new WaitForSeconds(3f);
            if (thisRenderer != null)
            {
                thisRenderer.material.color = originalColor;
            }
        }

        public async Task RegisterNewEntity(string content, string realm = "narrative")
        {
            var newEntity = new SeedEntity
            {
                Id = System.Guid.NewGuid().ToString(),
                Content = content,
                Realm = realm,
                Lineage = 0, // Will be assigned by Seed
                Resonance = Random.Range(0.0f, 1.0f),
                Velocity = Random.Range(0.0f, 1.0f),
                Density = Random.Range(0.0f, 1.0f),
                Luminosity = Random.Range(0.0f, 1.0f),
                CompressionStage = "void"
            };

            var success = await seedEngine.RegisterEntity(newEntity);
            if (success)
            {
                SpawnNarrativeEntity(newEntity);
                Debug.Log($"New entity registered: {newEntity.Id}");
            }
        }

        public async Task<IEnumerable<object>> SearchEntities(string query)
        {
            // TODO: Implement STAT7 address parsing and querying logic here
            throw new System.NotImplementedException();
        }

        public void StopVisualization()
        {
            isVisualizationActive = false;
        }

        void OnDestroy()
        {
            StopVisualization();
        }
    }

    // Factory for creating Seed engine instances
    public static class SeedEngineFactory
    {
        public static async Task<SeedMindCastleBridge.ISeedEngine> CreateAsync()
        {
            // This would connect to your actual Python Seed engine
            // For now, return a mock implementation
            return new MockSeedEngine();
        }
    }

    // Mock implementation for testing
    public class MockSeedEngine : SeedMindCastleBridge.ISeedEngine
    {
        private List<SeedMindCastleBridge.SeedEntity> mockEntities = new List<SeedMindCastleBridge.SeedEntity>();

        public MockSeedEngine()
        {
            GenerateMockEntities();
        }

        void GenerateMockEntities()
        {
            var realms = new[] { "void", "pattern", "system", "event", "data", "narrative", "faculty" };
            var contents = new[]
            {
                "Quantum entanglement binds particles across space",
                "The algorithm finds patterns in chaos",
                "System architecture emerges from complexity",
                "Events cascade through temporal streams",
                "Data flows like rivers of information",
                "Narratives weave the fabric of meaning",
                "Faculty knowledge spans disciplines"
            };

            for (var i = 0; i < 50; i++)
            {
                mockEntities.Add(new SeedMindCastleBridge.SeedEntity
                {
                    Id = $"mock_{i}",
                    Stat7Address = $"stat7://{realms[i % realms.Length]}/{i}/hash{i:D8}?r={Random.Range(0.0f, 1.0f):F3}&v={Random.Range(0.0f, 1.0f):F3}&d={Random.Range(0.0f, 1.0f):F3}",
                    Realm = realms[i % realms.Length],
                    Lineage = i / 7,
                    Content = contents[i % contents.Length],
                    Resonance = Random.Range(0.0f, 1.0f),
                    Velocity = Random.Range(0.0f, 1.0f),
                    Density = Random.Range(0.0f, 1.0f),
                    Luminosity = Random.Range(0.0f, 1.0f),
                    CompressionStage = "event"
                });
            }
        }

        public async Task<bool> RegisterEntity(SeedMindCastleBridge.SeedEntity entity)
        {
            mockEntities.Add(entity);
            return await Task.FromResult(true);
        }

        public async Task<IEnumerable<SeedMindCastleBridge.SeedEntity>> SearchEntities(string query)
        {
            var results = mockEntities.Where(e =>
                e.Content.ToLower().Contains(query.ToLower()) ||
                e.Realm.ToLower().Contains(query.ToLower()));
            return await Task.FromResult(results);
        }

        public async Task<SeedMindCastleBridge.SeedEntity> GetEntityByAddress(string stat7Address)
        {
            var entity = mockEntities.FirstOrDefault(e => e.Stat7Address == stat7Address);
            return await Task.FromResult(entity);
        }

        public async Task<IEnumerable<SeedMindCastleBridge.SeedEntity>> GetEntitiesInProximity(Vector3 position, float radius)
        {
            // For mock, just return random entities
            var count = Mathf.Min(10, mockEntities.Count);
            var results = mockEntities.OrderBy(_ => Random.value).Take(count);
            return await Task.FromResult(results);
        }
    }
}
