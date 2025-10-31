# Phase 6B REST API - Quick Start Guide

**Last Updated**: 2025-10-31  
**Status**: Production Ready

---

## 🚀 Quick Start (30 seconds)

```python
import asyncio
from phase6b_rest_api import launch_api_server

async def main():
    # Launch API server with demo universe
    api_server = await launch_api_server(
        seed=42,
        orbits=2,
        realms=["overworld", "tavern"]
    )
    
    # Run with uvicorn
    import uvicorn
    uvicorn.run(api_server.app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    asyncio.run(main())
```

**Access the API**:
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

---

## 📚 API Endpoints Reference

### 🏥 Health Check

```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-31T12:00:00Z",
  "orchestrator_initialized": true
}
```

---

### 🌍 Realm Endpoints

#### List All Realms

```http
GET /api/realms
```

**Response**:
```json
{
  "realms": [
    {
      "realm_id": "tavern",
      "entity_count": 15,
      "lineage": "bigbang→tavern",
      "tier": "terran",
      "theme": "city_state"
    }
  ]
}
```

#### Get Realm Details

```http
GET /api/realms/{realm_id}
```

**Example**: `GET /api/realms/tavern`

**Response**:
```json
{
  "realm_id": "tavern",
  "entity_count": 15,
  "lineage": "bigbang→tavern",
  "tier": "terran",
  "theme": "city_state",
  "semantic_anchors": ["urban", "social"],
  "entities": [
    {
      "id": "entity_001",
      "type": "building",
      "position": [10.0, 0.0, 5.0],
      "stat7": {...},
      "metadata": {...},
      "enrichment_count": 3
    }
  ]
}
```

#### Get Tier Metadata

```http
GET /api/realms/{realm_id}/tier
```

**Example**: `GET /api/realms/tavern/tier`

**Response**:
```json
{
  "realm_id": "tavern",
  "tier": "terran",
  "theme": "city_state",
  "semantic_anchors": ["urban", "social"],
  "tier_depth": 0,
  "parent_realm_id": null,
  "parent_entity_id": null,
  "created_at": "2025-10-31T12:00:00Z"
}
```

---

### 🎯 Tier Query Endpoints

#### Query Realms by Tier

```http
GET /api/realms/by-tier/{tier}
```

**Valid Tiers**: `celestial`, `terran`, `subterran`

**Example**: `GET /api/realms/by-tier/terran`

**Response**:
```json
{
  "realms": [
    {
      "realm_id": "tavern",
      "entity_count": 15,
      "lineage": "bigbang→tavern",
      "tier": "terran",
      "theme": "city_state"
    }
  ]
}
```

#### Query Realms by Theme

```http
GET /api/realms/by-theme/{theme}
```

**Valid Themes**: 
- Celestial: `heaven`, `aether`, `ascension`
- Terran: `overworld`, `city_state`, `rural`, `frontier`
- Subterran: `hell`, `abyss`, `underdark`, `dystopia`

**Example**: `GET /api/realms/by-theme/city_state`

---

### 🔍 Sub-Realm Navigation

#### Create Sub-Realm via Zoom

```http
POST /api/realms/{realm_id}/zoom
```

**Request Body**:
```json
{
  "entity_id": "entity_001",
  "additional_anchors": ["interior", "close_up"]
}
```

**Response**:
```json
{
  "sub_realm_id": "tavern_entity_001",
  "parent_realm_id": "tavern",
  "entity_id": "entity_001",
  "tier": "terran",
  "theme": "city_state",
  "tier_depth": 1,
  "semantic_anchors": ["urban", "social", "interior", "close_up"]
}
```

---

### 🤖 NPC Endpoints

#### List All NPCs

```http
GET /api/npcs
```

**Response**:
```json
{
  "npcs": [
    {
      "npc_id": "npc_001",
      "npc_name": "Barkeep Aldous",
      "realm_id": "tavern",
      "entity_type": "humanoid"
    }
  ]
}
```

#### Get NPC Details

```http
GET /api/npcs/{npc_id}
```

**Example**: `GET /api/npcs/npc_001`

**Response**:
```json
{
  "npc_id": "npc_001",
  "npc_name": "Barkeep Aldous",
  "realm_id": "tavern",
  "entity_type": "humanoid",
  "stat7_coordinates": "T1:L0:A5:H3:R2:V1:D4",
  "personality_traits": {
    "openness": 0.7,
    "conscientiousness": 0.8,
    "extraversion": 0.6,
    "agreeableness": 0.9,
    "neuroticism": 0.3
  },
  "enrichment_history": ["phase2", "phase3", "phase4"]
}
```

#### Get Dialogue Context

```http
GET /api/npcs/{npc_id}/context
```

**Example**: `GET /api/npcs/npc_001/context`

**Response**:
```json
{
  "npc_id": "npc_001",
  "realm_id": "tavern",
  "location_type": "indoor",
  "time_of_day": "evening",
  "npc_mood": "friendly",
  "narrative_phase": "introduction",
  "dialogue_turn": 0,
  "enrichment_depth": 3
}
```

---

### 📦 Universe Export

#### Export Full Universe

```http
GET /api/universe/export
```

**Response**:
```json
{
  "seed": 42,
  "total_orbits_completed": 2,
  "total_entities": 30,
  "initialization_time_ms": 156.7,
  "realms": {
    "tavern": {...},
    "overworld": {...}
  },
  "metadata": {
    "universe_initialized_at": "2025-10-31T12:00:00Z",
    "realm_entity_counts": {
      "tavern": 15,
      "overworld": 15
    }
  }
}
```

---

## 🔧 Advanced Configuration

### Custom Orchestrator Setup

```python
from phase6b_rest_api import Phase6BAPIServer
from phase6_orchestrator import UniverseDemoOrchestrator, OrchestratorConfig
from phase6_hierarchical_realms import (
    HierarchicalUniverseAdapter,
    TierClassification,
    TierTheme
)

# Step 1: Create orchestrator
config = OrchestratorConfig(
    seed=42,
    orbits=3,
    realms=["tavern", "overworld", "dungeon"]
)
orchestrator = UniverseDemoOrchestrator(config)
await orchestrator.launch_demo()

# Step 2: Create API server
api_server = Phase6BAPIServer(orchestrator)

# Step 3: Initialize hierarchical adapter
api_server.hierarchical_adapter = HierarchicalUniverseAdapter(
    orchestrator.universe
)

# Step 4: Classify realms
await api_server.hierarchical_adapter.initialize_with_tier_classification({
    "tavern": (TierClassification.TERRAN, TierTheme.CITY_STATE, ["urban"]),
    "overworld": (TierClassification.TERRAN, TierTheme.OVERWORLD, ["nature"]),
    "dungeon": (TierClassification.SUBTERRAN, TierTheme.UNDERDARK, ["dark"]),
})

# Step 5: Run server
import uvicorn
uvicorn.run(api_server.app, host="0.0.0.0", port=8000)
```

---

## 🧪 Testing the API

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# List realms
response = requests.get(f"{BASE_URL}/api/realms")
realms = response.json()["realms"]
print(f"Found {len(realms)} realms")

# Get realm details
response = requests.get(f"{BASE_URL}/api/realms/tavern")
tavern = response.json()
print(f"Tavern has {tavern['entity_count']} entities")

# Query by tier
response = requests.get(f"{BASE_URL}/api/realms/by-tier/terran")
terran_realms = response.json()["realms"]
print(f"Found {len(terran_realms)} terran realms")

# Create sub-realm
zoom_request = {
    "entity_id": "entity_001",
    "additional_anchors": ["interior"]
}
response = requests.post(
    f"{BASE_URL}/api/realms/tavern/zoom",
    json=zoom_request
)
sub_realm = response.json()
print(f"Created sub-realm: {sub_realm['sub_realm_id']}")
```

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# List realms
curl http://localhost:8000/api/realms

# Get realm details
curl http://localhost:8000/api/realms/tavern

# Query by tier
curl http://localhost:8000/api/realms/by-tier/terran

# Create sub-realm
curl -X POST http://localhost:8000/api/realms/tavern/zoom \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "entity_001", "additional_anchors": ["interior"]}'
```

---

## ⚠️ Error Handling

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Successful GET request |
| 404 | Not Found | Realm or NPC doesn't exist |
| 400 | Bad Request | Invalid tier/theme enum |
| 503 | Service Unavailable | Adapter not initialized |

### Error Response Format

```json
{
  "detail": {
    "error": "Realm 'unknown_realm' not found"
  }
}
```

### Python Error Handling

```python
import requests

try:
    response = requests.get("http://localhost:8000/api/realms/unknown")
    response.raise_for_status()
except requests.HTTPError as e:
    if e.response.status_code == 404:
        error = e.response.json()["detail"]["error"]
        print(f"Realm not found: {error}")
```

---

## 🔒 Production Deployment

### Using Uvicorn with Production Settings

```bash
uvicorn phase6b_rest_api:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info \
  --access-log
```

### Docker Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "packages.com.twg.the-seed.seed.engine.phase6b_rest_api:app", \
     "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t the-seed-api .
docker run -p 8000:8000 the-seed-api
```

---

## 📊 Performance Considerations

### Recommended Settings

- **Workers**: 2-4 (depends on CPU cores)
- **Timeout**: 60 seconds (for sub-realm creation)
- **Max Connections**: 100 (per worker)

### Caching Strategy

For production, consider caching:
- Realm lists (cache for 60 seconds)
- Tier metadata (cache until universe rebuild)
- NPC lists (cache for 30 seconds)

### Load Testing

```bash
# Install wrk
sudo apt-get install wrk

# Test health endpoint
wrk -t4 -c100 -d30s http://localhost:8000/health

# Test realm listing
wrk -t4 -c100 -d30s http://localhost:8000/api/realms
```

---

## 🐛 Troubleshooting

### Issue: "Hierarchical adapter not initialized"

**Symptom**: HTTP 503 error when accessing tier endpoints

**Solution**:
```python
# Ensure adapter is initialized before starting server
api_server.hierarchical_adapter = HierarchicalUniverseAdapter(
    orchestrator.universe
)
await api_server.hierarchical_adapter.initialize_with_tier_classification({
    "tavern": (TierClassification.TERRAN, TierTheme.CITY_STATE, ["urban"]),
})
```

### Issue: "Bridge not initialized"

**Symptom**: HTTP 503 error when accessing NPC endpoints

**Solution**:
```python
# Ensure orchestrator launches demo with bridge
await orchestrator.launch_demo()  # This initializes the bridge
```

### Issue: Slow sub-realm creation

**Symptom**: POST /api/realms/{realm_id}/zoom takes >5 seconds

**Cause**: Procedural generation is compute-intensive

**Solutions**:
- Use smaller entity counts (reduce `orbits` config)
- Enable async workers for parallel processing
- Cache generated sub-realms

---

## 📖 Further Reading

- [Phase 6B Delivery Summary](../PHASE6B_REST_API_DELIVERY.md)
- [Phase 6A Orchestrator Documentation](./PHASE6A_ORCHESTRATOR.md)
- [Phase 6-Alpha Hierarchical Realms](./PHASE6_ALPHA_HIERARCHICAL_REALMS.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 🎯 Next Steps

1. **Test the API**: Run the quick start example
2. **Explore Endpoints**: Use the Swagger UI at `/docs`
3. **Build a Client**: Create a dashboard or CLI tool
4. **Deploy to Production**: Use Docker or cloud hosting
5. **Integrate with Unity**: Create C# REST client

---

**Happy coding! The multiverse awaits. 🌱**