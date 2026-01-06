"""Tests for utility functions."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from firecrawl import load_api_key


class TestLoadApiKey:
    def test_load_from_env(self) -> None:
        with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "fc-test-key"}):
            assert load_api_key() == "fc-test-key"

    def test_load_from_env_with_whitespace(self) -> None:
        with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "  fc-test-key  \n"}):
            assert load_api_key() == "fc-test-key"

    def test_load_from_explicit_file(self, tmp_path: Path) -> None:
        key_file = tmp_path / "key.txt"
        key_file.write_text("fc-file-key")
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("FIRECRAWL_API_KEY", None)
            assert load_api_key(key_file) == "fc-file-key"

    def test_no_key_found(self, tmp_path: Path) -> None:
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("firecrawl.utils._KEY_PATHS", (tmp_path / "nonexistent",)),
        ):
            os.environ.pop("FIRECRAWL_API_KEY", None)
            with pytest.raises(ValueError, match="No API key found"):
                load_api_key()
