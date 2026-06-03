#!/usr/bin/env python
"""Load a ledger-schema CSV into db/variants.duckdb (idempotent) and re-export the
git-shared form db/exports/variants.csv. The DuckDB binary is the single source of
truth (git-ignored); the CSV export is what travels in git (CLAUDE.md §8).

Run (lecam): env -u PYTHONPATH PYTHONNOUSERSITE=1 LD_LIBRARY_PATH=$CONDA_PREFIX/lib \
   conda run -n lecam python scripts/_tools/ledger_load_csv.py --csv <file>
"""
import argparse
from pathlib import Path
import duckdb

REPO = Path(__file__).resolve().parents[2]
DB = REPO / "db/variants.duckdb"
SCHEMA = REPO / "db/schema.sql"
EXPORT = REPO / "db/exports/variants.csv"

COLS = ["variant_id", "parent", "track", "chain", "mutations", "n_mut",
        "edit_dist_to_wt", "status", "source_config"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    args = ap.parse_args()
    con = duckdb.connect(str(DB))
    if SCHEMA.exists():
        con.execute(SCHEMA.read_text())          # CREATE TABLE IF NOT EXISTS (whole-file)
    collist = ",".join(COLS)
    con.execute(
        f"INSERT OR REPLACE INTO variants ({collist}, created_at) "
        f"SELECT {collist}, current_timestamp FROM read_csv_auto(?, header=true)",
        [args.csv])
    n = con.execute("SELECT count(*) FROM variants").fetchone()[0]
    by_track = con.execute("SELECT track, count(*) FROM variants GROUP BY track ORDER BY track").fetchall()
    EXPORT.parent.mkdir(parents=True, exist_ok=True)
    con.execute("COPY (SELECT * FROM variants ORDER BY variant_id) TO ? (HEADER, DELIMITER ',')",
                [str(EXPORT)])
    con.close()
    print("ledger total variants:", n, "| by track:", dict(by_track))
    print("exported ->", EXPORT.relative_to(REPO))
    print("LEDGER_LOAD_DONE")


if __name__ == "__main__":
    main()
