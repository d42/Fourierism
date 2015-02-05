from distutils.core import setup
from esky.bdist_esky import Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(
    includes = ['ui', 'scipy.special._ufuncs_cxx',
        'matplotlib.backends.backend_qt4agg', 'atexit',
        'matplotlib.backends.backend_tkagg',
        'scipy.sparse.csgraph._validation', 'pyqtgraph', 'pyqtgraph.graphicsItems.BarGraphItem',
        'scipy.integrate.vode', 'scipy.integrate.lsoda'],
    excludes = ['tornado', 'IPython', 'PyQt5', 'PyQt4' 'webbrowser'],
    freezer_module="cx_freeze"
)

data_files = [('.', ['icons_rc.py'])]

import sys
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
    data_files=data_files,
)
