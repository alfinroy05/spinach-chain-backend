import os
import requests
from dotenv import load_dotenv

load_dotenv()

# =====================================================
# 🔐 ENV VALIDATION
# =====================================================

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET_API_KEY = os.getenv("PINATA_SECRET_KEY")

if not PINATA_API_KEY or not PINATA_SECRET_API_KEY:
    raise Exception("Pinata API keys not found in environment variables.")

PIN_JSON_URL = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
PIN_FILE_URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"

HEADERS = {
    "pinata_api_key": PINATA_API_KEY,
    "pinata_secret_api_key": PINATA_SECRET_API_KEY
}


# =====================================================
# 🔥 JSON UPLOAD (PRIMARY FUNCTION USED BY AI ROUTES)
# =====================================================

def upload_json_to_ipfs(data, name="batch_metadata"):
    """
    Upload structured JSON metadata to IPFS via Pinata
    """

    try:
        payload = {
            "pinataMetadata": {
                "name": name
            },
            "pinataContent": data
        }

        response = requests.post(
            PIN_JSON_URL,
            json=payload,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        cid = response.json().get("IpfsHash")

        if not cid:
            raise Exception("CID not returned from Pinata")

        return cid

    except requests.exceptions.RequestException as e:
        raise Exception(f"IPFS JSON upload failed: {str(e)}")


# =====================================================
# 📁 FILE UPLOAD (OPTIONAL - FOR IMAGES)
# =====================================================

def upload_file_to_ipfs(file_obj, filename="leaf_image.jpg"):
    """
    Upload file (image, document) to IPFS
    """

    try:
        files = {
            "file": (filename, file_obj)
        }

        response = requests.post(
            PIN_FILE_URL,
            files=files,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

        cid = response.json().get("IpfsHash")

        if not cid:
            raise Exception("CID not returned from Pinata")

        return cid

    except requests.exceptions.RequestException as e:
        raise Exception(f"IPFS file upload failed: {str(e)}")


# =====================================================
# 🌐 PUBLIC GATEWAY URL
# =====================================================

def get_ipfs_gateway_url(cid):
    return f"https://gateway.pinata.cloud/ipfs/{cid}"


# =====================================================
# 🔁 SAFE RETRY WRAPPER
# =====================================================

def safe_upload_json(data, retries=2):
    """
    Retry JSON upload if it fails
    """

    for attempt in range(retries + 1):
        try:
            return upload_json_to_ipfs(data)
        except Exception:
            if attempt == retries:
                raise


# =====================================================
# 🔄 BACKWARD COMPATIBILITY (OLD IMPORT FIX)
# =====================================================

# If any old file imports upload_to_ipfs, it will still work
def upload_to_ipfs(data):
    return upload_json_to_ipfs(data)