# This script should NOT BE EXECUTED DIRECTLY
# use "python setup.py build" instead (this is how you correctly invoke cx_freeze)

import os
import shutil
import zipfile
import time
import re
import cx_Freeze

if os.path.isdir("build"):
    shutil.rmtree("build")
	


# Apparently importing the actual script that is built is bad practice and may cause issues
ver = None
with open("nonsensicalnovelnations.py", "r") as f:
	for line in f:
		m = re.match('ver = "(.*)"', line)
		if m is not None:
			ver = m.groups()[0]
			print(f"Found version: {ver}")
			break
			
if ver is None:
	raise Exception("Failed to find version")

build_exe_options = {"include_msvcr":False, "excludes":["distutils", "test"]}

cx_Freeze.setup(name="NonsensicalNovelNations", version=ver,
				description="NonsensicalNovelNations: Randomly create Dominions 5 nations from vanilla creatures",
				options={"build_exe":build_exe_options},
				executables=[cx_Freeze.Executable("nonsensicalnovelnations.py"),
							 cx_Freeze.Executable("nonsensicalnovelnationsgui.pyw", base="Win32GUI"),
							 cx_Freeze.Executable("autocalcGUI.pyw", base="Win32GUI")
							 ])

# Permissions.
time.sleep(5)

buildfilename = os.listdir("build")[0]
os.rename(f"build/{buildfilename}", f"build/nonsensicalnovelnations-{ver}")

# cx_Freeze tries to include a bunch of dlls that Windows users may not have permissions to distribute
# but should be present on any recent system (and available through the MS VC redistributables if not)
# therefore clear them from the distribution

for root, dirs, files in os.walk(f"build/nonsensicalnovelnations-{ver}"):
	for file in files:
		if file.startswith("api-ms") or file in ["ucrtbase.dll", "vcruntime140.dll"]:
			print(f"Strip file {file} from output")
			os.unlink(os.path.join(f"build/nonsensicalnovelnations-{ver}", file))
		elif "api-ms" in file:
			print(file)

shutil.copy("LICENSE", f"build/nonsensicalnovelnations-{ver}/LICENSE")
shutil.copy("readme.md", f"build/nonsensicalnovelnations-{ver}/readme.md")
shutil.copy("changelog.txt", f"build/nonsensicalnovelnations-{ver}/changelog.txt")
shutil.copy("BaseU.csv", f"build/nonsensicalnovelnations-{ver}/BaseU.csv")
shutil.copy("armors.csv", f"build/nonsensicalnovelnations-{ver}/armors.csv")
shutil.copy("effects_weapons.csv", f"build/nonsensicalnovelnations-{ver}/effects_weapons.csv")
shutil.copy("protections_by_armor.csv", f"build/nonsensicalnovelnations-{ver}/protections_by_armor.csv")
shutil.copy("badunits.txt", f"build/nonsensicalnovelnations-{ver}/badunits.txt")
shutil.copy("long.txt", f"build/nonsensicalnovelnations-{ver}/long.txt")
shutil.copy("short.txt", f"build/nonsensicalnovelnations-{ver}/short.txt")
shutil.copy("suffix.txt", f"build/nonsensicalnovelnations-{ver}/suffix.txt")
os.mkdir(f"build/nonsensicalnovelnations-{ver}/output")

# change working dir so the /build folder doesn't end up in the zip
os.chdir("build")

zipf = zipfile.ZipFile(f"nonsensicalnovelnations-{ver}.zip", "w", zipfile.ZIP_DEFLATED)
for root, dirs, files in os.walk(f"nonsensicalnovelnations-{ver}"):
    for file in files:
        zipf.write(os.path.join(root, file))

zipf.close()