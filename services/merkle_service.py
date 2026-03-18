import hashlib


# ======================================================
# 🔐 HASH FUNCTION
# ======================================================

def hash_data(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


# ======================================================
# 🌳 GENERATE MERKLE ROOT
# ======================================================

def generate_merkle_root(hashes):
    """
    Generate Merkle root from list of SHA256 hashes
    """

    if not hashes:
        return None

    current_level = hashes[:]

    while len(current_level) > 1:
        next_level = []

        for i in range(0, len(current_level), 2):
            left = current_level[i]

            if i + 1 < len(current_level):
                right = current_level[i + 1]
            else:
                right = left  # duplicate if odd

            combined = left + right
            new_hash = hashlib.sha256(combined.encode()).hexdigest()

            next_level.append(new_hash)

        current_level = next_level

    return current_level[0]


# ======================================================
# 🌿 GENERATE MERKLE PROOF
# ======================================================

def generate_merkle_proof(hashes, target_hash):
    """
    Generate Merkle proof for a specific leaf
    """

    if not hashes or target_hash not in hashes:
        return None

    tree_levels = []
    current_level = hashes[:]
    tree_levels.append(current_level)

    # Build full tree
    while len(current_level) > 1:
        next_level = []

        for i in range(0, len(current_level), 2):
            left = current_level[i]

            if i + 1 < len(current_level):
                right = current_level[i + 1]
            else:
                right = left

            combined = left + right
            new_hash = hashlib.sha256(combined.encode()).hexdigest()
            next_level.append(new_hash)

        current_level = next_level
        tree_levels.append(current_level)

    # Generate proof
    proof = []
    index = hashes.index(target_hash)

    for level in tree_levels[:-1]:
        is_right_node = index % 2

        if is_right_node:
            pair_index = index - 1
            position = "left"
        else:
            pair_index = index + 1
            position = "right"

        if pair_index < len(level):
            proof.append({
                "position": position,
                "hash": level[pair_index]
            })

        index = index // 2

    return proof


# ======================================================
# ✅ VERIFY MERKLE PROOF (OPTIONAL BUT POWERFUL)
# ======================================================

def verify_merkle_proof(target_hash, proof, root):
    """
    Verify Merkle proof
    """

    current_hash = target_hash

    for step in proof:
        if step["position"] == "left":
            combined = step["hash"] + current_hash
        else:
            combined = current_hash + step["hash"]

        current_hash = hashlib.sha256(combined.encode()).hexdigest()

    return current_hash == root