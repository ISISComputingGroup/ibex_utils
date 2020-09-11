#!/usr/bin/env python

"""
This file is part of the ISIS IBEX application.
Copyright (C) 2012-2016 Science & Technology Facilities Council.
All rights reserved.

This program is distributed in the hope that it will be useful.
This program and the accompanying materials are made available under the
terms of the Eclipse Public License v1.0 which accompanies this distribution.
EXCEPT AS EXPRESSLY SET FORTH IN THE ECLIPSE PUBLIC LICENSE V1.0, THE PROGRAM
AND ACCOMPANYING MATERIALS ARE PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES
OR CONDITIONS OF ANY KIND.  See the Eclipse Public License v1.0 for more details.
"""

import argparse
from getpass import getpass

import sys

from repository_manipulator.RepositoryManipulator import RepositoryManipulator, UserError


def main(settings, token):
    """
    Main function
    :param settings: settings
    :param token: git hub token
    :return: error code
    """
    try:
        isis_repo_access = RepositoryManipulator(settings.username, token, dry_run=settings.dry_run)

        if settings.repo is not None:
            isis_repo_access.add_repository_from(settings.owner, [settings.repo])
        elif settings.repo_file is not None:
            repository_names = _get_repository_name_from_file(settings.repo_file)
            isis_repo_access.add_repository_from(settings.owner, repository_names)
        else:
            isis_repo_access.add_all_repos_for_owner(settings.owner)

        # milestones
        action = False
        if settings.date_from is not None or settings.ms_close:
            action = True
            isis_repo_access.update_milestones(settings.date_from, settings.date_to, settings.ms_close)

        # labels
        labels_list = []
        if settings.ensure_label is not None:
            action = True
            labels_list.append((settings.ensure_label, settings.ensure_label_colour))
        if settings.ensure_label_file is not None:
            labels_list.extend(_get_labels_from(settings.ensure_label_file))
            action = True
        if len(labels_list) > 0:
            isis_repo_access.update_labels(labels_list)

        # other
        if not action:
            isis_repo_access.list_repos()

        return 0
    except UserError as ex:
        print("Failed to update repositories: {0}".format(ex))
        return -1


def _get_repository_name_from_file(filename):
    """
    Get the repository names from a file
    :param filename: filename
    :return: unique items in file
    """
    try:
        repository_names = set()
        for line in file(filename):
            repo_name = line.strip()
            if repo_name != "" and not repo_name.startswith("#"):
                repository_names.add(repo_name)
        if len(repository_names) == 0:
            raise UserError("File has no entries in")
    except IOError as ex:
        raise UserError("Can not open repository list file, {0}".format(ex))
    return repository_names


def _get_labels_from(filename):
    """
    Get the labels from a file
    :param filename: file to get names from
    :return: label names and colours
    """
    try:
        has_comment = False
        labels = []
        for line in file(filename):
            label_line = line.strip()
            is_comment = label_line.startswith("#")
            has_comment = has_comment or is_comment
            if label_line != "" and not is_comment:
                split_line = line.split(",", 1)
                if len(split_line) != 2:
                    raise UserError("Label lines must be <colour code>, <label name>. Line: {0}".format(label_line))
                label_colour = split_line[0].strip()
                label_name = split_line[1].strip()
                if label_name == "":
                    raise UserError("Label name must not be empty. Line: {0}".format(label_line))
                if label_colour == "":
                    raise UserError("Label colour must not be empty. Line: {0}".format(label_line))

                labels.append((label_name, label_colour))
        if len(labels) == 0:
            if has_comment:
                raise UserError("Labels file has no entries in. "
                                "NB Lines with a # are comment, colours should not start with a hash")
            else:
                raise UserError("Labels file has no entries in")
    except IOError as ex:
        raise UserError("Can not open labels file, {0}".format(ex))
    return labels


def _parse_command_line():
    """
    Parse the command line
    :return: settings for the run
    """
    parser = argparse.ArgumentParser(
        description='Manipulate a set of repositories, you can add milestones, close milestones, add labels. '
                    'E.g. -u John-Holt-Tessella -o John-Holt-Tessella --ms-from 2010-04-02 --ms-to 2011-05-02 '
                    '--dry_run --repo repo_name')
    parser.add_argument('--dry-run', action="store_true", help="Don't change anything just tell me what you would do.")
    parser.add_argument('-u', '--username', required=True, help="GitHub username")

    # specify repositories
    parser.add_argument('-o', '--owner', required=True, default="ISISComputingGroup", help="Owner of the repositories")
    parser.add_argument('--repo-file', required=False, default=None, dest="repo_file",
                        help="Apply the changes to repositories in this file. File is list of repository names,"
                             "comments (lines starting with a #) and blank lines are ignored")
    parser.add_argument('--repo', required=False, default=None, dest="repo",
                        help="Apply the changes to this repository")

    # milestone creation
    parser.add_argument('--ms-from', required=False, dest="date_from", help="Date from which the sprint starts.")
    parser.add_argument('--ms-to', required=False, dest="date_to", help="Date to which the sprint runs.")

    # milestone close
    parser.add_argument('--ms-close', dest="ms_close", action="store_true",
                        help="Close all sprint milestones which are passed with closed tickets.")

    # label creation
    parser.add_argument('--label-name', required=False, default=None, dest="ensure_label",
                        help="Ensure that the repository has the following label")
    parser.add_argument('--label-colour', required=False, default=None, dest="ensure_label_colour",
                        help="Ensure that the repository has a label that is this colour. Colours are colour code no "
                             "leading #, e.g. 626262")
    parser.add_argument('--label-file', required=False, default=None, dest="ensure_label_file",
                        help="Ensure that the repository has the following labels read from this file. "
                             "File is lines of '<colour code>, <label name>'")

    if len(sys.argv) == 1:
        sys.stderr.write('You need to use commandline arguments and you passed none. If in windows make sure your *.py '
                         'is linked to \"...\python.exe "%1" %*\" or use python change_repos.py <args> \n')

    settings = parser.parse_args()

    if settings.date_from is not None or settings.date_to is not None:
        if settings.date_from is None or settings.date_to is None:
            print("Error from and to date for milestone must be set if one is")
            exit(-1)
        try:
            RepositoryManipulator.get_checked_date(settings.date_from)
        except UserError as ex:
            print("Error in from date: {0}".format(ex))
            exit(-1)
        try:
            RepositoryManipulator.get_checked_date(settings.date_to)
        except UserError as ex:
            print("Error in to date: {0}".format(ex))
            exit(-1)

    if settings.ensure_label is not None or settings.ensure_label_colour is not None:
        if settings.ensure_label is None or settings.ensure_label_colour is None:
            print("Error label name and colour must both be set if one is")
            exit(-1)

    return settings


def _get_user_token():
    """
    Get the users access token for github
    :return: token
    """
    token = ""
    while token == "":
        token = getpass('GitHub token for user (blank for help): ')
        if token == "":
            print("To get a personal token from git hub")
            print("  1. Log into git hub")
            print("  2. Open Your Setting (from icon top right)")
            print("  3. Click Personal access tokens")
            print("  4. Generate new token")
            print("  5. Add token description")
            print("  6. Select repo (Full control of private repositories)")
            print("  7. Generate token")
            print("  8. Copy the token an store it somewhere safe")
    return token


if __name__ == '__main__':
    exit(
        main(_parse_command_line(), _get_user_token())
        )
