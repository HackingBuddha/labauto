from fastapi import FastAPI, UploadFile
import gzip, pandas as pd, joblib, re
from io import StringIO

app   = FastAPI(title="Variant Pathogenicity API")
model = joblib.load("data/variant_lr.pkl")

@app.post("/annotate_vcf")
async def annotate_vcf(vcf_gz: UploadFile):
    raw = gzip.decompress(await vcf_gz.read()).decode()
    body = [l for l in raw.splitlines() if not l.startswith("#")]
    df = pd.read_csv(StringIO("\n".join(body)), sep="\t", header=None,
                     names=["CHROM","POS","ID","REF","ALT","QUAL","FILTER","INFO"])
    df["CADD"] = df["INFO"].str.extract(r"CADD=([\d\.]+)").astype(float)
    df["AF"]   = df["INFO"].str.extract(r"AF=([\d\.]+)").astype(float)
    df["DP"]   = df["INFO"].str.extract(r"DP=([\d\.]+)").astype(float)
    preds = model.predict_proba(df[["DP","AF","CADD"]].fillna(0))[:,1]
    return {
        "n": len(df),
        "pathogenic_calls": int((preds>0.5).sum()),
    }
