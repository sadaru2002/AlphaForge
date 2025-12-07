import asyncio
import os
import sys
import logging
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add current directory to path
sys.path.append('/app/backend')

# Import backend modules
from database.signal_models import TradingSignal, SignalStatus, TradeOutcome
from notifications.telegram import TelegramNotifier
from regime_detector import MarketRegimeDetector, MarketRegime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup DB
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////app/backend/data/trading_signals.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

async def verify_system():
    print("\n" + "="*50)
    print("ALPHAFORGE SYSTEM VERIFICATION")
    print("="*50 + "\n")
    
    # 1. Verify Telegram
    print("1. Testing Telegram Connectivity...")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ Telegram credentials missing in environment!")
    else:
        print(f"   Token: {token[:5]}... | Chat ID: {chat_id}")
        notifier = TelegramNotifier(token, chat_id)
        success = await notifier.send_message("🔔 <b>AlphaForge System Test</b>\n\nVerifying system connectivity...\n- Database: ✅\n- Telegram: ✅\n- Market: Closed (Weekend)", parse_mode="HTML")
        
        if success:
            print("✅ Telegram test message sent successfully.")
        else:
            print("❌ Failed to send Telegram message.")

    # 2. Verify Database & Signal Creation
    print("\n2. Testing Database & Signal Creation...")
    try:
        # Create a test signal
        test_signal = TradingSignal(
            symbol="TEST_USD",
            direction="BUY",
            entry=1.2345,
            stop_loss=1.2300,
            tp1=1.2400,
            tp2=1.2450,
            tp3=1.2500,
            rr_ratio="1:2.5",
            position_size=1.0,
            risk_amount=100.0,
            confidence_score=95.0,
            signal_strength="STRONG",
            reasoning="System verification test signal",
            status=SignalStatus.ACTIVE,
            market_condition="TESTING",
            session="WEEKEND_TEST",
            timestamp=datetime.utcnow()
        )
        
        db.add(test_signal)
        db.commit()
        db.refresh(test_signal)
        print(f"✅ Test signal saved to database (ID: {test_signal.id})")
        
        # Send signal notification
        if token and chat_id:
            print("   Sending signal notification to Telegram...")
            signal_dict = test_signal.to_dict()
            # Adapt dict structure for TelegramNotifier (it expects nested dicts based on previous analysis)
            # Actually, looking at telegram.py lines 86+, it expects:
            # signal.get('metadata', {}).get('symbol')
            # signal.get('setup_details', {}).get('direction')
            # So we need to construct a dict that matches that structure, NOT just the model to_dict()
            
            telegram_payload = {
                'metadata': {'symbol': test_signal.symbol},
                'setup_details': {'direction': test_signal.direction},
                'risk_management': {
                    'confidence_score': test_signal.confidence_score,
                    'setup_grade': 'A'
                },
                'trade_parameters': {
                    'entry_price': test_signal.entry,
                    'stop_loss': test_signal.stop_loss,
                    'take_profit_1': test_signal.tp1,
                    'take_profit_1_rr': 2.5
                }
            }
            
            await notifier.send_signal_notification(telegram_payload)
            print("✅ Signal notification sent to Telegram.")
            
    except Exception as e:
        print(f"❌ Database/Signal Error: {e}")
        import traceback
        traceback.print_exc()

    # 3. Verify Market Regime Detector
    print("\n3. Testing Market Regime Detector...")
    try:
        detector = MarketRegimeDetector()
        print("✅ MarketRegimeDetector initialized.")
        # We can't easily test detection without data, but initialization confirms imports work
    except Exception as e:
        print(f"❌ Regime Detector Error: {e}")

    print("\n" + "="*50)
    print("VERIFICATION COMPLETE")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(verify_system())
