import os
import random
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt


dataset_path = Path("C:/...")
save_path = Path("C:/...")


def main(dataset_path, num_images=5, save_to=None):

    # dataset_path - Путь к проверяемому датасету
    # num_images - Количество случайных изобржений из одного класса
    # save_to - Путь к папке для сохранения общей таблицы с изображениями

    if save_to is not None:
        Path(save_to).mkdir(parents=True, exist_ok=True)

    # Получаем список классов
    classes = [d.name for d in Path(dataset_path).iterdir() if d.is_dir()]
    classes.sort()  # Сортируем для удобства

    class_images = {}
    for class_name in classes:
        class_dir = Path(dataset_path) / class_name
        images = list(class_dir.glob('*.*'))
        # Оставляем только изображения
        images = [img for img in images if img.suffix.lower() in ['.jpg', '.jpeg', '.png']]
        # Предупреждение о пустой папке
        if not images:
            print(f"[!] Класс {class_name} не содержит изображений!")

        class_images[class_name] = images

    # Создаем фигуру для отображения
    fig, axes = plt.subplots(len(classes), num_images, figsize=(10, 3 * len(classes)), gridspec_kw={'hspace': 0.15})

    if len(classes) == 1:
        axes = [axes]  # Чтобы избежать проблем с индексацией для одного класса

    # Заполняем plt-таблицу изображениями
    for row, class_name in enumerate(classes):
        images = class_images[class_name]
        # Выбираем случайные изображения из папки класса
        selected_images = random.sample(images, min(num_images, len(images))) if images else []

        for col in range(num_images):
            ax = axes[row, col] if len(classes) > 1 else axes[col]
            ax.axis('off')

            if col < len(selected_images):
                img_path = selected_images[col]
                try:
                    img = Image.open(img_path)
                    ax.imshow(img)
                    ax.set_title(f"{class_name}\n{img_path.name}", fontsize=4)
                except Exception as e:
                    ax.text(0.5, 0.5, f"Error\n{img_path.name}", ha='center', va='center', fontsize=2)
                    print(f"Error loading {img_path}: {e}")
            else:
                ax.text(0.5, 0.5, "No image", ha='center', va='center', fontsize=6)

    if save_to is not None:
        output_path = Path(save_to) / "review_table.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to: {output_path}")

    plt.show()

if __name__ == '__main__':
    main(dataset_path, num_images=5, save_to=save_path)

