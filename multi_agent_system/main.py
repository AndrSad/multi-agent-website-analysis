"""
Main entry point for the Multi-Agent Website Analysis System

This script provides a command-line interface and can also be used to run the system.
"""

import sys
import os
import argparse
import logging
from typing import Optional

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import config


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(config.log_file, mode='a')
        ]
    )


def run_api_server():
    """Run the Flask API server."""
    try:
        config.validate_config()
        logging.info("Starting API server...")
        
        # Import here to avoid circular imports
        from api.main import app
        flask_config = config.get_flask_config()
        app.run(
            host=flask_config['host'],
            port=flask_config['port'],
            debug=flask_config['debug']
        )
    except Exception as e:
        logging.error(f"Failed to start API server: {str(e)}")
        sys.exit(1)


def analyze_website_cli(url: str, analysis_type: str = "full"):
    """Analyze a website using command line interface."""
    try:
        config.validate_config()
        logging.info(f"Starting {analysis_type} analysis of {url}")
        
        # Import here to avoid circular imports
        from core.orchestrator import MultiAgentOrchestrator
        orchestrator = MultiAgentOrchestrator()
        
        if analysis_type == "quick":
            result = orchestrator.get_quick_analysis(url)
        else:
            result = orchestrator.analyze_website(url)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
        
        print(f"✅ Analysis completed for {url}")
        print(f"📊 Status: {result['status']}")
        print(f"⏰ Timestamp: {result['timestamp']}")
        
        if analysis_type == "quick":
            print("\n📋 Quick Analysis Results:")
            print(result['quick_analysis'])
        else:
            print("\n📋 Full Analysis Results:")
            print(result['analysis_results'])
        
    except Exception as e:
        logging.error(f"Analysis failed: {str(e)}")
        print(f"❌ Analysis failed: {str(e)}")
        sys.exit(1)


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Website Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --url https://example.com                    # Full analysis
  python main.py --url https://example.com --quick           # Quick analysis
  python main.py --server                                     # Start API server
  python main.py --scrape https://example.com                # Only scraping
        """
    )
    
    parser.add_argument(
        '--url', 
        type=str, 
        help='Website URL to analyze'
    )
    
    parser.add_argument(
        '--quick', 
        action='store_true', 
        help='Perform quick analysis (only classification and summary)'
    )
    
    parser.add_argument(
        '--server', 
        action='store_true', 
        help='Start the API server'
    )
    
    parser.add_argument(
        '--scrape', 
        type=str, 
        help='Only scrape website data (provide URL)'
    )
    
    parser.add_argument(
        '--verbose', 
        action='store_true', 
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        config.log_level = "DEBUG"
    setup_logging()
    
    # Handle different modes
    if args.server:
        run_api_server()
    elif args.scrape:
        try:
            config.validate_config()
            # Import here to avoid circular imports
            from core.orchestrator import MultiAgentOrchestrator
            orchestrator = MultiAgentOrchestrator()
            result = orchestrator.scraping_tool.scrape_website(args.scrape)
            
            if 'error' in result:
                print(f"❌ Scraping failed: {result['error']}")
                sys.exit(1)
            
            print(f"✅ Scraping completed for {args.scrape}")
            print(f"📄 Title: {result.get('title', 'N/A')}")
            print(f"📝 Description: {result.get('meta_description', 'N/A')}")
            print(f"🔗 Links found: {len(result.get('links', []))}")
            print(f"🖼️ Images found: {len(result.get('images', []))}")
            print(f"📋 Forms found: {len(result.get('forms', []))}")
            
        except Exception as e:
            logging.error(f"Scraping failed: {str(e)}")
            print(f"❌ Scraping failed: {str(e)}")
            sys.exit(1)
    elif args.url:
        analysis_type = "quick" if args.quick else "full"
        analyze_website_cli(args.url, analysis_type)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
