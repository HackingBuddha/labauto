#!/usr/bin/env python
"""
serve_mcp.py  –  Minimal HTTP MCP gateway that proxies the two FastAPI
services you already run locally:

* Variant API   ->  http://127.0.0.1:8000/tool/annotate_variants
* Robot  API    ->  http://127.0.0.1:8001/tool/aliquot_plate
"""
import os
import requests
import uvicorn  # <<< FIX: Import uvicorn
from fastapi import UploadFile, HTTPException
from mcp.server.fastmcp import FastMCP

# --- Configuration ---
VARIANT_URL = os.getenv("VARIANT_URL", "http://127.0.0.1:8000/tool/annotate_variants")
ROBOT_URL   = os.getenv("ROBOT_URL", "http://127.0.0.1:8001/tool/aliquot_plate")
GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", 8080))

mcp = FastMCP("LabAuto 🧬🤖 Toolkit")

# ---------- annotate_variants ----------------------------------------
@mcp.tool(
    name="annotate_variants",
    description="Upload a gzip-compressed ClinVar VCF and "
                "return the number of predicted pathogenic variants.",
)
def annotate_variants(vcf_gz: UploadFile) -> dict:
    """
    Proxies a file upload to the variant annotation service.
    """
    try:
        # Stream the file instead of reading it all into memory.
        files = {"vcf_gz": (vcf_gz.filename, vcf_gz.file, vcf_gz.content_type)}
        
        resp = requests.post(
            VARIANT_URL,
            files=files,
            timeout=300,
        )
        resp.raise_for_status()
        return resp.json()

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: Error contacting Variant API: {e}",
        )
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from Variant API: {e.response.text}",
        )

# ---------- aliquot_plate --------------------------------------------
@mcp.tool(
    name="aliquot_plate",
    description="Run the OT-2 simulator aliquot protocol and "
                "return the first 20 log lines.",
)
def aliquot_plate() -> dict:
    """
    Proxies a request to the robot control service.
    """
    try:
        resp = requests.post(ROBOT_URL, timeout=120)
        resp.raise_for_status()
        return resp.json()
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: Error contacting Robot API: {e}",
        )
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from Robot API: {e.response.text}",
        )

# ---------- launch ----------------------------------------------------
if __name__ == "__main__":
    print(f"🧬🤖 LabAuto Gateway starting on http://0.0.0.0:{GATEWAY_PORT}")
    print(f"-> Proxying Variant Annotation to: {VARIANT_URL}")
    print(f"-> Proxying Robot Aliquot to:    {ROBOT_URL}")
    
    # <<< FIX: Use uvicorn.run() to serve the FastAPI application (`mcp` object)
    uvicorn.run(mcp, host="0.0.0.0", port=GATEWAY_PORT)
