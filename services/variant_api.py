# [FIX] Imports are now one per line, sorted, and unused 're' is removed.
import gzip
import joblib
from io import StringIO

import pandas as pd
from fastapi import FastAPI, UploadFile

# --- App and Model ---
# It's good practice to load models once at startup, not inside the endpoint.
model = joblib.load("data/model.joblib")
app = FastAPI()


@app.post("/tool/annotate_variants")
async def annotate_vcf(vcf_gz: UploadFile):
    """Takes a gzipped VCF file and returns a pathogenic variant count."""
    raw = gzip.decompress(await vcf_gz.read()).decode()

    # [FIX] Changed ambiguous variable 'l' to 'line' for clarity.
    body = [line for line in raw.splitlines() if not line.startswith("#")]

    df = pd.read_csv(
        StringIO("\n".join(body)),
        sep="\t",
        header=None,
        names=["CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO"],
    )

    # Placeholder for feature engineering logic that must match training
    # For this example, we'll assume a dummy feature.
    # In a real app, you would import and use the same feature
    # engineering functions from your training script.
    features = pd.DataFrame({"is_indel": (df["REF"].str.len() != df["ALT"].str.len())})

    # Predict
    predictions = model.predict(features)
    pathogenic_count = int(predictions.sum())

    return {"pathogenic_variant_count": pathogenic_count}