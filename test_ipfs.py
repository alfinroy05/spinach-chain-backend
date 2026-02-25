from services.ipfs_service import upload_to_ipfs

test_data = {
    "test": "SpinachChain IPFS working",
    "value": 123
}

cid = upload_to_ipfs(test_data)

print("Uploaded Successfully!")
print("CID:", cid)