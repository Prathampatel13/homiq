@echo off
setlocal
set "ROOT=c:/Users/prath/OneDrive/Desktop/HomiQ/homiq/backend"
cd /d "%ROOT%"
C:\Python314\python.exe -c "import sys; sys.path.insert(0, r'%ROOT%'); import app.main; print('import ok')"
