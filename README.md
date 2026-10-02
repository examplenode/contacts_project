# Contacts XML/JSON
Django-приложение для импорта/экспорта контактов в JSON и XML.
## Установка
```bash
git clone <URL>
cd contacts_project
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
## Запуск

```bash
python manage.py migrate
python manage.py runserver
```
Открой http://127.0.0.1:8000/
## Функционал
- Добавление контакта через форму - сохранение в `contacts/data/` в JSON или XML
- Валидация полей на сервере (имя, телефон, email, категория)
- Загрузка файла `.json`/`.xml`, проверка размера, расширения, структуры
- Невалидный файл удаляется, выводится сообщение
- Имя файла генерируется через `uuid4` - имя от пользователя не используется
- Просмотр содержимого всех файлов из папки `data/`
- Если файлов нет — выводится сообщение