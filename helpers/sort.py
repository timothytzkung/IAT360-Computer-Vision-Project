import os
import re
import shutil

def sort_files_by_number(src_folder, dest_folder):
    pattern = re.compile(r"^(\d+)")
    
    # Make sure destination folder exists
    os.makedirs(dest_folder, exist_ok=True)

    for filename in os.listdir(src_folder):
        match = pattern.match(filename)
        if match:
            number = match.group(1)
            src_path = os.path.join(src_folder, filename)

            if (int(number) % 2 == 0):
                shutil.move(src_path, dest_folder)
            else:
                print(f"Skipped: {filename}")

def main():
    sort_files_by_number("input", "cleaned_v2")

if __name__ == "__main__":
    main()

