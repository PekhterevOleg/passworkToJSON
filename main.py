import urllib3
import config
import os

from mainfunc import get_credential, \
    create_config_file, \
    set_secure_vaults, \
    get_config_file, \
    get_secure_data, \
    create_excel_data_file, \
    encrypt_pass_excel_file


import exceptions
from passwork import Passwork

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
svc = ['Passwork', 'Excel']

if not os.path.exists(config.CONFIG_FILE_PATH):
    _api_key, _xls_key = get_credential()
    config_parser = create_config_file(config.CONFIG_FILE_PATH)
    secure_data = zip(svc, (_api_key, _xls_key))
    # set_secure_vaults - Установка секретов в безопасном хранилище данных операционной системы
    set_secure_vaults(sec_data=secure_data)

else:
    config_parser = get_config_file(config.CONFIG_FILE_PATH)

try:
    api_key, xls_key = get_secure_data(con_parser=config_parser,
                                       username=os.getlogin(),
                                       services=svc)
except exceptions.ErrorGetSecureData as e:
    print(f"Секретные данные (частично) не найдены >> {e}")
    exit(1)

if not api_key or not xls_key:
    print('Один из ключей не найден.\n'
          'Удалите конфигурационный файл чтобы переназначить секреты')
    exit(1)

passwork = Passwork(api_key=api_key)
create_excel_data_file(passwork=passwork)
if os.path.exists(config.EXCEL_FILE):
    encrypt_pass_excel_file(config.EXCEL_FILE, xls_key)

else:
    raise FileExistsError(f'Excel файл [{config.EXCEL_FILE}] не найден в каталоге')
print('Done.....')