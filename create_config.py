import configparser


def create_config(config_path='/var/yang/conf/yangcatalog.conf'):
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read(config_path)
    return config
