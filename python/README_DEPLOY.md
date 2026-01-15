# 打包和部署指南

## 构建wheel包

### 开发模式（不包含OpenCV DLL）

```bash
python setup.py bdist_wheel
```

或使用脚本：
```bash
build_wheel.bat
```

**特点**：
- 包体积小（通常几MB）
- 需要目标设备单独部署OpenCV DLL
- 适合开发环境

### 部署模式（包含OpenCV DLL）

```bash
set INCLUDE_OPENCV_DLLS=1
python setup.py bdist_wheel
```

或使用脚本：
```bash
build_wheel.bat --with-dll
# 或
build_wheel.bat --deploy
```

**特点**：
- 包体积较大（可能几十MB，取决于OpenCV版本）
- 包含所有必需的OpenCV DLL
- 目标设备无需额外配置
- 适合生产部署

## 检查wheel包内容

```bash
python check_wheel.py dist/templatematcher-*.whl
```

或自动检查：
```bash
python check_wheel.py
```

## 在其他电脑上安装

### 方案1：包含DLL的wheel（推荐）

**只需要wheel文件即可！**

```bash
pip install templatematcher-1.0.0-cp310-cp310-win_amd64.whl
```

安装后直接使用：
```python
import templatematcher as tm
# DLL会自动加载，无需额外配置
```

### 方案2：不包含DLL的wheel

**需要wheel文件 + OpenCV DLL**

1. 安装wheel：
   ```bash
   pip install templatematcher-1.0.0-cp310-cp310-win_amd64.whl
   ```

2. 部署OpenCV DLL（三选一）：

   **方法A：复制到Python DLLs目录**
   ```bash
   copy opencv_*.dll C:\Python\DLLs\
   ```

   **方法B：添加到PATH**
   ```bash
   set PATH=%PATH%;C:\path\to\opencv\bin
   ```

   **方法C：在代码中设置**
   ```python
   import os
   os.add_dll_directory(r'C:\path\to\opencv\bin')
   import templatematcher as tm
   ```

## 部署检查清单

### 包含DLL的wheel

- [x] wheel文件
- [x] 目标设备有Python 3.6+
- [x] 目标设备有pip
- [ ] ~~需要OpenCV DLL~~（已包含）

### 不包含DLL的wheel

- [x] wheel文件
- [x] OpenCV DLL文件（4个：core, imgproc, highgui, imgcodecs）
- [x] 目标设备有Python 3.6+
- [x] 目标设备有pip
- [x] DLL部署方案（PATH或代码中设置）

## 常见问题

### Q: wheel包在目标设备安装失败？

**A**: 检查：
1. Python版本是否匹配（wheel文件名中的cp310表示Python 3.10）
2. 架构是否匹配（win_amd64表示64位）
3. 如果包含DLL，检查磁盘空间是否足够

### Q: 导入时提示找不到DLL？

**A**: 
1. 如果使用包含DLL的wheel，检查`templatematcher/opencv_dlls/`目录是否存在
2. 如果使用不包含DLL的wheel，确保OpenCV DLL在PATH中或使用`os.add_dll_directory()`

### Q: 如何为不同Python版本构建？

**A**: 
```bash
# Python 3.8
py -3.8 setup.py bdist_wheel

# Python 3.9
py -3.9 setup.py bdist_wheel

# Python 3.10
py -3.10 setup.py bdist_wheel
```

## 推荐方案

- **开发/测试**：使用不包含DLL的wheel（体积小，快速迭代）
- **生产部署**：使用包含DLL的wheel（一键安装，无需配置）
