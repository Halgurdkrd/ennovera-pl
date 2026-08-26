"""V4 Master Experiment Pipeline Runner.
Executes the entire end-to-end V4 Dynamic Team State research pipeline:
1. Error Diagnostic of V3 Holdout (Phase 1)
2. Squad Transition Index Extraction (Phase 5)
3. Dynamic Team State with Exponential Decay & Uncertainty (Phases 2, 3, 4, 6)
4. Full Walk-Forward Evaluation & Strong-Picks Analysis (Phases 7, 8, 9, 10, 11, 18, 19, 20, 21)
5. Vectorized Season Simulation & Case Studies (Phases 15, 16, 17)

Run from ennovera-pl/ directory:
python scripts/run_v4_full_pipeline.py
"""
import os
import sys
import time
import subprocess

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)

SCRIPTS = [
    ("Step 1: V3 Error Diagnostic", "scripts/v4_error_diagnostic.py"),
    ("Step 2: Squad Transition Extractor", "scripts/v4_transition_features.py"),
    ("Step 3: Dynamic Team State Engine", "scripts/v4_dynamic_team_state.py"),
    ("Step 4: Walk-Forward Score Model & Strong Picks", "scripts/v4_walkforward_eval.py"),
    ("Step 5: Season Simulation & Diagnostics", "scripts/v4_season_simulation.py"),
]

def main():
    print("=" * 80)
    print("STARTING COMPLETE V4 DYNAMIC TEAM STATE EXPERIMENTAL PIPELINE")
    print("=" * 80)
    t0 = time.time()
    
    for step_name, script_rel in SCRIPTS:
        script_path = os.path.join(_ROOT, script_rel)
        print(f"\n>>> Running {step_name} ({script_rel})...")
        step_t0 = time.time()
        
        res = subprocess.run([sys.executable, script_path], cwd=_ROOT, capture_output=True, text=True)
        
        if res.returncode != 0:
            print(f"FAILED: {step_name}")
            print("STDOUT:\n", res.stdout)
            print("STDERR:\n", res.stderr)
            sys.exit(1)
        else:
            print(f"COMPLETED in {time.time() - step_t0:.2f}s")
            lines = [line for line in res.stdout.strip().split("\n") if line]
            for line in lines[-5:]:
                print("  ", line)
                
    total_time = time.time() - t0
    print("\n" + "=" * 80)
    print(f"ALL V4 PHASES COMPLETED SUCCESSFULLY IN {total_time:.2f}s")
    print("=" * 80)

if __name__ == "__main__":
    main()

