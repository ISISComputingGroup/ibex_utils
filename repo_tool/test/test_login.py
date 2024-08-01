import unittest
from datetime import datetime

from github3 import GitHubError
from hamcrest import *
from mock import Mock

from repo_tool.repository_manipulator.RepositoryManipulator import RepositoryManipulator, UserError


class GitHubMock:
    username = None
    token = None

    git_hub_mock = None

    def __init__(self, repo_list=None):
        self.repo_list = repo_list

    @staticmethod
    def login(user, token):
        if (GitHubMock.username is None and GitHubMock.token is None) or \
                (user == GitHubMock.username and token == GitHubMock.token):
            if GitHubMock.git_hub_mock is None:
                return GitHubMock()
            else:
                return GitHubMock.git_hub_mock

        resp = Mock(side_effect="Error")
        resp.status_code = 401
        raise GitHubError(resp)

    @staticmethod
    def setUsernameAndPassword(usename, token):
        GitHubMock.username = usename
        GitHubMock.token = token


class TestLogin(unittest.TestCase):

    def setUp(self):
        self.github = GitHubMock

    def test_with_invalid_credential_user_cannot_log_in(self):
        GitHubMock.setUsernameAndPassword("user", "token")

        assert_that(
            calling(RepositoryManipulator).with_args(username="", token="", login_method=self.github.login),
            raises(UserError))

    def test_with_valid_credential_does_not_throw_excpetion(self):
        username = "user"
        token = "token"
        GitHubMock.setUsernameAndPassword(username, token)

        isis_repos = RepositoryManipulator(username=username, token=token, login_method=self.github.login)


class TestCheckedDate(unittest.TestCase):

    def test_GIVEN_blank_WHN_get_checked_date_THEN_error(self):
        date_string = ""

        assert_that(calling(RepositoryManipulator.get_checked_date).with_args(date_string),
                    raises(UserError))

    def test_GIVEN_valid_WHN_get_checked_date_THEN_date_tuple_retuned(self):
        date_string = "2010-02-01"
        expected_date = datetime(2010, 0o2, 0o1)

        result = RepositoryManipulator.get_checked_date(date_string)

        assert_that(result, is_(expected_date))

    def test_GIVEN_invalid_WHN_get_checked_date_THEN_error(self):
        date_string = "2010-13-20"

        assert_that(calling(RepositoryManipulator.get_checked_date).with_args(date_string),
                    raises(UserError))


if __name__ == '__main__':
    unittest.main()
