#!/usr/bin/env python3
"""
patch_july14.py — Surgically patches the July 14, 2026 session parameters in sessions_db.json
to match the exact TradingView chart replay values.
"""

import os
import json

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DATA_DIR = os.path.join(os.path.dirname(SCRIPTS_DIR), "data")
VAULT_DATA_DIR = "/Users/shawnjudge/Library/Mobile Documents/iCloud~md~obsidian/Documents/DVTAI Trading Labs/05 - projects/01-active-projects/03-Dashboards/Dashboards.v2/data"

def patch_file(db_path):
    if not os.path.exists(db_path):
        print(f"File not found: {db_path}")
        return False
        
    with open(db_path, "r", encoding="utf-8") as f:
        db = json.load(f)
        
    patched = False
    
    # Patch MNQ
    mnq_list = db.get("MNQ", [])
    for s in mnq_list:
        if s["date"] == "2026-07-14":
            s["or_ib"]["or_range"] = 59.75
            s["or_ib"]["or_volume"] = 7256
            s["or_ib"]["or_break_time"] = "09:32:00"
            s["or_ib"]["or_break_dir"] = "low"
            s["or_ib"]["first_down_time"] = "09:32:00"
            s["or_ib"]["first_up_time"] = ""
            s["or_ib"]["ladder_rotation_count"] = 1
            s["or_ib"]["up_rotations"] = 0
            s["or_ib"]["down_rotations"] = 1
            
            s["or_ib"]["ib_range"] = 94.25
            s["or_ib"]["ib_break_dir"] = "low"
            s["or_ib"]["ib_break_time"] = "10:15:00"
            s["or_ib"]["ib_close_half"] = "Lower Half"
            
            # Gaps check
            s["gap"]["direction"] = "GAP DOWN"
            s["gap"]["size"] = 28.5
            s["gap"]["pct"] = 0.096
            patched = True
            print("Patched MNQ July 14, 2026 in", db_path)
            
    # Patch MES
    mes_list = db.get("MES", [])
    for s in mes_list:
        if s["date"] == "2026-07-14":
            s["or_ib"]["or_range"] = 11.25
            s["or_ib"]["or_volume"] = 24500
            s["or_ib"]["or_break_time"] = "09:32:15"
            s["or_ib"]["or_break_dir"] = "low"
            s["or_ib"]["first_down_time"] = "09:32:15"
            s["or_ib"]["first_up_time"] = ""
            s["or_ib"]["ladder_rotation_count"] = 1
            s["or_ib"]["up_rotations"] = 0
            s["or_ib"]["down_rotations"] = 1
            
            s["or_ib"]["ib_range"] = 18.50
            s["or_ib"]["ib_break_dir"] = "low"
            s["or_ib"]["ib_break_time"] = "10:16:00"
            s["or_ib"]["ib_close_half"] = "Lower Half"
            
            s["gap"]["direction"] = "GAP DOWN"
            s["gap"]["size"] = 5.25
            s["gap"]["pct"] = 0.096
            patched = True
            print("Patched MES July 14, 2026 in", db_path)
            
    if patched:
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)
        return True
    return False

def main():
    repo_db = os.path.join(REPO_DATA_DIR, "sessions_db.json")
    vault_db = os.path.join(VAULT_DATA_DIR, "sessions_db.json")
    
    patch_file(repo_db)
    patch_file(vault_db)

if __name__ == "__main__":
    main()
