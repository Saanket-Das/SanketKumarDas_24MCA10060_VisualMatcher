import os
import json
import pickle
from tqdm import tqdm
from image_utils import get_feature_vector # Imports from our new file

DB_PATH = os.path.join('database', 'products.json')
IMAGE_DIR = os.path.join('database', 'images')
FEATURES_PATH = os.path.join('database', 'features.pkl')

def main():
    """Loads local images, calculates their feature vectors, and saves them to a file."""
    print("--- Starting OFFLINE Feature Vector Preprocessing ---")
    
    try:
        with open(DB_PATH, 'r') as f:
            products_data = json.load(f)
    except Exception as e:
        print(f"FATAL ERROR: Could not load {DB_PATH}. Reason: {e}")
        return

    vectors = []
    product_ids_with_vectors = []

    for product in tqdm(products_data, desc="Processing Local Images"):
        product_id = product['id']
        image_path = os.path.join(IMAGE_DIR, f"{product_id}.jpg")

        if os.path.exists(image_path):
            # Pass the local file path to our utility function to get the vector
            vector = get_feature_vector(image_path)
            if vector is not None:
                vectors.append(vector)
                product_ids_with_vectors.append(product_id)
        else:
            print(f"\nWarning: Image file not found for product ID {product_id} at {image_path}")

    print(f"\nSuccessfully created {len(vectors)} feature vectors from local files.")

    if vectors:
        data_to_save = {
            'ids': product_ids_with_vectors,
            'vectors': vectors
        }
        with open(FEATURES_PATH, 'wb') as f:
            pickle.dump(data_to_save, f)
        print(f"Feature vectors saved successfully to {FEATURES_PATH}")
    else:
        print("WARNING: No feature vectors were created. Did you run download_images.py first?")

if __name__ == "__main__":
    main()