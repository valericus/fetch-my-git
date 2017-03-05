import os
import logging
from configparser import ConfigParser, NoSectionError

from git import Repo, InvalidGitRepositoryError


logger = logging.getLogger(__name__)


def get_remote_url(repo: Repo, remote_name: str):
    return repo.remote(remote_name)\
        .config_reader.config.get('remote "{}"'.format(remote_name), 'url')


def make_config(paths, base_dir: str=None):
    logger.debug('Trying to create config from directories {}'.format(paths))
    result = ConfigParser()
    result[result.default_section]['remote_name'] = 'origin'
    result[result.default_section]['branch'] = 'master'
    result[result.default_section]['auto_merge'] = 'no'
    result[result.default_section]['hard_reset'] = 'no'

    for path in paths:
        for sub_path in os.listdir(path):
            sub_path = os.path.join(path, sub_path)
            logger.debug('Investigating directory {}'.format(sub_path))
            try:
                repo = Repo(sub_path)
            except InvalidGitRepositoryError:
                logger.debug('{} is not git repo'.format(sub_path))
                continue
            section = os.path.basename(repo.working_dir)
            logger.debug('git repo found in {}, adding section {}'
                         .format(sub_path, section))
            result.add_section(section)
            try:
                result[section]['origin'] = get_remote_url(repo, 'origin')
                logger.debug('Origin {} found'
                             .format(result[section]['origin']))
            except (ValueError, NoSectionError):
                result.remove_section(section)
                logger.warning('No origin found for {}, skipped'
                               .format(sub_path))
                continue

            result[section]['local'] = repo.working_dir
            if base_dir:
                result[section]['local'].replace(base_dir, '~')

    return result
