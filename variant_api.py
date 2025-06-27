#!/usr/bin/env python
# [FIX] This is the fully corrected and linted version.

import gzip
import joblib
from io import StringIO

import pandas as pd
from fastapi import FastAPI, UploadFile

# --- App and Model ---
model = joblib.load("data/model.joblib")
app = FastAPI()


@app.post("/tool/annotate_variants")
async def annotate_vcf(vcf_gz: UploadFile):
    """Takes a gzipped VCF file and returns a pathogenic variant count."""
    raw = gzip.decompress(await vcf_gz.read()).decode()

    # [FIX] The ambiguous variable 'l' is now 'line'.
    body = [line for line in raw.splitlines() if not line.startswith("#")]

    df = pd.read_csv(
        StringIO("\n".join(body)),
        sep="\t",
        header=None,
        names=["CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO"],
    )

    # Placeholder for feature engineering logic.
    features = pd.DataFrame({"is_indel": (df["REF"].str.len() != df["ALT"].str.len())})

    # Predict
    predictions = model.predict(features)
    pathogenic_count = int(predictions.sum())

    return {"pathogenic_variant_count": pathogenic_count}
