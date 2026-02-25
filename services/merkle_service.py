from merkletools import MerkleTools


def generate_merkle_root(hashes):
    """
    Generate Merkle root from list of SHA256 hashes
    """

    if not hashes:
        return None

    mt = MerkleTools(hash_type="sha256")

    # Add leaves
    for h in hashes:
        mt.add_leaf(h, True)  # True = already hashed

    mt.make_tree()

    return mt.get_merkle_root()


def generate_merkle_proof(hashes, target_hash):
    """
    Generate Merkle proof for a specific leaf
    """

    if not hashes:
        return None

    mt = MerkleTools(hash_type="sha256")

    for h in hashes:
        mt.add_leaf(h, True)

    mt.make_tree()

    index = hashes.index(target_hash)
    proof = mt.get_proof(index)

    return proof