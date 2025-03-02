import os
import shutil
import threading
import logging
import hashlib
from datetime import datetime

sync_interval: int = 0
source_path: str = ''
destination_path: str = ''

logging.basicConfig(
  level=logging.DEBUG,
  format='%(asctime)s.%(msecs)03d - %(message)s',
  datefmt='%Y-%m-%d %H:%M:%S',
  handlers=[
    logging.StreamHandler(),
    logging.FileHandler('sync_log.txt', mode='a')
  ]
)

def get_md5_for_file(file_path: str) -> str:
  md5_hash = hashlib.md5()
  with open(file_path, 'rb') as validated_file:
    for chunk in iter(lambda: validated_file.read(4096), b''):
      md5_hash.update(chunk)
  return md5_hash.hexdigest()
    
def is_md5_valid() -> bool:
  logging.info(f'  ⚙️ Running MD5 validation...')
  is_md5_validation_successful = True

  for dirpath, dirnames, filenames in os.walk(source_path):
    for filename in filenames:
      source_file_path = os.path.join(dirpath, filename)
      destination_file_path = os.path.join(destination_path, os.path.relpath(source_file_path, source_path))
        
      if not os.path.exists(destination_file_path):
        logging.error(f'    ❌ File not found: {destination_file_path}')
        is_md5_validation_successful = False
        continue

      logging.info(f'    ⚙️ Veryfying MD5 for file: {destination_file_path}')

      source_md5: str = get_md5_for_file(source_file_path)
      destination_md5: str = get_md5_for_file(destination_file_path)

      if (source_md5 != destination_md5):
        logging.error(f'      ❌ MD5 validation failed: {source_file_path} - {source_md5}, {destination_file_path} - {destination_md5}')
        is_md5_validation_successful = False
      else:
        logging.info(f'      ✅ MD5 validation for file "{destination_file_path}" was successful')
  return is_md5_validation_successful

def get_current_time() -> str:
  return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_folder_name(output_message: str) -> str:
  folder_name = input(output_message)
  if not isinstance(folder_name, str) or len(folder_name.strip()) == 0:
    print('❌ Please provide a valid folder name')
    return get_folder_name(output_message)
  if not os.path.isdir(folder_name):
    print(f'❌ Folder "{folder_name}" does not exist')
    return get_folder_name(output_message)
  return folder_name

def read_interval() -> None:
  global sync_interval
  sync_interval = int(input('Provide time interval for synchronisation in seconds: '))
  if sync_interval <= 0:
    print(f'❌ The value must be greater than 0')
    read_interval()

def sync() -> None:
  logging.info(f'🔄 Synchronising initiated')
  clean()
  logging.info(f'    ⚙️ Copying files from "{source_path}" to "{destination_path}"...')
  shutil.copytree(source_path, destination_path)
  if is_md5_valid():
    logging.info('✅ Synchronisation successful')
  else:
    logging.info('❌ Synchronisation failed')
  threading.Timer(sync_interval, sync).start()

def clean() -> None:
  if not os.path.exists(destination_path):
    return
  logging.info(f'  ⚙️ Removing old files from "{destination_path}" folder...')
  shutil.rmtree(destination_path)
  logging.info(f'    ✅ Old files removed from "{destination_path}" folder ')

def init() -> None:
  global source_path
  source_path = get_folder_name('Provide source folder name: ')
  global destination_path
  destination_path = get_folder_name('Provide destination folder name: ')
  read_interval()
  sync()

init()