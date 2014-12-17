from distutils.core import setup
from esky.bdist_esky import Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(
    freezer_module="cx_freeze"
)

#data_files = [('loc', ['loc/pol.qm'])]

import sys
base = 'Win32GUI' if sys.platform == 'win32' else None
suff = ".exe" if sys.platform == 'win32' else ""

executables = [
    Executable('main.py', name="Fourierism"+suff, gui_only=True)
]
try:
    with open('buildfile.txt', 'r+') as file:
        version = int(file.read())
        file.seek(0)
        file.write(str(version+1))
except OSError:
    version = 0

setup(
    name='Fourierism',
    version='0.1-%d' % version,
    description='',
    options=dict(bdist_esky=buildOptions),
    scripts=executables,
    #data_files=data_files,
)
