import yaml
import os
import glob


RULE_DIRECTORY = "config/rules"


def load_rules():

    rules = []

    rule_files = glob.glob(
        os.path.join(RULE_DIRECTORY, "*.yml")
    )

    for file in rule_files:

        with open(file, "r") as f:

            rule = yaml.safe_load(f)

            rules.append(rule)

    
    return rules