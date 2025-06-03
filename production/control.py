'''
    Import libraries
'''

import os
import re
import sys

from PyQt5.QtWidgets import ( QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QTabWidget)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import networkx as nx

# Programs
import closures
import modalFormula
import mequivalence
import pmorphism

from settings_ui import Ui_Settings


'''
    Gets data output path
'''
def get_data_file_path(filename):
    home_dir = os.path.expanduser("~")
    output_dir = os.path.join(home_dir, "finiteStructures_output")
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, filename)

# Execute methods based on setup file
def execute_methods(setup, program):
    parameters = setup["parameters"]
    methods = setup["methods"]
    results = []
    
    for method in methods:
        method_name = method["name"]
        params = [parameters[param] for param in method["params"]]
        try:
            result = getattr(program, method_name)(*params)
            results.append((method_name, result))  
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
    active = pyqtSignal()
    done = pyqtSignal()
    
    def __init__(self, program, setup, my_id):
        super().__init__()
        self.program = program
        self.setup = setup
        self.my_id = my_id

    def run(self):
        self.active.emit()
        try:
            results = execute_methods(self.setup, self.program)
            self.success.emit(self.setup,results, self.my_id)
        except Exception as e:
            self.fail.emit(str(e))

        self.done.emit()


'''
    Manages the creation of the settings window
'''
class MyMainWindow(QMainWindow, Ui_Settings):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_Settings.__init__(self)
        self.setupUi(self)

        self.num_threads = 0

        '''
            For storing relations
        '''
        self.R_closure_inputs = []
        self.R_quotient_inputs = []
        self.R_formula_inputs = []
        self.R_pMorph_inputs = []
        self.S_pMorph_inputs = []
        

        '''
            Connect Buttons
        '''
        # toggling between windows
        self.query_comboBox.currentIndexChanged.connect(self.queryTypeChanged)
        self.queryTypeChanged(0)


        # closure
        self.nClosure_spinBox.valueChanged.connect(lambda value: self.nChanged(value, "closure"))
        self.runClosures_pushButton.clicked.connect(self.run_closure_methods) 
        self.nClosure_spinBox.setMinimum(1)
        
            # List to hold all created closure graph windows
        self.graph_windows = []

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
  

    '''
        Lock buttons if threads running
    '''
    def startThread(self):
        self.num_threads +=1
        
        self.runQuotient_pushButton.setEnabled(False)
        self.runClosures_pushButton.setEnabled(False)
        self.runFormula_pushButton.setEnabled(False)
        self.runMEquiv_pushButton.setEnabled(False)

    '''
        Unlock buttons if no threads running
    '''
    def removeThread(self):
        self.num_threads -=1
        if self.num_threads == 0:
            self.runQuotient_pushButton.setEnabled(True)
            self.runClosures_pushButton.setEnabled(True)
            self.runFormula_pushButton.setEnabled(True)
            self.runMEquiv_pushButton.setEnabled(True)




    '''
        Toggle between windows
        Input: 
            index: index window to toggle to
    '''  
    def queryTypeChanged(self, index):
        self.query_stackedWidget.setCurrentIndex(index)

    
    '''
        Append symbol to self.formula_lineEdit after cursor
        Input: 
            symbol: id of symbol to write
    '''  
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


    '''
        Get values from GUI and start thread to run pmorphism  
        and m-equivalence methods
    '''
    def run_pMorph_methods(self):
        try:
            #Let me get some of them variables!
            n = self.mEquivN_spinBox.value()
            k = self.k_spinBox.value()
            m = self.m_spinBox.value()

            R = set()
            for i, (label, text_box) in enumerate(self.R_pMorph_inputs):
                y_values = text_box.text().split()
                for y in y_values:
                    try:
                        y_int = int(y)
                    except ValueError as e:
                        raise ValueError(f"Error in R at row {i}. R must be spaced seperated integers between 0 and {n-1}")
                    if y_int < 0 or y_int >= n:
                        raise ValueError(f"R contains invalid value {y_int} (must be between 0 and {n-1})")
                    R.add((i, y_int))
                    
            
            S = set()
            for i, (label, text_box) in enumerate(self.S_pMorph_inputs):
                y_values = text_box.text().split()
                for y in y_values:
                    try:
                        y_int = int(y)
                    except ValueError as e:
                        raise ValueError(f"Error in S at row {i}. S must be spaced seperated integers between 0 and {k-1}")
                    if y_int < 0 or y_int >= k:
                        raise ValueError(f"S contains invalid value {y_int} (must be between 0 and {k-1})")
                    S.add((i, y_int))
    
        
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
            self.pMorph.fail.connect(self.writeToLog)
            self.pMorph.active.connect(self.startThread)  
            self.pMorph.done.connect(self.removeThread)  
            self.pMorph.start()
        except Exception as e:
            self.writeToLog(f"Bad input: {e}")

    '''
        Get values from GUI and start thread to run quotient methods
    '''
    def run_quotient_methods(self):
        try:
            # Get variables
            n = self.nQuotient_spinBox.value()
            xn = set(range(n))

            R = set()
            for i, (label, text_box) in enumerate(self.R_quotient_inputs):
                y_values = text_box.text().split()
                for y in y_values:
                    try:
                        y_int = int(y)
                    except ValueError as e:
                        raise ValueError(f"Error in R at row {i}. R must be spaced seperated integers between 0 and {n-1}")
                    if y_int < 0 or y_int >= n:
                        raise ValueError(f"R contains invalid value {y_int} (must be between 0 and {n-1})")
                    R.add((i, y_int))
                    
            V = set()
            for line_edit in self.VQuotient_scrollArea.findChildren(QLineEdit):
                text = line_edit.text()
                if text:
                    try:
                        worlds = set(map(int, text.split()))
                    except ValueError as e:
                        raise ValueError(f"V must be spaced seperated integers between 0 and {n-1}")
                    
                    for world in worlds:
                        if world < 0 or world >= n:
                            raise ValueError(f"V contains invalid point {world} (must be between 0 and {n-1})")

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
            self.quotient.fail.connect(self.writeToLog) 
            self.quotient.active.connect(self.startThread)  
            self.quotient.done.connect(self.removeThread)  
            self.quotient.start()
        except Exception as e:
            self.writeToLog(f"Bad input: {e}")

    '''
        Get values from GUI and start thread to run closure methods
    '''
    def run_closure_methods(self):
        try:
            # Get variables
            n = self.nClosure_spinBox.value()
            l = self.l_spinBox.value()
            
            R = set()
            for i, (label, text_box) in enumerate(self.R_closure_inputs):
                y_values = text_box.text().split()
                for y in y_values:
                    try:
                        y_int = int(y)
                    except ValueError as e:
                        raise ValueError(f"Error in R at row {i}. R must be spaced seperated integers between 0 and {n-1}")
                    if y_int < 0 or y_int >= n:
                        raise ValueError(f"R contains invalid value {y_int} (must be between 0 and {n-1})")
                    R.add((i, y_int))
            
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
            self.closure.fail.connect(self.writeToLog) 
            self.closure.active.connect(self.startThread)  
            self.closure.done.connect(self.removeThread)  
            self.closure.start()
        except Exception as e:
            self.writeToLog(f"Bad input: {e}")


    '''
        Get values from GUI and start thread to run formula methods
    '''
    def run_formula_methods(self):
        try:
            # Get variables
            phi = self.formula_lineEdit.text()
            if not phi:
                raise ValueError("Formula cannot be empty")
        
            n = self.nFormula_spinBox.value()
            
            # R 
            R = set()
            for i, (label, text_box) in enumerate(self.R_formula_inputs):
                y_values = text_box.text().split()
                for y in y_values:
                    try:
                        y_int = int(y)
                    except ValueError as e:
                        raise ValueError(f"Error in R at row {i}. R must be spaced seperated integers between 0 and {n-1}")
                    if y_int < 0 or y_int >= n:
                        raise ValueError(f"R contains invalid value {y_int} (must be between 0 and {n-1})")
                    R.add((i, y_int))

            
            # V 
            V = {}
            for prop, text_box in self.V_formula_inputs.items():
                V[prop] = set()
                worlds = text_box.text().split()
                for world in worlds:
                    try:
                        world_int = int(world)
                    except ValueError as e:
                        raise ValueError(f"V contains invalid point '{world}' for proposition  {prop} (must be integers between 0 and {n-1})")

                    if world_int < 0 or world_int >= n:
                        raise ValueError(f"Invalid input in V for  proposition {prop} (must be spaced seperated integers between 0 and {n-1})")
                    V[prop].add(world_int)

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
            self.formula.fail.connect(self.writeToLog) 
            self.formula.active.connect(self.startThread)  
            self.formula.done.connect(self.removeThread)  
            self.formula.start()
        except Exception as e:
            self.writeToLog(f"Bad input: {e}")

    '''
        Write the results of the methods to {my_id}_output.txt 
        and generate a graph to display the closure method results.
        
        Input:
            setup: dictionary of method names and parameters
            results: dictionary of method names and return values
            my_id: id for the tab calling the methods
    '''
    def writeOutput(self, setup, results, my_id):

        # Define the output file name based on the type
        self.writeToLog(f"**** {my_id.upper() } ****")
        output_dir = "output"
        file = get_data_file_path(f"{my_id}_output.txt")
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

            # create graphs if type is closure
            if my_id == "closure":
                self.graph_window = GraphWindow()
                self.graph_window.show()

                self.graph_window.add_graph(setup["parameters"]["R"], "R") 
                for method_name, result in results: 
                    if method_name not in {"find_connected_components", "find_subframe"}:
                        self.graph_window.add_graph(result, method_name)            
                
            f.write("****************************************************************\n\n")
    
        self.writeToLog(f"Wrote {my_id} output to {file}")


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


    '''
        Append a new lineEdit to self.VQuotient_scrollArea 
    '''
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
        

    '''
        Remove the last lineEdit from self.VQuotient_scrollArea 
    '''
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
        Displays messages to the settings log
        
        Parameters:
            message - text to display
    '''
    def writeToLog(self, message):
     
        # Append the message to the QTextBrowser
        self.log_textBrowser.append(message+ "\n")
        
        # Automatically scroll to the bottom
        self.log_textBrowser.ensureCursorVisible()
        
        QApplication.processEvents()


    """
        Lock buttons
    """
    def lock_buttons(self):
        self.runQuotient_pushButton.setEnabled(False)
        self.runClosures_pushButton.setEnabled(False)
        self.runFormula_pushButton.setEnabled(False)
        self.runMEquiv_pushButton.setEnabled(False)

    
    """
        Unlock buttons
    """
    def unlock_buttons(self):
        self.runQuotient_pushButton.setEnabled(True)
        self.runClosures_pushButton.setEnabled(True)
        self.runFormula_pushButton.setEnabled(True)
        self.runMEquiv_pushButton.setEnabled(True)

    '''
        Quits the entire application when the main window is closed.
    '''
    def closeEvent(self, event):
        QApplication.quit()

'''
    Manages the creation of the graph window
'''
class GraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Closure Graphs")
        self.setMinimumSize(400, 300)

        # Tab widget to hold multiple graphs
        self.tab_widget = QTabWidget()
        
        # Layout for the main window
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)

        label = QLabel("Red is irreflexive, Blue is reflexive")
        layout.addWidget(label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def add_graph(self, R, title):
        # Create the figure for the graph
        figure = create_graph(R)
        canvas = FigureCanvas(figure)

        # Add a new tab for the graph
        self.tab_widget.addTab(canvas, title)
        
    
'''
    Creates figure from the relations
'''
def create_graph(R):
    # Create directed graph from edges in R
    graph_R = nx.DiGraph()
    for (x, y) in R:
        graph_R.add_edge(x, y)

    # 3D positions
    pos_R = nx.spring_layout(graph_R, dim=3)

    # Create the figure and 3D plot
    fig = Figure(figsize=(8, 6))
    ax1 = fig.add_subplot(111, projection='3d')
    closures.visualize_3d(graph_R, pos_R, ax1)
    
    return fig

if __name__ == '__main__':
    app = QApplication(sys.argv)
    icon_path = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))), "icon.ico")
    app.setWindowIcon(QIcon(icon_path))
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())