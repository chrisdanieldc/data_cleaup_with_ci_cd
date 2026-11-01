# Data Quality Pipeline

Clean, modular data quality engine for CSV processing with sequential rule chaining and automated testing.

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

## What's in here

This is a data cleaning pipeline that reads CSV files, applies rules to clean them up (remove duplicates, replace nulls, etc.), and saves the cleaned output. It's designed to be modular - you can add new cleaning rules without touching the core code.

## Architecture

```
config/
  └── rules/
      ├── remove_duplicates.yml    # Rule definitions
      └── replace_nulls.yml

engine/
  ├── rule_registry.py             # Loads rules from config
  ├── rule_executor.py             # Routes rules to operations
  ├── audit_logger.py              # Tracks what ran
  └── operations/
      ├── drop_duplicates.py       # Individual cleaning operations
      └── replace_nulls.py

data/
  ├── raw/                         # Input CSV files
  ├── processed/                   # Cleaned output
  ├── logs/                        # Audit trail
  └── test/                        # Test data for pytest
      ├── source/                  # Test inputs
      ├── after_test/              # Expected outputs
      └── output/                  # Test results

main.py                            # Runs the pipeline
test_pipeline.py                   # Integration tests
```

## How It Works

The pipeline runs all enabled rules sequentially on the same dataframe:

1. Load all enabled rules from `config/rules/*.yml`
2. Read the source CSV once
3. Apply each rule in order, transforming the dataframe
4. Add metadata columns (rules_applied, run_id, run_timestamp)
5. Save the final cleaned output with a timestamp

Each rule specifies an operation (like drop_duplicates or replace_nulls) and parameters for that operation. The engine loads the operation dynamically and executes it.

## Running Tests

We have integration tests that verify the pipeline works correctly:

```bash
# Run tests
pytest test_pipeline.py -v

# Or run directly
python test_pipeline.py
```

The tests work by comparing actual pipeline output against expected output. You put test CSV files in `data/test/source/` and the expected clean versions in `data/test/after_test/`, then the test runs the pipeline and checks if they match.

See [TEST_README.md](TEST_README.md) for details on how testing works.

## Adding New Rules

**1. Create the operation** (`engine/operations/validate_amount.py`):

```python
def execute(df, parameters):
    """Validate amount is positive"""
    column = parameters.get("column")
    min_value = parameters.get("min_value", 0)
    df = df[df[column] >= min_value]
    return df
```

**2. Create the rule config** (`config/rules/validate_amount.yml`):

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

**3. Run it**: `python main.py`

The rule executor automatically discovers the new operation and runs it.

## Current Rules

- **DQ-001**: Remove duplicate rows
- **DQ-002**: Replace null values in amount column with 0

## Data Flow

```
data/raw/orders.csv
    ↓ [DQ-002: replace_nulls]
    ↓ [DQ-001: drop_duplicates]
    ↓ [add metadata]
data/processed/orders_20260101_120000.csv
    ↓ [audit trail]
data/logs/audit.csv
```

## CI/CD Pipeline

The GitHub Actions workflow handles both testing and data processing intelligently:

### How it works

When you push to main, the workflow checks what files changed:

**If only data changed** (data/raw/orders.csv):
- Skips tests (code hasn't changed, no need to re-test)
- Runs data cleaning directly
- Commits the cleaned output

**If code changed** (any .py file, engine/, config/rules/):
- Runs tests first
- Only runs data cleaning if tests pass
- This prevents broken code from processing data

**If both data and code changed**:
- Runs tests first
- Runs cleaning only if tests pass

### The jobs

The workflow has three jobs:

1. **changes** - Detects what files changed
2. **test** - Runs pytest (only if code changed)
3. **clean** - Runs main.py (only if tests passed or were skipped)

The `clean` job depends on the `test` job using the `needs` keyword, so it literally cannot run until tests complete.

See [WORKFLOW_LOGIC.md](WORKFLOW_LOGIC.md) for more details on how the workflow decides what to run.

### Workflow file

The main workflow is `.github/workflows/pipeline.yml`

You can manually trigger it from the Actions tab in GitHub, or it runs automatically on push to main.

## Why this setup is useful

**Modular rules**: Add new cleaning operations without changing core code

**Testing**: Integration tests verify the pipeline works before processing real data

**Smart CI/CD**: Only runs tests when code changes, saves time when just adding new data

**Audit trail**: Every pipeline run is logged with what rules ran and what changed

**Version control**: Cleaned data is committed with timestamps, so you have history

## Project Structure

```
.
├── main.py                    # Run the pipeline
├── test_pipeline.py           # Run the tests
├── requirements.txt           # pandas, pyyaml, pytest
├── README.md                  # This file
├── TEST_README.md             # Testing guide
├── WORKFLOW_LOGIC.md          # CI/CD workflow explanation
├── config/
│   └── rules/                 # Rule definitions (YAML)
├── engine/
│   ├── operations/            # Cleaning operations (Python)
│   ├── rule_registry.py       # Loads rules
│   ├── rule_executor.py       # Executes rules
│   └── audit_logger.py        # Logging
├── data/
│   ├── raw/                   # Input data
│   ├── processed/             # Cleaned output
│   ├── logs/                  # Audit logs
│   └── test/                  # Test fixtures
└── .github/
    └── workflows/
        └── pipeline.yml       # CI/CD workflow
```

## Dependencies

```
pandas      # Data processing
pyyaml      # Reading rule configs
pytest      # Running tests
```

## Development Workflow

1. Make changes to code or add new rules
2. Add test cases in `data/test/` if needed
3. Run tests locally: `pytest test_pipeline.py -v`
4. If tests pass, commit and push
5. GitHub Actions runs tests automatically
6. If tests pass, pipeline processes any new data
7. Cleaned data is committed back to the repo

## Notes

The pipeline adds metadata columns to the output:
- `rules_applied`: Which rules ran (e.g., "DQ-002,DQ-001")
- `run_id`: Unique ID for this pipeline run
- `run_timestamp`: When the pipeline ran

Output files include timestamps so you can track different runs over time.

The audit log at `data/logs/audit.csv` tracks every rule execution with before/after row counts and status.
