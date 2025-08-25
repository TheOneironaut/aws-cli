import uuid
import pytest


@pytest.fixture(scope="session")
def unique_suffix():
    # Keep names unique to avoid collisions
    return str(uuid.uuid4())[:8]
