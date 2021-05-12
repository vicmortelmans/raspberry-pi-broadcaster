import configparser

data = configparser.ConfigParser()
data.read('config.ini')
# this path is hardcoded, so to support alternative configurations, it may
# be handy to use a symbolic link pointing to the applicable config file.

# configuration items can be read like this:
#  configuration.data[<section title>][<item name>]


class PasswordError(Exception):
    pass


def check_password(password):
    if data['DEFAULT']['password'] != password:
        raise PasswordError
