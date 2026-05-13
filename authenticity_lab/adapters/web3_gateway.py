from __future__ import annotations

from authenticity_lab.core.models import ProvenanceRecord, utc_now_iso


class GanacheProvenanceGateway:
    """Ganache/Web3 provenance adapter.

    This adapter is intentionally small and optional. The default Flask app uses
    the local research ledger unless this gateway is wired with a deployed
    contract address and ABI.
    """

    def __init__(self, rpc_url: str, contract_address: str, contract_abi: list[dict], account: str) -> None:
        try:
            from web3 import Web3
        except ImportError as exc:
            raise RuntimeError("web3 is required for Ganache provenance integration.") from exc

        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.web3.is_connected():
            raise RuntimeError(f"Could not connect to Ganache at {rpc_url}.")

        self.contract = self.web3.eth.contract(address=contract_address, abi=contract_abi)
        self.account = account
        self.chain_id = str(self.web3.eth.chain_id)

    def register(self, media_hash: str, owner: str, metadata: dict) -> ProvenanceRecord:
        tx_hash = self.contract.functions.registerMedia(media_hash, owner, str(metadata)).transact(
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
        return ProvenanceRecord(
            media_hash=media_hash,
            owner=owner,
            timestamp=str(timestamp),
            metadata={"contract_metadata": metadata},
            transaction_id="available-from-event-log",
            block_number=0,
            chain_id=self.chain_id,
        )

    def list_records(self) -> list[ProvenanceRecord]:
        return []
