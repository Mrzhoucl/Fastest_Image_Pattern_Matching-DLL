# 运行时依赖说明

## 动态库运行时依赖

生成的 `TemplateMatcher.dll` (Windows) 或 `libTemplateMatcher.so` (Linux) 需要以下运行时依赖：

### Windows

#### 必需文件

1. **OpenCV DLL文件**
   - `opencv_core*.dll`
   - `opencv_imgproc*.dll`
   - `opencv_highgui*.dll`
   - `opencv_imgcodecs*.dll`
   
   位置通常在：`E:\opencv\build\x64\vc16\bin\` 或类似路径

2. **Visual C++ 运行时库**
   - 通常系统已安装
   - 如果没有，需要安装对应版本的 VC++ Redistributable

#### 部署方式

**方式1：添加到PATH（推荐用于开发）**
```batch
set PATH=%PATH%;E:\opencv\build\x64\vc16\bin
```

**方式2：复制DLL到程序目录（推荐用于发布）**
```batch
copy E:\opencv\build\x64\vc16\bin\opencv_*.dll C:\YourApp\
copy E:\opencv\build\x64\vc16\bin\TemplateMatcher.dll C:\YourApp\
```

**方式3：使用CMake安装规则**
```cmake
# 在CMakeLists.txt中添加
install(FILES ${OpenCV_DLL_FILES} DESTINATION bin)
```

### Linux

#### 必需文件

1. **OpenCV共享库**
   - `libopencv_core.so*`
   - `libopencv_imgproc.so*`
   - `libopencv_highgui.so*`
   - `libopencv_imgcodecs.so*`

#### 安装方式

```bash
# Ubuntu/Debian
sudo apt-get install libopencv-dev

# 或确保库路径在LD_LIBRARY_PATH中
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

## Python绑定运行时依赖

使用Python绑定时，除了上述依赖，还需要：

### Python包

```bash
pip install pybind11 numpy opencv-python
```

### 运行时库路径

**Windows**：
- Python需要能找到 `TemplateMatcher.pyd` 和 OpenCV DLL
- 建议将OpenCV bin目录添加到PATH，或复制DLL到Python安装目录

**Linux**：
- 确保OpenCV库在系统库路径中，或设置 `LD_LIBRARY_PATH`

## 检查依赖

### Windows

使用 `dumpbin` 或 `Dependencies.exe` 工具检查DLL依赖：

```batch
dumpbin /dependents TemplateMatcher.dll
```

### Linux

使用 `ldd` 检查共享库依赖：

```bash
ldd libTemplateMatcher.so
```

## 打包发布

### Windows

推荐使用以下工具打包所有依赖：
- **Inno Setup** - 创建安装程序
- **NSIS** - 创建安装程序
- **CMake CPack** - 自动打包

### Linux

使用 `ldd` 找出所有依赖，然后打包：
```bash
ldd libTemplateMatcher.so | grep "=>" | awk '{print $3}' | xargs -I {} cp {} ./libs/
```

## 常见问题

### Q: 程序运行时提示找不到DLL

**A**: 确保OpenCV DLL在以下位置之一：
1. 程序运行目录
2. 系统PATH环境变量中
3. Windows系统目录（不推荐）

### Q: Python导入模块失败

**A**: 检查：
1. 是否正确安装了pybind11：`pip install pybind11`
2. OpenCV DLL是否在PATH中
3. Python版本是否兼容（需要3.6+）

### Q: 如何减少依赖？

**A**: 
1. 静态链接OpenCV（需要重新编译OpenCV）
2. 使用OpenCV的world库（单个DLL）
3. 只链接必需的OpenCV模块
