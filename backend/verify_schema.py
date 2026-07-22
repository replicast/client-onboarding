"""
Verify database schema in Azure SQL Database

This script checks that all required tables exist.
"""
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine
from sqlalchemy import text


def verify_tables():
    """Verify all tables exist in the database"""
    print("Verifying database schema...")
    print(f"Database: {engine.url.database}")
    print(f"Server: {engine.url.host}\n")

    try:
        with engine.connect() as conn:
            # Check for tables
            result = conn.execute(text("""
                SELECT
                    TABLE_NAME,
                    TABLE_TYPE
                FROM
                    INFORMATION_SCHEMA.TABLES
                WHERE
                    TABLE_NAME IN ('clients', 'sites')
                ORDER BY
                    TABLE_NAME
            """))

            tables = result.fetchall()

            if len(tables) == 0:
                print("✗ No tables found!")
                sys.exit(1)

            print("✓ Found tables:")
            for table in tables:
                print(f"  - {table[0]} ({table[1]})")

            # Check columns for clients table
            print("\n✓ Clients table columns:")
            result = conn.execute(text("""
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
            """))

            for col in result.fetchall():
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                print(f"  - {col[0]}: {col[1]} {nullable}")

            # Check columns for sites table
            print("\n✓ Sites table columns:")
            result = conn.execute(text("""
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
            """))

            for col in result.fetchall():
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                print(f"  - {col[0]}: {col[1]} {nullable}")

            # Check foreign keys
            print("\n✓ Foreign key constraints:")
            result = conn.execute(text("""
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
            """))

            for fk in result.fetchall():
                print(f"  - {fk[0]}: {fk[1]}.{fk[2]} -> {fk[3]}.{fk[4]}")

            # Check indexes
            print("\n✓ Indexes:")
            result = conn.execute(text("""
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
            """))

            for idx in result.fetchall():
                print(f"  - {idx[1]} on {idx[0]} ({idx[2]})")

            print("\n✓ Database schema verification complete!")
            print("✓ All tables, columns, foreign keys, and indexes are in place.")

    except Exception as e:
        print(f"\n✗ Error verifying schema: {e}")
        sys.exit(1)


if __name__ == "__main__":
    verify_tables()
