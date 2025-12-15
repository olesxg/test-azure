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
    created_at DATETIME DEFAULT GETDATE(),
    INDEX idx_symbol (symbol),
    INDEX idx_timestamp (timestamp),
    INDEX idx_profit_percent (profit_percent)
);

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
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (opportunity_id) REFERENCES arbitrage_opportunities(id),
    INDEX idx_symbol (symbol),
    INDEX idx_status (status),
    INDEX idx_execution_time (execution_time)
);

CREATE TABLE market_data (
    id INT IDENTITY(1,1) PRIMARY KEY,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    bid DECIMAL(18,8) NOT NULL,
    ask DECIMAL(18,8) NOT NULL,
    last_price DECIMAL(18,8) NOT NULL,
    volume DECIMAL(18,8) NOT NULL,
    timestamp DATETIME NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    INDEX idx_exchange_symbol (exchange, symbol),
    INDEX idx_timestamp (timestamp)
);

CREATE VIEW v_best_opportunities AS
SELECT TOP 100
    symbol,
    buy_exchange,
    sell_exchange,
    buy_price,
    sell_price,
    profit_percent,
    profit_usd,
    timestamp
FROM arbitrage_opportunities
WHERE timestamp >= DATEADD(day, -7, GETDATE())
ORDER BY profit_percent DESC;

CREATE VIEW v_exchange_performance AS
SELECT
    exchange,
    symbol,
    COUNT(*) as tick_count,
    AVG(last_price) as avg_price,
    MIN(last_price) as min_price,
    MAX(last_price) as max_price,
    AVG(volume) as avg_volume
FROM market_data
WHERE timestamp >= DATEADD(hour, -24, GETDATE())
GROUP BY exchange, symbol;

CREATE PROCEDURE sp_GetArbitrageStatistics
    @days INT = 7
AS
BEGIN
    SELECT
        COUNT(*) as total_opportunities,
        AVG(profit_percent) as avg_profit_percent,
        MAX(profit_percent) as max_profit_percent,
        SUM(profit_usd) as total_potential_profit,
        COUNT(DISTINCT symbol) as unique_symbols,
        COUNT(DISTINCT buy_exchange) as unique_buy_exchanges,
        COUNT(DISTINCT sell_exchange) as unique_sell_exchanges
    FROM arbitrage_opportunities
    WHERE timestamp >= DATEADD(day, -@days, GETDATE());
END;

