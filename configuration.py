import configparser

data = configparser.ConfigParser()
data.read('config.ini')
# this path is hardcoded, so to support alternative configurations, it may
# be handy to use a symbolic link pointing to the applicable config file.
