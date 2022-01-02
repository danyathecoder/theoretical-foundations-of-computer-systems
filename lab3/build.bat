@echo off
pyinstaller --exclude-module _bootlocale --paths .\env\Lib\site-packages -F -w main.py -n lab3