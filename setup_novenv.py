import os
from cx_Freeze import setup, Executable
import sys
import distutils
import opcode
import os
from pyproj import datadir

#RUN THIS: python setup.py bdist_msi


os.environ['TCL_LIBRARY'] = r'C:\Users\VanBoven\AppData\Local\Programs\Python\Python36\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\VanBoven\AppData\Local\Programs\Python\Python36\tcl\tk8.6'

#distutils_path = os.path.join(os.path.dirname(opcode.__file__), 'distutils')

build_exe_options = {"packages":['pandas','shapely','rasterio','fiona','geopandas','numpy','os','utm','tabulate','geopandas','pyproj'],
                     "include_files":['tcl86t.dll', 'tk86t.dll','logo.gif'],
                     "includes": ["tkinter"],
                     }

base = None
if sys.platform == 'win32':
    base = "Win32GUI"
if sys.platform == 'win64':
    base = "Win64GUI"

#executables = [
#    Executable('Inversion2QGIS.py.py', base=base, icon = 'logo.ico')
#] Also add logo.ico to include_files

executables = [
    Executable('Inversion2QGIS.py', base=base)
]

    
setup(name='Inversion2QGIS',
      version = '4.0',
      description = 'Tool for converting EM_Tomo output 2 files compatible with qgis',
      author = "Verhoeff, Vermeer, 2019",
      options = {"build_exe": build_exe_options},
      executables = executables)
