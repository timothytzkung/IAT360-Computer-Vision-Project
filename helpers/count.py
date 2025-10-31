import os
import re
import shutil

def move_files(src_folder, dest_folder, num=30):
    pattern = re.compile(r"^(\d+)")
    
    # Make sure destination folder exists
    os.makedirs(dest_folder, exist_ok=True)

    count = 0
    for filename in os.listdir(src_folder):
        if count >= num:
            return
        src_path = os.path.join(src_folder, filename)
        shutil.move(src_path, dest_folder)
        count += 1
    return

def main():
    move_files("input", "cleaned")

if __name__ == "__main__":
    main()

