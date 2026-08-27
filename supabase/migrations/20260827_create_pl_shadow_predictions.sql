-- ============================================================
-- Migration: 20260827_create_pl_shadow_predictions.sql
-- Description: Immutable pre-kickoff shadow prediction audit ledger
--              for prospective model evaluation (V2 vs V5.1).
-- Author: Antigravity
-- Date: 2026-08-27
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS pl_shadow_predictions (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fixture_id              TEXT NOT NULL,
    match_id                UUID REFERENCES matches(match_id) ON DELETE CASCADE,
    competition             VARCHAR(50) NOT NULL DEFAULT 'PL2026-27',
    season                  VARCHAR(20) NOT NULL DEFAULT '2026-27',
    gameweek                INTEGER NOT NULL CHECK (gameweek >= 1 AND gameweek <= 38),
    home_team               VARCHAR(100) NOT NULL,
    away_team               VARCHAR(100) NOT NULL,
    kickoff                 TIMESTAMP WITH TIME ZONE NOT NULL,
    
    model_public_version    VARCHAR(50) NOT NULL, -- e.g. 'ennovera-pl-v1.0'
    model_internal_version  VARCHAR(100) NOT NULL, -- e.g. 'pl_v2_final', 'pl_v5_1_candidate'
    model_role              VARCHAR(20) NOT NULL CHECK (model_role IN ('PRODUCTION', 'SHADOW', 'BENCHMARK')),
    
    home_probability        NUMERIC(6, 4) NOT NULL CHECK (home_probability >= 0.0 AND home_probability <= 1.0),
    draw_probability        NUMERIC(6, 4) NOT NULL CHECK (draw_probability >= 0.0 AND draw_probability <= 1.0),
    away_probability        NUMERIC(6, 4) NOT NULL CHECK (away_probability >= 0.0 AND away_probability <= 1.0),
    predicted_outcome       CHAR(1) NOT NULL CHECK (predicted_outcome IN ('H', 'D', 'A')),
    
    confidence              VARCHAR(10) NOT NULL CHECK (confidence IN ('LOW', 'MEDIUM', 'HIGH')),
    strong_pick             BOOLEAN NOT NULL DEFAULT FALSE,
    
    generated_at            TIMESTAMP WITH TIME ZONE NOT NULL,
    data_cutoff             TIMESTAMP WITH TIME ZONE NOT NULL,
    prediction_state        VARCHAR(30) NOT NULL DEFAULT 'PREMATCH' CHECK (prediction_state IN ('EARLY', 'PREMATCH', 'LINEUP_CONFIRMED', 'FINAL')),
    
    created_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Invariant: Probability sum must equal 1.0 within numerical tolerance (+/- 0.005)
    CONSTRAINT check_pl_shadow_probs_sum CHECK (
        ABS(home_probability + draw_probability + away_probability - 1.0) <= 0.005
    ),
    
    -- Uniqueness: One prediction per fixture, model version, state, and generated timestamp
    CONSTRAINT uq_pl_shadow_snapshot UNIQUE (fixture_id, model_internal_version, prediction_state, generated_at)
);

-- Query pattern indexes
CREATE INDEX IF NOT EXISTS idx_pl_shadow_lookup ON pl_shadow_predictions (season, gameweek, model_role);
CREATE INDEX IF NOT EXISTS idx_pl_shadow_fixture ON pl_shadow_predictions (fixture_id, model_internal_version);
CREATE INDEX IF NOT EXISTS idx_pl_shadow_match ON pl_shadow_predictions (match_id);
CREATE INDEX IF NOT EXISTS idx_pl_shadow_gen_time ON pl_shadow_predictions (generated_at DESC);

-- Enable RLS
ALTER TABLE pl_shadow_predictions ENABLE ROW LEVEL SECURITY;

-- Public read access for research evaluation & transparency
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'pl_shadow_predictions' AND policyname = 'Public Read Access for Shadow Predictions'
    ) THEN
        CREATE POLICY "Public Read Access for Shadow Predictions"
            ON pl_shadow_predictions
            FOR SELECT
            TO anon, authenticated
            USING (true);
    END IF;
END $$;

-- Write access restricted to service_role (pipeline worker)
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'pl_shadow_predictions' AND policyname = 'Service Role Write Access for Shadow Predictions'
    ) THEN
        CREATE POLICY "Service Role Write Access for Shadow Predictions"
            ON pl_shadow_predictions
            FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;
