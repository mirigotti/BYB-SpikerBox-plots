import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow,
                            QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, 
                            QFileDialog, QLineEdit, 
                            QLabel, QSpinBox, 
                            QDialog, QMessageBox,
                            QStackedLayout
                            )  

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from analysis import SpikeAnalysis # import the SpikeAnalysis class from analysis.py
import os
from PyQt6.QtGui import QPixmap, QFont

class RasterCanvas(FigureCanvas):

    def __init__(self, parent=None, width=6, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, constrained_layout=True)
        self.ax = fig.add_subplot(111)#, position=[0.1, 0.15, 0.85, 0.8])
        self.ax.axis('off')
        super().__init__(fig)

    def update_plot(self, analysis):

        trial_data, trials_matrix = analysis.get_trial_data()

        self.ax.clear()

        self.ax.imshow(1-trials_matrix, 
                       aspect='auto', 
                       cmap='gray', 
                       interpolation='none',
                    #    vmax=1, vmin=0,
                       extent=[analysis.pre_event_duration, analysis.post_event_duration, 0, len(trial_data)])

        # for tr, trial in enumerate(trial_data):
        #     event, spike_times = trial
        #     self.ax.plot(spike_times, tr + np.ones_like(spike_times), 'o', markersize=2)
        
        self.ax.axvline(0, color='k', linestyle='--', linewidth=1)

        self.ax.set_xlim([analysis.pre_event_duration, analysis.post_event_duration])

        self.ax.set_xlabel('Time (ms)')
        self.ax.set_ylabel('Trial #')
        self.ax.set_title('Raster plot')

        self.draw()

class PSTHCanvas(FigureCanvas):

    def __init__(self, parent=None, width=6, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, constrained_layout=True)
        self.ax = fig.add_subplot(111)#, position=[0.1, 0.15, 0.85, 0.8])
        self.ax.axis('off')
        super().__init__(fig)

    def update_plot(self, analysis):

        t_binned, psth_data = analysis.get_psth_data()

        self.ax.clear()

        self.ax.plot(t_binned, psth_data, linewidth=2)
        self.ax.axvline(0, color='k', linestyle='--', linewidth=1)

        self.ax.set_xlim([t_binned[0], t_binned[-1]])
        self.ax.set_ylim(bottom=0)

        self.ax.set_xlabel('Time (ms)')
        self.ax.set_ylabel('Firing rate (Hz)')
        self.ax.set_title('PSTH plot')
        
        self.draw()


# class InteractiveCanvas(MplCanvas):

#     def __init__(self, parent=None, width=5, height=4, dpi=100):
#         super().__init__(parent, width, height, dpi)
#         self.points, = self.axes.plot([0.5, 0.75], [0.5, 0.75], 'ro', picker=5)
#         self.selected_point = None
#         self.cid = self.mpl_connect('pick_event', self.on_pick)
#         self.cid_motion = self.mpl_connect('motion_notify_event', self.on_motion)
#         self.cid_release = self.mpl_connect('button_release_event', self.on_release)

#     def on_pick(self, event):
#         if event.artist != self.points:
#             return
#         self.selected_point = event.ind[0]

#     def on_motion(self, event):
#         if self.selected_point is None:
#             return
#         x, y = event.xdata, event.ydata
#         if x is None or y is None:
#             return
#         self.points.set_data(np.insert(self.points.get_xdata(), self.selected_point, x), 
#                              np.insert(self.points.get_ydata(), self.selected_point, y))
#         self.draw()

#     def on_release(self, event):
#         self.selected_point = None

# class InteractivePlotDialog(QDialog):

#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Interactive Plot")
#         self.canvas = InteractiveCanvas(self, width=5, height=4, dpi=100)
#         layout = QVBoxLayout()
#         layout.addWidget(self.canvas)
#         self.setLayout(layout)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("BYB SpikerBox Plotter")
        self.setFixedSize(1200, 720)

        # # Load wav button and text field
        # self.wav_button = QPushButton('Load .wav file (ephys recording from BYB SpikerBox)')
        # self.wav_button.clicked.connect(self.load_wav_file)
        # self.wav_button.setFont(QFont("Arial",20))
        # self.wav_file_label = QLineEdit()
        # self.wav_file_label.setReadOnly(True)
        # self.wav_file_label.setFont(QFont("Arial",16))

        # Load events button and text field
        self.txt_button = QPushButton('Load .txt file (output from BYB SpikeSorter)')
        self.txt_button.clicked.connect(self.load_txt_file)
        self.txt_button.setFont(QFont("Arial",20))
        self.txt_file_label = QLineEdit()
        self.txt_file_label.setReadOnly(True)
        self.txt_file_label.setFont(QFont("Arial",16))

        # Time input fields
        self.window_start_label = QLabel('Window start (ms):')
        self.window_start_label.setFont(QFont("Arial",20))
        self.window_start_input = QLineEdit()
        self.window_start_input.setFont(QFont("Arial",16))
        self.window_end_label = QLabel('Window end (ms):')
        self.window_end_label.setFont(QFont("Arial",20))
        self.window_end_input = QLineEdit()
        self.window_end_input.setFont(QFont("Arial",16))
        self.bin_size_label = QLabel('Bin size (ms):')
        self.bin_size_label.setFont(QFont("Arial",20))
        self.bin_size_input = QSpinBox(minimum=1, maximum=1000)
        self.bin_size_input.setFont(QFont("Arial",16))
        input_layout = QVBoxLayout()
        input_layout.addWidget(self.window_start_label)
        input_layout.addWidget(self.window_start_input)
        input_layout.addWidget(self.window_end_label)
        input_layout.addWidget(self.window_end_input)
        input_layout.addWidget(self.bin_size_label)
        input_layout.addWidget(self.bin_size_input)
        # Set default values
        self.window_start_input.setText('-500')
        self.window_end_input.setText('2500')
        self.bin_size_input.setValue(50)

        self.generate_button = QPushButton('Generate plots')
        self.generate_button.setStyleSheet("background-color: green")
        self.generate_button.clicked.connect(self.generate_plots)
        self.generate_button.setFont(QFont("Arial",20))

        self.export_label = QLabel('Export plots:')
        self.export_label.setFont(QFont("Arial",20))
        self.export_input = QLineEdit()
        self.export_input.setFont(QFont("Arial",16))
        self.export_input.setText('output')
        self.export_button = QPushButton('Export')
        self.export_button.clicked.connect(self.export_plots)
        self.export_button.setFont(QFont("Arial",20))

        # Right side plots
        self.canvas1 = RasterCanvas(self)
        self.canvas2 = PSTHCanvas(self)

        # Layouts
        left_layout = QVBoxLayout()

        # left_layout.addWidget(self.wav_button)
        # left_layout.addWidget(self.wav_file_label)
        # left_layout.addStretch(1)

        left_layout.addWidget(self.txt_button)
        left_layout.addWidget(self.txt_file_label)
        left_layout.addStretch(1)

        left_layout.addLayout(input_layout)
        left_layout.addWidget(self.generate_button)
        left_layout.addStretch(1)

        left_layout.addWidget(self.export_label)
        left_layout.addWidget(self.export_input)
        left_layout.addWidget(self.export_button)

        plot_layout = QVBoxLayout()
        plot_layout.addWidget(self.canvas1)
        plot_layout.addWidget(self.canvas2)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(plot_layout)

        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        self.setCentralWidget(central_widget)

        self.analysis = SpikeAnalysis()

    def load_wav_file(self):
        self.show_info_popup("Not implemented yet :(\nPlease process your .wav file with the BYB SpikeSorter software to generate a .txt file with spike events, and load that instead.")
        
        # file_name, _ = QFileDialog.getOpenFileName(self, "Open .wav File", "", "WAV Files (*.wav);;All Files (*)")
        # # check if file is a wav file
        # # if file_name and not file_name.endswith('.wav'):
        # if file_name:
        #     self.wav_file_label.setText(file_name)

    def load_txt_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open .txt File", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            self.txt_file_label.setText(file_name)
        
        if os.path.exists(file_name):
            self.analysis.load_events(file_name)

        # else:
        #     self.show_info_popup('No file selected')

    def generate_plots(self):
        # check if self.window_start.text() is an integer
        text = self.window_start_input.text()
        if text[0] == '-':
            text = text[1:]
        if not text.isnumeric():
            self.show_error_popup('Window start must be an integer')
            return

        # # check if self.window_end.text() is a number
        text = self.window_end_input.text()
        if text[0] == '-':
            text = text[1:]
        if not text.isnumeric():
            self.show_error_popup('Window end must be an integer')
            return
        
        # check if self.integer_input.value() is an integer
        if self.bin_size_input.value() <= 0:
            self.show_error_popup('Bin size must be a positive integer')
            return
        
        # check difference bewteen window start and window end is more than binsize
        binsize = self.bin_size_input.value()
        if int(self.window_end_input.text()) - int(self.window_start_input.text()) <= binsize:
            self.show_error_popup('Window end must be greater than window start + bin size')
            return

        if self.analysis.events is None or not self.analysis.neuron_events:
            self.show_error_popup('Please load a .txt file with spike events')
            return

        self.analysis.set_bin_size(self.bin_size_input.value())
        self.analysis.trialize_data(pre_event_duration=int(self.window_start_input.text()), 
                                    post_event_duration=int(self.window_end_input.text()))
        
        self.canvas1.update_plot(self.analysis)
        self.canvas2.update_plot(self.analysis)

    def set_save_directory(self):

        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.save_directory_path = directory

        # save plots to directory


    def export_plots(self):
        
        self.set_save_directory()
        
        if not hasattr(self, 'save_directory_path') or not self.save_directory_path:
            self.show_error_popup('Please select a directory to save the plots')
            return

        file_name = self.export_input.text()

        canvas1_path = os.path.join(self.save_directory_path, f'{file_name}_raster_plot.png')
        canvas2_path = os.path.join(self.save_directory_path, f'{file_name}_psth.png')

        self.canvas1.figure.savefig(canvas1_path)
        self.canvas2.figure.savefig(canvas2_path)

        self.show_info_popup(f'Plots saved to {self.save_directory_path}')

    # def show_interactive_plot(self):
    #     dialog = InteractivePlotDialog(self)
    #     dialog.exec()

    def show_error_popup(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def show_info_popup(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(message)
        msg.setWindowTitle("Information")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()