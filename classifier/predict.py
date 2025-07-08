import torch
from torchvision import transforms
from PIL import Image
from model import initialize_model
import numpy as np


def load_model(model_path, device='cpu'):
    """Загрузка обученной модели"""
    checkpoint = torch.load(model_path, map_location=device)
    model = initialize_model(checkpoint['num_classes'], device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    return model, checkpoint['class_names']


def preprocess_image(image_path):
    """Предобработка изображения для предсказания"""
    transform = transforms.Compose([
        transforms.Grayscale(),
        transforms.Resize((64, 64)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5])
    ])

    image = Image.open(image_path)
    image = transform(image).unsqueeze(0)  # Добавляем batch dimension
    return image


def predict_symbol(image_path, model_path, class_names, confidence_threshold=0.5, device='cpu'):
    """
    Предсказание класса музыкального символа

    Аргументы:
        image_path: путь к изображению символа
        model_path: путь к сохраненной модели
        class_names: список названий классов
        confidence_threshold: минимальная уверенность для предсказания
        device: устройство для вычислений (cpu/cuda)

    Возвращает:
        Словарь с предсказанным классом и уверенностью
        или None, если уверенность ниже порога
    """
    # Загрузка модели и изображения
    model, loaded_class_names = load_model(model_path, device)
    image = preprocess_image(image_path).to(device)

    # Предсказание
    with torch.no_grad():
        outputs = model(image)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities, 1)
        confidence = confidence.item()
        predicted_class = loaded_class_names[predicted.item()]

    # Проверка порога уверенности
    if confidence < confidence_threshold:
        return None

    return {
        'class': predicted_class,
        'confidence': confidence,
        'all_probs': {class_name: prob.item() for class_name, prob in zip(loaded_class_names, probabilities[0])}
    }