"""Tests for apify_client.py — uses unittest.mock, no real API calls."""
import pytest
from unittest.mock import patch, MagicMock

import opportunity_os.apify_client as ac


@pytest.fixture(autouse=True)
def reset_api_key_cache():
    ac._get_api_key.cache_clear()
    yield
    ac._get_api_key.cache_clear()


def test_run_actor_returns_items_on_success():
    mock_run = {"defaultDatasetId": "ds123"}
    mock_items = [{"title": "job1"}, {"title": "job2"}]
    mock_actor_instance = MagicMock()
    mock_actor_instance.call.return_value = mock_run
    mock_dataset_instance = MagicMock()
    mock_dataset_instance.list_items.return_value = MagicMock(items=mock_items)
    mock_client = MagicMock()
    mock_client.actor.return_value = mock_actor_instance
    mock_client.dataset.return_value = mock_dataset_instance

    with patch.object(ac, "_load_apify_key", return_value="test-key"), \
         patch("opportunity_os.apify_client.ApifyClient", return_value=mock_client):
        result = ac.run_actor("some/actor", {"key": "val"})
    assert result == mock_items


def test_run_actor_returns_empty_on_error():
    with patch.object(ac, "_load_apify_key", return_value="test-key"), \
         patch("opportunity_os.apify_client.ApifyClient", side_effect=Exception("boom")):
        result = ac.run_actor("some/actor", {})
    assert result == []


def test_fetch_linkedin_jobs_returns_int():
    mock_items = [{"title": "job"} for _ in range(5)]
    with patch.object(ac, "run_actor", return_value=mock_items):
        count = ac.fetch_linkedin_jobs("fintech", "Venezuela")
    assert count == 5


def test_fetch_g2_reviews_computes_neg_rate():
    mock_items = [
        {"rating": 1, "cons": "too expensive"},
        {"rating": 5, "cons": ""},
        {"rating": 2, "cons": "bad support"},
        {"rating": 4, "cons": ""},
    ]
    with patch.object(ac, "run_actor", return_value=mock_items):
        result = ac.fetch_g2_reviews("fintech")
    assert abs(result["neg_rate"] - 0.5) < 0.01
    assert "too expensive" in result["top_complaints"]
    assert "bad support" in result["top_complaints"]


def test_fetch_g2_reviews_returns_empty_dict_on_no_items():
    with patch.object(ac, "run_actor", return_value=[]):
        result = ac.fetch_g2_reviews("fintech")
    assert result == {}


def test_run_actor_returns_empty_when_apify_client_none():
    with patch.object(ac, "ApifyClient", None), \
         patch.object(ac, "_load_apify_key", return_value="test-key"):
        result = ac.run_actor("some/actor", {})
    assert result == []


def test_run_actor_returns_empty_when_no_api_key():
    with patch.object(ac, "_load_apify_key", return_value=None):
        result = ac.run_actor("some/actor", {})
    assert result == []
