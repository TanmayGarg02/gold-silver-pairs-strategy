import sys
import os
import requests
import pyotp
import logging
import csv
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# ----------------------------
# LOAD ENV VARIABLES
# ----------------------------
load_dotenv()

# ----------------------------
# LOGGING
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)

# ----------------------------
# ENDPOINTS
# ----------------------------
BASE_URL = "https://apiconnect.angelone.in"
LOGIN_URL = f"{BASE_URL}/rest/auth/angelbroking/user/v1/loginByPassword"
HIST_URL = f"{BASE_URL}/rest/secure/angelbroking/historical/v1/getCandleData"

# ----------------------------
# ACCOUNT CONFIG
# ----------------------------
@dataclass
class AngelAccountConfig:
    name: str
    clientcode: str
    pin: str
    api_key: str
    totp_secret: str
    local_ip: str = "127.0.0.1"
    public_ip: str = "127.0.0.1"
    mac: str = "00:00:00:00:00:00"
    state: str = "live"


@dataclass
class AngelAccountState:
    config: AngelAccountConfig
    jwt_token: Optional[str] = None
    refresh_token: Optional[str] = None
    feed_token: Optional[str] = None
    last_login: Optional[datetime] = None

# ----------------------------
# HEADERS
# ----------------------------
def base_headers(cfg: AngelAccountConfig, jwt_token: Optional[str] = None) -> Dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
        "X-UserType": "USER",
        "X-SourceID": "WEB",
        "X-ClientLocalIP": cfg.local_ip,
        "X-ClientPublicIP": cfg.public_ip,
        "X-MACAddress": cfg.mac,
        "X-PrivateKey": cfg.api_key,
    }
    if jwt_token:
        headers["Authorization"] = f"Bearer {jwt_token}"
    return headers

# ----------------------------
# LOGIN
# ----------------------------
def login_account(state: AngelAccountState) -> None:
    cfg = state.config
    totp = pyotp.TOTP(cfg.totp_secret).now()

    payload = {
        "clientcode": cfg.clientcode,
        "password": cfg.pin,
        "totp": totp,
        "state": cfg.state,
    }

    logging.info("Logging in to Angel One")

    r = requests.post(
        LOGIN_URL,
        json=payload,
        headers=base_headers(cfg),
        timeout=10,
    )

    data = r.json()
    if not data.get("status"):
        raise RuntimeError(f"Login failed: {data}")

    tok = data["data"]
    state.jwt_token = tok["jwtToken"]
    state.refresh_token = tok["refreshToken"]
    state.feed_token = tok["feedToken"]
    state.last_login = datetime.now(timezone.utc)

    logging.info("Login successful")

def ensure_logged_in(state: AngelAccountState) -> None:
    if not state.jwt_token:
        login_account(state)

# ----------------------------
# FETCH HISTORICAL DATA
# ----------------------------
def fetch_chunk(
    state: AngelAccountState,
    symbol_token: str,
    exchange: str,
    interval: str,
    from_dt: datetime,
    to_dt: datetime,
) -> List[List[Any]]:

    ensure_logged_in(state)

    payload = {
        "exchange": exchange,
        "symboltoken": symbol_token,
        "interval": interval,
        "fromdate": from_dt.strftime("%Y-%m-%d %H:%M"),
        "todate": to_dt.strftime("%Y-%m-%d %H:%M"),
    }

    r = requests.post(
        HIST_URL,
        json=payload,
        headers=base_headers(state.config, state.jwt_token),
        timeout=10,
    )

    data = r.json()
    if not data.get("status"):
        raise RuntimeError(data.get("message"))

    candles = data["data"]

    if isinstance(candles, dict) and "candles" in candles:
        candles = candles["candles"]

    return candles

def fetch_full_history(
    state: AngelAccountState,
    symbol_token: str,
    exchange: str,
    interval: str,
    start_date: datetime,
    end_date: datetime,
    chunk_days: int = 30,
) -> List[List[Any]]:

    rows = []
    cursor = start_date

    while cursor < end_date:
        chunk_end = min(cursor + timedelta(days=chunk_days), end_date)
        logging.info(f"Fetching {cursor.date()} → {chunk_end.date()}")

        chunk = fetch_chunk(
            state,
            symbol_token,
            exchange,
            interval,
            cursor,
            chunk_end,
        )

        rows.extend(chunk)
        cursor = chunk_end
        time.sleep(2)

    return rows

# ----------------------------
# SAVE TO CSV
# ----------------------------
def save_to_csv(rows: List[List[Any]], filename: str) -> None:
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "open", "high", "low", "close", "volume"])
        writer.writerows(rows)

    logging.info(f"Saved {filename}")

# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":

    cfg = AngelAccountConfig(
        name="Trade360",
        clientcode=os.getenv("ANGEL_CLIENT_CODE"),
        pin=os.getenv("ANGEL_PIN"),
        api_key=os.getenv("ANGEL_API_KEY"),
        totp_secret=os.getenv("ANGEL_TOTP_SECRET"),
    )

    if not all([cfg.clientcode, cfg.pin, cfg.api_key, cfg.totp_secret]):
        raise RuntimeError("Missing API credentials. Please configure .env file.")

    state = AngelAccountState(cfg)

    START = datetime(2015, 1, 1, 9, 15)
    END = datetime(2024, 12, 31, 15, 30)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # ----------------------------
    # GOLD
    # ----------------------------
    GOLD_TOKEN = "449534"
    gold_data = fetch_full_history(
        state,
        symbol_token=GOLD_TOKEN,
        exchange="MCX",
        interval="ONE_DAY",
        start_date=START,
        end_date=END,
    )
    save_to_csv(gold_data, os.path.join(BASE_DIR, "gold.csv"))

    # ----------------------------
    # SILVER
    # ----------------------------
    SILVER_TOKEN = "451666"
    silver_data = fetch_full_history(
        state,
        symbol_token=SILVER_TOKEN,
        exchange="MCX",
        interval="ONE_DAY",
        start_date=START,
        end_date=END,
    )
    save_to_csv(silver_data, os.path.join(BASE_DIR, "silver.csv"))
