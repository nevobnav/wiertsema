from setuptools import find_packages
import os
from distutils.core import setup
from distutils import dist, sysconfig
os.chdir(r'E:\200 Projects\201 Wiertsema\Scripts\Wiertsema')

os.environ['TCL_LIBRARY'] = "E:\\200 Projects\\201 Wiertsema\\Inversion2QGIS\\inversion2qgis\\tcl\\tcl8.6"
os.environ['TK_LIBRARY'] = "E:\\200 Projects\\201 Wiertsema\\Inversion2QGIS\\inversion2qgis\\tcl\\tk8.6"

from cx_Freeze import setup, Executable
import sys

build_exe_options = {"packages": ["tkinter", "sysconfig", "distutils", "cx_Freeze", "numpy", "pandas", "geopandas", "shapely", "fiona"], "includes":find_packages(r"C:\Users\VanBoven\AppData\Local\Programs\Python\Python36\Lib\distutils/dist")+find_packages(r"E:\200 Projects\201 Wiertsema\Inversion2QGIS\inversion2QGIS_py368\Lib\site-packages\tests")+find_packages(r"E:\200 Projects\201 Wiertsema\Inversion2QGIS\inversion2QGIS_py368\Lib\site-packages\cx_freeze"), "zip_include_packages": "*", "zip_exclude_packages": "","include_files": ["tk86t.dll", "sqlite3.dll","tcl86t.dll", "libiomp5md.dll", "mkl_core.dll", "mkl_def.dll", "mkl_intel_thread.dll", r"E:\200 Projects\201 Wiertsema\Inversion2QGIS\inversion2qgis\Lib\site-packages\shapely\DLLs/geos_c.dll"]}

base = None

setup(name="Inversion2QGIS",
      version="1.0",
      description="Tool for converting EM_Tomo output 2 files compatible with qgis",
      options={"build_exe": build_exe_options},
      executables=[Executable("Inversion2QGIS.py", base=base)]
      )
