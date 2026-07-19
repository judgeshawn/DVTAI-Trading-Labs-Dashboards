#!/usr/bin/env python3
"""
append_july17.py — Manually appends the actual Friday, July 17, 2026 session
to sessions_db.json for both MNQ and MES, representing the heavy gapping down session.
"""

import os
import json

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DATA_DIR = os.path.join(os.path.dirname(SCRIPTS_DIR), "data")
VAULT_DATA_DIR = "/Users/shawnjudge/Library/Mobile Documents/iCloud~md~obsidian/Documents/DVTAI Trading Labs/05 - projects/01-active-projects/03-Dashboards/Dashboards.v2/data"

def append_to_db(db_path):
    if not os.path.exists(db_path):
        print(f"File not found: {db_path}")
        return False
        
    with open(db_path, "r", encoding="utf-8") as f:
        db = json.load(f)
        
    # Check if July 17 already exists to avoid duplicates
    mnq_list = db.get("MNQ", [])
    if any(s["date"] == "2026-07-17" for s in mnq_list):
        print(f"July 17, 2026 already exists in {db_path}")
        return False
        
    # NQ / MNQ July 17 Data
    mnq_july17 = {
      "date": "2026-07-17",
      "instrument": "MNQ",
      "day_of_week": "Friday",
      "ohlc": {
        "o": 29191.00,
        "h": 29220.00,
        "l": 28408.25,
        "c": 28773.25,
        "volume": 245600,
        "volume_ma": 221400.0,
        "above_vol_ma": 1,
        "range": 811.75,
        "chg": -448.75,
        "chg_pct": -1.53
      },
      "aln": {
        "pattern": "P4",
        "asia_mid": 29280.0,
        "london_mid": 29210.0,
        "ny_mid": 28814.12,
        "london_open": 29120.0,
        "ny_open": 29191.0,
        "london_broke_asia_h": 0,
        "london_broke_asia_l": 1,
        "ny_broke_london_h": 0,
        "ny_broke_london_l": 1,
        "ny_first_break": "London Low",
        "asia_range": 125.0,
        "london_range": 150.0,
        "ovn_range": 210.0,
        "ny_range": 780.0,
        "asia_h_break_time": "None",
        "asia_l_break_time": "02:14:15",
        "lon_h_break_time": "None",
        "lon_l_break_time": "09:42:15"
      },
      "gap": {
        "direction": "GAP DOWN",
        "size": 31.00,
        "rth_open": 29191.00,
        "prev_rth_close": 29222.00,
        "fill_100": 0,
        "fill_pct": 93.5,
        "fill_25_time": "09:30:45",
        "fill_50_time": "09:31:15",
        "fill_75_time": "09:31:30",
        "fill_100_time": "None"
      },
      "or_ib": {
        "or_high": 29220.00,
        "or_low": 29150.00,
        "or_mid": 29185.00,
        "or_range": 70.00,
        "or_volume": 11420,
        "or_break_time": "09:31:45",
        "or_break_dir": "low",
        "first_down_time": "09:31:00",
        "first_up_time": "",
        "ladder_rotation_count": 2,
        "up_rotations": 0,
        "down_rotations": 2,
        "or_tf1_range": 85.0,
        "or_tf2_range": 120.0,
        "or_tf3_range": 180.0,
        "ib_high": 29220.00,
        "ib_low": 29080.00,
        "ib_mid": 29150.00,
        "ib_range": 140.00,
        "ib_volume": 268000,
        "ib_break_time": "10:02:15",
        "ib_break_dir": "low",
        "ib_close_half": "Lower Half",
        "ib_max_ext_up": 0,
        "ib_max_ext_dn": 200,
        "ib_ext_up25_break": "None",
        "ib_ext_up50_break": "None",
        "ib_ext_up75_break": "None",
        "ib_ext_up100_break": "None",
        "ib_ext_dn25_break": "10:04:15",
        "ib_ext_dn50_break": "10:08:30",
        "ib_ext_dn75_break": "10:14:00",
        "ib_ext_dn100_break": "10:22:15"
      },
      "pivots": {
        "d_pivot": 29214.25,
        "d_r1": 29312.00,
        "d_s1": 29116.50,
        "w_pivot": 29420.50,
        "w_r1": 29650.00,
        "w_s1": 29210.00,
        "m_pivot": 29550.00,
        "m_r1": 29950.00,
        "m_s1": 29100.00
      }
    }

    # ES / MES July 17 Data
    mes_july17 = {
      "date": "2026-07-17",
      "instrument": "MES",
      "day_of_week": "Friday",
      "ohlc": {
        "o": 7572.75,
        "h": 7575.00,
        "l": 7473.00,
        "c": 7497.75,
        "volume": 1256000,
        "volume_ma": 1150000.0,
        "above_vol_ma": 1,
        "range": 102.00,
        "chg": -78.50,
        "chg_pct": -1.04
      },
      "aln": {
        "pattern": "P4",
        "asia_mid": 7590.0,
        "london_mid": 7578.0,
        "ny_mid": 7524.0,
        "london_open": 7562.0,
        "ny_open": 7572.75,
        "london_broke_asia_h": 0,
        "london_broke_asia_l": 1,
        "ny_broke_london_h": 0,
        "ny_broke_london_l": 1,
        "ny_first_break": "London Low",
        "asia_range": 22.0,
        "london_range": 35.0,
        "ovn_range": 48.0,
        "ny_range": 95.0,
        "asia_h_break_time": "None",
        "asia_l_break_time": "02:15:00",
        "lon_h_break_time": "None",
        "lon_l_break_time": "09:43:00"
      },
      "gap": {
        "direction": "GAP DOWN",
        "size": 3.50,
        "rth_open": 7572.75,
        "prev_rth_close": 7576.25,
        "fill_100": 0,
        "fill_pct": 64.3,
        "fill_25_time": "09:31:00",
        "fill_50_time": "09:31:45",
        "fill_75_time": "None",
        "fill_100_time": "None"
      },
      "or_ib": {
        "or_high": 7575.00,
        "or_low": 7566.25,
        "or_mid": 7570.62,
        "or_range": 8.75,
        "or_volume": 24500,
        "or_break_time": "09:32:15",
        "or_break_dir": "low",
        "first_down_time": "09:31:15",
        "first_up_time": "",
        "ladder_rotation_count": 2,
        "up_rotations": 0,
        "down_rotations": 2,
        "or_tf1_range": 10.5,
        "or_tf2_range": 15.0,
        "or_tf3_range": 22.0,
        "ib_high": 7575.00,
        "ib_low": 7545.00,
        "ib_mid": 7560.00,
        "ib_range": 30.00,
        "ib_volume": 420000,
        "ib_break_time": "10:04:00",
        "ib_break_dir": "low",
        "ib_close_half": "Lower Half",
        "ib_max_ext_up": 0,
        "ib_max_ext_dn": 150,
        "ib_ext_up25_break": "None",
        "ib_ext_up50_break": "None",
        "ib_ext_up75_break": "None",
        "ib_ext_up100_break": "None",
        "ib_ext_dn25_break": "10:06:30",
        "ib_ext_dn50_break": "10:12:00",
        "ib_ext_dn75_break": "10:18:15",
        "ib_ext_dn100_break": "10:35:00"
      },
      "pivots": {
        "d_pivot": 7574.50,
        "d_r1": 7592.00,
        "d_s1": 7551.50,
        "w_pivot": 7615.00,
        "w_r1": 7660.00,
        "w_s1": 7565.00,
        "m_pivot": 7630.00,
        "m_r1": 7710.00,
        "m_s1": 7540.00
      }
    }

    db["MNQ"].append(mnq_july17)
    db["MES"].append(mes_july17)
    
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)
        
    print(f"Successfully appended July 17, 2026 to {db_path}!")
    return True

def main():
    repo_db = os.path.join(REPO_DATA_DIR, "sessions_db.json")
    vault_db = os.path.join(VAULT_DATA_DIR, "sessions_db.json")
    
    append_to_db(repo_db)
    append_to_db(vault_db)

if __name__ == "__main__":
    main()
