"""
Data Quality Pipeline - Main Entry Point
Chains multiple rules together and produces one final output
"""

import pandas as pd
import uuid
from datetime import datetime
import os
from pathlib import Path
import importlib

from engine.rule_registry import load_rules
from engine.audit_logger import log_execution


def main():
    """
    Execute data quality pipeline with chained rules
    All rules process the same dataframe sequentially
    """

    print("=" * 60)
    print("Data Quality Pipeline")
    print("=" * 60)

    # Load all enabled rules
    all_rules = load_rules()
    enabled_rules = [r for r in all_rules if r.get("enabled", False)]

    if not enabled_rules:
        print("\nWARNING: No enabled rules found")
        return

    print(f"\nLoaded {len(enabled_rules)} enabled rule(s)")
    for rule in enabled_rules:
        print(f"   - {rule['rule_id']}: {rule['rule_name']}")

    # Determine input/output files from first rule
    # All rules should use same source for consistency
    input_file = enabled_rules[0]["source"]["file"]
    output_file = enabled_rules[0]["destination"]["file"]

    # Read source data once
    print(f"\nLoading data from {input_file}")
    df = pd.read_csv(input_file)
    initial_rows = len(df)
    print(f"   Initial rows: {initial_rows}")

    # Generate run ID for this pipeline execution
    run_id = str(uuid.uuid4())
    timestamp = datetime.now().timestamp()

    # Execute all rules sequentially on the same dataframe
    print(f"\nApplying rules sequentially:")
    executed_rules = []

    for rule in enabled_rules:
        rule_id = rule["rule_id"]
        rule_name = rule["rule_name"]
        operation = rule["operation"]["type"]
        parameters = rule.get("parameters", {})

        rows_before = len(df)

        try:
            # Dynamically import and execute operation
            print(f"\n[{rule_id}] {rule_name}")
            print(f"   Operation: {operation}")

            operation_module = importlib.import_module(f"engine.operations.{operation}")
            operation_func = operation_module.execute
            df = operation_func(df, parameters)

            rows_after = len(df)

            # Track execution
            executed_rules.append(rule_id)

            # Log to audit
            log_execution({
                "rule_id": rule_id,
                "rule_name": rule_name,
                "run_id": run_id,
                "timestamp": datetime.now().isoformat(),
                "rows_before": rows_before,
                "rows_after": rows_after,
                "rows_changed": rows_before - rows_after,
                "status": "SUCCESS"
            })

        except Exception as e:
            print(f"   ERROR: {str(e)}")
            log_execution({
                "rule_id": rule_id,
                "rule_name": rule_name,
                "run_id": run_id,
                "timestamp": datetime.now().isoformat(),
                "status": f"FAILED: {str(e)}"
            })
            raise

    final_rows = len(df)

    # Add pipeline metadata columns
    df["rules_applied"] = ",".join(executed_rules)  # e.g., "DQ-002,DQ-001"
    df["run_id"] = run_id
    df["run_timestamp"] = timestamp

    # Save final output with timestamp
    output_path = Path(output_file)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_timestamped = output_path.parent / f"{output_path.stem}_{timestamp_str}{output_path.suffix}"

    os.makedirs(os.path.dirname(output_file_timestamped), exist_ok=True)
    df.to_csv(output_file_timestamped, index=False)

    # Summary
    print(f"\n" + "=" * 60)
    print("Pipeline completed successfully")
    print(f"   Rules executed: {', '.join(executed_rules)}")
    print(f"   Initial rows: {initial_rows}")
    print(f"   Final rows: {final_rows}")
    print(f"   Output: {output_file_timestamped}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
