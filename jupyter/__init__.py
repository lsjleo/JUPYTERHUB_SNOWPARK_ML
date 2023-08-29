import configparser

path = f"~/passwords.config"

config = configparser.ConfigParser()
config.read(path)