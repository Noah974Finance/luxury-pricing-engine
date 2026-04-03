import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
from lifelines import KaplanMeierFitter, CoxPHFitter
import yfinance as yf
from datetime import datetime

# ==========================================
# CONFIGURATION LUXE & STYLE
# ==========================================
st.set_page_config(page_title="Survival Engine ELITE", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8F9FA; }
    .stMetric { background-color: #FFFFFF; padding: 20px; border-radius: 12px; border: 1px solid #EAEAEA; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    div[data-testid="stExpander"] { border: none !important; box-shadow: none !important; background: transparent !important; }
    .stButton>button { border-radius: 8px; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. DATA HUB
# ==========================================
@st.cache_data(ttl=60)
def load_internal_data():
    conn = sqlite3.connect('luxury_inventory.db')
    df = pd.read_sql("SELECT * FROM inventory", conn)
    conn.close()
    # Conversion des dates
    df['date_entree'] = pd.to_datetime(df['date_entree'])
    df['date_vente'] = pd.to_datetime(df['date_vente'])
    return df

@st.cache_data(ttl=3600)
def get_historical_forex():
    data = yf.download('EURJPY=X', period='5y', interval='1d', progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

df = load_internal_data()
df_forex_hist = get_historical_forex()
current_rate = df_forex_hist['Close'].iloc[-1]
rate_start = df_forex_hist['Close'].iloc[0]
global_trend = ((current_rate - rate_start) / rate_start) * 100

# ==========================================
# 2. SIDEBAR STRATÉGIQUE (WAR ROOM)
# ==========================================
st.sidebar.title("🎮 War Room Control")
st.sidebar.markdown("---")

st.sidebar.subheader("🕹️ Simulation de Démarque")
discount_target = st.sidebar.slider("Profondeur de remise (%)", 0, 70, 20)
critical_days = st.sidebar.slider("Seuil d'Alerte (Jours)", 30, 365, 120)

st.sidebar.markdown("---")
st.sidebar.subheader("🔬 Paramètres Financiers")
frais_stockage_jour = st.sidebar.number_input("Coût portage journalier/pièce (€)", 0.05, 5.0, 0.50)

st.sidebar.markdown("---")
st.sidebar.subheader("📂 Filtres Actifs")
selected_cat = st.sidebar.multiselect("Catégories", df['categorie'].unique(), default=df['categorie'].unique())
selected_region = st.sidebar.multiselect("Régions", df['region'].unique(), default=df['region'].unique())

df_filtered = df[(df['categorie'].isin(selected_cat)) & (df['region'].isin(selected_region))].copy()

if df_filtered.empty:
    st.warning("⚠️ **Dashboard en pause** : Veuillez sélectionner au moins une catégorie et une région.")
    st.stop()

# ==========================================
# 3. MOTEUR MATHÉMATIQUE & KPI
# ==========================================
boost_elasticity = (discount_target / 10) * 0.35 
kmf = KaplanMeierFitter()
kmf.fit(df_filtered['jours_en_rayon'], event_observed=df_filtered['est_vendu'])

en_stock_now = df_filtered[df_filtered['est_vendu'] == 0]
stock_mort_reel = en_stock_now[en_stock_now['jours_en_rayon'] > critical_days]
cout_inaction_mensuel = len(stock_mort_reel) * frais_stockage_jour * 30

# ==========================================
# 4. INTERFACE PRINCIPALE
# ==========================================
st.title("🧬 Intelligence Pricing & Survival Engine")
st.caption(f"Analyse Stratégique au {datetime.now().strftime('%d/%m/%Y')} | Source : ERP Interne & Marchés Financiers")

tab_exec, tab_sim, tab_live, tab_data = st.tabs([
    "👔 Executive Summary", "📉 Simulation What-If", "🌍 Dynamique Marchés", "🔬 Data Lab"
])

# ---------------------------------------------------------
# ONGLET 1 : EXECUTIVE SUMMARY
# ---------------------------------------------------------
with tab_exec:
    st.error(f"⚠️ **Coût d'Inaction Financière :** L'immobilisation du stock critique (>{critical_days}j) coûte environ **{cout_inaction_mensuel:,.0f} € / mois** en frais de portage.")
    
    col_kpi, col_gauge = st.columns([2, 1])
    with col_kpi:
        c1, c2, c3 = st.columns(3)
        c1.metric("📦 Stock Actif", f"{len(en_stock_now):,}", help="Total des articles non vendus.")
        c2.metric("☠️ Volume Critique", f"{len(stock_mort_reel):,}", f"-{len(stock_mort_reel)*100/len(en_stock_now):.1f}%" if len(en_stock_now)>0 else "0%", delta_color="inverse")
        c3.metric("💸 Capital Immobilisé", f"{stock_mort_reel['prix_original'].sum():,.0f} €")

    with col_gauge:
        health_score = 100 - (len(stock_mort_reel)/len(en_stock_now)*100) if len(en_stock_now) > 0 else 100
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = health_score,
            number = {'suffix': "%", 'font': {'size': 36, 'color': '#2C3E50'}},
            title = {'text': "Indice de Santé", 'font': {'size': 16, 'color': '#7F8C8D'}},
            gauge = {'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                     'bar': {'color': "#1A252F", 'thickness': 0.25},
                     'steps': [{'range': [0, 60], 'color': "#E74C3C"}, {'range': [60, 85], 'color': "#F39C12"}, {'range': [85, 100], 'color': "#27AE60"}],
                     'threshold': {'line': {'color': "#2C3E50", 'width': 4}, 'thickness': 0.5, 'value': 85}}
        ))
        fig_gauge.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.divider()

    st.markdown("**🗺️ Cartographie du Capital Immobilisé (Réseau Global)**")
    if not stock_mort_reel.empty:
        df_toxic = stock_mort_reel.copy()
        df_toxic['Score_Toxicite'] = df_toxic['prix_original'] * df_toxic['jours_en_rayon']

        df_geo = df_toxic.groupby('pays').agg(Capital_Bloque=('prix_original', 'sum'), Age_Moyen=('jours_en_rayon', 'mean')).reset_index()

        idx_pires_geo = df_toxic.groupby('pays')['Score_Toxicite'].idxmax()
        df_pires_geo = df_toxic.loc[idx_pires_geo]
        df_pires_geo['Pire_Produit_Label'] = df_pires_geo['categorie'] + " " + df_pires_geo['matiere'] + " " + df_pires_geo['couleur'] + " (" + df_pires_geo['prix_original'].astype(int).astype(str) + "€)"
        
        df_geo = df_geo.merge(df_pires_geo[['pays', 'Pire_Produit_Label']], on='pays', how='left')

        iso_mapping = {'France': 'FRA', 'Italie': 'ITA', 'Royaume-Uni': 'GBR', 'Allemagne': 'DEU', 'Suisse': 'CHE', 'Espagne': 'ESP', 'Chine': 'CHN', 'Japon': 'JPN', 'Corée du Sud': 'KOR', 'Singapour': 'SGP'}
        df_geo['iso_alpha'] = df_geo['pays'].map(iso_mapping)

        fig_map = px.choropleth(df_geo, locations="iso_alpha", color="Capital_Bloque", hover_name="pays",
                                custom_data=["Capital_Bloque", "Age_Moyen", "Pire_Produit_Label"], color_continuous_scale="Reds", projection="natural earth")
        fig_map.update_geos(showland=True, landcolor="#F4F6F6", showocean=True, oceancolor="rgba(0,0,0,0)", showcountries=True, countrycolor="#E5E7E9", showframe=False, bgcolor="rgba(0,0,0,0)", fitbounds="locations")
        fig_map.update_traces(hovertemplate="<b>%{hovertext}</b><br><br>Capital Immobilisé: <b>%{customdata[0]:,.0f} €</b><br>Âge Moyen: %{customdata[1]:.0f} jours<br><br>🔥 <b>Alerte Produit:</b><br>%{customdata[2]}<extra></extra>", marker_line_width=0.5, marker_line_color="#BDC3C7")
        fig_map.update_layout(height=450, margin=dict(l=0, r=0, t=0, b=0), coloraxis_colorbar=dict(title="Capital Bloqué (€)", thickness=15, len=0.8))
        st.plotly_chart(fig_map, use_container_width=True)

    st.divider()

    st.markdown("**🎯 Plan d'Action : Top 1 Urgence par Catégorie**")
    if not stock_mort_reel.empty:
        idx_pires = df_toxic.groupby('categorie')['Score_Toxicite'].idxmax()
        df_top_pires = df_toxic.loc[idx_pires].sort_values(by='Score_Toxicite', ascending=False)
        df_display = df_top_pires[['categorie', 'pays', 'product_id', 'matiere', 'couleur', 'prix_original', 'jours_en_rayon']].rename(columns={'categorie': 'Catégorie', 'pays': 'Pays', 'product_id': 'Réf. Produit', 'matiere': 'Matière', 'couleur': 'Couleur', 'prix_original': 'Valeur Bloquée', 'jours_en_rayon': 'Ancienneté'})

        st.dataframe(df_display.style.format({"Valeur Bloquée": "{:,.0f} €", "Ancienneté": "{:.0f} jours"}).background_gradient(subset=['Ancienneté'], cmap='Reds', vmin=critical_days).set_properties(**{'background-color': '#FFFFFF'}), use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# ONGLET 2 : SIMULATION DYNAMIQUE
# ---------------------------------------------------------
with tab_sim:
    st.subheader("📈 Simulation de l'accélération du temps de vente")
    survival_sim = kmf.survival_function_.copy()
    survival_sim.index = survival_sim.index / (1 + boost_elasticity)
    
    fig_sim = go.Figure()
    fig_sim.add_trace(go.Scatter(x=kmf.survival_function_.index, y=kmf.survival_function_['KM_estimate'], name="Survie Actuelle (Prix Fort)", line=dict(color='#BDC3C7', dash='dot')))
    fig_sim.add_trace(go.Scatter(x=survival_sim.index, y=survival_sim['KM_estimate'], name=f"Survie Boostée (-{discount_target}%)", fill='tonexty', line=dict(color='#2ECC71', width=4)))
    
    fig_sim.update_layout(xaxis_title="Jours en Boutique", yaxis_title="Probabilité d'Invendu", hovermode="x unified", height=500, plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(gridcolor='#EAECEE'))
    st.plotly_chart(fig_sim, use_container_width=True)
    st.info(f"💡 Analyse IA : Une démarque de {discount_target}% accélère mathématiquement votre cycle de vente de {boost_elasticity*100:.0f}%.")

# ---------------------------------------------------------
# ONGLET 3 : MARCHÉS LIVE & VENTES
# ---------------------------------------------------------
with tab_live:
    st.subheader("🏛️ Terminal Monitoring Macro-Économique & Ventes")
    
    st.markdown("**📈 Évolution des Ventes par Région (Sell-Out)**")
    df_sold = df_filtered[df_filtered['est_vendu'] == 1].dropna(subset=['date_vente']).copy()
    
    if not df_sold.empty:
        # Fréquence 'ME' = Month End
        df_trend = df_sold.groupby([pd.Grouper(key='date_vente', freq='M'), 'region']).agg(Volume_Ventes=('product_id', 'count')).reset_index()
        
        fig_trend = px.area(df_trend, x='date_vente', y='Volume_Ventes', color='region', color_discrete_map={'Europe': '#2C3E50', 'Asie': '#E74C3C'}, line_shape='spline')
        fig_trend.update_traces(mode='lines+markers', marker=dict(size=4), hovertemplate="<b>%{x|%B %Y}</b><br>Ventes: <b>%{y} pièces</b><extra></extra>")
        fig_trend.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0), xaxis_title="", yaxis_title="Volume de ventes", legend_title="", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=True, gridcolor='#F2F3F4', dtick="M3", tickformat="%b %Y"), yaxis=dict(showgrid=True, gridcolor='#F2F3F4'))
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Aucune vente enregistrée pour les filtres actuels.")

    st.divider()

    m1, m2, m3 = st.columns(3)
    m1.metric("Cours EUR/JPY", f"¥ {current_rate:.2f}", f"{global_trend:.2f}% (5 ans)")
    m2.metric("Plus Haut Historique", f"¥ {df_forex_hist['Close'].max():.2f}")
    m3.metric("Plus Bas Historique", f"¥ {df_forex_hist['Close'].min():.2f}")

    st.markdown("<br>", unsafe_allow_html=True)
    col_l1, col_l2 = st.columns([1.5, 1])

    with col_l1:
        st.markdown("**🔍 Analyse de Tendance Long-Terme (FX 5 Ans)**")
        fig_pro = go.Figure()
        fig_pro.add_trace(go.Scatter(x=df_forex_hist.index, y=df_forex_hist['Close'], fill='tozeroy', fillcolor='rgba(0, 102, 204, 0.05)', line=dict(color='#0066CC', width=2), name="Cours Clôture"))
        ma_200 = df_forex_hist['Close'].rolling(window=200).mean()
        fig_pro.add_trace(go.Scatter(x=df_forex_hist.index, y=ma_200, line=dict(color='rgba(128, 128, 128, 0.5)', width=2, dash='dash'), name="Tendance 200j"))
        fig_pro.update_layout(height=400, hovermode="x unified", margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(rangeselector=dict(buttons=list([dict(count=6, label="6M", step="month", stepmode="backward"), dict(count=1, label="1Y", step="year", stepmode="backward"), dict(step="all", label="MAX")])), type="date"), yaxis=dict(autorange=True, fixedrange=False, side="right", title="Yen (¥)"), plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pro, use_container_width=True)

    with col_l2:
        st.markdown("**📊 Impact Taux de Change (P&L)**")
        val_brute = en_stock_now['prix_original'].sum()
        cout_fab = val_brute * 0.28
        perte_soldes = -(stock_mort_reel['prix_original'].sum() * (discount_target / 100))
        impact_fx = (val_brute * 0.20) * (global_trend / 100)
        ebitda = val_brute - cout_fab + perte_soldes + impact_fx

        fig_wf = go.Figure(go.Waterfall(
            orientation = "v", x = ["Valeur Brut", "Coûts Fab", "Impact Soldes", "Impact FX", "Profit Net Est."],
            y = [val_brute, -cout_fab, perte_soldes, impact_fx, ebitda], measure = ["relative", "relative", "relative", "relative", "total"],
            decreasing = {"marker":{"color":"#E74C3C"}}, increasing = {"marker":{"color":"#2ECC71"}}, totals = {"marker":{"color":"#2C3E50"}}
        ))
        fig_wf.update_layout(height=400, margin=dict(t=10, b=0, l=0, r=0), showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_wf, use_container_width=True)

# ---------------------------------------------------------
# ONGLET 4 : DATA LAB & ADVANCED ANALYTICS
# ---------------------------------------------------------
with tab_data:
    st.subheader("🔬 Laboratoire d'Analyse Multidimensionnelle")
    
    st.markdown("**1. L'Effet Entonnoir : Le Détecteur d'Anomalies**")
    st.caption("Comparez les pièces qui s'accumulent dans le stock mort face à ce qui était prévu dans vos achats initiaux.")

    col_visuel, col_data = st.columns([1.2, 1])

    with col_visuel:
        st.markdown(f"**☠️ Cartographie du Stock Mort (> {critical_days} j)**")
        if not stock_mort_reel.empty:
            fig_apres = px.sunburst(stock_mort_reel, path=['categorie', 'matiere', 'couleur'], values='prix_original', color='jours_en_rayon', color_continuous_scale='YlOrRd')
            fig_apres.update_traces(textinfo="label+percent root", hovertemplate="<b>%{label}</b><br>Capital Bloqué: <b>%{value:,.0f} €</b><br>Poids Toxique: %{percentRoot:.1%}<br>Âge Moyen: %{color:.0f} j<extra></extra>", marker=dict(line=dict(color='white', width=1.5)))
            fig_apres.update_layout(coloraxis_showscale=False, margin=dict(t=10, l=0, r=0, b=0), height=380, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_apres, use_container_width=True)
        else:
            st.success("🎉 Aucun stock critique.")

    with col_data:
        st.markdown("**🚨 Top 5 des Erreurs d'Assortiment (Deltas)**")
        if not df_filtered.empty and not stock_mort_reel.empty:
            prod_grp = df_filtered.groupby(['categorie', 'matiere', 'couleur'])['prix_original'].sum().reset_index()
            prod_grp['Poids_Achats'] = prod_grp['prix_original'] / prod_grp['prix_original'].sum()
            mort_grp = stock_mort_reel.groupby(['categorie', 'matiere', 'couleur'])['prix_original'].sum().reset_index()
            mort_grp['Poids_Mort'] = mort_grp['prix_original'] / mort_grp['prix_original'].sum()
            
            anomalies = pd.merge(prod_grp, mort_grp, on=['categorie', 'matiere', 'couleur'], suffixes=('_prod', '_mort'))
            anomalies['Sur_Representation'] = anomalies['Poids_Mort'] - anomalies['Poids_Achats']
            top_anomalies = anomalies.sort_values('Sur_Representation', ascending=False).head(5)
            top_anomalies['Produit'] = top_anomalies['categorie'] + " " + top_anomalies['matiere'] + " " + top_anomalies['couleur']
            
            st.dataframe(top_anomalies[['Produit', 'Poids_Achats', 'Poids_Mort', 'Sur_Representation']].style.format({"Poids_Achats": "{:.1%}", "Poids_Mort": "{:.1%}", "Sur_Representation": "{:+.1%}"}).background_gradient(subset=['Sur_Representation'], cmap='Reds'), use_container_width=True, hide_index=True)
            st.info("💡 **Comment lire :** Une Sur-Représentation de +15% indique que ce produit étouffe vos finances bien plus que prévu.")

    st.divider()

    st.markdown("**2. Modèle de Survie (L'Impact Réel du Design)**")
    st.caption("Algorithme IA identifiant l'impact d'une caractéristique sur la probabilité de vente (toutes choses égales par ailleurs).")
    
    features = ['jours_en_rayon', 'est_vendu', 'couleur', 'matiere']
    df_ml = df_filtered[features].dropna()
    
    if len(df_ml) > 50:
        ref_couleur = sorted(df_ml['couleur'].unique())[0]
        ref_matiere = sorted(df_ml['matiere'].unique())[0]
        df_cox_encoded = pd.get_dummies(df_ml, columns=['couleur', 'matiere'], drop_first=True)
        cph = CoxPHFitter(penalizer=0.1)
        
        try:
            cph.fit(df_cox_encoded, duration_col='jours_en_rayon', event_col='est_vendu')
            summary_df = cph.summary[['exp(coef)']].copy()
            summary_df['exp(coef)'] = summary_df['exp(coef)'] - 1
            summary_df.index = summary_df.index.str.replace('couleur_', 'Couleur: ').str.replace('matiere_', 'Matière: ')
            summary_df = summary_df.sort_values(by='exp(coef)', ascending=True)
            summary_df['Couleur_Barre'] = np.where(summary_df['exp(coef)'] > 0, '#27AE60', '#E74C3C')
            
            fig_cox = px.bar(summary_df, x='exp(coef)', y=summary_df.index, orientation='h')
            fig_cox.update_traces(marker_color=summary_df['Couleur_Barre'], hovertemplate="<b>%{y}</b><br>Impact sur la vitesse de vente: <b>%{x:+.1%}</b><extra></extra>")
            fig_cox.update_layout(height=450, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(title="Vitesse d'écoulement relative", tickformat=".0%", zeroline=True, zerolinecolor='#2C3E50', zerolinewidth=2), yaxis=dict(title="", tickfont=dict(size=12, color='#2C3E50')), plot_bgcolor='rgba(0,0,0,0)')
            
            st.plotly_chart(fig_cox, use_container_width=True)
            st.warning(f"📐 **Note Méthodologique :** Le modèle utilise **{ref_couleur}** et **{ref_matiere}** comme bases (Point 0%). Les autres caractéristiques sont comparées à ces bases.")
        except Exception as e:
            st.warning("⚠️ L'échantillon manque de variance pour calculer un modèle fiable.")
    else:
        st.warning("⚠️ Pas assez de données pour l'algorithme.")

    st.divider()

    st.markdown("**3. Matrice de Performance (Couleur x Matière)**")
    df_unsold = df_filtered[df_filtered['est_vendu'] == 0]
    if not df_unsold.empty:
        pivot_df = pd.pivot_table(df_unsold, values='jours_en_rayon', index='matiere', columns='couleur', aggfunc='mean').round(0)
        fig_heat = px.imshow(pivot_df, labels=dict(x="", y="", color="Jours"), x=pivot_df.columns, y=pivot_df.index, color_continuous_scale='Reds', text_auto='.0f', aspect="auto")
        fig_heat.update_xaxes(side="top", tickfont=dict(size=12, color='#2C3E50'))
        fig_heat.update_yaxes(tickfont=dict(size=12, color='#2C3E50'))
        fig_heat.update_traces(hovertemplate="Matière: <b>%{y}</b><br>Couleur: <b>%{x}</b><br>Âge moyen: <b>%{z} jours</b><extra></extra>")
        fig_heat.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_heat, use_container_width=True)

    st.divider()
    
    st.markdown("**📥 Base de Données Globale (Exportable via l'icône de téléchargement en haut à droite)**")
        
        # Utilisation de column_config (La méthode ultra-rapide pour les millions de lignes)
    st.dataframe(
            df_filtered,
            use_container_width=True,
            hide_index=True,
            height=400,
            column_config={
                "prix_original": st.column_config.NumberColumn("Prix Original", format="%d €"),
                "marge_pct": st.column_config.NumberColumn("Marge", format="%d %%"),
                "jours_en_rayon": st.column_config.NumberColumn("Jours en rayon", format="%d j"),
                "trafic_web": st.column_config.NumberColumn("Trafic Web", format="%d")
            }
        )