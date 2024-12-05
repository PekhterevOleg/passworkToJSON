import requests.exceptions
import exceptions
import config

from classes import Folder
from requests.sessions import Session
from requests.exceptions import ConnectionError

TOKEN_API = str
VAULTS_ID = list
FOLDERS_ID = list[str]
FOLDER_LIST = list[Folder]
PASSWORDS_LIST = list[dict]
META_PASSWORDS_LIST = list[dict]


def get_token(json_data: dict) -> TOKEN_API:
    """Возвращаем токен безопасности для доступа к БД passwork"""

    match json_data:
        case {'data': {'token': str(token)}}:
            return token
        case _:
            raise exceptions.TokenNotFound('Ошибка получения токена доступа к API passwork')


def get_vaults(session: Session, headers: dict) -> VAULTS_ID:
    """Возвращаем все json-объекты найденных сейфов организации"""

    conn_str = config.URL_ROOT + config.URL_VAULTS
    try:
        response = session.get(url=conn_str, headers=headers, verify=False)
    except requests.exceptions.ConnectionError as e:
        raise exceptions.VaultsNotFound(e)

    match response.json():
        case {'data': vaults} if isinstance(vaults, list):
            result = [vault['id'] for vault in vaults]
        case _:
            raise exceptions.VaultsNotFound('Сейфы не найдены')
    return result


def get_root_folder(session: Session, headers: dict, value_id: str) -> FOLDER_LIST | None:
    """Возвращаем корневой список папок сейфа"""

    url = config.URL_ROOT + config.URL_ROOT_FOLDER
    conn_str = url.format(id=value_id)
    try:
        response = session.get(url=conn_str, headers=headers, verify=False)
    except requests.exceptions.ConnectionError as e:
        raise exceptions.APIErrorConnectToRootFolder(e)

    if not response:
        print(response.json())
        raise ConnectionError('Возникли проблемы с подключением к API')

    folders = response.json()
    if folders['data']:
        result = [Folder(folder['name'],
                         folder['parentId'],
                         folder['vaultId'],
                         folder['id'])
                  for folder in folders['data']]
    else:
        result = None
    return result


def get_passwords_vault(session: Session, headers: dict, vault_id: str) -> PASSWORDS_LIST | list:
    """"Возвращаем пароли из корня сейфа"""

    url = config.URL_ROOT + config.URL_VAULTS_PASS
    conn_str = url.format(id=vault_id)
    try:
        response = session.get(url=conn_str, headers=headers, verify=False)
    except requests.exceptions.ConnectionError as e:
        raise exceptions.APIErrorGetPasswordVault(e)

    if not response:
        msg = response.json()
        raise ConnectionError(f"Возникли проблемы с подключением к API >>> {msg['code']} - {msg['errorMessage']}")

    meta_passwords = response.json()['data']
    if meta_passwords:
        try:
            return _get_passwords_from_meta_passwords(meta_passwords=meta_passwords, session=session, headers=headers)
        except exceptions.APIErrorGetMetaPassword as e:
            print('Ошибка подключения к API passwork - получениe мета-паролей')
            exit(e)
    else:
        return list()


def _get_passwords_from_meta_passwords(session: Session,
                                       headers: dict, meta_passwords: list[dict]) -> PASSWORDS_LIST:
    """Возвращаем объекты паролей из МЕТА-паролей"""

    conn_str = config.URL_ROOT + config.URL_PASSWORD
    passwords = []
    for meta_pass in meta_passwords:
        conn_str_new = conn_str.format(id=meta_pass['id'])
        try:
            obj_pass = session.get(url=conn_str_new, headers=headers, verify=False)
        except requests.exceptions.ConnectionError as e:
            raise exceptions.APIErrorGetMetaPassword(e)

        passwords.append(obj_pass.json())

    return passwords


def _get_meta_passwords_folder(folder: Folder,
                               session: Session, headers: dict) -> META_PASSWORDS_LIST | None:
    """Возвращаем все МЕТА-пароли из текущей папки"""

    url = config.URL_ROOT + config.URL_FOLDER_PASSWORDS
    conn_str = url.format(id=folder.id)
    try:
        obj_meta_passwords = session.get(url=conn_str, headers=headers, verify=False)
    except requests.exceptions.ConnectionError as e:
        raise exceptions.APIErrorGetMetaPasswordsFolder(e)

    _meta_passwords = obj_meta_passwords.json()['data']
    if _meta_passwords:
        return _meta_passwords
    return None


def get_all_password_from_folders(session: Session,
                                  headers: dict,
                                  root_folders: list[Folder], passwords=[]) -> PASSWORDS_LIST:
    """Возвращаем все найденные пароли рекурсивно по папкам"""

    for folder in root_folders:
        url = config.URL_ROOT + config.URL_CHILD_FOLDER
        conn_str = url.format(id=folder.id)
        try:
            obj_child_folders = session.get(url=conn_str, headers=headers, verify=False)
        except requests.exceptions.ConnectionError as e:
            raise exceptions.APIErrorGetALLPasswordsFromFolder(e)

        child_folders = obj_child_folders.json()['data']
        if child_folders:
            folders = [Folder(folder['name'],
                              folder['parentId'],
                              folder['vaultId'],
                              folder['id']) for folder in child_folders]

            get_all_password_from_folders(session=session,
                                          headers=headers,
                                          root_folders=folders)

        try:
            meta_passwords = _get_meta_passwords_folder(session=session,
                                                        headers=headers,
                                                        folder=folder)
        except exceptions.APIErrorGetMetaPasswordsFolder as e:
            print(f'Ошибка подключения к API passwork - получение мета-паролей из папки >>> {e}')
            exit(1)


        if meta_passwords:
            try:
                passwords += _get_passwords_from_meta_passwords(session=session,
                                                                headers=headers,
                                                                meta_passwords=meta_passwords)
            except exceptions.APIErrorGetMetaPassword as e:
                print(f'Невозможно получение паролей из метапаролей >>> {e}')
                exit(1)
    return passwords
