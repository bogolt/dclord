import sys
from cx_Freeze import setup, Executable

setup(
    name = "dcLord",
    version = "0.1",
    description = "Divide and Conquer game client",
    executables = [Executable("dcLord.py", base = "Win32GUI")])
