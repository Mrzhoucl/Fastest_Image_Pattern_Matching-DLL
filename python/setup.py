from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11
from setuptools import setup, Extension
import os
import sys

# 获取OpenCV路径
opencv_dir = os.environ.get('OpenCV_DIR', '')
if not opencv_dir:
    # 尝试常见路径
    possible_paths = [
        r'E:\opencv411\opencv\build',
        r'E:\opencv\build',
        r'C:\opencv\build',
    ]
    for path in possible_paths:
        if os.path.exists(path):
            opencv_dir = path
            break

if not opencv_dir:
    raise RuntimeError("Cannot find OpenCV. Please set OpenCV_DIR environment variable.")

# 确定include和lib目录
if sys.platform == 'win32':
    # Windows
    opencv_include = os.path.join(opencv_dir, 'include')
    if not os.path.exists(opencv_include):
        opencv_include = os.path.join(opencv_dir, '..', 'include')
    
    # 检测VS版本和架构
    import platform
    arch = 'x64' if platform.machine().endswith('64') else 'x86'
    
    # 尝试不同的vc版本
    vc_versions = ['vc17', 'vc16', 'vc15', 'vc14']
    opencv_lib = None
    for vc in vc_versions:
        lib_path = os.path.join(opencv_dir, arch, vc, 'lib')
        if os.path.exists(lib_path):
            opencv_lib = lib_path
            break
    
    if not opencv_lib:
        opencv_lib = os.path.join(opencv_dir, 'lib')
        if not os.path.exists(opencv_lib):
            raise RuntimeError(f"Cannot find OpenCV lib directory in {opencv_dir}")
else:
    # Linux/Mac
    opencv_include = os.path.join(opencv_dir, 'include')
    opencv_lib = os.path.join(opencv_dir, 'lib')

print(f"OpenCV include: {opencv_include}")
print(f"OpenCV lib: {opencv_lib}")

# 自动查找OpenCV库文件
def find_opencv_libs(lib_dir):
    """查找OpenCV库文件的实际名称"""
    import glob
    libs = {}
    
    # 尝试查找各个库
    lib_names = {
        'core': ['opencv_core', 'opencv_core4110', 'opencv_core411', 'opencv_core4', 'opencv_core454', 'opencv_core455'],
        'imgproc': ['opencv_imgproc', 'opencv_imgproc4110', 'opencv_imgproc411', 'opencv_imgproc4', 'opencv_imgproc454', 'opencv_imgproc455'],
        'highgui': ['opencv_highgui', 'opencv_highgui4110', 'opencv_highgui411', 'opencv_highgui4', 'opencv_highgui454', 'opencv_highgui455'],
        'imgcodecs': ['opencv_imgcodecs', 'opencv_imgcodecs4110', 'opencv_imgcodecs411', 'opencv_imgcodecs4', 'opencv_imgcodecs454', 'opencv_imgcodecs455'],
    }
    
    for key, names in lib_names.items():
        for name in names:
            pattern = os.path.join(lib_dir, f"{name}*.lib")
            matches = glob.glob(pattern)
            if matches:
                # 提取不带扩展名的库名
                lib_name = os.path.splitext(os.path.basename(matches[0]))[0]
                libs[key] = lib_name
                print(f"Found {key} library: {lib_name}")
                break
    
    # 如果找不到单独的库，尝试world库
    if not libs:
        world_patterns = ['opencv_world*.lib', 'opencv_world4110*.lib', 'opencv_world411*.lib', 
                         'opencv_world4*.lib', 'opencv_world454*.lib', 'opencv_world455*.lib']
        for pattern in world_patterns:
            matches = glob.glob(os.path.join(lib_dir, pattern))
            if matches:
                lib_name = os.path.splitext(os.path.basename(matches[0]))[0]
                libs['world'] = lib_name
                print(f"Found world library: {lib_name}")
                break
    
    return libs

opencv_libs = find_opencv_libs(opencv_lib)

if not opencv_libs:
    raise RuntimeError(f"Cannot find OpenCV libraries in {opencv_lib}")

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(project_root)

# 构建库列表
if 'world' in opencv_libs:
    # 使用world库（单个库包含所有模块）
    libraries = [opencv_libs['world']]
    print("Using OpenCV world library")
else:
    # 使用单独的库
    libraries = []
    for key in ['core', 'imgproc', 'highgui', 'imgcodecs']:
        if key in opencv_libs:
            libraries.append(opencv_libs[key])
    print(f"Using OpenCV libraries: {libraries}")

ext_modules = [
    Pybind11Extension(
        "templatematcher",
        [
            "pybind11_wrapper.cpp",
            os.path.join(parent_dir, "src", "TemplateMatcher.cpp"),
            os.path.join(parent_dir, "src", "TemplateMatcherC.cpp"),
            os.path.join(parent_dir, "src", "simd_utils.cpp"),
        ],
        include_dirs=[
            os.path.join(parent_dir, "include"),
            opencv_include,
            pybind11.get_include(),
        ],
        library_dirs=[opencv_lib],
        libraries=libraries,
        language='c++',
        cxx_std=17,
    ),
]

setup(
    name="templatematcher",
    version="1.0.0",
    author="Template Matcher",
    description="Fast Image Pattern Matching Library",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.6",
)
