
# Платформа для блогеров
### Описание
Yatube - это социальная сеть. Она даёт пользователям возможность создать учетную запись, публиковать записи, подписываться на любимых авторов и отмечать понравившиеся записи. 
### Технологии
- [Python 3.7](https://www.python.org/)
- [`Django 2.2.19`](https://github.com/django/django)
- [`django-rest-framework`](https://www.django-rest-framework.org/) для API
- [`poetry`](https://github.com/python-poetry/poetry) для управления зависимостями
- [`pytest`](https://pytest.org/)  для юнит тестов
- [`flake8`](http://flake8.pycqa.org/en/latest/) линтер
- [`drf-yasg`](https://github.com/axnsan12/drf-yasg/) для документации API
- [`docker`](https://github.com/docker) для развёртывания
### Запуск проекта в dev-режиме

- склонируйте репозиторий
```
git clone https://github.com/SaPer663/yatube.git
```
- в директории ```yatube/config``` создате ```.env.dev``` на основе ```.env.template```

- соберите образ контейнера
```
docker-compose build
```
- запустите контейнер
```
docker-compose up
```
- после запуска контейнера сервер будет доступен по адресу:
```
http://0.0.0.0:8000/
```
- документация API доступна по адресу:
```
http://0.0.0.0:8000/swagger/
```

### Авторы
Александр @saper663 
