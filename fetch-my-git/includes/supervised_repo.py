import os
import logging

from git import Repo, InvalidGitRepositoryError


logger = logging.getLogger(__name__)


class SupervisedRepo(Repo):
    def __init__(self, path: str, remote_name: str, remote_url: str, branch: str,
                 auto_merge: bool=False, hard_reset: bool=False):
        self.remote_name = remote_name
        self.remote_url = remote_url
        self.branch = branch,
        self.auto_merge = auto_merge
        self.hard_reset = hard_reset

        try:
            super().__init__(path)
        except InvalidGitRepositoryError:
            logger.info('No repo found under {}, trying to clone it'
                        .format(path))
            self.clone(path)
            super().__init__(path)

        logger.info('Found git repo under {}'.format(path))

        self.tracked_remote = self.remote(remote_name)
        self.tracked_remote_url = self.tracked_remote.config_reader\
            .config.get('remote "{}"'.format(remote_name), 'url')
        if self.tracked_remote_url != remote_url:
            raise RuntimeError(
                'URL of {}/{} in repo {} is but expected be {}'
                .format(remote_name, branch, path, remote_url)
            )

    def _update_commits(self):
        self.local_commit = self.commit(self.branch)
        self.remote_commit = self.commit('{}/{}'.format(self.remote_name,
                                                        self.branch))
        self.common_base = self.git.merge_base(self.local_commit,
                                               self.remote_commit)

    def proceed(self, refspec=None, progress=None, **kwargs):
        self.tracked_remote.fetch(refspec=refspec, progress=progress, **kwargs)
        self._update_commits()
        if self.auto_merge:
            logger.info('Auto merge is enabled for {}, trying to merge'
                         .format(self.git_dir))
            if self.hard_reset:
                logger.info('Hard reset enabled for {}, resetting'
                            .format(self.git_dir))
                self.git.reset('--hard', self.common_base)
            self.git.merge(self.tracked_remote, self.branch, '--ff-only')

    @property
    def unpulled(self):
        self._update_commits()
        return self.common_base != self.remote_name

    @property
    def unpushed(self):
        self._update_commits()
        return self.common_base != self.local_commit