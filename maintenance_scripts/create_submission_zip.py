import zipfile
import os

output_dir = "output"
zip_filename = "submission.zip"

files_to_zip = [
    "task-a-en.tsv",
    "task-a-es.tsv",
    "task-a-zh.tsv",
    "task-b1.tsv",
    "task-b2.tsv"
]

print(f"Creating {zip_filename}...")

with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for filename in files_to_zip:
        file_path = os.path.join(output_dir, filename)
        if os.path.exists(file_path):
            print(f"  Adding {filename}...")
            zipf.write(file_path, arcname=filename)
        else:
            print(f"  [ERROR] File not found: {filename}")

print(f"\n[SUCCESS] {zip_filename} created successfully!")
print(f"Location: {os.path.abspath(zip_filename)}")
