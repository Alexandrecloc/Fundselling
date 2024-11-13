import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import shutil
import appdirs

# Define your application name for appdirs
app_name = "Fundselling"

# Determine the user data directory using appdirs
DATA_DIR = appdirs.user_data_dir(app_name)

# Ensure the user data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Global assets file path
ASSETS_FILE = os.path.join(DATA_DIR, "assets.csv")

# Configure the page for a wide layout
st.set_page_config(layout="wide")

# Function to get the list of scenarios
def get_scenarios():
    return [name for name in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, name))]

# Function to select a scenario
def select_scenario():
    st.sidebar.header("Sélection de Scénario")

    scenarios = get_scenarios()

    # Initialize the selected scenario
    if 'selected_scenario' not in st.session_state:
        if scenarios:
            st.session_state['selected_scenario'] = scenarios[0]
        else:
            st.session_state['selected_scenario'] = None  # No scenario selected

    scenario_options = scenarios + ["Créer un Nouveau Scénario"]

    selected_option = st.sidebar.selectbox(
        "Sélectionnez un Scénario",
        scenario_options,
        index=scenario_options.index(st.session_state['selected_scenario']) if st.session_state['selected_scenario'] in scenarios else len(scenario_options) - 1
    )

    if selected_option == "Créer un Nouveau Scénario":
        new_scenario_name = st.sidebar.text_input("Entrez le nom du nouveau scénario")
        if st.sidebar.button("Créer le Scénario"):
            if new_scenario_name:
                st.session_state['selected_scenario'] = new_scenario_name
                os.makedirs(os.path.join(DATA_DIR, st.session_state['selected_scenario']), exist_ok=True)
                st.experimental_rerun()
    else:
        if selected_option != st.session_state.get('selected_scenario', None):
            st.session_state['selected_scenario'] = selected_option
            st.experimental_rerun()

    # **Option to delete the selected scenario**
    if st.session_state['selected_scenario'] is not None:
        st.sidebar.markdown("---")

        # Initialize the delete confirmation state
        if 'delete_scenario_clicked' not in st.session_state:
            st.session_state['delete_scenario_clicked'] = False

        # If the delete button has been clicked
        if st.session_state['delete_scenario_clicked']:
            confirmer_suppression = st.sidebar.checkbox("Je confirme la suppression du scénario", key='confirm_delete_scenario')
            if confirmer_suppression:
                supprimer_scenario(st.session_state['selected_scenario'])
                st.session_state['selected_scenario'] = None
                st.session_state['delete_scenario_clicked'] = False
                st.experimental_rerun()
        else:
            # Display the delete button
            if st.sidebar.button("Supprimer le Scénario Sélectionné"):
                st.session_state['delete_scenario_clicked'] = True
                st.experimental_rerun()


# Function to delete a scenario
def supprimer_scenario(nom_scenario):
    scenario_path = os.path.join(DATA_DIR, nom_scenario)
    if os.path.exists(scenario_path):
        shutil.rmtree(scenario_path)
        st.success(f"Le scénario '{nom_scenario}' a été supprimé avec succès.")
    else:
        st.error(f"Le scénario '{nom_scenario}' n'existe pas.")

# Function to load assets from the global CSV file at startup
def charger_actifs():
    if os.path.exists(ASSETS_FILE):
        return pd.read_csv(ASSETS_FILE, index_col=0).to_dict(orient='index')
    return {}

# Function to save assets to the global CSV file
def sauvegarder_actifs():
    pd.DataFrame.from_dict(st.session_state['assets'], orient='index').to_csv(ASSETS_FILE)

# Function to compute the total price per asset
def compute_asset_data(assets_dict):
    assets_df = pd.DataFrame.from_dict(assets_dict, orient='index')
    assets_df['prix_total'] = assets_df['quantite'] * assets_df['prix']
    return assets_df

# Function to display data in the sidebar
def afficher_donnees_sidebar():
    st.sidebar.header("Données des Actifs")
    if st.session_state['assets']:
        assets_df = compute_asset_data(st.session_state['assets'])
        st.sidebar.dataframe(assets_df[['prix', 'quantite', 'prix_total']])
        st.sidebar.write("Graphique du Prix Total par Actif")
        fig, ax = plt.subplots(figsize=(5, 4))
        assets_df['prix_total'].plot(kind='bar', ax=ax, color="#69b3a2", edgecolor="black", alpha=0.8)
        ax.set_xlabel("Actifs")
        ax.set_ylabel("Prix Total (€)")
        ax.set_title("Prix Total par Actif")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        st.sidebar.pyplot(fig, use_container_width=True)
    else:
        st.sidebar.write("Aucun actif ajouté.")

# Function to add a new asset
def ajouter_actif(nom, prix, quantite, nb_ventes):
    if nom not in st.session_state['assets']:
        st.session_state['assets'][nom] = {
            'prix': prix,
            'quantite': quantite,
            'nb_ventes': nb_ventes
        }
        sauvegarder_actifs()
        st.experimental_rerun()

# Function to modify an existing asset
def modifier_actif(nom, prix, quantite, nb_ventes):
    if nom in st.session_state['assets']:
        st.session_state['assets'][nom].update({
            'prix': prix,
            'quantite': quantite,
            'nb_ventes': nb_ventes
        })
        sauvegarder_actifs()
        st.experimental_rerun()

# Function to delete an asset
def supprimer_actif(nom):
    if nom in st.session_state['assets']:
        del st.session_state['assets'][nom]
        # Delete the asset's sales files in all scenarios
        for scenario in get_scenarios():
            scenario_folder = os.path.join(DATA_DIR, scenario)
            supprimer_fichier_vente(nom, scenario_folder)
        sauvegarder_actifs()
        st.experimental_rerun()

# Function to delete sales and configuration files associated with an asset in a scenario
def supprimer_fichier_vente(nom, scenario_folder):
    file_paths = [
        os.path.join(scenario_folder, f"{nom}_ventes.csv"),
        os.path.join(scenario_folder, f"{nom}_config.csv")
    ]
    for path in file_paths:
        if os.path.exists(path):
            os.remove(path)

# Function to load the sales configuration of an asset
def charger_config_vente(nom_actif, nb_ventes, scenario_folder):
    file_path = os.path.join(scenario_folder, f"{nom_actif}_config.csv")
    if os.path.exists(file_path):
        config_df = pd.read_csv(file_path)
        ventes = config_df['Vente'].tolist()
        augmentations = config_df['Augmentation'].tolist()
    else:
        ventes = [0.0] * nb_ventes
        augmentations = [1.0] * nb_ventes
    return ventes, augmentations

# Function to save the sales configuration of an asset
def sauvegarder_config_vente(nom_actif, ventes, augmentations, scenario_folder):
    config_df = pd.DataFrame({
        'Vente': ventes,
        'Augmentation': augmentations
    })
    file_path = os.path.join(scenario_folder, f"{nom_actif}_config.csv")
    config_df.to_csv(file_path, index=False)

# Function to calculate the sales values for an asset and save
def calculer_valeurs_vente(nom_actif, ventes, augmentations, scenario_folder):
    actif = st.session_state['assets'][nom_actif]
    valeurs_vente = []
    valeurs_reste = []
    valeurs_unitaire = []
    vt = actif['prix'] * actif['quantite']
    vu = actif['prix']
    Vts = vt

    for i in range(actif['nb_ventes']):
        Vts *= augmentations[i]
        vu *= augmentations[i]
        valeur_vente = Vts * ventes[i]
        valeurs_vente.append(valeur_vente)
        Vts -= valeur_vente
        valeurs_reste.append(Vts)
        valeurs_unitaire.append(vu)

    result_df = pd.DataFrame({
        'Valeurs de Vente': valeurs_vente,
        'Valeurs Restantes': valeurs_reste,
        'Valeurs Unitaires': valeurs_unitaire
    })
    file_path = os.path.join(scenario_folder, f"{nom_actif}_ventes.csv")
    result_df.to_csv(file_path, index=False)
    total_ventes = sum(valeurs_vente)
    total_restes = valeurs_reste[-1] if valeurs_reste else 0

    sauvegarder_config_vente(nom_actif, ventes, augmentations, scenario_folder)  # Save the configuration
    return result_df, total_ventes, total_restes

# Main Streamlit application
def main():
    st.title("Simulateur de Vente")

    # Scenario selection
    select_scenario()

    if st.session_state['selected_scenario'] is None:
        st.info("Veuillez créer un nouveau scénario pour commencer.")
        return

    # Initialize SCENARIO_FOLDER
    SCENARIO_FOLDER = os.path.join(DATA_DIR, st.session_state['selected_scenario'])

    # Ensure the scenario folder exists
    os.makedirs(SCENARIO_FOLDER, exist_ok=True)

    # Initialize session state for assets
    if 'assets' not in st.session_state:
        st.session_state['assets'] = charger_actifs()

    afficher_donnees_sidebar()

    onglet1, onglet2, onglet3 = st.tabs(["Ajouter un Actif", "Modifier un Actif", "Supprimer un Actif"])

    with onglet1:
        st.header("Ajouter un Nouvel Actif")
        nom = st.text_input("Nom de l'actif")
        prix = st.number_input("Prix unitaire", min_value=0.0, step=0.000001, format="%.6f")
        quantite = st.number_input("Quantité", min_value=0.0, step=0.000001, format="%.6f")
        nb_ventes = st.number_input("Nombre d'itérations de vente", min_value=1, step=1, value=3)
        if st.button("Ajouter l'Actif", key="add_button"):
            ajouter_actif(nom, prix, quantite, nb_ventes)

    with onglet2:
        st.header("Modifier un Actif")
        if st.session_state['assets']:
            nom_actif = st.selectbox("Sélectionner un Actif", list(st.session_state['assets'].keys()), key="modify_select")
            if nom_actif:
                actif = st.session_state['assets'][nom_actif]
                prix = st.number_input("Prix unitaire", min_value=0.0, value=actif['prix'], step=0.000001, format="%.6f", key="modify_price")
                quantite = st.number_input("Quantité", min_value=0.0, value=actif['quantite'], step=0.000001, format="%.6f", key="modify_quantity")
                nb_ventes = st.number_input("Nombre d'itérations de vente", min_value=1, value=actif['nb_ventes'], step=1, key="modify_num_sells")
                if st.button("Modifier l'Actif", key="modify_button"):
                    modifier_actif(nom_actif, prix, quantite, nb_ventes)
        else:
            st.write("Aucun actif à modifier.")

    with onglet3:
        st.header("Supprimer un Actif")
        if st.session_state['assets']:
            nom_actif = st.selectbox("Sélectionner un Actif", list(st.session_state['assets'].keys()), key="delete_select")
            if nom_actif and st.button("Supprimer l'Actif", key="delete_button"):
                supprimer_actif(nom_actif)
        else:
            st.write("Aucun actif à supprimer.")

    # Sales calculation section
    st.header("Calculateur de Vente d'Actif")
    if st.session_state['assets']:
        actif_selectionne = st.selectbox("Choisir un actif pour les calculs de vente", list(st.session_state['assets'].keys()), key="calculator_select")
        if actif_selectionne:
            actif = st.session_state['assets'][actif_selectionne]
            ventes, augmentations = charger_config_vente(actif_selectionne, actif['nb_ventes'], SCENARIO_FOLDER)
            st.write(f"Entrez les ventes et augmentations pour chaque itération de vente de '{actif_selectionne}':")

            colonnes = st.columns(actif['nb_ventes'])
            for i, col in enumerate(colonnes):
                with col:
                    ventes[i] = st.number_input(f"Vente {i+1}", min_value=0.0, max_value=1.0, step=0.01, key=f"vente_{actif_selectionne}_{i}", value=ventes[i])
                    augmentations[i] = st.number_input(f"Augmentation de l'actif {i+1}", min_value=0.0, step=0.01, value=augmentations[i], key=f"augmentation_{actif_selectionne}_{i}")

            result_df, total_ventes, total_restes = calculer_valeurs_vente(actif_selectionne, ventes, augmentations, SCENARIO_FOLDER)

            st.subheader("Résumé des KPI")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total des Ventes (€)", f"{total_ventes:.2f}")
            with col2:
                st.metric("Total Restant (€)", f"{total_restes:.2f}")

            st.write("Tableau des Valeurs de Vente")
            st.dataframe(result_df)
    else:
        st.write("Aucun actif pour calculer les ventes.")

    # Global summary of assets
    st.header("Résumé Global des Actifs")
    total_ventes_all, total_restes_all = 0, 0

    for nom_actif in st.session_state['assets']:
        file_path = os.path.join(SCENARIO_FOLDER, f"{nom_actif}_ventes.csv")
        if os.path.exists(file_path):
            ventes_df = pd.read_csv(file_path)
            total_ventes_all += ventes_df['Valeurs de Vente'].sum()
            total_restes_all += ventes_df['Valeurs Restantes'].iloc[-1]  # Last remaining value per asset

    if st.session_state['assets']:
        # Horizontal bar chart for global totals
        fig, ax = plt.subplots(figsize=(8, 2))
        categories = ['Total Valeurs de Vente', 'Total Valeurs Restantes']
        totals = [total_ventes_all, total_restes_all]
        ax.barh(categories, totals, color=['#4CAF50', '#FF9800'], edgecolor='black', alpha=0.8)
        ax.set_xlabel("Total (€)")
        ax.set_title("Résumé Global des Actifs")
        st.pyplot(fig)
    else:
        st.write("Aucun actif pour afficher le résumé global.")

if __name__ == '__main__':
    main()
