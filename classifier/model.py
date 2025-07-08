import torch
import torch.nn as nn
import torch.nn.functional as F


class MusicSymbolClassifier(nn.Module):
    """
    CNN для классификации музыкальных символов.
    Вход: 64x64 grayscale изображение
    Выход: вероятность принадлежности к каждому классу
    """

    def __init__(self, num_classes):
        super(MusicSymbolClassifier, self).__init__()

        # Сверточные слои
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)
        self.conv4 = nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1)

        # Max pooling
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

        # Dropout для регуляризации
        self.dropout = nn.Dropout(0.25)

        # Полносвязные слои
        self.fc1 = nn.Linear(4096, 512)
        self.fc2 = nn.Linear(512, num_classes)

    def forward(self, x):
        # Размеры: (batch_size, 1, 64, 64)

        # Первый сверточный блок
        x = F.relu(self.conv1(x))  # (32, 64, 64)
        x = self.pool(x)  # (32, 32, 32)

        # Второй сверточный блок
        x = F.relu(self.conv2(x))  # (64, 32, 32)
        x = self.pool(x)  # (64, 16, 16)

        # Третий сверточный блок
        x = F.relu(self.conv3(x))  # (128, 16, 16)
        x = self.pool(x)  # (128, 8, 8)

        # Четвёртый сверточный блок
        x = F.relu(self.conv4(x))
        x = self.pool(x)

        # Выравнивание для полносвязных слоев
        x = x.view(x.size(0), -1)

        # Полносвязные слои с dropout
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)

        return x


def initialize_model(num_classes, device='cpu'):
    """Инициализация модели и перемещение на устройство (CPU/GPU)"""
    model = MusicSymbolClassifier(num_classes)
    return model.to(device)