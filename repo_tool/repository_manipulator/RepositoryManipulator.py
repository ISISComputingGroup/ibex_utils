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

import re
from datetime import datetime, timedelta

import pytz as pytz
from github3 import GitHubError, login

# template for the sprint milestones title
SPRINT_MILESTONE_REGEX = "SPRINT_(\d+)_(\d+)_(\d+)"
SPRINT_MILESTONE_TEMPLATE = "SPRINT_{year:04d}_{month:02d}_{day:02d}"


class UserError(Exception):
    """
    Exception with a message that can be shown to the user
    """

    def __init__(self, detail):
        super(UserError, self).__init__()
        self.detail = detail

    def __str__(self):
        return self.detail


class RepositoryManipulator:
    """
    GitHub Repository Manipulator class

    Provides functions that can manipulate a set of repositories in GitHub
    Uses github3.py: https://github.com/sigmavirus24/github3.py
    """

    def __init__(self, username, token, login_method=login, dry_run=False):
        """
        Constructor
        :param username: username
        :param token: token for access to GitHub
        :param login_method: method to login to GitHub and provide a GitHub manipulation object
        :param dry_run: true if nothing should be added or deleted
        :return:
        """
        self._repo_list = []
        self.dry_run = dry_run
        try:
            self.github_api = login_method(username, token=token)
        except GitHubError as ex:
            raise UserError(f"Failed to log in. {str(ex)}")

    @staticmethod
    def get_checked_date(date_string):
        """
        Return a date dictionary from a text date
        :param date_string: date string YYYY-MM-DD
        :return: date dictionary
        """
        match = re.match("(\d{4})-(\d+)-(\d+)\s*", date_string)
        if match is None:
            raise UserError("Date must of format YYYY-MM-DD")
        try:
            return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except (ValueError, TypeError):
            raise UserError("Invalid date")

    def add_all_repos_for_owner(self, owner_name="ISISComputingGroup"):
        """
        Add all the repositories for an owner to the list of repositories to manipulate;
        assume owner is an organisation but default to user if organisation doesn't exist
        :param owner_name: name of the owner; organisation/user
        :return:
        :raises UserError: when repository can not be found
        """
        try:
            organisation = self.github_api.organization(owner_name)
        except GitHubError as ex:
            raise UserError(f"Failed to get owner as organisation. {str(ex)}")

        try:
            if organisation is None:
                print(f"Owner {owner_name} not found as organisation, defaulting to user")
                iter_repos = self.github_api.iter_user_repos(owner_name)
            else:
                iter_repos = organisation.iter_repos()
            self._add_to_repositories_to_use(iter_repos)
        except GitHubError as ex:
            raise UserError(f"Failed to get owner's repositories. {str(ex)}")

    def _add_to_repositories_to_use(self, iter_repos):
        """
        Add the repositories from the generator to the list and sort by name
        :param iter_repos: generator for repositories
        :return:
        """
        for repo in iter_repos:
            self._repo_list.append(repo)
        self._sort_repo_list()

    def _sort_repo_list(self):
        """
        sort the repository list
        :return: nothing
        """
        self._repo_list.sort(key=lambda x: x.name)

    def use_repos_for_user(self, owner):
        """
        Add all repositories from the currently logged in user to the list of repositories to manipulate
        :param owner: owner of the repos
        :return:
        """
        try:
            self._add_to_repositories_to_use(self.github_api.iter_user_repos(owner))
        except GitHubError as ex:
            raise UserError(f"Failed to get user repositories. {str(ex)}")

    def add_repository_from(self, owner, names):
        """
        Add repositories to those to be manipulated
        :param owner: owner of the repository
        :param names: repository names
        :return: nothing
        """
        try:
            for name in names:
                repo = self.github_api.repository(owner, name)
                if repo is None:
                    raise UserError(f"Repository {name} does not exist for {owner}")
                self._repo_list.append(repo)
                self._sort_repo_list()
        except GitHubError as ex:
            raise UserError(f"Failed to get named repositories. {str(ex)}")

    def update_milestones(self, date_from, date_to, close_old_milestones):
        """
        Update milestones for all selected repositories
        :param date_to: date that the milestone runs to
        :param date_from: date that the milestone runs from
        :param close_old_milestones: close old sprint milestones, if possible
        :return:
        """
        print("Milestones")
        print("")
        if date_from is not None:
            from_date = RepositoryManipulator.get_checked_date(date_from)
            new_milestone_title = SPRINT_MILESTONE_TEMPLATE.format(
                year=from_date.year, month=from_date.month, day=from_date.day)
            due_on_date = RepositoryManipulator.get_checked_date(date_to)
            due_on = due_on_date.isoformat()+"Z"
        else:
            due_on = None
            new_milestone_title = None

        for repo in self._repo_list:
            print(f"{repo.name}:")
            if not repo.has_issues:
                print("    no issues milestone not updates")
            else:
                self._update_milestones_on_rep(due_on, new_milestone_title, repo, close_old_milestones)

    def _update_milestones_on_rep(self, due_on, new_milestone_title, repo, close_old_milestones):
        """
        Create a new milestones for the repository if it does not exist already
        :param due_on: date that the milestone is due on
        :param new_milestone_title: title for the milestone
        :param repo: repository to which it should be added
        :return:
        """
        for milestone in repo.iter_milestones(state='open'):
            if close_old_milestones:
                self._close_milestone_if_old(milestone, repo.name)
            if new_milestone_title is not None and milestone.title == new_milestone_title:
                return

        if new_milestone_title is None:
            return

        print(f"    milestone add {new_milestone_title}")
        if not self.dry_run:
            milestone = repo.create_milestone(
                title=new_milestone_title,
                description="Milestone for sprint.",
                due_on=due_on)
            if milestone is None:
                raise UserError("Unknown error creating milestone on repository.")

    def _close_milestone_if_old(self, milestone, repo_name):
        """
        Close a milestone if it is old
        :param milestone: milestone to close
        :param repo_name: repository that the milestone is from
        :return:
        :raises UserError: if there is a problem closing the milestone
        """

        match = re.match(SPRINT_MILESTONE_REGEX, milestone.title)
        if match is not None:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))

            milestone_date = datetime(year, month, day, tzinfo=pytz.utc)
            close_issue = milestone.due_on is not None and milestone.due_on < datetime.now(pytz.utc)
            if not close_issue and milestone_date + timedelta(days=31) < datetime.now(pytz.utc):
                close_issue = True

            if close_issue and milestone.open_issues > 0:
                print(f"Milestone '{milestone.title}' is past its due date but has open issues so can not be closed")
            elif close_issue:
                print(f"Close {milestone.title}")
                if not self.dry_run:
                    if not milestone.update(state="closed"):
                        raise UserError(f"Can not close milestone '{milestone.title}' in repo '{repo_name}'")

    def update_labels(self, ensure_labels):
        """
        Update labels on all repositories
        :param ensure_labels: labels to ensure are on the repository; list of (colour, name) tuples
        :type ensure_labels: list(tuple(string, string))
        :return:
        """
        print("Labels")
        print("")

        for repo in self._repo_list:
            print(f"{repo.name}:")
            if not repo.has_issues:
                print("    no issues labels not updates")
            else:
                self._update_labels_on_rep(ensure_labels, repo)

    def _update_labels_on_rep(self, ensure_labels, repo):
        """
        Update the labels on a single repository
        :param ensure_labels: labels to ensure are on the repository; list of (colour, name) tuples
        :param repo: repository top update
        :return:
        """
        current_labels = {}
        for label in repo.iter_labels():
            current_labels[label.name] = label

        for label_name, label_colour in ensure_labels:
            try:
                if label_name not in current_labels.keys():
                    print(f"    label add {label_name}")
                    if not self.dry_run:
                        label = repo.create_label(label_name, label_colour)
                        if label is None:
                            raise UserError("Unknown error creating label on repository.")
                        current_labels[label_name] = label
                elif current_labels[label_name].color != label_colour:
                    current_labels[label_name].update(name=label_name, color=label_colour)
            except GitHubError as ex:
                if ex.code == 422:
                    raise UserError("Validation filed on create/modify label")

    def list_repos(self):
        """
        List the repositories
        :return:
        """
        print("Repository set")
        for repo in self._repo_list:
            print(f"  {repo.name}:")
