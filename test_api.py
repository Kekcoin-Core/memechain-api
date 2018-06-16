# To run, navigate to memechain-api/tests and enter "py.test -s"
# The -s flag prints any messages in the std i/o, so prints become usable.

from falcon import testing
import pytest

from api import app


@pytest.fixture
def client():
    return testing.TestClient(app)

# pytest will inject the object returned by the `client` function
# as an additional parameter.


def test_get_memechain_height(client):

    known_result = 0
    response = client.simulate_get('/api/getheight')
    queried_result = response.json['result']
    assert known_result == queried_result


def test_get_meme_data_by_height(client):
    # TODO: Once the database can be populated, define
    # the genesis meme data and run this test
    GENESIS_MEME_DATA = {}
    known_result = GENESIS_MEME_DATA
    test_height = 0
    response = client.simulate_get('/api/getmemedatabyheight/%i'
                                   % (test_height))
    queried_result = response.json['result']
    assert known_result == queried_result


def test_get_meme_data_by_hash(client):
    # TODO: Once the database can be populated, define
    # the genesis meme data test_hash and run this test
    GENESIS_MEME_DATA = {}
    known_result = GENESIS_MEME_DATA
    test_hash = 'Fill in test hash here...'
    response = client.simulate_get('/api/getmemedatabyhash/%s'
                                   % (test_hash))
    queried_result = response.json['result']
    assert known_result == queried_result


def test_get_meme_img_by_height(client):
    # TODO: Once the database can be populated, define
    # the genesis meme img and run this test
    GENESIS_MEME = None
    known_result = GENESIS_MEME
    test_height = 0
    response = client.simulate_get('/api/getmemeimgbyheight/%i'
                                   % (test_height))
    queried_result = response.json['result']
    assert known_result == queried_result


def test_get_meme_img_by_hash(client):
    # TODO: Once the database can be populated, define
    # the genesis meme img and run this test
    GENESIS_MEME = None
    known_result = GENESIS_MEME
    test_hash = 'Fill in test hash here...'
    response = client.simulate_get('/api/getmemeimgbyhash/%s'
                                   % (test_hash))
    queried_result = response.json['result']
    assert known_result == queried_result


def test_add_meme(client):
    response = client.simulate_post('/api/addmeme')
    # Check image written to local storage

    # Check image added to ipfs

    # Wait sufficient time for block to be staked,
    # then check existence in blockchain
