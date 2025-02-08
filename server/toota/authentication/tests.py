# from django.test import TestCase
# from django.core.files.uploadedfile import SimpleUploadedFile
# from rest_framework.test import APIClient
# from rest_framework import status
# from .models import DriverCheck
# from datetime import datetime, timedelta
# import os

# class DriverCheckVerificationTest(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.test_name = "Jane Smith"

#         # Create a mock driver's license image
#         self.image_path = "mock_driver_license.png"
#         with open(self.image_path, "wb") as f:
#             f.write(os.urandom(1024))  # Mock binary content for the test

#         self.uploaded_image = SimpleUploadedFile(
#             name=self.image_path,
#             content=open(self.image_path, "rb").read(),
#             content_type="image/png"
#         )

#         # Define the test URL (update to your endpoint URL if needed)
#         self.url = "/auth/driver-check/"

#     def tearDown(self):
#         if os.path.exists(self.image_path):
#             os.remove(self.image_path)

#     def test_successful_verification(self):
#         """Test verification with a valid name and mock driver's license image."""
#         data = {
#             "name": self.test_name,
#             "uploaded_image": self.uploaded_image
#         }

#         response = self.client.post(self.url, data, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("Verification successful", response.data.get("message"))

#     def test_expired_document(self):
#         """Test verification fails for expired documents."""
#         # Simulate expired document in mock verification logic
#         DriverCheck.objects.create(
#             name=self.test_name,
#             uploaded_image=self.uploaded_image,
#             expiry_date=datetime.now() - timedelta(days=1)  # Expired yesterday
#         )

#         data = {
#             "name": self.test_name,
#             "uploaded_image": self.uploaded_image
#         }

#         response = self.client.post(self.url, data, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("Document expired", response.data.get("message"))

#     def test_failed_name_match(self):
#         """Test verification fails when name does not match."""
#         data = {
#             "name": "Invalid Name",
#             "uploaded_image": self.uploaded_image
#         }

#         response = self.client.post(self.url, data, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("Name does not match", response.data.get("message"))

#     def test_rate_limiting(self):
#         """Test rate limiting for verification attempts."""
#         data = {
#             "name": self.test_name,
#             "uploaded_image": self.uploaded_image
#         }

#         # Simulate 3 attempts in a day
#         for _ in range(3):
#             response = self.client.post(self.url, data, format='multipart')

#         # Fourth attempt should be rate-limited
#         response = self.client.post(self.url, data, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
#         self.assertIn("Rate limit exceeded", response.data.get("message"))


from cryptography.fernet import Fernet

# Generate a secure encryption key
key = Fernet.generate_key()
print("Your encryption key:", key.decode())
