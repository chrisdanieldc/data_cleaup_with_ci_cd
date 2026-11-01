"""
Integration tests for data quality pipeline
Compares actual output with expected output
"""

import pandas as pd
import os


def test_orders_csv():
    """
    Test the pipeline with orders.csv

    Steps:
    1. Read test input CSV
    2. Apply data cleaning (replace nulls, remove duplicates)
    3. Compare with expected output
    """

    input_csv = "data/test/source/orders.csv"
    expected_csv = "data/test/after_test/orders.csv"
    output_csv = "data/test/output/orders.csv"

    # Skip if test files don't exist
    if not os.path.exists(input_csv):
        print(f"Skipping: {input_csv} not found")
        return

    if not os.path.exists(expected_csv):
        print(f"Skipping: {expected_csv} not found")
        return

    # Create output directory
    os.makedirs("data/test/output", exist_ok=True)

    # Read input data
    df = pd.read_csv(input_csv)
    print(f"Loaded {len(df)} rows from {input_csv}")

    # Apply cleaning operations
    null_count = df['amount'].isnull().sum()
    df['amount'] = df['amount'].fillna(0)
    print(f"Replaced {null_count} null values with 0")

    rows_before = len(df)
    df = df.drop_duplicates(keep='first')
    df = df.reset_index(drop=True)
    rows_removed = rows_before - len(df)
    print(f"Removed {rows_removed} duplicate rows")

    # Save output
    df.to_csv(output_csv, index=False)
    print(f"Saved output to {output_csv}")

    # Compare with expected
    expected_df = pd.read_csv(expected_csv)
    pd.testing.assert_frame_equal(df, expected_df, check_dtype=False)
    print("PASSED - Output matches expected")


def test_all_csv_files():
    """
    Test all CSV files in the source folder

    For each CSV in source/:
    - Run the pipeline
    - Compare with corresponding file in after_test/
    """

    source_folder = "data/test/source"
    expected_folder = "data/test/after_test"
    output_folder = "data/test/output"

    # Create output directory
    os.makedirs(output_folder, exist_ok=True)

    # Find all CSV files
    csv_files = [f for f in os.listdir(source_folder) if f.endswith('.csv')]

    if not csv_files:
        print("No CSV files found in source folder")
        return

    print(f"Found {len(csv_files)} CSV file(s) to test\n")

    results = []

    for csv_file in csv_files:
        print(f"{'='*60}")
        print(f"Testing: {csv_file}")
        print(f"{'='*60}")

        input_path = os.path.join(source_folder, csv_file)
        expected_path = os.path.join(expected_folder, csv_file)
        output_path = os.path.join(output_folder, csv_file)

        # Skip if expected file doesn't exist
        if not os.path.exists(expected_path):
            print(f"WARNING: No expected file for {csv_file}, skipping\n")
            continue

        # Read input
        df = pd.read_csv(input_path)
        print(f"Loaded {len(df)} rows")

        # Apply cleaning operations
        null_count = df['amount'].isnull().sum()
        df['amount'] = df['amount'].fillna(0)
        print(f"Replaced {null_count} nulls")

        rows_before = len(df)
        df = df.drop_duplicates(keep='first')
        df = df.reset_index(drop=True)
        print(f"Removed {rows_before - len(df)} duplicates")

        # Save output
        df.to_csv(output_path, index=False)

        # Compare with expected
        expected_df = pd.read_csv(expected_path)

        try:
            pd.testing.assert_frame_equal(df, expected_df, check_dtype=False)
            print(f"PASSED: {csv_file}\n")
            results.append((csv_file, True))
        except AssertionError as e:
            print(f"FAILED: {csv_file}")
            print(f"Difference: {e}\n")
            results.append((csv_file, False))

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    for filename, result in results:
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {filename}")

    # Assert all tests passed
    all_passed = all(result for _, result in results)
    assert all_passed, f"Some tests failed: {passed}/{total} passed"


if __name__ == "__main__":
    print("Running pipeline tests\n")

    # Test orders.csv
    test_orders_csv()

    print("\n" + "="*60 + "\n")

    # Test all CSV files
    test_all_csv_files()
