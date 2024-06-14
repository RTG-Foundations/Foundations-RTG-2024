'''
    Import libraries
'''

import os
import re
import sys
import json
import datetime as dt

from PyQt5.QtWidgets import ( QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QScrollArea, QCheckBox)
from PyQt5.QtCore import QThread, pyqtSignal

# Programs
import closures
import modalFormula
import mequivalence

from settings1_ui import Ui_Settings



'''
    Loads and runs the JSON file
'''
# Get absolute path to program's data directory
def get_data_file_path(filename):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, filename)

# Load the setup file
def load_setup_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Execute methods based on setup file
def execute_methods(setup, program):
    parameters = setup["parameters"]
    methods = setup["methods"]
    results = []
    
    for method in methods:
        method_name = method["name"]
        params = [parameters[param] for param in method["params"]]
        try:
            # Dynamically call the method from control module with the parameters
            result = getattr(program, method_name)(*params)
            results.append((method_name, result))  # Append tuple of (method_name, result)
        except AttributeError:
            results.append((method_name, f"Method {method_name} not found in control module."))
        except Exception as e:
            results.append((method_name, f"Error calling {method_name}: {e}"))
    
    return results


'''
    
    Background task for running methods
    Extends the QThread class to perform tasks asynchronously.

'''
class RunMethods(QThread):
    success = pyqtSignal(object, object)
    fail = pyqtSignal(str)
    
    def __init__(self, program, setup):
        super().__init__()
        self.program = program
        self.setup = setup

    def run(self):
        try:
            results = execute_methods(self.setup, self.program)
            self.success.emit(self.setup,results)
        except Exception as e:
            self.fail.emit(str(e))



'''
    Manages the creation of the settings window
'''
class MyMainWindow(QMainWindow, Ui_Settings):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_Settings.__init__(self)
        self.setupUi(self)
        

        '''
            Connect Buttons
        '''
        # Let's see if Andrew's code goes!
        self.query_comboBox.setCurrentIndex(-1)
        self.query_comboBox.currentIndexChanged.connect(self.queryTypeChanged)

        # closure
        self.nClosure_spinBox.valueChanged.connect(lambda value: self.nChanged(value, "closure"))
        self.runClosures_pushButton.clicked.connect(self.run_closure_methods) 
        self.nClosure_spinBox.setMinimum(1)
        
        # formula
        self.nFormula_spinBox.valueChanged.connect(lambda value: self.nChanged(value, "formula"))
        self.nFormula_spinBox.setMinimum(1)

        self.arrow_pushButton.clicked.connect(lambda: self.appendFormula("arrow"))
        self.diamond_pushButton.clicked.connect(lambda: self.appendFormula("diamond"))
        self.false_pushButton.clicked.connect(lambda: self.appendFormula("false"))

        self.formula_lineEdit.textChanged.connect(self.check_formula_for_params)

        self.runFormula_pushButton.clicked.connect(self.run_formula_methods) 


        # Quotient Frame
        self.V_counter = 0
        self.V_layout = QVBoxLayout()
        self.nQuotient_spinBox.valueChanged.connect(lambda value: self.nChanged(value, "quotient"))
        self.addV_pushButton.clicked.connect(self.add_V)
        self.delV_pushButton.clicked.connect(self.remove_V)
        self.runQuotient_pushButton.clicked.connect(self.run_quotient_methods) 
        
        

        # Create the scroll widget for the output log
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.log_scrollArea.setWidgetResizable(True)
        self.log_scrollArea.setWidget(self.scroll_widget)

    def queryTypeChanged(self, index):
        self.query_stackedWidget.setCurrentIndex(index)

    def appendFormula(self, symbol):
        current_text = self.formula_lineEdit.text()
        if (symbol == "arrow"):
            self.formula_lineEdit.setText(current_text + "-->")
        elif (symbol == "diamond"):
            self.formula_lineEdit.setText(current_text + "♢")
        elif (symbol == "false"):
            self.formula_lineEdit.setText(current_text + "⊥")

    def run_quotient_methods(self):
        # Get variables
        xn = list(range(self.nQuotient_spinBox.value()))

        R = []
        for i, (label, text_box) in enumerate(self.R_quotient_inputs):
            y_values = text_box.text().split()
            for y in y_values:
                R.append([i, int(y)])

        V = []
        for line_edit in self.VQuotient_scrollArea.findChildren(QLineEdit):
            text = line_edit.text()
            if text:
                worlds = set(map(int, text.split()))
                V.append(list(worlds))

        selected_methods = []

        
        if self.vClosure_checkBox.isChecked():
            selected_methods.append( {"name": "compute_closure", "params": ["V", "R", "X"]})
        if self.quotient_checkBox.isChecked():
            selected_methods.append({"name": "quotient_frame", "params": ["X", "R", {"closure_V": ["compute_closure_result"]}]})

        mysetup = {
            "parameters": {
                "V": V,
                "R": R,
                "X": xn
            },
            "methods": selected_methods
        }

        # Thread to execute methods
        self.quotient = RunMethods(program=mequivalence, setup= mysetup)
        self.quotient.success.connect(self.writeclosureOutput)  
        self.quotient.fail.connect(self.taskFailed) 
        self.quotient.start()

       
     
        
       

   
    def run_closure_methods(self):
        
        # Get variables
        n = self.nClosure_spinBox.value()
        l = self.l_spinBox.value()
        
        R = []
        for i, (label, text_box) in enumerate(self.R_closure_inputs):
            y_values = text_box.text().split()
            for y in y_values:
                R.append([i, int(y)])
        

        # Create JSON
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
        
        mysetup = {
            "parameters": {
                "n": n,
                "R": R,
                "l": l
            },
            "methods": selected_methods
        }
        
        setup_file_path = "closure_setup.json"
        with open(setup_file_path, 'w') as f:
            json.dump(mysetup, f, indent=4)
        
        # Thread to execute methods
        self.closure = RunMethods(program=closures, setup= mysetup)
        self.closure.success.connect(self.writeclosureOutput)  
        self.closure.fail.connect(self.taskFailed) 
        self.closure.start()

    
    def writeclosureOutput(self, setup, results):

        file = get_data_file_path('closure_output.txt')
        with open(file, 'a') as f:
            # Write the parameters from the setup
            f.write("Parameters:\n")
            for param, value in setup["parameters"].items():
                f.write(f"{param}: {value}\n")
            
            # Write results
            f.write("\nResults:\n")
            for method_name, result in results:
                f.write(f"{method_name}: {result}\n")
                self.writeToLog(f"{method_name}: {result}")
            f.write("****************************************************************\n\n")
        self.writeToLog(f"Wrote output to {file}")


    def taskFailed(self, e):
        self.writeToLog(f"{e}")



    def run_formula_methods(self):
        
        # Get variables
        phi = self.formula_lineEdit.text()
        n = self.nFormula_spinBox.value()
        # R 
        R = []
        for i, (label, text_box) in enumerate(self.R_formula_inputs):
            y_values = text_box.text().split()
            for y in y_values:
                R.append([i, int(y)])
        # V 
        V = {}
        for prop, text_box in self.V_formula_inputs.items():
            V[prop] = set()
            worlds = text_box.text().split()
            for world in worlds:
                V[prop].add(world)
        
        # Create JSON file
        V_serializable = {k: list(v) for k, v in V.items()}
        selected_methods = []
        if self.subformulas_radioButton.isChecked():
            selected_methods.append({"name": "find_subformulas", "params": ["phi"]})
        if self.sValid_radioButton.isChecked():
            selected_methods.append({"name": "is_formula_valid_in_model", "params": ["phi", "n", "R"]})
        if self.findX_radioButton.isChecked():
            selected_methods.append({"name": "get_satisfying_points_ast", "params": ["phi", "n", "R", "V"]})

        mysetup = {
            "parameters": {
                "phi": phi,
                "n": n,
                "R": R,
                "V": V_serializable
            },
            "methods": selected_methods
        }
        
        setup_file_path = "formula_setup.json"
        with open(setup_file_path, 'w') as f:
            json.dump(mysetup, f, indent=4)

        # Thread to execute methods
        self.formula = RunMethods(program=modalFormula, setup= mysetup)
        self.formula.success.connect(self.writeFormulaOutput)  
        self.formula.fail.connect(self.taskFailed) 
        self.formula.start()


    def writeFormulaOutput(self, setup, results):
        file = get_data_file_path('formula_output.txt')
        with open(file, 'a') as f:
            # Write the parameters from the setup
            f.write("Parameters:\n")
            for param, value in setup["parameters"].items():
                f.write(f"{param}: {value}\n")
            
            f.write("\nResults:\n")
            
            # Write the results from the methods
            with open(file, 'a') as f:
                for method_name, result in results:
                    f.write(f"{method_name}: {result}\n")
                    self.writeToLog(f"{method_name}: {result}")
                f.write("****************************************************************\n\n")
            self.writeToLog(f"Wrote output to {file}")
            

    '''
        Cnstructs V by creating a label for each unique propositions in formula_lineEdit,  
        and a corresponding lineEdit to be filled with with worlds where the proposition 
        is true
    '''
    def check_formula_for_params(self):
        
        formula_text = self.formula_lineEdit.text()
        
        # Find all unique matches of "p\d+"
        matches = set(re.findall(r'p\d+', formula_text))

        # Clear existing widgits from layout
        scrollArea = self.VFormula_scrollArea
        layout = scrollArea.layout()

        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        # Create a new layout for the scroll area content
        content_widget = QWidget()
        self.V_layout = QVBoxLayout(content_widget)
        self.V_formula_inputs = {}

        # Populate the layout with label-text box pairs
        for prop in list(matches):
            self.V_formula_inputs[prop] = []
            row_layout = QHBoxLayout() 

            label = QLabel(f'{prop}')
            text_box = QLineEdit()
            
            row_layout.addWidget(label)
            row_layout.addWidget(text_box)
            
            self.V_layout.addLayout(row_layout)
            self.V_formula_inputs[prop] = text_box

        # Set the content widget with the new layout to the scroll area
        scrollArea.setWidget(content_widget)

    def add_V(self):
        layout = self.VQuotient_scrollArea.widget().layout()
        
        # Ensure the VQuotient_layout exists
        if layout is None:
            layout = QVBoxLayout()
            content_widget = QWidget()
            content_widget.setLayout(layout)
            self.VQuotient_scrollArea.setWidget(content_widget)
        
        # Create a horizontal layout for each label-text box pair
        row_layout = QHBoxLayout()
        
        label = QLabel(f"V{self.V_counter}", self)
        text_box = QLineEdit()
        
        row_layout.addWidget(label)
        row_layout.addWidget(text_box)
        
        # Add the horizontal layout to the vertical layout of the scroll area
        layout.addLayout(row_layout)
        
        # Increment the counter
        self.V_counter += 1
        


    def remove_V(self):
        layout = self.VQuotient_scrollArea.widget().layout()
        
        # Ensure there is a layout to work with
        if layout is None:
            return  # No items to remove
        
        # Get the count of items in the layout
        count = layout.count()
        
        # Check if there are any items to remove
        if count > 0:
            # Remove the last added horizontal layout (label-text box pair)
            item = layout.itemAt(count - 1)
            if item is not None:
                # Remove all widgets from the layout item
                for i in reversed(range(item.count())):
                    widget = item.itemAt(i).widget()
                    if widget is not None:
                        widget.deleteLater()
                    item.removeItem(item.itemAt(i))
                
                # Remove the layout item itself from the main layout
                layout.removeItem(item)
                
                # Reset the counter if any items are removed
                if self.V_counter > 0:
                    self.V_counter -= 1


    '''
        Constructs R from N, where each label is a node 0, ... n-1
        and the line edit can be filled with  a list of relations
     
    '''
    def nChanged(self, n, type):

        numbers = [str(num) for num in range(n)]
        formatted_numbers = '\n\t'.join(', '.join(numbers[i:i+20]) for i in range(0, len(numbers), 20))
        
        if type == "closure":
            self.Xn_label.setText(f"Xn= {{\t{formatted_numbers}\t}}") # Xn label
            scrollArea = self.RClosure_scrollArea
            self.R_closure_inputs = []

        elif type == "quotient":
            self.xnQuotient_label.setText(f"Xn= {{\t{formatted_numbers}\t}}") # Xn label
            scrollArea = self.RQuotient_scrollArea
            self.R_quotient_inputs = []

        elif type == "formula":
            scrollArea = self.RFormula_scrollArea
            self.R_formula_inputs = []
        else:
            raise ValueError(f"nChanged called on invalid type {type}")
        

        # Clear any existing widgets from the layout
        layout = scrollArea.layout()
        
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        

        # Create a new layout for the scroll area content
        content_widget = QWidget()
        self.R_layout = QVBoxLayout(content_widget)
        
        
        # Populate the layout with label-text box pairs
        for i in range(n):
            row_layout = QHBoxLayout()  # Create a horizontal layout for each label-text box pair

            label = QLabel(f'{i}')
            text_box = QLineEdit()
            
            row_layout.addWidget(label)
            row_layout.addWidget(text_box)
            
            self.R_layout.addLayout(row_layout)
            
            if type == "closure":
                self.R_closure_inputs.append((label, text_box))
            elif type == "formula":
                self.R_formula_inputs.append((label, text_box))
            elif type == "quotient":
                self.R_quotient_inputs.append((label, text_box))

             
        # Set the content widget with the new layout to the scroll area
        scrollArea.setWidget(content_widget)

        

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