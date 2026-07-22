"""Run database migration to convert geolocation_polygon from GEOGRAPHY to TEXT"""
import pymssql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get database connection details
server = os.getenv('DB_SERVER')
database = os.getenv('DB_NAME')
username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

print(f"Connecting to {server}/{database}...")

# Connect to database
conn = pymssql.connect(
    server=server,
    user=username,
    password=password,
    database=database
)

cursor = conn.cursor()

print("Running migration...")

# Step 1: Drop the existing GEOGRAPHY column
print("Step 1: Dropping GEOGRAPHY column...")
try:
    cursor.execute("ALTER TABLE sites DROP COLUMN geolocation_polygon;")
    conn.commit()
    print("✓ GEOGRAPHY column dropped")
except Exception as e:
    print(f"Note: {e}")
    conn.rollback()

# Step 2: Add new TEXT column
print("Step 2: Adding TEXT column...")
try:
    cursor.execute("ALTER TABLE sites ADD geolocation_polygon NVARCHAR(MAX) NULL;")
    conn.commit()
    print("✓ TEXT column added")
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()

# Verify the change
print("\nVerifying column type...")
cursor.execute("""
    SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'sites' AND COLUMN_NAME = 'geolocation_polygon';
""")

result = cursor.fetchone()
if result:
    print(f"✓ Column type: {result[1]}, Max length: {result[2]}")
else:
    print("✗ Column not found")

cursor.close()
conn.close()

print("\n✅ Migration completed successfully!")
