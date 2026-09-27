# Paper-1 SafetyRiskEvaluator V0 Observational Freeze V1

**Status: PASS**

- Baseline: `112d2bd0f3412fc83b13d5587d2b41402d2d0f5e`
- C04 seed0 authoritative result SHA: `47e3ff50997d6ea095fce0ea0532ca9c01ace31abdc4646980f3b92b09129ca0`
- Sidecar result SHA: `47e3ff50997d6ea095fce0ea0532ca9c01ace31abdc4646980f3b92b09129ca0`
- Result byte parity: **PASS**
- Diagnostic log byte parity: **PASS**
- V0 records: **126**
- V2R route-geometry violations: **0**
- V2R direct actual-footprint violations: **0**
- Route/direct V2R boolean mismatches: **0**
- V2V internal collision transitions: **0**
- V0 route-geometry swept minimum V2V clearance: **2.038038141194 m**
- `paper1_safe_node_decision_available`: **false**
- V2H: **NOT_IMPLEMENTED_V0**

## Scientific boundary

This freezes only the **observational parity layer**. It does not approve Paper-1 `Pi_safe` pruning yet.
Before pruning, the project still needs raw/continuous safety features compatible with the paper's equations:
continuous `d_v2r`, context-aware V2V threshold inputs, and a separate V2H contract.
