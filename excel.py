import os.path
import pathlib
import subprocess
import openpyxl


from openpyxl import Workbook
from typing import NoReturn, Generator
from config import EXCEL_FILE


def insert_data_excel_file(passwords_json: Generator, titles: tuple) -> NoReturn:
    """Вставка данных паролей в excel файл"""

    excel_file = Workbook()
    try:
        excel_sheet = excel_file.create_sheet(title='Passwords', index=0)
    except openpyxl.utils.exceptions.SheetTitleException as e:
        print(f'Невозможно установить заголовки в Excel файле >>> {e}')
        exit(1)

    for title in titles:
        excel_sheet[title[1]] = title[0]

    count = 2
    for pass_obj in passwords_json:
        pass_data = pass_obj['data']
        name = pass_data['name']
        login = pass_data['login']
        password = pass_data['cryptedPassword']
        excel_sheet['A' + str(count)] = name
        excel_sheet['B' + str(count)] = login
        excel_sheet['C' + str(count)] = password
        count += 1

    if os.path.exists(EXCEL_FILE):
        os.remove(EXCEL_FILE)
        excel_file.save(EXCEL_FILE)
    else:
        excel_file.save(EXCEL_FILE)


def set_password_excel_file(excel_file_path: str, set_password: str) -> NoReturn:
    from pathlib import Path

    excel_file_path = Path(excel_file_path)
    str_excel_path = str(excel_file_path.absolute())

    vbs_script = \
        f""" 'Save with password required upon opening'

        Set excel_object = CreateObject("Excel.Application")
        Set workbook = excel_object.Workbooks.Open("{str_excel_path}")
    
        excel_object.DisplayAlerts = False
        excel_object.Visible = False
    
        workbook.SaveAs "{str_excel_path}",, "{set_password}"
    
        excel_object.Application.Quit
        """

    # Запись кода в VBS файл
    vbs_script_path = excel_file_path.parent.joinpath("set_pw.vbs")
    with open(vbs_script_path, "w") as file:
        file.write(vbs_script)

    # Исполняем VBS код в отдельном процессе
    subprocess.call(['cscript.exe', str(vbs_script_path)])

    # удаляем скрипт VBS
    vbs_script_path.unlink()