## Запуск бэкэнда

### Требования

- Docker
- Docker Compose
- Git (для клонирования репозитория)

### Установка и запуск с использованием Docker Compose

1. Клонируйте репозиторий:

    ```sh
    git clone https://github.com/dedlaf/e-comet.git
    cd e-comet
    ```

2. Укажите переменные окружения в файле `docker-compose.yml`:

    ```yaml
    version: '3.8'

    services:
      backend:
        build: .
        container_name: fastapi_backend
        ports:
          - "8080:8080"
        environment:
          DB_NAME: your_db_name 
          DB_USER: your_db_user
          DB_PASS: your_db_password
          DB_HOST: your_db_host
          DB_PORT: your_db_port
          GH_AUTH_TOKEN: your_github_auth_token
    ```

3. Запустите контейнер с помощью Docker Compose:

    ```sh
    docker-compose up --build
    ```

Приложение будет доступно по адресу `http://localhost:8080`.

### Краткое примечание:
Исходя из т/з не совсем понятно как следует выполнить эндпоинт
``GET /api/repos/{owner}/{repo}/activity``, т.к по условию таблицы top100 и activity
не имеют связи по репозиториям. Поэтому этот эндпоинт парсит данные по запросу, а затем
отдает пользователю, не используя бд. Остальные комментарии к ключевым моментам оставил в коде.


## Запуск парсера

1. Запакуйте папку ```parser``` в ```zip-архив```
2. Создайте клауд функцию в яндекс.облаке
3. Загрузите ```zip-архив``` в редакторе
4. Как точку входа укажите ```parser.main.handler```
5. В качестве переменных окружения укажите параметры для подключения к бд
   ```    
   DB_NAME: your_db_name 
   DB_USER: your_db_user
   DB_PASS: your_db_password
   DB_HOST: your_db_host
   DB_PORT: your_db_port
   ```
6. Скопируйте ```requirements.txt``` в корень проекта в редакторе(К сожалению, я не нашёл 
   как можно явно указать, где лежит ```requirements.txt```)
7. В качестве триггера можно использовать таймер на 3 часа(Учитывая устойчивые позиции
   топа репозиториев,не думаю, что есть смысл обновлять информацию более активно).
   Cron-выражение: ```0 */3 * * *```

Парсер будет парсить данные с гитхаба с помощью api, а затем заносить их базу.

Остальные комментарии к ключевым моментам оставил в коде.