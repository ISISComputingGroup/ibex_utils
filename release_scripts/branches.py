import argparse
import git
import logging
import os
import sys
import re
import xml.etree.ElementTree as ET
from typing import Any, List
from git.repo import Repo



EPICS_REPO_URL = "https://github.com/ISISComputingGroup/EPICS.git"
IBEX_REPO_URL = "https://github.com/ISISComputingGroup/ibex_gui.git"
GENIE_PYTHON_URL = "https://github.com/ISISComputingGroup/genie_python.git"
JSON_BOURNE_URL = "https://github.com/ISISComputingGroup/JSON_bourne.git"

EPICS_DIR = "EPICS"
IBEX_DIR = "IBEX"
SCRIPT_GEN_DIR = "SCRIPT_GEN"
GENIE_PYTHON_DIR = "genie_python"
JSON_BOURNE_DIR = "JSON_bourne"

INSTETC_TEMPLATE_LOCAL_PATH = os.path.join("INSTETC", "INSTETC-IOC-01App", "Db", "svn-revision.db.tmpl")
INSTETC_TEMPLATE_ABSOLUTE_PATH = os.path.join(EPICS_DIR, "ioc", "master", INSTETC_TEMPLATE_LOCAL_PATH)

IBEX_MANIFEST_LOCAL_PATH = os.path.join("base", "uk.ac.stfc.isis.ibex.e4.client", "META-INF", "MANIFEST.MF")
IBEX_MANIFEST_ABSOLUTE_PATH = os.path.join(IBEX_DIR, IBEX_MANIFEST_LOCAL_PATH)
IBEX_POM_LOCAL_PATH = os.path.join("base", "uk.ac.stfc.isis.ibex.e4.client", "pom.xml")
IBEX_POM_ABSOLUTE_PATH = os.path.join(IBEX_DIR, IBEX_POM_LOCAL_PATH)

SCRIPT_GENERATOR_MANIFEST_LOCAL_PATH = os.path.join("base", "uk.ac.stfc.isis.scriptgenerator.client", "META-INF", "MANIFEST.MF")
SCRIPT_GENERATOR_MANIFEST_ABSOLUTE_PATH = os.path.join(SCRIPT_GEN_DIR, SCRIPT_GENERATOR_MANIFEST_LOCAL_PATH)
SCRIPT_GENERATOR_POM_LOCAL_PATH = os.path.join("base", "uk.ac.stfc.isis.scriptgenerator.client", "pom.xml")
SCRIPT_GENERATOR_POM_ABSOLUTE_PATH = os.path.join(SCRIPT_GEN_DIR, SCRIPT_GENERATOR_POM_LOCAL_PATH)

GENIE_PYTHON_VERSION_LOCAL_PATH = os.path.join("Lib", "site-packages", "genie_python", "version.py")
GENIE_PYTHON_VERSION_ABSOLUTE_PATH = os.path.join(GENIE_PYTHON_DIR, GENIE_PYTHON_VERSION_LOCAL_PATH)



def write_instetc_version(version: str):
    logging.info(f"Writing version '{version}' to '{INSTETC_TEMPLATE_ABSOLUTE_PATH}'.")

    with open(INSTETC_TEMPLATE_ABSOLUTE_PATH, "r") as file:
        data = re.sub(r"0\.0\.0(\.\$WCREV\$)", rf"{version}\1", file.read(), count=1)

    with open(INSTETC_TEMPLATE_ABSOLUTE_PATH, "w") as file:
        file.write(data)

def write_gui_version(manifest_path: str, pom_path: str, version: str):
    # In Manifest file.
    logging.info(f"Writing version '{version}' to '{manifest_path}'.")

    # "\1{version}" doesn't work as version can be e.g. 1.2.3 which gives \11.2.3 being interpreted as \11
    # so break out the space match and add it back afterwards
    with open(manifest_path, "r") as file:
        data = re.sub(r"(Bundle-Version:)[ ].*", rf"\1 {version}", file.read(), count=1)

    with open(manifest_path, "w") as file:
        file.write(data)

    # In pom.xml file.
    logging.info(f"Writing version '{version}' to '{pom_path}'.")

    namespace = "http://maven.apache.org/POM/4.0.0"
    ET.register_namespace("", namespace)
    tree = ET.parse(pom_path)
    root = tree.getroot()
    version_element = root.find(f"{{{namespace}}}version")

    if version_element is not None:
        version_element.text = version
    else:
        v = ET.SubElement(root, "version")
        v.text = version
        v.tail = "\n"
        root.find(f"{{{namespace}}}parent").tail = "\n  "

    tree.write(pom_path)

def write_genie_python_version(version: str):
    logging.info(f"Writing version '{version}' to '{GENIE_PYTHON_VERSION_ABSOLUTE_PATH}'.")
    
    with open(GENIE_PYTHON_VERSION_ABSOLUTE_PATH, "w") as file:
        file.write(f"VERSION = \"{version}\"\n")


class ReleaseBranch:
    """Wrapper around a Repo object. Used to perform Git operations on a release branch."""

    def __init__(self, repo: Repo = None):
        self.repo = repo
    
    def create(self, url: str, dir: str, branch_name: str, submodules: bool = False):
        """
        Initializes a repository by using 'git clone'.
        Creates a release branch for the main repository and, optionally, all submodules.

        Uses an environment variable 'REMOTE' set in Jenkins to check if submodules should be updated with '--remote'.
        Will fail the script if there are any new submodule commits. Defaults to true.

        Uses an environment variable 'TAG' set in Jenkins as the source for the release branch.
        Defaults to 'HEAD'. Set to specific tag when doing a patch release.

            Parameters:
                url: The repository remote url.
                dir: The directory to clone to.
                branch_name: The name of the release branch.
                submodules: If submodules should be updated and have release branches created.
        """

        self.branch_name = branch_name

        logging.info(f"Cloning '{url}' into '{dir}'.")
        self.repo = git.Repo.clone_from(url=url, to_path=dir)
        if branch_name in self.repo.references:
            logging.error(f"Branch name '{branch_name}' already exists for repo '{url}'.")
            sys.exit(1)
        
        source = os.getenv("TAG")
        # if we specify a top level tag other then HEAD then this is
        # inconsistent with asking that all submodules be
        # on their latest version as we would only give a TAG if we
        # specifically didn't want them to be the latest
        if source != "HEAD" and os.getenv("REMOTE") == "true":
            logging.error(f"Specifying a branch source '{source}' is not consistent with REMOTE == true.")
            sys.exit(1)

        logging.info(f"Creating branch '{branch_name}' for '{self.repo.remote().url}' from '{source}'.")
        self.repo.create_head(branch_name, commit=source).checkout()

        if submodules:
            if os.getenv("REMOTE") == "true":
                logging.info(f"Updating submodules from remote for '{self.repo.remote().url}'.")
                self.repo.git.submodule("update", "--init", "--recursive", "--remote")

                new_commits = False
                for i in self.repo.index.diff(None).iter_change_type("M"):
                    logging.warning(f"Submodule '{i.a_path}' in repo '{self.repo.remotes.origin.url}' has new commits.")
                    new_commits = True

                if new_commits:
                    logging.error("Submodules updated from remote have new commits. Stopping script.")
                    sys.exit(1)
            else:
                logging.info(f"Updating submodules for '{self.repo.remote().url}'.")
                self.repo.git.submodule("update", "--init", "--recursive")

            # check for branch name in all submodules before we create any, so
            # if we have made a mistake there is less to remove afterwards
            for submodule in self.repo.submodules:
                if branch_name in submodule.module().references:
                    logging.error(f"Branch name '{branch_name}' already exists for repo '{submodule.module().remote().url}'.")
                    sys.exit(1)

            for submodule in self.repo.submodules:
                logging.info(f"Creating branch '{branch_name}' for: '{submodule.module().remote().url}'.")
                submodule.module().create_head(branch_name).checkout()

    def commit(self, items: List[Any], msg: str):
        """
        Commits a list of items.

            Parameters:
                items: The list of items to stage.
                msg: The commit message.
        """
        logging.info(f"Committing '{msg}' to '{self.repo.remote().url}'.")

        self.repo.index.add(items)
        self.repo.index.commit(msg)

    def push(self, submodules: bool = False):
        """
        Pushes changes to remote.

            Parameters:
                submodules: If changes to submodules should be pushed.
        """
        logging.info(f"Pushing to repo '{self.repo.remote().url}'.")

        if submodules:
            for submodule in self.repo.submodules:
                logging.info(f"Pushing to submodule '{submodule.module().remote().url}'.")
                submodule.module().git.push("origin", self.branch_name)

        self.repo.git.push("origin", self.branch_name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format="[%(asctime)s][%(levelname)s][%(filename)s:%(funcName)s:%(lineno)s]: %(message)s")


    parser = argparse.ArgumentParser(description="Create release branches.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--version", default=None, help="Release version.", required=True)
    args = parser.parse_args()


    if os.getenv("EPICS") == "true":
        epics = ReleaseBranch()
        epics.create(EPICS_REPO_URL, EPICS_DIR, f"Release_{args.version}", True)
        write_instetc_version(args.version)

        ioc_submodule = epics.repo.submodule("ioc/master")
        ioc = ReleaseBranch(ioc_submodule.module())
        ioc.commit([INSTETC_TEMPLATE_LOCAL_PATH], f"Update version to {args.version}.")
        # Set submodule hash to created commit hash. This ensures we use the latest submodule commit.
        ioc_submodule.binsha = ioc.repo.head.commit.binsha

        epics.commit([ioc_submodule], "Update submodule ioc.")
        epics.push(True)


    if os.getenv("IBEX_GUI") == "true":
        ibex = ReleaseBranch()
        ibex.create(IBEX_REPO_URL, IBEX_DIR, f"Release_{args.version}")
        write_gui_version(IBEX_MANIFEST_ABSOLUTE_PATH, IBEX_POM_ABSOLUTE_PATH, args.version)
        ibex.commit([IBEX_MANIFEST_LOCAL_PATH, IBEX_POM_LOCAL_PATH], f"Update version to {args.version}.")
        ibex.push()


    if os.getenv("SCRIPT_GENERATOR") == "true":
        script_gen = ReleaseBranch()
        script_gen.create(IBEX_REPO_URL, SCRIPT_GEN_DIR, f"Release_Script_Gen_{args.version}")
        write_gui_version(SCRIPT_GENERATOR_MANIFEST_ABSOLUTE_PATH, SCRIPT_GENERATOR_POM_ABSOLUTE_PATH, args.version)
        script_gen.commit([SCRIPT_GENERATOR_MANIFEST_LOCAL_PATH, SCRIPT_GENERATOR_POM_LOCAL_PATH], f"Update version to {args.version}.")
        script_gen.push()


    if os.getenv("GENIE_PYTHON") == "true":
        genie_python = ReleaseBranch()
        genie_python.create(GENIE_PYTHON_URL, GENIE_PYTHON_DIR, f"Release_{args.version}")
        write_genie_python_version(args.version)
        genie_python.commit([GENIE_PYTHON_VERSION_LOCAL_PATH], f"Update version to {args.version}.")
        genie_python.push()


    if os.getenv("JSON_BOURNE") == "true":
        json_bourne = ReleaseBranch()
        json_bourne.create(JSON_BOURNE_URL, JSON_BOURNE_DIR, f"Release_{args.version}")
        json_bourne.push()
