#!/usr/bin/env python3
"""
Database Migration Script for Themed Animation Platform

This script applies database migrations to PostgreSQL.
It tracks applied migrations and ensures idempotent execution.

Requirements: 2.2, 2.3, 9.1, 9.2
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from datetime import datetime
from pathlib import Path
from typing import List, Tuple
import argparse


class MigrationManager:
    """Manages database migrations"""
    
    def __init__(self, connection_string: str):
        """
        Initialize migration manager
        
        Args:
            connection_string: PostgreSQL connection string
                Format: postgresql://user:password@host:port/database
        """
        self.connection_string = connection_string
        self.migrations_dir = Path(__file__).parent / 'migrations'
        
    def connect(self):
        """Establish database connection"""
        try:
            return psycopg2.connect(self.connection_string)
        except psycopg2.Error as e:
            print(f"Error connecting to database: {e}")
            sys.exit(1)
    
    def ensure_migrations_table(self, conn):
        """Create migrations tracking table if it doesn't exist"""
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id SERIAL PRIMARY KEY,
                    migration_name VARCHAR(255) UNIQUE NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    checksum VARCHAR(64)
                )
            """)
            conn.commit()
            print("✓ Migrations tracking table ready")
    
    def get_applied_migrations(self, conn) -> List[str]:
        """Get list of already applied migrations"""
        with conn.cursor() as cur:
            cur.execute("SELECT migration_name FROM schema_migrations ORDER BY migration_name")
            return [row[0] for row in cur.fetchall()]
    
    def get_pending_migrations(self, applied: List[str]) -> List[Tuple[str, Path]]:
        """Get list of migrations that haven't been applied yet"""
        if not self.migrations_dir.exists():
            print(f"Error: Migrations directory not found: {self.migrations_dir}")
            sys.exit(1)
        
        all_migrations = sorted([
            (f.stem, f) for f in self.migrations_dir.glob('*.sql')
        ])
        
        pending = [
            (name, path) for name, path in all_migrations 
            if name not in applied
        ]
        
        return pending
    
    def apply_migration(self, conn, name: str, path: Path):
        """Apply a single migration"""
        print(f"\nApplying migration: {name}")
        
        # Read migration file
        with open(path, 'r') as f:
            migration_sql = f.read()
        
        try:
            with conn.cursor() as cur:
                # Execute migration
                cur.execute(migration_sql)
                
                # Record migration
                cur.execute(
                    "INSERT INTO schema_migrations (migration_name) VALUES (%s)",
                    (name,)
                )
                
                conn.commit()
                print(f"✓ Successfully applied: {name}")
                
        except psycopg2.Error as e:
            conn.rollback()
            print(f"✗ Error applying migration {name}: {e}")
            raise
    
    def migrate(self, dry_run: bool = False):
        """Run all pending migrations"""
        print("=" * 60)
        print("Themed Animation Platform - Database Migration")
        print("=" * 60)
        
        conn = self.connect()
        
        try:
            # Ensure migrations table exists
            self.ensure_migrations_table(conn)
            
            # Get applied and pending migrations
            applied = self.get_applied_migrations(conn)
            pending = self.get_pending_migrations(applied)
            
            print(f"\nApplied migrations: {len(applied)}")
            print(f"Pending migrations: {len(pending)}")
            
            if not pending:
                print("\n✓ Database is up to date!")
                return
            
            if dry_run:
                print("\n[DRY RUN] Would apply the following migrations:")
                for name, _ in pending:
                    print(f"  - {name}")
                return
            
            # Apply pending migrations
            print("\nApplying pending migrations...")
            for name, path in pending:
                self.apply_migration(conn, name, path)
            
            print("\n" + "=" * 60)
            print(f"✓ Successfully applied {len(pending)} migration(s)")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ Migration failed: {e}")
            sys.exit(1)
        finally:
            conn.close()
    
    def status(self):
        """Show migration status"""
        print("=" * 60)
        print("Migration Status")
        print("=" * 60)
        
        conn = self.connect()
        
        try:
            self.ensure_migrations_table(conn)
            
            applied = self.get_applied_migrations(conn)
            pending = self.get_pending_migrations(applied)
            
            print("\nApplied Migrations:")
            if applied:
                for name in applied:
                    print(f"  ✓ {name}")
            else:
                print("  (none)")
            
            print("\nPending Migrations:")
            if pending:
                for name, _ in pending:
                    print(f"  ○ {name}")
            else:
                print("  (none)")
            
            print(f"\nTotal: {len(applied)} applied, {len(pending)} pending")
            
        finally:
            conn.close()
    
    def rollback(self, migration_name: str):
        """
        Rollback a specific migration
        
        Note: This requires a corresponding rollback SQL file
        """
        print(f"Rolling back migration: {migration_name}")
        
        rollback_file = self.migrations_dir / f"{migration_name}_rollback.sql"
        
        if not rollback_file.exists():
            print(f"Error: Rollback file not found: {rollback_file}")
            sys.exit(1)
        
        conn = self.connect()
        
        try:
            with open(rollback_file, 'r') as f:
                rollback_sql = f.read()
            
            with conn.cursor() as cur:
                cur.execute(rollback_sql)
                cur.execute(
                    "DELETE FROM schema_migrations WHERE migration_name = %s",
                    (migration_name,)
                )
                conn.commit()
            
            print(f"✓ Successfully rolled back: {migration_name}")
            
        except psycopg2.Error as e:
            conn.rollback()
            print(f"✗ Error rolling back migration: {e}")
            sys.exit(1)
        finally:
            conn.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Database migration tool for Themed Animation Platform'
    )
    
    parser.add_argument(
        'command',
        choices=['migrate', 'status', 'rollback'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--connection-string',
        '-c',
        help='PostgreSQL connection string',
        default=os.environ.get('DATABASE_URL', 'postgresql://localhost/themed_animation')
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without applying changes'
    )
    
    parser.add_argument(
        '--migration',
        '-m',
        help='Migration name (for rollback command)'
    )
    
    args = parser.parse_args()
    
    manager = MigrationManager(args.connection_string)
    
    if args.command == 'migrate':
        manager.migrate(dry_run=args.dry_run)
    elif args.command == 'status':
        manager.status()
    elif args.command == 'rollback':
        if not args.migration:
            print("Error: --migration required for rollback command")
            sys.exit(1)
        manager.rollback(args.migration)


if __name__ == '__main__':
    main()
