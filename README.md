# LabAuto 🧬🤖 Bioinformatics + Lab‑Automation Starter

End‑to‑end demo that:
1. Parses a ClinVar VCF, engineers features, saves Parquet
2. Trains a logistic‐regression pathogenicity model
3. Serves a FastAPI endpoint `/annotate_vcf`
4. Exposes the endpoint as an MCP tool for LangGraph / CrewAI

See **scripts/** for CLI helpers and **services/** for the API.
