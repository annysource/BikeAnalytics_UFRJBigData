"""
fetch_citibike.py — Pipeline unificado v2
Coleta station_status + station_info do GBFS oficial CitiBike NYC
e envia ao HDFS.
"""
import requests
import json
import time
from datetime import datetime, timezone
from hdfs import InsecureClient

#APIs
API_STATUS  = "https://gbfs.citibikenyc.com/gbfs/en/station_status.json"
API_INFO    = "https://gbfs.citibikenyc.com/gbfs/en/station_information.json"

#HDFS
HDFS_URL        = "http://namenode:9870"
HDFS_DIR_STATUS = "/citibike/station_status"
HDFS_DIR_INFO   = "/citibike/station_info"
INTERVAL_SECONDS = 300

client = InsecureClient(HDFS_URL, user="root")

#Cria diretórios
def ensure_dirs():
    for d in [HDFS_DIR_STATUS, HDFS_DIR_INFO]:
        if not client.status(d, strict=False):
            client.makedirs(d)

#Busca pelos dados e armazena no HDFS
def fetch_and_store():
    print(f"Pipeline iniciado. Coletando GBFS a cada {INTERVAL_SECONDS}s")
    print("Feeds: station_status + station_information\n")
    ensure_dirs()

    while True:
        now = datetime.now(timezone.utc)
        ts  = now.strftime("%Y%m%d_%H%M%S")

        #Busca pelos dados de station_stauts
        try:
            data = requests.get(API_STATUS, timeout=15).json()
            stations = data["data"]["stations"]
            for s in stations:
                s["collected_at"] = now.isoformat()

            json_bytes = json.dumps(stations, indent=2).encode("utf-8")
            hdfs_path = f"{HDFS_DIR_STATUS}/status_{ts}.json"

            with client.write(hdfs_path, overwrite=True) as w:
                w.write(json_bytes)

            total_bikes = sum(s.get("num_bikes_available", 0) for s in stations)
            total_docks = sum(s.get("num_docks_available", 0) for s in stations)

            print(f"[{now.strftime('%H:%M:%S')}] ✓ STATUS: {len(stations)} estações | "
                  f"{total_bikes} bikes | {total_docks} vagas | "
                  f"{len(json_bytes)/1024:.1f} KB → {hdfs_path}")
        except Exception as e:
            print(f"[{now.strftime('%H:%M:%S')}] ✗ ERRO status: {e}")

        #Busca pelos dados de station information
        try:
            data = requests.get(API_INFO, timeout=15).json()
            stations = data["data"]["stations"]

            json_bytes = json.dumps(stations, indent=2).encode("utf-8")
            hdfs_path = f"{HDFS_DIR_INFO}/info_{ts}.json"

            with client.write(hdfs_path, overwrite=True) as w:
                w.write(json_bytes)

            print(f"[{now.strftime('%H:%M:%S')}] ✓ INFO: {len(stations)} estações | "
                  f"{len(json_bytes)/1024:.1f} KB → {hdfs_path}")
        except Exception as e:
            print(f"[{now.strftime('%H:%M:%S')}] ✗ ERRO info: {e}")

        print()
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    fetch_and_store()