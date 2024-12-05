import config
import requests
import exceptions
import passworktools
import classes
import base64

from typing import Any
from typing import Generator
from requests.models import Response
from requests.sessions import Session
from exceptions import AccessDeniedToPasswordDatabase
from collections import abc


class Passwork(classes.BasePasswork, abc.Sequence):

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._url_logon = config.URL_ROOT + config.URL_LOGIN
        self._conn_string = self._url_logon + self._api_key
        self._passwords: list[dict] = []

        response, session = self._connect_passwork()
        try:
            if not response:
                raise AccessDeniedToPasswordDatabase('Доступ к БД passwork запрещён проверьте API ключ')
        except AccessDeniedToPasswordDatabase as e:
            print(f'Error access DB >>> {e}')
            exit(1)

        token = passworktools.get_token(response.json())
        header_access = {
            "Accept": "application/json",
            "Passwork-Auth": token
        }

        connect_config: dict[str, Any] = {
            'session': session,
            'headers': header_access
        }

        try:
            vaults: list = passworktools.get_vaults(**connect_config)

        except exceptions.VaultsNotFound as e:
            print(f'Ошибка получения сейфов >>> {e}')
            exit(1)

        for vault in vaults:
            try:
                folders = passworktools.get_root_folder(**connect_config, value_id=vault)

                self._passwords += passworktools.get_passwords_vault(**connect_config, vault_id=vault)

                if folders is not None:
                    self._passwords += passworktools.get_all_password_from_folders(**connect_config,
                                                                                   root_folders=folders)
            except exceptions.APIErrorConnectToRootFolder as e:
                print(f'Ошибка подключения к API passwork - корневые папки сейфа >>> {e}')
                exit(1)
            except exceptions.APIErrorGetPasswordVault as e:
                print(f'Ошибка подключения к API passwork - получения паролей сейфа >>> {e}')
                exit(1)
            except exceptions.APIErrorGetALLPasswordsFromFolder as e:
                print(f'Ошибка подключения к API passwork - рекурсивное получение всех объектов паролей сейфа >>> {e}')
                exit(1)

        session.close()

    def _connect_passwork(self) -> tuple[Response, Session]:
        """подключение к API passwork"""

        conn_string = self._conn_string
        session = requests.Session()
        try:
            return session.post(url=conn_string, verify=False), session
        except requests.exceptions.SSLError as e:
            print(f'Ошибка подключения по SSL >>> {e}')
            exit(1)
        except requests.exceptions.Timeout as e:
            print(f'Вышло время подключения к {conn_string} >>> {e}')
            exit(1)
        except requests.exceptions.ConnectionError as e:
            print(f"Ошибка подключения к API passwork >>> {e}")
            exit(1)

    def decrypt_passwords(self) -> Generator:
        """Декодирование паролей"""

        for obj_password in self._passwords:
            str_crpt_pass = obj_password['data']['cryptedPassword']
            str_crpt_pass = base64.b64decode(str_crpt_pass)
            obj_password['data']['cryptedPassword'] = str_crpt_pass.decode()
            yield obj_password
