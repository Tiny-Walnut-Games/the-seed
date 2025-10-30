# ⚡ Quick Start: Finding Your MMO Soft-Cap

## 🚀 Start Here

### **Step 1: Go to Actions**
```
GitHub → Your Repo → Actions Tab
```

### **Step 2: Select "MMO Load Test - Third-Party Validation"**

### **Step 3: Click "Run workflow"**

### **Step 4: Configure Your Test**

```
Player Count:    ← SELECT HERE
  ├─ 100         (baseline)
  ├─ 250         (early stress)
  ├─ 500         (standard)
  ├─ 1000        (extreme)
  ├─ 2500        ⭐ SOFT-CAP ZONE
  ├─ 5000        🔥 BREAKING POINT
  └─ comprehensive (all tests)

Stress Pattern:  ← AND HERE
  ├─ standard    (concurrent connections)
  ├─ message-flood (high-frequency flood)
  ├─ connection-spikes (rapid ramp-up)
  └─ all         (run all patterns)
```

### **Step 5: Click "Run workflow"**

---

## 📊 What Happens Next

### **Parallel Matrix Execution**
```
All 10 test configurations run simultaneously:

✅ 100 players standard
✅ 250 players standard  
✅ 500 players standard
✅ 1000 players standard
⚠️  2500 players standard     ← Watch here
🔥 5000 players standard      ← And here
🌊 500 players message-flood
🌊 1000 players message-flood
📈 500 players connection-spikes
📈 1000 players connection-spikes
```

**Total Time**: ~90 minutes (parallel execution)

---

## 🎯 Reading the Results

### **GitHub Issues Created**
After each test completes, a GitHub Issue is created:

```
✅ MMO Load Test: 500-players-standard - HEALTHY - 2024-01-15
   Severity: HEALTHY
   Players: 500
   Pattern: standard
   
   🎯 Soft-Cap Analysis
   - Connection failures: 0
   - Message drops: 0.00%
   - Latency spike: NO
   
   📊 Performance Metrics
   - Avg Latency: 245ms
   - P99 Latency: 890ms
   - Reception rate: 100.0%
```

---

## 🔍 Finding Your Soft-Cap

### **Look for This Pattern**

```
✅ 500 players   = HEALTHY    (no issues)
✅ 1000 players  = HEALTHY    (no issues)
⚠️  2500 players  = DEGRADED   ← SOFT-CAP STARTS HERE
🔥 5000 players  = CRITICAL   (system struggling)
```

### **The Exact Point**

The **soft-cap** is where you see:
- First message drops (>0.5%)
- Latency spikes (P99 > 1000ms)
- Connection timeouts
- First labeled "DEGRADED"

---

## 💾 Artifacts & Logs

Each test produces artifacts (saved for 90 days):

```
test-results/
├── load-test-output.log           (raw output)
├── metrics.json                    (parsed metrics)
├── load-test-500-players.xml       (JUnit format)
└── VALIDATION_REPORT.md            (formatted report)
```

**Download from**: Actions Run → Artifacts

---

## 🎓 Example: Finding a 2000-Player Soft-Cap

### **Run 1**: Test boundaries
```
Select: player_count = 1000, stress_patterns = standard
Result: ✅ HEALTHY
Next: Try higher
```

### **Run 2**: Push harder
```
Select: player_count = 5000, stress_patterns = standard
Result: 🔥 CRITICAL (too much)
Next: Narrow down
```

### **Run 3**: Find the zone
```
Select: player_count = 2500, stress_patterns = standard
Result: ⚠️ DEGRADED (getting close)
Next: Test in between
```

### **Run 4**: Binary search
```
Select: player_count = 1500, stress_patterns = standard
Result: ✅ HEALTHY
Next: Test 2000
```

### **Run 5**: Pinpoint
```
Select: player_count = 2000, stress_patterns = standard
Result: ⚠️ DEGRADED (found it!)
```

**Conclusion**: Soft-cap is between 1500-2000 players

---

## 🔧 Stress Pattern Differences

### **Standard** (Most useful for soft-cap)
- Simple concurrent connections
- Measures baseline capacity
- Best for: Finding the absolute limit

### **Message Flood** (Stress testing)
- Rapid message bombardment
- Measures throughput limits
- Best for: Finding message bandwidth limits

### **Connection Spikes** (Real-world simulation)
- Rapid on/off patterns
- Measures connection pool limits
- Best for: Finding cluster scaling limits

---

## ✅ Metrics to Watch

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| **Avg Latency** | <250ms | 250-500ms | >500ms |
| **P99 Latency** | <500ms | 500-1000ms | >1000ms |
| **Message Drops** | 0% | 0.5-5% | >5% |
| **Connection Success** | 100% | 99-100% | <99% |
| **Reception Rate** | 100% | 98-100% | <98% |

---

## 🚀 Next Actions

1. **Run your first test** (player_count = 500, stress = standard)
2. **Check the results** in GitHub Issues
3. **Note the metrics** 
4. **Try 2500 players** to find where degradation starts
5. **Iterate** to find exact soft-cap

---

## 📞 Troubleshooting

### **Tests Keep Timing Out**
- The player count may be too high for your system
- Check runner specs (usually GitHub's ubuntu-latest)
- Review artifact logs for error messages

### **Metrics Not Captured**
- Look for test output messages in the step logs
- Check if the test actually ran (look for connection messages)
- Verify pytest output format matches regex patterns

### **GitHub Issue Not Created**
- Test may have failed (check FAILED issues)
- Issues only created if test.outputs.test_status == 'PASSED'
- Check workflow logs for errors

---

## 📚 Full Documentation

See: `.github/SOFT_CAP_STRESS_TEST_UPGRADE.md`

---

**Ready? 🎯 Go to Actions and run your first comprehensive soft-cap discovery!**