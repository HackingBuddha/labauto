#!/usr/bin/env python
"""Extract features *and labels* from a ClinVar gz‑VCF and save Parquet.

* Pulls INFO sub‑fields **CADD**, **AF**, **DP**
* Extracts **CLNSIG** (clinical significance) so the training script has
  real labels and no longer exits with the “one class” error.
* Forces CHROM to string + POS to Int64 to keep PyArrow happy.
"""
import gzip, re, argparse
from io import StringIO
import pandas as pd

VCF_COLS = [
    "CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO",
]

INFO_PATTERN = re.compile(r"([A-Za-z_]+)=([A-Za-z0-9\.,]+)")

def parse_info_field(info: str):
    """Return a dict of INFO key/value strings (no type coercion)."""
    return dict(INFO_PATTERN.findall(info))

def main(vcf_path: str, out_path: str):
    with gzip.open(vcf_path) as fh:
        rows = [l.decode() for l in fh if not l.startswith(b"#")]

    df = pd.read_csv(
        StringIO("".join(rows)),
        sep="	",
        names=VCF_COLS,
        header=None,
        low_memory=False,
    )

    # Split INFO field once to avoid repeated regex calls per feature
    info_dicts = df["INFO"].apply(parse_info_field)
    df["CADD"]   = info_dicts.apply(lambda d: float(d.get("CADD", "nan")))
    df["AF"]     = info_dicts.apply(lambda d: float(d.get("AF",   "nan")))
    df["DP"]     = info_dicts.apply(lambda d: float(d.get("DP",   "nan")))
    df["CLNSIG"] = info_dicts.apply(lambda d: d.get("CLNSIG"))

    df["CHROM"] = df["CHROM"].astype(str)
    df["POS"]   = pd.to_numeric(df["POS"], errors="coerce").astype("Int64")

    df.to_parquet(out_path, index=False)
    print(f"✅ Saved {len(df):,} rows → {out_path}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("vcf", help="clinvar_YYYYMMDD.vcf.gz")
    ap.add_argument("--out", default="data/clinvar_features.parquet")
    args = ap.parse_args()

    import os; os.makedirs(os.path.dirname(args.out), exist_ok=True)
    main(args.vcf, args.out)
