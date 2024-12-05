chcp 65001
python.exe -m venv venv
echo "Проверьте наличие соединения с интернетом (отключить инспектирование HTTPS трафика)"
pause
CALL .\venv\Scripts\activate.bat
pip install -r requirement.txt
CALL .\venv\Scripts\deactivate.bat
