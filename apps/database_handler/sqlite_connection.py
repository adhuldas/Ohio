import sqlite3
import pandas as pd
import os
import logging

from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SqlInitHandler:
    """Handles database initialization, loading data, and saving processed data."""

    def __init__(self, report_path="apps/database_handler/report.xls"):
        """Initialize the handler with the path to the report."""
        self.report_path = report_path

    def init_sqldb(self):
        """Create the database and populate it with the processed data."""
        try:
            self.init_table()
            annual_data = self.load_data()
            self.save_to_db(annual_data)
            return True
        except Exception as e:
            logging.error(f"Failed to initialize database: {e}")
            return False

    def get_db_connection(self):
        """Establish a connection to the SQLite database."""
        try:
            conn = sqlite3.connect(Config.SQL_DB_PATH)
            conn.row_factory = sqlite3.Row  # Enable access to columns by name
            return conn
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            raise

    def init_table(self):
        """Initialize the SQLite database with the required schema."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS annual_production (
                    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_well_number TEXT,
                    oil INTEGER,
                    gas INTEGER,
                    brine INTEGER,
                    days INTEGER,
                    quarter1 INTEGER,
                    quarter2 INTEGER,
                    quarter3 INTEGER,
                    quarter4 INTEGER
                );
                ''')
                conn.commit()
        except Exception as e:
            logging.error(f"Failed to initialize table: {e}")
            raise

    def load_data(self):
        """Load the data from the Excel file and process it."""
        try:
            file_extension = os.path.splitext(self.report_path)[-1].lower()

            if file_extension == '.xls':
                df = pd.read_excel(self.report_path, sheet_name=0, engine='xlrd', header=0)
            elif file_extension == '.xlsx':
                df = pd.read_excel(self.report_path, sheet_name=0, engine='openpyxl', header=0)
            else:
                raise ValueError("Unsupported file format. Please provide an .xls or .xlsx Excel file.")


            # Strip leading/trailing spaces from column names
            df.columns = df.columns.str.strip()

            # Print the columns to check their alignment

            # Check the actual number of columns to understand the structure
            num_columns = len(df.columns)

            # Check for required columns
            required_columns = ['API WELL  NUMBER', 'GAS', 'BRINE', 'DAYS', 'QUARTER 1,2,3,4']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

            # Process the data with dynamic column handling
            annual_data = {}
            for _, row in df.iterrows():
                well_number = str(row['API WELL  NUMBER'])
                if well_number not in annual_data:
                    annual_data[well_number] = {
                        'oil': row.get('OIL', 0),  # Use 'OIL' or default to 0 if it's missing
                        'gas': 0,  # Initialize gas, brine, and days to zero for now
                        'brine': 0,
                        'days': 0,
                        'quarters': {'Q1': 0, 'Q2': 0, 'Q3': 0, 'Q4': 0}  # To store quarterly data
                    }

                # Add up the gas, brine, and days data for each well
                annual_data[well_number]['gas'] += row['GAS']
                annual_data[well_number]['brine'] += row['BRINE']
                annual_data[well_number]['days'] += row['DAYS']

                # Store quarterly data from 'QUARTER 1,2,3,4'
                for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
                    quarter_col = f'QUARTER {quarter}'
                    if quarter_col in df.columns:
                        annual_data[well_number]['quarters'][quarter] += row[quarter_col]  # Add quarterly value

            return annual_data

        except Exception as e:
            logging.error(f"Failed to load data: {e}")
            raise

    def save_to_db(self, annual_data):
        """Save the processed annual data into SQLite."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                for well_number, data in annual_data.items():
                    cursor.execute('''
                    INSERT INTO annual_production (api_well_number, oil, gas, brine, days, quarter1, quarter2, quarter3, quarter4)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (well_number, data['oil'], data['gas'], data['brine'], data['days'],
                          data['quarters']['Q1'], data['quarters']['Q2'], data['quarters']['Q3'], data['quarters']['Q4']))
                conn.commit()
        except Exception as e:
            logging.error(f"Failed to save data to the database: {e}")
            raise
