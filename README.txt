Открыть exe.файл
Перейти по ссылке

---Через командную строку---

1. Установите зависимости:

bash
pip install -r requirements.txt

1.1 при ошибке:

PowerShell
cd "C:\Users\HP\Desktop\visual-novel-pwa"

1.2 Создайте requirements.txt с основными зависимостями

1.3 Проверьте, что файл создан

PowerShell
cat requirements.txt

1.4 Установка зависимости:

# Способ 1: Обычная установка
PowerShell
python -m pip install -r requirements.txt

# Способ 2: С отключением SSL (если были проблемы)
PowerShell
python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

2. Запустите приложение:

bash
python app.py

3. Перейдите по адресу:

text
http://localhost:5000

вводить команды в PowerShell, если не запускается через VSCode