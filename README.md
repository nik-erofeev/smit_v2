

# Установка и запуск
Создайте в корне приложения файл **.env** и определите в нём все переменные, указанные в [.env_example](./.env_example).

.env.compose.pg и .env.compose.rmq это конфиги БД и RMQ
## Запуск через docker-compose

#### Собрать и запустить/остановить приложение с помощью
```sh
$ make up
$ make up_re

$ make down
```



#### Перейти на swagger [http://localhost:8000/docs](http://localhost:8000)
```sh
http://localhost:8000/docs
```


## Локально

#### Установить и активировать виртуальное окружение с помощью команд:
```sh
$ python3.12 -m venv venv
$ source venv/bin/activate
```

#### Установить зависимости:
```sh
$ pip install poetry
$ poetry install
```

#### Запустить/остановить контейнеры кроме API:
```sh
$ make up_local
$ make down
```

<br>

#### Загрузить ЕНВы из файла .env(при локальном  смотреть коммент в [.env_example](./.env_example))

<br>

#### Прогнать миграции с помощью с помощью [alembic](https://alembic.sqlalchemy.org/en/latest/):
```sh
$ alembic upgrade head
```


#### Запустить приложение с помощью:
```sh
python -m app.main
```

<br>

#### Перейти на swagger [http://localhost:8000/](http://localhost:8000)
```sh
http://localhost:8000/
```

<br>

#### Перейти на веб интерфейс kafka (topik) [http://localhost:8090](http://localhost:8090)
в кафку отправляются по 5 батчам(default), если не указать в env
```sh
http://localhost:8090
```

<br>

#### Перейти на веб интерфейс RMQ [http://localhost:15672/](http://localhost:15672/)
лог/пароль в env
```sh
http://localhost:15672
```

<br>

#### Перейти на веб интерфейс Prometheus [http://localhost:19090/query](http://localhost:19090/query)
лог/пароль в env
```sh
http://localhost:19090/query
```

<br>

#### json файл для загрузки в API  [exa.json](./exa.json).

<br>


#### дока по настройке grafana/prometheus.yml

https://habr.com/ru/companies/slurm/articles/741670/

