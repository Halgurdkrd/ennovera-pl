"""Test cross-season player continuity and price priors for GW1-5."""
import os
import pandas as pd
import numpy as np

RAW_FPL_DIR = "data/raw/fpl_full/data"
SEASONS = ["2022-23", "2023-24", "2024-25", "2025-26"]

all_gw_records = []
for season in SEASONS:
    season_dir = os.path.join(RAW_FPL_DIR, season, "gws")
    for gw in range(1, 39):
        gw_path = os.path.join(season_dir, f"gw{gw}.csv")
        if os.path.exists(gw_path):
            df_gw = pd.read_csv(gw_path, low_memory=False)
            df_gw["season"] = season
            df_gw["gw"] = gw
            df_gw["price"] = df_gw["value"] / 10.0 if "value" in df_gw.columns else 5.0
            all_gw_records.append(df_gw)

df_all = pd.concat(all_gw_records, ignore_index=True)
print(f"Total records: {len(df_all)}")

# Match players by name across seasons
df_all["clean_name"] = df_all["name"].str.strip().str.lower()
df_all = df_all.sort_values(["clean_name", "season", "gw"]).reset_index(drop=True)

# Rolling across seasons
num_cols = ["minutes", "total_points", "expected_goals", "expected_assists", "clean_sheets", "saves"]
for c in num_cols:
    if c in df_all.columns:
        df_all[c] = pd.to_numeric(df_all[c], errors="coerce").fillna(0.0)

grp = df_all.groupby("clean_name")
df_all["roll_mins_5"] = grp["minutes"].shift(1).rolling(5, min_periods=1).mean().fillna(0.0)
df_all["roll_pts_5"] = grp["total_points"].shift(1).rolling(5, min_periods=1).mean().fillna(0.0)
df_all["roll_xg_5"] = grp["expected_goals"].shift(1).rolling(5, min_periods=1).mean().fillna(0.0)
df_all["roll_xa_5"] = grp["expected_assists"].shift(1).rolling(5, min_periods=1).mean().fillna(0.0)

# Check Haaland / Salah in GW1 of 2024-25
sub = df_all[(df_all["season"] == "2024-25") & (df_all["gw"] == 1) & (df_all["clean_name"].str.contains("haaland|salah|saka", case=False))]
print(sub[["name", "team", "price", "roll_mins_5", "roll_pts_5", "roll_xg_5", "roll_xa_5"]])

