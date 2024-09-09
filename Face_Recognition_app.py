import streamlit as st
import cv2
import numpy as np
import torch
import pickle
import faiss
from torchvision import transforms
from facenet_pytorch import InceptionResnetV1, MTCNN

# Load the model
model = InceptionResnetV1(pretrained='vggface2').eval()

# Load FAISS index
index = faiss.read_index('/kaggle/working/faiss_index.index')

# Load embeddings and labels
with open('lfw_embeddings.pkl', 'rb') as f:
    all_embeddings = pickle.load(f)
with open('labels.pkl', 'rb') as f:
    labels = pickle.load(f)  

# Define preprocessing function
def preprocess_image(img):
    # Convert image to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Resize image to 160x160
    img = cv2.resize(img, (160, 160))
    
    # Convert image to tensor
    img = torch.tensor(img, dtype=torch.float32)
    img = img.permute(2, 0, 1)  # Change to (C, H, W)
    img = img.unsqueeze(0)  # Add batch dimension
    
    # Normalize image
    img = (img / 255.0 - 0.5) / 0.5
    return img

# Define function for face recognition
def recognize_face(uploaded_file):
    # Load and preprocess image
    img = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)
    img_tensor = preprocess_image(img)
    
    # Generate face embedding
    with torch.no_grad():
        query_embedding = model(img_tensor).numpy().flatten()
    
    # Search for similar faces
    D, I = index.search(np.expand_dims(query_embedding, axis=0), k=5)  # Top 5 matches
    
    # Retrieve the closest label
    closest_index = I[0][0]
    closest_label = labels.get(closest_index, 'Unknown')  # Use get() for safety
    return closest_label

# Streamlit UI
st.title("Face Recognition System")
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Recognize face
    result = recognize_face(uploaded_file)
    
    # Display result
    st.write(f"Closest match: {result}")
