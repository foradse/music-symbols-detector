import os
import shutil
import random
from pathlib import Path

SOURCE_POS = Path("recognize_old/positive_images")
SOURCE_NEG = Path("recognize_old/negative_images")
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


    print("\nПроверка классов в recognize_old/positive_images:")
    pos_classes = [cls for cls in os.listdir(SOURCE_POS) if (SOURCE_POS / cls).is_dir()]
    total_pos = 0
    for cls in pos_classes:
        files = []
        for ext in ("*.png", "*.jpg", "*.jpeg", "*.JPG", "*.JPEG"):
            files.extend((SOURCE_POS / cls).glob(ext))
        print(f"  {cls}: {len(files)} файлов")
        total_pos += len(files)
    if total_pos == 0:
        print("[!] Нет данных в recognize_old/positive_images. Проверьте структуру и наличие файлов.")

    neg_files = []
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.JPG", "*.JPEG"):
        neg_files.extend(SOURCE_NEG.rglob(ext))
    print(f"\nНегативные примеры: {len(neg_files)} файлов в recognize_old/negative_images")
    if len(neg_files) == 0:
        print("[!] Нет данных в recognize_old/negative_images. Проверьте структуру и наличие файлов.")

    for split in ['train', 'val']:
        for cls in pos_classes:
            prepare_dir(DEST / split / cls)
        prepare_dir(DEST / split / 'negative')


    for cls in pos_classes:
        cls_path = SOURCE_POS / cls
        files = []
        for ext in ("*.png", "*.jpg", "*.jpeg", "*.JPG", "*.JPEG"):
            files.extend(cls_path.glob(ext))
        split_and_copy(files, DEST / 'train' / cls, DEST / 'val' / cls)

    split_and_copy(neg_files, DEST / 'train' / 'negative', DEST / 'val' / 'negative')
    print("\n Датасет собран в папке /dataset")

if __name__ == "__main__":
    main() 