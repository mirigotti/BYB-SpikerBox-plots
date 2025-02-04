:: create conda env
call conda create -n plotter python=3.12

:: activate conda env
call conda activate plotter

:: install libraries
pip install matplotlib
pip install PyQt6

pause
