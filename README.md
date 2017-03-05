**fetch-my-git** is an utility designed to notify users about updates in
in some remote repositories. It makes no magic, just scheduled
`git fetch` and `git merge-base`. It also can make merge if changes can
be merged in fast-forward mode or just keep some directory absolutely
equal to some remote repo purging any local update.
