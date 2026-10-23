import os
from typing import Set
from yandex_disk import YandexDisk


def get_local_files(folder_path: str) -> Set[str]:
    """Возвращает множество имен файлов в локальной папке."""
    try:
        return set(os.listdir(folder_path))
    except OSError:
        return set()


def get_remote_files(disk_client: YandexDisk) -> Set[str]:
    """Возвращает множество имен файлов в удаленной папке."""
    info = disk_client.get_info()
    if not info or "_embedded" not in info:
        return set()
    
    items = info["_embedded"].get("items", [])
    # Фильтруем только файлы (не папки)
    return {item["name"] for item in items if item.get("type") == "file"}


def upload_new_files(local_files: Set[str], remote_files: Set[str], 
                     local_folder: str, disk_client: YandexDisk, logger) -> None:
    """Загружает файлы, которых нет в облаке."""
    files_to_upload = local_files - remote_files
    for filename in files_to_upload:
        full_path = os.path.join(local_folder, filename)
        success = disk_client.load(full_path)
        if success:
            logger.info(f"Файл {filename} успешно записан.")
        else:
            logger.error(f"Файл {filename} не записан. Ошибка соединения.")


def delete_missing_files(local_files: Set[str], remote_files: Set[str], 
                         disk_client: YandexDisk, logger) -> None:
    """Удаляет из облака файлы, которых нет локально."""
    files_to_delete = remote_files - local_files
    for filename in files_to_delete:
        success = disk_client.delete(filename)
        if success:
            logger.info(f"Файл {filename} успешно удален из облака.")
        else:
            logger.error(f"Файл {filename} не удален. Ошибка соединения.")


def update_existing_files(local_files: Set[str], remote_files: Set[str], 
                          local_folder: str, disk_client: YandexDisk, logger) -> None:
    """Перезаписывает файлы в облаке (новая версия локального файла)."""
    common_files = local_files & remote_files
    for filename in common_files:
        full_path = os.path.join(local_folder, filename)
        # По ТЗ: если файл изменился, его новая версия загружается.
        # Мы перезаписываем все общие файлы, чтобы гарантировать синхронизацию.
        success = disk_client.reload(full_path)
        if success:
            logger.info(f"Файл {filename} успешно перезаписан.")
        else:
            logger.error(f"Файл {filename} не перезаписан. Ошибка соединения.")


def sync_once(local_folder: str, disk_client: YandexDisk, logger) -> None:
    """Выполняет одну итерацию синхронизации."""
    local_files = get_local_files(local_folder)
    remote_files = get_remote_files(disk_client)

    upload_new_files(local_files, remote_files, local_folder, disk_client, logger)
    update_existing_files(local_files, remote_files, local_folder, disk_client, logger)
    delete_missing_files(local_files, remote_files, disk_client, logger)
