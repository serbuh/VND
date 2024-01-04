from cx_Freeze import setup, Executable
import os

executables = [Executable('interface_creator.py',
                          base='Win32GUI',
                          icon='demolition.ico',
                         )]

zip_include_packages = ['PySimpleGUI']
include_files = ['examples']

options = {
    'build_exe': {
        'include_msvcr': True,
        'build_exe': os.path.join('..', 'build_windows'),
        'include_files': include_files,
        'zip_include_packages': zip_include_packages,
    }
}

setup(name='interface_creator',
      version='0.0.2',
      description="Nice app, isn't it?",
      executables=executables,
      options=options)