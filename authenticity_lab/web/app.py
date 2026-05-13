from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from authenticity_lab.config import load_config
from authenticity_lab.core.ai import build_authenticity_analyzer
from authenticity_lab.core.pipeline import VerificationPipeline
from authenticity_lab.core.provenance import LocalResearchLedger, ProvenanceService


def create_app() -> Flask:
    app = Flask(__name__)
    config = load_config()
    ledger = LocalResearchLedger(config.ledger_path)
    pipeline = VerificationPipeline(
        ProvenanceService(ledger),
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


if __name__ == "__main__":
    create_app().run(debug=True)
