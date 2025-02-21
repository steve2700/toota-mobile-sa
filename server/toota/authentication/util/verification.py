import requests
from typing import Dict, Any
from django.conf import settings

class IDAnalyzerService:
    def __init__(self):
        self.base_url = "https://api2.idanalyzer.com/scan"
        self.api_key = settings.ID_ANALYZER_API_KEY
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-API-KEY": self.api_key
        }

    def verify_identity(self, document_url: str, face_url: str) -> Dict[str, Any]:
        """
        Verify identity using ID Analyzer API
        """
        payload = {
            "document": document_url,
            "face": face_url,
            "profile": settings.PROFILE_ID
        }

        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"ID Analyzer API request failed: {str(e)}")

# serializers.py