@echo off
echo Starting News Analyzer Agent backend...
cd backend
call venv\Scripts\activate.bat
python main.py
