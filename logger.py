import logging


def setup_logger(log_file_path: str) -> logging.Logger:
    """Настраивает логгер для записи в файл и вывода в консоль."""
    logger = logging.getLogger("file_sync")
    logger.setLevel(logging.INFO)

    # Проверяем, есть ли уже хендлеры, чтобы не дублировать при перезапуске
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(name)s %(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Хендлер для файла
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Хендлер для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
