-- variant ledger (single source of truth on the coordinator).
-- The binary .duckdb is git-ignored; the git-shared form is db/exports/*.csv.
CREATE TABLE IF NOT EXISTS variants (
  variant_id        TEXT PRIMARY KEY,   -- e.g. LEC-AM-T1-0042
  parent            TEXT,               -- 'lecanemab_WT'
  track             TEXT,               -- T1 | T2 | T3 | T4
  chain             TEXT,               -- HC | LC | both
  mutations         TEXT,               -- 'HC:Y32F;LC:S56T' (IMGT numbering)
  n_mut             INTEGER,
  edit_dist_to_wt   INTEGER,
  cluster           TEXT,               -- which cluster produced/scored it
  -- Stage 5 (affinity, vs WT)
  boltz_iptm        DOUBLE,
  boltz_ipsae       DOUBLE,
  af3_iptm          DOUBLE,
  flexddg_kcal      DOUBLE,
  consensus_rank    INTEGER,
  -- Stage 6 (selectivity + developability)
  sel_monomer_delta DOUBLE,             -- Δprotofibril - Δmonomer  (want >0, >= WT)
  sel_cafib_delta   DOUBLE,             -- Δprotofibril - ΔCAA-fibril
  oasis_humanness   DOUBLE,
  agg3d_score       DOUBLE,
  netsolp           DOUBLE,
  viscosity_flag    BOOLEAN,
  tap_flags         TEXT,
  -- Stage 8 (experimental)
  kd_protofibril_M  DOUBLE,
  koff_protofibril  DOUBLE,
  monomer_screen    TEXT,               -- 'negative' (desired) | 'positive'
  -- provenance
  stage_reached     INTEGER,
  status            TEXT,               -- generated|scored|gated|rejected|tested|hit
  source_config     TEXT,
  created_at        TIMESTAMP
);
