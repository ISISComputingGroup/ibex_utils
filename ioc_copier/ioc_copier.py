from shutil import copytree
from pathlib import Path
import os
import re
ioc = "DFKPS"  # The name of the ioc to run, folders to copy will be of the form, <ioc>-IOC-01App and ioc<ioc>-IOC-01
start_copy = 11  # The folder to copy (avoid IOC1 as other IOCs usually reference this rather than copying it directly)
initial_copy = 12  # The first copy
max_copy = 35  # The final copy

answer = ""
while answer != "y":
    answer = input("Have you copied ioc copier to EPICS/ioc/master/<ioc_to_copy>? y/n: ")
    if answer == "n":
        print("please make a copy of the file at that location, then run that file.")
        exit()
    else:
        if answer != "y":
            print("please answer y or n")
answer = ""
while answer != "y":
    answer = input("Have you set the ioc, start_copy, initial_copy, and max_copy variables in the file? y/n: ")
    if answer == "n":
        print("open the file and set those variable to match the ioc to copy")
        exit()
    else:
        if answer != "y":
            print("please answer y or n")

ioc_name = f"{ioc}-IOC"
for current_copy in range(initial_copy,max_copy+1):
    copytree(os.path.join(os.getcwd(), f"{ioc_name}-{start_copy}App"),
             os.path.join(os.getcwd(), f"{ioc_name}-{current_copy}App"))
    path = os.path.join(os.getcwd(), f"{ioc_name}-{current_copy}App")
    for root, subFolder, files in os.walk(path):
        for file in files:
            if "exe" not in file and "obj" not in file and "pdb" not in file:
                with open(os.path.join(root, file), "r") as fp:
                    print(os.path.join(root, file))
                    text = fp.readlines()

                for i in range(len(text)):
                    temp = re.sub(f"IOC_{start_copy}", f"IOC_{current_copy}",text[i])
                    text[i] = temp
                    temp = re.sub(f"IOC-{start_copy}", f"IOC-{current_copy}",text[i])
                    text[i] = temp
                with open(os.path.join(root, file), "w") as fp:
                    fp.seek(0)
                    fp.writelines(text)
                    fp.truncate()
            if f"IOC_{start_copy}" in file:
                os.rename(os.path.join(root, file), os.path.join(root, file.replace(f"IOC_{start_copy}",
                                                                                    f"IOC_{current_copy}")))
            if f"IOC-{start_copy}" in file:
                os.rename(os.path.join(root, file), os.path.join(root, file.replace(f"IOC-{start_copy}",
                                                                                    f"IOC-{current_copy}")))
        for folder in subFolder:
            if f"IOC_{start_copy}" in folder:
                os.rename(os.path.join(root, folder), os.path.join(root, folder.replace(f"IOC_{start_copy}",
                                                                                        f"IOC_{current_copy}")))
            if f"IOC-{start_copy}" in folder:
                os.rename(os.path.join(root, folder), os.path.join(root, folder.replace(f"IOC-{start_copy}",
                                                                                        f"IOC-{current_copy}")))

os.chdir(os.path.join(os.getcwd(), "iocBoot"))
for current_copy in range(initial_copy, max_copy+1):
    copytree(os.path.join(os.getcwd(), f"ioc{ioc_name}-{start_copy}"),
             os.path.join(os.getcwd(), f"ioc{ioc_name}-{current_copy}"))
    path = os.path.join(os.getcwd(), f"ioc{ioc_name}-{current_copy}")
    for root, subFolder, files in os.walk(path):
        for file in files:
            if "exe" not in file and "obj" not in file and "pdb" not in file:
                with open(os.path.join(root, file), "r") as fp:
                    print(os.path.join(root, file))
                    text = fp.readlines()

                for i in range(len(text)):
                    temp = re.sub(f"IOC_{start_copy}", f"IOC_{current_copy}",text[i])
                    text[i] = temp
                    temp = re.sub(f"IOC-{start_copy}", f"IOC-{current_copy}",text[i])
                    text[i] = temp
                    temp = re.sub(f"{ioc}_{start_copy}", f"{ioc}_{current_copy}", text[i])
                    text[i] = temp
                    temp = re.sub(f"RAMPFILELIST{start_copy}", f"RAMPFILELIST{current_copy}", text[i])
                    text[i] = temp
                with open(os.path.join(root, file), "w") as fp:
                    fp.seek(0)
                    fp.writelines(text)
                    fp.truncate()
            if f"IOC_{start_copy}" in file:
                os.rename(os.path.join(root, file), os.path.join(root, file.replace(f"IOC_{start_copy}",
                                                                                    f"IOC_{current_copy}")))
            if f"IOC-{start_copy}" in file:
                os.rename(os.path.join(root, file), os.path.join(root, file.replace(f"IOC-{start_copy}",
                                                                                    f"IOC-{current_copy}")))
        for folder in subFolder:
            if f"IOC_{start_copy}" in folder:
                os.rename(os.path.join(root, folder), os.path.join(root, folder.replace(f"IOC_{start_copy}",
                                                                                        f"IOC_{current_copy}")))
            if f"IOC-{start_copy}" in folder:
                os.rename(os.path.join(root, folder), os.path.join(root, folder.replace(f"IOC-{start_copy}",
                                                                                        f"IOC-{current_copy}")))
                
print(f"Please run a grep for {start_copy}. There may be some things missed by ths such as axes on a motor, "
      f"as this file cannot just replace all iterations of {start_copy} as doing so could break functionality.")
