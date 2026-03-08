#!/usr/bin/env python3
"""
Database Schema Test Script

Tests the database schema to ensure all tables, indexes, and constraints
are properly created.

Requirements: 2.2, 2.3, 9.1, 9.2
"""

import sys
import psycopg2
from typing import List, Tuple
import argparse


class SchemaValidator:
    """Validates database schema"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.errors = []
        self.warnings = []
    
    def connect(self):
        """Establish database connection"""
        try:
            return psycopg2.connect(self.connection_string)
        except psycopg2.Error as e:
            print(f"Error connecting to database: {e}")
            sys.exit(1)
    
    def check_table_exists(self, conn, table_name: str) -> bool:
        """Check if a table exists"""
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """, (table_name,))
            return cur.fetchone()[0]
    
    def check_column_exists(self, conn, table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table"""
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = %s 
                    AND column_name = %s
                )
            """, (table_name, column_name))
            return cur.fetchone()[0]
    
    def check_index_exists(self, conn, index_name: str) -> bool:
        """Check if an index exists"""
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM pg_indexes 
                    WHERE schemaname = 'public' 
                    AND indexname = %s
                )
            """, (index_name,))
            return cur.fetchone()[0]
    
    def check_view_exists(self, conn, view_name: str) -> bool:
        """Check if a view exists"""
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.views 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """, (view_name,))
            return cur.fetchone()[0]
    
    def check_trigger_exists(self, conn, trigger_name: str) -> bool:
        """Check if a trigger exists"""
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.triggers 
                    WHERE trigger_schema = 'public' 
                    AND trigger_name = %s
                )
            """, (trigger_name,))
            return cur.fetchone()[0]
    
    def get_table_count(self, conn, table_name: str) -> int:
        """Get row count for a table"""
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cur.fetchone()[0]
    
    def validate_tables(self, conn):
        """Validate all required tables exist"""
        print("\n" + "="*60)
        print("Validating Tables")
        print("="*60)
        
        required_tables = [
            'users',
            'themes',
            'themed_worlds',
            'drawings',
            'animation_data',
            'drawing_entities',
            'processing_jobs',
            'notifications',
            'system_logs',
        ]
        
        for table in required_tables:
            exists = self.check_table_exists(conn, table)
            status = "✓" if exists else "✗"
            print(f"{status} Table: {table}")
            
            if not exists:
                self.errors.append(f"Missing table: {table}")
            else:
                count = self.get_table_count(conn, table)
                print(f"  Rows: {count}")
    
    def validate_indexes(self, conn):
        """Validate all required indexes exist"""
        print("\n" + "="*60)
        print("Validating Indexes")
        print("="*60)
        
        required_indexes = [
            'idx_users_email',
            'idx_drawings_user_id',
            'idx_drawings_status',
            'idx_drawings_theme_id',
            'idx_drawing_entities_world_id',
            'idx_themed_worlds_theme_id',
            'idx_themed_worlds_is_full',
            'idx_processing_jobs_status',
            'idx_processing_jobs_drawing_id',
        ]
        
        for index in required_indexes:
            exists = self.check_index_exists(conn, index)
            status = "✓" if exists else "✗"
            print(f"{status} Index: {index}")
            
            if not exists:
                self.warnings.append(f"Missing index: {index}")
    
    def validate_views(self, conn):
        """Validate all required views exist"""
        print("\n" + "="*60)
        print("Validating Views")
        print("="*60)
        
        required_views = [
            'active_worlds',
            'drawing_details',
            'world_composition',
        ]
        
        for view in required_views:
            exists = self.check_view_exists(conn, view)
            status = "✓" if exists else "✗"
            print(f"{status} View: {view}")
            
            if not exists:
                self.warnings.append(f"Missing view: {view}")
    
    def validate_triggers(self, conn):
        """Validate all required triggers exist"""
        print("\n" + "="*60)
        print("Validating Triggers")
        print("="*60)
        
        required_triggers = [
            'trigger_update_world_timestamp',
            'trigger_update_entity_count',
            'trigger_update_user_drawing_count',
        ]
        
        for trigger in required_triggers:
            exists = self.check_trigger_exists(conn, trigger)
            status = "✓" if exists else "✗"
            print(f"{status} Trigger: {trigger}")
            
            if not exists:
                self.warnings.append(f"Missing trigger: {trigger}")
    
    def validate_default_data(self, conn):
        """Validate default theme data exists"""
        print("\n" + "="*60)
        print("Validating Default Data")
        print("="*60)
        
        required_themes = ['jungle', 'christmas', 'party', 'school', 'ocean', 'general']
        
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM themes")
            existing_themes = [row[0] for row in cur.fetchall()]
        
        for theme in required_themes:
            exists = theme in existing_themes
            status = "✓" if exists else "✗"
            print(f"{status} Theme: {theme}")
            
            if not exists:
                self.warnings.append(f"Missing default theme: {theme}")
    
    def validate_constraints(self, conn):
        """Validate key constraints"""
        print("\n" + "="*60)
        print("Validating Constraints")
        print("="*60)
        
        # Check foreign key constraints
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    tc.table_name, 
                    tc.constraint_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                    AND tc.table_schema = 'public'
                ORDER BY tc.table_name
            """)
            
            fk_count = 0
            for row in cur.fetchall():
                fk_count += 1
                print(f"✓ FK: {row[0]}.{row[2]} -> {row[3]}")
            
            print(f"\nTotal foreign keys: {fk_count}")
    
    def run_validation(self):
        """Run all validation checks"""
        print("="*60)
        print("Database Schema Validation")
        print("="*60)
        
        conn = self.connect()
        
        try:
            self.validate_tables(conn)
            self.validate_indexes(conn)
            self.validate_views(conn)
            self.validate_triggers(conn)
            self.validate_default_data(conn)
            self.validate_constraints(conn)
            
            # Print summary
            print("\n" + "="*60)
            print("Validation Summary")
            print("="*60)
            
            if self.errors:
                print(f"\n✗ Errors ({len(self.errors)}):")
                for error in self.errors:
                    print(f"  - {error}")
            
            if self.warnings:
                print(f"\n⚠ Warnings ({len(self.warnings)}):")
                for warning in self.warnings:
                    print(f"  - {warning}")
            
            if not self.errors and not self.warnings:
                print("\n✓ All validation checks passed!")
                return True
            elif not self.errors:
                print("\n✓ Schema is valid (with warnings)")
                return True
            else:
                print("\n✗ Schema validation failed")
                return False
                
        finally:
            conn.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Validate database schema for Themed Animation Platform'
    )
    
    parser.add_argument(
        '--connection-string',
        '-c',
        help='PostgreSQL connection string',
        default='postgresql://localhost/themed_animation'
    )
    
    args = parser.parse_args()
    
    validator = SchemaValidator(args.connection_string)
    success = validator.run_validation()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
