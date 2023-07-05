#!/usr/bin/env python
import subprocess
import os
import getpass
from chapters import CHAPTERS


REMOTE = "local" if getpass.getuser() == "harry" else "origin"
BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fetch_if_possible(target_dir):
    fetch = subprocess.Popen(
        ["git", "fetch", REMOTE],
        cwd=target_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = fetch.communicate()
    print(stdout.decode(), stderr.decode())
    if fetch.returncode:
        if (
            "Name or service not known" in stderr.decode()
            or "Could not resolve" in stderr.decode()
        ):
            # no internet
            print("No Internet")
            return False
        raise Exception("Error running git fetch")
    return True


def update_sources_for_chapter(chapter, previous_chapter=None):
    source_dir = os.path.join(BASE_FOLDER, "source", chapter, "superlists")
    print("updating", source_dir)
    subprocess.check_output(["git", "submodule", "update", source_dir])
    commit_specified_by_submodule = (
        subprocess.check_output(["git", "log", "-n 1", "--format=%H"], cwd=source_dir)
        .decode()
        .strip()
    )

    connected = fetch_if_possible(source_dir)
    if not connected:
        return

    if previous_chapter is not None:
        # make sure branch for previous chapter is available to start tests
        subprocess.check_output(["git", "checkout", previous_chapter], cwd=source_dir)
        subprocess.check_output(
            ["git", "reset", "--hard", "{}/{}".format(REMOTE, previous_chapter)],
            cwd=source_dir,
        )

    # check out current branch, local version, for final diff
    subprocess.check_output(["git", "checkout", chapter], cwd=source_dir)
    if os.environ.get("CI") == "true":
        # if in CI, we use the submodule commit, to check that the submodule
        # config is up to date
        print("resetting submodule to", commit_specified_by_submodule)
        subprocess.check_output(
            ["git", "reset", "--hard", commit_specified_by_submodule], cwd=source_dir
        )
    else:
        print("skipping {} reset on dev machine".format(chapter))


def main():
    """
    update sources for all chapters
    """
    for chapter, previous_chapter in zip(CHAPTERS, [None, *CHAPTERS]):
        update_sources_for_chapter(chapter, previous_chapter=previous_chapter)


if __name__ == "__main__":
    main()
