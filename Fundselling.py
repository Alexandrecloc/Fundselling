import streamlit.web.cli as stcli
import sys
import os

def get_resource_path(relative_path):
    """Get the absolute path to a resource; works for dev and PyInstaller."""
    try:
        # For PyInstaller
        base_path = sys._MEIPASS
    except AttributeError:
        # For normal execution
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    app_path = get_resource_path('app.py')
    sys.argv = ['streamlit', 'run', app_path, '--global.developmentMode=false']
    sys.exit(stcli.main())
