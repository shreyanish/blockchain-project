from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from authenticity_lab.adapters.web3_gateway import GanacheProvenanceGateway
from authenticity_lab.config import load_config
from authenticity_lab.core.ai import build_authenticity_analyzer
from authenticity_lab.core.pipeline import VerificationPipeline
from authenticity_lab.core.provenance import LocalResearchLedger, ProvenanceGateway, ProvenanceService


def create_app() -> Flask:
    app = Flask(__name__)
    config = load_config()
    gateway = _build_provenance_gateway(config)
    pipeline = VerificationPipeline(
        ProvenanceService(gateway),
        ai_analyzer=build_authenticity_analyzer(config.ai_analyzer),
    )

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/provenance")
    def provenance_records():
        return jsonify({"records": [record.to_dict() for record in pipeline.provenance.list_records()]})

    @app.post("/api/register")
    def register_media():
        uploaded = request.files.get("media")
        if uploaded is None:
            return jsonify({"error": "Upload an image using the 'media' field."}), 400
        owner = request.form.get("owner", "research-demo")
        content = uploaded.read()
        record = pipeline.register(content=content, file_name=uploaded.filename or "uploaded-image", owner=owner)
        report = pipeline.verify(content=content, file_name=uploaded.filename or "uploaded-image")
        return jsonify({"record": record.to_dict(), "verification": report.to_dict()})

    @app.post("/api/verify")
    def verify_media():
        uploaded = request.files.get("media")
        if uploaded is None:
            return jsonify({"error": "Upload an image using the 'media' field."}), 400
        content = uploaded.read()
        reference_hash = request.form.get("reference_hash") or None
        report = pipeline.verify(
            content=content,
            file_name=uploaded.filename or "uploaded-image",
            reference_hash=reference_hash,
        )
        return jsonify(report.to_dict())

    return app


def _build_provenance_gateway(config) -> ProvenanceGateway:
    if config.provenance_gateway.strip().lower() != "ganache":
        return LocalResearchLedger(config.ledger_path)

    if not config.ganache_contract_address:
        raise RuntimeError("GANACHE_CONTRACT_ADDRESS is required when PROVENANCE_GATEWAY=ganache.")

    artifact_path = Path(config.ganache_contract_abi_path)
    if not artifact_path.exists():
        raise RuntimeError(
            f"Ganache contract ABI artifact not found at {artifact_path}. Run `npm run compile` first."
        )

    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    abi = artifact.get("abi", artifact)
    return GanacheProvenanceGateway(
        rpc_url=config.ganache_rpc_url,
        contract_address=config.ganache_contract_address,
        contract_abi=abi,
        account=config.ganache_account,
    )


if __name__ == "__main__":
    create_app().run(debug=True)
