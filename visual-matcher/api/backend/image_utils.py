import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from io import BytesIO

# --- Model Configuration ---
# Load a pre-trained ResNet50 model, which is excellent for feature extraction.
model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
# Set the model to evaluation mode for better performance during inference.
model.eval()

# Define the specific image transformations that the ResNet50 model requires.
# Every image must be processed this way before being analyzed.
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def get_feature_vector(image_source):
    """
    Calculates a deep learning feature vector (a numerical "fingerprint") for an image.
    The source can be either a file path (string) or image bytes from an upload.
    """
    try:
        # Open the image from the provided source
        with Image.open(image_source) as image:
            image = image.convert('RGB')
            # Apply the transformations and add a batch dimension for the model
            image_tensor = preprocess(image).unsqueeze(0)

            # Disable gradient calculations for faster, more efficient inference
            with torch.no_grad():
                # Pass the image through the model to get its feature vector
                features = model(image_tensor)
            
            # Return the feature vector as a simple, one-dimensional array
            return features.numpy().flatten()
            
    except Exception as e:
        print(f"\nError processing image for feature extraction: {e}")
        return None