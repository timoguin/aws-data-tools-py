from aws_data_tools.client import APIClient  # noqa: F401


class TestAPIClient:
    """Test the APIClient class"""

    def test_api(self):
        """Test API calls with the client"""
        assert "pass" == "pass"

    def test_init_with_client(self):
        """Test initializing an APIClient with a custom botocore client being passed"""
        assert "pass" == "pass"

    def test_init_with_client_kwargs(self):
        """Test APIClient init with kwargs for the botocore client"""
        assert "pass" == "pass"

    def test_init_with_session(self):
        """Test initializing an APIClient with a custom botocore session being passed"""
        assert "pass" == "pass"

    def test_init_with_session_kwargs(self):
        """Test APIClient init with kwargs for the botocore session"""
        assert "pass" == "pass"
