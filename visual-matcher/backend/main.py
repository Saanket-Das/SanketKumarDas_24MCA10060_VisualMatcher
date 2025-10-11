import os
import json
import pickle
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # Import this to serve images
from sklearn.metrics.pairwise import cosine_similarity
from io import BytesIO
import uvicorn
from image_utils import get_feature_vector

# --- Initialize FastAPI ---
app = FastAPI()

# --- THIS IS THE NEW PART ---
# Mount a static directory to serve the downloaded images.
# The path "/images" will now point to your 'backend/database/images' folder.
app.mount("/images", StaticFiles(directory="database/images"), name="images")

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load Pre-calculated Data on Startup ---
DB_PATH = os.path.join('database', 'products.json')
FEATURES_PATH = os.path.join('database', 'features.pkl')

try:
    with open(DB_PATH, 'r') as f:
        products_data = {prod['id']: prod for prod in json.load(f)}
    
    with open(FEATURES_PATH, 'rb') as f:
        saved_data = pickle.load(f)
        product_ids = saved_data['ids']
        product_vectors = np.array(saved_data['vectors'])
    print("Successfully loaded product data and feature vectors.")
except Exception as e:
    print(f"FATAL ERROR: Could not load data files. Please run preprocess.py first. Error: {e}")
    exit()

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Visual Product Matcher API (Feature Vector) is running!"}

@app.post("/api/search")
async def search_similar_products(image_file: UploadFile = File(...)):
    image_bytes = await image_file.read()
    
    query_vector = get_feature_vector(BytesIO(image_bytes))
    if query_vector is None:
        raise HTTPException(status_code=400, detail="Could not process the uploaded image.")

    query_vector = query_vector.reshape(1, -1)

    # --- Matching Logic ---
    similarities = cosine_similarity(query_vector, product_vectors)[0]
    
    results = []
    for i, similarity_score in enumerate(similarities):
        product_id = product_ids[i]
        
        product_info = products_data.get(product_id)
        if product_info:
            result_item = product_info.copy()
            
            # --- THIS IS THE KEY CHANGE ---
            # Instead of the old URL, create a new URL pointing to OUR server.
            result_item['imageUrl'] = f"http://127.0.0.1:8000/images/{product_id}.jpg"
            
            result_item['similarity'] = float(similarity_score * 100)
            results.append(result_item)
            
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    return results[:20]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)