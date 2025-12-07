import os
import sys
from database.database import Base, engine

print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")

try:
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")
except Exception as e:
    print(f"Error creating tables: {e}")
    sys.exit(1)
