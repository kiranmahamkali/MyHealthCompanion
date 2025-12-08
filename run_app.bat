@echo off
cd /d "%~dp0"

REM Try to activate venv if it exists
if exist .venv\Scripts\activate (
    call .venv\Scripts\activate
)

REM Run using the python module approach which is more reliable
python -m streamlit run app.py

pause
