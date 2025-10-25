using System.Collections.Generic;
using UnityEngine;
using System.Linq;

namespace TWG.TLDA.Visualization
{
    /// <summary>
    /// 3D visualization of the Warbler Mind Castle with flowing data streams
    /// Shows the cacophony of Warbler voices syncing into coherent decisions
    /// </summary>
    public class MindCastleVisualizer : MonoBehaviour
    {
        [Header("Castle Structure")]
        [SerializeField] private GameObject roomPrefab;
        [SerializeField] private GameObject corridorPrefab;
        [SerializeField] private Material[] roomMaterials; // Different colors for different faculty

        [Header("Warbler Data Flow")]
        [SerializeField] private GameObject warblerVoicePrefab; // Particle or orb for voices
        [SerializeField] private LineRenderer dataStreamPrefab;
        [SerializeField] private float voiceSpeed = 2f;
        [SerializeField] private int maxConcurrentVoices = 50;

        [Header("Alice Filter")]
        [SerializeField] private GameObject aliceFilterPrefab;
        [SerializeField] private Material goodThoughtMaterial;
        [SerializeField] private Material badThoughtMaterial;

        private Dictionary<string, CastleRoom> _rooms = new Dictionary<string, CastleRoom>();
        private List<WarblerVoice> _activeVoices = new List<WarblerVoice>();
        private AliceFilter _aliceFilter;

        public class CastleRoom
        {
            public GameObject RoomObject = null;
            public string Faculty = string.Empty; // "Chronicle Keeper", "Warbler Core", etc.
            public Vector3 Position;
            public List<WarblerVoice> ContainedVoices = new List<WarblerVoice>();
            public float Activity = 0f; // How active this room is
        }

        public class WarblerVoice
        {
            public GameObject VoiceObject = null;
            public string Content = string.Empty; // The "words" this voice carries
            public Vector3 TargetPosition;
            public bool IsGoodThought = true;
            public float Lifespan = 5f;
            public CastleRoom CurrentRoom = null;
        }

        public class AliceFilter
        {
            public GameObject FilterObject = null;
            public List<WarblerVoice> ProcessingVoices = new List<WarblerVoice>();

            public bool ProcessThought(WarblerVoice voice)
            {
                // Alice's gentle filtering - bad thoughts get recycled, not destroyed
                if (voice.Content.Contains("error") || voice.Content.Contains("impossible"))
                {
                    voice.IsGoodThought = false;
                    RecycleThought(voice);
                    return false; // Don't let it through yet
                }
                return true; // Good thought, let it flow
            }

            private void RecycleThought(WarblerVoice voice)
            {
                // Transform negative thought into learning opportunity
                voice.Content = voice.Content.Replace("error", "learning")
                                           .Replace("impossible", "challenging");
                voice.Lifespan += 2f; // Give it more time to be useful
            }
        }

        void Start()
        {
            CreateCastleStructure();
            SetupAliceFilter();
            StartWarblerActivity();
        }

        void CreateCastleStructure()
        {
            // Create rooms based on TLDA faculty
            var facultyRooms = new Dictionary<string, Vector3>
            {
                {"Warbler Core", new Vector3(0, 0, 0)},
                {"Chronicle Keeper", new Vector3(-5, 2, 0)},
                {"Mind Castle Navigator", new Vector3(5, 2, 0)},
                {"Sentiment Analyst", new Vector3(0, 4, -5)},
                {"Decision Synthesizer", new Vector3(0, -2, 5)}
            };

            foreach (var room in facultyRooms)
            {
                CreateRoom(room.Key, room.Value);
            }

            CreateCorridors();
        }

        void CreateRoom(string faculty, Vector3 position)
        {
            var roomObj = Instantiate(roomPrefab, position, Quaternion.identity, transform);
            roomObj.name = $"Room_{faculty}";

            // Color code by faculty type
            var renderer = roomObj.GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.material = GetMaterialForFaculty(faculty);
            }

            var room = new CastleRoom
            {
                RoomObject = roomObj,
                Faculty = faculty,
                Position = position
            };

            _rooms[faculty] = room;
        }

        void SetupAliceFilter()
        {
            var filterPos = _rooms["Decision Synthesizer"].Position + Vector3.up * 2;
            var filterObj = Instantiate(aliceFilterPrefab, filterPos, Quaternion.identity, transform);

            _aliceFilter = new AliceFilter { FilterObject = filterObj };
        }

        void StartWarblerActivity()
        {
            // Continuously spawn Warbler voices (the cacophony)
            InvokeRepeating(nameof(SpawnWarblerVoice), 0f, 0.5f);
        }

        void SpawnWarblerVoice()
        {
            if (_activeVoices.Count >= maxConcurrentVoices) return;

            var startRoom = _rooms["Warbler Core"];
            var voiceObj = Instantiate(warblerVoicePrefab, startRoom.Position, Quaternion.identity, transform);

            var voice = new WarblerVoice
            {
                VoiceObject = voiceObj,
                Content = GenerateRandomThought(),
                TargetPosition = GetRandomRoomPosition(),
                CurrentRoom = startRoom,
                Lifespan = Random.Range(3f, 8f)
            };

            _activeVoices.Add(voice);
            StartCoroutine(AnimateVoiceFlow(voice));
        }

        string GenerateRandomThought()
        {
            var thoughts = new[]
            {
                "implement feature X",
                "refactor code structure",
                "this seems impossible",
                "error in logic",
                "beautiful solution found",
                "need more testing",
                "user will love this",
                "performance optimization needed"
            };
            return thoughts[Random.Range(0, thoughts.Length)];
        }

        Vector3 GetRandomRoomPosition()
        {
            var roomList = _rooms.Values.ToList();
            return roomList[Random.Range(0, roomList.Count)].Position;
        }

        System.Collections.IEnumerator AnimateVoiceFlow(WarblerVoice voice)
        {
            while (voice.Lifespan > 0 && voice.VoiceObject != null)
            {
                // Move towards target room
                voice.VoiceObject.transform.position = Vector3.MoveTowards(
                    voice.VoiceObject.transform.position,
                    voice.TargetPosition,
                    voiceSpeed * Time.deltaTime
                );

                // Check if voice reached Alice filter
                if (voice.VoiceObject != null && _aliceFilter.FilterObject != null &&
                    Vector3.Distance(voice.VoiceObject.transform.position, _aliceFilter.FilterObject.transform.position) < 1f)
                {
                    if (!_aliceFilter.ProcessThought(voice))
                    {
                        // Alice bounced it back - give it a new target
                        voice.TargetPosition = GetRandomRoomPosition();
                    }
                }

                voice.Lifespan -= Time.deltaTime;
                yield return null;
            }

            // Voice has completed its journey or expired
            if (voice.VoiceObject != null)
            {
                Destroy(voice.VoiceObject);
            }
            _activeVoices.Remove(voice);
        }

        Material GetMaterialForFaculty(string faculty)
        {
            return faculty switch
            {
                "Warbler Core" => roomMaterials[0], // Blue
                "Chronicle Keeper" => roomMaterials[1], // Green  
                "Mind Castle Navigator" => roomMaterials[2], // Purple
                "Sentiment Analyst" => roomMaterials[3], // Orange
                "Decision Synthesizer" => roomMaterials[4], // Gold
                _ => roomMaterials[0]
            };
        }

        void CreateCorridors()
        {
            // Connect rooms with flowing data streams
            foreach (var room1 in _rooms.Values)
            {
                foreach (var room2 in _rooms.Values)
                {
                    if (room1 != room2)
                    {
                        CreateDataStream(room1.Position, room2.Position);
                    }
                }
            }
        }

        void CreateDataStream(Vector3 start, Vector3 end)
        {
            var stream = Instantiate(dataStreamPrefab, transform);
            stream.positionCount = 2;
            stream.SetPosition(0, start);
            stream.SetPosition(1, end);

            // Animate the stream to show data flow
            StartCoroutine(AnimateDataStream(stream));
        }

        System.Collections.IEnumerator AnimateDataStream(LineRenderer stream)
        {
            var material = stream.material;
            while (stream != null)
            {
                // Animate texture offset to show flowing data
                material.mainTextureOffset += Vector2.right * Time.deltaTime * 0.5f;
                yield return null;
            }
        }
    }
}
