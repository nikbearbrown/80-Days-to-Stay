"""
Tests for the unified schema validator.
Run: pytest tests/test_schema_validator.py -v
"""

from scrapers.common.schema_validator import validate_job_record, validate_batch


def _make_valid_job(**overrides):
    """Helper to create a valid job record with optional overrides."""
    job = {
        "job_id": "12345",
        "title": "Software Engineer",
        "company_name": "Acme Corp",
        "company_slug": "acmecorp",
        "ats_source": "greenhouse",
        "source_url": "https://boards.greenhouse.io/acmecorp/jobs/12345",
        "apply_url": "https://boards.greenhouse.io/acmecorp/jobs/12345",
        "location": "San Francisco, CA",
        "department": "Engineering",
        "employment_type": "Full-time",
        "date_posted": "2025-02-15T00:00:00+00:00",
        "description_text": "We are looking for a software engineer...",
        "description_html": "<p>We are looking for a software engineer...</p>",
        "salary_range": "$120,000 - $160,000",
        "metadata": {
            "scraped_at": "2025-02-16T12:00:00+00:00",
            "scraper_version": "1.0.0",
            "extraction_status": "success",
            "raw_response_hash": "abc123def456",
        },
    }
    job.update(overrides)
    return job


class TestValidateJobRecord:
    """Tests for validate_job_record()."""

    def test_valid_record_passes(self):
        job = _make_valid_job()
        is_valid, errors = validate_job_record(job)
        assert is_valid is True
        assert errors == []

    def test_missing_required_field_fails(self):
        job = _make_valid_job()
        del job["title"]
        is_valid, errors = validate_job_record(job)
        assert is_valid is False
        assert any("title" in e for e in errors)

    def test_empty_required_field_fails(self):
        job = _make_valid_job(title="")
        is_valid, errors = validate_job_record(job)
        assert is_valid is False
        assert any("title" in e and "empty" in e for e in errors)

    def test_invalid_ats_source_fails(self):
        job = _make_valid_job(ats_source="invalid_ats")
        is_valid, errors = validate_job_record(job)
        assert is_valid is False
        assert any("ats_source" in e for e in errors)

    def test_valid_ats_sources(self):
        for source in ["greenhouse", "lever", "workday", "icims", "taleo"]:
            job = _make_valid_job(ats_source=source)
            is_valid, _ = validate_job_record(job)
            assert is_valid is True, f"ats_source '{source}' should be valid"

    def test_invalid_employment_type_fails(self):
        job = _make_valid_job(employment_type="Freelance")
        is_valid, errors = validate_job_record(job)
        assert is_valid is False
        assert any("employment_type" in e for e in errors)

    def test_valid_employment_types(self):
        for emp_type in ["Full-time", "Part-time", "Contract", "Intern", ""]:
            job = _make_valid_job(employment_type=emp_type)
            is_valid, _ = validate_job_record(job)
            assert is_valid is True, f"employment_type '{emp_type}' should be valid"

    def test_invalid_date_format_fails(self):
        job = _make_valid_job(date_posted="Feb 15, 2025")
        is_valid, errors = validate_job_record(job)
        assert is_valid is False
        assert any("date_posted" in e for e in errors)

    def test_empty_date_is_acceptable(self):
        job = _make_valid_job(date_posted="")
        is_valid, _ = validate_job_record(job)
        assert is_valid is True

    def test_missing_metadata_fails(self):
        job = _make_valid_job()
        del job["metadata"]
        is_valid, errors = validate_job_record(job)
        assert is_valid is False
        assert any("metadata" in e for e in errors)

    def test_missing_metadata_field_fails(self):
        job = _make_valid_job()
        del job["metadata"]["scraper_version"]
        is_valid, errors = validate_job_record(job)
        assert is_valid is False
        assert any("scraper_version" in e for e in errors)

    def test_invalid_extraction_status_fails(self):
        job = _make_valid_job()
        job["metadata"]["extraction_status"] = "unknown"
        is_valid, errors = validate_job_record(job)
        assert is_valid is False
        assert any("extraction_status" in e for e in errors)

    def test_wrong_type_for_field_fails(self):
        job = _make_valid_job(job_id=12345)  # should be str, not int
        is_valid, errors = validate_job_record(job)
        assert is_valid is False
        assert any("job_id" in e for e in errors)

    def test_optional_field_wrong_type_fails(self):
        job = _make_valid_job(location=123)  # should be str, not int
        is_valid, errors = validate_job_record(job)
        assert is_valid is False
        assert any("location" in e for e in errors)

    def test_optional_field_missing_is_ok(self):
        job = _make_valid_job()
        del job["location"]  # optional field can be absent
        is_valid, _ = validate_job_record(job)
        assert is_valid is True


class TestValidateBatch:
    """Tests for validate_batch()."""

    def test_all_valid_batch(self):
        jobs = [_make_valid_job(job_id=str(i)) for i in range(5)]
        report = validate_batch(jobs)
        assert report["total"] == 5
        assert report["valid"] == 5
        assert report["invalid"] == 0
        assert report["batch_passed"] is True
        assert report["has_valid_records"] is True
        assert report["partial_success"] is False

    def test_mixed_batch_non_strict(self):
        jobs = [
            _make_valid_job(job_id="1"),
            _make_valid_job(job_id=""),  # empty required field
            _make_valid_job(job_id="3"),
        ]
        report = validate_batch(jobs)  # strict=False by default
        assert report["total"] == 3
        assert report["valid"] == 2
        assert report["invalid"] == 1
        assert report["batch_passed"] is True  # non-strict: passes if any valid
        assert report["has_valid_records"] is True
        assert report["partial_success"] is True

    def test_mixed_batch_strict(self):
        jobs = [
            _make_valid_job(job_id="1"),
            _make_valid_job(job_id=""),  # empty required field
            _make_valid_job(job_id="3"),
        ]
        report = validate_batch(jobs, strict=True)
        assert report["batch_passed"] is False  # strict: fails if any invalid
        assert report["strict"] is True
        assert report["has_valid_records"] is True
        assert report["partial_success"] is True

    def test_empty_batch(self):
        report = validate_batch([])
        assert report["total"] == 0
        assert report["pass_rate"] == "N/A"
        assert report["batch_passed"] is True
        assert report["has_valid_records"] is False
