"""
AlphaForge Automated Signal Scheduler
Runs signal generation every 5 minutes with Gemini validation
"""

import schedule
import time
import logging
from datetime import datetime
import requests
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('signal_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")
SCHEDULE_INTERVAL = 5  # minutes
PAIRS = ['GBP_USD', 'XAU_USD', 'USD_JPY']

class SignalScheduler:
    def __init__(self):
        self.last_run = None
        self.total_signals_generated = 0
        self.total_runs = 0
        
    def generate_signals(self):
        """Generate signals for all pairs with Gemini validation"""
        try:
            self.total_runs += 1
            logger.info("="*80)
            logger.info(f"🔄 Starting scheduled signal generation cycle #{self.total_runs}")
            logger.info(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("="*80)
            
            # Call the enhanced signal generation endpoint
            # This endpoint automatically:
            # 1. Fetches M5/M15/H1 data
            # 2. Calculates indicators
            # 3. Runs multi-timeframe voting
            # 4. Detects regime
            # 5. Applies quality filters
            # 6. Calculates SL/TP
            # 7. Validates with Gemini AI (if API key configured)
            # 8. Saves to database
            
            response = requests.post(
                f"{API_BASE_URL}/api/signals/enhanced/generate",
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                
                signals_count = result.get('signals_generated', 0)
                self.total_signals_generated += signals_count
                
                logger.info(f"\n✅ Cycle complete!")
                logger.info(f"📊 Signals generated: {signals_count}")
                
                # Log each pair result
                if 'results' in result:
                    logger.info("\n📋 Pair-by-pair results:")
                    for pair_result in result['results']:
                        pair = pair_result['pair']
                        generated = pair_result['generated']
                        reason = pair_result.get('reason', 'N/A')
                        
                        if generated:
                            logger.info(f"  ✅ {pair}: SIGNAL GENERATED")
                        else:
                            logger.info(f"  ❌ {pair}: No signal - {reason}")
                
                # Log statistics
                if 'statistics' in result:
                    stats = result['statistics']
                    if 'strategy' in stats:
                        strategy = stats['strategy']
                        logger.info(f"\n📈 Strategy stats:")
                        logger.info(f"  - Total signals attempted: {strategy.get('total_signals', 0)}")
                        logger.info(f"  - Tradeable signals: {strategy.get('tradeable_signals', 0)}")
                        logger.info(f"  - Filter efficiency: {strategy.get('filter_efficiency', '0%')}")
                        logger.info(f"  - Regime filtered: {strategy.get('regime_filtered', 0)}")
                
                logger.info(f"\n📊 Session statistics:")
                logger.info(f"  - Total runs: {self.total_runs}")
                logger.info(f"  - Total signals generated: {self.total_signals_generated}")
                logger.info(f"  - Average signals per run: {self.total_signals_generated / self.total_runs:.2f}")
                
                self.last_run = datetime.now()
                
            else:
                logger.error(f"❌ API request failed with status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                
        except requests.exceptions.Timeout:
            logger.error("❌ Signal generation timeout (>120s)")
        except requests.exceptions.ConnectionError:
            logger.error("❌ Cannot connect to backend server. Is it running on port 5000?")
        except Exception as e:
            logger.error(f"❌ Error during signal generation: {e}")
            import traceback
            traceback.print_exc()
    
    def check_backend_health(self):
        """Check if backend server is running"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                logger.info(f"✅ Backend server is healthy")
                logger.info(f"   - Status: {health.get('status')}")
                logger.info(f"   - OANDA: {health.get('oanda')}")
                logger.info(f"   - Strategy: {health.get('strategy')}")
                return True
            else:
                logger.error(f"⚠️ Backend returned status code: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Backend health check failed: {e}")
            return False
    
    def start(self):
        """Start the scheduler"""
        logger.info("\n" + "="*80)
        logger.info("🚀 AlphaForge Automated Signal Scheduler")
        logger.info("="*80)
        logger.info(f"📡 Backend API: {API_BASE_URL}")
        logger.info(f"⏱️  Schedule: Every {SCHEDULE_INTERVAL} minutes")
        logger.info(f"💱 Pairs: {', '.join(PAIRS)}")
        logger.info(f"🤖 Gemini AI: Enabled (if API key configured)")
        logger.info("="*80 + "\n")
        
        # Check backend health
        logger.info("🔍 Checking backend server health...")
        if not self.check_backend_health():
            logger.error("\n❌ Backend server is not running!")
            logger.error("Please start the backend server first:")
            logger.error("  cd backend")
            logger.error("  python app.py")
            sys.exit(1)
        
        logger.info("\n✅ Backend server is running and healthy!")
        
        # Run immediately on start
        logger.info(f"\n⚡ Running initial signal generation...")
        self.generate_signals()
        
        # Schedule every 5 minutes
        schedule.every(SCHEDULE_INTERVAL).minutes.do(self.generate_signals)
        
        logger.info(f"\n⏰ Scheduler started! Next run in {SCHEDULE_INTERVAL} minutes...")
        logger.info("Press Ctrl+C to stop\n")
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n\n" + "="*80)
            logger.info("🛑 Scheduler stopped by user")
            logger.info(f"📊 Final statistics:")
            logger.info(f"   - Total runs: {self.total_runs}")
            logger.info(f"   - Total signals generated: {self.total_signals_generated}")
            logger.info("="*80)
            sys.exit(0)


if __name__ == "__main__":
    scheduler = SignalScheduler()
    scheduler.start()
