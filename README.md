# Fastest Image Pattern Matching DLL

这是从原始MFC应用程序中提取的模板匹配算法动态库版本。
[源代码链接](https://github.com/DennisLiu1993/Fastest_Image_Pattern_Matching)

## 特性

- ✅ 完全去除MFC依赖，纯C++实现
- ✅ 支持SIMD优化（x86/ARM）
- ✅ 提供C接口，易于集成
- ✅ 包含可视化绘制功能
- ✅ 支持多尺度金字塔匹配
- ✅ 支持旋转角度匹配
- ✅ 支持次像素估计
- ✅ 跨平台支持（Windows/Linux）
- ✅ python接口/wheel包/opencv依赖一键打包

## 编译

### 前置要求

- CMake 3.11+
- C++17 编译器
- OpenCV 4.x

### Windows (Visual Studio)

#### 方法1：自动检测（推荐）

```bash
build.bat Release
```

CMake会自动尝试在以下路径查找OpenCV：
- `E:/opencv411/opencv`
- `E:/opencv/build`
- `C:/opencv`

#### 方法2：指定OpenCV路径

如果自动检测失败，可以通过环境变量指定：

```bash
set OpenCV_DIR=E:\opencv\build
build.bat Release
```

或者在CMake配置时指定：

```bash
cmake .. -DCMAKE_BUILD_TYPE=Release -DOpenCV_DIR=E:\opencv\build
cmake --build . --config Release
```

### Linux

```bash
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j4
```

如果OpenCV不在标准路径，可以指定：

```bash
cmake .. -DCMAKE_BUILD_TYPE=Release -DOpenCV_DIR=/usr/local
```

## 使用示例

### C++ 接口

```cpp
#include "TemplateMatcher.h"
#include <opencv2/opencv.hpp>

using namespace TemplateMatching;

int main() {
    // 创建匹配器
    TemplateMatcher matcher;
    
    // 学习模板
    cv::Mat templateImg = cv::imread("template.bmp", cv::IMREAD_GRAYSCALE);
    matcher.LearnPattern(templateImg);
    
    // 配置匹配参数
    MatchConfig config;
    config.iMaxPos = 10;
    config.dScore = 0.7;
    config.dToleranceAngle = 30.0;
    config.bUseSIMD = true;
    
    // 执行匹配
    cv::Mat sourceImg = cv::imread("source.bmp", cv::IMREAD_GRAYSCALE);
    MatchResult result = matcher.Match(sourceImg, config);
    
    // 处理结果
    if (result.success) {
        for (const auto& match : result.matches) {
            std::cout << "Score: " << match.dMatchScore 
                      << ", Angle: " << match.dMatchedAngle 
                      << ", Center: (" << match.ptCenter.x 
                      << ", " << match.ptCenter.y << ")" << std::endl;
        }
        
        // 可视化
        cv::Mat visImg = sourceImg.clone();
        cv::cvtColor(visImg, visImg, cv::COLOR_GRAY2BGR);
        Visualization::DrawMatchResult(visImg, result.matches);
        cv::imwrite("result.bmp", visImg);
    }
    
    return 0;
}
```

### C 接口

```c
#include "TemplateMatcherC.h"
#include <stdio.h>

int main() {
    // 创建匹配器
    TM_MatcherHandle matcher = TM_CreateMatcher();
    
    // 学习模板
    TM_LearnPatternFromFile(matcher, "template.bmp");
    
    // 配置匹配参数
    TM_MatchConfig config;
    TM_GetDefaultConfig(&config);
    config.maxPos = 10;
    config.score = 0.7;
    config.toleranceAngle = 30.0;
    
    // 执行匹配
    TM_MatchResult results[100];
    double execTime;
    int count = TM_MatchFromFile(matcher, "source.bmp", &config, 
                                 results, 100, &execTime);
    
    // 处理结果
    printf("Found %d matches in %.2f ms\n", count, execTime);
    for (int i = 0; i < count; i++) {
        printf("Match %d: Score=%.3f, Angle=%.2f, Center=(%.2f, %.2f)\n",
               i, results[i].score, results[i].angle,
               results[i].centerX, results[i].centerY);
    }
    
    // 可视化
    TM_DrawMatchesToFile("source.bmp", "result.bmp", results, count);
    
    // 清理
    TM_DestroyMatcher(matcher);
    return 0;
}
```

## API 文档

### C++ 接口

#### TemplateMatcher 类

- `bool LearnPattern(const cv::Mat& templateImage)` - 学习模板图像
- `MatchResult Match(const cv::Mat& sourceImage, const MatchConfig& config)` - 执行匹配

#### MatchConfig 结构

- `int iMaxPos` - 最大匹配数量（默认70）
- `double dMaxOverlap` - 最大重叠比例（默认0.0）
- `double dScore` - 最低匹配分数（默认0.5）
- `double dToleranceAngle` - 角度容差（默认0.0）
- `int iMinReduceArea` - 最小缩减区域（默认256）
- `bool bUseSIMD` - 使用SIMD优化（默认true）
- `bool bSubPixelEstimation` - 次像素估计（默认false）
- `bool bBitwiseNot` - 图像取反（默认false）
- `bool bStopLayer1` - 快速模式（默认false）

### C 接口

主要函数：
- `TM_CreateMatcher()` - 创建匹配器
- `TM_DestroyMatcher()` - 销毁匹配器
- `TM_LearnPatternFromFile()` - 从文件学习模板
- `TM_LearnPatternFromData()` - 从内存数据学习模板
- `TM_MatchFromFile()` - 从文件执行匹配
- `TM_MatchFromData()` - 从内存数据执行匹配
- `TM_DrawMatchesToFile()` - 绘制匹配结果到文件
- `TM_DrawMatchesToData()` - 绘制匹配结果到内存
- `TM_GetDefaultConfig()` - 获取默认配置

## 故障排除

### OpenCV 找不到

如果CMake报错找不到OpenCV，可以：

1. 设置环境变量：
   ```bash
   set OpenCV_DIR=E:\opencv\build
   ```

2. 或者在CMake配置时指定：
   ```bash
   cmake .. -DOpenCV_DIR=E:\opencv\build
   ```

3. 确保OpenCV已正确安装，包含以下文件：
   - `include/opencv2/opencv.hpp`
   - `lib/opencv_core*.lib` 或 `lib/libopencv_core*.a`

### OpenCVModules.cmake 缺失

如果遇到 `OpenCVModules.cmake` 缺失错误，CMake会自动回退到手动配置模式，使用库文件直接链接。

## 性能优化

- 使用SIMD指令集加速（SSE2/NEON）
- 多尺度金字塔匹配
- 块最大值优化（大图像）
- 可选的快速模式（牺牲精度提升速度）

## 许可证

与原项目相同
