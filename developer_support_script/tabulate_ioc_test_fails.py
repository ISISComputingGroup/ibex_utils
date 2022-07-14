"""
A utility script to tabulate IOC test failiures to allow for spotting consistent errors
(as apposed to transient ones) by looking across several historical builds 
of the various system test jobs.

So the base table would be test name v number of failures over time window considered,
but then that could be enhanced with additional information e.g. last time passed,
breakdown of which jobs it failed on, ibex build numebrs of failures. Not sure what
are most useful, but starting point is just proviing an overview of
which test is failing the most consistently

"""

# To start with just get name of test and quantity of failures across builds

# Dependencies
import json
import urllib.request
from collections import Counter
# import numpy
# import pandas as pd
# import plotly.graph_objects as go


def request_page_and_metadata(url: str):
    """
    Request a jenkins webpage and return 
    the metadata json containing system test build info

    :param url: the url to the jenkins webpage
    :return: the metadata json
    """
    try:
        page = urllib.request.urlopen(url)
        metadata = json.loads(page.read())
        return metadata
    except Exception as e:
        print(f"Failed to get metadata: {e}")

def get_all_builds(metadata: dict):
    """
    Return a list of all builds in the system tests job

    :param metadata: the metadata json from the system tests job
    :return: a list of all builds in the system tests job
    """
    builds = [build["number"] for build in test_metadata_json["builds"]]
    return builds

def get_current_and_complete_builds(metadata: dict):
    """
    Return the current and complete builds from the metadata json

    :param metadata: the metadata json from the system tests job
    :return: the current and complete builds from the metadata json
    """
    current_build = test_metadata_json["lastBuild"]["number"]
    complete_build = test_metadata_json["lastCompletedBuild"]["number"]

    return current_build, complete_build

def remove_current_build_if_no_results(builds: list, current_build: int):
    """
    Remove the current build from the list of builds if there 
    are no results for it

    :param builds: the list of builds
    :param current_build: the current build
    :return: the list of builds without the current build if there
    """
    if complete_build != current_build:
        builds.remove(current_build)
    return builds

def retrieve_test_data(test_num: int):
    """
    Retrieve test data for a given build number

    :param test_num: the build number to retrieve test data for
    :return: the test data json
    """
    print(f"Getting data for {test_num}")
    try:
        page = urllib.request.urlopen(system_tests_url.format(test_num))
        test_json = json.loads(page.read())
        return test_json
    except Exception as e:
        print(f"Failed to get test data for {test_num}: {e}")

def add_failed_tests_to_counter(test_json: dict, failing_tests: Counter):
    """
    Add failed tests to a Counter object containing all failed tests

    :param test_json: the test data json
    :param failing_tests: the Counter object to add failed tests to
    :return: the Counter object containing all failed tests
    """
    for test in test_json["suites"]:
        for case in test["cases"]:
            if case["status"] == "FAILED":
                failing_tests.update([case["className"] + "." + case["name"]])
    return failing_tests

def retrieve_failed_tests_from_builds(builds: list):
    """
    Retreive tests data and return failed tests from builds 
    within a Counter object.

    :param builds: the list of builds to retrieve test data for
    :return: a Counter object containing all failed tests
    """
    test_counter = Counter()
    for test_num in builds:
        test_json = retrieve_test_data(test_num)
        failing_tests = add_failed_tests_to_counter(test_json, test_counter)
    return failing_tests

def get_top_n_failed_tests(failing_tests: Counter, n: int):
    """
    Get the top n failed tests from a Counter object of failed tests

    :param failing_tests: the Counter object containing all failed tests
    :param n: the number of failed tests to return
    :return: the top n failed tests
    """
    return failing_tests.most_common(n)

def print_failing_tests(failing_tests: Counter):
    """
    Print the top n failing tests

    :param failing_tests: the top n failing tests
    """
    for test in failing_tests:
        print(test)


system_tests_url = "https://epics-jenkins.isis.rl.ac.uk/job/System_Tests/{}/testReport/api/json"
test_metadata = "https://epics-jenkins.isis.rl.ac.uk/job/System_Tests/api/json"

number_to_print = 15

test_metadata_json = request_page_and_metadata(test_metadata) # NEW
builds = get_all_builds(test_metadata_json) # NEW
current_build, complete_build = get_current_and_complete_builds(test_metadata_json) # NEW
remove_current_build_if_no_results(builds, current_build) # NEW
failing_tests = retrieve_failed_tests_from_builds(builds) # NEW
failing_tests = get_top_n_failed_tests(failing_tests, number_to_print) # NEW
print_failing_tests(failing_tests) # NEW
