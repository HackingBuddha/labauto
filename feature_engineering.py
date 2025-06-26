[⚠️ Suspicious Content] #!/usr/bin/env python
"""Extract features from a ClinVar VCF and save Parquet."""
import gzip, re, argparse, pandas as pd
from io import StringIO

VCF_COLS = [
    "CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO"
]

def parse_info(info: str, key: str, default=float("nan")):
    m = re.search(fr"{key}=([^;]+)", info)
    return float(m.group(1)) if m else default

def main(vcf_path: str, out_path: str):
    lines = []
    with gzip.open(vcf_path) as fh:
        for l in fh:
            if l.startswith(b"#"):  # skip headers
                continue
            lines.append(l.decode())
    df = pd.read_csv(StringIO("".join(lines)), sep="\t", names=VCF_COLS, header=None)

    # Minimal features
    df["CADD"] = df["INFO"].apply(lambda x: parse_info(x, "CADD"))
    df["AF"]   = df["INFO"].apply(lambda x: parse_info(x, "AF"))
    df["DP"]   = df["INFO"].apply(lambda x: parse_info(x, "DP"))

    df.to_parquet(out_path, index=False)
    print(f"✅ Saved {len(df):,} rows → {out_path}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("vcf", help="clinvar_YYYYMMDD.vcf.gz")
    ap.add_argument("--out", default="data/clinvar_features.parquet")
    args = ap.parse_args()

    import os; os.makedirs(os.path.dirname(args.out), exist_ok=True)
    main(args.vcf, args.out)
