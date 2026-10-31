# Data Quality Pipeline

Clean, modular data quality engine for CSV processing with sequential rule chaining.

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

## Architecture

```
config/
  └── rules/
      ├── remove_duplicates.yml    # Rule definitions (WHAT to run)
      └── replace_nulls.yml

engine/
  ├── rule_registry.py             # Loads rules from config
  ├── rule_executor.py             # Rule dispatcher (routes to operations)
  ├── audit_logger.py              # Tracks execution history
  └── operations/
      ├── drop_duplicates.py       # Individual operation implementations
      └── replace_nulls.py

main.py                            # Pipeline orchestrator (chains rules)
```

## How It Works

The pipeline executes all enabled rules **sequentially on the same dataframe**:

1. **Load rules** from `config/rules/*.yml`
2. **Read source data** once from first rule's source file
3. **Apply each rule** in order, transforming the same dataframe
4. **Add metadata** (rules_applied, run_id, run_timestamp)
5. **Save final output** with timestamp

## Adding New Rules

**1. Create operation** (`engine/operations/validate_amount.py`):
```python
def execute(df, parameters):
    """
    Validate amount is positive
    """
    column = parameters.get("column")
    min_value = parameters.get("min_value", 0)
    df = df[df[column] >= min_value]
    return df
```

**2. Define rule config** (`config/rules/validate_amount.yml`):
```yaml
rule_id: DQ-003
rule_name: validate_amount
enabled: true
description: Ensure amount is positive

source:
  file: data/raw/orders.csv

destination:
  file: data/processed/orders.csv

operation:
  type: validate_amount

parameters:
  column: amount
  min_value: 0
```

**3. Run pipeline**: `python main.py`

The operation is automatically discovered and executed by the rule executor.

## Current Rules

- **DQ-001**: Remove duplicate rows (drop_duplicates)
- **DQ-002**: Replace null values in amount column (replace_nulls)

## Data Flow

```
data/raw/orders.csv
    ↓ [DQ-002: replace_nulls]
    ↓ [DQ-001: drop_duplicates]
    ↓ [add metadata]
data/processed/orders_YYYYMMDD_HHMMSS.csv
    ↓ [audit trail]
data/logs/audit.csv
```

## CI/CD

- **Trigger:** Changes to `data/raw/orders.csv`, `config/rules/**`, or `engine/**` on main branch
- **Action:** Auto-runs pipeline and commits cleaned data with timestamp
- **Workflow:** `.github/workflows/clean-data.yml`
