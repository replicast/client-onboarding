"""
Test Azure SQL Database connection with different methods
"""
import pymssql
import os
from dotenv import load_dotenv

load_dotenv()

server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

print("Testing Azure SQL Database connection...")
print(f"Server: {server}")
print(f"Database: {database}")
print(f"Username: {username}")
print()

# Extract server name for Azure format
server_name = server.split('.')[0]

# Test different connection formats
connection_attempts = [
    {
        "description": "Format 1: username@servername",
        "user": f"{username}@{server_name}",
        "server": server,
        "port": 1433
    },
    {
        "description": "Format 2: Plain username",
        "user": username,
        "server": server,
        "port": 1433
    },
    {
        "description": "Format 3: username@FQDN",
        "user": f"{username}@{server}",
        "server": server,
        "port": 1433
    },
]

for i, attempt in enumerate(connection_attempts, 1):
    print(f"Attempt {i}: {attempt['description']}")
    print(f"  User: {attempt['user']}")
    print(f"  Server: {attempt['server']}")
    print(f"  Port: {attempt['port']}")

    try:
        conn = pymssql.connect(
            server=attempt['server'],
            user=attempt['user'],
            password=password,
            database=database,
            port=attempt['port'],
            as_dict=True
        )

        print("  ✓ CONNECTION SUCCESSFUL!")

        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION AS version")
        result = cursor.fetchone()
        print(f"  ✓ SQL Server version: {result['version'][:100]}...")

        # Check tables
        cursor.execute("""
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME IN ('clients', 'sites')
        """)
        tables = cursor.fetchall()
        print(f"  ✓ Found {len(tables)} tables: {[t['TABLE_NAME'] for t in tables]}")

        conn.close()
        print("\n✓✓✓ Database connection verified! ✓✓✓\n")
        exit(0)

    except Exception as e:
        print(f"  ✗ Failed: {str(e)[:200]}")
        print()

print("✗ All connection attempts failed")
exit(1)
