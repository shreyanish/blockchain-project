from __future__ import annotations

import ast
import json

from authenticity_lab.core.models import ProvenanceRecord, utc_now_iso


class GanacheProvenanceGateway:
    """Ganache/Web3 provenance adapter.

    This adapter is intentionally small and optional. The default Flask app uses
    the local research ledger unless this gateway is wired with a deployed
    contract address and ABI.
    """

    def __init__(self, rpc_url: str, contract_address: str, contract_abi: list[dict], account: str = "") -> None:
        try:
            from web3 import Web3
        except ImportError as exc:
            raise RuntimeError("web3 is required for Ganache provenance integration.") from exc

        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.web3.is_connected():
            raise RuntimeError(f"Could not connect to Ganache at {rpc_url}.")

        self.contract = self.web3.eth.contract(address=contract_address, abi=contract_abi)
        accounts = self.web3.eth.accounts
        self.account = account or (accounts[0] if accounts else "")
        if not self.account:
            raise RuntimeError("No Ganache account was provided or exposed by the RPC node.")
        self.chain_id = str(self.web3.eth.chain_id)

    def register(self, media_hash: str, owner: str, metadata: dict) -> ProvenanceRecord:
        metadata_payload = json.dumps(metadata, sort_keys=True)
        tx_hash = self.contract.functions.registerMedia(media_hash, owner, metadata_payload).transact(
            {"from": self.account}
        )
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return ProvenanceRecord(
            media_hash=media_hash,
            owner=owner,
            timestamp=utc_now_iso(),
            metadata=metadata,
            transaction_id=receipt.transactionHash.hex(),
            block_number=receipt.blockNumber,
            chain_id=self.chain_id,
        )

    def lookup(self, media_hash: str) -> ProvenanceRecord | None:
        exists, owner, timestamp, metadata = self.contract.functions.getMedia(media_hash).call()
        if not exists:
            return None
        event_record = self._event_record(media_hash)
        return ProvenanceRecord(
            media_hash=media_hash,
            owner=owner,
            timestamp=str(timestamp),
            metadata=self._decode_metadata(metadata),
            transaction_id=event_record.transaction_id if event_record else "available-from-event-log",
            block_number=event_record.block_number if event_record else 0,
            chain_id=self.chain_id,
        )

    def list_records(self) -> list[ProvenanceRecord]:
        try:
            events = self.contract.events.MediaRegistered().get_logs(fromBlock=0, toBlock="latest")
        except TypeError:
            events = self.contract.events.MediaRegistered().get_logs(from_block=0, to_block="latest")

        return [self._record_from_event(event) for event in events]

    def _event_record(self, media_hash: str) -> ProvenanceRecord | None:
        try:
            events = self.contract.events.MediaRegistered().get_logs(
                fromBlock=0,
                toBlock="latest",
                argument_filters={"mediaHash": media_hash},
            )
        except TypeError:
            events = self.contract.events.MediaRegistered().get_logs(
                from_block=0,
                to_block="latest",
                argument_filters={"mediaHash": media_hash},
            )
        if not events:
            return None
        return self._record_from_event(events[-1])

    def _record_from_event(self, event) -> ProvenanceRecord:
        args = event["args"]
        tx_hash = event["transactionHash"]
        media_hash = args["mediaHash"]
        owner = args["owner"]
        # Convert bytes to hex strings if needed
        if isinstance(media_hash, bytes):
            media_hash = media_hash.hex()
        if isinstance(owner, bytes):
            owner = owner.hex()
        return ProvenanceRecord(
            media_hash=str(media_hash),
            owner=str(owner),
            timestamp=str(args["timestamp"]),
            metadata=self._decode_metadata(args["metadata"]),
            transaction_id=tx_hash.hex() if hasattr(tx_hash, "hex") else str(tx_hash),
            block_number=event["blockNumber"],
            chain_id=self.chain_id,
        )

    def _decode_metadata(self, payload: str) -> dict:
        try:
            decoded = json.loads(payload)
            return decoded if isinstance(decoded, dict) else {"contract_metadata": decoded}
        except json.JSONDecodeError:
            try:
                decoded = ast.literal_eval(payload)
                return decoded if isinstance(decoded, dict) else {"contract_metadata": decoded}
            except (SyntaxError, ValueError):
                return {"contract_metadata": payload}
