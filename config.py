import os

URL_ROOT = 'https://passwork.achimgaz.ru/api/v4'
URL_LOGIN = '/auth/login/'
URL_ROOT_FOLDER = '/vaults/{id}/folders'
URL_CHILD_FOLDER = '/folders/{id}/children'
URL_VAULTS = '/vaults/list'
URL_VAULTS_PASS = '/vaults/{id}/passwords'
URL_PASSWORD = '/passwords/{id}'
URL_FOLDER_PASSWORDS = '/folders/{id}/passwords'

TEST_URL = 'https://passwork.achimgaz.ru/api/v4/passwords/62cbba8fcfcf23119f076146'

CONFIG_FILE_PATH = os.getcwd() + '\\' + 'config.ini'
SAVE_FILE = os.getcwd() + '\\' + 'decrypt_pass_passwork.txt'

EXCEL_FILE = 'encrypted_passwords.xlsx'