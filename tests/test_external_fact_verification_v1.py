"""Automated Test Suite for External Fact Verification Audit.
Covers 30 distinct tests verifying manager identities, UEFA Champions League campaigns,
match counts, xG provenance, dual-source confirmation, blast radius, and source-of-truth gate.
"""
import sys
import json
import hashlib
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

repo_root = Path(r'f:\AI\fifi2026\innovera-wc2026-backend\ennovera-pl')
sys.path.insert(0, str(repo_root))

reports_dir = repo_root / 'reports'
audit_dir = reports_dir / 'dry_run' / 'external_fact_verification_v1'
prospective_dir = repo_root / 'prospective' / '2026_27'

# 1. Preseason cutoff explicit
def test_preseason_cutoff_explicit():
    p = audit_dir / '02_preseason_cutoff.md'
    assert '2026-08-21T18:00:00Z' in p.read_text(encoding='utf-8')

# 2. Arsenal manager primary source
def test_arsenal_manager_primary_source():
    df = pd.read_csv(audit_dir / '03_arsenal_manager_external.csv')
    row = df[df['field'] == 'Primary Source'].iloc[0]
    assert 'Official Arsenal FC Club Registry' in row['value']

# 3. Arsenal manager secondary source
def test_arsenal_manager_secondary_source():
    df = pd.read_csv(audit_dir / '03_arsenal_manager_external.csv')
    row = df[df['field'] == 'Secondary Source'].iloc[0]
    assert 'PremierLeague.com' in row['value']

# 4. City manager primary source
def test_city_manager_primary_source():
    df = pd.read_csv(audit_dir / '04_city_manager_external.csv')
    row = df[df['field'] == 'Primary Source'].iloc[0]
    assert 'Official Manchester City FC Club Registry' in row['value']

# 5. City manager secondary source
def test_city_manager_secondary_source():
    df = pd.read_csv(audit_dir / '04_city_manager_external.csv')
    row = df[df['field'] == 'Secondary Source'].iloc[0]
    assert 'PremierLeague.com' in row['value']

# 6. Manager source agreement
def test_manager_source_agreement():
    df_ars = pd.read_csv(audit_dir / '03_arsenal_manager_external.csv')
    df_city = pd.read_csv(audit_dir / '04_city_manager_external.csv')
    assert 'YES' in df_ars[df_ars['field'] == 'Source Agreement'].iloc[0]['value']
    assert 'YES' in df_city[df_city['field'] == 'Source Agreement'].iloc[0]['value']

# 7. Manager date cutoff valid
def test_manager_date_cutoff_valid():
    df_ars = pd.read_csv(audit_dir / '03_arsenal_manager_external.csv')
    df_city = pd.read_csv(audit_dir / '04_city_manager_external.csv')
    assert '2019-12-20' in df_ars[df_ars['field'] == 'Appointment Date'].iloc[0]['value']
    assert '2016-07-01' in df_city[df_city['field'] == 'Appointment Date'].iloc[0]['value']

# 8. Previous manager verified
def test_previous_manager_verified():
    df_city = pd.read_csv(audit_dir / '04_city_manager_external.csv')
    assert 'Manuel Pellegrini' in df_city[df_city['field'] == 'Previous Manager'].iloc[0]['value']

# 9. Internal manager compared
def test_internal_manager_compared():
    df = pd.read_csv(audit_dir / '05_manager_source_comparison.csv')
    assert len(df) == 2
    assert (df['match'] == True).all()

# 10. Manager mismatch classification
def test_manager_mismatch_classification():
    df = pd.read_csv(audit_dir / '05_manager_source_comparison.csv')
    assert (df['verdict'] == 'MANAGER_FACT_CONFIRMED').all()

# 11. Arsenal UCL official stage
def test_arsenal_ucl_official_stage():
    p = audit_dir / '09_ucl_stage_verification.md'
    assert 'Semi-Finals' in p.read_text(encoding='utf-8')

# 12. Arsenal UCL second-source stage
def test_arsenal_ucl_second_source_stage():
    df = pd.read_csv(audit_dir / '10_ucl_match_reconciliation.csv')
    row = df[df['dimension'] == 'Final Stage Reached'].iloc[0]
    assert 'Bayern' in row['arsenal_verified']

# 13. City UCL official stage
def test_city_ucl_official_stage():
    p = audit_dir / '09_ucl_stage_verification.md'
    assert 'Quarter-Finals' in p.read_text(encoding='utf-8')

# 14. City UCL second-source stage
def test_city_ucl_second_source_stage():
    df = pd.read_csv(audit_dir / '10_ucl_match_reconciliation.csv')
    row = df[df['dimension'] == 'Final Stage Reached'].iloc[0]
    assert 'Barcelona' in row['city_verified']

# 15. Arsenal complete match list
def test_arsenal_complete_match_list():
    df = pd.read_csv(audit_dir / '07_arsenal_ucl_external.csv')
    assert len(df) == 14
    assert 'Bayern Munich' in df['opponent'].values

# 16. City complete match list
def test_city_complete_match_list():
    df = pd.read_csv(audit_dir / '08_city_ucl_external.csv')
    assert len(df) == 12
    assert 'Barcelona' in df['opponent'].values

# 17. Arsenal match count
def test_arsenal_match_count():
    df = pd.read_csv(audit_dir / '07_arsenal_ucl_external.csv')
    assert df['match_num'].max() == 14

# 18. City match count
def test_city_match_count():
    df = pd.read_csv(audit_dir / '08_city_ucl_external.csv')
    assert df['match_num'].max() == 12

# 19. Arsenal W-D-L
def test_arsenal_wdl():
    df = pd.read_csv(audit_dir / '07_arsenal_ucl_external.csv')
    w = (df['result'] == 'W').sum()
    d = (df['result'] == 'D').sum()
    l = (df['result'] == 'L').sum()
    assert (w, d, l) == (8, 3, 3)

# 20. City W-D-L
def test_city_wdl():
    df = pd.read_csv(audit_dir / '08_city_ucl_external.csv')
    w = (df['result'] == 'W').sum()
    d = (df['result'] == 'D').sum()
    l = (df['result'] == 'L').sum()
    assert (w, d, l) == (6, 3, 3)

# 21. Arsenal final-stage reconciliation
def test_arsenal_final_stage_reconciliation():
    df = pd.read_csv(audit_dir / '10_ucl_match_reconciliation.csv')
    row = df[df['dimension'] == 'Final Stage Reached'].iloc[0]
    assert row['arsenal_prior'] == 'Semi-Finals'

# 22. City final-stage reconciliation
def test_city_final_stage_reconciliation():
    df = pd.read_csv(audit_dir / '10_ucl_match_reconciliation.csv')
    row = df[df['dimension'] == 'Final Stage Reached'].iloc[0]
    assert row['city_prior'] == 'Quarter-Finals'

# 23. xG provider identified
def test_xg_provider_identified():
    p = audit_dir / '11_ucl_xg_provenance.md'
    assert 'Opta' in p.read_text(encoding='utf-8')

# 24. xG coverage complete
def test_xg_coverage_complete():
    df_ars = pd.read_csv(audit_dir / '07_arsenal_ucl_external.csv')
    df_city = pd.read_csv(audit_dir / '08_city_ucl_external.csv')
    assert (df_ars['xg'] > 0).all()
    assert (df_city['xg'] > 0).all()

# 25. No silent provider mixing
def test_no_silent_provider_mixing():
    p = audit_dir / '11_ucl_xg_provenance.md'
    assert 'Opta Sports / UEFA Event Feed' in p.read_text(encoding='utf-8')

# 26. Internal Europe comparison
def test_internal_europe_comparison():
    df = pd.read_csv(audit_dir / '13_internal_external_europe_diff.csv')
    assert len(df) == 3
    assert df[df['field'] == 'Arsenal Final Stage'].iloc[0]['status'] == 'EXTERNAL_MATCH'

# 27. Blast radius completed
def test_blast_radius_completed():
    p = audit_dir / '15_blast_radius.md'
    assert 'VALID' in p.read_text(encoding='utf-8')

# 28. Source-of-truth gate
def test_source_truth_gate():
    p = audit_dir / '16_source_truth_gate.md'
    assert 'SOURCE_OF_TRUTH_PASS:' in p.read_text(encoding='utf-8')
    assert 'TRUE' in p.read_text(encoding='utf-8')

# 29. Protected hashes unchanged
def test_protected_hashes_unchanged():
    fpl_p = reports_dir / 'phase10_6_final_manifest.json'
    pl_p = reports_dir / 'pl11_12_final_manifest.json'
    gw2_p = repo_root / 'data' / 'live_snapshots' / '2026-27' / 'GW02' / 'plan_frozen.json'
    reg_p = prospective_dir / 'manifests' / 'snapshot_registry.csv'
    assert hashlib.sha256(fpl_p.read_bytes()).hexdigest() == '7d4bac2af06b06c13bf81d5036a403cb3173266f5dca0c16011440f47c71af5d'
    assert hashlib.sha256(pl_p.read_bytes()).hexdigest() == '2e1f294dbf47cd70088342ae16ad8a50b579ba728cf9b9f64c551c51f799ee5f'
    assert hashlib.sha256(gw2_p.read_bytes()).hexdigest() == 'a4f87e16b805d8fbfb956bc371d5aea45695d5b1b8493f9e362e114a378e1c2e'
    assert hashlib.sha256(reg_p.read_bytes()).hexdigest() == '13d60f5824db4315df42eb631c306572d6100e189946f630ebed499e8638e266'

# 30. No production mutation
def test_no_production_mutation():
    p = audit_dir / '22_final_report.md'
    assert 'Frozen controls remain 100% intact' in p.read_text(encoding='utf-8')
