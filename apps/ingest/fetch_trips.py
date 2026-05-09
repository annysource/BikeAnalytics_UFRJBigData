"""
fetch_trips.py — Ingestão incremental dos CSVs históricos CitiBike
Verifica quais arquivos já existem no HDFS e baixa apenas os novos.
"""
import requests
import zipfile
import io
import time
from datetime import datetime, timezone
from hdfs import InsecureClient

BASE_URL = "https://s3.amazonaws.com/tripdata/{month}-citibike-tripdata.zip"
HDFS_URL = "http://namenode:9870"
HDFS_DIR = "/citibike/trips"

client = InsecureClient(HDFS_URL, user="root")


def ensure_dir():
    if not client.status(HDFS_DIR, strict=False):
        client.makedirs(HDFS_DIR)


def get_available_months():
    """Gera lista de meses desde Jan/2026 até o mês anterior ao atual."""
    now = datetime.now(timezone.utc)
    months = []
    year, month = 2026, 1
    while (year, month) < (now.year, now.month):
        months.append(f"{year}{month:02d}")
        month += 1
        if month > 12:
            month = 1
            year += 1
    return months


def get_hdfs_files():
    """Retorna set de arquivos já existentes no HDFS."""
    try:
        return set(client.list(HDFS_DIR))
    except Exception:
        return set()


def check_remote_exists(url):
    """Verifica se o arquivo existe no S3 sem baixar."""
    try:
        return requests.head(url, timeout=10).status_code == 200
    except Exception:
        return False


def download_and_store(month_code):
    url = BASE_URL.format(month=month_code)
    try:
        # Baixa o zip para um arquivo temporário em disco (sem carregar na RAM)
        import tempfile, os
        resp = requests.get(url, timeout=120, stream=True)
        resp.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            total = 0
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                tmp.write(chunk)
                total += len(chunk)
                print(f"  ↓ {total/1024/1024:.1f} MB...", end="\r")
            tmp_path = tmp.name

        print(f"  ↓ Download completo: {total/1024/1024:.1f} MB")

        with zipfile.ZipFile(tmp_path) as zf:
            csv_files = [f for f in zf.namelist() if f.endswith(".csv")]
            for csv_name in csv_files:
                csv_bytes = zf.read(csv_name)
                with client.write(f"{HDFS_DIR}/{csv_name}", overwrite=True) as w:
                    w.write(csv_bytes)
                print(f"  ✓ {csv_name} ({len(csv_bytes)/1024/1024:.1f} MB) → HDFS")

        os.unlink(tmp_path)  # Remove o temp após enviar
        return csv_files

    except requests.exceptions.HTTPError as e:
        print(f"  ✗ HTTP {e.response.status_code}")
        return []
    except Exception as e:
        print(f"  ✗ ERRO: {e}")
        return []

def sync_trips():
    now = datetime.now(timezone.utc)
    print(f"[{now.strftime('%H:%M:%S')}] 🔄 Verificando Trip History...")

    ensure_dir()
    available_months = get_available_months()
    hdfs_files = get_hdfs_files()

    new_downloads = 0
    for month_code in available_months:
        expected_file = f"{month_code}-citibike-tripdata.csv"
        if expected_file in hdfs_files:
            print(f"  ✓ {month_code} já existe no HDFS — pulando")
            continue

        url = BASE_URL.format(month=month_code)
        if not check_remote_exists(url):
            print(f"  ⏳ {month_code} ainda não disponível no S3")
            continue

        print(f"  📥 {month_code} — novo arquivo detectado, baixando...")
        stored = download_and_store(month_code)
        new_downloads += len(stored)

    if new_downloads == 0:
        print(f"[{now.strftime('%H:%M:%S')}] ✓ Nenhum arquivo novo nos trips")
    else:
        print(f"[{now.strftime('%H:%M:%S')}] ✅ {new_downloads} arquivo(s) adicionados ao HDFS")