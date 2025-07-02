import os
import shutil
import random
from pathlib import Path

SOURCE_POS = Path("recognize/positive_images")
SOURCE_NEG = Path("recognize/negative_images")
DEST = Path("dataset")
SPLIT_RATIO = 0.8  # 80% train, 20% val

def prepare_dir(path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)

def split_and_copy(src_paths, train_dir, val_dir):
    random.shuffle(src_paths)
    split_idx = int(len(src_paths) * SPLIT_RATIO)
    train_files = src_paths[:split_idx]
    val_files = src_paths[split_idx:]

    for f in train_files:
        shutil.copy(f, train_dir / f.name)
    for f in val_files:
        shutil.copy(f, val_dir / f.name)

def main():
    random.seed(42)


    for split in ['train', 'val']:
        for cls in os.listdir(SOURCE_POS):
            prepare_dir(DEST / split / cls)
        prepare_dir(DEST / split / 'negative')


    for cls in os.listdir(SOURCE_POS):
        cls_path = SOURCE_POS / cls
        if not cls_path.is_dir():
            continue
        files = list(cls_path.glob("*.png"))
        split_and_copy(files, DEST / 'train' / cls, DEST / 'val' / cls)


    neg_files = list(SOURCE_NEG.glob("*.png"))
    split_and_copy(neg_files, DEST / 'train' / 'negative', DEST / 'val' / 'negative')

    print("✅ Датасет собран в папке /dataset")

if __name__ == "__main__":
    main() 