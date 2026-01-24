import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.optimize import minimize

# =========================================================
# 🔒 MODULE SÉCURITÉ (COFFRE-FORT)
# =========================================================

# 1. Récupération intelligente du mot de passe
try:
    # Sur le Serveur : on lit le secret caché
    MOT_DE_PASSE = st.secrets["PASSWORD"]
except FileNotFoundError:
    # Sur ton PC (si pas de fichier secrets) : mot de passe par défaut pour tester
    MOT_DE_PASSE = "atelier123"

def check_password():
    """Gère l'écran de connexion"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.set_page_config(page_title="Accès Restreint", layout="centered")
        st.title("🔒 Accès Sécurisé")
        st.markdown("### Assistant de Cintrage")
        st.info("Veuillez vous identifier pour accéder à l'outil.")
        
        pwd = st.text_input("Mot de passe", type="password")
        
        if st.button("Se Connecter", type="primary"):
            if pwd == MOT_DE_PASSE:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect.")
        return False
    return True

# Si l'utilisateur n'est pas connecté, on arrête tout ici.
if not check_password():
    st.stop()

# =========================================================
# 🏭 LE LOGICIEL COMMENCE ICI (Une fois connecté)
# =========================================================

# --- CONFIGURATION ---
# Note : set_page_config est déjà appelé dans check_password si non connecté, 
# mais on peut le rappeler ici pour changer le layout en "wide"
st.set_page_config(page_title="Cintrage V44 - Secure", layout="wide")
st.title("🏭 Assistant de Cintrage : V44 (Sécurisé)")
st.caption("Connecté en mode sécurisé.")
st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Paramètres")
    target_val = st.number_input("Cible Rayon/Dév (mm)", value=500.0)
    
    # Sélecteur simple
    nb_rayons = st.selectbox("Nombre de Rayons", options=[3, 4])
    
    st.info(f"🚀 Moteur : {nb_rayons} Arcs Indépendants.\n(Mode 4 arcs : 5 tentatives lancées pour garantir la précision)")
    
    st.markdown("---")
    if st.button("🔒 Déconnexion"):
        st.session_state.authenticated = False
        st.rerun()

# --- DONNÉES ---
col_input, col_graph = st.columns([1, 2])

with col_input:
    st.subheader("📍 Points Relevés")
    # Données Grand Profil
    default_data = pd.DataFrame([
        {"X (mm)": 0.0,    "Y (mm)": 0.0},
        {"X (mm)": 200.0,  "Y (mm)": 390.0},
        {"X (mm)": 400.0,  "Y (mm)": 529.0},
        {"X (mm)": 600.0,  "Y (mm)": 632.0},
        {"X (mm)": 800.0,  "Y (mm)": 706.0},
        {"X (mm)": 1000.0, "Y (mm)": 755.0},
        {"X (mm)": 1200.0, "Y (mm)": 780.0},
        {"X (mm)": 1400.0, "Y (mm)": 782.0},
        {"X (mm)": 1600.0, "Y (mm)": 762.0},
        {"X (mm)": 1800.0, "Y (mm)": 719.0},
        {"X (mm)": 2000.0, "Y (mm)": 651.0},
        {"X (mm)": 2200.0, "Y (mm)": 554.0},
        {"X (mm)": 2445.0, "Y (mm)": 389.0},
        {"X (mm)": 2645.0, "Y (mm)": 0.0}
    ])
    edited_df = st.data_editor(default_data, num_rows="dynamic", height=450)
    run_calc = st.button("LANCER LE CALCUL", type="primary", use_container_width=True)

# =========================================================
# MOTEUR UNIFIÉ (3 ou 4 ARCS)
# =========================================================
def solve_universal_engine(pts_x, pts_y, W_total, target_min, num_arcs):
    
    # --- GÉNÉRATEUR GÉOMÉTRIQUE UNIVERSEL ---
    def build_curve_generic(x_vals, params):
        # params contient : alpha, puis (R, th) pour chaque arc sauf le dernier th
        # Structure 3 arcs: [alpha, R1, th1, R2, th2, R3]
        # Structure 4 arcs: [alpha, R1, th1, R2, th2, R3, th3, R4]
        
        alpha = params[0]
        Rs = []
        ths = []
        
        # Extraction dynamique des variables
        if num_arcs == 3:
            Rs = [params[1], params[3], params[5]]
            ths = [params[2], params[4]]
        elif num_arcs == 4:
            Rs = [params[1], params[3], params[5], params[7]]
            ths = [params[2], params[4], params[6]]
            
        # Calcul des Centres (C) et Transitions (T)
        Cs = [] # [(Cx, Cy), ...]
        Ts = [] # [(Tx, Ty), ...]
        
        # C1
        C1x = Rs[0] * np.sin(alpha)
        C1y = -Rs[0] * np.cos(alpha)
        Cs.append((C1x, C1y))
        
        current_phi_end = alpha + np.pi/2 - ths[0]
        
        # T1
        T1x = C1x + Rs[0] * np.cos(current_phi_end)
        T1y = C1y + Rs[0] * np.sin(current_phi_end)
        Ts.append((T1x, T1y))
        
        # Boucle pour les arcs intermédiaires
        for i in range(1, num_arcs-1):
            # Ci (Centre actuel basé sur T précédent)
            prev_Tx, prev_Ty = Ts[-1]
            prev_R = Rs[i]
            
            Cix = prev_Tx - prev_R * np.cos(current_phi_end)
            Ciy = prev_Ty - prev_R * np.sin(current_phi_end)
            Cs.append((Cix, Ciy))
            
            # Ti
            current_phi_end -= ths[i]
            Tix = Cix + prev_R * np.cos(current_phi_end)
            Tiy = Ciy + prev_R * np.sin(current_phi_end)
            Ts.append((Tix, Tiy))
            
        # Dernier Centre (Cn)
        last_Tx, last_Ty = Ts[-1]
        last_R = Rs[-1]
        Cnx = last_Tx - last_R * np.cos(current_phi_end)
        Cny = last_Ty - last_R * np.sin(current_phi_end)
        Cs.append((Cnx, Cny))
        
        # Génération des points Y
        y_res = np.zeros_like(x_vals)
        transitions_x = [t[0] for t in Ts]
        
        for i, x in enumerate(x_vals):
            val = 0
            arc_idx = 0
            # Trouver dans quel arc on se trouve
            for k, tx in enumerate(transitions_x):
                if x <= tx:
                    arc_idx = k
                    break
                else:
                    arc_idx = k + 1
            
            # Sécurité index
            if arc_idx >= num_arcs: arc_idx = num_arcs - 1
            
            # Calcul hauteur cercle
            Cx, Cy = Cs[arc_idx]
            R = Rs[arc_idx]
            
            if abs(x - Cx) < R:
                val = Cy + np.sqrt(max(0, R**2 - (x - Cx)**2))
            else:
                val = 0 # Erreur math, shouldn't happen
                
            y_res[i] = max(0, val)
            
        return y_res, transitions_x, Rs, ths

    # --- LE JUGE ---
    def objective(params):
        # 1. Check Crash
        if params[0] < 0.1 or params[0] > 1.6: return 1e12 # Alpha
        # Check Rayons (indices impairs)
        for i in range(1, len(params), 2):
            if params[i] < 50: return 1e12
        # Check Angles (indices pairs à partir de 2)
        for i in range(2, len(params)-1, 2):
            if params[i] < 0.05: return 1e12
            
        y_calc, trans, Rs, ths = build_curve_generic(pts_x, params)
        
        # 2. Précision (Priorité absolue)
        mse = np.mean((y_calc - pts_y)**2)
        score_precision = mse * 100000
        
        # 3. Ordre Transitions
        if any(t <= 0 for t in trans): return 1e12
        if any(trans[i] >= trans[i+1] for i in range(len(trans)-1)): return 1e12
        if trans[-1] >= W_total: return 1e12
        
        # 4. Longueur (Soft constraint)
        pen_len = 0
        # Calcul longueurs connues
        for r, th in zip(Rs[:-1], ths):
            if r*th < target_min: pen_len += (target_min - r*th)**2 * 100
        
        # 5. Fermeture
        y_end, _, _, _ = build_curve_generic([W_total], params)
        pen_close = (y_end[0] - 0)**2 * 1000
        
        return score_precision + pen_len + pen_close

    # --- MULTI-START (Force Brute) ---
    best_res = None
    best_score = float('inf')
    
    # On définit 5 points de départ différents pour "secouer" le solveur
    # Format: [alpha, R1, th1, R2, th2, (R3, th3)... Rn]
    
    init_configs = []
    
    # Estimation angle départ
    ang_guess = 1.0
    if len(pts_x)>1: ang_guess = np.arctan((pts_y[1]-pts_y[0])/(pts_x[1]-pts_x[0]))
    
    R_base = W_total / 2
    
    if num_arcs == 3:
        # Configs pour 3 arcs
        init_configs.append([ang_guess, R_base, 0.5, R_base*2, 0.5, R_base])
    else:
        # Configs pour 4 arcs (On varie les rayons initiaux pour explorer)
        # 1. Standard
        init_configs.append([ang_guess, R_base, 0.4, R_base, 0.4, R_base, 0.4, R_base])
        # 2. Grands Rayons Extérieurs
        init_configs.append([ang_guess, R_base*1.5, 0.3, R_base, 0.5, R_base, 0.5, R_base*1.5])
        # 3. Grands Rayons Intérieurs
        init_configs.append([ang_guess, R_base, 0.5, R_base*2, 0.3, R_base*2, 0.3, R_base])
        # 4. Asymétrique (Fort à gauche)
        init_configs.append([ang_guess, R_base*2, 0.6, R_base, 0.3, R_base, 0.3, R_base])
        # 5. Asymétrique (Fort à droite)
        init_configs.append([ang_guess, R_base, 0.3, R_base, 0.3, R_base, 0.6, R_base*2])

    # BOUCLE D'OPTIMISATION
    for idx, x0 in enumerate(init_configs):
        # Bornes génériques
        bnds = []
        for i in range(len(x0)):
            if i == 0: bnds.append((0.1, 1.6)) # Alpha
            elif i % 2 != 0: bnds.append((50, W_total*10)) # Rayons
            else: bnds.append((0.05, 2.0)) # Angles
            
        try:
            res = minimize(objective, x0, bounds=bnds, method='L-BFGS-B', options={'maxiter': 3000})
            if res.fun < best_score:
                best_score = res.fun
                best_res = res
        except:
            continue # Si une config plante, on passe à la suivante

    # Récupération du gagnant
    p = best_res.x
    x_plot = np.linspace(0, W_total, 800)
    y_plot, trans, Rs, ths = build_curve_generic(x_plot, p)
    
    # Calcul L final (Géométrique)
    mask_last = x_plot > trans[-1]
    if np.any(mask_last):
        L_last = np.sum(np.sqrt(np.diff(x_plot[mask_last])**2 + np.diff(y_plot[mask_last])**2))
    else: L_last = 0
    
    # Construction tableau final
    Ls = []
    for r, th in zip(Rs[:-1], ths):
        Ls.append(r * th)
    Ls.append(L_last)
    
    # Re-calcul précision exacte
    y_check, _, _, _ = build_curve_generic(pts_x, p)
    err = np.mean(np.abs(y_check - pts_y))
    
    return {
        "x_plot": x_plot, "y_plot": y_plot,
        "trans": trans, "Rs": Rs, "Ls": Ls,
        "err": err, "width": W_total,
        "alpha": np.degrees(p[0])
    }

# --- AFFICHAGE ---
if run_calc:
    df = edited_df.dropna().astype(float).sort_values("X (mm)")
    all_pts = df[["X (mm)", "Y (mm)"]].values
    W_total = np.max(all_pts[:,0])
    
    with st.spinner(f"Calcul Intensif ({nb_rayons} Arcs)..."):
        res = solve_universal_engine(all_pts[:,0], all_pts[:,1], W_total, target_val, nb_rayons)
        
        # --- RÉSULTATS ---
        col1, col2, col3 = st.columns(3)
        col1.metric("Précision (Écart)", f"{res['err']:.1f} mm")
        col2.metric("Angle Départ", f"{res['alpha']:.1f}°")
        col3.metric("Largeur", f"{res['width']:.0f} mm")
        
        # Tableau
        data_res = []
        for i in range(nb_rayons):
            data_res.append({
                "Zone": f"Arc {i+1}", 
                "Rayon": res["Rs"][i], 
                "Dév": res["Ls"][i]
            })
            
        final_df = pd.DataFrame(data_res)
        
        def color_status(row):
            if row["Dév"] >= target_val: return "✅ OK"
            elif row["Dév"] >= target_val * 0.8: return "⚠️ Court"
            else: return "❌ Trop Court"
            
        final_df["État"] = final_df.apply(color_status, axis=1)
        st.dataframe(final_df.style.format({"Rayon": "{:.1f} mm", "Dév": "{:.1f} mm"}), use_container_width=True)
        
        # Graphique
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=all_pts[:,0], y=all_pts[:,1], mode='markers', name='Points', marker=dict(color='red', size=12, symbol='x')))
        
        colors = ['#ff9f1c', '#2ec4b6', '#9d4edd', '#ef476f', '#118ab2']
        x_plot = res["x_plot"]
        y_plot = res["y_plot"]
        trans = res["trans"]
        boundaries = [0] + trans + [W_total]
        
        for i in range(nb_rayons):
            mask = (x_plot >= boundaries[i]) & (x_plot <= boundaries[i+1])
            fig.add_trace(go.Scatter(
                x=x_plot[mask], y=y_plot[mask], 
                mode='lines', name=f'Arc {i+1}', 
                line=dict(color=colors[i%5], width=5)
            ))
            if i < len(trans):
                fig.add_vline(x=trans[i], line_dash="dot", annotation_text=f"T{i+1}")
        
        fig.update_layout(title=f"Optimisation {nb_rayons} Arcs", height=600, yaxis=dict(scaleanchor="x", scaleratio=1))
        st.plotly_chart(fig, use_container_width=True)