import pandas as pd
import os

tasks = ["task-a-en.tsv", "task-a-es.tsv", "task-a-zh.tsv", "task-b1.tsv", "task-b2.tsv"]
output_dir = "output"

print("Results of Final Row Count Verification:")
for task in tasks:
    path = os.path.join(output_dir, task)
    if os.path.exists(path):
        df = pd.read_csv(path, sep='\t')
        print(f"{task}: {len(df)} rows")
    else:
        print(f"{task}: NOT FOUND")
