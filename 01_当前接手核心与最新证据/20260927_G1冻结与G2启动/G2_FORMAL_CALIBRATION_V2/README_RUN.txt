G2_FORMAL_CALIBRATION_V2
Generated 2026-09-27 from real AutoDL source/evidence snapshots.

Current state before execution:
- G0 = PASS_FROZEN
- G1 = PASS_FROZEN
- G2 scientific Stage-A = NOT RUN
- G9 holdout = untouched
- MineSim repo HEAD = 112d2bd0f3412fc83b13d5587d2b41402d2d0f5e
- tracked repo remains clean; historical untracked `?? ^C` must not be touched

This V2 closes the V1 blockers:
1. exact-tick V2V + V2R consolidated transition
2. production semantic-map loader binding for D_drivable
3. deadlock tree/reward/action/root/task integration
4. frozen G1 reward/value contract; no time/wait on deadlock terminal transition
5. 400/380/20 ms planning-deadline / no-late-execution contract
6. Budget=[4,8,16,32,64], Horizon=[4,8,16], including B64-H8 anchor
7. per-decision paired RNG across budgets at fixed horizon
8. resume-safe atomic cells and explicit calibration-development role

D_drivable provenance:
- The original G1 stage script G1_V2R_DRIVABLE_DOMAIN_V1_FAST.py is no longer present on AutoDL.
- Therefore V2 does NOT pretend to reproduce that script byte-for-byte.
- LOW prepare reconstructs D_drivable through the byte-bound production MineSim semantic-map loader from the exact frozen map bytes.
- It requires exactly the four frozen layers road/intersection/loading_area/unloading_area, 178 linked polygon records, valid MultiPolygon union with 29 components, exact map SHA, exact production loader SHA, and route endpoint coverage for the real A/B providers.
- The historical G1 token-set SHA remains recorded. If its unknown old serialization is not re-derived, this is reported explicitly rather than silently claimed as PASS.

G2-A scope:
- current Retry2 4 C11 roots only
- ROLE=G2_CALIBRATION_DEVELOPMENT
- G9_HOLDOUT_ELIGIBLE=false
- Stage-A is a coarse screen, NOT G2 final freeze and NOT cross-scene generalization
- G2-B later tests only shortlisted frontier/anchor settings on C04/C06/C11 without re-tuning

Run LOW prepare first (do not start HIGH-CPU before PASS):
  cd /root/MineSim-Dynamic
  source /root/miniconda3/etc/profile.d/conda.sh 2>/dev/null || true
  conda activate minesim
  export PYTHONPATH=/root/MineSim-Dynamic
  export PYTHONDONTWRITEBYTECODE=1
  export CUDA_VISIBLE_DEVICES=""
  cd /root/autodl-tmp
  python G2_FORMAL_CALIBRATION_V2/g2_formal_v2.py prepare 2>&1 | tee G2_FORMAL_CALIBRATION_V2_PREPARE.log

Only if LOW prepare prints PASS:G2_FORMAL_CALIBRATION_V2_PREPARE may Stage-A be started.
Stage-A additionally requires G2_HIGH_CPU_AUTHORIZED=YES.
