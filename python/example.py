"""
Python示例：使用模板匹配库
"""
import os
import sys
import numpy as np
import cv2

# 添加OpenCV DLL路径（Windows需要）
if sys.platform == 'win32':
    # 尝试常见路径
    possible_paths = [
        r'E:\opencv411\opencv\build\x64\vc16\bin',
        r'E:\opencv411\opencv\build\x64\vc17\bin',
        r'E:\opencv\build\x64\vc16\bin',
        r'C:\opencv\build\x64\vc16\bin',
    ]
    for path in possible_paths:
        if os.path.exists(path):
            os.add_dll_directory(path)
            print(f"Added OpenCV DLL path: {path}")
            break
    else:
        print("Warning: OpenCV bin directory not found. Please add it to PATH or os.add_dll_directory()")

import templatematcher as tm

def main():
    # 创建匹配器
    matcher = tm.TemplateMatcher()
    
    # 方法1：从文件学习模板
    print("Learning pattern from file...")
    if not matcher.learn_pattern_from_file(r"E:\project-test\feed_back\back_260114\feed_new\UNLOADING_IMAGES\cam1_tpl_20260114_172732.png"):
        print("Failed to learn pattern")
        return
    
    # 配置匹配参数
    config = tm.MatchConfig()
    config.max_pos = 10
    config.score = 0.7
    config.tolerance_angle = 30.0
    config.use_simd = True
    config.sub_pixel_estimation = True
    
    # 方法1：从文件匹配
    print("Matching from file...")
    result = matcher.match_from_file(r"E:\project-test\feed_back\back_260114\feed_new\UNLOADING_IMAGES\unloading_cam1_20260114_173410_540384.png", config)
    
    # 方法2：使用numpy数组
    # template_img = cv2.imread("template.bmp", cv2.IMREAD_GRAYSCALE)
    # source_img = cv2.imread("source.bmp", cv2.IMREAD_GRAYSCALE)
    # matcher.learn_pattern(template_img)
    # result = matcher.match(source_img, config)
    
    if result.success:
        print(f"Found {len(result)} matches in {result.execution_time_ms:.2f} ms")
        
        for i, match in enumerate(result):
            print(f"Match {i}:")
            print(f"  Score: {match.score:.3f}")
            print(f"  Angle: {match.angle:.2f} degrees")
            print(f"  Center: ({match.pt_center.x:.2f}, {match.pt_center.y:.2f})")
        
        # 可视化
        source_img = cv2.imread(r"E:\project-test\feed_back\back_260114\feed_new\UNLOADING_IMAGES\unloading_cam1_20260114_173410_540384.png", cv2.IMREAD_COLOR)
        if source_img is not None:
            vis_img = tm.draw_match_result(
                source_img, 
                result.matches,
                color=[0, 255, 0],  # 绿色
                thickness=2,
                draw_labels=True
            )
            cv2.imwrite("result.bmp", vis_img)
            print("Result saved to result.bmp")
    else:
        print("No matches found")

if __name__ == "__main__":
    main()
