import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
import os

# Database file path - will be relative to exe location
DB_FILE = "broiler_data.db"

class SQLiteDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            # Use current directory or executable directory
            if hasattr(os, '_MEIPASS'):
                # Running in PyInstaller bundle
                base_path = os.path.dirname(os.path.abspath(__file__))
            else:
                # Running in development
                base_path = os.getcwd()
            self.db_path = os.path.join(base_path, DB_FILE)
        else:
            self.db_path = db_path
        
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create broiler_calculations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS broiler_calculations (
                id TEXT PRIMARY KEY,
                batch_id TEXT UNIQUE NOT NULL,
                input_data TEXT NOT NULL,
                feed_conversion_ratio REAL,
                mortality_rate_percent REAL,
                weighted_average_age REAL,
                daily_weight_gain REAL,
                total_cost REAL,
                total_revenue REAL,
                net_cost_per_kg REAL,
                total_weight_produced_kg REAL,
                total_feed_consumed_kg REAL,
                surviving_chicks INTEGER,
                removed_chicks INTEGER,
                missing_chicks INTEGER,
                viability INTEGER,
                average_weight_per_chick REAL,
                cost_breakdown TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Create handlers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS handlers (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                email TEXT,
                phone TEXT,
                notes TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Create sheds table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sheds (
                id TEXT PRIMARY KEY,
                number TEXT UNIQUE NOT NULL,
                capacity INTEGER,
                location TEXT,
                status TEXT DEFAULT 'active',
                notes TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_batch_id ON broiler_calculations(batch_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_handler_name ON handlers(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_shed_number ON sheds(number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON broiler_calculations(created_at)')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    # Broiler Calculations Operations
    async def insert_calculation(self, calculation_data):
        """Insert a new calculation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Generate ID if not provided
        if 'id' not in calculation_data:
            calculation_data['id'] = str(uuid.uuid4())
        
        # Serialize complex fields
        input_data_json = json.dumps(calculation_data['input_data'], default=str)
        cost_breakdown_json = json.dumps(calculation_data['cost_breakdown'], default=str)
        
        # Current timestamp
        now = datetime.now().isoformat()
        calculation_data['created_at'] = now
        calculation_data['updated_at'] = now
        
        cursor.execute('''
            INSERT INTO broiler_calculations (
                id, batch_id, input_data, feed_conversion_ratio, mortality_rate_percent,
                weighted_average_age, daily_weight_gain, total_cost, total_revenue,
                net_cost_per_kg, total_weight_produced_kg, total_feed_consumed_kg,
                surviving_chicks, removed_chicks, missing_chicks, viability,
                average_weight_per_chick, cost_breakdown, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            calculation_data['id'], calculation_data['input_data']['batch_id'],
            input_data_json, calculation_data['feed_conversion_ratio'],
            calculation_data['mortality_rate_percent'], calculation_data['weighted_average_age'],
            calculation_data['daily_weight_gain'], calculation_data['total_cost'],
            calculation_data['total_revenue'], calculation_data['net_cost_per_kg'],
            calculation_data['total_weight_produced_kg'], calculation_data['total_feed_consumed_kg'],
            calculation_data['surviving_chicks'], calculation_data['removed_chicks'],
            calculation_data['missing_chicks'], calculation_data['viability'],
            calculation_data['average_weight_per_chick'], cost_breakdown_json,
            calculation_data['created_at'], calculation_data['updated_at']
        ))
        
        conn.commit()
        conn.close()
        return calculation_data['id']
    
    async def find_calculation_by_batch_id(self, batch_id):
        """Find calculation by batch ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM broiler_calculations WHERE batch_id = ?', (batch_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_calculation_dict(row)
        return None
    
    async def find_calculation_by_id(self, calc_id):
        """Find calculation by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM broiler_calculations WHERE id = ?', (calc_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_calculation_dict(row)
        return None
    
    async def get_all_calculations(self, limit=50):
        """Get all calculations with limit"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM broiler_calculations ORDER BY created_at DESC LIMIT ?', 
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_calculation_dict(row) for row in rows]
    
    async def update_calculation(self, batch_id, calculation_data):
        """Update existing calculation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Serialize complex fields
        input_data_json = json.dumps(calculation_data['input_data'], default=str)
        cost_breakdown_json = json.dumps(calculation_data['cost_breakdown'], default=str)
        
        # Update timestamp
        calculation_data['updated_at'] = datetime.now().isoformat()
        
        cursor.execute('''
            UPDATE broiler_calculations SET
                input_data = ?, feed_conversion_ratio = ?, mortality_rate_percent = ?,
                weighted_average_age = ?, daily_weight_gain = ?, total_cost = ?,
                total_revenue = ?, net_cost_per_kg = ?, total_weight_produced_kg = ?,
                total_feed_consumed_kg = ?, surviving_chicks = ?, removed_chicks = ?,
                missing_chicks = ?, viability = ?, average_weight_per_chick = ?,
                cost_breakdown = ?, updated_at = ?
            WHERE batch_id = ?
        ''', (
            input_data_json, calculation_data['feed_conversion_ratio'],
            calculation_data['mortality_rate_percent'], calculation_data['weighted_average_age'],
            calculation_data['daily_weight_gain'], calculation_data['total_cost'],
            calculation_data['total_revenue'], calculation_data['net_cost_per_kg'],
            calculation_data['total_weight_produced_kg'], calculation_data['total_feed_consumed_kg'],
            calculation_data['surviving_chicks'], calculation_data['removed_chicks'],
            calculation_data['missing_chicks'], calculation_data['viability'],
            calculation_data['average_weight_per_chick'], cost_breakdown_json,
            calculation_data['updated_at'], batch_id
        ))
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    async def delete_calculation_by_batch_id(self, batch_id):
        """Delete calculation by batch ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM broiler_calculations WHERE batch_id = ?', (batch_id,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        return deleted_count > 0
    
    async def delete_calculation_by_id(self, calc_id):
        """Delete calculation by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM broiler_calculations WHERE id = ?', (calc_id,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        return deleted_count > 0
    
    def _row_to_calculation_dict(self, row):
        """Convert SQLite row to calculation dictionary"""
        return {
            'id': row['id'],
            'input_data': json.loads(row['input_data']),
            'feed_conversion_ratio': row['feed_conversion_ratio'],
            'mortality_rate_percent': row['mortality_rate_percent'],
            'weighted_average_age': row['weighted_average_age'],
            'daily_weight_gain': row['daily_weight_gain'],
            'total_cost': row['total_cost'],
            'total_revenue': row['total_revenue'],
            'net_cost_per_kg': row['net_cost_per_kg'],
            'total_weight_produced_kg': row['total_weight_produced_kg'],
            'total_feed_consumed_kg': row['total_feed_consumed_kg'],
            'surviving_chicks': row['surviving_chicks'],
            'removed_chicks': row['removed_chicks'],
            'missing_chicks': row['missing_chicks'],
            'viability': row['viability'],
            'average_weight_per_chick': row['average_weight_per_chick'],
            'cost_breakdown': json.loads(row['cost_breakdown']),
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
    
    # Handler Operations
    async def insert_handler(self, handler_data):
        """Insert a new handler"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if 'id' not in handler_data:
            handler_data['id'] = str(uuid.uuid4())
        
        now = datetime.now().isoformat()
        handler_data['created_at'] = now
        handler_data['updated_at'] = now
        
        cursor.execute('''
            INSERT INTO handlers (id, name, email, phone, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            handler_data['id'], handler_data['name'], handler_data.get('email'),
            handler_data.get('phone'), handler_data.get('notes'),
            handler_data['created_at'], handler_data['updated_at']
        ))
        
        conn.commit()
        conn.close()
        return handler_data['id']
    
    async def find_handler_by_name(self, name):
        """Find handler by name"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM handlers WHERE name = ?', (name,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    async def find_handler_by_id(self, handler_id):
        """Find handler by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM handlers WHERE id = ?', (handler_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    async def get_all_handlers(self):
        """Get all handlers"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM handlers ORDER BY name')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    async def get_handler_names(self):
        """Get all handler names"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT name FROM handlers ORDER BY name')
        rows = cursor.fetchall()
        conn.close()
        
        return [row['name'] for row in rows]
    
    async def update_handler(self, handler_id, handler_data):
        """Update handler"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        handler_data['updated_at'] = datetime.now().isoformat()
        
        cursor.execute('''
            UPDATE handlers SET name = ?, email = ?, phone = ?, notes = ?, updated_at = ?
            WHERE id = ?
        ''', (
            handler_data['name'], handler_data.get('email'), handler_data.get('phone'),
            handler_data.get('notes'), handler_data['updated_at'], handler_id
        ))
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    async def delete_handler(self, handler_id):
        """Delete handler"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM handlers WHERE id = ?', (handler_id,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        return deleted_count > 0
    
    # Shed Operations
    async def insert_shed(self, shed_data):
        """Insert a new shed"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if 'id' not in shed_data:
            shed_data['id'] = str(uuid.uuid4())
        
        now = datetime.now().isoformat()
        shed_data['created_at'] = now
        shed_data['updated_at'] = now
        
        cursor.execute('''
            INSERT INTO sheds (id, number, capacity, location, status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            shed_data['id'], shed_data['number'], shed_data.get('capacity'),
            shed_data.get('location'), shed_data.get('status', 'active'),
            shed_data.get('notes'), shed_data['created_at'], shed_data['updated_at']
        ))
        
        conn.commit()
        conn.close()
        return shed_data['id']
    
    async def find_shed_by_number(self, number):
        """Find shed by number"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM sheds WHERE number = ?', (number,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    async def find_shed_by_id(self, shed_id):
        """Find shed by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM sheds WHERE id = ?', (shed_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    async def get_all_sheds(self):
        """Get all sheds"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM sheds ORDER BY number')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    async def get_shed_numbers(self):
        """Get all shed numbers from calculations"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT json_extract(input_data, '$.shed_number') as shed_number
            FROM broiler_calculations
            ORDER BY shed_number
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        return [row['shed_number'] for row in rows if row['shed_number']]
    
    async def update_shed(self, shed_id, shed_data):
        """Update shed"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        shed_data['updated_at'] = datetime.now().isoformat()
        
        cursor.execute('''
            UPDATE sheds SET number = ?, capacity = ?, location = ?, status = ?, notes = ?, updated_at = ?
            WHERE id = ?
        ''', (
            shed_data['number'], shed_data.get('capacity'), shed_data.get('location'),
            shed_data.get('status'), shed_data.get('notes'), shed_data['updated_at'], shed_id
        ))
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    async def delete_shed(self, shed_id):
        """Delete shed"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sheds WHERE id = ?', (shed_id,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        return deleted_count > 0
    
    # Performance and Analytics
    async def get_calculations_by_handler(self, handler_name):
        """Get all calculations for a specific handler"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM broiler_calculations 
            WHERE json_extract(input_data, '$.handler_name') = ?
            ORDER BY created_at DESC
        ''', (handler_name,))
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_calculation_dict(row) for row in rows]
    
    async def count_calculations_by_handler(self, handler_name):
        """Count calculations by handler"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM broiler_calculations 
            WHERE json_extract(input_data, '$.handler_name') = ?
        ''', (handler_name,))
        row = cursor.fetchone()
        conn.close()
        
        return row['count'] if row else 0
    
    def close(self):
        """Close database connections"""
        # SQLite connections are closed after each operation
        pass

# Global database instance
db = SQLiteDatabase()