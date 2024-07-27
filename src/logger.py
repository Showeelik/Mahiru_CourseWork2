import os
import logging
import logging.handlers
import datetime


class CustomFormatter(logging.Formatter):

    LEVEL_COLORS = [
        (logging.DEBUG, '\x1b[32;1m'),
        (logging.INFO, '\x1b[34;1m'),
        (logging.WARNING, '\x1b[33;1m'),
        (logging.ERROR, '\x1b[31;1m'),
        (logging.CRITICAL, '\x1b[41m'),
    ]
    FORMATS = {
        level: logging.Formatter(
            f'\x1b[30;1m%(asctime)s\x1b[0m {color}%(levelname)-10s\x1b[0m \x1b[35m%(name)s\x1b[0m -> %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
        for level, color in LEVEL_COLORS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Переопределите функцию обратной трассировки, чтобы она всегда печаталась красным цветом
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f'\x1b[31m{text}\x1b[0m'

        output = formatter.format(record)

        # Удаление слоя кэша
        record.exc_text = None
        return output


def setup_logger(module_name:str) -> logging.Logger:
    """
    
    """
    # Cоздание логгера
    library, _, _ = module_name.partition('.py')
    logger = logging.getLogger(library)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Создание консольного обработчика с помощью CustomFormatter (цветной)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(CustomFormatter())

        # укажите, чтобы путь к файлу журнала совпадал с путем к файлу `main.py`.
        grandparent_dir = os.path.abspath(__file__ + "/../../")
        # Создайте папку logs, если она не существует
        logs_dir = os.path.join(grandparent_dir, "logs")
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        # Укажите название к журналу в папке logs
        log_name = f'{datetime.datetime.now().strftime("%Y-%m-%d")}.log'
        log_path = os.path.join(logs_dir, log_name)
        # Создайте обработчик файлов с обычным форматером (без ANSI)
        log_handler = logging.handlers.RotatingFileHandler(
            filename=log_path,
            encoding='utf-8',
            maxBytes=32 * 1024 * 1024,  # 32 MiB
            backupCount=2,
        )
        log_handler.setFormatter(logging.Formatter(  # Используйте форматер по умолчанию
            '%(asctime)s %(levelname)-8s %(name)s -> %(message)s',
            '%Y-%m-%d %H:%M:%S'
        ))

        # Добавляем обработчики в логгер
        logger.addHandler(log_handler)
        logger.addHandler(console_handler)

    return logger