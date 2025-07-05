import cv2
import albumentations as A
from pathlib import Path
import os
import logging
from tqdm import tqdm


class MusicSymbolAugmenter:
    def __init__(self):
        """Инициализация трансформаций с правильными параметрами"""
        self.train_transform = A.Compose([
            A.Rotate(limit=15, border_mode=cv2.BORDER_REFLECT, p=0.7),
            A.ShiftScaleRotate(shift_limit=0.05, scale_limit=0.1, rotate_limit=0, p=0.5),
            A.HorizontalFlip(p=0.3),
            A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.7),
            A.GaussNoise(var_limit=(10.0, 50.0), p=0.5),
            A.ElasticTransform(alpha=1, sigma=50, p=0.3),
        ])

        self.val_transform = A.Compose([
            A.Rotate(limit=10, p=0.5),
            A.RandomBrightnessContrast(brightness_limit=0.1, contrast_limit=0.1, p=0.5),
        ])

    def augment_dataset(self,
                        train_path: str = r"C:\Users\user\Documents\GitHub\music-symbols-detector\dataset\train",
                        val_path: str = None,
                        output_dir: str = r"C:\Users\user\Documents\GitHub\music-symbols-detector\augmented_dataset",
                        train_augmentations: int = 3,
                        val_augmentations: int = 1):
        """
        Аугментирует весь датасет

        Args:
            train_path: Путь к тренировочным данным
            val_path: Путь к валидационным данным (опционально)
            output_dir: Директория для сохранения
            train_augmentations: Количество аугментаций для train
            val_augmentations: Количество аугментаций для val
        """
        try:
            # Проверка и создание директорий
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Обработка тренировочных данных
            if os.path.exists(train_path):
                self._process_split(
                    input_path=train_path,
                    output_path=os.path.join(output_dir, "train"),
                    transform=self.train_transform,
                    augmentations_per_image=train_augmentations
                )
            else:
                logging.error(f"Train directory not found: {train_path}")

            # Обработка валидационных данных (если указаны)
            if val_path and os.path.exists(val_path):
                self._process_split(
                    input_path=val_path,
                    output_path=os.path.join(output_dir, "val"),
                    transform=self.val_transform,
                    augmentations_per_image=val_augmentations
                )

            logging.info("Аугментация завершена успешно!")

        except Exception as e:
            logging.error(f"Ошибка при аугментации: {str(e)}")
            raise

    def _process_split(self, input_path: str, output_path: str,
                       transform: A.Compose, augmentations_per_image: int):
        """Обрабатывает одну часть датасета (train/val)"""
        logging.info(f"Обработка {input_path}...")

        # Получаем список классов
        class_dirs = [d for d in os.listdir(input_path)
                      if os.path.isdir(os.path.join(input_path, d))]

        for class_dir in tqdm(class_dirs, desc="Classes"):
            # Создаем выходную директорию
            output_class_dir = os.path.join(output_path, class_dir)
            Path(output_class_dir).mkdir(parents=True, exist_ok=True)

            # Обрабатываем изображения
            input_class_dir = os.path.join(input_path, class_dir)
            for img_file in os.listdir(input_class_dir):
                if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(input_class_dir, img_file)
                    img = cv2.imread(img_path)

                    if img is not None:
                        # Сохраняем оригинал
                        orig_path = os.path.join(output_class_dir, f"orig_{img_file}")
                        cv2.imwrite(orig_path, img)

                        # Генерируем аугментированные версии
                        for i in range(augmentations_per_image):
                            augmented = transform(image=img)["image"]
                            aug_path = os.path.join(
                                output_class_dir,
                                f"aug_{i}_{img_file}"
                            )
                            cv2.imwrite(aug_path, augmented)
                    else:
                        logging.warning(f"Не удалось загрузить {img_path}")


if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Инициализация и запуск
    augmenter = MusicSymbolAugmenter()

    # Укажите путь к валидационным данным, если они есть
    val_path = r"C:\Users\user\Documents\GitHub\music-symbols-detector\dataset\val"

    augmenter.augment_dataset(
        train_path=r"C:\Users\user\Documents\GitHub\music-symbols-detector\dataset\train",
        val_path=val_path if os.path.exists(val_path) else None,
        output_dir=r"C:\Users\user\Documents\GitHub\music-symbols-detector\augmented_dataset",
        train_augmentations=3,
        val_augmentations=1
    )