import os
from pathlib import Path

import pytest


FIXTURES_PATH = Path(__file__).parent.absolute() / "fixtures"


@pytest.fixture(scope="session")
def apiclient_client_kwargs():
    return dict(endpoint_url="http://localhost:5000")


@pytest.fixture(scope="session")
def apiclient_session_kwargs():
    return dict(
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
        aws_session_token="testing",
        region_name="us-east-1",
    )


@pytest.fixture(scope="session")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
