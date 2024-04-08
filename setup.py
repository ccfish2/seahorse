import sys
import site
import os

from distutils.sysconfig import get_python_lib

from setuptools import setup

overlay_warning = False
if "install" in sys.argv:
    lib_paths = [get_python_lib()]
    if lib_paths[0].startswith("/usr/lib/"):
       lib_paths.append(get_python_lib(prefix="/usr/local"))
    for lib_path in lib_paths:
        existing_path = os.path.abspath(os.path.join(lib_path,"seahorse"))
        if os.path.exists(existing_path):
            overlay_warning = True
            break

setup()

if overlay_warning:
    os.stderr.write(
    """install on top of existing installation 
    %(existing_path)s
    """ %{"existing_path":existing_path}
    )%                                                   
