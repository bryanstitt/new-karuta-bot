import logging

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    handler = logging.FileHandler('log.log', encoding='utf-8', mode='w')
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(filename)s:%(lineno)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
