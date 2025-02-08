import pytesseract
from PIL import Image
import face_recognition
import cv2
import numpy as np
from datetime import datetime
import re
from cryptography.fernet import Fernet
def extract_text(image_path):
    """
    Extract text from user uploaded document for validation 
    """
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)

def validate_expiry(expiry_date):
    """Validate user document expiry date"""
    if expiry_date and datetime.strptime(expiry_date, '%Y-%m-%d') < datetime.now():
        return False
    return True

def extract_expiry_date(image_path):
    """
    Extract expiry date from the text in an image using OCR.
    Assumes a standard format like 'Expiry Date: YYYY-MM-DD'.
    """
    image = Image.open(image_path)
    extracted_text = pytesseract.image_to_string(image)

    # Regex to find dates in common formats
    date_patterns = [
        r'\b(?:Expiry\s*Date[:\-]?\s*)(\d{4}-\d{2}-\d{2})\b',  # Format: YYYY-MM-DD
        r'\b(?:Expiry\s*Date[:\-]?\s*)(\d{2}/\d{2}/\d{4})\b',  # Format: DD/MM/YYYY
        r'\b(?:Expiry\s*Date[:\-]?\s*)(\d{2}-\d{2}-\d{4})\b',  # Format: DD-MM-YYYY
    ]

    for pattern in date_patterns:
        match = re.search(pattern, extracted_text, re.IGNORECASE)
        if match:
            extracted_date = match.group(1)
            try:
                # Normalize to YYYY-MM-DD
                if '/' in extracted_date:
                    extracted_date = datetime.strptime(extracted_date, '%d/%m/%Y').strftime('%Y-%m-%d')
                elif '-' in extracted_date and len(extracted_date.split('-')[0]) == 2:
                    extracted_date = datetime.strptime(extracted_date, '%d-%m-%Y').strftime('%Y-%m-%d')

                return extracted_date
            except ValueError:
                continue

    return None  # No valid expiry date found

def compare_faces(uploaded_image_path, reference_image_path):
    uploaded_image = face_recognition.load_image_file(uploaded_image_path)
    reference_image = face_recognition.load_image_file(reference_image_path)

    uploaded_encoding = face_recognition.face_encodings(uploaded_image)
    reference_encoding = face_recognition.face_encodings(reference_image)

    if uploaded_encoding and reference_encoding:
        return face_recognition.compare_faces([reference_encoding[0]], uploaded_encoding[0])
    return False


def detect_watermark(image_path):
    """
    Detects the presence of a watermark in the given image.

    Args:
        image_path: Path to the image file.

    Returns:
        True if a watermark is detected, False otherwise.
    """
    # Load the image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Apply edge detection to highlight watermark patterns
    edges = cv2.Canny(image, threshold1=50, threshold2=150)

    # Perform Hough Line Transformation to detect straight lines (common in watermarks)
    lines = cv2.HoughLines(edges, rho=1, theta=np.pi / 180, threshold=200)

    # If lines are detected, it's likely that a watermark exists
    if lines is not None and len(lines) > 5:  # Adjust threshold as needed
        return True
    return False



# Generate a symmetric key (do this once and store it securely)
# key = Fernet.generate_key()
# Store the key securely, e.g., in environment variables or a secret manager
SECRET_KEY = b'your-secure-key-from-above'  # Replace with your generated key

def encrypt_data(data):
    """
    Encrypts the given data using the Fernet symmetric encryption.

    Args:
        data: The data to encrypt (string).

    Returns:
        The encrypted data as a string.
    """
    fernet = Fernet(SECRET_KEY)
    encrypted_data = fernet.encrypt(data.encode('utf-8'))
    return encrypted_data.decode('utf-8')

def decrypt_data(encrypted_data):
    """
    Decrypts the given data.

    Args:
        encrypted_data: The encrypted data (string).

    Returns:
        The decrypted data as a string.
    """
    fernet = Fernet(SECRET_KEY)
    decrypted_data = fernet.decrypt(encrypted_data.encode('utf-8'))
    return decrypted_data.decode('utf-8')


def get_dynamic_threshold(user):
    """
    Return a fixed threshold for face matching.

    Args:
        user: The user object (not used in this simplified version).

    Returns:
        A float representing the fixed threshold (0.5).
    """
    return 0.5

