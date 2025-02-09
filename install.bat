:: activate conda
set CONDA_PATH=C:\tools\Anaconda3\Scripts\activate.bat
call %CONDA_PATH%

:: create conda env
call conda create -n plotter python=3.12

:: activate conda env
call conda activate plotter

:: install libraries
pip install matplotlib
pip install PyQt6

pause
