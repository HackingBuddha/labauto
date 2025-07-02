# scripts/feature_engineering.py

import pandas as pd
import vcf
import argparse
import logging

# Set up the logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


def vcf_to_dataframe(vcf_file):
    """
    Convert a VCF file to a pandas DataFrame.
    This is a simplified VCF parser that only extracts the fields we need.
    It is not a general-purpose VCF parser.
    For a more robust solution, you should use a library like cyvcf2 or pyvcf.
    """
    vcf_reader = vcf.Reader(open(vcf_file, "r"))
    records = []
    for record in vcf_reader:
        records.append(
            {
                "CHROM": record.CHROM,
                "POS": record.POS,
                "ID": record.ID,
                "REF": record.REF,
                "ALT": str(record.ALT[0]),
                "QUAL": record.QUAL,
                "FILTER": str(record.FILTER),
                "INFO": str(record.INFO),
                "CLNSIG": record.INFO.get("CLNSIG", [None])[0],
            }
        )
    return pd.DataFrame(records)


def is_pathogenic(clnsig):
    """
    Convert the CLNSIG field to a binary is_pathogenic label.
    This is a simplified version of the logic used in the paper.
    For a more robust solution, you should use a more sophisticated mapping
    of ClinVar significance to pathogenicity.
    """
    if clnsig is None:
        return 0
    clnsig = clnsig.lower()
    if "pathogenic" in clnsig:
        return 1
    else:
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Feature engineering script for ClinVar VCF file"
    )
    parser.add_argument("vcf_file", help="Path to ClinVar VCF file")
    parser.add_argument("--out", help="Path to output parquet file", required=True)
    args = parser.parse_args()

    # Convert VCF to DataFrame
    logging.info(f"Loading VCF file {args.vcf_file}...")
    df = vcf_to_dataframe(args.vcf_file)

    # Create features
    logging.info("Creating features...")
    df["REF_LEN"] = df["REF"].str.len()
    df["ALT_LEN"] = df["ALT"].str.len()
    df["is_snp"] = (df["REF_LEN"] == 1) & (df["ALT_LEN"] == 1)
    df["is_indel"] = df["REF_LEN"] != df["ALT_LEN"]
    df["is_deletion"] = df["REF_LEN"] > df["ALT_LEN"]
    df["is_insertion"] = df["REF_LEN"] < df["ALT_LEN"]

    # Create the target variable
    logging.info("Creating target variable 'is_pathogenic'...")
    df["is_pathogenic"] = df["CLNSIG"].apply(is_pathogenic)

    # Select only the feature columns
    # We are keeping the target variable 'is_pathogenic' in the dataframe
    # so that we can use it for training.
    feature_cols = [
        "POS",
        "REF_LEN",
        "ALT_LEN",
        "is_snp",
        "is_indel",
        "is_deletion",
        "is_insertion",
        "is_pathogenic",  # <-- THE FIX IS HERE
    ]
    df = df[feature_cols]

    # Save to parquet
    logging.info(f"Saving {len(df)} rows → {args.out}")
    df.to_parquet(args.out)


if __name__ == "__main__":
    main()