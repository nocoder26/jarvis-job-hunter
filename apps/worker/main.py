"""
Jarvis Job Hunter - Background Worker

This worker runs scheduled jobs for:
- Polling job sources (TheirStack, SerpApi)
- Enriching company data
- Running AI analysis on new jobs
"""

import schedule
import time
import logging
from datetime import datetime

from jobs.poll_theirstack import poll_theirstack
from jobs.poll_serpapi import poll_serpapi
from jobs.enrich_companies import enrich_companies
from jobs.analyze_jobs import analyze_new_jobs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_job_polling():
    """Poll all job sources."""
    logger.info("Starting job polling cycle...")

    try:
        # Poll TheirStack
        theirstack_count = poll_theirstack()
        logger.info(f"TheirStack: Found {theirstack_count} new jobs")
    except Exception as e:
        logger.error(f"TheirStack polling failed: {e}")

    try:
        # Poll SerpApi (Google Jobs)
        serpapi_count = poll_serpapi()
        logger.info(f"SerpApi: Found {serpapi_count} new jobs")
    except Exception as e:
        logger.error(f"SerpApi polling failed: {e}")

    logger.info("Job polling cycle complete")


def run_enrichment():
    """Enrich companies with additional data."""
    logger.info("Starting company enrichment...")

    try:
        enriched_count = enrich_companies()
        logger.info(f"Enriched {enriched_count} companies")
    except Exception as e:
        logger.error(f"Company enrichment failed: {e}")


def run_analysis():
    """Run AI analysis on new jobs."""
    logger.info("Starting AI analysis...")

    try:
        analyzed_count = analyze_new_jobs()
        logger.info(f"Analyzed {analyzed_count} jobs")
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")


def main():
    """Main entry point for the worker."""
    logger.info("Starting Jarvis Job Hunter Worker...")
    logger.info(f"Current time: {datetime.utcnow().isoformat()}")

    # Schedule jobs
    # Poll for new jobs every 15 minutes
    schedule.every(15).minutes.do(run_job_polling)

    # Enrich companies every 30 minutes
    schedule.every(30).minutes.do(run_enrichment)

    # Run AI analysis every 10 minutes
    schedule.every(10).minutes.do(run_analysis)

    # Run initial jobs on startup
    logger.info("Running initial job cycle...")
    run_job_polling()
    run_enrichment()
    run_analysis()

    # Keep running
    logger.info("Worker started. Running scheduled jobs...")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    main()
