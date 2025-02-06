:: activate conda
set CONDA_PATH=C:\tools\Anaconda3\Scripts\activate.bat
call %CONDA_PATH%

:: activate conda env
call conda activate plotter

:: run script
python gui.py

pause
