"""V3 Master Experiment Pipeline Runner.
Executes the entire end-to-end V3 walk-forward experiment sequentially:
1. Walk-forward V2 baseline generation (out-of-time)
2. Temporal FPL feature extraction with automated leakage assertions
3. Independent signal screening on development split (2022-24) with block bootstrap CI
4. Multi-signal model selection and parameter freezing on validation split (2024-25)
5. Final holdout evaluation, diagnostics, and 10,000-run Monte Carlo simulation (2025-26)

Run from ennovera-pl/ directory:
python scripts/run_v3_full_pipeline.py
"""
import os
import sys
import time
import subprocess

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)

SCRIPTS = [
    ("Step 1: Walk-Forward V2 Baselines", "scripts/v3_walkforward_v2_baseline.py"),
    ("Step 2: Temporal FPL Feature Extraction", "scripts/v3_extract_fpl_features.py"),
    ("Step 3: Signal Screening (Dev Split 2022-24)", "scripts/v3_signal_screening.py"),
    ("Step 4: Model Selection & Freezing (Val Split 2024-25)", "scripts/v3_fit_correction_layers.py"),
    ("Step 5: Holdout Evaluation & Simulation (Holdout 2025-26)", "scripts/v3_evaluate_holdout.py"),
]

def main():
    print("=" * 80)
    print("STARTING COMPLETE V3 WALK-FORWARD EXPERIMENTAL PIPELINE")
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
            # Print last few lines of stdout
            lines = [line for line in res.stdout.strip().split("\n") if line]
            for line in lines[-6:]:
                print("  ", line)
                
    total_time = time.time() - t0
    print("\n" + "=" * 80)
    print(f"ALL 5 EXPERIMENTAL PHASES COMPLETED SUCCESSFULLY IN {total_time:.2f}s")
    print("=" * 80)

if __name__ == "__main__":
    main()
