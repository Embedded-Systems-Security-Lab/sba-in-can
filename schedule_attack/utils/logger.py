import logging


class CustomLogger(logging.getLoggerClass()):

    def __init__(self,
                name,
                file_name,
                format="%(asctime)s | %(levelname)s | %(message)s",
                level=logging.DEBUG,
                stream_level=logging.ERROR ):

        self.name = name
        self.file_name = file_name
        self.format = format
        self.level = level

        self.formatter = logging.Formatter(self.format)

        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(stream_level) # We can change this
        self.stream_handler.setFormatter(self.formatter)


        self.file_handler = logging.FileHandler(self.file_name)
        self.file_handler.setFormatter(self.formatter)

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.level)
        self.logger.addHandler(self.stream_handler)
        self.logger.addHandler(self.file_handler)

    def info(self, msg, extra=None):
        self.logger.info(msg, extra=extra)

    def error(self, msg, extra=None):
        self.logger.error(msg, extra=extra)

    def debug(self, msg, extra=None):
        self.logger.debug(msg, extra=extra)

    def warn(self, msg, extra=None):
        self.logger.warning(msg, extra=extra)

    def critical(self, msg, extra=None):
        self.logger.critical(msg, extra=extra)

