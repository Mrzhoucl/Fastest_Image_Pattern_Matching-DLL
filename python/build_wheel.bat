@echo off
REM 构建wheel包的脚本

echo ========================================
echo 构建 templatematcher wheel 包
echo ========================================
echo.

REM 检查是否包含DLL
set INCLUDE_DLLS=0
if "%1"=="--with-dll" set INCLUDE_DLLS=1
if "%1"=="--deploy" set INCLUDE_DLLS=1

if %INCLUDE_DLLS%==1 (
    echo 模式: 部署模式（包含OpenCV DLL）
    set INCLUDE_OPENCV_DLLS=1
) else (
    echo 模式: 开发模式（不包含OpenCV DLL）
    echo 提示: 使用 --with-dll 或 --deploy 参数可包含DLL
    set INCLUDE_OPENCV_DLLS=0
)

echo.

REM 清理旧文件
echo 清理旧文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist templatematcher.egg-info rmdir /s /q templatematcher.egg-info
if exist templatematcher (
    if %INCLUDE_DLLS%==0 rmdir /s /q templatematcher
)

REM 构建wheel
echo.
echo 构建wheel包...
set INCLUDE_OPENCV_DLLS=%INCLUDE_OPENCV_DLLS%
python setup.py bdist_wheel

if errorlevel 1 (
    echo.
    echo 构建失败！
    pause
    exit /b 1
)

REM 显示结果
echo.
echo ========================================
echo 构建完成！
echo ========================================
echo.
echo 生成的wheel文件:
dir /b dist\*.whl
echo.

REM 检查wheel包大小
for %%f in (dist\*.whl) do (
    for %%s in ("%%f") do (
        set size=%%~zs
        set /a sizeMB=%%~zs/1048576
        echo 文件大小: !sizeMB! MB
    )
)

echo.
if %INCLUDE_DLLS%==1 (
    echo 此wheel包包含OpenCV DLL，可直接部署到目标设备
) else (
    echo 此wheel包不包含OpenCV DLL
    echo 目标设备需要单独部署OpenCV DLL
)
echo.
pause
