# main.py
from collector import DataCollector
import json
from datetime import datetime
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_collector():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        collector = DataCollector(config)
        data = collector.collect()
        
        output_file = f'output_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Data collection completed. Results saved to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_collector()
    sys.exit(0 if success else 1)