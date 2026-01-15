from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11
from setuptools import setup, Extension
import os
import sys
import glob
import shutil

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
    opencv_bin = None
    for vc in vc_versions:
        lib_path = os.path.join(opencv_dir, arch, vc, 'lib')
        bin_path = os.path.join(opencv_dir, arch, vc, 'bin')
        if os.path.exists(lib_path):
            opencv_lib = lib_path
            if os.path.exists(bin_path):
                opencv_bin = bin_path
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
if opencv_bin:
    print(f"OpenCV bin: {opencv_bin}")

# 检查是否包含OpenCV DLL（通过环境变量控制）
INCLUDE_OPENCV_DLLS = os.environ.get('INCLUDE_OPENCV_DLLS', '1').lower() in ('1', 'true', 'yes', 'on')
print(f"\n包含OpenCV DLL: {'是' if INCLUDE_OPENCV_DLLS else '否'}")

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

# 准备包数据（如果包含DLL）
packages = []
package_data = {}

if INCLUDE_OPENCV_DLLS and sys.platform == 'win32' and opencv_bin:
    print("\n准备包含OpenCV DLL...")
    
    # 创建包目录结构
    pkg_dir = os.path.join(project_root, 'templatematcher')
    os.makedirs(pkg_dir, exist_ok=True)
    
    # 复制OpenCV DLL
    dll_dest = os.path.join(pkg_dir, 'opencv_dlls')
    if os.path.exists(dll_dest):
        shutil.rmtree(dll_dest)
    os.makedirs(dll_dest, exist_ok=True)
    
    dll_files = []
    
    # 根据使用的库类型选择DLL模式
    if 'world' in opencv_libs:
        # 使用world库，查找world DLL（包括Debug和Release版本）
        world_lib_name = opencv_libs['world']
        # 从库名提取版本号（如 opencv_world4110 -> 4110）
        import re
        version_match = re.search(r'(\d+)', world_lib_name)
        if version_match:
            version = version_match.group(1)
            # 尝试多种可能的DLL文件名
            world_dll_patterns = [
                f'opencv_world{version}*.dll',  # Release版本
                f'opencv_world{version}d*.dll',  # Debug版本（带d后缀）
                'opencv_world*.dll',  # 通用模式
            ]
        else:
            world_dll_patterns = ['opencv_world*.dll']
        
        print(f"  查找world库DLL (库名: {world_lib_name})...")
        for pattern in world_dll_patterns:
            matches = glob.glob(os.path.join(opencv_bin, pattern))
            if matches:
                dll_files.extend(matches)
                print(f"  找到 {len(matches)} 个world DLL文件")
                break
        
        # 如果还是没找到，尝试所有opencv_world开头的文件
        if not dll_files:
            all_world = glob.glob(os.path.join(opencv_bin, 'opencv_world*.dll'))
            if all_world:
                dll_files.extend(all_world)
                print(f"  找到 {len(all_world)} 个world DLL文件（通用搜索）")
    else:
        # 使用单独的库，查找各个模块的DLL
        dll_patterns = ['opencv_core*.dll', 'opencv_imgproc*.dll', 
                       'opencv_highgui*.dll', 'opencv_imgcodecs*.dll']
        print("  查找单独库DLL...")
        for pattern in dll_patterns:
            matches = glob.glob(os.path.join(opencv_bin, pattern))
            if matches:
                dll_files.extend(matches)
                print(f"  找到: {pattern} -> {len(matches)} 个文件")
    
    if dll_files:
        # 去重（可能有多个模式匹配到同一个文件）
        dll_files = list(set(dll_files))
        for dll_file in dll_files:
            shutil.copy2(dll_file, dll_dest)
            print(f"  复制: {os.path.basename(dll_file)}")
        
        # 创建自动加载DLL的__init__.py
        init_content = '''"""
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
'''
        init_file = os.path.join(pkg_dir, '__init__.py')
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write(init_content)
        
        packages = ['templatematcher']
        package_data = {'templatematcher': ['opencv_dlls/*.dll']}
        print(f"✓ 已包含 {len(dll_files)} 个OpenCV DLL文件")
        print(f"✓ 已创建自动加载DLL的__init__.py")
    else:
        print("警告: 未找到OpenCV DLL文件，将不包含DLL")
        print(f"  搜索路径: {opencv_bin}")
        print(f"  使用的库: {opencv_libs}")
        # 列出bin目录中的所有文件，帮助调试
        if os.path.exists(opencv_bin):
            all_files = os.listdir(opencv_bin)
            dll_files_in_dir = [f for f in all_files if f.endswith('.dll')]
            if dll_files_in_dir:
                print(f"  bin目录中的DLL文件（前10个）:")
                for f in dll_files_in_dir[:10]:
                    print(f"    {f}")
        INCLUDE_OPENCV_DLLS = False

setup(
    name="templatematcher",
    version="1.0.0",
    author="Template Matcher",
    description="Fast Image Pattern Matching Library" + (" (with OpenCV DLLs)" if INCLUDE_OPENCV_DLLS else ""),
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.6",
    packages=packages,
    package_data=package_data,
    install_requires=[
        'numpy>=1.19.0',
    ],
)
