cmake_minimum_required(VERSION 3.11)

project(TemplateMatcher VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 设置输出目录
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# 允许用户指定OpenCV路径
if(DEFINED ENV{OpenCV_DIR})
    set(OpenCV_DIR $ENV{OpenCV_DIR} CACHE PATH "OpenCV directory")
elseif(NOT DEFINED OpenCV_DIR)
    # 尝试自动检测常见路径
    set(OpenCV_POSSIBLE_PATHS
        "E:/opencv411/opencv/build"
        "E:/opencv/build"
        "C:/opencv"
        "C:/opencv/build"
    )
    foreach(PATH ${OpenCV_POSSIBLE_PATHS})
        if(EXISTS "${PATH}/OpenCVConfig.cmake" OR EXISTS "${PATH}/build/OpenCVConfig.cmake")
            set(OpenCV_DIR "${PATH}" CACHE PATH "OpenCV directory")
            break()
        endif()
    endforeach()
endif()

# 尝试查找OpenCV
set(OpenCV_FOUND FALSE)

# 首先尝试CONFIG模式
if(OpenCV_DIR)
    find_package(OpenCV CONFIG QUIET PATHS ${OpenCV_DIR} NO_DEFAULT_PATH)
endif()

# 如果失败，尝试标准查找
if(NOT OpenCV_FOUND)
    find_package(OpenCV CONFIG QUIET)
endif()

# 如果仍然失败，尝试MODULE模式
if(NOT OpenCV_FOUND)
    find_package(OpenCV MODULE QUIET)
endif()

# 如果还是失败，手动设置路径
if(NOT OpenCV_FOUND)
    message(STATUS "OpenCV not found via find_package, trying manual setup...")
    
    # 确定OpenCV基础目录
    if(OpenCV_DIR)
        set(OpenCV_BASE_DIR "${OpenCV_DIR}")
    else()
        # 尝试从环境变量获取
        if(DEFINED ENV{OpenCV_DIR})
            set(OpenCV_BASE_DIR "$ENV{OpenCV_DIR}")
        else()
            # 默认路径
            set(OpenCV_BASE_DIR "E:/opencv")
        endif()
    endif()
    
    # 查找include目录
    if(EXISTS "${OpenCV_BASE_DIR}/build/include/opencv2/opencv.hpp")
        set(OpenCV_INCLUDE_DIRS "${OpenCV_BASE_DIR}/build/include")
    elseif(EXISTS "${OpenCV_BASE_DIR}/include/opencv2/opencv.hpp")
        set(OpenCV_INCLUDE_DIRS "${OpenCV_BASE_DIR}/include")
    elseif(EXISTS "${OpenCV_BASE_DIR}/opencv2/opencv.hpp")
        get_filename_component(OpenCV_INCLUDE_DIRS "${OpenCV_BASE_DIR}" DIRECTORY)
        set(OpenCV_INCLUDE_DIRS "${OpenCV_INCLUDE_DIRS}/include")
    else()
        message(FATAL_ERROR "Cannot find OpenCV include directory. Please set OpenCV_DIR or OpenCV_BASE_DIR")
    endif()
    
    # 查找库目录
    if(MSVC)
        # Visual Studio版本检测
        if(MSVC_VERSION GREATER_EQUAL 1930)  # VS 2022
            set(VC_VERSION "vc17")
        elseif(MSVC_VERSION GREATER_EQUAL 1920)  # VS 2019
            set(VC_VERSION "vc16")
        elseif(MSVC_VERSION GREATER_EQUAL 1910)  # VS 2017
            set(VC_VERSION "vc15")
        else()
            set(VC_VERSION "vc14")
        endif()
        
        if(CMAKE_SIZEOF_VOID_P EQUAL 8)
            set(ARCH "x64")
        else()
            set(ARCH "x86")
        endif()
        
        if(EXISTS "${OpenCV_BASE_DIR}/build/${ARCH}/${VC_VERSION}/lib")
            set(OpenCV_LIBS_DIR "${OpenCV_BASE_DIR}/build/${ARCH}/${VC_VERSION}/lib")
        elseif(EXISTS "${OpenCV_BASE_DIR}/build/${ARCH}/vc16/lib")
            set(OpenCV_LIBS_DIR "${OpenCV_BASE_DIR}/build/${ARCH}/vc16/lib")
        elseif(EXISTS "${OpenCV_BASE_DIR}/build/${ARCH}/vc15/lib")
            set(OpenCV_LIBS_DIR "${OpenCV_BASE_DIR}/build/${ARCH}/vc15/lib")
        elseif(EXISTS "${OpenCV_BASE_DIR}/build/${ARCH}/vc14/lib")
            set(OpenCV_LIBS_DIR "${OpenCV_BASE_DIR}/build/${ARCH}/vc14/lib")
        elseif(EXISTS "${OpenCV_BASE_DIR}/lib")
            set(OpenCV_LIBS_DIR "${OpenCV_BASE_DIR}/lib")
        else()
            message(FATAL_ERROR "Cannot find OpenCV library directory. Please set OpenCV_DIR")
        endif()
    else()
        # Linux/Mac
        if(EXISTS "${OpenCV_BASE_DIR}/lib")
            set(OpenCV_LIBS_DIR "${OpenCV_BASE_DIR}/lib")
        else()
            message(FATAL_ERROR "Cannot find OpenCV library directory. Please set OpenCV_DIR")
        endif()
    endif()
    
    # 查找库文件
    find_library(OpenCV_CORE_LIB 
        NAMES opencv_core opencv_core454 opencv_core455 opencv_core4
        PATHS ${OpenCV_LIBS_DIR}
        NO_DEFAULT_PATH
    )
    find_library(OpenCV_IMGPROC_LIB 
        NAMES opencv_imgproc opencv_imgproc454 opencv_imgproc455 opencv_imgproc4
        PATHS ${OpenCV_LIBS_DIR}
        NO_DEFAULT_PATH
    )
    find_library(OpenCV_HIGHGUI_LIB 
        NAMES opencv_highgui opencv_highgui454 opencv_highgui455 opencv_highgui4
        PATHS ${OpenCV_LIBS_DIR}
        NO_DEFAULT_PATH
    )
    find_library(OpenCV_IMGCODECS_LIB 
        NAMES opencv_imgcodecs opencv_imgcodecs454 opencv_imgcodecs455 opencv_imgcodecs4
        PATHS ${OpenCV_LIBS_DIR}
        NO_DEFAULT_PATH
    )
    
    if(OpenCV_CORE_LIB AND OpenCV_IMGPROC_LIB AND OpenCV_HIGHGUI_LIB)
        set(OpenCV_LIBS ${OpenCV_CORE_LIB} ${OpenCV_IMGPROC_LIB} ${OpenCV_HIGHGUI_LIB})
        if(OpenCV_IMGCODECS_LIB)
            list(APPEND OpenCV_LIBS ${OpenCV_IMGCODECS_LIB})
        endif()
        set(OpenCV_FOUND TRUE)
    else()
        # 尝试world库
        find_library(OpenCV_WORLD_LIB 
            NAMES opencv_world opencv_world454 opencv_world455 opencv_world4
            PATHS ${OpenCV_LIBS_DIR}
            NO_DEFAULT_PATH
        )
        if(OpenCV_WORLD_LIB)
            set(OpenCV_LIBS ${OpenCV_WORLD_LIB})
            set(OpenCV_FOUND TRUE)
        else()
            message(FATAL_ERROR "Cannot find OpenCV libraries. Please check OpenCV installation.")
        endif()
    endif()
    
    message(STATUS "OpenCV manually configured:")
    message(STATUS "  Include dirs: ${OpenCV_INCLUDE_DIRS}")
    message(STATUS "  Library dir: ${OpenCV_LIBS_DIR}")
    message(STATUS "  Libraries: ${OpenCV_LIBS}")
endif()

# 验证OpenCV是否可用
if(OpenCV_FOUND)
    if(TARGET opencv_core)
        message(STATUS "OpenCV found via targets")
        set(OpenCV_LIBS opencv_core opencv_imgproc opencv_highgui opencv_imgcodecs)
    elseif(OpenCV_INCLUDE_DIRS AND OpenCV_LIBS)
        message(STATUS "OpenCV found via manual configuration")
    else()
        message(FATAL_ERROR "OpenCV configuration incomplete")
    endif()
else()
    message(FATAL_ERROR "OpenCV not found. Please set OpenCV_DIR environment variable or CMake variable.")
endif()

# 包含目录
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
if(OpenCV_INCLUDE_DIRS)
    include_directories(${OpenCV_INCLUDE_DIRS})
endif()

# 源文件
set(SOURCES
    src/TemplateMatcher.cpp
    src/TemplateMatcherC.cpp
    src/simd_utils.cpp
)

set(HEADERS
    include/TemplateMatcher.h
    include/TemplateMatcherC.h
    include/simd_utils.h
)

# 创建共享库
add_library(TemplateMatcher SHARED ${SOURCES} ${HEADERS})

# 设置导出宏
target_compile_definitions(TemplateMatcher PRIVATE TEMPLATEMATCHER_EXPORTS)

# 链接 OpenCV
if(TARGET opencv_core)
    # 使用目标链接（如果可用）
    target_link_libraries(TemplateMatcher PRIVATE opencv_core opencv_imgproc opencv_highgui opencv_imgcodecs)
else()
    # 手动链接
    target_include_directories(TemplateMatcher PRIVATE ${OpenCV_INCLUDE_DIRS})
    target_link_directories(TemplateMatcher PRIVATE ${OpenCV_LIBS_DIR})
    target_link_libraries(TemplateMatcher PRIVATE ${OpenCV_LIBS})
endif()

# 设置编译选项
if(MSVC)
    target_compile_options(TemplateMatcher PRIVATE /W4)
    # 启用SSE2
    target_compile_options(TemplateMatcher PRIVATE /arch:SSE2)
else()
    target_compile_options(TemplateMatcher PRIVATE -Wall -Wextra)
    # 启用SSE2 (x86/x64)
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64|i[3-6]86")
        target_compile_options(TemplateMatcher PRIVATE -msse2)
    endif()
endif()

# 安装规则
install(TARGETS TemplateMatcher
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
)

install(FILES ${HEADERS}
    DESTINATION include/TemplateMatcher
)

# 创建示例程序（可选）
option(BUILD_EXAMPLES "Build example programs" OFF)

if(BUILD_EXAMPLES)
    add_executable(example_cpp examples/example_cpp.cpp)
    target_link_libraries(example_cpp PRIVATE TemplateMatcher)
    if(TARGET opencv_core)
        target_link_libraries(example_cpp PRIVATE opencv_core opencv_imgproc opencv_highgui opencv_imgcodecs)
    else()
        target_link_libraries(example_cpp PRIVATE ${OpenCV_LIBS})
    endif()
    
    add_executable(example_c examples/example_c.c)
    target_link_libraries(example_c PRIVATE TemplateMatcher)
    if(TARGET opencv_core)
        target_link_libraries(example_c PRIVATE opencv_core opencv_imgproc opencv_highgui opencv_imgcodecs)
    else()
        target_link_libraries(example_c PRIVATE ${OpenCV_LIBS})
    endif()
endif()

# Python绑定（可选，需要pybind11）
option(BUILD_PYTHON_BINDINGS "Build Python bindings" OFF)

if(BUILD_PYTHON_BINDINGS)
    find_package(pybind11 QUIET)
    if(pybind11_FOUND)
        message(STATUS "Building Python bindings with pybind11")
        
        pybind11_add_module(templatematcher
            python/pybind11_wrapper.cpp
        )
        
        target_link_libraries(templatematcher PRIVATE TemplateMatcher)
        if(TARGET opencv_core)
            target_link_libraries(templatematcher PRIVATE opencv_core opencv_imgproc opencv_highgui opencv_imgcodecs)
        else()
            target_link_libraries(templatematcher PRIVATE ${OpenCV_LIBS})
        endif()
        
        # 设置C++17标准
        set_target_properties(templatematcher PROPERTIES
            CXX_STANDARD 17
            CXX_STANDARD_REQUIRED ON
        )
        
        if(MSVC)
            target_compile_options(templatematcher PRIVATE /W3)
        endif()
    else()
        message(WARNING "pybind11 not found. Python bindings will not be built.")
        message(STATUS "Install pybind11: pip install pybind11")
        message(STATUS "Or use setup.py in python/ directory")
    endif()
endif()
