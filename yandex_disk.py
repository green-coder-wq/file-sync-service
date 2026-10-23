import os
import requests


class YandexDisk:
    """Класс для работы с API Яндекс.Диска."""

    BASE_URL = "https://cloud-api.yandex.net/v1/disk/resources"

    def __init__(self, token: str, remote_folder: str):
        """Инициализация клиента.
        
        :param token: OAuth-токен Яндекс.Диска.
        :param remote_folder: Имя папки на Яндекс.Диске.
        """
        self.token = token
        self.remote_folder = remote_folder.strip("/")
        self.headers = {
            "Authorization": f"OAuth {self.token}"
        }

    def get_info(self) -> dict:
        """Получает информацию о файлах в удаленной папке.
        
        :return: Словарь с метаданными папки (включая список файлов) или пустой словарь при ошибке.
        """
        url = f"{self.BASE_URL}?path={self.remote_folder}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            if response.status_code == 401:
                raise ValueError("Неверный токен Яндекс.Диска.")
            return {}
        except requests.RequestException:
            return {}

    def load(self, local_path: str) -> bool:
        """Загружает новый файл в облако.
        
        :param local_path: Путь к локальному файлу.
        :return: True, если загрузка успешна, иначе False.
        """
        filename = os.path.basename(local_path)
        remote_path = f"{self.remote_folder}/{filename}"
        
        # 1. Получаем ссылку для загрузки
        url = f"{self.BASE_URL}/upload?path={remote_path}&overwrite=false"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return False
            
            upload_url = response.json().get("href")
            if not upload_url:
                return False

            # 2. Загружаем файл по полученной ссылке
            with open(local_path, "rb") as file:
                upload_response = requests.put(upload_url, files={"file": file}, timeout=30)
                return upload_response.status_code in (200, 201, 202)
                
        except (requests.RequestException, OSError):
            return False

    def reload(self, local_path: str) -> bool:
        """Перезаписывает существующий файл в облаке.
        
        :param local_path: Путь к локальному файлу.
        :return: True, если перезапись успешна, иначе False.
        """
        filename = os.path.basename(local_path)
        remote_path = f"{self.remote_folder}/{filename}"
        
        # 1. Получаем ссылку для загрузки (overwrite=true)
        url = f"{self.BASE_URL}/upload?path={remote_path}&overwrite=true"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return False
            
            upload_url = response.json().get("href")
            if not upload_url:
                return False

            # 2. Загружаем файл по полученной ссылке
            with open(local_path, "rb") as file:
                upload_response = requests.put(upload_url, files={"file": file}, timeout=30)
                return upload_response.status_code in (200, 201, 202)
                
        except (requests.RequestException, OSError):
            return False

    def delete(self, filename: str) -> bool:
        """Удаляет файл из облака.
        
        :param filename: Имя файла (без пути).
        :return: True, если удаление успешно, иначе False.
        """
        remote_path = f"{self.remote_folder}/{filename}"
        url = f"{self.BASE_URL}?path={remote_path}&permanently=true"
        
        try:
            response = requests.delete(url, headers=self.headers, timeout=10)
            return response.status_code in (200, 202, 204)
        except requests.RequestException:
            return False
