"""
Telechargement des donnees Eurostat -- Emploi jeunes diplomes Europe
"""

import requests
import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

# Codes valides Eurostat (verifies via API metadata)
DATASETS = {
    "emploi_education":  {"code": "lfsa_ergaed",  "since": "2010"},
    "chomage_education": {"code": "lfsa_urgaed",  "since": "2010"},
    "neet":              {"code": "edat_lfse_22",  "since": "2010"},
    "emploi_secteur":    {"code": "lfsa_egan2",   "since": "2015"},
}

# Filtres appliques apres download (colonnes Eurostat standard)
FILTERS = {
    "emploi_education":  {"sex": "T", "age": ["Y15-24", "Y25-34"]},
    "chomage_education": {"sex": "T", "age": ["Y15-24", "Y25-34"]},
    "neet":              {"sex": "T", "age": ["Y15-29", "Y15-24"]},
    "emploi_secteur":    {"sex": "T", "age": ["Y15-24", "Y25-34"]},
}


def fetch_eurostat(code: str, since: str = "2010") -> pd.DataFrame:
    url = f"{BASE_URL}/{code}"
    params = {"format": "JSON", "lang": "EN", "sinceTimePeriod": since}

    print(f"  {code} ...", end=" ", flush=True)
    r = requests.get(url, params=params, timeout=90)
    r.raise_for_status()
    return parse_json(r.json())


def parse_json(data: dict) -> pd.DataFrame:
    dims = data["dimension"]
    dim_ids = data["id"]
    values = data["value"]

    if not values:
        return pd.DataFrame()

    dim_sizes = [len(dims[d]["category"]["index"]) for d in dim_ids]
    dim_idx   = [{v: k for k, v in dims[d]["category"]["index"].items()} for d in dim_ids]

    rows = []
    for pos_str, val in values.items():
        pos = int(pos_str)
        coords, remaining = [], pos
        for i in range(len(dim_sizes) - 1, -1, -1):
            coords.insert(0, remaining % dim_sizes[i])
            remaining //= dim_sizes[i]

        row = {dim_ids[i]: dim_idx[i][coords[i]] for i in range(len(dim_ids))}
        row["value"] = val
        rows.append(row)

    return pd.DataFrame(rows)


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    for col, val in filters.items():
        if col not in df.columns:
            continue
        if isinstance(val, list):
            df = df[df[col].isin(val)]
        else:
            df = df[df[col] == val]
    return df


def main():
    print("=== Telechargement donnees Eurostat ===\n")
    results = []

    for name, cfg in DATASETS.items():
        try:
            df = fetch_eurostat(cfg["code"], cfg["since"])
            if df.empty:
                print("vide")
                results.append((name, 0, "vide"))
                continue

            total = len(df)
            df = apply_filters(df, FILTERS.get(name, {}))
            out = RAW_DIR / f"{name}.csv"
            df.to_csv(out, index=False, encoding="utf-8")
            print(f"OK  ({total} -> {len(df)} lignes apres filtres)")
            results.append((name, len(df), "OK"))

        except Exception as e:
            print(f"ERREUR")
            results.append((name, 0, str(e)))

    print("\n--- Resume ---")
    for name, n, status in results:
        print(f"  {name:30s} {n:>6} lignes  [{status}]")
    print(f"\nFichiers dans : {RAW_DIR}")


if __name__ == "__main__":
    main()
