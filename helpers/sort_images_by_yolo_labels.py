
import argparse, shutil
from pathlib import Path

def read_classes(classes_txt: Path):
    return [line.strip() for line in classes_txt.read_text().splitlines() if line.strip()]

def parse_label_line(line):
    parts = line.strip().split()
    if len(parts) != 5:
        return None
    cls = int(parts[0])
    cx, cy, w, h = map(float, parts[1:])
    return cls, cx, cy, w, h

def choose_class(labels, strategy="duplicate"):
    """
    labels: list[(cls, cx, cy, w, h)]
    strategy:
      - duplicate: return all class ids (duplicate or link image into each class)
      - first: return [first class id seen]
      - largest: return [class id of bbox with largest area w*h]
    """
    if not labels:
        return []
    if strategy == "first":
        return [labels[0][0]]
    if strategy == "largest":
        cls, *_ = max(labels, key=lambda t: t[3]*t[4])
        return [cls]
    # default duplicate
    return list({t[0] for t in labels})

def find_image(images_dir: Path, stem: str):
    for ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
        p = images_dir / f"{stem}{ext}"
        if p.exists():
            return p
    return None

def main():
    ap = argparse.ArgumentParser(description="Sort full images into per-class folders based on YOLO detection labels.")
    ap.add_argument("--images", required=True, help="Images dir (e.g., datasets/parts_multi/images/train)")
    ap.add_argument("--labels", required=True, help="Labels dir (e.g., datasets/parts_multi/labels/train)")
    ap.add_argument("--classes", required=True, help="Path to classes.txt (YOLO order)")
    ap.add_argument("--out", required=True, help="Output root for classification-style folders (e.g., cls_images/train)")
    ap.add_argument("--strategy", choices=["duplicate", "first", "largest"], default="duplicate",
                    help="How to handle images with multiple classes in labels")
    ap.add_argument("--mode", choices=["copy", "move", "symlink"], default="copy",
                    help="File operation for placing images into class folders")
    args = ap.parse_args()

    images_dir = Path(args.images)
    labels_dir = Path(args.labels)
    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    class_names = read_classes(Path(args.classes))

    # create class folders
    for name in class_names:
        (out_root / name).mkdir(parents=True, exist_ok=True)

    label_files = sorted(labels_dir.glob("*.txt"))
    assigned, missing_img, empty_labels = 0, 0, 0
    for lf in label_files:
        stem = lf.stem
        img_path = find_image(images_dir, stem)
        if img_path is None:
            missing_img += 1
            continue

        labels = []
        for line in lf.read_text().splitlines():
            parsed = parse_label_line(line)
            if parsed is not None:
                labels.append(parsed)

        if not labels:
            empty_labels += 1
            continue

        chosen = choose_class(labels, args.strategy)
        for cls in chosen:
            cls_name = class_names[cls] if 0 <= cls < len(class_names) else f"class_{cls}"
            dst = out_root / cls_name / img_path.name
            if args.mode == "symlink":
                try:
                    dst.symlink_to(img_path)
                except FileExistsError:
                    pass
            elif args.mode == "move":
                if dst.exists():
                    continue
                shutil.move(str(img_path), str(dst))
            else:  # copy
                if dst.exists():
                    continue
                shutil.copy2(str(img_path), str(dst))
            assigned += 1

    print({
        "label_files": len(label_files),
        "assigned_entries": assigned,
        "missing_images": missing_img,
        "empty_label_files": empty_labels,
        "output_root": str(out_root)
    })

if __name__ == "__main__":
    main()
