import os
from typing import Dict, Set
from yandex_disk import YandexDisk


def get_local_files(folder_path: str) -> Set[str]:
    try:
        return set(os.listdir(folder_path))
    except OSError:
        return set()


def get_remote_files(disk_client: YandexDisk) -> Dict[str, int]:
    """Возвращает словарь {имя_файла: размер} для файлов в облаке."""
    info = disk_client.get_info()
    if not info or "_embedded" not in info:
        return {}
    items = info["_embedded"].get("items", [])
    return {item["name"]: item.get("size", 0) for item in items if item.get("type") == "file"}


def get_file_size(path: str) -> int:
    try:
        return os.path.getsize(path)
    except OSError:
        return -1


def upload_new_files(local_files: Set[str], remote_files: Dict[str, int], local_folder: str, disk_client: YandexDisk, logger) -> None:
    files_to_upload = local_files - set(remote_files.keys())
    for filename in files_to_upload:
        full_path = os.path.join(local_folder, filename)
        success = disk_client.load(full_path)
        if success:
            logger.info(f"Файл {filename} успешно записан.")
        else:
            logger.error(f"Файл {filename} не записан. Ошибка соединения.")


def delete_missing_files(local_files: Set[str], remote_files: Dict[str, int], disk_client: YandexDisk, logger) -> None:
    files_to_delete = set(remote_files.keys()) - local_files
    for filename in files_to_delete:
        success = disk_client.delete(filename)
        if success:
            logger.info(f"Файл {filename} успешно удален из облака.")
        else:
            logger.error(f"Файл {filename} не удален. Ошибка соединения.")


def update_existing_files(local_files: Set[str], remote_files: Dict[str, int], local_folder: str, disk_client: YandexDisk, logger) -> None:
    common_files = local_files & set(remote_files.keys())
    for filename in common_files:
        full_path = os.path.join(local_folder, filename)
        local_size = get_file_size(full_path)
        remote_size = remote_files[filename]

        if local_size == -1:
            logger.error(f"Файл {filename} не перезаписан. Ошибка чтения локального файла.")
            continue

        if local_size != remote_size:
            success = disk_client.reload(full_path)
            if success:
                logger.info(f"Файл {filename} успешно перезаписан.")
            else:
                logger.error(f"Файл {filename} не перезаписан. Ошибка соединения.")


def sync_once(local_folder: str, disk_client: YandexDisk, logger) -> None:
    local_files = get_local_files(local_folder)
    remote_files = get_remote_files(disk_client)

    upload_new_files(local_files, remote_files, local_folder, disk_client, logger)
    update_existing_files(local_files, remote_files, local_folder, disk_client, logger)
    delete_missing_files(local_files, remote_files, disk_client, logger)
