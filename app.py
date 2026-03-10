import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.optimize import minimize, differential_evolution
import io
import json
from datetime import datetime

# =========================================================
# 🔒 SÉCURITÉ
# =========================================================
try:
    MOT_DE_PASSE = st.secrets["PASSWORD"]
except (FileNotFoundError, KeyError):
    MOT_DE_PASSE = "atelier123"

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.set_page_config(page_title="Accès Restreint", layout="centered", page_icon="🔒")
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow:wght@300;600&display=swap');
        body { background: #0d0d0d; }
        .stApp { background: #0d0d0d; }
        h1, h2, h3, p, label { color: #e8e0d0 !important; font-family: 'Barlow', sans-serif; }
        .stTextInput input { background: #1a1a1a; color: #f0c040; border: 1px solid #f0c040; font-family: 'Share Tech Mono', monospace; }
        .stButton>button { background: #f0c040; color: #0d0d0d; font-family: 'Barlow', sans-serif; font-weight: 600; border: none; border-radius: 2px; padding: 0.6rem 2rem; }
        </style>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("## 🔒 ASSISTANT CINTRAGE")
            st.markdown("*Identifiez-vous pour accéder à l'outil*")
            pwd = st.text_input("Mot de passe", type="password", label_visibility="collapsed", placeholder="Mot de passe...")
            if st.button("→ CONNEXION", use_container_width=True):
                if pwd == MOT_DE_PASSE:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Mot de passe incorrect.")
        return False
    return True

if not check_password():
    st.stop()

# =========================================================
# 🎨 STYLES GLOBAUX
# =========================================================
st.set_page_config(
    page_title="CintragePro V5.0",
    layout="wide",
    page_icon="🏭",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow+Condensed:wght@300;400;600;700&family=Barlow:wght@300;400;600&display=swap');

body, .stApp { background: #111318; }

/* Titres */
h1 { font-family: 'Barlow Condensed', sans-serif; font-weight: 700; letter-spacing: 2px; color: #f0c040 !important; font-size: 2rem !important; }
h2, h3 { font-family: 'Barlow Condensed', sans-serif; font-weight: 600; color: #e8e0d0 !important; letter-spacing: 1px; }
p, label, .stMarkdown { font-family: 'Barlow', sans-serif; color: #a0a8b8 !important; }

/* Sidebar */
[data-testid="stSidebar"] { background: #0d0f14 !important; border-right: 1px solid #2a2d35; }
[data-testid="stSidebar"] * { color: #e8e0d0 !important; font-family: 'Barlow', sans-serif; }
[data-testid="stSidebar"] h2 { color: #f0c040 !important; font-family: 'Barlow Condensed', sans-serif; letter-spacing: 2px; font-size: 1.1rem !important; }

/* Inputs */
.stNumberInput input, .stSelectbox select, .stTextInput input {
    background: #1a1d24 !important; color: #f0c040 !important;
    border: 1px solid #2a2d35 !important; border-radius: 2px !important;
    font-family: 'Share Tech Mono', monospace !important;
}
.stSelectbox > div > div { background: #1a1d24 !important; border: 1px solid #2a2d35 !important; }

/* Bouton principal */
.stButton>button[kind="primary"] {
    background: linear-gradient(135deg, #f0c040, #e8a020) !important;
    color: #0d0d0d !important; font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important; letter-spacing: 2px !important;
    border: none !important; border-radius: 2px !important;
    font-size: 1rem !important;
}
.stButton>button { 
    background: #1a1d24 !important; color: #e8e0d0 !important;
    border: 1px solid #2a2d35 !important; border-radius: 2px !important;
    font-family: 'Barlow Condensed', sans-serif !important;
}

/* Métriques */
[data-testid="stMetric"] { background: #1a1d24; border: 1px solid #2a2d35; border-radius: 4px; padding: 0.8rem 1rem; }
[data-testid="stMetricLabel"] { color: #a0a8b8 !important; font-family: 'Barlow', sans-serif !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 1px; }
[data-testid="stMetricValue"] { color: #f0c040 !important; font-family: 'Share Tech Mono', monospace !important; }

/* DataEditor */
.stDataFrame { border: 1px solid #2a2d35 !important; }

/* Tabs */
.stTabs [data-baseweb="tab"] { background: #1a1d24; color: #a0a8b8 !important; font-family: 'Barlow Condensed', sans-serif; letter-spacing: 1px; border-bottom: 2px solid transparent; }
.stTabs [aria-selected="true"] { color: #f0c040 !important; border-bottom: 2px solid #f0c040 !important; }

/* Séparateurs */
hr { border-color: #2a2d35 !important; }

/* Alertes */
.stSuccess { background: #0d2010 !important; border: 1px solid #2a6030 !important; color: #50d080 !important; }
.stWarning { background: #201500 !important; border: 1px solid #604010 !important; color: #f0a040 !important; }
.stError { background: #200d0d !important; border: 1px solid #602020 !important; color: #e05050 !important; }
.stInfo { background: #0d1520 !important; border: 1px solid #204060 !important; color: #6090d0 !important; }

/* Badge status */
.badge-ok { color: #50d080; font-weight: 600; }
.badge-warn { color: #f0a040; font-weight: 600; }
.badge-err { color: #e05050; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 📦 SESSION STATE : HISTORIQUE & PROFILS
# =========================================================
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "compare_result" not in st.session_state:
    st.session_state.compare_result = None

# =========================================================
# 📚 PROFILS PRÉDÉFINIS
# =========================================================
PROFILS = {
    "Grand Profil (défaut)": [
        [0.0, 0.0], [200.0, 390.0], [400.0, 529.0], [600.0, 632.0],
        [800.0, 706.0], [1000.0, 755.0], [1200.0, 780.0], [1400.0, 782.0],
        [1600.0, 762.0], [1800.0, 719.0], [2000.0, 651.0], [2200.0, 554.0],
        [2445.0, 389.0], [2645.0, 0.0]
    ],
    "Profil Petit": [
        [0.0, 0.0], [100.0, 150.0], [200.0, 210.0], [300.0, 240.0],
        [400.0, 250.0], [500.0, 240.0], [600.0, 210.0], [700.0, 150.0],
        [800.0, 0.0]
    ],
    "Profil Asymétrique": [
        [0.0, 0.0], [150.0, 280.0], [350.0, 430.0], [600.0, 520.0],
        [900.0, 490.0], [1100.0, 420.0], [1250.0, 310.0], [1400.0, 0.0]
    ],
    "Personnalisé": None
}

# =========================================================
# 🔧 MOTEUR DE CALCUL UNIFIÉ V5
# =========================================================
def solve_engine_v5(pts_x, pts_y, W_total, target_min, num_arcs, symmetric=False, weights=None):
    """
    Moteur V5 :
    - Différential Evolution (global) + L-BFGS-B (local) en 2 phases
    - np.searchsorted vectorisé
    - Symétrie optionnelle
    - Pondération par point
    - Longueur développée analytique pour tous les arcs
    """
    
    if weights is None:
        weights = np.ones(len(pts_x))
    weights = weights / weights.sum()

    def build_curve(x_vals, params):
        """Construction vectorisée de la courbe multi-arcs."""
        alpha = params[0]
        
        # Extraction R et theta selon num_arcs
        if num_arcs == 3:
            Rs = [params[1], params[3], params[5]]
            ths = [params[2], params[4]]
        elif num_arcs == 4:
            Rs = [params[1], params[3], params[5], params[7]]
            ths = [params[2], params[4], params[6]]
        elif num_arcs == 5:
            Rs = [params[1], params[3], params[5], params[7], params[9]]
            ths = [params[2], params[4], params[6], params[8]]
        
        # Si symétrie : forcer R et theta symétriques
        if symmetric:
            n = num_arcs
            for i in range(n // 2):
                Rs[n-1-i] = Rs[i]
            for i in range((n-1) // 2):
                ths[n-2-i] = ths[i]

        # Calcul des centres et transitions
        Cs = []
        Ts = []
        
        C1x = Rs[0] * np.sin(alpha)
        C1y = -Rs[0] * np.cos(alpha)
        Cs.append((C1x, C1y))
        
        phi = alpha + np.pi/2 - ths[0]
        T1x = C1x + Rs[0] * np.cos(phi)
        T1y = C1y + Rs[0] * np.sin(phi)
        Ts.append((T1x, T1y))
        
        for i in range(1, num_arcs - 1):
            Cix = Ts[-1][0] - Rs[i] * np.cos(phi)
            Ciy = Ts[-1][1] - Rs[i] * np.sin(phi)
            Cs.append((Cix, Ciy))
            if i < len(ths):
                phi -= ths[i]
            Tix = Cix + Rs[i] * np.cos(phi)
            Tiy = Ciy + Rs[i] * np.sin(phi)
            Ts.append((Tix, Tiy))
        
        last_R = Rs[-1]
        Cnx = Ts[-1][0] - last_R * np.cos(phi)
        Cny = Ts[-1][1] - last_R * np.sin(phi)
        Cs.append((Cnx, Cny))
        
        # Vectorisé : np.searchsorted remplace la boucle for
        transitions_x = np.array([t[0] for t in Ts])
        arc_indices = np.searchsorted(transitions_x, x_vals, side='right')
        arc_indices = np.clip(arc_indices, 0, num_arcs - 1)
        
        y_res = np.zeros_like(x_vals, dtype=float)
        for arc_idx in range(num_arcs):
            mask = arc_indices == arc_idx
            if not np.any(mask):
                continue
            Cx, Cy = Cs[arc_idx]
            R = Rs[arc_idx]
            dx = x_vals[mask] - Cx
            discriminant = np.maximum(0, R**2 - dx**2)
            y_res[mask] = Cy + np.sqrt(discriminant)
        
        y_res = np.maximum(0, y_res)
        return y_res, transitions_x.tolist(), Rs, ths

    def objective(params):
        # Validation des bornes
        if params[0] < 0.05 or params[0] > 1.65:
            return 1e12
        for i in range(1, len(params)):
            if i % 2 == 1 and params[i] < 50:  # Rayon
                return 1e12
            if i % 2 == 0 and params[i] < 0.03:  # Angle
                return 1e12
        
        try:
            y_calc, trans, Rs, ths = build_curve(pts_x, params)
        except Exception:
            return 1e12
        
        # Ordre des transitions
        if any(t <= 0 for t in trans):
            return 1e12
        for i in range(len(trans) - 1):
            if trans[i] >= trans[i+1]:
                return 1e12
        if trans[-1] >= W_total:
            return 1e12
        
        # Score précision pondéré
        errors = (y_calc - pts_y) ** 2
        score_precision = np.sum(weights * errors) * 100000

        # Pénalité longueurs développées
        pen_len = 0
        for r, th in zip(Rs, ths):
            L = r * th
            if L < target_min:
                pen_len += ((target_min - L) / target_min) ** 2 * 5000
        
        # Pénalité fermeture (Y final = 0)
        y_end, _, _, _ = build_curve(np.array([W_total]), params)
        pen_close = (y_end[0] ** 2) * 1000
        
        # Pénalité continuité de pente aux transitions (C1)
        pen_c1 = 0
        for k, tx in enumerate(trans):
            x_left = np.array([tx - 0.1])
            x_right = np.array([tx + 0.1])
            y_l, _, _, _ = build_curve(x_left, params)
            y_r, _, _, _ = build_curve(x_right, params)
            slope_diff = abs((y_r[0] - y_l[0]) / 0.2)  # Approx dérivée
            pen_c1 += slope_diff * 0.1
        
        return score_precision + pen_len + pen_close + pen_c1

    # Bornes génériques
    def make_bounds(n_params):
        bnds = []
        for i in range(n_params):
            if i == 0:
                bnds.append((0.05, 1.65))       # alpha
            elif i % 2 == 1:
                bnds.append((100, W_total * 10)) # Rayon
            else:
                bnds.append((0.05, 1.8))         # Angle
        return bnds

    # Structure des paramètres selon num_arcs
    n_params = 1 + num_arcs * 2 - 1  # alpha + (R,th) * (n-1) + Rn
    bnds = make_bounds(n_params)
    
    ang_guess = 1.0
    if len(pts_x) > 1:
        ang_guess = np.clip(np.arctan2(pts_y[1] - pts_y[0], pts_x[1] - pts_x[0]), 0.1, 1.5)
    R_base = W_total / 2

    # ─── PHASE 1 : Differential Evolution (recherche globale) ───
    with st.spinner("⚡ Phase 1 : Recherche globale (Differential Evolution)..."):
        de_result = differential_evolution(
            objective,
            bounds=bnds,
            maxiter=600,
            tol=1e-9,
            seed=42,
            workers=1,
            mutation=(0.5, 1.2),
            recombination=0.85,
            popsize=18,
            init='latinhypercube',
            polish=False
        )

    # ─── PHASE 2 : L-BFGS-B (affinage local) ───
    with st.spinner("🔬 Phase 2 : Affinage local (L-BFGS-B)..."):
        fine_result = minimize(
            objective,
            de_result.x,
            bounds=bnds,
            method='L-BFGS-B',
            options={'maxiter': 8000, 'ftol': 1e-14, 'gtol': 1e-10}
        )
    
    best_params = fine_result.x if fine_result.fun < de_result.fun else de_result.x
    best_score = min(fine_result.fun, de_result.fun)

    # ─── RÉSULTATS FINAUX ───
    x_plot = np.linspace(0, W_total, 1200)
    y_plot, trans, Rs, ths = build_curve(x_plot, best_params)

    # Longueurs développées analytiques pour tous les arcs
    Ls = [r * th for r, th in zip(Rs, ths)]
    # Dernier arc : intégration numérique de précision
    boundaries = [0.0] + trans + [float(W_total)]
    mask_last = (x_plot >= boundaries[-2]) & (x_plot <= boundaries[-1])
    if np.any(mask_last):
        x_seg = x_plot[mask_last]
        y_seg = y_plot[mask_last]
        L_last = float(np.sum(np.sqrt(np.diff(x_seg)**2 + np.diff(y_seg)**2)))
    else:
        L_last = Rs[-1] * 0.5
    Ls.append(L_last)

    # Erreur point par point
    y_check, _, _, _ = build_curve(pts_x, best_params)
    err_pts = np.abs(y_check - pts_y)
    err_mean = float(np.mean(err_pts))
    err_max  = float(np.max(err_pts))

    # Score de confiance (0-100)
    confidence = max(0, min(100, int(100 - best_score / 1000)))

    return {
        "x_plot": x_plot,
        "y_plot": y_plot,
        "trans": trans,
        "Rs": Rs,
        "Ls": Ls,
        "ths": ths,
        "err_mean": err_mean,
        "err_max": err_max,
        "err_pts": err_pts.tolist(),
        "width": float(W_total),
        "alpha": float(np.degrees(best_params[0])),
        "confidence": confidence,
        "de_score": float(de_result.fun),
        "fine_score": float(fine_result.fun),
        "params": best_params.tolist(),
        "pts_x": pts_x.tolist(),
        "pts_y": pts_y.tolist(),
        "num_arcs": num_arcs,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "date": datetime.now().strftime("%d/%m/%Y")
    }


# =========================================================
# 📊 FONCTIONS D'AFFICHAGE
# =========================================================
COLORS = ['#f0c040', '#40c0f0', '#f04090', '#40f090', '#c040f0']

def make_main_chart(res, compare_res=None, pts_x=None, pts_y=None):
    fig = go.Figure()
    
    x_plot = np.array(res["x_plot"])
    y_plot = np.array(res["y_plot"])
    trans = res["trans"]
    num_arcs = res["num_arcs"]
    W = res["width"]
    boundaries = [0.0] + trans + [W]
    
    # Zones de fond par arc
    for i in range(num_arcs):
        fig.add_vrect(
            x0=boundaries[i], x1=boundaries[i+1],
            fillcolor=COLORS[i % 5], opacity=0.03,
            layer="below", line_width=0
        )
    
    # Courbe comparaison (si présente)
    if compare_res:
        fig.add_trace(go.Scatter(
            x=compare_res["x_plot"], y=compare_res["y_plot"],
            mode='lines', name='Comparaison',
            line=dict(color='#505060', width=2, dash='dash'),
            opacity=0.6
        ))
    
    # Courbes par arc
    for i in range(num_arcs):
        mask = (x_plot >= boundaries[i]) & (x_plot <= boundaries[i+1])
        fig.add_trace(go.Scatter(
            x=x_plot[mask], y=y_plot[mask],
            mode='lines', name=f'Arc {i+1} — R={res["Rs"][i]:.0f}mm',
            line=dict(color=COLORS[i % 5], width=4)
        ))
    
    # Lignes de transition
    for i, tx in enumerate(trans):
        fig.add_vline(
            x=tx, line_dash="dot", line_color="#505060", line_width=1,
            annotation_text=f"T{i+1} {tx:.0f}mm",
            annotation_font_color="#a0a8b8", annotation_font_size=11
        )
    
    # Points relevés
    if pts_x is not None:
        fig.add_trace(go.Scatter(
            x=pts_x, y=pts_y,
            mode='markers', name='Points relevés',
            marker=dict(color='#ffffff', size=10, symbol='x', line=dict(width=2))
        ))

    fig.update_layout(
        paper_bgcolor='#111318', plot_bgcolor='#151820',
        font=dict(family="Barlow, sans-serif", color='#a0a8b8'),
        legend=dict(
            bgcolor='#1a1d24', bordercolor='#2a2d35', borderwidth=1,
            font=dict(size=11)
        ),
        xaxis=dict(
            gridcolor='#1e2128', zerolinecolor='#2a2d35',
            title="X (mm)", title_font_color='#a0a8b8',
            tickfont_color='#a0a8b8'
        ),
        yaxis=dict(
            gridcolor='#1e2128', zerolinecolor='#2a2d35',
            scaleanchor="x", scaleratio=1,
            title="Y (mm)", title_font_color='#a0a8b8',
            tickfont_color='#a0a8b8'
        ),
        height=500,
        margin=dict(l=40, r=40, t=40, b=40),
    )
    return fig


def make_error_chart(res):
    """Graphique d'erreur point par point."""
    pts_x = res["pts_x"]
    err_pts = res["err_pts"]
    
    colors = []
    for e in err_pts:
        if e < 5: colors.append('#40f090')
        elif e < 15: colors.append('#f0c040')
        else: colors.append('#f04050')
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=pts_x, y=err_pts,
        marker_color=colors,
        name="Erreur (mm)",
        text=[f"{e:.1f}" for e in err_pts],
        textposition='outside',
        textfont_color='#a0a8b8'
    ))
    fig.add_hline(y=5, line_dash="dot", line_color="#40f090", annotation_text="5mm")
    fig.add_hline(y=15, line_dash="dot", line_color="#f0c040", annotation_text="15mm")
    fig.update_layout(
        paper_bgcolor='#111318', plot_bgcolor='#151820',
        font=dict(family="Barlow", color='#a0a8b8'),
        xaxis=dict(gridcolor='#1e2128', title="X (mm)", tickfont_color='#a0a8b8'),
        yaxis=dict(gridcolor='#1e2128', title="Erreur (mm)", tickfont_color='#a0a8b8'),
        height=300,
        margin=dict(l=40, r=40, t=30, b=40),
        showlegend=False
    )
    return fig


# =========================================================
# 📤 EXPORT
# =========================================================
def export_excel(res, target_val, num_arcs):
    """Génère un rapport Excel."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Feuille Résultats
        rows = []
        for i in range(num_arcs):
            L = res["Ls"][i]
            R = res["Rs"][i]
            status = "OK" if L >= target_val else ("Court" if L >= target_val * 0.8 else "Trop Court")
            rows.append({
                "Zone": f"Arc {i+1}",
                "Rayon (mm)": round(R, 1),
                "Dév. L (mm)": round(L, 1),
                "Cible (mm)": target_val,
                "État": status
            })
        df_res = pd.DataFrame(rows)
        df_res.to_excel(writer, sheet_name="Résultats", index=False)
        
        # Feuille Points
        df_pts = pd.DataFrame({"X (mm)": res["pts_x"], "Y (mm)": res["pts_y"], "Erreur (mm)": [round(e,2) for e in res["err_pts"]]})
        df_pts.to_excel(writer, sheet_name="Points", index=False)
        
        # Feuille Infos
        df_info = pd.DataFrame({
            "Paramètre": ["Date", "Nombre d'arcs", "Angle départ (°)", "Largeur (mm)", "Erreur moy (mm)", "Erreur max (mm)", "Confiance (%)"],
            "Valeur": [res["date"], num_arcs, round(res["alpha"], 2), res["width"], round(res["err_mean"], 2), round(res["err_max"], 2), res["confidence"]]
        })
        df_info.to_excel(writer, sheet_name="Infos", index=False)
    
    return output.getvalue()


def export_json(res):
    """Export JSON pour import ultérieur."""
    data = {
        "version": "5.0",
        "date": res["date"],
        "pts_x": res["pts_x"],
        "pts_y": res["pts_y"],
        "Rs": [round(r,2) for r in res["Rs"]],
        "Ls": [round(l,2) for l in res["Ls"]],
        "alpha": round(res["alpha"],3),
        "trans": [round(t,2) for t in res["trans"]],
        "err_mean": round(res["err_mean"],3),
        "confidence": res["confidence"]
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


# =========================================================
# 🖥️ INTERFACE PRINCIPALE
# =========================================================

# ─── TITRE ───
st.markdown("## 🏭 CINTRAGE PRO — V5.0")
st.caption(f"Moteur Différential Evolution + L-BFGS-B · {datetime.now().strftime('%d/%m/%Y')}")
st.markdown("---")

# ─── SIDEBAR ───
with st.sidebar:
    st.markdown("### ⚙️ PARAMÈTRES")
    
    target_val = st.number_input("Cible Dév. min (mm)", value=500.0, step=10.0)
    nb_rayons = st.selectbox("Nombre d'arcs", options=[3, 4, 5])
    
    st.markdown("---")
    st.markdown("### 🔧 OPTIONS AVANCÉES")
    
    symmetric = st.checkbox("Profil symétrique", value=False,
                             help="Force R1=Rn, θ1=θn-1... Réduit l'espace de recherche et améliore la convergence pour les profils symétriques.")
    
    st.markdown("**Pondération des points :**")
    weight_mode = st.radio(
        "Mode de pondération",
        ["Uniforme", "Bords renforcés", "Manuel"],
        help="Bords renforcés : x4 aux extrémités. Manuel : modifiez le tableau de points.",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 📚 PROFIL PRÉDÉFINI")
    profil_choice = st.selectbox("Charger un profil", list(PROFILS.keys()))
    
    st.markdown("---")
    if st.button("🔒 Déconnexion", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    
    # Indicateur de confiance du dernier calcul
    if st.session_state.last_result:
        r = st.session_state.last_result
        conf = r["confidence"]
        col_conf = "#40f090" if conf > 70 else ("#f0c040" if conf > 40 else "#f04050")
        st.markdown(f"""
        <div style='background:#1a1d24;border:1px solid #2a2d35;border-radius:4px;padding:1rem;margin-top:1rem;'>
        <div style='color:#a0a8b8;font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;font-family:Barlow,sans-serif;'>Dernier calcul</div>
        <div style='color:{col_conf};font-size:1.8rem;font-family:Share Tech Mono,monospace;'>{conf}%</div>
        <div style='color:#a0a8b8;font-size:0.75rem;font-family:Barlow,sans-serif;'>Score confiance</div>
        </div>
        """, unsafe_allow_html=True)

# ─── DONNÉES ───
col_input, col_main = st.columns([1, 2.2])

with col_input:
    st.markdown("### 📍 POINTS RELEVÉS")
    
    # Données selon profil choisi
    if profil_choice != "Personnalisé" and PROFILS[profil_choice]:
        default_pts = PROFILS[profil_choice]
    else:
        default_pts = PROFILS["Grand Profil (défaut)"]
    
    default_data = pd.DataFrame(default_pts, columns=["X (mm)", "Y (mm)"])
    
    edited_df = st.data_editor(
        default_data, num_rows="dynamic", height=420,
        column_config={
            "X (mm)": st.column_config.NumberColumn(format="%.1f"),
            "Y (mm)": st.column_config.NumberColumn(format="%.1f")
        }
    )
    
    # Pondération manuelle des points
    if weight_mode == "Manuel":
        with st.expander("⚖️ Pondérations"):
            w_df = pd.DataFrame({
                "X (mm)": edited_df["X (mm)"].dropna().values,
                "Poids": [1.0] * len(edited_df.dropna())
            })
            w_edited = st.data_editor(w_df, height=200)
            manual_weights = w_edited["Poids"].values.astype(float)
    else:
        manual_weights = None
    
    run_calc = st.button("▶ LANCER LE CALCUL", type="primary", use_container_width=True)

# ─── GRAPHIQUE EN TEMPS RÉEL (aperçu) ───
with col_main:
    if st.session_state.last_result:
        res = st.session_state.last_result
        
        tab1, tab2, tab3 = st.tabs(["📈 COURBE", "📊 ERREURS", "🕐 HISTORIQUE"])
        
        with tab1:
            pts_x = np.array(res["pts_x"])
            pts_y = np.array(res["pts_y"])
            compare = st.session_state.compare_result
            fig = make_main_chart(res, compare_res=compare, pts_x=pts_x, pts_y=pts_y)
            st.plotly_chart(fig, use_container_width=True)
            
            # Métriques
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Erreur moy.", f"{res['err_mean']:.1f} mm")
            c2.metric("Erreur max.", f"{res['err_max']:.1f} mm")
            c3.metric("Angle départ", f"{res['alpha']:.1f}°")
            c4.metric("Confiance", f"{res['confidence']}%")
        
        with tab2:
            st.plotly_chart(make_error_chart(res), use_container_width=True)
            
            # Tableau erreurs
            err_data = pd.DataFrame({
                "X (mm)": [f"{x:.0f}" for x in res["pts_x"]],
                "Y relevé": [f"{y:.1f}" for y in res["pts_y"]],
                "Erreur": [f"{e:.2f} mm" for e in res["err_pts"]],
                "État": ["✅" if e < 5 else "⚠️" if e < 15 else "❌" for e in res["err_pts"]]
            })
            st.dataframe(err_data, use_container_width=True, height=250)
        
        with tab3:
            if st.session_state.history:
                for i, h in enumerate(reversed(st.session_state.history[-5:])):
                    conf_col = "#40f090" if h["confidence"] > 70 else ("#f0c040" if h["confidence"] > 40 else "#f04050")
                    st.markdown(f"""
                    <div style='background:#1a1d24;border:1px solid #2a2d35;border-radius:3px;padding:0.6rem 1rem;margin-bottom:0.4rem;display:flex;justify-content:space-between;align-items:center;'>
                      <span style='color:#a0a8b8;font-family:Barlow Condensed,sans-serif;font-size:0.85rem;'>{h['timestamp']} · {h['num_arcs']} arcs</span>
                      <span style='color:#e8e0d0;font-family:Share Tech Mono,monospace;font-size:0.9rem;'>Ø{h['err_mean']:.1f}mm</span>
                      <span style='color:{conf_col};font-family:Share Tech Mono,monospace;'>{h['confidence']}%</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                if st.button("📌 Utiliser comme référence", help="Ce calcul apparaîtra en pointillés sur le prochain graphique"):
                    st.session_state.compare_result = st.session_state.last_result
                    st.success("Référence enregistrée !")
            else:
                st.info("Aucun historique pour cette session.")
    
    else:
        st.markdown("""
        <div style='height:460px;display:flex;align-items:center;justify-content:center;border:1px dashed #2a2d35;border-radius:4px;'>
          <div style='text-align:center;'>
            <div style='font-size:3rem;'>⚙️</div>
            <div style='color:#505060;font-family:Barlow Condensed,sans-serif;font-size:1.2rem;letter-spacing:2px;margin-top:1rem;'>LANCEZ UN CALCUL</div>
            <div style='color:#404050;font-family:Barlow,sans-serif;font-size:0.85rem;margin-top:0.5rem;'>Entrez vos points et cliquez sur Lancer le calcul</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ─── CALCUL ───
if run_calc:
    df = edited_df.dropna().astype(float).sort_values("X (mm)")
    all_pts = df[["X (mm)", "Y (mm)"]].values
    W_total = float(np.max(all_pts[:, 0]))
    pts_x = all_pts[:, 0]
    pts_y = all_pts[:, 1]
    
    # Pondération
    if weight_mode == "Bords renforcés":
        w = np.ones(len(pts_x))
        n = len(w)
        w[0] = 4.0; w[-1] = 4.0
        if n > 2: w[1] = 2.0; w[-2] = 2.0
    elif weight_mode == "Manuel" and manual_weights is not None:
        w = manual_weights[:len(pts_x)]
    else:
        w = np.ones(len(pts_x))
    
    with st.spinner(f"🚀 Optimisation {nb_rayons} arcs en cours..."):
        res = solve_engine_v5(pts_x, pts_y, W_total, target_val, nb_rayons, symmetric=symmetric, weights=w)
    
    # Sauvegarde
    st.session_state.last_result = res
    st.session_state.history.append({
        "timestamp": res["timestamp"],
        "num_arcs": nb_rayons,
        "err_mean": res["err_mean"],
        "confidence": res["confidence"]
    })
    
    # Sauvegarde du nb_rayons et target dans la session pour l'affichage
    st.session_state.last_nb_rayons = nb_rayons
    st.session_state.last_target = target_val

# ─── AFFICHAGE RÉSULTATS (piloté par session_state, toujours visible) ───
if st.session_state.last_result:
    res = st.session_state.last_result
    disp_nb_rayons = st.session_state.get("last_nb_rayons", res["num_arcs"])
    disp_target = st.session_state.get("last_target", target_val)

    st.markdown("---")
    st.markdown("### 📋 RÉSULTATS")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Erreur moy.", f"{res['err_mean']:.1f} mm")
    c2.metric("Erreur max.", f"{res['err_max']:.1f} mm")
    c3.metric("Angle départ", f"{res['alpha']:.1f}°")
    c4.metric("Confiance", f"{res['confidence']}%")
    c5.metric("Largeur", f"{res['width']:.0f} mm")

    rows = []
    for i in range(disp_nb_rayons):
        L = res["Ls"][i]
        R = res["Rs"][i]
        if L >= disp_target:
            status = "✅ OK"
        elif L >= disp_target * 0.8:
            status = "⚠️ Court"
        else:
            status = "❌ Trop Court"
        rows.append({
            "Zone": f"Arc {i+1}",
            "Rayon (mm)": round(R, 1),
            "Dév. L (mm)": round(L, 1),
            "Cible (mm)": disp_target,
            "État": status
        })

    final_df = pd.DataFrame(rows)
    st.dataframe(
        final_df.style.format({"Rayon (mm)": "{:.1f}", "Dév. L (mm)": "{:.1f}"}),
        use_container_width=True
    )

    # ─── EXPORTS ───
    st.markdown("### 📤 EXPORT")
    ec1, ec2, ec3 = st.columns(3)

    with ec1:
        excel_data = export_excel(res, disp_target, disp_nb_rayons)
        st.download_button(
            "⬇ Excel (.xlsx)",
            data=excel_data,
            file_name=f"cintrage_{res['date'].replace('/','')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with ec2:
        json_data = export_json(res)
        st.download_button(
            "⬇ JSON",
            data=json_data,
            file_name=f"cintrage_{res['date'].replace('/','')}.json",
            mime="application/json",
            use_container_width=True
        )

    with ec3:
        csv_rows = [f"Arc {i+1};{round(res['Rs'][i],1)};{round(res['Ls'][i],1)}" for i in range(disp_nb_rayons)]
        csv_data = "Zone;Rayon (mm);Dév. L (mm)\n" + "\n".join(csv_rows)
        st.download_button(
            "⬇ CSV",
            data=csv_data,
            file_name=f"cintrage_{res['date'].replace('/','')}.csv",
            mime="text/csv",
            use_container_width=True
        )
