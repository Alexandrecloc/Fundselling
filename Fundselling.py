import streamlit.web.cli as stcli
import sys
import os
import appdirs

def get_resource_path(relative_path):
    """Get the absolute path to a resource; works for dev and PyInstaller."""
    try:
        # For PyInstaller
        base_path = sys._MEIPASS
    except AttributeError:
        # For normal execution
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Define your app name (used for creating a dedicated folder)
app_name = "FundsellingApp"  # Replace this with your actual app name

# Get the application data directory specific to this app
data_dir = appdirs.user_data_dir(app_name)

# Ensure the data directory exists
os.makedirs(data_dir, exist_ok=True)

# Redirect stdout and stderr to log files in the app's data directory
sys.stdout = open(os.path.join(data_dir, "output.log"), "w")
sys.stderr = open(os.path.join(data_dir, "error.log"), "w")

if __name__ == '__main__':
    app_path = get_resource_path('app.py')
    # Set up arguments for Streamlit to run the app
    sys.argv = ['streamlit', 'run', app_path, '--global.developmentMode=false']
    # Run the Streamlit CLI main function
    sys.exit(stcli.main())
