# RELEASE CRITERIA: Alpha v0.1.0

**Status:** ACTIVE VALIDATION  
**Last Updated:** 2025-01-17  
**Scope:** Transparent Real-World Testing Only

---

## 🎯 RELEASE PHILOSOPHY

This project will NOT release with mock tests or fake claims. Every assertion in the release will be:
- ✅ **Verifiable** - Anyone can run the tests and see real results
- ✅ **Transparent** - Tests show what they actually test (no pretending)
- ✅ **Repeatable** - GitHub Actions CI/CD proves it works every time
- ✅ **Honest** - We document what works AND what's missing

**No fake tests. No mock claims. Only real data flow.**

---

## 📋 REQUIRED FOR ALPHA RELEASE

### Category 1: TEST INFRASTRUCTURE (BLOCKING)

**All tests MUST be categorized correctly:**

| Category | Location | Status | Mock Allowed? |
|----------|----------|--------|---------------|
| **Unit Tests** | `test_*_unit.py` or `@pytest.mark.unit` | Must pass | ✅ Yes, mocks OK |
| **Integration Tests** | `test_*_integration.py` or `@pytest.mark.integration` | Must pass | ⚠️ Limited mocks |
| **E2E Tests** | `test_*_e2e.py` or `@pytest.mark.e2e` | Must pass | ❌ NO mocks allowed |
| **Stress/Load Tests** | `test_*_load.py` or `@pytest.mark.load` | Optional for alpha | ⚠️ Limited mocks |

**ACTION REQUIRED:**
- [ ] Audit ALL test files
- [ ] Tag each test with `@pytest.mark.unit`, `@pytest.mark.integration`, or `@pytest.mark.e2e`
- [ ] Separate mock-based tests from real system tests
- [ ] Create separate test runners:
  - `pytest -m "not e2e"` (fast, includes mocks)
  - `pytest -m "e2e"` (real systems only)

---

### Category 2: REAL SYSTEM E2E TESTS (BLOCKING)

**For Alpha, E2E tests MUST connect to REAL systems:**

#### STAT7 System
```
GitHub Actions Workflow:
  1. Start STAT7 server (real process)
  2. Start WebSocket server (real process)
  3. Launch browser with Playwright (real automation)
  4. Assert entities exist in database
  5. Assert WebSocket messages received
  6. Assert visualization renders
  7. Assert admin can query entity data
```

**Current Status:** `test_stat7_e2e.py` looks real ✅  
**Required Test Cases:**
- [ ] Server starts successfully
- [ ] WebSocket connection established
- [ ] Create entity → verify in database
- [ ] Update entity → websocket broadcasts
- [ ] Query entity by address → returns full data
- [ ] Admin access filters applied correctly

#### WARBLER Integration
```
GitHub Actions Workflow:
  1. Start STAT7 server
  2. Initialize WARBLER bridge
  3. Test plugin system with real plugins (no mocks)
  4. Verify Ollama connectivity (or skip with documented limitation)
  5. Test recovery gates with real manifests
```

**Current Status:** Mixed (some mocks, needs categorization)  
**Required Test Cases:**
- [ ] WFC firewall works with real manifests
- [ ] Recovery gates enforce security rules
- [ ] Plugin system loads real plugins
- [ ] STAT7 bridge communicates correctly
- [ ] No mock objects in the flow

#### GitHub/Authentication
```
Test Strategy: Documented Limitation
- Real GitHub API cannot be tested in CI/CD (requires credentials)
- Solution: Mock GitHub API at integration boundary ONLY
- Document: "GitHub integration tested locally, CI/CD uses mock API"
```

**Current Status:** GitHub tests will use mocks (acceptable, documented)  
**Required:**
- [ ] Mock GitHub API clearly labeled
- [ ] Boundary between real/mock documented
- [ ] Credentials never in test code

---

### Category 3: ADMIN VISUALIZATION (BLOCKING)

**Admin must be able to:**

#### 3.1 View Entities
```python
# REAL TEST CASE:
def test_admin_can_view_entity_in_visualizer():
    """Admin navigates to entity and sees real data."""
    # 1. Create test player entity in STAT7
    player = create_player(name="TestPlayer", realm="alpha-1")
    
    # 2. Admin logs into visualization
    admin_page = browser.goto(ADMIN_UI)
    admin_page.login(admin_credentials)
    
    # 3. Search for player by address
    admin_page.search_entity(player.stat7_address)
    
    # 4. Assert entity appears
    assert admin_page.has_entity(player.stat7_address)
    
    # 5. Assert data is real (not mock)
    assert admin_page.entity_data() == player.data()
```

**Must Show (for Players):**
- ✅ Name, ID, STAT7 address
- ✅ Current position (x, y, z coordinates)
- ✅ Current realm/frequency
- ✅ Character sheet (stats, skills)
- ✅ Action history (last 50 actions)
- ✅ Chat history (last 50 messages)
- ✅ Leaderboard position/rank

**Must Show (for All Entities):**
- ✅ Entity type (player, NPC, object, etc.)
- ✅ STAT7 address (cryptographic identifier)
- ✅ Current state (created, active, paused, etc.)
- ✅ Last modified timestamp
- ✅ Connected entities (relationships)

**Current Status:** Needs building  
**Required:**
- [ ] Admin UI built (HTML/React/Vue)
- [ ] Entity search working
- [ ] Data display working
- [ ] Permission filters applied

#### 3.2 Navigate Realms
```python
# REAL TEST CASE:
def test_admin_can_switch_realms():
    """Admin can view same coordinates in different realms."""
    # 1. Create two overlapping realms
    realm_a = create_realm(name="earth-like", location=(100, 100, 100))
    realm_b = create_realm(name="void-realm", location=(100, 100, 100))  # Same coords, different reality
    
    # 2. Place entities in both
    player_a = create_player(realm=realm_a, coords=(100, 100, 100))
    player_b = create_player(realm=realm_b, coords=(100, 100, 100))
    
    # 3. Admin views realm A
    admin_page.switch_realm(realm_a)
    assert admin_page.has_entity(player_a.address)
    assert not admin_page.has_entity(player_b.address)
    
    # 4. Admin switches to realm B (same location)
    admin_page.switch_realm(realm_b)
    assert not admin_page.has_entity(player_a.address)
    assert admin_page.has_entity(player_b.address)
```

**Must Support:**
- ✅ Multi-realm selector
- ✅ Realm info display
- ✅ Filtering by realm
- ✅ Visual indication of current realm

**Current Status:** Needs building  
**Required:**
- [ ] Realm picker in UI
- [ ] Data filtering by realm
- [ ] Visual differentiation

#### 3.3 Real-Time Position Updates
```python
# REAL TEST CASE:
def test_admin_sees_real_time_entity_movement():
    """Admin sees entity move in real-time (via WebSocket)."""
    # 1. Create entity
    entity = create_entity(coords=(100, 100, 100))
    
    # 2. Admin loads visualization
    admin_page.goto_entity(entity.address)
    initial_pos = admin_page.get_position()
    assert initial_pos == (100, 100, 100)
    
    # 3. Entity moves (in another thread/process)
    entity.move_to((101, 101, 101))
    
    # 4. Admin sees update (within 500ms)
    admin_page.wait_for_position_update(timeout=500)
    new_pos = admin_page.get_position()
    assert new_pos == (101, 101, 101)
```

**Must Support:**
- ✅ WebSocket push updates (not polling)
- ✅ Real-time position sync
- ✅ Sub-500ms latency
- ✅ Visual entity movement

**Current Status:** WebSocket infrastructure exists, UI needs building  
**Required:**
- [ ] WebSocket event broadcasting
- [ ] Browser event listeners
- [ ] Visual entity rendering
- [ ] Position interpolation

---

### Category 4: DATA INTEGRITY (BLOCKING)

**All data shown must be REAL and CONSISTENT:**

```python
# REAL TEST CASE:
def test_data_consistency_database_to_visualization():
    """Data in DB == Data in visualization."""
    # 1. Create entity with specific data
    entity = create_player(
        name="Alice",
        level=42,
        experience=100000,
        stats={"health": 100, "mana": 50}
    )
    
    # 2. Query database directly
    db_data = database.query(entity.id)
    
    # 3. Query via STAT7 API
    api_data = stat7_api.get_entity(entity.address)
    
    # 4. Query via visualization
    admin_page.search(entity.address)
    ui_data = admin_page.get_entity_data()
    
    # 5. All three must match
    assert db_data == api_data == ui_data
```

**Must Verify:**
- [ ] Database has real entity
- [ ] STAT7 API returns exact same data
- [ ] Visualization displays exact same data
- [ ] No transformation/truncation
- [ ] Timestamps match

---

### Category 5: SECURITY & PRIVACY (BLOCKING)

**Admin access must be properly controlled:**

```python
# REAL TEST CASE:
def test_privacy_filters_applied():
    """Sensitive data filtered from non-admin views."""
    # 1. Create player with sensitive data
    player = create_player(
        email="private@example.com",
        last_ip="192.168.1.1",
        payment_info="***",  # Redacted
        private_messages=[...]  # Sensitive
    )
    
    # 2. Regular user views player
    user_view = regular_user.view_player(player.id)
    assert user_view.has_field("name")  # OK
    assert not user_view.has_field("email")  # BLOCKED
    assert not user_view.has_field("payment_info")  # BLOCKED
    
    # 3. Admin views player
    admin_view = admin.view_player(player.id)
    assert admin_view.has_field("name")  # OK
    assert admin_view.has_field("email")  # VISIBLE to admin
    assert admin_view.has_field("payment_info")  # VISIBLE to admin
    
    # 4. Verify admin access is logged
    audit_log = database.get_audit_log()
    assert audit_log.has_entry(admin.id, player.id, "view")
```

**Must Verify:**
- [ ] Admin authentication works
- [ ] Privacy filters applied for non-admin
- [ ] Admin sees unfiltered data
- [ ] Audit logging of admin access
- [ ] No credentials in logs

---

### Category 6: GITHUB ACTIONS CI/CD (BLOCKING)

**Release must pass automated testing:**

```yaml
# .github/workflows/release-validation.yml
name: Release Validation

on: [push, pull_request]

jobs:
  unit_tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests (mocks OK)
        run: pytest -m "not e2e" -v

  e2e_tests:
    runs-on: ubuntu-latest
    services:
      stat7-server:
        image: stat7-server:latest  # REAL server
        ports:
          - 8000:8000
          - 8765:8765  # WebSocket
    steps:
      - uses: actions/checkout@v3
      - name: Wait for services
        run: sleep 5
      - name: Run E2E tests (real systems only)
        run: pytest -m "e2e" -v
```

**Must Pass:**
- [ ] Unit tests: PASS
- [ ] E2E tests: PASS (with real STAT7)
- [ ] Load tests: PASS (optional for alpha)
- [ ] No mock warnings in CI output

---

## ✅ CHECKLIST FOR ALPHA RELEASE

### Pre-Release (This Week)

- [ ] **Encoding**: UTF-8 BOM added to all test files ✅ DONE
- [ ] **Test Categorization**: All tests tagged @pytest.mark.{unit,integration,e2e}
- [ ] **Mock Audit**: All mocks identified and documented
- [ ] **E2E Verification**: Real server tests verified locally
- [ ] **Admin UI**: Basic entity viewer built and tested
- [ ] **Real Data Tests**: Confirm entity data flows database → API → UI

### Release (Alpha v0.1.0)

- [ ] GitHub Actions workflow passes
- [ ] All E2E tests use real STAT7 server (documented in workflow)
- [ ] Admin can view player entities with real data
- [ ] Admin can see player actions/commands/chat history
- [ ] Multi-realm support working (documented)
- [ ] Privacy filters applied and tested
- [ ] Release notes document:
  - [ ] What's tested (real)
  - [ ] What's limited (documented)
  - [ ] What requires external service (documented)

---

## 📌 WHAT'S NOT REQUIRED FOR ALPHA

These can wait for Beta or later:

- ❌ Character sheet interactive editing
- ❌ Full skill tree visualization
- ❌ 3D game world rendering
- ❌ Player leaderboard UI
- ❌ External hosting
- ❌ Load testing at scale (>1000 concurrent)
- ❌ GitHub API real integration (documented as limitation)

---

## 🚨 THINGS THAT WILL GET YOU LAUGHED OUT OF A ROOM

**DO NOT DO THESE:**

1. ❌ Run mock tests and claim "E2E tests passing"
2. ❌ Claim visualization works when it's not built
3. ❌ Use fake data in real test assertions
4. ❌ Document limitations but hide them
5. ❌ Let untested features ship
6. ❌ Claim security when it's not tested

---

## 📞 HOW TO VALIDATE BEFORE RELEASE

**For the Researcher/Auditor:**

```bash
# Clone repo
git clone https://github.com/twg/the-seed.git
cd the-seed

# Run unit tests (these use mocks, that's OK)
pytest -m "not e2e" -v

# Verify tests are real
grep -r "MockEmbeddingProvider" tests/  # Find mocks
grep -r "@pytest.mark.e2e" tests/      # Find real tests

# Run E2E tests (must have real STAT7 running)
python start_stat7.py &                # Start real server
pytest -m "e2e" -v                     # Run real tests

# View admin UI (if available)
# Navigate to http://localhost:8000/admin
# Search for an entity
# Verify data matches database
```

**Expected Output:**
- ✅ Unit tests: GREEN (mocks used, that's OK)
- ✅ E2E tests: GREEN (real server tested)
- ✅ Admin UI: FUNCTIONAL (shows real data)
- ✅ Data matches: DATABASE == API == UI

---

## 🎯 BOTTOM LINE

**Before we call this "Alpha v0.1.0", you will be able to tell a University:**

> "Every test that says E2E actually connects to real servers and real databases. Every assertion is verifiable. Here's the GitHub Actions log proving it works every commit. Here's the admin tool showing real player data. Here's the audit log showing what admin accessed. I can prove this is real."

**That's what Alpha looks like.**

---

**Document Version:** 1.0  
**Last Review:** 2025-01-17  
**Author:** QA Automation Framework  
**Status:** ACTIVE (implementation in progress)