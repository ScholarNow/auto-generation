import configparser

config = configparser.ConfigParser()
config.read('config.ini')

BACKEND_URL = config['SYS']['BACKEND_URL']
ML_URL = config['SYS']['ML_URL']

HOST = config['DATABASE']['HOST']
PORT = int(config['DATABASE']['PORT'])
USER = config['DATABASE']['USER']
PASSWORD = config['DATABASE']['PASSWORD']
DATABASE = config['DATABASE']['DATABASE']
NEWS_TABLE = config['DATABASE']['NEWS_TABLE']
NEWS_LOGS_TABLE = config['DATABASE']['NEWS_LOGS_TABLE']

PATH = config['DEFAULT']['PATH']
CRON = config['DEFAULT']['CRON']