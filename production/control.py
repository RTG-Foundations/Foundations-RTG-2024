'''
    GUI application 

'''


import sys
import json
from PyQt5.QtWidgets import ( QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QScrollArea, QCheckBox)
from PyQt5.QtCore import QThread, pyqtSignal
import datetime as dt
import closures
import os

from settings_ui import Ui_Settings

# Get absolute path to program's data directory
def get_data_file_path(filename):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, filename)

# Load the setup file
def load_setup_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Execute methods based on setup file
def execute_methods(setup):
    parameters = setup["parameters"]
    methods = setup["methods"]
    results = []
    
    for method in methods:
        method_name = method["name"]
        params = [parameters[param] for param in method["params"]]
        try:
            # Dynamically call the method from control module with the parameters
            result = getattr(closures, method_name)(*params)
            results.append((method_name, result))  # Append tuple of (method_name, result)
        except AttributeError:
            results.append((method_name, f"Method {method_name} not found in control module."))
        except Exception as e:
            results.append((method_name, f"Error calling {method_name}: {e}"))
    
    return results



'''
    Manages the creation of the settings window
'''
class MyMainWindow(QMainWindow, Ui_Settings):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_Settings.__init__(self)
        self.setupUi(self)

        # connect N
        self.N_spinBox.valueChanged['int'].connect(self.nChanged)
        self.runClosures_pushButton.clicked.connect(self.run_methods) 
        self.N_spinBox.setMinimum(1)

        
        # Create the scroll widget for the output log
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.log_scrollArea.setWidgetResizable(True)
        self.log_scrollArea.setWidget(self.scroll_widget)

        
      
   
    def run_methods(self):
        n = self.N_spinBox.value()
        l = self.l_spinBox.value()
        
        # Construct R from the text boxes
        R = []
        for i, (label, text_box) in enumerate(self.R_inputs):
            y_values = text_box.text().split()
            for y in y_values:
                R.append([i, int(y)])
        
        selected_methods = []
        
    
        if self.reflex_checkBox.isChecked():
            selected_methods.append({"name": "reflexive_closure", "params": ["n", "R"]})
        if self.sym_checkBox.isChecked():
            selected_methods.append({"name": "symmetric_closure", "params": ["n", "R"]})
        if self.transFloyd_checkBox.isChecked():
            selected_methods.append({"name": "floyd_transitive_closure", "params": ["n", "R"]})
        if self.transDot_checkBox.isChecked():
            selected_methods.append({"name": "transitive_closure", "params": ["n", "R"]})
        if self.connected_checkBox.isChecked():
            selected_methods.append({"name": "find_connected_components", "params": ["n", "R"]})
        if self.subframe_checkBox.isChecked():
            selected_methods.append({"name": "find_subframe", "params": ["n", "l", "R"]})
        
        setup = {
            "parameters": {
                "n": n,
                "R": R,
                "l": l
            },
            "methods": selected_methods
        }
        
        # Save setup to a JSON file
        setup_file_path = "closure_setup.json"
        with open(setup_file_path, 'w') as f:
            json.dump(setup, f, indent=4)
        
        # Execute methods
        try:
            results = execute_methods(setup)
            # Write output to output.txt
            file = get_data_file_path('closure_output.txt')
            with open(file, 'a') as f:
                f.write(f"N = {n} R ={R}\n")
                for method_name, result in results:
                    f.write(f"{method_name}: {result}\n")
                    self.writeToLog(f"{method_name}: {result}\n")
                f.write("****************************************************************\n\n")
            self.writeToLog(f"Wrote output to {file}")
        except Exception as e:
            self.writeToLog(e)

        
        
    
    def nChanged(self, n):

        # Xn label
        numbers = [str(num) for num in range(n)]
        formatted_numbers = '\n\t'.join(', '.join(numbers[i:i+10]) for i in range(0, len(numbers), 10))
        self.Xn_label.setText(f"Xn= {{\t{formatted_numbers}\t}}")

        
        # Clear any existing widgets from the layout
        layout = self.R_scrollArea.layout()
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        

        # Create a new layout for the scroll area content
        content_widget = QWidget()
        self.R_layout = QVBoxLayout(content_widget)
        self.R_inputs = []

        
        # Populate the layout with new label-text box pairs
        for i in range(n):
            row_layout = QHBoxLayout()  # Create a horizontal layout for each label-text box pair

            label = QLabel(f'{i}')
            text_box = QLineEdit()
            
            row_layout.addWidget(label)
            row_layout.addWidget(text_box)
            
            self.R_layout.addLayout(row_layout)
            self.R_inputs.append((label, text_box))

        # Set the content widget with the new layout to the scroll area
        self.R_scrollArea.setWidget(content_widget)

        

    '''
        Displays messages and the time they were sent to the settings log
        
        Parameters:
            message - text to display
    '''
    def writeToLog(self, message):
        current_datetime = dt.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H:%M:%S")
        label = QLabel('{}: {}'.format(formatted_datetime,message))
        self.scroll_layout.addWidget(label) 

        # Scroll to the bottom of the scroll view
        parent = self.scroll_layout.parentWidget()
        area = QScrollArea(parent)
        vbar = area.verticalScrollBar()
        vbar.setValue(vbar.maximum())
        
        QApplication.processEvents()


   

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())