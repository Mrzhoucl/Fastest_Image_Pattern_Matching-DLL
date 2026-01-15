"""
检查wheel包内容的工具
"""
import zipfile
import os
import sys

def check_wheel(wheel_file):
    """检查wheel包内容"""
    if not os.path.exists(wheel_file):
        print(f"错误: 文件不存在: {wheel_file}")
        return
    
    print("=" * 60)
    print(f"检查wheel包: {wheel_file}")
    print("=" * 60)
    
    file_size = os.path.getsize(wheel_file) / (1024 * 1024)  # MB
    print(f"\n文件大小: {file_size:.2f} MB")
    
    with zipfile.ZipFile(wheel_file, 'r') as z:
        files = z.namelist()
        
        print(f"\n总文件数: {len(files)}")
        
        # 检查DLL文件
        dll_files = [f for f in files if f.endswith('.dll')]
        if dll_files:
            print(f"\n✓ 包含 {len(dll_files)} 个DLL文件:")
            for dll in sorted(dll_files):
                info = z.getinfo(dll)
                size_kb = info.file_size / 1024
                print(f"  {dll} ({size_kb:.1f} KB)")
        else:
            print("\n✗ 不包含DLL文件")
            print("  目标设备需要单独部署OpenCV DLL")
        
        # 检查.pyd文件
        pyd_files = [f for f in files if f.endswith('.pyd') or f.endswith('.so')]
        if pyd_files:
            print(f"\n✓ 包含 {len(pyd_files)} 个Python扩展模块:")
            for pyd in pyd_files:
                print(f"  {pyd}")
        
        # 检查__init__.py
        init_files = [f for f in files if '__init__.py' in f]
        if init_files:
            print(f"\n✓ 包含包初始化文件:")
            for init in init_files:
                print(f"  {init}")
        
        # 检查其他重要文件
        other_files = [f for f in files if f.endswith('.txt') or f.endswith('.md')]
        if other_files:
            print(f"\n其他文件:")
            for f in other_files:
                print(f"  {f}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        wheel_file = sys.argv[1]
    else:
        # 自动查找dist目录中的wheel文件
        dist_dir = 'dist'
        if os.path.exists(dist_dir):
            wheel_files = [f for f in os.listdir(dist_dir) if f.endswith('.whl')]
            if wheel_files:
                wheel_file = os.path.join(dist_dir, wheel_files[0])
                print(f"自动找到: {wheel_file}\n")
            else:
                print("错误: dist目录中没有找到wheel文件")
                sys.exit(1)
        else:
            print("用法: python check_wheel.py <wheel_file>")
            sys.exit(1)
    
    check_wheel(wheel_file)
