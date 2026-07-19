#!/usr/bin/env python3
"""
build_db.py — Compiles processed CSV datasets from the vault into a single
unified daily-level sessions_db.json database for the Dashboard v2.

This handles both NQ/MNQ and ES/MES.
"""

import os
import csv
import json

# Setup paths
VAULT_PROCESSED_DIR = "/Users/shawnjudge/Library/Mobile Documents/iCloud~md~obsidian/Documents/DVTAI Trading Labs/04 - reporting-dashboards/probability-dashboard/v1/data/processed"
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DATA_DIR = os.path.join(os.path.dirname(SCRIPTS_DIR), "data")

def clean_float(val):
    if not val or val.strip() == "":
        return None
    try:
        return round(float(val), 4)
    except ValueError:
        return val

def clean_int(val):
    if not val or val.strip() == "":
        return None
    try:
        return int(float(val))
    except ValueError:
        return val

def load_csv_data(filepath, date_col="date"):
    if not os.path.exists(filepath):
        print(f"Warning: File not found {filepath}")
        return {}
    
    data_by_date = {}
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row.get(date_col)
            if date:
                data_by_date[date] = row
    return data_by_date

def build_instrument_db(inst):
    print(f"Processing data for {inst}...")
    
    # Load files
    ohlc_file = os.path.join(VAULT_PROCESSED_DIR, f"{inst}_daily_ohlc.csv")
    or_ib_file = os.path.join(VAULT_PROCESSED_DIR, f"{inst}_daily_or_ib.csv")
    aln_file = os.path.join(VAULT_PROCESSED_DIR, f"{inst}_daily_aln.csv")
    gaps_file = os.path.join(VAULT_PROCESSED_DIR, f"{inst}_daily_gaps.csv")
    
    ohlc_data = load_csv_data(ohlc_file)
    or_ib_data = load_csv_data(or_ib_file)
    aln_data = load_csv_data(aln_file)
    gaps_data = load_csv_data(gaps_file)
    
    # Get all unique dates across datasets, sorted chronologically
    all_dates = sorted(list(set(
        list(ohlc_data.keys()) + 
        list(or_ib_data.keys()) + 
        list(aln_data.keys()) + 
        list(gaps_data.keys())
    )))
    
    print(f"Found {len(all_dates)} total session dates for {inst}.")
    
    sessions = []
    
    for dt in all_dates:
        row_ohlc = ohlc_data.get(dt, {})
        row_or_ib = or_ib_data.get(dt, {})
        row_aln = aln_data.get(dt, {})
        row_gaps = gaps_data.get(dt, {})
        
        # 1. Base Info
        session = {
          "date": dt,
          "instrument": inst,
          "day_of_week": row_ohlc.get("day_of_week") or row_aln.get("day_of_week") or row_gaps.get("day_of_week") or ""
        }
        
        # Determine day of week if blank
        if not session["day_of_week"] and row_or_ib:
            session["day_of_week"] = row_or_ib.get("day_of_week") or ""
            
        # 2. OHLC Data
        if row_ohlc:
            session["ohlc"] = {
              "o": clean_float(row_ohlc.get("open")),
              "h": clean_float(row_ohlc.get("high")),
              "l": clean_float(row_ohlc.get("low")),
              "c": clean_float(row_ohlc.get("close")),
              "volume": clean_int(row_ohlc.get("volume")),
              "volume_ma": clean_float(row_ohlc.get("volume_ma")),
              "above_vol_ma": clean_int(row_ohlc.get("above_vol_ma")),
              "range": clean_float(row_ohlc.get("daily_range")),
              "chg": clean_float(row_ohlc.get("daily_change")),
              "chg_pct": clean_float(row_ohlc.get("daily_change_pct"))
            }
        else:
            session["ohlc"] = None

        # 3. ALN Session Data
        if row_aln:
            session["aln"] = {
              "pattern": row_aln.get("pattern"),
              "asia_range": clean_float(row_aln.get("asia_range")),
              "london_range": clean_float(row_aln.get("london_range")),
              "ovn_range": clean_float(row_aln.get("ovn_range")),
              "ny_broke_london_h": clean_int(row_aln.get("ny_broke_london_h")),
              "ny_broke_london_l": clean_int(row_aln.get("ny_broke_london_l")),
              "ny_broke_london_both": clean_int(row_aln.get("ny_broke_london_both")),
              "ny_first_break": row_aln.get("ny_first_break"),
              "ny_london_h_break_time": row_aln.get("ny_london_h_break_time_0930") or row_aln.get("ny_london_h_break_time_0800") or "",
              "ny_london_l_break_time": row_aln.get("ny_london_l_break_time_0930") or row_aln.get("ny_london_l_break_time_0800") or "",
              "ny_broke_asia_h": clean_int(row_aln.get("ny_broke_asia_h")),
              "ny_broke_asia_l": clean_int(row_aln.get("ny_broke_asia_l")),
              "ny_broke_asia_both": clean_int(row_aln.get("ny_broke_asia_both")),
              "ny_first_break_asia": row_aln.get("ny_first_break_asia"),
              "ny_asia_h_break_time": row_aln.get("ny_asia_h_break_time_0930") or row_aln.get("ny_asia_h_break_time_0800") or "",
              "ny_asia_l_break_time": row_aln.get("ny_asia_l_break_time_0930") or row_aln.get("ny_asia_l_break_time_0800") or ""
            }
        else:
            session["aln"] = None

        # 4. Gap Data
        if row_gaps:
            session["gap"] = {
              "rth_open": clean_float(row_gaps.get("rth_open")),
              "prev_rth_close": clean_float(row_gaps.get("prev_rth_close")),
              "size": clean_float(row_gaps.get("gap_pts")),
              "pct": clean_float(row_gaps.get("gap_pct")),
              "direction": row_gaps.get("gap_dir"),
              "fill_25": clean_int(row_gaps.get("gap_fill_25")),
              "fill_50": clean_int(row_gaps.get("gap_fill_50")),
              "fill_75": clean_int(row_gaps.get("gap_fill_75")),
              "fill_100": clean_int(row_gaps.get("gap_fill_100")),
              "fill_25_time": row_gaps.get("gap_fill_25_time") or "",
              "fill_50_time": row_gaps.get("gap_fill_50_time") or "",
              "fill_75_time": row_gaps.get("gap_fill_75_time") or "",
              "fill_100_time": row_gaps.get("gap_fill_100_time") or ""
            }
        else:
            session["gap"] = None

        # 5. OR & IB Data
        if row_or_ib:
            session["or_ib"] = {
              "or_high": clean_float(row_or_ib.get("or_high")),
              "or_low": clean_float(row_or_ib.get("or_low")),
              "or_mid": clean_float(row_or_ib.get("or_mid")),
              "or_range": clean_float(row_or_ib.get("or_range")),
              "or_break_time": row_or_ib.get("or_break_time") or row_or_ib.get("or_break_hhmm") or "",
              
              "or_tf1_high": clean_float(row_or_ib.get("or_tf1_high")),
              "or_tf1_low": clean_float(row_or_ib.get("or_tf1_low")),
              "or_tf1_range": clean_float(row_or_ib.get("or_tf1_range")),
              "or_tf1_break_time": row_or_ib.get("or_tf1_break_hhmm") or "",
              
              "or_tf2_high": clean_float(row_or_ib.get("or_tf2_high")),
              "or_tf2_low": clean_float(row_or_ib.get("or_tf2_low")),
              "or_tf2_range": clean_float(row_or_ib.get("or_tf2_range")),
              "or_tf2_break_time": row_or_ib.get("or_tf2_break_hhmm") or "",
              
              "or_tf3_high": clean_float(row_or_ib.get("or_tf3_high")),
              "or_tf3_low": clean_float(row_or_ib.get("or_tf3_low")),
              "or_tf3_range": clean_float(row_or_ib.get("or_tf3_range")),
              "or_tf3_break_time": row_or_ib.get("or_tf3_break_hhmm") or "",
              
              "or_volume": clean_int(row_or_ib.get("or_volume")),
              
              "ib_high": clean_float(row_or_ib.get("ib_high")),
              "ib_low": clean_float(row_or_ib.get("ib_low")),
              "ib_mid": clean_float(row_or_ib.get("ib_mid")),
              "ib_range": clean_float(row_or_ib.get("ib_range")),
              "ib_break_time": row_or_ib.get("ib_break_time") or row_or_ib.get("ib_break_hhmm") or "",
              "ib_break_dir": row_or_ib.get("ib_break_dir"),
              "ib_close_half": row_or_ib.get("ib_close_half"),
              "ib_volume": clean_int(row_or_ib.get("ib_volume")),
              
              "ib_ext_up25_break": row_or_ib.get("ib_ext_up25_break") or "",
              "ib_ext_up50_break": row_or_ib.get("ib_ext_up50_break") or "",
              "ib_ext_up75_break": row_or_ib.get("ib_ext_up75_break") or "",
              "ib_ext_up100_break": row_or_ib.get("ib_ext_up100_break") or "",
              "ib_ext_dn25_break": row_or_ib.get("ib_ext_dn25_break") or "",
              "ib_ext_dn50_break": row_or_ib.get("ib_ext_dn50_break") or "",
              "ib_ext_dn75_break": row_or_ib.get("ib_ext_dn75_break") or "",
              "ib_ext_dn100_break": row_or_ib.get("ib_ext_dn100_break") or "",
              
              "ib_max_ext_up": clean_int(row_or_ib.get("ib_max_ext_up")),
              "ib_max_ext_dn": clean_int(row_or_ib.get("ib_max_ext_dn")),
              
              "ladder_rotation_count": clean_int(row_or_ib.get("Ladder Rotation Count")),
              "up_rotations": clean_int(row_or_ib.get("Up Ladder Rotations")),
              "down_rotations": clean_int(row_or_ib.get("Down Ladder Rotations")),
              "first_up_time": row_or_ib.get("First Up Ladder Time (HHMM)") or "",
              "first_down_time": row_or_ib.get("First Down Ladder Time (HHMM)") or ""
            }
        else:
            session["or_ib"] = None

        # 6. Pivot Data
        if row_or_ib:
            session["pivots"] = {
              "d_piv": clean_float(row_or_ib.get("D-Piv")),
              "d_r1": clean_float(row_or_ib.get("D-R1")),
              "d_s1": clean_float(row_or_ib.get("D-S1")),
              "d_r2": clean_float(row_or_ib.get("D-R2")),
              "d_s2": clean_float(row_or_ib.get("D-S2")),
              
              "w_piv": clean_float(row_or_ib.get("W-Piv")),
              "w_r1": clean_float(row_or_ib.get("W-R1")),
              "w_s1": clean_float(row_or_ib.get("W-S1")),
              "w_r2": clean_float(row_or_ib.get("W-R2")),
              "w_s2": clean_float(row_or_ib.get("W-S2")),
              
              "m_piv": clean_float(row_or_ib.get("M-Piv")),
              "m_r1": clean_float(row_or_ib.get("M-R1")),
              "m_s1": clean_float(row_or_ib.get("M-S1")),
              "m_r2": clean_float(row_or_ib.get("M-R2")),
              "m_s2": clean_float(row_or_ib.get("M-S2"))
            }
        else:
            session["pivots"] = None
            
        sessions.append(session)
        
    return sessions

def main():
    os.makedirs(REPO_DATA_DIR, exist_ok=True)
    
    # Process both NQ/MNQ and ES/MES
    mnq_sessions = build_instrument_db("MNQ")
    mes_sessions = build_instrument_db("MES")
    
    # Combine into a single database dict keyed by instrument
    db = {
      "MNQ": mnq_sessions,
      "MES": mes_sessions
    }
    
    output_file = os.path.join(REPO_DATA_DIR, "sessions_db.json")
    with open(output_file, mode="w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)
        
    print(f"Success! Unified database written to {output_file}")

if __name__ == "__main__":
    main()
