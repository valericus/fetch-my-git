#!/usr/bin/env python3

import argparse
import configparser
import logging
import sys
import os

from .includes.make_config import make_config
from .includes.supervised_repo import SupervisedRepo


logger = logging.getLogger('fetch-my-git')


default_config_path = os.path.join('/', 'etc', 'fetch-my-git.ini')


def get_repos(config: configparser.ConfigParser):
    for section in config.sections():
        try:
            yield SupervisedRepo(
                path=config.get(section, 'local'),
                remote_name=config.get(section, 'remote_name'),
                remote_url=config.get(section, 'remote_url'),
                branch=config.get(section, 'branch'),
                auto_merge=config.getboolean(section, 'auto_merge'),
                hard_reset=config.getboolean(section, 'hard_reset')
            )
        except configparser.NoOptionError as e:
            logger.error(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--make-config',
        nargs='+',
        help='make config from passed directories. Script will scan '
             'sub-directories of these paths and look for git repositories. '
             'Each repository will be listed in config printed to stdout.',
        default=None,
        metavar='PATH'
    )
    parser.add_argument(
        '--config',
        default=default_config_path,
        help='path to config file, default path is {}'.format(
            default_config_path),
    )
    parser.add_argument(
        '--log',
        default=sys.stderr,
        help='path to log file, default log destinaton is stderr',
        type=argparse.FileType('w')
    )
    parser.add_argument(
        '--log-level',
        default='WARNING',
        help='verbosity level of logs, default one id warning',
        choices=['ERROR', 'WARNING', 'INFO', 'DEBUG'],
    )
    args = parser.parse_args()

    logger.setLevel(getattr(logging, args.log_level))

    if args.make_config:
        try:
            make_config(args.make_config).write(sys.stdout)
        except NotADirectoryError:
            logger.error('{} is not a directory'.format(args.make_config))
        exit(0)

    config = configparser.ConfigParser()
    try:
        config.read_file(open(args.config))
    except IOError as e:
        logger.error('Can\'t read config file: {}'.format(e))
        exit(1)

    for repo in get_repos(config):
        repo.proceed()
        state = list()
        for s in ('unpulled', 'unpushed'):
            if getattr(repo, s):
                state.append(s)
        print('Repo {} is {}'.format(
            repo.git_dir,
            ' and '.join(state) if state else 'up to date'
        ))
