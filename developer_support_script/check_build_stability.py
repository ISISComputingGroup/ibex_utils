"""
A utility script to retrieve tests data from Jenkins jobs.
Checks for common failures as Jenkins only tracks continuous failures.
"""

import requests
from collections import Counter, defaultdict
from typing import Any


WARNING_THRESHOLD_PERCENTAGE = 10
ERROR_THRESHOLD_PERCENTAGE = 50


def request_json(url: str) -> Any:
    """
    Utility function to get Json data from Jenkins.

    Args:
        url: The URL to request.
    """
    request: requests.Response = requests.get(url)
    
    if request.status_code == requests.codes["ok"]:
        return request.json()
    else:
        print(f"ERROR: Failed to get '{url}': [{request.status_code}] {request.reason}")
        return None

def calculate_level(percentage: int, error_percentage: int, warning_percentage: int) -> str:
    """
    Utility function to calculate log level based on a percentage.
    
    Args:
        percentage: The percentage to calculate.
        error_percentage: The error threshold.
        warning_percentage: The warning threshold.
    """
    if percentage >= error_percentage:
        return "ERROR"
    elif percentage >= warning_percentage:
        return "WARNING"
    else:
        return "INFO"


class JobData:
    """
    Calculates and prints common test failures and number of aborted builds in a Jenkins job.
    """
    def __init__(self, name: str) -> None:
        print(f"****** Evaluating job '{name}' ******")

        self.name = name
        self.job_json = request_json(f"https://epics-jenkins.isis.rl.ac.uk/job/{name}/api/json")
        self.buildable = self.job_json["buildable"]
        self.builds = self._get_builds()
        self.no_test_report_failures = 0
        self.test_reports = self._get_test_reports()
        self.failed_tests = self._get_failed_tests()
        self.num_evaluate_builds = self._get_num_evaluate_builds()
        self.num_aborted_builds = self._get_num_aborted_builds()

    def add_job(self, job):
        """
        add another job's results to here so we can get a summary across jobs
        """
        self.no_test_report_failures += job.no_test_report_failures
        self.test_reports.append(job.test_reports)
        self.failed_tests.update(job.failed_tests)
        self.num_evaluate_builds += job.num_evaluate_builds
        self.num_aborted_builds += job.num_aborted_builds

    def _get_builds(self) -> defaultdict[str, Any]:
        """
        Gets all the build data grouped by status. Ignores builds currently in progress.

        Returns:
            defaultdict: Key is build status, value is the builds Json data. Defaults to empty list.
        """
        builds = defaultdict(list)
        
        # ignore projects that are currently disabled
        if self.buildable:
            for build in self.job_json["builds"]:
                build_json = request_json(f"{build['url']}api/json")
                if not build_json["inProgress"]:
                    builds[build_json["result"]].append(build_json)
        
        return builds

    def _get_num_evaluate_builds(self) -> int:
        """
        Gets the number of builds that have valid test results.
        """
        num = 0

        num += len(self.builds["SUCCESS"])
        num += len(self.builds["UNSTABLE"])
        num += len(self.builds["FAILURE"])
        num -= self.no_test_report_failures

        return num

    def _get_num_aborted_builds(self) -> int:
        """
        Gets the number of aborted builds. Ignores builds that were aborted manually.
        This will generally be the number of builds that timed out.
        """
        aborted_manually = 0

        for build in self.builds["ABORTED"]:
            data = request_json(f"https://epics-jenkins.isis.rl.ac.uk/job/{self.name}/{build['number']}/api/json?tree=actions[causes[*]]")
            for action in data["actions"]:
                if "_class" in action and action["_class"] == "jenkins.model.InterruptedBuildAction":
                    if "causes" in action:
                        for cause in action["causes"]:
                            if "_class" in cause and cause["_class"] == "jenkins.model.CauseOfInterruption$UserInterruption":
                                aborted_manually += 1
                                break

        return len(self.builds["ABORTED"]) - aborted_manually

    def _get_test_reports(self) -> list[Any]:
        """
        Gets the test reports of the builds that have failing tests results.

        Returns:
            list: A list of test reports Json data.
        """
        test_reports_json = []

        bad_builds = self.builds["UNSTABLE"] + self.builds["FAILURE"]
        for build in bad_builds:
            report = request_json(f"{build['url']}testReport/api/json")
            if report is not None:
                test_reports_json.append(report)
            else:
                self.no_test_report_failures += 1

        return test_reports_json

    def _get_failed_tests(self) -> Counter:
        """
        Gets all the failed tests. The name is generated by using the the class name and the test name.

        Returns:
            Counter: Key is test case name, value is number of failures.
        """
        counter = Counter()

        for report in self.test_reports:
            for suite in report["suites"]:
                for case in suite["cases"]:
                    if case["status"] == "FAILED":
                        counter[f"{case['className']}.{case['name']}"] += 1
        
        return counter

    def print_results(self) -> None:
        """
        Prints the percentage of aborted builds for the job, the percentage of failures with no test report, and the percentage failure of each failing test.
        """
        if not self.buildable:
            print("WARNING: build is currently disabled")
            return

        # Aborted builds.
        valid_builds = self.num_evaluate_builds + self.no_test_report_failures
        all_builds = valid_builds + self.num_aborted_builds 
        percentage_aborted_builds = (self.num_aborted_builds / all_builds) * 100
        level = calculate_level(percentage_aborted_builds, ERROR_THRESHOLD_PERCENTAGE, WARNING_THRESHOLD_PERCENTAGE)
        print(f"{level}: Aborted builds [{percentage_aborted_builds:.0f}% ({self.num_aborted_builds}/{all_builds})]")

        # Failures with no test report
        # valid_builds will only be 0 if self.no_test_report_failures is also 0
        if valid_builds > 0:
            percentage_no_test_report_failures = (self.no_test_report_failures / valid_builds) * 100
        else:
            percentage_no_test_report_failures = 0
            
        level = calculate_level(percentage_no_test_report_failures, ERROR_THRESHOLD_PERCENTAGE, WARNING_THRESHOLD_PERCENTAGE)
        print(f"{level}: Failed builds with no Test Report [{percentage_no_test_report_failures:.0f}% ({self.no_test_report_failures}/{valid_builds})]")

        # Tests.
        for name, num in self.failed_tests.most_common():
            if self.num_evaluate_builds > 0:
                percentage_test_failure = (num / self.num_evaluate_builds) * 100
            else:
                percentage_test_failure = 0
            level = calculate_level(percentage_test_failure, ERROR_THRESHOLD_PERCENTAGE, WARNING_THRESHOLD_PERCENTAGE)
            print(f"{level}: [{percentage_test_failure:.0f}% ({num}/{self.num_evaluate_builds})] {name}")


def process_jobs(jobs, summary_name):
    first = True
    job_summary = None
    for job in jobs:
        job_data = JobData(job)
        if first:
            job_summary = job_data
            first = False
        else:
            job_summary.add_job(job_data)
        job_data.print_results()

    print(f"****** Summary across {summary_name} jobs ******")
    job_summary.print_results()

if __name__ == "__main__":
    # Jenkins jobs to evaluate.
    EPICS_JOBS = [
        "System_Tests",
        "System_Tests_debug",
        "System_Tests_static",
        "System_Tests_win32",
        "System_Tests_galilold",
    ]
    SQUISH_JOBS = [
        "System_Tests_Squish"
    ]
    process_jobs(EPICS_JOBS, "EPICS")
    process_jobs(SQUISH_JOBS, "SQUISH")
