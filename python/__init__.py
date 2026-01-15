"""
TemplateMatcher Python绑定
"""
import os
import sys

# Windows下自动添加OpenCV DLL路径
if sys.platform == 'win32':
    # 尝试从环境变量获取
    opencv_bin = os.environ.get('OpenCV_BIN', '')
    
    if not opencv_bin:
        # 尝试常见路径
        possible_paths = [
            r'E:\opencv411\opencv\build\x64\vc16\bin',
            r'E:\opencv411\opencv\build\x64\vc17\bin',
            r'E:\opencv\build\x64\vc16\bin',
            r'C:\opencv\build\x64\vc16\bin',
        ]
        for path in possible_paths:
            if os.path.exists(path):
                opencv_bin = path
                break
    
    if opencv_bin and os.path.exists(opencv_bin):
        try:
            os.add_dll_directory(opencv_bin)
        except AttributeError:
            # Python < 3.8 不支持 add_dll_directory
            # 需要手动添加到PATH
            path_env = os.environ.get('PATH', '')
            if opencv_bin not in path_env:
                os.environ['PATH'] = opencv_bin + os.pathsep + path_env

# 导入模块
try:
    from .templatematcher import *
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import templatematcher
    from templatematcher import *

__version__ = "1.0.0"
