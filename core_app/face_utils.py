import torch
import numpy as np
from PIL import Image
from facenet_pytorch import InceptionResnetV1, MTCNN

# -----------------------------
# Global Model Initialization
# -----------------------------
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"✅ Using device: {DEVICE}")

# Load FaceNet
FACENET_MODEL = InceptionResnetV1(pretrained='vggface2').eval().to(DEVICE)

# Load MTCNN for detection & alignment
MTCNN_DETECTOR = MTCNN(
    image_size=160,
    margin=10,              # small margin helps crop slightly larger area
    min_face_size=40,       # ignore tiny detections
    thresholds=[0.7, 0.8, 0.9],
    post_process=True,
    device=DEVICE
)

print("✅ FaceNet + MTCNN models loaded successfully")


# -----------------------------
# Generate Face Embedding
# -----------------------------
def generate_face_embedding(image_path):
    """
    Detect face, align it and generate a 512-d embedding.
    Returns normalized vector list or None.
    """
    try:
        img = Image.open(image_path).convert("RGB")

        # Detect and align face
        face = MTCNN_DETECTOR(img)
        if face is None:
            print(f"❌ No face detected in image: {image_path}")
            return None

        # FaceNet expects normalized tensor in [-1,1], already handled by MTCNN
        with torch.no_grad():
            embedding = FACENET_MODEL(face.unsqueeze(0).to(DEVICE))
        embedding = embedding / embedding.norm(dim=1, keepdim=True)

        return embedding.cpu().numpy()[0].tolist()

    except Exception as e:
        print("❌ Error generating face embedding:", e)
        return None


# -----------------------------
# Compare Faces (Cosine Similarity)
# -----------------------------
def compare_faces(known_embedding, uploaded_embedding, threshold=0.65):
    """
    Compare embeddings using cosine similarity.
    Returns (is_match, confidence %).
    """
    try:
        known_vec = np.array(known_embedding, dtype=np.float32)
        uploaded_vec = np.array(uploaded_embedding, dtype=np.float32)

        # Normalize
        known_vec /= np.linalg.norm(known_vec)
        uploaded_vec /= np.linalg.norm(uploaded_vec)

        # Cosine similarity
        similarity = np.dot(known_vec, uploaded_vec)
        confidence = round(float(similarity) * 100, 2)

        # Match if above threshold
        is_match = similarity >= threshold
        print(f"🔍 Similarity: {similarity:.4f}, Confidence: {confidence}%, Match: {is_match}")
        return is_match, confidence

    except Exception as e:
        print("❌ Error comparing faces:", e)
        return False, 0.0