## Требования

**Python 3.7+**

**Framework: FastAPI**

## Установка

```bash
pip install -r requirements.txt
```

## Данные

**Файл БД и файл с почтой и паролем не нужно хранить на гите. Здесь они хранятся ради использования их в качестве примера**

* Использумая СУБД: SQLite. В рабочей директории уже создан файл БД `md5.db`. При необходимости можно изменить адрес БД в файле `database.py`:

```Python
DATABASE_URL = "sqlite:///md5.db"
```

* Для отправки письма используется уже созданная тестовая почта. При необходимости изменить почтовые данные в файле `data.yml`. Данные почтового сервера находятся в файле `main.py`:

```Python
SERVER = "smtp.gmail.com"
PORT = 587
```

## Запуск

Запуск сервера:

```bash
python manage.py
```

Или:

```bash
uvicorn main:app
```

## Проверка

POST запрос по адресу http://127.0.0.1:8000/submit . В теле запроса:

```JSON
{
	"url": "http://site.com/example.pdf",
	"email": "my@example.com"
}
```

Ответ на запрос - идентификатор текущей задачи:

```JSON
{
	"status_id": "some_random_id"
}
```

GET запрос на http://127.0.0.1:8000/check/{status_id} .Где status_id - полученный идентификатор.

**Возможные варианты ответа:**

Не найдено

```JSON
{
	"status": "not found"
}
```

В процессе

```JSON
{
	"status": "running"
}
```

Неудача

```JSON
{
	"status": "failed"
}
```

Завершено

```JSON
{
	"md5_checksum": "some_md5sum",
	"status": "failed",
	"url": "http://site.com/example.pdf"
}
```

**Статус код ответа соответсвует ответу:**
Код POST запроса - 201 Created
Не найдено - 404 Not found
В процессе - 202 Accepted
Неудача - 500 Internal Server Error
Завершено - 200 OK

**Если в запросе указан email адрес, то туда отправляется письмо в формате: url, md5sum**
