# Python 绑定使用说明

## 运行时依赖

生成的动态库需要以下运行时依赖：

### Windows
- **OpenCV DLL文件**：需要将OpenCV的bin目录添加到PATH，或复制以下DLL到可执行文件目录：
  - `opencv_core*.dll`
  - `opencv_imgproc*.dll`
  - `opencv_highgui*.dll`
  - `opencv_imgcodecs*.dll`
- **Visual C++ 运行时**：通常已安装，如果没有需要安装VC++ Redistributable

### Linux
- **OpenCV共享库**：需要安装OpenCV开发包
  ```bash
  sudo apt-get install libopencv-dev  # Ubuntu/Debian
  ```

## 安装Python绑定

### 方法1：使用setup.py（推荐）

```bash
cd python
pip install pybind11
python setup.py install
```

或者开发模式：
```bash
python setup.py develop
```

### 方法2：使用CMake构建（需要pybind11）

在CMakeLists.txt中添加Python绑定支持（见下文）

## 使用示例

```python
import numpy as np
import cv2
import templatematcher as tm

# 创建匹配器
matcher = tm.TemplateMatcher()

# 学习模板
matcher.learn_pattern_from_file("template.bmp")

# 配置参数
config = tm.MatchConfig()
config.max_pos = 10
config.score = 0.7
config.tolerance_angle = 30.0

# 执行匹配
result = matcher.match_from_file("source.bmp", config)

# 处理结果
if result.success:
    for match in result:
        print(f"Score: {match.score}, Angle: {match.angle}")
    
    # 可视化
    img = cv2.imread("source.bmp")
    vis_img = tm.draw_match_result(img, result.matches)
    cv2.imwrite("result.bmp", vis_img)
```

## API 参考

### TemplateMatcher 类

- `learn_pattern(template_img: numpy.ndarray)` - 从numpy数组学习模板
- `learn_pattern_from_file(filepath: str)` - 从文件学习模板
- `match(source_img: numpy.ndarray, config: MatchConfig)` - 匹配numpy数组
- `match_from_file(filepath: str, config: MatchConfig)` - 匹配文件
- `is_pattern_learned()` - 检查是否已学习模板

### MatchConfig 类

- `max_pos` - 最大匹配数量
- `score` - 最低匹配分数
- `tolerance_angle` - 角度容差
- `use_simd` - 使用SIMD优化
- `sub_pixel_estimation` - 次像素估计
- 等等...

### MatchResult 类

- `success` - 是否成功
- `matches` - 匹配结果列表
- `execution_time_ms` - 执行时间（毫秒）

### MatchResult 对象（单个匹配）

- `score` - 匹配分数
- `angle` - 匹配角度
- `pt_center` - 中心点 (Point2d)
- `pt_lt`, `pt_rt`, `pt_rb`, `pt_lb` - 四个角点

## 故障排除

### 找不到OpenCV DLL

**Windows**：
```bash
# 方法1：添加到PATH
set PATH=%PATH%;E:\opencv\build\x64\vc16\bin

# 方法2：复制DLL到Python脚本目录
copy E:\opencv\build\x64\vc16\bin\opencv_*.dll C:\Python\Scripts\
```

**Linux**：
```bash
# 确保库路径在LD_LIBRARY_PATH中
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

### 导入错误

如果遇到导入错误，检查：
1. Python版本兼容性（需要Python 3.6+）
2. 是否正确安装了pybind11：`pip install pybind11`
3. 编译时是否正确链接了OpenCV
