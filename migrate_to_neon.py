#!/usr/bin/env python3
"""
scripts/migrate_to_neon.py
Database migration script: SQLite → Neon Postgres

Handles schema transformation and data transfer with integrity verification.
"""

import os
import json
import sqlite3
import sys
from datetime import datetime

try:
    import psycopg2
    from psycopg2.extras import execute_values
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("Warning: psycopg2 not installed. Install with: pip install psycopg2-binary")


class NeonMigrator:
    """Handles migration from SQLite to Neon Postgres."""

    def __init__(self, sqlite_path: str, neon_url: str):
        self.sqlite_path = sqlite_path
        self.neon_url = neon_url
        self.data_export = {}

    def export_sqlite(self):
        """Export all data from SQLite to JSON."""
        print(f"[1/5] Exporting data from SQLite: {self.sqlite_path}")

        if not os.path.exists(self.sqlite_path):
            raise FileNotFoundError(f"SQLite database not found: {self.sqlite_path}")

        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]

        print(f"   Found {len(tables)} tables: {', '.join(tables)}")

        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()

            self.data_export[table] = [dict(row) for row in rows]
            print(f"   - {table}: {len(rows)} rows")

        conn.close()

        # Save to JSON backup
        backup_path = f"migration_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_path, 'w') as f:
            json.dump(self.data_export, f, indent=2, default=str)

        print(f"   ✓ Backup saved: {backup_path}")
        return self.data_export

    def create_postgres_schema(self, pg_conn):
        """Create Postgres schema (converted from SQLite)."""
        print("[2/5] Creating Postgres schema...")

        cursor = pg_conn.cursor()

        # Drop existing tables (careful!)
        print("   Dropping existing tables...")
        cursor.execute("""
            DROP TABLE IF EXISTS prompt_tags CASCADE;
            DROP TABLE IF EXISTS versions CASCADE;
            DROP TABLE IF EXISTS variants CASCADE;
            DROP TABLE IF EXISTS tags CASCADE;
            DROP TABLE IF EXISTS prompt_model CASCADE;
        """)

        # Create tables
        print("   Creating prompt_model table...")
        cursor.execute("""
            CREATE TABLE prompt_model (
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL CHECK (LENGTH(text) <= 10000),
                tags_json TEXT DEFAULT '[]',
                q_score REAL NOT NULL CHECK (q_score >= 0 AND q_score <= 1),
                features_json TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                parent_id INTEGER REFERENCES prompt_model(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        print("   Creating tags table...")
        cursor.execute("""
            CREATE TABLE tags (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        print("   Creating variants table...")
        cursor.execute("""
            CREATE TABLE variants (
                id SERIAL PRIMARY KEY,
                prompt_id INTEGER NOT NULL REFERENCES prompt_model(id) ON DELETE CASCADE,
                variant_type TEXT NOT NULL CHECK (variant_type IN ('concise', 'neutral', 'commanding')),
                text TEXT NOT NULL,
                q_score REAL CHECK (q_score >= 0 AND q_score <= 1),
                metrics_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        print("   Creating indices...")
        cursor.execute("CREATE INDEX idx_prompts_qscore ON prompt_model(q_score);")
        cursor.execute("CREATE INDEX idx_prompts_created ON prompt_model(created_at);")
        cursor.execute("CREATE INDEX idx_variants_prompt ON variants(prompt_id);")

        pg_conn.commit()
        print("   ✓ Schema created")

    def import_to_postgres(self, pg_conn):
        """Import data from JSON export to Postgres."""
        print("[3/5] Importing data to Postgres...")

        cursor = pg_conn.cursor()

        # Import prompt_model
        if 'prompt_model' in self.data_export:
            prompts = self.data_export['prompt_model']
            print(f"   Importing {len(prompts)} prompts...")

            for prompt in prompts:
                cursor.execute("""
                    INSERT INTO prompt_model (id, text, tags_json, q_score, features_json, version, parent_id, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    prompt['id'],
                    prompt['text'],
                    prompt['tags_json'],
                    prompt['q_score'],
                    prompt['features_json'],
                    prompt['version'],
                    prompt['parent_id'],
                    prompt['created_at']
                ))

            # Reset sequence
            cursor.execute("SELECT setval('prompt_model_id_seq', (SELECT MAX(id) FROM prompt_model));")
            print(f"   ✓ Imported {len(prompts)} prompts")

        # Import tags
        if 'tags' in self.data_export:
            tags = self.data_export['tags']
            print(f"   Importing {len(tags)} tags...")

            for tag in tags:
                cursor.execute("INSERT INTO tags (id, name, created_at) VALUES (%s, %s, %s)",
                              (tag['id'], tag['name'], tag.get('created_at')))

            cursor.execute("SELECT setval('tags_id_seq', (SELECT MAX(id) FROM tags));")
            print(f"   ✓ Imported {len(tags)} tags")

        pg_conn.commit()

    def verify_migration(self, pg_conn):
        """Verify data integrity after migration."""
        print("[4/5] Verifying migration...")

        cursor = pg_conn.cursor()
        errors = []

        # Check row counts
        for table in ['prompt_model', 'tags', 'variants']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            pg_count = cursor.fetchone()[0]
            sqlite_count = len(self.data_export.get(table, []))

            if pg_count != sqlite_count:
                errors.append(f"Row count mismatch in {table}: SQLite={sqlite_count}, Postgres={pg_count}")
            else:
                print(f"   ✓ {table}: {pg_count} rows match")

        # Check Q score checksums
        cursor.execute("SELECT SUM(q_score) FROM prompt_model")
        pg_sum = cursor.fetchone()[0] or 0

        sqlite_sum = sum(p['q_score'] for p in self.data_export.get('prompt_model', []))

        if abs(pg_sum - sqlite_sum) > 0.01:
            errors.append(f"Q score checksum mismatch: SQLite={sqlite_sum:.4f}, Postgres={pg_sum:.4f}")
        else:
            print(f"   ✓ Q score checksum: {pg_sum:.4f}")

        if errors:
            print("   ✗ Migration verification FAILED:")
            for error in errors:
                print(f"     - {error}")
            return False
        else:
            print("   ✓ Migration verified successfully!")
            return True

    def run(self):
        """Execute full migration."""
        print("\n" + "=" * 70)
        print("NEON POSTGRES MIGRATION")
        print("=" * 70 + "\n")

        if not PSYCOPG2_AVAILABLE:
            print("✗ psycopg2 not installed. Cannot connect to Postgres.")
            print("  Install with: pip install psycopg2-binary")
            return False

        try:
            # Export SQLite
            self.export_sqlite()

            # Connect to Postgres
            print(f"\n[Connecting to Neon Postgres...]")
            pg_conn = psycopg2.connect(self.neon_url)
            print("   ✓ Connected")

            # Create schema
            self.create_postgres_schema(pg_conn)

            # Import data
            self.import_to_postgres(pg_conn)

            # Verify
            success = self.verify_migration(pg_conn)

            pg_conn.close()

            if success:
                print("\n" + "=" * 70)
                print("✓ MIGRATION COMPLETED SUCCESSFULLY")
                print("=" * 70)
                return True
            else:
                print("\n" + "=" * 70)
                print("✗ MIGRATION COMPLETED WITH ERRORS")
                print("=" * 70)
                return False

        except Exception as e:
            print(f"\n✗ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description='Migrate SQLite to Neon Postgres')
    parser.add_argument('--sqlite', default='api/prompts.db', help='Path to SQLite database')
    parser.add_argument('--neon-url', help='Neon Postgres connection string')
    parser.add_argument('--dry-run', action='store_true', help='Export only, no import')

    args = parser.parse_args()

    if not args.neon_url and not args.dry_run:
        # Try to get from environment
        args.neon_url = os.getenv('DATABASE_URL')

        if not args.neon_url:
            print("Error: Neon URL required. Provide via --neon-url or DATABASE_URL env var")
            print("Example: DATABASE_URL=postgresql://user:pass@host/db")
            sys.exit(1)

    migrator = NeonMigrator(args.sqlite, args.neon_url)

    if args.dry_run:
        print("DRY RUN: Exporting data only...")
        migrator.export_sqlite()
        print("\n✓ Dry run complete. Review backup file before actual migration.")
    else:
        success = migrator.run()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
