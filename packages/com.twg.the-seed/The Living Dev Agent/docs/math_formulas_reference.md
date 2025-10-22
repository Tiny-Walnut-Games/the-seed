# Mathematical Formulas Reference
## STAT7-RAG Stress Testing & Performance Analysis

### 📊 Core Performance Metrics

#### 1. **Latency Calculations**

**Average Latency:**
```
μ_latency = (1/n) * Σ(i=1 to n) latency_i
```

**Standard Deviation:**
```
σ_latency = √[(1/n) * Σ(i=1 to n) (latency_i - μ_latency)²]
```

**Coefficient of Variation (CV):**
```
CV = σ_latency / μ_latency
```
*Interpretation: CV < 0.3 = stable, CV > 0.5 = unstable*

#### 2. **Hybrid Scoring Mathematics**

**STAT7 Resonance Score:**
```
R_stat7 = w_l * L_norm + w_p * P_norm + w_d * D_norm + w_h * H_norm + w_a * A_norm
```
Where:
- `L_norm` = normalized luminosity (0-1)
- `P_norm` = normalized polarity (0-1)
- `D_norm` = normalized dimensionality (1/7)
- `H_norm` = normalized horizon score
- `A_norm` = normalized adjacency
- `w_*` = weighting factors (default: 0.2 each)

**Cosine Similarity:**
```
S_cosine = (q · d) / (||q|| * ||d||)
```

**Hybrid Score:**
```
S_hybrid = α * S_cosine + (1-α) * R_stat7
```
Where `α` = semantic weight (typically 0.6-0.8)

#### 3. **Quality Improvement Metrics**

**Score Improvement:**
```
Δ_quality = μ_hybrid_scores - μ_semantic_scores
```

**Overlap Percentage:**
```
P_overlap = (|Results_semantic ∩ Results_hybrid| / k) * 100
```
Where `k` = number of top results (typically 10)

**Average Reranking Distance:**
```
D_rerank = (1/k) * Σ(i=1 to k) |pos_semantic(i) - pos_hybrid(i)|
```

#### 4. **Throughput Calculations**

**Documents per Second:**
```
TPS_docs = N_docs / T_generation
```

**Queries per Second:**
```
QPS = 1000 / μ_latency_ms
```

**Concurrent Load Capacity:**
```
L_concurrent = QPS * N_users
```

#### 5. **Server Performance Grading**

**Response Time Grade:**
```
Grade = {
  A+: t < 50ms
  A : 50ms ≤ t < 100ms
  B : 100ms ≤ t < 200ms
  C : 200ms ≤ t < 500ms
  D : t ≥ 500ms
}
```

**Performance Score:**
```
S_performance = 100 * exp(-t_latency / 100)
```

#### 6. **Scalability Projections**

**Hourly Capacity:**
```
C_hourly = QPS * 3600
```

**Daily Capacity:**
```
C_daily = C_hourly * 24
```

**Resource Efficiency:**
```
E_resource = TPS_docs / M_usage_MB
```

#### 7. **STAT7 Dimension Normalization**

**Luminosity Normalization:**
```
L_norm = (L - L_min) / (L_max - L_min)
```

**Polarity Normalization:**
```
P_norm = |P| / P_max
```

**Dimensionality Normalization:**
```
D_norm = D / D_max  # D_max = 7
```

**Adjacency Normalization:**
```
A_norm = A / A_max  # A_max = 1.0
```

#### 8. **Temporal Decay Functions**

**Exponential Decay:**
```
D_temporal(t) = exp(-t / τ)
```
Where `τ` = decay constant (typically 24 hours)

**Temporal Relevance:**
```
R_temporal = max(0.1, 1.0 - age_hours / 24.0)
```

#### 9. **Cache Performance Metrics**

**Hit Rate:**
```
HR = N_hits / (N_hits + N_misses)
```

**Cache Efficiency:**
```
E_cache = HR - min(N_cache / 100, 0.2)
```

#### 10. **Assembly Quality Score**

**Quality Components:**
```
Q_relevance = (1/k) * Σ(i=1 to k) score_i
Q_coverage = min(k/k_max, 1.0)
Q_conflict = max(0, 1.0 - N_conflicts * 0.1)
Q_diversity = min(N_types / 3.0, 1.0)
```

**Overall Quality:**
```
Q_assembly = 0.4*Q_relevance + 0.2*Q_coverage + 0.2*Q_conflict + 0.2*Q_diversity
```

### 🧮 Statistical Analysis Formulas

#### 11. **Confidence Intervals**

**95% Confidence Interval for Mean:**
```
CI_95 = μ ± 1.96 * (σ / √n)
```

#### 12. **Percentile Calculations**

**95th Percentile (P95):**
```
P95 = μ + 1.645 * σ
```

**99th Percentile (P99):**
```
P99 = μ + 2.326 * σ
```

#### 13. **Trend Analysis**

**Linear Trend Coefficient:**
```
β = Σ((x_i - x̄)(y_i - ȳ)) / Σ((x_i - x̄)²)
```

**Trend Direction:**
```
Direction = sign(β)
```

### 🔍 Optimization Metrics

#### 14. **Latency Overhead Analysis**

**Percentage Overhead:**
```
O_latency = ((T_hybrid - T_semantic) / T_semantic) * 100
```

**Acceptable Threshold:**
```
O_acceptable = 10%  # Maximum acceptable overhead
```

#### 15. **Memory Efficiency**

**Memory per Document:**
```
M_per_doc = M_total / N_docs
```

**Memory Growth Rate:**
```
R_memory = ΔM / Δt
```

### 📈 Composite Metrics

#### 16. **System Health Score**

**Health Components:**
```
H_latency = max(0, 1 - μ_latency / 500)
H_throughput = min(1, TPS / 1000)
H_quality = max(0, Δ_quality + 0.5)
H_stability = max(0, 1 - CV)
```

**Overall Health:**
```
H_system = 0.3*H_latency + 0.3*H_throughput + 0.2*H_quality + 0.2*H_stability
```

#### 17. **Performance Index**

**Performance Index (PI):**
```
PI = (QPS / QPS_target) * (1000 / μ_latency) * (1 + Δ_quality) * HR
```

### 🎯 Decision Thresholds

#### 18. **Performance Decision Rules**

**Pass/Fail Criteria:**
```
Pass_Overall = (O_latency < 10%) AND (Δ_quality > -0.25) AND (H_system > 0.7)
```

**Optimization Priority:**
```
Priority = max(
  severity_latency * weight_latency,
  severity_throughput * weight_throughput,
  severity_quality * weight_quality
)
```

---

## 📚 Notation Legend

| Symbol | Meaning | Typical Range |
|--------|---------|---------------|
| μ | Mean/Average | Variable |
| σ | Standard Deviation | ≥ 0 |
| n | Sample Size | ≥ 1 |
| k | Top-K Results | 1-100 |
| α | Semantic Weight | 0.6-0.8 |
| τ | Time Constant | Hours |
| t | Time | Seconds/Hours |
| N | Count | ≥ 0 |
| w | Weight | 0-1 |
| L | Luminosity | 0-1 |
| P | Polarity | -1 to 1 |
| D | Dimensionality | 1-7 |
| A | Adjacency | 0-1 |
| H | Horizon | Categorical |
| Q | Quality | 0-1 |
| R | Relevance | 0-1 |
| T | Time/Throughput | Variable |

---

## 🔢 Quick Reference Cheat Sheet

**Essential Formulas for Performance Analysis:**

1. **Average Latency:** `μ = Σx / n`
2. **Hybrid Score:** `S_hybrid = α*S_cosine + (1-α)*R_stat7`
3. **Quality Improvement:** `Δ = μ_hybrid - μ_semantic`
4. **Throughput:** `TPS = N_docs / T_generation`
5. **Server Grade:** `Grade = f(t_latency)`
6. **Cache Hit Rate:** `HR = hits / (hits + misses)`
7. **System Health:** `H = 0.3*H_latency + 0.3*H_throughput + 0.2*H_quality + 0.2*H_stability`

**Key Thresholds:**
- Latency < 50ms = A+ Grade
- Overhead < 10% = Acceptable
- Quality Δ > -0.25 = Maintained
- Health Score > 0.7 = Good
- Cache Hit Rate > 0.8 = Excellent

---

*This reference provides the mathematical foundation for all performance calculations used in the STAT7-RAG stress testing system. All formulas are implemented in the rapid_fire_stress_runner.py with appropriate statistical safeguards and edge case handling.*
