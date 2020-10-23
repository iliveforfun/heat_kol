import logging
import os


class Logger():
    def __init__(self):
        self.logger = logging.getLogger('heatLogger')
        self.logger.setLevel(level=logging.INFO)

        formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')

        file_handler = logging.FileHandler(os.path.join('cache', 'heat.log'))
        file_handler.setFormatter(formater)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formater)

        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)

    def log(self, level=logging.INFO,message='no info'):
        self.logger.log(msg=message,level=level)


if __name__ == '__main__':
    Logger().log()
