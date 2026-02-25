import os
import requests
from dotenv import load_dotenv

load_dotenv()

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET_KEY = os.getenv("PINATA_SECRET_KEY")

PINATA_URL = "https://api.pinata.cloud/pinning/pinJSONToIPFS"


def upload_to_ipfs(data):
    try:
        headers = {
            "Content-Type": "application/json",
            "pinata_api_key": PINATA_API_KEY,
            "pinata_secret_api_key": PINATA_SECRET_KEY
        }

        response = requests.post(
            PINATA_URL,
            json=data,
            headers=headers
        )

        if response.status_code != 200:
            raise Exception(response.text)

        cid = response.json()["IpfsHash"]

        return cid

    except Exception as e:
        raise Exception(f"IPFS upload failed: {str(e)}")