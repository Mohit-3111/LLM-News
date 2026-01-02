"""
Agent 2: Orchestrator & Scheduler Agent
The brain of the operation - triggers 15-minute cycles, manages workflow, coordinates agents.
"""

import logging
import signal
import sys
import yaml
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Add parent directory to path for imports
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.scraper_agent import ScraperAgent
from database.mongodb import MongoDBManager

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    Orchestrates the news pipeline with scheduled execution.
    
    Pipeline stages:
    1. Scrape - Fetch news from APIs
    2. Curate - LLM summarization (future)
    3. Generate Image - Create visuals (future)
    4. Publish - Post to platforms (future)
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the orchestrator with configuration.
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.config = self._load_config(config_path)
        self.config_path = config_path
        self.scheduler: Optional[BackgroundScheduler] = None
        self.is_running = False
        self.pipeline_status = {
            "last_run": None,
            "last_result": None,
            "runs_count": 0,
            "errors_count": 0
        }
        
        # Pipeline stage handlers (will be populated as agents are added)
        self.pipeline_stages = {
            "scrape": self._run_scraper,
            # "curate": self._run_curator,      # Future
            # "generate_image": self._run_image_gen,  # Future
            # "publish": self._run_publisher,   # Future
        }
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            logger.info("Orchestrator configuration loaded")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def _run_scraper(self) -> Dict[str, Any]:
        """Execute the scraper agent."""
        logger.info("Pipeline Stage: SCRAPE - Starting")
        try:
            scraper_config = self.config.get("SCRAPER", {})
            newsapi_count = scraper_config.get("NEWSAPI_COUNT", 5)
            gnews_count = scraper_config.get("GNEWS_COUNT", 2)
            
            agent = ScraperAgent(config_path=self.config_path)
            result = agent.run(newsapi_count=newsapi_count, gnews_count=gnews_count)
            agent.close()
            
            logger.info(f"Pipeline Stage: SCRAPE - Complete. "
                       f"Fetched {result['totalFetched']}, Stored {result['inserted']}")
            return {"stage": "scrape", "success": True, "result": result}
        except Exception as e:
            logger.error(f"Pipeline Stage: SCRAPE - Failed: {e}")
            return {"stage": "scrape", "success": False, "error": str(e)}
    
    def run_pipeline(self) -> Dict[str, Any]:
        """
        Execute the full news pipeline.
        Currently only runs the scraper, but designed for future expansion.
        
        Returns:
            Dictionary with pipeline execution results
        """
        start_time = datetime.utcnow()
        logger.info("="*60)
        logger.info("PIPELINE EXECUTION STARTED")
        logger.info(f"Time: {start_time.isoformat()}")
        logger.info("="*60)
        
        results = {
            "start_time": start_time.isoformat(),
            "stages": {},
            "success": True
        }
        
        # Execute each active pipeline stage
        for stage_name, stage_handler in self.pipeline_stages.items():
            try:
                stage_result = stage_handler()
                results["stages"][stage_name] = stage_result
                
                if not stage_result.get("success", False):
                    results["success"] = False
                    logger.warning(f"Stage '{stage_name}' failed, continuing pipeline...")
            except Exception as e:
                logger.error(f"Unexpected error in stage '{stage_name}': {e}")
                results["stages"][stage_name] = {"success": False, "error": str(e)}
                results["success"] = False
        
        # Update pipeline status
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        results["end_time"] = end_time.isoformat()
        results["duration_seconds"] = duration
        
        self.pipeline_status["last_run"] = end_time.isoformat()
        self.pipeline_status["last_result"] = results
        self.pipeline_status["runs_count"] += 1
        if not results["success"]:
            self.pipeline_status["errors_count"] += 1
        
        logger.info("="*60)
        logger.info(f"PIPELINE EXECUTION COMPLETE")
        logger.info(f"Duration: {duration:.2f}s | Success: {results['success']}")
        logger.info("="*60)
        
        return results
    
    def _scheduled_pipeline_run(self):
        """Wrapper for scheduled pipeline execution with error handling."""
        try:
            self.run_pipeline()
        except Exception as e:
            logger.error(f"Scheduled pipeline run failed: {e}")
            self.pipeline_status["errors_count"] += 1
    
    def start(self, interval_minutes: int = None, run_immediately: bool = None):
        """
        Start the scheduler for periodic pipeline execution.
        
        Args:
            interval_minutes: Minutes between runs (default from config)
            run_immediately: Whether to run pipeline immediately on start
        """
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        # Get settings from config or use overrides
        scheduler_config = self.config.get("SCHEDULER", {})
        interval = interval_minutes or scheduler_config.get("INTERVAL_MINUTES", 15)
        run_on_start = run_immediately if run_immediately is not None else scheduler_config.get("RUN_ON_START", True)
        
        logger.info(f"Starting Orchestrator Scheduler")
        logger.info(f"  Interval: {interval} minutes")
        logger.info(f"  Run on start: {run_on_start}")
        
        # Create and configure scheduler
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            self._scheduled_pipeline_run,
            trigger=IntervalTrigger(minutes=interval),
            id="news_pipeline",
            name="News Pipeline",
            replace_existing=True
        )
        
        # Start scheduler
        self.scheduler.start()
        self.is_running = True
        
        logger.info("Scheduler started successfully")
        
        # Run immediately if configured
        if run_on_start:
            logger.info("Running initial pipeline...")
            self.run_pipeline()
        
        # Calculate next run time
        job = self.scheduler.get_job("news_pipeline")
        if job and job.next_run_time:
            logger.info(f"Next scheduled run: {job.next_run_time}")
    
    def stop(self):
        """Stop the scheduler gracefully."""
        if self.scheduler and self.is_running:
            logger.info("Stopping scheduler...")
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("Scheduler stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status."""
        status = {
            "is_running": self.is_running,
            "pipeline_status": self.pipeline_status,
            "active_stages": list(self.pipeline_stages.keys())
        }
        
        if self.scheduler and self.is_running:
            job = self.scheduler.get_job("news_pipeline")
            if job and job.next_run_time:
                status["next_run"] = job.next_run_time.isoformat()
        
        return status
    
    def wait(self):
        """Block until interrupted (for running as main process)."""
        import time
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            self.stop()


def setup_signal_handlers(orchestrator: OrchestratorAgent):
    """Setup graceful shutdown handlers."""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        orchestrator.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


# For running as a standalone script
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    orchestrator = OrchestratorAgent()
    setup_signal_handlers(orchestrator)
    
    print("\n" + "="*60)
    print("  ORCHESTRATOR AGENT - Scheduled Mode")
    print("="*60)
    print("  Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    orchestrator.start()
    orchestrator.wait()
