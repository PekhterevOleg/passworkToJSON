import config
import exceptions
import configparser
import os
import keyring
import json

from typing import NoReturn
from typing import Generator
from getpass import getpass
from classes import ProtPasswork


SECRET_DATA = tuple[str, str]


def get_credential() -> SECRET_DATA:
    """Если конфигурационный файл в каталоге не найден то возвращаем данные секретов"""

    msg = (
        'Длина пароля должна быть не менее 8 символов включая большие,'
        ' маленькие буквы, цифры и спецсимвол(ы) - {spsymb}'
    )
    spsymb = '* | & | ^ | @ | %'
    print(msg.format(spsymb=spsymb), '\n')

    try:
        while True:
            api_key = getpass('Enter API key for Passwork: ')
            if not api_key:
                print('Пустые значения недопустимы !')
                continue
            while True:
                xls_pass = getpass('Enter secret for excel file: ')
                check_pass = _check_valid_password(xls_pass, 8)
                if not check_pass:
                    print('Пароль не соответствует требованиям парольной политики, повторите попытку!')
                    continue
                else:
                    break
            break
    except KeyboardInterrupt:
        print('\n', 'Выход...')
        exit(0)
    return api_key, xls_pass


def _check_valid_password(passwd: str, length: int) -> bool:
    """Проверка пароля на соответствие требованиям парольной политики"""

    import re
    if len(passwd) < length:
        return False

    patterns = [r'\d+', r'[a-z]+', r'[A-Z]+', r'[\*\&\^\@\%]+']
    check_valid = []
    for pattern in patterns:
        regex = re.compile(pattern)
        result = regex.findall(passwd)
        check_valid.append(bool(result))

    return all(check_valid)


def get_config_file(conf_file: str) -> configparser.ConfigParser:
    """Получаем объект кофигурационного файла"""

    parser = configparser.ConfigParser()
    parser.read(conf_file)
    return parser


def create_config_file(conf_file: str) -> configparser.ConfigParser:
    """Создаём конфигурационный файл с параметрами переданных служб"""

    obj_config_file = configparser.ConfigParser()
    obj_config_file['Passwork'] = {
        'service_name': 'Passwork',
        'username': os.getlogin()
    }
    obj_config_file['Excel'] = {
        'service_name': 'Excel',
        'username': os.getlogin()
    }
    try:
        with open(conf_file, encoding='utf-8', mode='w') as file:
            obj_config_file.write(file)
    except IOError as e:
        print(f'Невозможно записать данные в конфигурационный файл >>> {e}')
        exit(1)
    return obj_config_file


def set_secure_vaults(sec_data: zip) -> NoReturn:
    """Установка секретов служб в безопасном хранилище ОС"""

    obj_config_file = configparser.ConfigParser()
    obj_config_file.read(config.CONFIG_FILE_PATH)
    for svc, secret in sec_data:
        _set_secure_service(secret=secret, data=obj_config_file[svc])


def _set_secure_service(secret: str, data: dict) -> NoReturn:
    """Внутренняя реализация механизма установки секретов в безопасном хранилище ОС"""

    svcname = data['service_name']
    usrname = data['username']
    print(f'Выполнятеся попытка установить секрет для: {svcname}')
    try:
        keyring.set_password(service_name=svcname, 
                             username=usrname, 
                             password=secret)
    except Exception as e:
        print(f'Невозможно сохранить секрет в защищенном хранилище >>>> {e}')
        exit(1)
    print('Успешно')


def get_secure_data(con_parser: configparser.ConfigParser,
                    username: str,
                    services: list) -> SECRET_DATA:
    """Возвращаем кортеж секретов служб (API KEY, EXCEL PASS)"""

    secure_data = (keyring.get_password(svc, username) for svc in services)
    check_generator_and_return_data = _check_generator_is_empty(secure_data)
    if not check_generator_and_return_data:
        raise exceptions.ErrorGetSecureData('Функция вернула пустые значения для секретов, '
                                            'продолжение работы невозможно')
    return check_generator_and_return_data


def _check_generator_is_empty(secure_data) -> SECRET_DATA | None:
    """Проверяем является ли генератор пустым"""

    try:
        first = next(secure_data)
        two = next(secure_data)
    except StopIteration:
        return None
    return first, two

    
def dump_secrets_passwork_to_disk(save_path: str, passwords: Generator) -> NoReturn:
    """Сохраняем декодирвоанные объекты passwork (пароли) на диск"""

    with open(file=save_path, encoding='utf-8', mode='w') as file:
        for passwd in passwords:
            json.dump(passwd, file, ensure_ascii=False, indent=4)


def create_excel_data_file(passwork: ProtPasswork) -> NoReturn:
    """Создание excel файла с данными паролей"""

    from excel import insert_data_excel_file

    titles = (('Name', 'A1'),
              ('Login', 'B1'),
              ('Password', 'C1'))
    insert_data_excel_file(passwords_json=passwork.decrypt_passwords(),
                           titles=titles)


def encrypt_pass_excel_file(excel_file: str, password: str) -> NoReturn:
    """Установка пароля на Excel файл"""

    from excel import set_password_excel_file

    set_password_excel_file(excel_file, password)






















    # import zipfile
    #
    # try:
    #     with zipfile.ZipFile('passwork.zip', mode='a') as archive:
    #         #archive.setpassword(xls_password.encode())
    #         with archive.open('decrypt_pass.txt', mode='w', pwd=xls_password.encode()) as pass_file:
    #             for password in passwork.decrypt_passwords():
    #                 pass_file.write((str(password)).encode())
    # except zipfile.BadZipfile as e:
    #     print(f'Ошибка zip архива >>> {e}')
    #     exit(1)
    # except TypeError as e:
    #     print(f'Error >>> {e}')
    #     exit(1)
    # return True


