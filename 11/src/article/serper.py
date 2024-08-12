import json
import logging
from http import client as http_client
from http.client import HTTPSConnection, HTTPResponse
from typing import Optional

from .config import config


class SerperService:
    """Service to find sites that match your search using Serper API"""

    SERPER_URL: str = "google.serper.dev"

    def request_to_serper(self, query: str) -> Optional[dict]:
        """Send a search request to the Serper API and return the parsed data"""
        try:
            connection = self._make_connection()
            payload = self._build_payload(query=query)
            response = self._get_response(connection=connection, payload=payload)
            print("type of response", type(response))
            data = self._parse_response(response)
            print("type of data", type(data))
            return data
        except Exception as e:
            logging.error(f"Error in SerperService: {e}")
            return None

    def _make_connection(self) -> HTTPSConnection:
        """Establishes an HTTPS connection to the Serper API"""
        return http_client.HTTPSConnection(host=self.SERPER_URL)

    @staticmethod
    def _build_payload(query: str) -> str:
        """Creates the payload for the search request"""
        return json.dumps({"q": query})

    def _get_response(self, connection, payload) -> HTTPResponse:
        """Sends the request and retrieves the response from the Serper API"""
        connection.request("POST", "/search", payload, self._headers)
        response = connection.getresponse()
        return response

    @property
    def _headers(self):
        """Headers required for the Serper API request"""
        return {
            "X-API-KEY": config.SERPER_API_KEY,
            "Content-Type": "application/json"
        }

    @staticmethod
    def _parse_response(response) -> dict:
        """Parses the response from the Serper API"""
        data = response.read()
        data = json.loads(data.decode("utf-8"))
        return data