import subprocess

# Список путей к скриптам Python, которые нужно запустить
scripts = [
    'find_urls.py',
    'find_data.py'
]

# Запуск каждого скрипта по очереди
for script in scripts:
    subprocess.run(['python', script])
