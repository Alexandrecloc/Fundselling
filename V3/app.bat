@echo off
if not exist "app_env" (
    python -m venv app_env
    echo Environnement virtuel cree.
)

echo Activation de l'environnement virtuel...
call app_env\Scripts\activate

echo Installation des dependances depuis requirements.txt...
pip install -r requirements.txt

echo Lancement de l'application Streamlit...
streamlit run app.py

pause
