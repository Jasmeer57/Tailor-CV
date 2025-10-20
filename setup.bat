@echo off
REM CV Tailor Setup Script for Windows
echo.
echo 🚀 CV Tailor Setup Script
echo ==========================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Check if Ollama is installed
where ollama >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Ollama is not installed.
    echo Please install Ollama from: https://ollama.ai
    echo.
    pause
) else (
    echo ✅ Ollama found
    echo.

    REM Check if Ollama is running
    curl -s http://localhost:11434 >nul 2>&1
    if errorlevel 1 (
        echo ⚠️ Ollama is not running.
        echo Please start Ollama manually.
        echo.
    ) else (
        echo ✅ Ollama is running
    )
)

echo.
echo 📦 Setting up Python environment...

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo 📚 Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ✅ Setup complete!
echo.
echo 🎉 You can now run the application with:
echo    streamlit run app.py
echo.
pause
