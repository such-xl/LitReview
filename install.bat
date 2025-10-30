@echo off
REM LitReview Windows 安装脚本

echo ========================================
echo    LitReview 安装脚本 (Windows)
echo ========================================
echo.

echo 请选择安装方式:
echo 1) 完整安装（包含Web界面，需要cmake和Visual Studio）
echo 2) 核心功能（命令行工具，推荐）
echo 3) 使用Conda安装（推荐，最稳定）
echo.
set /p choice="请输入选项 [1-3]: "

if "%choice%"=="1" goto full
if "%choice%"=="2" goto core
if "%choice%"=="3" goto conda
goto invalid

:full
echo.
echo 正在安装完整版本...
echo.
echo 注意: 需要安装以下工具:
echo   1. CMake: https://cmake.org/download/
echo   2. Visual Studio Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/
echo.
pause
python -m pip install --upgrade pip
pip install -r requirements-minimal.txt
goto done

:core
echo.
echo 正在安装核心功能...
python -m pip install --upgrade pip
pip install -r requirements-no-web.txt
echo.
echo 提示: 使用命令行工具，无需Web界面
echo   python scripts\import_papers.py data\pdfs\
echo   python scripts\search_papers.py search "深度学习"
echo   python scripts\generate_review.py "深度学习" -o review.md
goto done

:conda
echo.
echo 使用Conda安装...
echo.
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo 未检测到conda，请先安装Miniconda:
    echo   https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)
conda create -n litreview python=3.10 -y
echo.
echo 请运行以下命令激活环境并继续安装:
echo   conda activate litreview
echo   conda install -c conda-forge chromadb sentence-transformers streamlit -y
echo   pip install PyMuPDF ollama python-dotenv pydantic pydantic-settings tqdm
goto end

:invalid
echo 无效选项
pause
exit /b 1

:done
echo.
echo ========================================
echo    安装完成！
echo ========================================
echo.
echo 下一步:
echo 1. 初始化数据库: python scripts\init_database.py
echo 2. 启动应用: streamlit run web\app.py
echo    或使用: run.sh
echo.

:end
pause
