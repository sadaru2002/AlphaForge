"""
Collect rejected signal details for yesterday using real OANDA data.

Outputs a JSON report with per-hour, per-instrument rejections including:
- reason, filter flags, atr_pct, adx, strength, agreement, buy/sell votes,
  and timeframe-level snapshots when available.

Report saved to: backend/reports/rejected_signals_{YYYY-MM-DD}.json
"""
import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

from enhanced_signal_generator import EnhancedSignalGenerator


async def collect_rejections_for_yesterday():
    load_dotenv()

    now = datetime.now()
    yesterday = now - timedelta(days=1)
    y_date = yesterday.strftime('%Y-%m-%d')
    start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    instruments = ["GBP_USD", "XAU_USD", "USD_JPY"]
    hours_to_check = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]

    gen = EnhancedSignalGenerator()

    report = {
        "date": y_date,
        "instruments": instruments,
        "hours": hours_to_check,
        "rejections": [],  # list of {hour, instrument, reason, metrics}
        "summary": {
            "by_instrument": {},
            "by_reason": {},
            "total": 0,
        },
    }

    for hr in hours_to_check:
        check_time = start.replace(hour=hr)
        for inst in instruments:
            try:
                result = await gen.generate_signal(inst)
                if not result:
                    report["rejections"].append({
                        "hour": hr,
                        "instrument": inst,
                        "reason": "generator_error",
                    })
                    continue

                # Accept only explicit rejections (SKIP / tradeable False)
                if result.get("signal") == "SKIP" or not result.get("tradeable", False):
                    reason = result.get("reason", "unknown")
                    mtf = result.get("mtf_signal", {})
                    filters = result.get("filter_results", {})

                    # Extract metrics if present
                    metrics = {
                        "strength": mtf.get("strength", 0),
                        "agreement": mtf.get("agreement", 0.0) if isinstance(mtf, dict) else 0.0,
                        "buy_votes": mtf.get("buy_votes", 0),
                        "sell_votes": mtf.get("sell_votes", 0),
                        "confidence": mtf.get("confidence", 0.0),
                        "atr_pct": filters.get("atr_pct"),
                        "adx": filters.get("adx"),
                        "volatility_ok": filters.get("volatility_ok"),
                        "strength_ok": filters.get("strength_ok"),
                        "adx_ok": filters.get("adx_ok"),
                        "filter_reasons": filters.get("reasons", []),
                        # Price context
                        "last_price": result.get("last_price"),
                        "suggested_direction": result.get("suggested_direction"),
                        "proposed_entry": result.get("proposed_entry"),
                        "proposed_stop_loss": result.get("proposed_stop_loss"),
                        "proposed_take_profit": result.get("proposed_take_profit"),
                    }

                    # Add timeframe breakdown if available
                    tf = mtf.get("timeframe_signals", {}) if isinstance(mtf, dict) else {}
                    tf_compact = {}
                    for k, v in tf.items():
                        tf_compact[k] = {
                            "buy_votes": v.get("buy_votes"),
                            "sell_votes": v.get("sell_votes"),
                            "strength": v.get("strength"),
                        }

                    entry = {
                        "hour": hr,
                        "timestamp": check_time.isoformat(),
                        "instrument": inst,
                        "regime": result.get("regime"),
                        "reason": reason,
                        "metrics": metrics,
                        "timeframes": tf_compact,
                    }
                    report["rejections"].append(entry)

                    # Update summary
                    report["summary"]["total"] += 1
                    report["summary"]["by_instrument"].setdefault(inst, 0)
                    report["summary"]["by_instrument"][inst] += 1
                    report["summary"]["by_reason"].setdefault(reason, 0)
                    report["summary"]["by_reason"][reason] += 1

            except Exception as e:
                report["rejections"].append({
                    "hour": hr,
                    "instrument": inst,
                    "reason": f"exception: {e}",
                })

    # Save report
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_path = reports_dir / f"rejected_signals_{y_date}.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    # Print concise summary for terminal
    print("\n=== Rejected Signals Summary ===")
    print(f"Date: {y_date}")
    print(f"Total: {report['summary']['total']}")
    print("By Instrument:")
    for k, v in sorted(report["summary"]["by_instrument"].items()):
        print(f"  - {k}: {v}")
    print("By Reason:")
    for k, v in sorted(report["summary"]["by_reason"].items(), key=lambda x: -x[1]):
        print(f"  - {k}: {v}")
    print(f"Saved: {out_path}")


async def main():
    await collect_rejections_for_yesterday()


if __name__ == "__main__":
    asyncio.run(main())
