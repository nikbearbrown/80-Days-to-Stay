"""
Tests for company name normalization utilities.
Run: pytest tests/test_normalize.py -v
"""

import pytest
from scrapers.common.normalize import normalize_company_name, epoch_ms_to_iso8601


class TestNormalizeCompanyName:
    """Tests for normalize_company_name()."""

    def test_basic_name(self):
        assert normalize_company_name("Databricks") == "databricks"

    def test_strip_inc(self):
        assert normalize_company_name("Databricks, Inc.") == "databricks"
        assert normalize_company_name("Databricks Inc") == "databricks"
        assert normalize_company_name("Databricks, Inc") == "databricks"

    def test_strip_llc(self):
        assert normalize_company_name("Acme LLC") == "acme"
        assert normalize_company_name("Acme, LLC.") == "acme"

    def test_strip_corp(self):
        assert normalize_company_name("Mega Corp.") == "mega"
        assert normalize_company_name("Mega Corporation") == "mega"

    def test_strip_ltd(self):
        assert normalize_company_name("British Ltd.") == "british"
        assert normalize_company_name("British Limited") == "british"

    def test_strip_lp(self):
        assert normalize_company_name("Fund L.P.") == "fund"
        assert normalize_company_name("Fund LP") == "fund"

    def test_remove_spaces_and_special_chars(self):
        assert normalize_company_name("Coca Cola Company") == "cocacola"
        assert normalize_company_name("Ben & Jerry's") == "benjerrys"

    def test_remove_hyphens(self):
        assert normalize_company_name("Proof-Point") == "proofpoint"

    def test_lowercase(self):
        assert normalize_company_name("DISCORD") == "discord"
        assert normalize_company_name("Discord") == "discord"

    def test_already_normalized(self):
        assert normalize_company_name("roblox") == "roblox"

    def test_empty_string(self):
        assert normalize_company_name("") == ""

    def test_whitespace(self):
        assert normalize_company_name("  Databricks  ") == "databricks"

    def test_multiple_suffixes(self):
        # Only the matching suffix should be removed
        assert normalize_company_name("Company Co.") == "company"


class TestEpochMsToIso8601:
    """Tests for epoch_ms_to_iso8601()."""

    def test_known_timestamp(self):
        # 2025-02-15T00:00:00Z in epoch ms
        result = epoch_ms_to_iso8601(1739577600000)
        assert "2025-02-15" in result

    def test_zero_epoch(self):
        result = epoch_ms_to_iso8601(0)
        assert "1970-01-01" in result

    def test_returns_iso_format(self):
        result = epoch_ms_to_iso8601(1707850000000)
        # Should be parseable as ISO 8601
        from datetime import datetime
        datetime.fromisoformat(result)  # should not raise
