"""
AlphaForge multi-instrument monthly backtest runner (OANDA historical data)

Runs the OANDABacktestEngine for a set of instruments across a fixed month
and saves per-instrument results plus a compact aggregated summary.

Usage:
  - Ensure the environment variable OANDA_API_KEY is set (practice key)
  - Optionally run via the PowerShell helper script in the repo root
"""
import asyncio
import json
import os
from datetime import datetime

from backtest_oanda import OANDABacktestEngine


async def run_month_backtest(
    instruments,
    start_date: str,
    end_date: str,
    initial_balance: float = 10000.0,
    risk_per_trade: float = 0.02,
    min_votes_required: float = 1.5,
    min_strength: float = 30.0,
):
    api_key = os.getenv("OANDA_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OANDA_API_KEY not set. Please set it in your environment before running."
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = os.path.join(os.path.dirname(__file__), "backtest_results")
    os.makedirs(results_dir, exist_ok=True)

    aggregated = {
        "period": {"start": start_date, "end": end_date},
        "initial_balance": initial_balance,
        "risk_per_trade": risk_per_trade,
        "min_votes_required": min_votes_required,
        "min_strength": min_strength,
        "instruments": {},
    }

    for instrument in instruments:
        print(f"\n=== Running backtest for {instrument} ({start_date} -> {end_date}) ===")
        engine = OANDABacktestEngine(
            api_key=api_key,
            initial_balance=initial_balance,
            min_votes_required=min_votes_required,
            min_strength=min_strength,
        )

        results = await engine.run_backtest(
            instrument=instrument,
            start_date=start_date,
            end_date=end_date,
            risk_per_trade=risk_per_trade,
            focus_date=None,
        )

        # Save per-instrument results and collect key metrics
        if results:
            per_file = os.path.join(
                results_dir, f"backtest_results_{instrument}_{timestamp}.json"
            )
            engine.save_results(results, per_file)

            aggregated["instruments"][instrument] = {
                "final_balance": results.get("final_balance"),
                "net_profit": results.get("net_profit"),
                "return_pct": results.get("return_pct"),
                "total_trades": results.get("total_trades"),
                "win_rate": results.get("win_rate"),
                "profit_factor": results.get("profit_factor"),
                "max_drawdown": results.get("max_drawdown"),
            }
        else:
            aggregated["instruments"][instrument] = {
                "error": "No results (possibly no data or no trades)"
            }

    # Save aggregated summary
    summary_file = os.path.join(
        results_dir, f"backtest_summary_{start_date}_to_{end_date}_{timestamp}.json"
    )
    with open(summary_file, "w") as f:
        json.dump(aggregated, f, indent=2)

    print("\n=== Aggregated Summary ===")
    print(json.dumps(aggregated, indent=2))
    print(f"\nSaved summary to: {summary_file}")


async def main():
    # Default: August 2024 monthly backtest across core instruments
    instruments = ["GBP_USD", "XAU_USD", "USD_JPY"]
    start_date = "2024-08-01"
    end_date = "2024-08-31"

    await run_month_backtest(
        instruments=instruments,
        start_date=start_date,
        end_date=end_date,
        initial_balance=10000.0,
        risk_per_trade=0.02,
        min_votes_required=1.5,
        min_strength=30.0,
    )


if __name__ == "__main__":
    asyncio.run(main())
