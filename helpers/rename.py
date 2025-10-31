import os
import re

def rename_files_to_number(folder):
    pattern = re.compile(r"^(\d+)")
    
    for filename in os.listdir(folder):
        match = pattern.match(filename)
        if match:
            number = match.group(1)
            ext = os.path.splitext(filename)[1]  # keeps the original file extension
            new_name = f"{number}{ext}"
            
            old_path = os.path.join(folder, filename)
            new_path = os.path.join(folder, new_name)

            # Only rename if new name is different
            if old_path != new_path:
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} → {new_name}")
        else:
            print(f"Skipped (no number at start): {filename}")

# Example usage:
# rename_files_to_number("path/to/your/folder")

def main():
    rename_files_to_number("cleaned")


if __name__ == "__main__":
    main()
