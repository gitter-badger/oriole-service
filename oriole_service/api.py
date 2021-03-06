"""
                __   _,--="=--,_   __
               /  \."    .-.    "./  \
              /  ,/  _   : :   _  \/` \
              \  `| /o\  :_:  /o\ |\__/
               `-'| :="~` _ `~"=: |
                  \`     (_)     `/
           .-"-.   \      |      /   .-"-.
    .-----{     }--|  /,.-'-.,\  |--{     }-----.
     )    (_)_)_)  \_/`~-===-~`\_/  (_(_(_)    (
    (                                          )
     )                Oriole-API               (
    (                  Eric.Zhou               )
    '-------------------------------------------'
"""

import yaml
import code
from redis import StrictRedis
from subprocess import run as sr
from os import path, walk, pardir, getcwd
from nameko.standalone.rpc import ClusterRpcProxy
import logging
from logging import DEBUG, INFO, WARNING, ERROR
from logging import StreamHandler, Formatter, getLogger, FileHandler

exe = lambda s: sr(s, shell=True)
mexe = lambda f, s: tuple(map(f, s))
cwd = lambda: getcwd()
test_cmd = "py.test -v --html=report.html"


def get_config(f="services.cfg"):
    return get_yml(get_file(f))


def get_yml(f):
    with open(f) as filename:
        return yaml.load(filename)


def get_file(f):
    loc = cwd()
    for _ in range(3):
        config = path.join(loc, f)
        if path.isfile(config):
            return config
        loc = path.join(loc, pardir)


def get_path(f, loc):
    for fpath, _, fs in walk(loc):
        if f in fs:
            return fpath


def run(service):
    fmt = "cd %s && nameko run %s --config %s"
    config = path.join(cwd(), "services.cfg")
    fpath = get_path("%s.py" % service, "services")
    if fpath:
        exe(fmt % (fpath, service, config))


def remote_test(f):
    usage = 'Usage: s.log_service.ping()'
    config = get_yml(f)
    with ClusterRpcProxy(config) as s:
        code.interact(usage, None, {"s": s})


def mtest(test):
    fmt = "cd %s && %s"
    fpath = get_path("test_%s.py" % test, "tests")
    if fpath:
        exe(fmt % (fpath, test_cmd))


def test(tests):
    if not tests:
        exe(test_cmd)
    else:
        mexe(mtest, tests)


def Config(name="services.cfg"):
    """ Obsoleted """
    return get_config(name)


def logger(level='DEBUG', name=""):
    fmt = '[%(module)s] %(asctime)s %(levelname)-7.7s %(message)s'
    dfmt = '%Y-%m-%d %H:%M:%S'
    level = getattr(logging, level, DEBUG)

    logger = getLogger('services')
    logger.setLevel(level)
    fmter = Formatter(fmt, dfmt)
    del logger.handlers[:]

    if name:
        fh = FileHandler(name)
        fh.setLevel(level)
        fh.setFormatter(fmter)
        logger.addHandler(fh)

    ch = StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(fmter)
    logger.addHandler(ch)
    logger.propagate = False

    return logger


def get_logger():
    cf = get_config()
    level = cf.get("log_level", "DEBUG")
    name = cf.get("log_name", "")
    return logger(level, name)


def get_rs():
    return StrictRedis.from_url(get_config().get("datasets"))
