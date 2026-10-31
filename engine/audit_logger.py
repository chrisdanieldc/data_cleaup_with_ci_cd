import pandas as pd
import os


def log_execution(audit_record):

    audit_file = "data/logs/audit.csv"

    os.makedirs(
        "data/logs",
        exist_ok=True
    )

    audit = pd.DataFrame([audit_record])

    audit.to_csv(
        audit_file,
        mode="a",
        header=not os.path.exists(audit_file),
        index=False
    )