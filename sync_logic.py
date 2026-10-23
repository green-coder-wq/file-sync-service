import os
from typing import Set
from yandex_disk import YandexDisk


def get_local_files(folder_path: str) -> Set[str]:
    try:
        return set(os.listdir(folder_path))
    except OSError:
        return set()


def get_remote_files(disk_client: YandexDisk) -> Set[str]:
    info = disk_client.get_info()
    if not info or "_embedded" not in info:
        return set()
    items = info["_embedded"].get("items", [])
    return {item["name"] for item in items if item.get("type") == "file"}


def get_file_size(path: str) -> int:
    try:
        return os.path.getsize(path)
    except OSError:
        return -1


def upload_new_files(local_files: Set[str], remote_files: Set[str], local_folder: str, disk_client: YandexDisk, logger) -> None:
    files_to_upload = local_files - remote_files
    for filename in files_to_upload:
        full_path = os.path.join(local_folder, filename)
        success = disk_client.load(full_path)
        if success:
            logger.info(f"Файл {filename} успешно записан.")
        else:
            logger.error(f"Файл {filename} не записан. Ошибка соединения.")


def delete_missing_files(local_files: Set[str], remote_files: Set[str], disk_client: YandexDisk, logger) -> None:
    files_to_delete = remote_files - local_files
    for filename in files_to_delete:
        success = disk_client.delete(filename)
        if success:
            logger.info(f"Файл {filename} успешно удален из облака.")
        else:
            logger.error(f"Файл {filename} не удален. Ошибка соединения.")


def update_existing_files(local_files: Set[str], remote_files: Set[str], local_folder: str, disk_client: YandexDisk, logger) -> None:
    common_files = local_files & remote_files
    for filename in common_files:
        full_path = os.path.join(local_folder, filename)
        local_size = get_file_size(full_path)
        
        if local_size == -1:
            logger.error(f"Файл {filename} не перезаписан. Ошибка чтения локального файла.")
            continue

        # По ТЗ: "При изменении локального файла его новая версия загружается".
        # Так как мы не храним хеши, перезаписываем только если размер изменился.
        # Для простоты и надежности (чтобы не пропустить изменения) перезаписываем всегда.
        # Но чтобы не спамить, можно добавить проверку. Оставим перезапись.
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
