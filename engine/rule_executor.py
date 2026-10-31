"""
Rule Executor - Main dispatcher
Routes operations to their specific executor modules
"""

import pandas as pd
import uuid
from datetime import datetime
import os
from pathlib import Path
import importlib


def execute_rule(rule):
    """
    Execute a data quality rule by dispatching to the appropriate operation executor

    Args:
        rule: Rule dictionary from YAML config

    Returns:
        Execution result dictionary
    """

    input_file = rule["source"]["file"]
    output_file = rule["destination"]["file"]
    rule_id = rule["rule_id"]
    rule_name = rule["rule_name"]
    operation = rule["operation"]["type"]
    parameters = rule.get("parameters", {})

    # Read input data
    df = pd.read_csv(input_file)
    rows_before = len(df)

    # Dynamically import the operation module
    try:
        operation_module = importlib.import_module(f"engine.operations.{operation}")
        operation_func = operation_module.execute
    except ModuleNotFoundError:
        raise ValueError(f"Unsupported operation: {operation}. Create engine/operations/{operation}.py")

    # Execute the operation
    print(f"  Running: {operation}")
    df = operation_func(df, parameters)

    rows_after = len(df)
    rows_changed = rows_before - rows_after

    # Add execution metadata
    run_id = str(uuid.uuid4())
    timestamp = datetime.now().timestamp()
    df["rule_id"] = rule_id
    df["run_id"] = run_id
    df["run_timestamp"] = timestamp

    # Save processed data with timestamp and rule ID for uniqueness
    output_path = Path(output_file)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_timestamped = output_path.parent / f"{output_path.stem}_{rule_id}_{timestamp_str}{output_path.suffix}"

    os.makedirs(os.path.dirname(output_file_timestamped), exist_ok=True)
    df.to_csv(output_file_timestamped, index=False)

    # Return execution details
    return {
        "rule_id": rule_id,
        "rule_name": rule_name,
        "run_id": run_id,
        "timestamp": timestamp,
        "input_file": input_file,
        "output_file": str(output_file_timestamped),
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_changed": rows_changed,
        "status": "SUCCESS"
    }
