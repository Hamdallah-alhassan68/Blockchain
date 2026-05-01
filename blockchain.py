import hashlib
import json
from time import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_certificates = []
        self.create_block('0')

    def create_block(self, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(time()),
            'certificates': self.pending_certificates,
            'previous_hash': previous_hash
        }

        self.pending_certificates = []  # clear pending
        self.chain.append(block)
        return block

    def add_certificate(self, cert_hash):
        self.pending_certificates.append(cert_hash)

    def mine_block(self):
        previous_block = self.chain[-1]
        previous_hash = self.hash(previous_block)
        return self.create_block(previous_hash)

    def hash(self, block):
        return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

    def is_valid(self, cert_hash):
        for block in self.chain:
            if cert_hash in block['certificates']:
                return True
        return False
