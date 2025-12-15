from typing import List, Dict, Optional
from datetime import datetime

try:
    import pyodbc

    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False


class SQLManager:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        if not PYODBC_AVAILABLE:
            raise ImportError("pyodbc is not installed")

    def get_connection(self):
        return pyodbc.connect(self.connection_string)

    async def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='arbitrage_opportunities' AND xtype='U')
            CREATE TABLE arbitrage_opportunities (
                id INT IDENTITY(1,1) PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                buy_exchange VARCHAR(50) NOT NULL,
                sell_exchange VARCHAR(50) NOT NULL,
                buy_price DECIMAL(18,8) NOT NULL,
                sell_price DECIMAL(18,8) NOT NULL,
                profit_percent DECIMAL(10,4) NOT NULL,
                profit_usd DECIMAL(18,2) NOT NULL,
                volume DECIMAL(18,8) NOT NULL,
                timestamp DATETIME NOT NULL,
                created_at DATETIME DEFAULT GETDATE()
            )
            """
        )

        cursor.execute(
            """
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='trades' AND xtype='U')
            CREATE TABLE trades (
                id INT IDENTITY(1,1) PRIMARY KEY,
                opportunity_id INT,
                symbol VARCHAR(20) NOT NULL,
                buy_exchange VARCHAR(50) NOT NULL,
                sell_exchange VARCHAR(50) NOT NULL,
                executed_buy_price DECIMAL(18,8),
                executed_sell_price DECIMAL(18,8),
                actual_profit_usd DECIMAL(18,2),
                status VARCHAR(20) NOT NULL,
                execution_time DATETIME NOT NULL,
                created_at DATETIME DEFAULT GETDATE()
            )
            """
        )

        conn.commit()
        conn.close()

    async def save_opportunity(self, opportunity: Dict) -> Optional[int]:
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO arbitrage_opportunities 
                (symbol, buy_exchange, sell_exchange, buy_price, sell_price, 
                 profit_percent, profit_usd, volume, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    opportunity["symbol"],
                    opportunity["buy_exchange"],
                    opportunity["sell_exchange"],
                    opportunity["buy_price"],
                    opportunity["sell_price"],
                    opportunity["profit_percent"],
                    opportunity["profit_usd"],
                    opportunity["volume"],
                    opportunity["timestamp"],
                ),
            )
            conn.commit()
            cursor.execute("SELECT @@IDENTITY")
            opportunity_id = cursor.fetchone()[0]
            return opportunity_id
        except Exception:
            return None
        finally:
            conn.close()

    async def get_opportunities_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT * FROM arbitrage_opportunities 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY profit_percent DESC
                """,
                (start_date, end_date),
            )

            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            return results
        except Exception:
            return []
        finally:
            conn.close()
