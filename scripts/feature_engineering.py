#!/usr/bin/env python
"""Extract features *and labels* from a ClinVar gz‑VCF and save Parquet.

* Pulls INFO sub‑fields **CADD**, **AF**, **DP**
* Extracts **CLNSIG** (clinical significance) so the training script has
  real labels and no longer exits with the “one class” error.
* Forces CHROM to string + POS to Int64 to keep PyArrow happy.
"""

# [FIX] Imports are now sorted and 'os' is at the top level.
import argparse
import gzip
import os
import re
from io import StringIO

import pandas as pd

# Constants are best defined at the top level.
VCF_COLS = [
    "CHROM",
    "POS",
    "ID",
    "REF",
    "ALT",
    "QUAL",
    "FILTER",
    "INFO",
]

INFO_PATTERN = re.compile(r"([A-Za-z_]+)=([A-Za-z0-9\.,]+)")


def parse_info_field(info: str) -> dict:
    """Return a dict of INFO key/value strings (no type coercion)."""
    return dict(INFO_PATTERN.findall(info))


def main(vcf_path: str, out_path: str):
    """Main ETL logic."""
    with gzip.open(vcf_path) as fh:
        # [FIX] Changed ambiguous variable 'l' to 'line' for clarity.
        rows = [line.decode() for line in fh if not line.startswith(b"#")]

    df = pd.read_csv(
        StringIO("".join(rows)),
        # [FIX] Using "\t" is clearer than a literal tab character.
        sep="\t",
        names=VCF_COLS,
        header=None,
        low_memory=False,
    )

    # Split INFO field once to avoid repeated regex calls per feature
    info_dicts = df["INFO"].apply(parse_info_field)
    df["CADD"] = info_dicts.apply(lambda d: float(d.get("CADD", "nan")))
    df["AF"] = info_dicts.apply(lambda d: float(d.get("AF", "nan")))
    df["DP"] = info_dicts.apply(lambda d: float(d.get("DP", "nan")))
    
    # after parsing CADD/AF/DP …
    df["SpliceAI_DS"] = info_dicts.apply(
        lambda d: max(float(x) for x in d.get("SpliceAI", "nan|nan|nan|nan").split("|") if x != "nan")
                if "SpliceAI" in d else float("nan")
    )

    df["gnomAD_AF"] = info_dicts.apply(
        lambda d: float(d.get("gnomad_AF", "nan"))
    )

    df["CLNSIG"] = info_dicts.apply(lambda d: d.get("CLNSIG"))

    # Force types to prevent downstream errors with PyArrow
    df["CHROM"] = df["CHROM"].astype(str)
    df["POS"] = pd.to_numeric(df["POS"], errors="coerce").astype("Int64")

    df.to_parquet(out_path, index=False)
    print(f"✅ Saved {len(df):,} rows → {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("vcf", help="clinvar_YYYYMMDD.vcf.gz")
    ap.add_argument("--out", default="data/clinvar_features.parquet")
    args = ap.parse_args()

    # [FIX] The 'os.makedirs' call is now here, but the import is at the top.
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    main(args.vcf, args.out)
