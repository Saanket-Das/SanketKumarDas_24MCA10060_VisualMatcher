# Save this file as backend/download_images.py

import os
import json
import requests
from tqdm import tqdm

DB_PATH = os.path.join('database', 'products.json')
IMAGE_DIR = os.path.join('database', 'images')

def main():
    """Downloads all product images to a local folder."""
    print("--- Starting Image Downloader ---")

    # Create the target directory if it doesn't exist
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
        print(f"Created directory: {IMAGE_DIR}")

    try:
        with open(DB_PATH, 'r') as f:
            products_data = json.load(f)
    except Exception as e:
        print(f"FATAL ERROR: Could not load {DB_PATH}. Reason: {e}")
        return

    print(f"Found {len(products_data)} products to download.")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for product in tqdm(products_data, desc="Downloading Images"):
        url = product['imageUrl']
        product_id = product['id']
        # Create a simple filename, e.g., '1.jpg', '2.jpg'
        filename = os.path.join(IMAGE_DIR, f"{product_id}.jpg")

        # Only download if the file doesn't already exist
        if not os.path.exists(filename):
            try:
                response = requests.get(url, headers=headers, timeout=20)
                response.raise_for_status()
                with open(filename, 'wb') as f:
                    f.write(response.content)
            except Exception as e:
                print(f"\nFailed to download image for product ID {product_id} from {url}. Error: {e}")

    print("\n--- Download process finished. ---")
    # Count how many files were successfully downloaded
    downloaded_count = len(os.listdir(IMAGE_DIR))
    print(f"Successfully downloaded {downloaded_count} out of {len(products_data)} images.")
    if downloaded_count < len(products_data):
        print("There might be a persistent network issue. Please check the errors above.")

if __name__ == "__main__":
    main()
    