"""
Main entry point for the Multiagent LLM News system.
Supports single run and scheduled (continuous) modes.
"""

import logging
import argparse
import signal
import sys


def setup_logging(verbose: bool = False):
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("pipeline.log", encoding="utf-8")
        ]
    )


def run_once(args):
    """Run the scraper once and exit."""
    from agents.scraper_agent import ScraperAgent
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Multiagent LLM News - Single Run Mode")
    
    try:
        agent = ScraperAgent(config_path=args.config)
        result = agent.run(newsapi_count=args.newsapi_count, gnews_count=args.gnews_count)
        
        print("\n" + "="*60)
        print("  SCRAPER AGENT RUN COMPLETE")
        print("="*60)
        print(f"  Total articles fetched:  {result['totalFetched']}")
        print(f"  Unique sources selected: {result['uniqueSelected']}")
        print(f"  New articles stored:     {result['inserted']}")
        print(f"  Duplicates skipped:      {result['duplicates']}")
        print(f"  Errors:                  {result['errors']}")
        print("="*60)
        
        stats = agent.get_stats()
        if stats:
            print("\n  Database Statistics:")
            for status, count in stats.items():
                print(f"    {status}: {count}")
            print()
        
        agent.close()
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"\nERROR: {e}")
        return 1


def run_scheduler(args):
    """Run the orchestrator in scheduled mode."""
    from agents.orchestrator_agent import OrchestratorAgent, setup_signal_handlers
    import yaml
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Multiagent LLM News - Scheduled Mode")
    
    try:
        orchestrator = OrchestratorAgent(config_path=args.config)
        setup_signal_handlers(orchestrator)
        
        # Get interval from args or config
        interval = args.interval
        if interval is None:
            with open(args.config, 'r') as f:
                config = yaml.safe_load(f)
            interval = config.get('SCHEDULER', {}).get('INTERVAL_MINUTES', 15)
        
        print("\n" + "="*60)
        print("  ORCHESTRATOR AGENT - Scheduled Mode")
        print("="*60)
        print(f"  Interval: {interval} minutes")
        print("  Press Ctrl+C to stop")
        print("="*60 + "\n")
        
        orchestrator.start(
            interval_minutes=interval,
            run_immediately=not args.no_initial_run
        )
        orchestrator.wait()
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"\nERROR: {e}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Multiagent LLM News System"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration file"
    )
    
    # Scheduler mode arguments
    parser.add_argument(
        "--scheduler",
        action="store_true",
        help="Run in scheduled mode (continuous 15-min cycles)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Scheduler interval in minutes (default: from config.yaml)"
    )
    parser.add_argument(
        "--no-initial-run",
        action="store_true",
        help="Don't run pipeline immediately on scheduler start"
    )
    
    # Single run mode arguments
    parser.add_argument(
        "--newsapi-count",
        type=int,
        default=5,
        help="Number of articles from NewsAPI (default: 5)"
    )
    parser.add_argument(
        "--gnews-count",
        type=int,
        default=2,
        help="Number of articles from GNews (default: 2)"
    )
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    
    if args.scheduler:
        return run_scheduler(args)
    else:
        return run_once(args)


if __name__ == "__main__":
    sys.exit(main())
