# Python绑定快速开始

## 安装

### 方法1：使用setup.py（最简单）

```bash
cd python
pip install pybind11 numpy opencv-python
python setup.py install
```

### 方法2：使用CMake（需要先编译DLL）

```bash
# 在项目根目录
cmake -DBUILD_PYTHON_BINDINGS=ON ..
cmake --build . --config Release
```

## 使用

```python
import templatematcher as tm
import cv2

# 创建匹配器
matcher = tm.TemplateMatcher()

# 学习模板
matcher.learn_pattern_from_file("template.bmp")

# 配置参数
config = tm.MatchConfig()
config.max_pos = 10
config.score = 0.7

# 执行匹配
result = matcher.match_from_file("source.bmp", config)

# 查看结果
if result.success:
    print(f"找到 {len(result)} 个匹配")
    for match in result:
        print(f"分数: {match.score:.3f}, 角度: {match.angle:.2f}")
```

## 运行时依赖

确保OpenCV DLL在PATH中：

**Windows**:
```batch
set PATH=%PATH%;E:\opencv\build\x64\vc16\bin
```

**Linux**:
```bash
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```
