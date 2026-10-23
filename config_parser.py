import configparser
import os
import sys


def read_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        print(f"Ошибка: Файл конфигурации {config_path} не найден.")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf-8")

    try:
        settings = config["Settings"]
    except KeyError:
        print("Ошибка: В файле конфигурации отсутствует секция [Settings].")
        sys.exit(1)

    local_folder = settings.get("local_folder")
    if not local_folder or not os.path.isdir(local_folder):
        print(f"Ошибка: Локальная папка '{local_folder}' не существует или не является директорией.")
        sys.exit(1)

    token = settings.get("token", "").strip()
    if not token:
        print("Ошибка: Токен доступа к Яндекс.Диску не указан в config.ini.")
        sys.exit(1)

    return {
        "local_folder": local_folder,
        "remote_folder": settings.get("remote_folder", "backup_folder"),
        "token": token,
        "sync_period": settings.getint("sync_period", 10),
        "log_file": settings.get("log_file", "sync.log"),
    }
