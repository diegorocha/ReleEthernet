from random import choice

LOW = 0
HIGH = 1
BCM = 0
IN = 0
OUT = 1


def setmode(mode):
    return mode


def setup(*args, **kwargs):
    return


def input(pin):
    print('Obtendo valor do pino %s' % pin)
    return choice(range(1))


def output(pin, value):
    print('Escrevendo %s no pino %s' % (value, pin))
    return
