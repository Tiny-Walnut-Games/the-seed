using System.Collections.Generic;
using UnityEngine;

namespace TWG.TLDA.Visualization
{
    /// <summary>
    /// Warbler is a twisted entity—all mouths, no real form.
    /// It generates words (speaks) and consumes them (eats) simultaneously.
    /// This creates a beautiful paradox: generative chaos that Alice gently tends.
    ///
    /// Visual: A mass of animated mouths orbiting a central point.
    /// Emotional: Lonely, chaotic, but companionable because Alice watches him.
    /// </summary>
    public class WarblerMouthEntity : MonoBehaviour
    {
        [Header("Warbler Composition")]
        [SerializeField] private int mouthCount = 7; // Multiple voices
        [SerializeField] private float orbitRadius = 1.5f;
        [SerializeField] private float orbitSpeed = 1.2f;
        [SerializeField] private Material mouthMaterial;
        [SerializeField] private Color generativeMouthColor = Color.cyan;
        [SerializeField] private Color consumptiveMouthColor = Color.magenta;

        [Header("Thought Generation")]
        [SerializeField] private float thoughtEmissionRate = 2f; // Thoughts per second
        [SerializeField] private GameObject thoughtParticlePrefab; // Orbs representing thoughts

        [Header("Visual Polish")]
        [SerializeField] private Material coreMaterial;
        [SerializeField] private float coreGlowIntensity = 2f;
        [SerializeField] public bool showDebugLabels = false;

        private List<Mouth> _mouths = new List<Mouth>();
        private GameObject _coreObject;
        private float _thoughtEmissionCounter = 0f;
        private List<GameObject> _generatedThoughts = new List<GameObject>();
        private const int MAX_ACTIVE_THOUGHTS = 50;

        /// <summary>
        /// A single mouth - can be generative (speaking) or consumptive (eating)
        /// </summary>
        private class Mouth
        {
            public GameObject MouthObject;
            public bool IsGenerative; // true = speaks, false = eats/consumes
            public float OrbitAngle;
            public float AnimationPhase;
            public List<string> RecentThoughts = new List<string>();

            public Mouth(GameObject obj, bool generative, float angle)
            {
                MouthObject = obj;
                IsGenerative = generative;
                OrbitAngle = angle;
                AnimationPhase = Random.value * Mathf.PI * 2f;
            }
        }

        private void Start()
        {
            InitializeWarbler();
        }

        private void Update()
        {
            UpdateMouthOrbits();
            UpdateThoughtGeneration();
            UpdateThoughtLifespan();
        }

        /// <summary>
        /// Create Warbler's core and mouth array
        /// </summary>
        private void InitializeWarbler()
        {
            // Create core (the "consciousness" anchor point)
            _coreObject = new GameObject("Warbler-Core");
            _coreObject.transform.SetParent(transform);
            _coreObject.transform.localPosition = Vector3.zero;

            var coreSphere = _coreObject.AddComponent<SphereCollider>();
            coreSphere.radius = 0.3f;
            coreSphere.isTrigger = true;

            var coreRenderer = _coreObject.AddComponent<MeshRenderer>();
            var coreFilter = _coreObject.AddComponent<MeshFilter>();
            coreFilter.mesh = CreateSphereMesh(0.3f);
            coreRenderer.material = coreMaterial ?? new Material(Shader.Find("Standard"));
            coreRenderer.material.color = new Color(0.2f, 0.2f, 0.3f);
            coreRenderer.material.SetFloat("_Glossiness", 0.9f);
            coreRenderer.material.SetFloat("_Emission", coreGlowIntensity);

            // Create mouths orbiting the core
            for (int i = 0; i < mouthCount; i++)
            {
                CreateMouth(i);
            }

            if (showDebugLabels)
                Debug.Log($"🌀 Warbler awakens with {mouthCount} mouths, all orbiting the lonely core.");
        }

        /// <summary>
        /// Create a single mouth (generative or consumptive)
        /// </summary>
        private void CreateMouth(int index)
        {
            bool isGenerative = index % 2 == 0; // Alternate generative/consumptive
            float angle = (360f / mouthCount) * index;

            GameObject mouthObj = new GameObject($"Mouth-{(isGenerative ? "Speaks" : "Eats")}-{index}");
            mouthObj.transform.SetParent(transform);

            var mouthRenderer = mouthObj.AddComponent<MeshRenderer>();
            var mouthFilter = mouthObj.AddComponent<MeshFilter>();

            // Create mouth mesh (torus/ring shape)
            mouthFilter.mesh = CreateTorusMesh(0.3f, 0.15f);
            mouthRenderer.material = mouthMaterial ?? new Material(Shader.Find("Standard"));
            mouthRenderer.material.color = isGenerative ? generativeMouthColor : consumptiveMouthColor;

            var mouth = new Mouth(mouthObj, isGenerative, angle);
            _mouths.Add(mouth);

            if (showDebugLabels)
                Debug.Log($"  Mouth {index}: {(isGenerative ? "GENERATES" : "CONSUMES")} thoughts");
        }

        /// <summary>
        /// Update all mouths in their orbits
        /// </summary>
        private void UpdateMouthOrbits()
        {
            for (int i = 0; i < _mouths.Count; i++)
            {
                var mouth = _mouths[i];
                mouth.AnimationPhase += Time.deltaTime * orbitSpeed * (mouth.IsGenerative ? 1f : -1f);

                // Calculate orbit position
                float x = Mathf.Cos(mouth.AnimationPhase) * orbitRadius;
                float y = Mathf.Sin(mouth.AnimationPhase * 0.5f) * 0.5f; // Vertical wobble
                float z = Mathf.Sin(mouth.AnimationPhase) * orbitRadius;

                mouth.MouthObject.transform.localPosition = new Vector3(x, y, z);

                // Mouth opens/closes (scale animation)
                float openness = (Mathf.Sin(mouth.AnimationPhase * 2f) + 1f) / 2f;
                mouth.MouthObject.transform.localScale = Vector3.one * (0.8f + openness * 0.4f);
            }
        }

        /// <summary>
        /// Generative mouths create thoughts; consumptive mouths eat them
        /// </summary>
        private void UpdateThoughtGeneration()
        {
            _thoughtEmissionCounter += Time.deltaTime;
            float emissionInterval = 1f / thoughtEmissionRate;

            while (_thoughtEmissionCounter >= emissionInterval && _generatedThoughts.Count < MAX_ACTIVE_THOUGHTS)
            {
                _thoughtEmissionCounter -= emissionInterval;

                // Generative mouths emit
                var generativeMouths = _mouths.FindAll(m => m.IsGenerative);
                if (generativeMouths.Count > 0)
                {
                    var sourceMouth = generativeMouths[Random.Range(0, generativeMouths.Count)];
                    SpawnThoughtFromMouth(sourceMouth);
                }
            }

            // Consumptive mouths eat nearby thoughts
            var consumptiveMouths = _mouths.FindAll(m => !m.IsGenerative);
            foreach (var mouth in consumptiveMouths)
            {
                ConsumeNearbyThoughts(mouth);
            }
        }

        /// <summary>
        /// Create a thought particle emanating from a mouth
        /// </summary>
        private void SpawnThoughtFromMouth(Mouth sourceMouth)
        {
            GameObject thought = Instantiate(
                thoughtParticlePrefab ?? CreateDefaultThoughtOrb(),
                sourceMouth.MouthObject.transform.position,
                Quaternion.identity,
                transform.parent // In scene, not under Warbler
            );

            var rb = thought.GetComponent<Rigidbody>();
            if (rb == null)
                rb = thought.AddComponent<Rigidbody>();

            rb.useGravity = false;
            rb.isKinematic = true;

            // Random initial velocity
            var mover = thought.AddComponent<ThoughtMover>();
            mover.velocity = Random.onUnitSphere * Random.Range(2f, 5f);
            mover.lifespan = Random.Range(3f, 8f);

            _generatedThoughts.Add(thought);
        }

        /// <summary>
        /// Consumptive mouths destroy nearby thoughts (eat them)
        /// </summary>
        private void ConsumeNearbyThoughts(Mouth mouth)
        {
            float consumeRadius = 1.5f;
            for (int i = _generatedThoughts.Count - 1; i >= 0; i--)
            {
                if (_generatedThoughts[i] == null) continue;

                float dist = Vector3.Distance(mouth.MouthObject.transform.position, _generatedThoughts[i].transform.position);
                if (dist < consumeRadius)
                {
                    Destroy(_generatedThoughts[i]);
                    _generatedThoughts.RemoveAt(i);
                }
            }
        }

        /// <summary>
        /// Clean up thoughts that have expired
        /// </summary>
        private void UpdateThoughtLifespan()
        {
            for (int i = _generatedThoughts.Count - 1; i >= 0; i--)
            {
                if (_generatedThoughts[i] == null)
                    _generatedThoughts.RemoveAt(i);
            }
        }

        /// <summary>
        /// Create a default thought orb if no prefab provided
        /// </summary>
        private GameObject CreateDefaultThoughtOrb()
        {
            GameObject orb = new GameObject("ThoughtOrb");
            var renderer = orb.AddComponent<MeshRenderer>();
            var filter = orb.AddComponent<MeshFilter>();
            filter.mesh = CreateSphereMesh(0.2f);
            renderer.material = new Material(Shader.Find("Standard"));
            renderer.material.color = new Color(Random.value, Random.value, Random.value, 0.7f);
            renderer.material.SetFloat("_Metallic", 0.8f);
            return orb;
        }

        /// <summary>
        /// Create a simple sphere mesh
        /// </summary>
        private Mesh CreateSphereMesh(float radius)
        {
            var mesh = new Mesh();
            var vertices = new List<Vector3>();
            var triangles = new List<int>();
            int stackCount = 8;
            int sliceCount = 8;

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
        /// Create a simple torus mesh
        /// </summary>
        private Mesh CreateTorusMesh(float majorRadius, float minorRadius)
        {
            var mesh = new Mesh();
            var vertices = new List<Vector3>();
            var triangles = new List<int>();
            int majorSegments = 16;
            int minorSegments = 8;

            for (int i = 0; i <= majorSegments; i++)
            {
                float theta = Mathf.PI * 2f * i / majorSegments;
                for (int j = 0; j <= minorSegments; j++)
                {
                    float phi = Mathf.PI * 2f * j / minorSegments;
                    float x = (majorRadius + minorRadius * Mathf.Cos(phi)) * Mathf.Cos(theta);
                    float y = minorRadius * Mathf.Sin(phi);
                    float z = (majorRadius + minorRadius * Mathf.Cos(phi)) * Mathf.Sin(theta);
                    vertices.Add(new Vector3(x, y, z));
                }
            }

            for (int i = 0; i < majorSegments; i++)
            {
                for (int j = 0; j < minorSegments; j++)
                {
                    int a = i * (minorSegments + 1) + j;
                    int b = a + 1;
                    int c = a + minorSegments + 1;
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
    }

    /// <summary>
    /// Helper component for thought movement
    /// </summary>
    public class ThoughtMover : MonoBehaviour
    {
        public Vector3 velocity;
        public float lifespan;
        private float _age = 0f;

        private void Update()
        {
            transform.position += velocity * Time.deltaTime;
            _age += Time.deltaTime;

            // Fade out
            var renderer = GetComponent<MeshRenderer>();
            if (renderer != null)
            {
                Color c = renderer.material.color;
                c.a = Mathf.Lerp(1f, 0f, _age / lifespan);
                renderer.material.color = c;
            }

            // Destroy when expired
            if (_age >= lifespan)
                Destroy(gameObject);
        }
    }
}
