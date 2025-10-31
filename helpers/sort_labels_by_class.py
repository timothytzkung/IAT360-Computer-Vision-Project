import argparse
import shutil
from pathlib import Path

def read_classes(classes_file: Path):
    """Read class names from classes.txt into a list."""
    return [line.strip() for line in classes_file.read_text().splitlines() if line.strip()]

def parse_label_file(label_file: Path):
    """Read all class indices present in a YOLO label file."""
    classes = set()
    with open(label_file) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            try:
                cls_id = int(parts[0])
                classes.add(cls_id)
            except ValueError:
                continue
    return list(classes)

def sort_labels(labels_dir: Path, classes_file: Path, output_dir: Path,
                strategy: str = "duplicate", mode: str = "copy"):
    """
    Sort YOLO label text files into per-class folders.

    strategy:
      - 'duplicate': place the same label file into every class folder it contains.
      - 'first': use only the first class found in the file.
      - 'largest': same as 'first' here (YOLO txt has no box area data after parsing) — can customize if needed.

    mode:
      - 'copy': copy files into class folders.
      - 'move': move files (removes original).
      - 'symlink': create symlinks (UNIX only).
    """
    class_names = read_classes(classes_file)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in class_names:
        (output_dir / name).mkdir(parents=True, exist_ok=True)

    label_files = sorted(labels_dir.glob("*.txt"))
    for lf in label_files:
        class_ids = parse_label_file(lf)
        if not class_ids:
            continue

        # strategy
        if strategy == "first" and class_ids:
            chosen = [class_ids[0]]
        else:
            chosen = class_ids

        for cid in chosen:
            if cid < 0 or cid >= len(class_names):
                continue
            class_name = class_names[cid]
            dst = output_dir / class_name / lf.name
            if mode == "move":
                shutil.move(str(lf), str(dst))
            elif mode == "symlink":
                try:
                    dst.symlink_to(lf)
                except FileExistsError:
                    pass
            else:
                shutil.copy2(lf, dst)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sort YOLO label .txt files into per-class folders.")
    parser.add_argument("--labels", required=True, help="Path to YOLO labels directory")
    parser.add_argument("--classes", required=True, help="Path to classes.txt")
    parser.add_argument("--out", required=True, help="Output root for sorted label files")
    parser.add_argument("--strategy", choices=["duplicate", "first"], default="duplicate")
    parser.add_argument("--mode", choices=["copy", "move", "symlink"], default="copy")
    args = parser.parse_args()

    sort_labels(
        labels_dir=Path(args.labels),
        classes_file=Path(args.classes),
        output_dir=Path(args.out),
        strategy=args.strategy,
        mode=args.mode
    )