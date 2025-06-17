import os
import unittest
from unittest.mock import patch, MagicMock
from purviewcli.client._domain import Domain


class TestDomainClient(unittest.TestCase):
    """Unit tests for the Domain client"""

    def setUp(self):
        """Set up test environment"""
        self.test_endpoint = "https://test.purview.azure.com"
        self.test_token = "dummy_token"
        
        # Create an instance with explicit values
        self.domain_client = Domain(self.test_endpoint, self.test_token)

    @patch('purviewcli.client._domain.requests.post')
    def test_create_domain(self, mock_post):
        """Test create_domain method"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"name": "test-domain", "friendlyName": "Test Domain"}
        mock_post.return_value = mock_response
        
        # Call the method
        result = self.domain_client.create_domain("test-domain", "Test Domain", "Test description")
        
        # Verify the result
        self.assertEqual(result["name"], "test-domain")
        self.assertEqual(result["friendlyName"], "Test Domain")
        
        # Verify the mock was called with expected parameters
        url = f"{self.test_endpoint}/catalog/api/domains"
        headers = {
            "Authorization": f"Bearer {self.test_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "name": "test-domain", 
            "friendlyName": "Test Domain", 
            "description": "Test description"
        }
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], url)
        self.assertEqual(kwargs["headers"], headers)
        self.assertEqual(kwargs["json"], payload)

    @patch('purviewcli.client._domain.requests.get')
    def test_list_domains(self, mock_get):
        """Test list_domains method"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"value": [{"name": "domain1"}, {"name": "domain2"}]}
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.domain_client.list_domains()
        
        # Verify the result
        self.assertEqual(len(result["value"]), 2)
        
        # Verify the mock was called with expected parameters
        url = f"{self.test_endpoint}/catalog/api/domains"
        headers = {
            "Authorization": f"Bearer {self.test_token}",
            "Content-Type": "application/json"
        }
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], url)
        self.assertEqual(kwargs["headers"], headers)

    @patch('purviewcli.client._domain.requests.get')
    def test_get_domain(self, mock_get):
        """Test get_domain method"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"name": "test-domain", "friendlyName": "Test Domain"}
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.domain_client.get_domain("test-domain")
        
        # Verify the result
        self.assertEqual(result["name"], "test-domain")
        
        # Verify the mock was called with expected parameters
        url = f"{self.test_endpoint}/catalog/api/domains/test-domain"
        headers = {
            "Authorization": f"Bearer {self.test_token}",
            "Content-Type": "application/json"
        }
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], url)
        self.assertEqual(kwargs["headers"], headers)


if __name__ == "__main__":
    unittest.main()
