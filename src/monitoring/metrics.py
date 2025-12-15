from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict


class MetricsCollector:
    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_time = datetime.now()

    def record_ticker_fetch(self, exchange: str, symbol: str, success: bool):
        self.metrics["ticker_fetches"].append(
            {
                "exchange": exchange,
                "symbol": symbol,
                "success": success,
                "timestamp": datetime.now(),
            }
        )

    def record_opportunity(self, opportunity: Dict):
        self.metrics["opportunities"].append(
            {"opportunity": opportunity, "timestamp": datetime.now()}
        )

    def record_execution(self, execution_result: Dict):
        self.metrics["executions"].append(
            {"result": execution_result, "timestamp": datetime.now()}
        )

    def get_summary(self) -> Dict:
        uptime = (datetime.now() - self.start_time).total_seconds()

        ticker_fetches = self.metrics.get("ticker_fetches", [])
        opportunities = self.metrics.get("opportunities", [])
        executions = self.metrics.get("executions", [])

        successful_fetches = sum(1 for f in ticker_fetches if f["success"])
        total_fetches = len(ticker_fetches)

        return {
            "uptime_seconds": uptime,
            "total_ticker_fetches": total_fetches,
            "successful_ticker_fetches": successful_fetches,
            "fetch_success_rate": (
                successful_fetches / total_fetches if total_fetches > 0 else 0
            ),
            "total_opportunities_found": len(opportunities),
            "total_executions": len(executions),
            "opportunities_per_minute": (
                len(opportunities) / (uptime / 60) if uptime > 0 else 0
            ),
        }

    def get_exchange_statistics(self) -> Dict[str, Dict]:
        ticker_fetches = self.metrics.get("ticker_fetches", [])
        exchange_stats = defaultdict(lambda: {"total": 0, "successful": 0})

        for fetch in ticker_fetches:
            exchange = fetch["exchange"]
            exchange_stats[exchange]["total"] += 1
            if fetch["success"]:
                exchange_stats[exchange]["successful"] += 1

        for exchange, stats in exchange_stats.items():
            if stats["total"] > 0:
                stats["success_rate"] = stats["successful"] / stats["total"]

        return dict(exchange_stats)
