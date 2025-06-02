# Installing Algorithms on Finite Structures Program

## Prerequisites
- Python 3.x – https://www.python.org/downloads/
- Git – https://git-scm.com/downloads
- PyInstaller – Installed via pip (we’ll cover this below).

## Step 1: Install git

* Windows:
Download and install Git:
https://git-scm.com/downloads

During installation:
Select "Add Git to PATH".

* macOS:
Install Git using Homebrew:
Install homebrew from:  https://brew.sh/
brew install git

* Linux:
Install Git via your package manager:
sudo apt install git       # Debian/Ubuntu
sudo dnf install git       # Fedora
sudo pacman -S git         # Arch

Verify installation:
git --version
You should see something like:
git version 2.44.0


## Step 2: Clone the Repository
Open a terminal and run:
git clone https://github.com/RTG-Foundations/Foundations-RTG-2024

# Step 3: Install Python Dependencies
Navigate into the project directory:
cd Foundations-RTG-2024

Install the dependencies:
pip3 install -r requirements.txt

# Step 4: Install PyInstaller
pip3 install pyinstaller
pyinstaller  afstructs.spec
✅ This creates a dist folder with the executable.

📂 Step 6: Locate and Run the Executable
Your executable will be in the dist directory:

bash
Copy
Edit
dist/
├── YourExecutable.exe        # Windows
├── YourExecutable            # macOS/Linux (no extension)
Run the program:

Windows: Double-click the .exe file or run in terminal:

bash
Copy
Edit
./dist/YourExecutable.exe
macOS/Linux: Run in terminal:

bash
Copy
Edit
./dist/YourExecutable
You may need to give execute permissions on macOS/Linux:

bash
Copy
Edit
chmod +x ./dist/YourExecutable
🔧 Notes and Troubleshooting
If you encounter issues:

Ensure Python and Git are installed and in your PATH.

Use the correct Python version (python --version or python3 --version).

Use a virtual environment to avoid conflicts.

On macOS, if you see a security warning, allow the app in System Preferences > Security & Privacy > General.
