"""
Third party program version checker infrastructure.
"""
import subprocess

INDENT = "    "

def version_check(program, version):
    """
        Decorator for tasks that check program version numbers.

        Identifies the current installed version of program by running the following code in the terminal.
        'program --version'
        If version returned matches required version skips the task otherwise execute it as any other task.
        Prints to user as it goes along.
        """
    
    def _version_check_decorator(func):
        def _wrapper(self_of_decorated_method, *args, **kwargs):
            print(f"Checking \'{program}\' version ...")

            try:
                installed_version = subprocess.check_output(f"{program} --version").decode()
                version_text = installed_version.strip().replace("\n", f"\n{INDENT}")
                print(f"{INDENT}Installed version:\n{INDENT}{version_text}")
                
                if version in installed_version:
                    print(f"{INDENT}Matches required version ({version}), skipping update task.")
                    return
                else:
                    print(f"{INDENT}The installed version appears to be different to required ({version})")
                    func(self_of_decorated_method, *args, **kwargs)
            except:
                print(f"{INDENT}Error occured while checking version, tried to execute \'{program} --version\'")
                func(self_of_decorated_method, *args, **kwargs)
        return _wrapper
    return _version_check_decorator
