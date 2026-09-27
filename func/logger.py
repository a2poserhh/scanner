import logging
import sys

def setup_logging(log_file='data.log', level=logging.DEBUG):
    logger = logging.getLogger()
    logger.setLevel(level)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(message)s')
    #s is setting as a string rather than not
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    #Calling the handler's setFormatter method to assign the formatter we created

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)