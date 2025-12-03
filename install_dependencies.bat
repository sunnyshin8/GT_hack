@echo off
REM Installation script for GT_hack FastAPI Chatbot (Windows)
REM Run this script to install dependencies in the correct order

echo 🚀 Installing GT_hack FastAPI Chatbot Dependencies...
echo ==================================================

REM Stage 1: Core FastAPI dependencies
echo 📦 Stage 1: Installing core FastAPI dependencies...
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0

REM Stage 2: Database and basic utilities
echo 📦 Stage 2: Installing database and utilities...
pip install sqlalchemy[asyncio]==2.0.23 alembic==1.12.1 aiosqlite==0.19.0
pip install pydantic[email]==2.5.1 pydantic-settings==2.1.0 python-multipart==0.0.6 python-dotenv==1.0.0

REM Stage 3: HTTP and logging
echo 📦 Stage 3: Installing HTTP client and logging...
pip install httpx==0.25.2 structlog==23.2.0 faker==19.6.2

REM Stage 4: Redis (optional)
echo 📦 Stage 4: Installing Redis (optional)...
pip install redis[hiredis]==5.0.1
if errorlevel 1 echo ⚠️ Redis installation failed - continuing without it

REM Stage 5: Google Gemini AI
echo 📦 Stage 5: Installing Google Gemini AI...
pip install google-generativeai==0.3.2
pip install langchain-core
pip install langchain-google-genai==0.0.6

REM Stage 6: Vector store
echo 📦 Stage 6: Installing vector store...
pip install faiss-cpu==1.7.4

echo.
echo ✅ Installation completed!
echo 🚀 You can now run: python run.py
echo.
echo Optional ML packages (install if needed):
echo   pip install numpy==1.24.3 scikit-learn==1.3.0 sentence-transformers==2.2.2

pause