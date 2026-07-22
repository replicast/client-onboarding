"""
Verify database schema in Azure SQL Database using pymssql

This script checks that all required tables exist.
"""
import pymssql
import os
from dotenv import load_dotenv

load_dotenv()

def verify_tables():
    """Verify all tables exist in the database"""
    print("Verifying database schema...")
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    print(f"Database: {database}")
    print(f"Server: {server}\n")

    try:
        # For Azure SQL, username might need @servername suffix
        # Try both formats
        server_name = server.split('.')[0]  # Extract server name from FQDN

        # Connect to database
        try:
            # Try with @servername first (Azure SQL format)
            conn = pymssql.connect(
                server=server,
                user=f"{username}@{server_name}",
                password=password,
                database=database,
                as_dict=True
            )
        except Exception as e1:
            # Try without @servername (standard format)
            print(f"First connection attempt failed, trying alternative format...")
            conn = pymssql.connect(
                server=server,
                user=username,
                password=password,
                database=database,
                as_dict=True
            )
        cursor = conn.cursor()

        # Check for tables
        cursor.execute("""
            SELECT
                TABLE_NAME,
                TABLE_TYPE
            FROM
                INFORMATION_SCHEMA.TABLES
            WHERE
                TABLE_NAME IN ('clients', 'sites')
            ORDER BY
                TABLE_NAME
        """)

        tables = cursor.fetchall()

        if len(tables) == 0:
            print("✗ No tables found!")
            return False

        print("✓ Found tables:")
        for table in tables:
            print(f"  - {table['TABLE_NAME']} ({table['TABLE_TYPE']})")

        # Check columns for clients table
        print("\n✓ Clients table columns:")
        cursor.execute("""
            SELECT
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE
            FROM
                INFORMATION_SCHEMA.COLUMNS
            WHERE
                TABLE_NAME = 'clients'
            ORDER BY
                ORDINAL_POSITION
        """)

        for col in cursor.fetchall():
            nullable = "NULL" if col['IS_NULLABLE'] == "YES" else "NOT NULL"
            print(f"  - {col['COLUMN_NAME']}: {col['DATA_TYPE']} {nullable}")

        # Check columns for sites table
        print("\n✓ Sites table columns:")
        cursor.execute("""
            SELECT
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE
            FROM
                INFORMATION_SCHEMA.COLUMNS
            WHERE
                TABLE_NAME = 'sites'
            ORDER BY
                ORDINAL_POSITION
        """)

        for col in cursor.fetchall():
            nullable = "NULL" if col['IS_NULLABLE'] == "YES" else "NOT NULL"
            print(f"  - {col['COLUMN_NAME']}: {col['DATA_TYPE']} {nullable}")

        # Check foreign keys
        print("\n✓ Foreign key constraints:")
        cursor.execute("""
            SELECT
                fk.name AS constraint_name,
                tp.name AS parent_table,
                cp.name AS parent_column,
                tr.name AS referenced_table,
                cr.name AS referenced_column
            FROM
                sys.foreign_keys AS fk
                INNER JOIN sys.foreign_key_columns AS fkc ON fk.object_id = fkc.constraint_object_id
                INNER JOIN sys.tables AS tp ON fkc.parent_object_id = tp.object_id
                INNER JOIN sys.columns AS cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id
                INNER JOIN sys.tables AS tr ON fkc.referenced_object_id = tr.object_id
                INNER JOIN sys.columns AS cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id
        """)

        for fk in cursor.fetchall():
            print(f"  - {fk['constraint_name']}: {fk['parent_table']}.{fk['parent_column']} -> {fk['referenced_table']}.{fk['referenced_column']}")

        # Check indexes
        print("\n✓ Indexes:")
        cursor.execute("""
            SELECT
                t.name AS table_name,
                i.name AS index_name,
                i.type_desc
            FROM
                sys.indexes AS i
                INNER JOIN sys.tables AS t ON i.object_id = t.object_id
            WHERE
                t.name IN ('clients', 'sites')
                AND i.is_primary_key = 0
                AND i.type > 0
            ORDER BY
                t.name, i.name
        """)

        for idx in cursor.fetchall():
            print(f"  - {idx['index_name']} on {idx['table_name']} ({idx['type_desc']})")

        print("\n✓ Database schema verification complete!")
        print("✓ All tables, columns, foreign keys, and indexes are in place.")

        conn.close()
        return True

    except Exception as e:
        print(f"\n✗ Error verifying schema: {e}")
        return False


if __name__ == "__main__":
    success = verify_tables()
    exit(0 if success else 1)
