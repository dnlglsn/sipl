from distutils.core import setup
from os.path import join
import subprocess

# References:
# http://docs.python.org/2/distutils/setupscript.html
# http://stackoverflow.com/questions/14989858/get-the-current-git-hash-in-a-python-script
# http://git-scm.com/book/en/Git-Basics-Tagging

# Get the git version and store it as the module's verion
# To add another tag: git tag -a v<num> -m "Message"
describe = subprocess.check_output(["git", "describe"]).replace("\n", "")
vSplit = describe.split("-")
version = vSplit[0]
if len(vSplit) > 1:
    version += "." + vSplit[1]
if len(vSplit) > 2:
    version += "#" + vSplit[2]

# Write the version to the _version.py file in grad
versionString = "__version__ = \"%s\"\n" % version
open(join("sipl", "_version.py"), "wt").write(versionString)

# Read the description from the README file
description = open(join("..", "README")).read()

# Set up the package
setup(name="sipl",
      version=version,
      description=description,
      author="Daniel Gleason",
      author_email="dgleason@gmail.com",
      packages=["sipl",
                "sipl.hdfs",
                "sipl.image",
                "sipl.spark"])
