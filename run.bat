CALL attrib main.py +h
CALL attrib src.py +h
CALL attrib pockie_ninja_automation.py +h
CALL attrib README.md +h
CALL attrib requirements.txt +h
CALL attrib run.bat +h

CALL python -m pip install --upgrade pip
CALL py -m venv venv
CALL venv\scripts\activate
CALL pip install -r requirements.txt
CALL SET PLAYWRIGHT_BROWSERS_PATH=0
CALL playwright install chromium
CALL pyinstaller -y -F main.py --add-data "venv/lib/site-packages/playwright/driver;playwright/driver" --add-data "venv/Lib/site-packages/sv_ttk;sv_ttk/" --add-data "venv/Lib/site-packages/sv_ttk/sv.tcl;."
CALL MOVE dist\main.exe main.exe
CALL REN main.exe PockieNinjaFarm-Beta1.exe

CALL attrib build +h
CALL attrib dist +h
CALL attrib venv +h
CALL attrib main.spec +h
