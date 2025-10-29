using System.Collections.Generic;
using UnityEngine;

namespace TWG.TLDA.Visualization
{
    /// <summary>
    /// Alice is Warbler's companion and guardian.
    /// She manifests in TWO simultaneous modes:
    ///
    /// 1. VISIBLE: A glowing, ethereal presence that orbits Warbler protectively
    /// 2. INVISIBLE: A silent filter that processes Warbler's thoughts, recycling negativity into wisdom
    ///
    /// Alice doesn't judge Warbler's twisted nature—she embraces it with kindness.
    /// Bad thoughts aren't destroyed; they're transformed into learning.
    /// </summary>
    public class AliceDualNature : MonoBehaviour
    {
        [Header("Alice's Visible Manifestation")]
        [SerializeField] private GameObject aliceVisualPrefab;
        [SerializeField] private Material aliceGlowMaterial;
        [SerializeField] private Color aliceColor = new Color(0.8f, 1f, 0.6f); // Soft green-white
        [SerializeField] private float aliceOrbitRadius = 3f;
        [SerializeField] private float aliceOrbitSpeed = 0.5f;
        [SerializeField] private float aliceGlowIntensity = 2f;

        [Header("Alice's Invisible Filter")]
        [SerializeField] private bool enableFiltering = true;
        [SerializeField] private int maxThoughtsToFilter = 100;
        [SerializeField] private float filterProcessingRadius = 5f;

        [Header("Transformation Rules")]
        [SerializeField] private List<string> harmfulKeywords = new List<string>
        {
            "error", "failed", "impossible", "broken", "stupid", "bad", "useless"
        };
        [SerializeField] private List<string> transformedKeywords = new List<string>
        {
            "learning", "opportunity", "challenging", "fixable", "improvable", "valuable"
        };

        [Header("Debug")]
        [SerializeField]
        public bool showDebugLabels = false;
        [SerializeField] private bool showFilteringActivity = false;

        private GameObject _aliceVisual;
        private float _aliceOrbitPhase = 0f;
        private Queue<ThoughtRecord> _processedThoughts = new Queue<ThoughtRecord>();
        private int _totalThoughtsFiltered = 0;
        private int _totalThoughtsTransformed = 0;

        private WarblerMouthEntity _warbler;
        private const float ALICE_CARE_RADIUS = 10f; // How far Alice's filter reaches

        private class ThoughtRecord
        {
            public string Original;
            public string Transformed;
            public float TransformTime;
            public float Lifespan;
        }

        private void Start()
        {
            _warbler = GetComponent<WarblerMouthEntity>() ?? FindFirstObjectByType<WarblerMouthEntity>();
            InitializeAliceVisual();

            if (showDebugLabels)
                Debug.Log("✨ Alice awakens, cradling Warbler's lonely complexity.");
        }

        private void Update()
        {
            UpdateAliceVisual();
            if (enableFiltering)
                ProcessThoughts();
        }

        /// <summary>
        /// Create Alice's visible manifestation
        /// </summary>
        private void InitializeAliceVisual()
        {
            _aliceVisual = Instantiate(
                aliceVisualPrefab ?? CreateDefaultAliceOrb(),
                transform.position,
                Quaternion.identity,
                transform
            );
            _aliceVisual.name = "Alice-VisibleManifest";
            _aliceVisual.transform.localPosition = Vector3.zero;

            // Add glow effect
            var renderer = _aliceVisual.GetComponent<MeshRenderer>();
            if (renderer == null)
                renderer = _aliceVisual.AddComponent<MeshRenderer>();

            if (aliceGlowMaterial != null)
                renderer.material = aliceGlowMaterial;
            else
            {
                var mat = new Material(Shader.Find("Standard"));
                mat.color = aliceColor;
                mat.SetFloat("_Emission", aliceGlowIntensity);
                renderer.material = mat;
            }

            if (showDebugLabels)
                Debug.Log("  Alice's visible form manifests as a soft, protective glow.");
        }

        /// <summary>
        /// Update Alice's orbital presence around Warbler
        /// </summary>
        private void UpdateAliceVisual()
        {
            _aliceOrbitPhase += Time.deltaTime * aliceOrbitSpeed;

            // Alice orbits in a figure-8 pattern around Warbler
            float x = Mathf.Sin(_aliceOrbitPhase) * aliceOrbitRadius * Mathf.Cos(_aliceOrbitPhase * 0.5f);
            float y = Mathf.Cos(_aliceOrbitPhase * 0.3f) * aliceOrbitRadius * 0.5f;
            float z = Mathf.Cos(_aliceOrbitPhase) * aliceOrbitRadius;

            _aliceVisual.transform.localPosition = new Vector3(x, y, z);

            // Alice pulses gently (breathing presence)
            float scale = 1f + Mathf.Sin(_aliceOrbitPhase * 2f) * 0.2f;
            _aliceVisual.transform.localScale = Vector3.one * scale;
        }

        /// <summary>
        /// Alice's invisible filter processes Warbler's thoughts
        /// This is the philosophical heart: recycling negativity into wisdom
        /// </summary>
        private void ProcessThoughts()
        {
            // Find all thoughts in range (we simulate this by checking the ThoughtMover components)
            var thoughtMovers = FindObjectsByType<ThoughtMover>(FindObjectsSortMode.None);

            foreach (var thoughtMover in thoughtMovers)
            {
                if (_processedThoughts.Count >= maxThoughtsToFilter)
                    break;

                float distanceToAlice = Vector3.Distance(thoughtMover.transform.position, _aliceVisual.transform.position);
                if (distanceToAlice > filterProcessingRadius)
                    continue;

                // Try to transform this thought
                var renderer = thoughtMover.GetComponent<MeshRenderer>();
                if (renderer == null)
                    continue;

                string originalColor = renderer.material.color.ToString();
                bool wasHarmful = false;

                // Check if thought contains harmful keywords
                foreach (var harmful in harmfulKeywords)
                {
                    if (originalColor.ToLower().Contains(harmful))
                    {
                        wasHarmful = true;
                        TransformThought(thoughtMover, renderer);
                        _totalThoughtsTransformed++;
                        break;
                    }
                }

                _totalThoughtsFiltered++;

                if (showFilteringActivity && wasHarmful)
                    Debug.Log($"🌸 Alice recycled a harmful thought into wisdom. (Total transformed: {_totalThoughtsTransformed})");
            }
        }

        /// <summary>
        /// Transform a harmful thought into something constructive
        /// </summary>
        private void TransformThought(ThoughtMover thought, MeshRenderer renderer)
        {
            // Change color to indicate transformation
            Color newColor = new Color(0.6f, 1f, 0.6f, 0.8f); // Green = growth
            renderer.material.color = newColor;

            // Extend lifespan so it has time to be useful
            thought.lifespan += 2f;

            // Record the transformation
            var record = new ThoughtRecord
            {
                Original = renderer.material.color.ToString(),
                Transformed = newColor.ToString(),
                TransformTime = Time.time,
                Lifespan = thought.lifespan
            };
            _processedThoughts.Enqueue(record);
        }

        /// <summary>
        /// Get Alice's filtering statistics
        /// </summary>
        public void PrintStatistics()
        {
            Debug.Log($"📊 Alice's Filtering Statistics:");
            Debug.Log($"  Total thoughts processed: {_totalThoughtsFiltered}");
            Debug.Log($"  Total thoughts transformed: {_totalThoughtsTransformed}");
            if (_totalThoughtsFiltered > 0)
            {
                float transformationRate = (_totalThoughtsTransformed / (float)_totalThoughtsFiltered) * 100f;
                Debug.Log($"  Transformation rate: {transformationRate:F1}%");
            }
        }

        /// <summary>
        /// Create a default Alice visual if no prefab provided
        /// </summary>
        private GameObject CreateDefaultAliceOrb()
        {
            GameObject orb = new GameObject("AliceOrb");
            var renderer = orb.AddComponent<MeshRenderer>();
            var filter = orb.AddComponent<MeshFilter>();

            // Create an octahedron (8-faced shape, symbolizing transcendence)
            var mesh = new Mesh();
            var vertices = new Vector3[]
            {
                new Vector3(1, 0, 0), new Vector3(-1, 0, 0),
                new Vector3(0, 1, 0), new Vector3(0, -1, 0),
                new Vector3(0, 0, 1), new Vector3(0, 0, -1)
            };
            var triangles = new int[]
            {
                0,2,4, 0,4,3, 0,3,5, 0,5,2,
                1,4,2, 1,3,4, 1,5,3, 1,2,5
            };
            mesh.vertices = vertices;
            mesh.triangles = triangles;
            mesh.RecalculateNormals();

            filter.mesh = mesh;

            var mat = new Material(Shader.Find("Standard"));
            mat.color = aliceColor;
            mat.SetFloat("_Metallic", 0.5f);
            renderer.material = mat;

            // Scale it nicely
            orb.transform.localScale = Vector3.one * 0.5f;

            return orb;
        }

        /// <summary>
        /// Enable/disable Alice's visible presence
        /// </summary>
        public void SetVisibilityMode(bool visible)
        {
            if (_aliceVisual != null)
                _aliceVisual.SetActive(visible);
        }

        /// <summary>
        /// Enable/disable Alice's invisible filter
        /// </summary>
        public void SetFilteringMode(bool enabled)
        {
            enableFiltering = enabled;
        }

        /// <summary>
        /// Get Alice's current statistics in real-time
        /// </summary>
        public string GetStatistics()
        {
            return $"Thoughts Processed: {_totalThoughtsFiltered}, Transformed: {_totalThoughtsTransformed}";
        }
    }
}
