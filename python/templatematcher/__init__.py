"""
TemplateMatcher - 自动加载OpenCV DLL
"""
import os
import sys

# 自动添加OpenCV DLL路径
if sys.platform == 'win32':
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    dll_dir = os.path.join(pkg_dir, 'opencv_dlls')
    if os.path.exists(dll_dir):
        try:
            # Python 3.8+
            os.add_dll_directory(dll_dir)
        except AttributeError:
            # Python < 3.8，需要手动添加到PATH
            path_env = os.environ.get('PATH', '')
            if dll_dir not in path_env:
                os.environ['PATH'] = dll_dir + os.pathsep + path_env

# 导入模块
from .templatematcher import *
__version__ = "1.0.0"
