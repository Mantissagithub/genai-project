import os
import firebase_admin
from firebase_admin import credentials, storage
from dotenv import load_dotenv

load_dotenv()

cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET")

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'storageBucket': bucket_name
    })
    print(f"Successfully connected to Firebase project with bucket: {bucket_name}")

bucket = storage.bucket()

def upload_file_to_firebase(local_file_path, firebase_path=None):
    try:
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"File not found: {local_file_path}")
            
        if firebase_path is None:
            firebase_path = f"genai/{os.path.basename(local_file_path)}"
        else:
            if not firebase_path.startswith("genai/"):
                firebase_path = f"genai/{firebase_path}"
            
        blob = bucket.blob(firebase_path)
        blob.upload_from_filename(local_file_path)
        
        # Make the file publicly accessible
        blob.make_public()
        
        print(f"File uploaded successfully to {firebase_path}")
        return blob.public_url
    except Exception as e:
        print(f"Error uploading file to Firebase: {e}")
        return None