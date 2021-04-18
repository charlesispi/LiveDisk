from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': [], 'include_files': ['icons/']}

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('main.py', base=base, target_name = 'LiveDisk', icon="icons/icon.ico")
]

setup(name='LiveDisk',
      version = '1.0.0',
      description = 'A simple tool to monitor disk space live, without having to right click and refresh.',
      options = {'build_exe': build_options},
      executables = executables)
