#To run, navigate to memechain-api/tests and enter "py.test -s"
#The -s flag prints any messages in the std i/o, so prints become usable. 

import falcon
from falcon import testing
import pytest

from api import app

@pytest.fixture
def client():
	return testing.TestClient(app)

# pytest will inject the object returned by the `client` function
# as an additional parameter.
def test_api_call(client):
	
	known_result = 0
	response = client.simulate_get('/api/getheight')
	queried_result = response.json['result']
	assert known_result == queried_result

