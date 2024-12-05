class TokenNotFound(Exception):
    """Не обнаружен токен доступа к API passwork"""


class AccessDeniedToPasswordDatabase(Exception):
    """Невозможно подключиться к базе данных passwork"""


class VaultsNotFound(Exception):
    """Неудалось обнаружить сейфы организации"""


class APIErrorConnectToRootFolder(Exception):
    """Ошибка подключения к API passwork - корневые папки сейфа"""


class APIErrorGetPasswordVault(Exception):
    """Ошибка подключения к API passwork - получения паролей сейфа"""


class APIErrorGetMetaPassword(Exception):
    """Ошибка подключения к API passwork - получения мета-паролей"""


class APIErrorGetMetaPasswordsFolder(Exception):
    """Ошибка подключения к API passwork - получение мета-паролей из папки"""


class APIErrorGetALLPasswordsFromFolder(Exception):
    """Ошибка подключения к API passwork - рекурсивное получение всех объектов паролей сейфа"""


class ErrorGetSecureData(Exception):
    """Нквозможно получить данные секретов из защищённой области операционной системы"""