#!/usr/bin/env python3
"""
Clean up old system data:
- Remove duplicate database files
- Clear old log files
- Keep only the main trading_signals.db in backend
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

def cleanup_old_data():
    print("\n" + "="*80)
    print("ALPHAFORGE - SYSTEM CLEANUP")
    print("="*80 + "\n")
    
    removed_files = []
    kept_files = []
    
    # Define the main database to keep
    main_db = Path("trading_signals.db")
    
    # Remove duplicate databases
    duplicate_dbs = [
        "../trading_signals.db",  # Duplicate in root
        "trading.db"  # Old database
    ]
    
    for db_path in duplicate_dbs:
        db = Path(db_path)
        if db.exists():
            try:
                # Backup before removing
                backup_path = db.with_suffix(f'.db.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
                shutil.copy2(db, backup_path)
                os.remove(db)
                removed_files.append(str(db))
                print(f"✅ Removed duplicate: {db}")
                print(f"   (Backup saved as: {backup_path})")
            except Exception as e:
                print(f"❌ Error removing {db}: {e}")
    
    # Clear old log files
    log_files = [
        "scheduler.log",
        "signal_scheduler.log",
        "../signal_scheduler.log"
    ]
    
    for log_path in log_files:
        log = Path(log_path)
        if log.exists():
            try:
                # Archive log content before clearing
                archive_path = log.with_suffix(f'.log.archive.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
                shutil.copy2(log, archive_path)
                
                # Clear the log file
                with open(log, 'w') as f:
                    f.write(f"Log cleared on {datetime.now().isoformat()}\n")
                
                removed_files.append(f"{log} (cleared)")
                print(f"✅ Cleared log: {log}")
                print(f"   (Archive saved as: {archive_path})")
            except Exception as e:
                print(f"❌ Error clearing {log}: {e}")
    
    # Report
    print("\n" + "="*80)
    print("CLEANUP SUMMARY")
    print("="*80)
    print(f"\nMaintaining main database: {main_db.absolute()}")
    print(f"Files processed: {len(removed_files)}")
    
    if removed_files:
        print("\nCleaned up:")
        for f in removed_files:
            print(f"  - {f}")
    
    print("\n✅ Cleanup complete!")
    print("="*80 + "\n")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    cleanup_old_data()
