@echo off
chcp 65001 >nul
title django-admin backend :8000
cd /d %~dp0
echo Starting Django backend at http://127.0.0.1:8000 ...
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
pause
