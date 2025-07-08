import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms, datasets
from model import initialize_model
import numpy as np


# Конфигурация
class Config:
    data_dir = "../dataset"
    model_save_path = "../models/classifier_cnn.pth"
    batch_size = 32
    num_epochs = 50
    learning_rate = 0.001
    num_classes = 31  # Количество классов музыкальных символов
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def get_dataloaders():
    """Создание DataLoader для train и validation"""

    # Трансформации для изображений
    transform = transforms.Compose([
        transforms.Grayscale(),
        transforms.Resize((64, 64)),
        transforms.RandomRotation(10),  # Случайный поворот
        transforms.RandomAffine(0, translate=(0.1, 0.1)),  # Сдвиг
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5])
    ])

    # Загрузка данных
    train_dataset = datasets.ImageFolder(
        root=os.path.join(Config.data_dir, 'train'),
        transform=transform
    )

    val_dataset = datasets.ImageFolder(
        root=os.path.join(Config.data_dir, 'val'),
        transform=transform
    )

    # DataLoader
    train_loader = DataLoader(
        train_dataset,
        batch_size=Config.batch_size,
        shuffle=True,
        drop_last=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=Config.batch_size,
        shuffle=False
    )

    return train_loader, val_loader, train_dataset.classes


def train_model():
    """Обучение модели классификации"""

    # Получение данных
    train_loader, val_loader, class_names = get_dataloaders()

    # Инициализация модели
    model = initialize_model(Config.num_classes, Config.device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=Config.learning_rate)

    best_accuracy = 0.0

    print(f"Обучение на устройстве: {Config.device}")
    print(f"Количество классов: {Config.num_classes}")
    print(f"Размер тренировочного батча: {len(train_loader.dataset)}")
    print(f"Размер валидационного батча: {len(val_loader.dataset)}")

    for epoch in range(Config.num_epochs):
        # Режим обучения
        model.train()
        running_loss = 0.0

        for images, labels in train_loader:
            images = images.to(Config.device)
            labels = labels.to(Config.device)

            # Обнуление градиентов
            optimizer.zero_grad()

            # Forward pass
            outputs = model(images)
            loss = criterion(outputs, labels)

            # Backward pass и оптимизация
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)

        # Валидация
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(Config.device)
                labels = labels.to(Config.device)

                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * images.size(0)

                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        # Статистика эпохи
        train_loss = running_loss / len(train_loader.dataset)
        val_loss = val_loss / len(val_loader.dataset)
        val_accuracy = 100 * correct / total

        print(f"Epoch {epoch + 1}/{Config.num_epochs} | "
              f"Train Loss: {train_loss:.4f} | "
              f"Val Loss: {val_loss:.4f} | "
              f"Val Acc: {val_accuracy:.2f}%")

        # Сохранение лучшей модели
        if val_accuracy > best_accuracy:
            best_accuracy = val_accuracy
            torch.save({
                'model_state_dict': model.state_dict(),
                'class_names': class_names,
                'num_classes': Config.num_classes
            }, Config.model_save_path)
            print(f"Модель сохранена с точностью {val_accuracy:.2f}%")

    print(f"Обучение завершено. Лучшая точность: {best_accuracy:.2f}%")


if __name__ == "__main__":
    train_model()