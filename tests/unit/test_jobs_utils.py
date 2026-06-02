import pytest
from pydantic import ValidationError

from surfaced.jobs.schemas import JobFilters
from surfaced.jobs.utilities import next_cursor_b64_decode, next_cursor_b64_encode


def test_jobfilters_defaults():
    filters = JobFilters(q="test string", limit=15)
    assert filters.q == "test string"
    assert filters.location is None
    assert filters.limit == 15
    assert filters.cursor is None


def test_jobfilters_validation_check():

    with pytest.raises(ValidationError) as exc_info:
        JobFilters(limit=101)

    assert "Input should be less than or equal to 100" in str(exc_info.value)


def test_b64_encoding():

    id = "42"
    expected_token = "NDI="

    token = next_cursor_b64_encode(id)

    assert token == expected_token
    assert isinstance(token, str)

    expected_bytes = expected_token.encode()
    assert isinstance(expected_bytes, bytes)

    decoded_id = next_cursor_b64_decode(expected_bytes)

    assert decoded_id == id
    assert isinstance(decoded_id, str)


def test_b64_encoding_malformed_data():

    invalid_cursor_bytes = b"INVALIDCURSORDATA!"

    with pytest.raises(Exception):
        _ = next_cursor_b64_decode(invalid_cursor_bytes)
