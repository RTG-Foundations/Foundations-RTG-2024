'''
    Import libraries
'''

import os
import re
import sys
import datetime as dt

from PyQt5.QtWidgets import ( QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit)
from PyQt5.QtCore import QThread, pyqtSignal

# Programs
import closures
import modalFormula
import mequivalence
import pmorphism

from settings_ui import Ui_Settings



'''
    Loads and runs the JSON file
'''
# Get absolute path to program's data directory
def get_data_file_path(filename):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, filename)

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
    success = pyqtSignal(object, object, object)
    fail = pyqtSignal(str)
    
    def __init__(self, program, setup, my_id):
        super().__init__()
        self.program = program
        self.setup = setup
        self.my_id = my_id

    def run(self):
        #try:
        results = execute_methods(self.setup, self.program)
        self.success.emit(self.setup,results, self.my_id)
        #except Exception as e:
        #    self.fail.emit(str(e))



'''
    Manages the creation of the settings window
'''
class MyMainWindow(QMainWindow, Ui_Settings):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_Settings.__init__(self)
        self.setupUi(self)
  
        self.R_closure_inputs = []
        self.R_quotient_inputs = []
        self.R_formula_inputs = []
        self.R_pMorph_inputs = []
        self.S_pMorph_inputs = []
        

        '''
            Connect Buttons
        '''
        # Let's see if Andrew's code goes!
        self.query_comboBox.currentIndexChanged.connect(self.queryTypeChanged)
        self.queryTypeChanged(0)


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

        # m-equivalence
        self.m_spinBox.setMinimum(1)
        self.mEquivN_spinBox.valueChanged.connect(lambda value: self.nChanged(value, "pMorph_R"))
        self.k_spinBox.valueChanged.connect(lambda value: self.nChanged(value, "pMorph_S"))
        self.mEquivN_spinBox.setMinimum(1)
        self.k_spinBox.setMinimum(1)
        self.runMEquiv_pushButton.clicked.connect(self.run_pMorph_methods)

        
        
    def queryTypeChanged(self, index):
        self.query_stackedWidget.setCurrentIndex(index)

    
    def appendFormula(self, symbol):
        # Get the current text and cursor position in the line edit
        current_text = self.formula_lineEdit.text()
        cursor_position = self.formula_lineEdit.cursorPosition()

        # Determine the symbol to append
        if symbol == "arrow":
            new_text = current_text[:cursor_position] + "-->" + current_text[cursor_position:]
            new_cursor_position = cursor_position + 3  # Adjust for length of "-->"
        elif symbol == "diamond":
            new_text = current_text[:cursor_position] + "♢" + current_text[cursor_position:]
            new_cursor_position = cursor_position + 1  # Adjust for length of "♢"
        elif symbol == "false":
            new_text = current_text[:cursor_position] + "⊥" + current_text[cursor_position:]
            new_cursor_position = cursor_position + 1  # Adjust for length of "⊥"
        else:
            return  # Return early if an invalid symbol is passed

        # Set the new text and restore the cursor position
        self.formula_lineEdit.setText(new_text)
        self.formula_lineEdit.setCursorPosition(new_cursor_position)
        self.formula_lineEdit.setFocus()


    def run_pMorph_methods(self):
        #Let me get some of them variables!
        n = self.mEquivN_spinBox.value()
        k = self.k_spinBox.value()
        m = self.m_spinBox.value()

        R = set()
        for i, (label, text_box) in enumerate(self.R_pMorph_inputs):
            y_values = text_box.text().split()
            for y in y_values:
                R.add((i, int(y)))
        
        S = set()
        for i, (label, text_box) in enumerate(self.S_pMorph_inputs):
            y_values = text_box.text().split()
            for y in y_values:
                S.add((i, int(y)))
    
        
        #Let me create this json, I guess!
        selected_methods = []
        if self.pmorphic_radioButton.isChecked():
            selected_methods.append({"name": "call_check_p_morphism", "params": ["F", "G"]})
        if self.log_radioButton.isChecked():
            selected_methods.append({"name": "call_log_equal", "params": ["F", "G"]})
        if self.mEquiv_radioButton.isChecked():
            selected_methods.append({"name": "mEquiv", "params": ["F", "G", "m"]})

        points_F = list(range(n))
        points_G = list(range(k))
    
        F = pmorphism.Frame(points=points_F, relation=R)
        G = pmorphism.Frame(points=points_G, relation=S)
        mysetup = {
        "parameters":
            {
                "F": F,
                "G": G,
                "m": m
            },
            "methods": selected_methods
        }
        
        self.pMorph = RunMethods(program=mequivalence, setup=mysetup, my_id="mEquiv")
        self.pMorph.success.connect(self.writeOutput)  
        self.pMorph.fail.connect(self.taskFailed) 
        self.pMorph.start()

    def run_quotient_methods(self):
        # Get variables
        xn = set(range(self.nQuotient_spinBox.value()))

        R = set()
        for i, (label, text_box) in enumerate(self.R_quotient_inputs):
            y_values = text_box.text().split()
            for y in y_values:
                R.add((i, int(y)))

        V = set()
        for line_edit in self.VQuotient_scrollArea.findChildren(QLineEdit):
            text = line_edit.text()
            if text:
                worlds = set(map(int, text.split()))
                V.add(frozenset(worlds))  # Use frozenset if the inner sets should be immutable

        selected_methods = []

        if self.vClosure_checkBox.isChecked():
            selected_methods.append({"name": "call_compute_closure", "params": ["V", "R", "X"]})
        if self.quotient_checkBox.isChecked():
            selected_methods.append({"name": "call_compute_quotient_frame", "params": ["X", "R", "V"]})

        mysetup = {
            "parameters": {
                "V": V,
                "R": R,
                "X": xn
            },
            "methods": selected_methods
        }

        self.quotient = RunMethods(program=mequivalence, setup=mysetup, my_id="quotient")
        self.quotient.success.connect(self.writeOutput)  
        self.quotient.fail.connect(self.taskFailed) 
        self.quotient.start()

       
     
        
       

   
    def run_closure_methods(self):
        
        # Get variables
        n = self.nClosure_spinBox.value()
        l = self.l_spinBox.value()
        
        R = set()
        for i, (label, text_box) in enumerate(self.R_closure_inputs):
            y_values = text_box.text().split()
            for y in y_values:
                R.add((i, int(y)))
        

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
        
        # Thread to execute methods
        self.closure = RunMethods(program=closures, setup= mysetup, my_id="closure")
        self.closure.success.connect(self.writeOutput)  
        self.closure.fail.connect(self.taskFailed) 
        self.closure.start()


    def writeOutput(self, setup, results, my_id):
        # Define the output file name based on the type

        output_dir = "output"
        file = get_data_file_path(f"{output_dir}/{my_id}_output.txt")
        os.makedirs(output_dir, exist_ok=True)


        with open(file, 'a') as f:
            # Write the parameters from the setup
            f.write("\nParameters:\n")
            for param, value in setup["parameters"].items():
                f.write(f"{param}: {value}\n")
            
            # Write the results from the methods
            f.write("\nResults:\n")
            for method_name, result in results:
                f.write(f"{method_name}:\n{result}\n")
                self.writeToLog(f"{method_name}:\n{result}")

                

            f.write("****************************************************************\n\n")
        
        self.writeToLog(f"Wrote {my_id} output to {file}")


   
    def taskFailed(self, e):
        self.writeToLog(f"{e}")



    def run_formula_methods(self):
        
        # Get variables
        phi = self.formula_lineEdit.text()
        n = self.nFormula_spinBox.value()
        # R 
        R = set()
        for i, (label, text_box) in enumerate(self.R_formula_inputs):
            y_values = text_box.text().split()
            for y in y_values:
                R.add((i, int(y)))
                R = set()
        
        # V 
        V = {}
        for prop, text_box in self.V_formula_inputs.items():
            V[prop] = set()
            worlds = text_box.text().split()
            for world in worlds:
                V[prop].add(world)
        
        # Create JSON file
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
                "V": V
            },
            "methods": selected_methods
        }
        
        # Thread to execute methods
        self.formula = RunMethods(program=modalFormula, setup= mysetup, my_id="formula")
        self.formula.success.connect(self.writeOutput)  
        self.formula.fail.connect(self.taskFailed) 
        self.formula.start()

    '''
        Constructs V by creating a label for each unique propositions in formula_lineEdit,  
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
        # Generate the formatted numbers for display
        numbers = [str(num) for num in range(n)]
        formatted_numbers = ', '.join(numbers)
        
        # Initialize the scroll area and input list based on the type
        if type == "closure":
            self.closureXn_textBrowser.setText(f"Xn= {{{formatted_numbers}}}")
            scrollArea = self.RClosure_scrollArea
            input_list = self.R_closure_inputs
        elif type == "quotient":
            self.xnQuotient_textBrowser.setText(f"Xn= {{{formatted_numbers}}}")
            scrollArea = self.RQuotient_scrollArea
            input_list = self.R_quotient_inputs
        elif type == "formula":
            scrollArea = self.RFormula_scrollArea
            input_list = self.R_formula_inputs
        elif type == "pMorph_R":
            self.mEquivXn_textBrowser.setText(f"Xn= {{{formatted_numbers}}}")
            scrollArea = self.mEquivR_scrollArea
            input_list = self.R_pMorph_inputs
        elif type == "pMorph_S":
            self.mEquivYk_textBrowser.setText(f"Yk= {{{formatted_numbers}}}")
            scrollArea = self.s_scrollArea
            input_list = self.S_pMorph_inputs
        else:
            raise ValueError(f"nChanged called on invalid type {type}")
        
        # Store current values in a dictionary before clearing
        old_values = {label.text(): text_box.text() for label, text_box in input_list}
        input_list.clear()  # Clear the list to store the new widgets
        
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
            
            # Restore the previous value if it exists
            old_value = old_values.get(label.text())
            if old_value is not None:
                text_box.setText(old_value)
            
            row_layout.addWidget(label)
            row_layout.addWidget(text_box)
            
            self.R_layout.addLayout(row_layout)
            
            # Store references to the new widgets
            input_list.append((label, text_box))
        
        # Set the content widget with the new layout to the scroll area
        scrollArea.setWidget(content_widget)


        

    '''
        Displays messages and the time they were sent to the settings log
        
        Parameters:
            message - text to display
    '''
    def writeToLog(self, message):
        current_datetime = dt.datetime.now()
        formatted_datetime = current_datetime.strftime("%H:%M:%S")
        log_message = f'{formatted_datetime}: {message}'
        
        # Append the message to the QTextBrowser
        self.log_textBrowser.append(log_message)
        
        # Automatically scroll to the bottom
        self.log_textBrowser.ensureCursorVisible()
        
        QApplication.processEvents()


   

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())