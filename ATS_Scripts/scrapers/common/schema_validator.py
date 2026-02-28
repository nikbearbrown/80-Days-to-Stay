"""
Validates scraper output against the unified job record schema.

Usage:
    from scrapers.common.schema_validator import validate_job_record, validate_batch

    is_valid, errors = validate_job_record(job_dict)
    report = validate_batch(list_of_jobs)
"""

from typing import Any, Dict, List, Tuple
from datetime import datetime

from .logger import get_logger

logger = get_logger("schema_validator", file=False)

# --- Unified Job Record Schema ---
# Defines required fields, types, and allowed values.

REQUIRED_FIELDS = {
    "job_id": str,
    "title": str,
    "company_name": str,
    "company_slug": str,
    "ats_source": str,
    "source_url": str,
}

OPTIONAL_FIELDS = {
    "apply_url": str,
    "location": str,
    "department": str,
    "employment_type": str,
    "date_posted": str,
    "description_text": str,
    "description_html": str,
    "salary_range": str,
}

METADATA_REQUIRED_FIELDS = {
    "scraped_at": str,
    "scraper_version": str,
    "extraction_status": str,
}

METADATA_OPTIONAL_FIELDS = {
    "raw_response_hash": str,
}

VALID_ATS_SOURCES = [
    "greenhouse", "lever", "ashby", "smartrecruiters", "workable",
    "bamboohr", "jazzhr", "workday", "icims", "taleo",
    "jobvite", "recruitee", "teamtailor", "avature",
    "sap_successfactors", "cornerstone",
]

VALID_EMPLOYMENT_TYPES = [
    "Full-time", "Part-time", "Contract", "Intern", "",
]

VALID_EXTRACTION_STATUSES = ["success", "error", "partial"]


def _is_iso8601(value: str) -> bool:
    """Check if a string is a valid ISO 8601 datetime."""
    if not value:
        return True  # empty/null dates are acceptable
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except (ValueError, AttributeError):
        return False


def validate_job_record(job: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a single job record against the unified schema.

    Args:
        job: A dictionary representing a job record.

    Returns:
        Tuple of (is_valid: bool, errors: list of error strings).
    """
    errors: List[str] = []

    # Check required fields
    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in job:
            errors.append(f"Missing required field: '{field}'")
        elif not isinstance(job[field], expected_type):
            errors.append(
                f"Field '{field}' should be {expected_type.__name__}, "
                f"got {type(job[field]).__name__}"
            )
        elif not job[field].strip():
            errors.append(f"Required field '{field}' is empty")

    # Check optional fields types (only when present)
    for field, expected_type in OPTIONAL_FIELDS.items():
        if field in job and not isinstance(job[field], expected_type):
            errors.append(
                f"Optional field '{field}' should be {expected_type.__name__}, "
                f"got {type(job[field]).__name__}"
            )

    # Check ats_source value
    if job.get("ats_source") and job["ats_source"] not in VALID_ATS_SOURCES:
        errors.append(
            f"Invalid ats_source: '{job['ats_source']}' "
            f"(valid: {VALID_ATS_SOURCES})"
        )

    # Check employment_type value
    if job.get("employment_type") and job["employment_type"] not in VALID_EMPLOYMENT_TYPES:
        errors.append(
            f"Invalid employment_type: '{job['employment_type']}' "
            f"(valid: {VALID_EMPLOYMENT_TYPES})"
        )

    # Check date_posted format
    if job.get("date_posted") and not _is_iso8601(job["date_posted"]):
        errors.append(
            f"Field 'date_posted' is not valid ISO 8601: '{job['date_posted']}'"
        )

    # Check metadata block
    metadata = job.get("metadata")
    if metadata is None:
        errors.append("Missing required field: 'metadata'")
    elif not isinstance(metadata, dict):
        errors.append(
            f"Field 'metadata' should be dict, got {type(metadata).__name__}"
        )
    else:
        for field, expected_type in METADATA_REQUIRED_FIELDS.items():
            if field not in metadata:
                errors.append(f"Missing required metadata field: '{field}'")
            elif not isinstance(metadata[field], expected_type):
                errors.append(
                    f"Metadata field '{field}' should be {expected_type.__name__}, "
                    f"got {type(metadata[field]).__name__}"
                )

        # Check optional metadata fields types (only when present)
        for field, expected_type in METADATA_OPTIONAL_FIELDS.items():
            if field in metadata and not isinstance(metadata[field], expected_type):
                errors.append(
                    f"Optional metadata field '{field}' should be "
                    f"{expected_type.__name__}, got {type(metadata[field]).__name__}"
                )

        # Validate scraped_at is ISO 8601
        if metadata.get("scraped_at") and not _is_iso8601(metadata["scraped_at"]):
            errors.append(
                f"Metadata 'scraped_at' is not valid ISO 8601: "
                f"'{metadata['scraped_at']}'"
            )

        # Validate extraction_status
        if (
            metadata.get("extraction_status")
            and metadata["extraction_status"] not in VALID_EXTRACTION_STATUSES
        ):
            errors.append(
                f"Invalid extraction_status: '{metadata['extraction_status']}'"
            )

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_batch(
    jobs: List[Dict[str, Any]], strict: bool = False
) -> Dict[str, Any]:
    """
    Validate a batch of job records and produce a summary report.

    Args:
        jobs: List of job record dictionaries.
        strict: If True, any single error fails the entire batch.

    Returns:
        Report dict with counts and per-job errors.
    """
    total = len(jobs)
    valid_count = 0
    invalid_count = 0
    all_errors: List[Dict[str, Any]] = []

    for i, job in enumerate(jobs):
        is_valid, errors = validate_job_record(job)
        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1
            all_errors.append({
                "index": i,
                "job_id": job.get("job_id", "UNKNOWN"),
                "errors": errors,
            })

    report = {
        "total": total,
        "valid": valid_count,
        "invalid": invalid_count,
        "pass_rate": f"{(valid_count / total * 100):.1f}%" if total > 0 else "N/A",
        "errors": all_errors,
        "batch_passed": invalid_count == 0 if strict else (valid_count > 0 or total == 0),
        "has_valid_records": valid_count > 0,
        "partial_success": valid_count > 0 and invalid_count > 0,
        "strict": strict,
    }

    if all_errors:
        logger.warning(
            "Validation: %d/%d records invalid (%.1f%% pass rate)",
            invalid_count,
            total,
            valid_count / total * 100 if total > 0 else 0,
        )
    else:
        logger.info("Validation: all %d records passed", total)

    return report
