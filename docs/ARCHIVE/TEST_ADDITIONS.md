# 🧪 Test Additions Reference

## New Test Functions Added to `test_websocket_load_stress.py`

### **SOFT-CAP DISCOVERY TESTS** (Lines 239-268)

#### 1. `test_concurrent_250_clients()`
- **Players**: 250
- **Events**: 5 per client
- **Purpose**: Early stress exploration
- **Expected**: HEALTHY (exploration zone)
- **Runtime**: 40 minutes

```python
@pytest.mark.asyncio
@pytest.mark.slow
async def test_concurrent_250_clients():
    """Test 250 concurrent clients (high load - soft-cap exploration)."""
    await _test_concurrent_clients(num_clients=250, num_events=5)
```

---

#### 2. `test_concurrent_1000_clients()`
- **Players**: 1000
- **Events**: 3 per client
- **Purpose**: Extreme load boundary testing
- **Expected**: HEALTHY or DEGRADED (depends on system)
- **Runtime**: 60 minutes

```python
@pytest.mark.asyncio
@pytest.mark.slow
async def test_concurrent_1000_clients():
    """Test 1000 concurrent clients (extreme load - soft-cap boundary)."""
    await _test_concurrent_clients(num_clients=1000, num_events=3)
```

---

#### 3. `test_concurrent_2500_clients()` ⭐
- **Players**: 2500
- **Events**: 2 per client
- **Purpose**: SOFT-CAP ZONE - Find where degradation starts
- **Expected**: DEGRADED (where soft-cap begins)
- **Runtime**: 75 minutes
- **Key**: First test to show stress indicators

```python
@pytest.mark.asyncio
@pytest.mark.slow
async def test_concurrent_2500_clients():
    """Test 2500 concurrent clients (ultra-extreme load - soft-cap push)."""
    await _test_concurrent_clients(num_clients=2500, num_events=2)
```

---

#### 4. `test_concurrent_5000_clients()` 🔥
- **Players**: 5000
- **Events**: 1 per client
- **Purpose**: BREAKING POINT - System stress limit
- **Expected**: CRITICAL (system under heavy duress)
- **Runtime**: 90 minutes
- **Key**: Where system likely fails or severely degrades

```python
@pytest.mark.asyncio
@pytest.mark.slow
async def test_concurrent_5000_clients():
    """Test 5000 concurrent clients (absolute stress - breaking point discovery)."""
    await _test_concurrent_clients(num_clients=5000, num_events=1)
```

---

### **HARDCORE STRESS PATTERNS** (Lines 271-300)

#### 5. `test_message_flood_500_clients()` 🌊
- **Players**: 500
- **Pattern**: High-frequency message flooding
- **Configuration**: 100 messages/second for 10 seconds
- **Purpose**: Throughput limit testing
- **Measures**: Message delivery under rapid fire
- **Runtime**: 50 minutes

```python
@pytest.mark.asyncio
@pytest.mark.slow
async def test_message_flood_500_clients():
    """Sustained high-frequency message flooding with 500 clients."""
    await _test_concurrent_clients_message_flood(num_clients=500, messages_per_sec=100)
```

**What it tests**:
- 🌊 Rapid message bombardment (100 msg/sec)
- 📊 Message drop detection
- 🔍 Reception degradation
- ⚠️ System queue saturation

---

#### 6. `test_message_flood_1000_clients()` 🌊
- **Players**: 1000
- **Pattern**: High-frequency message flooding
- **Configuration**: 50 messages/second for 10 seconds
- **Purpose**: Sustained load at extreme scale
- **Measures**: Message delivery with 1000 concurrent clients
- **Runtime**: 60 minutes

```python
@pytest.mark.asyncio
@pytest.mark.slow
async def test_message_flood_1000_clients():
    """Sustained high-frequency message flooding with 1000 clients."""
    await _test_concurrent_clients_message_flood(num_clients=1000, messages_per_sec=50)
```

**What it tests**:
- 🌊 Sustained high-frequency under extreme load
- 📊 Connection pool stress
- 🔍 Reception rate degradation
- ⚠️ Message queue limits

---

#### 7. `test_connection_spike_500_clients()` 📈
- **Players**: 500
- **Pattern**: Connection spikes (batched ramp-up)
- **Spike Batch Size**: 50 clients per spike
- **Purpose**: Real-world cluster scaling simulation
- **Runtime**: 50 minutes

```python
@pytest.mark.asyncio
@pytest.mark.slow
async def test_connection_spike_500_clients():
    """Rapid connection spikes (gradual ramp-up under load)."""
    await _test_concurrent_clients_spike_pattern(num_clients=500, spike_batch=50)
```

**Two-Phase Test**:
1. **Phase 1**: Rapid connection spikes (50 clients at a time)
   - 10 spikes total to reach 500 clients
   - 0.5s pause between spikes
   
2. **Phase 2**: Sustained messaging under spike load
   - 5 seconds of continuous messages (~20 msg/sec)
   - Measures delivery rate during load

**What it tests**:
- 📈 Connection pool ramp-up
- 🔄 System recovery during load
- ⚡ Message delivery during spike phase
- 🔍 Connection state management

---

#### 8. `test_connection_spike_1000_clients()` 📈
- **Players**: 1000
- **Pattern**: Connection spikes (batched ramp-up)
- **Spike Batch Size**: 100 clients per spike
- **Purpose**: Large-scale cluster scaling simulation
- **Runtime**: 65 minutes

```python
@pytest.mark.asyncio
@pytest.mark.slow
async def test_connection_spike_1000_clients():
    """Rapid connection spikes with 1000 clients."""
    await _test_concurrent_clients_spike_pattern(num_clients=1000, spike_batch=100)
```

**Two-Phase Test**:
1. **Phase 1**: Rapid connection spikes (100 clients at a time)
   - 10 spikes total to reach 1000 clients
   - Tests connection pool at extreme scale
   
2. **Phase 2**: Sustained messaging
   - 5 seconds of messages (~20 msg/sec)
   - Shows system behavior under scaled load

**What it tests**:
- 📈 Large-scale ramp-up behavior
- 🔄 Connection pool at 1000+ scale
- ⚡ System response to rapid scaling
- 🔍 Message delivery during scale events

---

### **HELPER FUNCTIONS** (NEW)

#### `_test_concurrent_clients_message_flood(num_clients, messages_per_sec)`
**Purpose**: Hardcore stress test with sustained message flooding

**Parameters**:
- `num_clients`: Number of concurrent clients (500 or 1000)
- `messages_per_sec`: Message frequency (100 or 50)

**What it does**:
1. Connect all clients in parallel
2. Run 10-second message flood at specified rate
3. Measure reception rate per client
4. Detect message drops
5. Analyze degradation patterns

**Metrics collected**:
- Connection time
- Message flood duration
- Messages sent vs received
- Average/min/max reception per client
- Reception rate percentage
- Drops detected

**Severity mapping**:
- 0% drops = HEALTHY
- 1-5% drops = DEGRADED
- >5% drops = CRITICAL

---

#### `_test_concurrent_clients_spike_pattern(num_clients, spike_batch)`
**Purpose**: Hardcore stress test with connection spikes

**Parameters**:
- `num_clients`: Total clients to eventually connect (500 or 1000)
- `spike_batch`: Clients per spike batch (50 or 100)

**Two-phase structure**:

**Phase 1 - Connection Spikes**:
- Connect in batches
- Each batch takes ~spike_time seconds
- 0.5s pause between spikes
- Measures ramp-up duration

**Phase 2 - Sustained Messaging**:
- Once all connected, send messages for 5 seconds
- ~20 messages/second rate
- Measures delivery during sustained load
- Calculates reception rate

**Metrics collected**:
- Per-spike connection time
- Overall connection time
- Messages sent
- Average/min/max reception
- Reception rate percentage
- System stability indicators

**Severity mapping**:
- <1% drops = HEALTHY
- 1-5% drops = DEGRADED
- >5% drops = CRITICAL

---

## 🔍 Existing Test Functions (Unchanged)

These still work and are used by the matrix strategy:

```python
test_concurrent_10_clients()    # Basic test
test_concurrent_50_clients()    # Light load
test_concurrent_100_clients()   # Standard low
test_concurrent_500_clients()   # Standard high
```

All new tests extend from these existing patterns.

---

## 📊 Test Statistics

### **Total New Tests**: 8
- 4 soft-cap discovery tests (250, 1000, 2500, 5000)
- 2 message flood tests (500, 1000)
- 2 connection spike tests (500, 1000)

### **Helper Functions**: 2
- `_test_concurrent_clients_message_flood()`
- `_test_concurrent_clients_spike_pattern()`

### **Lines Added**:
- Test definitions: ~60 lines
- Helper functions: ~180 lines
- Total: ~240 lines added

### **Backward Compatibility**: ✅ 100%
- All existing tests unchanged
- New tests use same helper pattern
- Can run individually or in matrix

---

## 🚀 Running Tests Individually

### **From Command Line**

```bash
# Run single test
pytest tests/test_websocket_load_stress.py::test_concurrent_2500_clients -v

# Run soft-cap tests only
pytest tests/test_websocket_load_stress.py -k "concurrent_250 or concurrent_1000 or concurrent_2500 or concurrent_5000" -v

# Run stress patterns only
pytest tests/test_websocket_load_stress.py -k "message_flood or connection_spike" -v

# Run all new tests
pytest tests/test_websocket_load_stress.py -k "250 or 1000 or 2500 or 5000 or flood or spike" -v
```

### **From GitHub Actions**

All tests are automatically selected by matrix strategy when you run the workflow.

---

## 🎯 Test Execution Matrix

| Test | Players | Pattern | Phase 1 | Phase 2 | Timeout |
|------|---------|---------|---------|---------|---------|
| 250 std | 250 | Concurrent | - | 5s msgs | 40 min |
| 1000 std | 1000 | Concurrent | - | 3s msgs | 60 min |
| 2500 std | 2500 | Concurrent | - | 2s msgs | 75 min |
| 5000 std | 5000 | Concurrent | - | 1s msgs | 90 min |
| 500 flood | 500 | Flooding | - | 10s flood | 50 min |
| 1000 flood | 1000 | Flooding | - | 10s flood | 60 min |
| 500 spike | 500 | Spikes | Ramp-up | 5s msgs | 50 min |
| 1000 spike | 1000 | Spikes | Ramp-up | 5s msgs | 65 min |

---

**All tests marked with `@pytest.mark.slow` for easy filtering**

Use: `pytest -m slow` to run only stress tests
Use: `pytest -m "not slow"` to skip stress tests