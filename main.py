import sys
import time

from config_parser import read_config
from logger import setup_logger
from sync_logic import sync_once
from yandex_disk import YandexDisk


def main() -> None:
    try:
        settings = read_config("config.ini")
    except SystemExit:
        sys.exit(1)

    logger = setup_logger(settings["log_file"])
    logger.info(f"Программа синхронизации файлов начинает работу с директорией {settings['local_folder']}.")

    disk_client = YandexDisk(settings["token"], settings["remote_folder"])

    # Проверка доступа к облаку
    test_info = disk_client.get_info()
    if not test_info:
        logger.error("Ошибка подключения к Яндекс.Диску. Проверьте токен и имя папки.")
        sys.exit(1)

    while True:
        try:
            sync_once(settings["local_folder"], disk_client, logger)
        except Exception as error:
            logger.error(f"Непредвиденная ошибка в процессе синхронизации: {error}")
        time.sleep(settings["sync_period"])


if __name__ == "__main__":
    main()
