# Utilities for the IBEX Project

## repo-tools

Python scripts to manipulate the ibex repositories.

### Installation

    cd ibex_utils\repo-tool
    pip install .

### Usage

    python change_repos.py [-h] [--dry-run] -u USERNAME -o OWNER
                       [--repo-file REPO_FILE] [--repo REPO]
                       [--ms-from DATE_FROM] [--ms-to DATE_TO] [--ms-close]
                       [--label-name ENSURE_LABEL]
                       [--label-colour ENSURE_LABEL_COLOUR]
                       [--label-file ENSURE_LABEL_FILE]

    Manipulate a set of repositories, you can add milestones, close milestones, add labels. E.g. -u John-Holt-Tessella -o John-Holt-Tessella --from 2010-04-02 --to 2011-05-02 --dry_run --repo repo_name

    optional arguments:
      -h, --help            show this help message and exit
      --dry-run             Don't change anything just tell me what you would do.
      -u USERNAME, --username USERNAME                       GitHub username
      -o OWNER, --owner OWNER                        Owner of the repositories
      --repo-file REPO_FILE
                            Apply the changes to repositories in the file
      --repo REPO           Apply the changes to this repository
      --ms-from DATE_FROM   Date from which the sprint starts.
      --ms-to DATE_TO       Date to which the sprint runs.
      --ms-close            Close all sprint milestones which are passed with
                            closed tickets.
      --label-name ENSURE_LABEL
                            Ensure that the repository has the following label
      --label-colour ENSURE_LABEL_COLOUR
                            Ensure that the repository has a label that is this
                            colour. Colours are colour code no leading #, e.g.
                            626262
      --label-file ENSURE_LABEL_FILE
                            Ensure that the repository has the following labels
                            read from this file. File is lines of '<colour code>,
                            <label name>'
