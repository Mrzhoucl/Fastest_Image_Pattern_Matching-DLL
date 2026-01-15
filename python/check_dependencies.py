"""
检查Python模块依赖的工具脚本
"""
import os
import sys
import platform

def check_opencv_dlls():
    """检查OpenCV DLL是否在PATH中"""
    print("=" * 60)
    print("检查OpenCV DLL依赖")
    print("=" * 60)
    
    # 可能的OpenCV bin路径
    possible_paths = [
        r'E:\opencv411\opencv\build\x64\vc16\bin',
        r'E:\opencv411\opencv\build\x64\vc17\bin',
        r'E:\opencv\build\x64\vc16\bin',
        r'C:\opencv\build\x64\vc16\bin',
    ]
    
    opencv_bin = None
    for path in possible_paths:
        if os.path.exists(path):
            dll_files = [f for f in os.listdir(path) if f.endswith('.dll') and 'opencv' in f.lower()]
            if dll_files:
                opencv_bin = path
                print(f"找到OpenCV bin目录: {path}")
                print(f"  包含 {len(dll_files)} 个DLL文件")
                break
    
    if not opencv_bin:
        print("警告: 未找到OpenCV bin目录")
        return None
    
    # 检查PATH
    path_env = os.environ.get('PATH', '')
    if opencv_bin.lower() not in path_env.lower():
        print(f"\n警告: OpenCV bin目录不在PATH中")
        print(f"请运行以下命令添加到PATH:")
        print(f'  set PATH=%PATH%;{opencv_bin}')
        print(f"\n或在Python代码中添加:")
        print(f'  import os')
        print(f'  os.add_dll_directory(r"{opencv_bin}")')
        return opencv_bin
    else:
        print(f"\nOpenCV bin目录已在PATH中")
        return opencv_bin

def check_python_module():
    """检查Python模块"""
    print("\n" + "=" * 60)
    print("检查Python模块")
    print("=" * 60)
    
    try:
        import templatematcher
        print("✓ templatematcher 模块导入成功")
        print(f"  模块路径: {templatematcher.__file__}")
        return True
    except ImportError as e:
        print(f"✗ templatematcher 模块导入失败: {e}")
        return False

if __name__ == "__main__":
    opencv_bin = check_opencv_dlls()
    module_ok = check_python_module()
    
    if not module_ok and opencv_bin:
        print("\n" + "=" * 60)
        print("解决方案")
        print("=" * 60)
        print("在导入模块前添加以下代码:")
        print(f"""
import os
os.add_dll_directory(r"{opencv_bin}")
import templatematcher as tm
""")
