"""
A utility script to retrieve system tests from a jenkins job.

The class currently acts as a singleton.
"""

# Dependencies
import http.client as http
import json
import urllib.request
from collections import Counter


class SystemTestData:
    """
    Singleton class to host system test data pulled down from jenkins
    """

    def __init__(self, system_tests_url, test_metadata, test_return_quantity):
        self.system_tests_url = system_tests_url
        self.raw_test_metadata = test_metadata
        self.test_return_quantity = test_return_quantity

        self._json_test_metadata = self.request_page_and_metadata()
        self._raw_builds = self.get_all_builds()
        self._current_build, self._complete_build = self.get_current_and_complete_builds()
        self._proccessed_builds = self.remove_current_build_if_no_results()
        self.failing_tests = self.retrieve_failed_tests_from_builds()
        self.top_n_failing_tests = self.get_top_n_failed_tests()

    def request_page_and_metadata(self):
        """
        Request a jenkins webpage and return
        the metadata json containing system test build info

        :return: the metadata json
        """
        try:
            page = urllib.request.urlopen(self.raw_test_metadata)
            metadata = json.loads(page.read())
            self._json_test_metadata = metadata
            return metadata
        except http.IncompleteRead as err:
            err_page = err.partial
            print(f"Failed to get metadata: {err_page}")
            return None

    def get_all_builds(self):
        """
        Return a list of all builds in the system tests job

        :return: a list of all builds in the system tests job
        """
        builds = [build["number"] for build in self._json_test_metadata["builds"]]
        self._raw_builds = builds
        return builds

    def get_current_and_complete_builds(self):
        """
        Return the current and complete builds from the metadata json

        :return: the current and complete builds from the metadata json
        """

        current_build =  self._json_test_metadata["lastBuild"]["number"]
        complete_build =  self._json_test_metadata["lastCompletedBuild"]["number"]

        return current_build, complete_build

    def remove_current_build_if_no_results(self):
        """
        Remove the current build from the list of builds if there
        are no results for it

        :return: the list of builds without the current build if there
        """
        if self._complete_build != self._current_build:
            self._raw_builds.remove( self._current_build)
        return self._raw_builds

    def retrieve_test_data(self, test_num: int):
        """
        Retrieve test data for a given build number

        :param test_num: the build number to retrieve test data for
        :return: the test data json
        """
        print(f"Getting data for {test_num}")
        try:
            page = urllib.request.urlopen(self.system_tests_url.format(test_num))
            test_json = json.loads(page.read())
            return test_json
        except http.IncompleteRead as err:
            err_page = err.partial
            print(f"Failed to get test data for {test_num}: {err_page}")
            return err_page

    @staticmethod
    def add_failed_tests_to_counter(test_json: dict, failing_tests: Counter):
        """
        Add failed tests to a Counter object containing all failed tests

        :param test_json: the test data json
        :param failing_tests: the Counter object to add failed tests to
        :return: the Counter object containing all failed tests
        """
        try:
            for test in test_json["suites"]:
                for case in test["cases"]:
                    if case["status"] == "FAILED":
                        failing_tests.update([case["className"] + "." + case["name"]])
        except KeyError as err:
            print(f"Failed to add failed tests to counter: {err}")
        return failing_tests


    def retrieve_failed_tests_from_builds(self):
        """
        Retreive tests data and return failed tests from builds
        within a Counter object.

        :return: a Counter object containing all failed tests
        """
        test_counter = Counter()
        for test_num in self._proccessed_builds:
            test_json = self.retrieve_test_data(test_num)
            failing_tests = self.add_failed_tests_to_counter(test_json, test_counter)
        self.failing_tests = failing_tests
        return failing_tests

    def get_top_n_failed_tests(self):
        """
        Get the top n failed tests from a Counter object of failed tests

        :return: the top n failed tests
        """
        return self.failing_tests.most_common(self.test_return_quantity)

    @staticmethod
    def print_failing_tests(failing_tests):
        """
        Print the top n failing tests

        :param failing_tests: the top n failing tests
        """
        for test in failing_tests:
            print(test)


def main():
    """
    Main function
    """

    system_tests_url = "https://epics-jenkins.isis.rl.ac.uk/job/System_Tests/{}/testReport/api/json"
    test_metadata = "https://epics-jenkins.isis.rl.ac.uk/job/System_Tests/api/json"
    my_test_data = SystemTestData(system_tests_url, test_metadata, 15)
    my_test_data.print_failing_tests(my_test_data.top_n_failing_tests)


if __name__ == "__main__":
    main()
