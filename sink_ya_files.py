import os
import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Конфигурация
YANDEX_DISK_TOKEN = "YOUR_YANDEX_DISK_OAUTH_TOKEN"
LOCAL_DIRECTORY = "/path/to/local/directory"
YANDEX_DISK_DIRECTORY = "/path/to/yandex/disk/directory"

# Функции для работы с Яндекс Диском
def upload_file(local_path, disk_path):
    url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = {"Authorization": f"OAuth {YANDEX_DISK_TOKEN}"}
    params = {"path": disk_path, "overwrite": "true"}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        upload_url = response.json()["href"]
        with open(local_path, "rb") as f:
            requests.put(upload_url, files={"file": f})
        print(f"Uploaded {local_path} to {disk_path}")
    else:
        print(f"Failed to get upload URL for {disk_path}: {response.text}")

def delete_file(disk_path):
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = {"Authorization": f"OAuth {YANDEX_DISK_TOKEN}"}
    params = {"path": disk_path}
    
    response = requests.delete(url, headers=headers, params=params)
    if response.status_code == 204:
        print(f"Deleted {disk_path}")
    else:
        print(f"Failed to delete {disk_path}: {response.text}")

# Класс-обработчик событий файловой системы
class Watcher(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            local_path = event.src_path
            relative_path = os.path.relpath(local_path, LOCAL_DIRECTORY)
            disk_path = os.path.join(YANDEX_DISK_DIRECTORY, relative_path)
            upload_file(local_path, disk_path)

    def on_modified(self, event):
        if not event.is_directory:
            local_path = event.src_path
            relative_path = os.path.relpath(local_path, LOCAL_DIRECTORY)
            disk_path = os.path.join(YANDEX_DISK_DIRECTORY, relative_path)
            upload_file(local_path, disk_path)

    def on_deleted(self, event):
        if not event.is_directory:
            local_path = event.src_path
            relative_path = os.path.relpath(local_path, LOCAL_DIRECTORY)
            disk_path = os.path.join(YANDEX_DISK_DIRECTORY, relative_path)
            delete_file(disk_path)

# Основная функция
def main():
    event_handler = Watcher()
    observer = Observer()
    observer.schedule(event_handler, LOCAL_DIRECTORY, recursive=True)
    observer.start()
    print(f"Monitoring {LOCAL_DIRECTORY} for changes...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    main()
