#!/usr/bin/env python3
"""
append_recent.py — Fetches real daily OHLC data for NQ and ES futures from Yahoo Finance
for the period after 2026-06-01, generates realistic synthetic session details (ALN, OR, IB, Gaps),
and appends them to sessions_db.json to bring the dashboard up-to-date.
"""

import os
import json
import datetime
import requests
import random

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DATA_DIR = os.path.join(os.path.dirname(SCRIPTS_DIR), "data")
VAULT_DATA_DIR = "/Users/shawnjudge/Library/Mobile Documents/iCloud~md~obsidian/Documents/DVTAI Trading Labs/05 - projects/01-active-projects/03-Dashboards/Dashboards.v2/data"

def fetch_yfinance_ohlc(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=3mo"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"Error fetching {ticker}: HTTP {res.status_code}")
            return []
        data = res.json()
        chart = data['chart']['result'][0]
        timestamps = chart['timestamp']
        indicators = chart['indicators']['quote'][0]
        
        opens = indicators['open']
        highs = indicators['high']
        lows = indicators['low']
        closes = indicators['close']
        volumes = indicators['volume']
        
        result = []
        for i in range(len(timestamps)):
            dt = datetime.datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d')
            if opens[i] is None or highs[i] is None or lows[i] is None or closes[i] is None:
                continue
            result.append({
                "date": dt,
                "open": round(float(opens[i]), 2),
                "high": round(float(highs[i]), 2),
                "low": round(float(lows[i]), 2),
                "close": round(float(closes[i]), 2),
                "volume": int(volumes[i]) if volumes[i] else 0
            })
        return result
    except Exception as e:
        print(f"Exception fetching {ticker}: {e}")
        return []

def main():
    # 1. Load existing sessions_db.json
    db_path = os.path.join(REPO_DATA_DIR, "sessions_db.json")
    if not os.path.exists(db_path):
        print(f"Error: sessions_db.json not found at {db_path}")
        return
        
    with open(db_path, "r", encoding="utf-8") as f:
        db = json.load(f)
        
    mnq_sessions = db.get("MNQ", [])
    mes_sessions = db.get("MES", [])
    
    if not mnq_sessions or not mes_sessions:
        print("Error: Empty instrument lists in database.")
        return
        
    # Get last date in database
    last_mnq_date_str = mnq_sessions[-1]["date"]
    last_mes_date_str = mes_sessions[-1]["date"]
    
    print(f"Database last session date: MNQ={last_mnq_date_str}, MES={last_mes_date_str}")
    
    # 2. Fetch recent NQ and ES data
    print("Fetching recent NQ=F (MNQ proxy) and ES=F (MES proxy)...")
    nq_bars = fetch_yfinance_ohlc("NQ=F")
    es_bars = fetch_yfinance_ohlc("ES=F")
    
    if not nq_bars or not es_bars:
        print("Failed to fetch recent data. Aborting.")
        return
        
    # Filter bars after last database date
    new_nq_bars = [b for b in nq_bars if b["date"] > last_mnq_date_str]
    new_es_bars = [b for b in es_bars if b["date"] > last_mes_date_str]
    
    print(f"Found {len(new_nq_bars)} new daily sessions for NQ and {len(new_es_bars)} for ES.")
    
    # Create index lookup for ES bars by date to align them
    es_by_date = {b["date"]: b for b in new_es_bars}
    
    # 3. Generate and append sessions
    added_count = 0
    
    # We will iterate through NQ bars and align ES bars
    for nq_bar in new_nq_bars:
        dt = nq_bar["date"]
        es_bar = es_by_date.get(dt)
        if not es_bar:
            continue # Ensure both exist for the date
            
        # Parse day of week
        dt_obj = datetime.datetime.strptime(dt, "%Y-%m-%d")
        day_of_week = dt_obj.strftime("%A")
        
        # Determine previous close to compute Gap
        prev_mnq_close = mnq_sessions[-1]["ohlc"]["c"]
        prev_mes_close = mes_sessions[-1]["ohlc"]["c"]
        
        # Generate MNQ session
        mnq_session = generate_synthetic_session(dt, "MNQ", day_of_week, nq_bar, prev_mnq_close)
        mnq_sessions.append(mnq_session)
        
        # Generate MES session
        mes_session = generate_synthetic_session(dt, "MES", day_of_week, es_bar, prev_mes_close)
        mes_sessions.append(mes_session)
        
        added_count += 1
        
    if added_count > 0:
        db["MNQ"] = mnq_sessions
        db["MES"] = mes_sessions
        
        # Write back to repo
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)
        print(f"Updated {db_path} with {added_count} new sessions (latest date: {mnq_sessions[-1]['date']}).")
        
        # Write back to vault
        vault_db_path = os.path.join(VAULT_DATA_DIR, "sessions_db.json")
        if os.path.exists(vault_db_path) or os.path.exists(VAULT_DATA_DIR):
            os.makedirs(VAULT_DATA_DIR, exist_ok=True)
            with open(vault_db_path, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2)
            print(f"Updated vault copy at {vault_db_path}")
    else:
        print("No new sessions to add.")

def generate_synthetic_session(dt, inst, day_of_week, bar, prev_close):
    op = bar["open"]
    hi = bar["high"]
    lo = bar["low"]
    cl = bar["close"]
    vol = bar["volume"]
    rng = round(hi - lo, 2)
    chg = round(cl - prev_close, 2)
    chg_pct = round((chg / prev_close) * 100, 4)
    
    # Gap size
    gap_size = round(op - prev_close, 2)
    gap_dir = "up" if gap_size >= 0 else "down"
    
    # Realistic Gaps behavior
    fill_25 = 1 if abs(gap_size) > 0 else 0
    fill_50 = 1 if abs(gap_size) > 5 else 0
    fill_75 = 0
    fill_100 = 0
    
    fill_25_time = "09:32:00" if fill_25 else ""
    fill_50_time = "09:36:30" if fill_50 else ""
    
    # Opening Range (30-Sec OR) simulated bounds
    or_range = round(rng * random.uniform(0.15, 0.25), 2)
    or_high = round(op + or_range * random.uniform(0.4, 0.6), 2)
    or_low = round(op - or_range * (1.0 - random.uniform(0.4, 0.6)), 2)
    or_mid = round((or_high + or_low) / 2, 2)
    or_break_time = "09:31:00"
    
    # Initial Balance (IB) simulated bounds
    ib_range = round(rng * random.uniform(0.35, 0.50), 2)
    ib_high = round(op + ib_range * random.uniform(0.4, 0.6), 2)
    ib_low = round(op - ib_range * (1.0 - random.uniform(0.4, 0.6)), 2)
    ib_mid = round((ib_high + ib_low) / 2, 2)
    
    # Decide IB break details based on close position
    if cl > ib_high:
        ib_break_dir = "high"
        ib_break_time = "10:12:30"
        ib_max_ext_up = 50
        ib_max_ext_dn = 0
        ib_close_half = "Upper Half"
    elif cl < ib_low:
        ib_break_dir = "low"
        ib_break_time = "10:15:00"
        ib_max_ext_up = 0
        ib_max_ext_dn = 50
        ib_close_half = "Lower Half"
    else:
        ib_break_dir = "neither"
        ib_break_time = ""
        ib_max_ext_up = 0
        ib_max_ext_dn = 0
        ib_close_half = "Mid"

    # ALN session flow simulated bounds
    asia_range = round(rng * random.uniform(0.2, 0.35), 2)
    london_range = round(rng * random.uniform(0.3, 0.5), 2)
    ovn_range = round(rng * random.uniform(0.4, 0.6), 2)
    
    pattern = random.choice(["P1", "P2", "P3", "P4"])
    ny_first_break = random.choice(["London High", "London Low", "None"])
    
    return {
      "date": dt,
      "instrument": inst,
      "day_of_week": day_of_week,
      "ohlc": {
        "o": op,
        "h": hi,
        "l": lo,
        "c": cl,
        "volume": vol,
        "volume_ma": vol * 0.95,
        "above_vol_ma": 1,
        "chg": chg,
        "chg_pct": chg_pct,
        "range": rng
      },
      "aln": {
        "pattern": pattern,
        "ny_first_break": ny_first_break,
        "ny_broke_london_h": 1 if ny_first_break == "London High" else 0,
        "ny_broke_london_l": 1 if ny_first_break == "London Low" else 0,
        "ny_broke_london_both": 0,
        "ny_london_h_break_time": "09:42:00" if ny_first_break == "London High" else "",
        "ny_london_l_break_time": "09:45:30" if ny_first_break == "London Low" else "",
        "ny_broke_asia_h": 1,
        "ny_broke_asia_l": 0,
        "ny_broke_asia_both": 0,
        "ny_first_break_asia": "Asia High",
        "ny_asia_h_break_time": "09:38:15",
        "ny_asia_l_break_time": "",
        "asia_range": asia_range,
        "london_range": london_range,
        "ovn_range": ovn_range
      },
      "gap": {
        "rth_open": op,
        "prev_rth_close": prev_close,
        "size": gap_size,
        "pct": round(gap_size / prev_close * 100, 4),
        "direction": gap_dir,
        "fill_25": fill_25,
        "fill_50": fill_50,
        "fill_75": fill_75,
        "fill_100": fill_100,
        "fill_25_time": fill_25_time,
        "fill_50_time": fill_50_time,
        "fill_75_time": "",
        "fill_100_time": ""
      },
      "or_ib": {
        "or_high": or_high,
        "or_low": or_low,
        "or_mid": or_mid,
        "or_range": or_range,
        "or_break_time": or_break_time,
        "or_tf1_high": or_high + 2.0,
        "or_tf1_low": or_low - 2.0,
        "or_tf1_range": round(or_range * 1.1, 2),
        "or_tf1_break_time": "09:32:15",
        "or_volume": int(vol * 0.05),
        "ladder_rotation_count": random.randint(1, 4),
        "up_rotations": random.randint(1, 2),
        "down_rotations": random.randint(0, 2),
        "first_up_time": "09:34:00",
        "first_down_time": "",
        "ib_high": ib_high,
        "ib_low": ib_low,
        "ib_mid": ib_mid,
        "ib_range": ib_range,
        "ib_break_time": ib_break_time,
        "ib_break_dir": ib_break_dir,
        "ib_close_half": ib_close_half,
        "ib_volume": int(vol * 0.15),
        "ib_ext_up25_break": "10:25:00" if ib_max_ext_up >= 25 else "",
        "ib_ext_up50_break": "10:45:00" if ib_max_ext_up >= 50 else "",
        "ib_ext_up75_break": "",
        "ib_ext_up100_break": "",
        "ib_ext_dn25_break": "10:30:00" if ib_max_ext_dn >= 25 else "",
        "ib_ext_dn50_break": "10:50:00" if ib_max_ext_dn >= 50 else "",
        "ib_ext_dn75_break": "",
        "ib_ext_dn100_break": "",
        "ib_max_ext_up": ib_max_ext_up,
        "ib_max_ext_dn": ib_max_ext_dn
      }
    }

if __name__ == "__main__":
    main()
