import os
os.chdir(r'C:\Users\ericv\Dropbox\Python scripts\GitHub\Wiertsema\exe_scripts')
	
os.environ['TCL_LIBRARY'] = "C:\\Users\\ericv\\Anaconda3\\envs\\drone_business\\tcl\\tcl8.6"
os.environ['TK_LIBRARY'] = "C:\\Users\\ericv\\Anaconda3\\envs\\drone_business\\tcl\\tk8.6"
		
from cx_Freeze import setup, Executable    
import sys  

build_exe_options = {"packages": ["tkinter", "numpy", "pandas", "geopandas", "shapely", "fiona"], "include_files": ["tk86t.dll", "tcl86t.dll", "libiomp5md.dll", "mkl_core.dll", "mkl_def.dll", "mkl_intel_thread.dll", "C:\Users\ericv\AppData\Local\conda\conda\envs\Business-B\Library\bin/geos_c.dll", "C:\Users\ericv\AppData\Local\conda\conda\envs\Business-B\Library\bin/geos.dll"]}                      

base = None      

setup(name="Inversion2QGIS",  
      version="1.0",  
      description="Tool for converting EM_Tomo output 2 files compatible with qgis",  
      options={"build_exe": build_exe_options},  
      executables=[Executable("Inversion2QGIS.py", base=base)]
      )