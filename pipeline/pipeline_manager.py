"""
pipeline_manager.py — вспомогательный модуль для управления пайплайном:
- запуск пайплайна
- логирование
- обработка ошибок
- (опционально) визуализация промежуточных результатов
"""

import logging
from pipeline.config import DEBUG

def setup_logging(log_file="pipeline.log"):
    """Настраивает логирование для пайплайна"""
    logging.basicConfig(
        level=logging.DEBUG if DEBUG else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def run_pipeline(process_func, *args, **kwargs):
    """Запускает основной пайплайн с обработкой ошибок и логированием"""
    setup_logging()
    try:
        logging.info("Пайплайн запущен")
        result = process_func(*args, **kwargs)
        logging.info("Пайплайн завершён успешно")
        return result
    except Exception as e:
        logging.exception(f"Ошибка в пайплайне: {e}")
        raise


if __name__ == "__main__":
    def dummy_pipeline(x):
        print(f"Работаем с {x}")
        return x * 2
    run_pipeline(dummy_pipeline, 5)