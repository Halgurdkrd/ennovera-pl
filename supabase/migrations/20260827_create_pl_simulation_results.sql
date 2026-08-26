-- ============================================================
-- Migration: 20260827_create_pl_simulation_results.sql
-- Description: Store Premier League 10,000 Monte Carlo simulation runs
--              (Champion%, Top-4%, Top-6%, Relegation%, Expected Points).
-- Author: Antigravity
-- Date: 2026-08-27
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS pl_simulation_results (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competition             VARCHAR(50) NOT NULL DEFAULT 'PL2026-27',
    season                  VARCHAR(20) NOT NULL DEFAULT '2026-27',
    gameweek                INTEGER NOT NULL CHECK (gameweek >= 1 AND gameweek <= 38),
    
    team_name               VARCHAR(100) NOT NULL, -- Canonical team name e.g. 'Arsenal'
    
    champion_probability    NUMERIC(6, 4) NOT NULL CHECK (champion_probability >= 0.0 AND champion_probability <= 1.0),
    top4_probability        NUMERIC(6, 4) NOT NULL CHECK (top4_probability >= 0.0 AND top4_probability <= 1.0),
    top6_probability        NUMERIC(6, 4) NOT NULL CHECK (top6_probability >= 0.0 AND top6_probability <= 1.0),
    relegation_probability  NUMERIC(6, 4) NOT NULL CHECK (relegation_probability >= 0.0 AND relegation_probability <= 1.0),
    
    expected_points         NUMERIC(5, 2) NOT NULL,
    expected_position       NUMERIC(4, 2) NOT NULL,
    
    simulation_runs         INTEGER NOT NULL DEFAULT 10000,
    production_model_version VARCHAR(50) NOT NULL DEFAULT 'ennovera-pl-v1.0',
    simulation_version      VARCHAR(50) NOT NULL DEFAULT 'mc_10k_v1.0',
    
    generated_at            TIMESTAMP WITH TIME ZONE NOT NULL,
    data_cutoff             TIMESTAMP WITH TIME ZONE NOT NULL,
    is_latest               BOOLEAN NOT NULL DEFAULT TRUE,
    
    created_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Uniqueness: One team entry per simulation run snapshot
    CONSTRAINT uq_pl_sim_team_snapshot UNIQUE (season, gameweek, team_name, generated_at)
);

-- Query pattern indexes
CREATE INDEX IF NOT EXISTS idx_pl_sim_latest ON pl_simulation_results (season, is_latest, champion_probability DESC);
CREATE INDEX IF NOT EXISTS idx_pl_sim_gw_team ON pl_simulation_results (season, gameweek, team_name);
CREATE INDEX IF NOT EXISTS idx_pl_sim_gen_time ON pl_simulation_results (generated_at DESC);

-- Enable RLS
ALTER TABLE pl_simulation_results ENABLE ROW LEVEL SECURITY;

-- Public read access for league table display
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'pl_simulation_results' AND policyname = 'Public Read Access for Simulation Results'
    ) THEN
        CREATE POLICY "Public Read Access for Simulation Results"
            ON pl_simulation_results
            FOR SELECT
            TO anon, authenticated
            USING (true);
    END IF;
END $$;

-- Write access restricted to service_role (pipeline worker)
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'pl_simulation_results' AND policyname = 'Service Role Write Access for Simulation Results'
    ) THEN
        CREATE POLICY "Service Role Write Access for Simulation Results"
            ON pl_simulation_results
            FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;
