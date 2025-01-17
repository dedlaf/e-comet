import json
import logging

import psycopg2
from db.postgres import PostgresHandler
from fetcher.fetcher import Fetcher
from loader.loader import Loader

logging.basicConfig(level=logging.INFO)

"""
Точка входа парсера. Добавил обработку возможных ошибок, а также 
небольшое логгирование, для отслеживания работы скрипта.
"""


def handler(event, context):
    db_handler = PostgresHandler()
    loader = Loader(db_handler)
    fetcher = Fetcher()

    try:
        logging.info("Fetching repositories...")
        data = fetcher.fetch_repositories()

        logging.info("Transforming data...")
        transformed_data = loader.transform_data(data)

        logging.info("Processing data...")
        loader.process_data(transformed_data)

        logging.info("Data processing completed successfully.")

    except psycopg2.DatabaseError as db_error:
        logging.error(f"Database error occurred: {db_error}")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"error": "Database error occurred", "message": str(db_error)}
            ),
        }

    except json.JSONDecodeError as json_error:
        logging.error(f"JSON decoding error occurred: {json_error}")
        return {
            "statusCode": 400,
            "body": json.dumps(
                {"error": "JSON decoding error occurred", "message": str(json_error)}
            ),
        }

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"error": "An unexpected error occurred", "message": str(e)}
            ),
        }

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Data processing completed successfully",
                "event": event,
                "context": context,
            },
            default=vars,
        ),
    }
