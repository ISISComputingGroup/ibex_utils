import json
import urllib.request
from collections import Counter

system_tests_url = "https://epics-jenkins.isis.rl.ac.uk/job/System_Tests_IOCs/{}/testReport/api/json"

test_metadata = "https://epics-jenkins.isis.rl.ac.uk/job/System_Tests_IOCs/api/json"

number_to_print = 15

failing_tests = Counter()

try:
    page = urllib.request.urlopen(test_metadata)

    test_metadata_json = json.loads(page.read())
except Exception as e:
    print(f"Failed to get metadata: {e}")

builds = [build["number"] for build in test_metadata_json["builds"]]

current_build = test_metadata_json["lastBuild"]["number"]
complete_build = test_metadata_json["lastCompletedBuild"]["number"]

# No results for current build
if complete_build != current_build:
    builds.remove(current_build)

for test_num in builds:
    print(f"Getting data for {test_num}")
    try:
        page = urllib.request.urlopen(system_tests_url.format(test_num))

        test_json = json.loads(page.read())
    except Exception as e:
        print(f"Failed to get test data for {test_num}: {e}")

    for test in test_json["suites"]:
        for case in test["cases"]:
            if case["status"] == "FAILED":
                failing_tests.update([case["className"] + "." + case["name"]])

failing_tests = failing_tests.most_common(number_to_print)
for test in failing_tests:
    print(test)
