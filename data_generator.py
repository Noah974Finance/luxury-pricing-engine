import sqlite3
import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import timedelta

fake = Faker('fr_FR')

def generate_luxury_data(n_products=200000):
    print(f"⚡ Initialisation du moteur probabiliste V4 (EURASIA) pour {n_products} produits...")

    # ==========================================
    # 1. PARAMÈTRES MÉTIER (LES LOIS DU LUXE)
    # ==========================================
    categories = {
        'Sacs': {'prix': (1500, 8000), 'marge': (75, 88), 'tailles': ['Unique', 'Mini', 'Medium', 'Maxi']},
        'Chaussures': {'prix': (600, 2500), 'marge': (65, 80), 'tailles': ['36', '37', '38', '39', '40', '41', '42', '43', '44']},
        'Robes': {'prix': (2000, 15000), 'marge': (80, 92), 'tailles': ['34', '36', '38', '40', '42', '44']},
        'Manteaux': {'prix': (3000, 12000), 'marge': (70, 85), 'tailles': ['46', '48', '50', '52', '54', '56']},
        'Accessoires': {'prix': (200, 1200), 'marge': (85, 95), 'tailles': ['Unique']}
    }
    
    couleurs_core = ['Noir', 'Beige', 'Marine', 'Blanc']
    couleurs_fashion = ['Rose Fluo', 'Jaune Moutarde', 'Vert Émeraude', 'Argenté']
    matieres = ['Cuir Grainé', 'Cuir Lisse', 'Cachemire', 'Soie', 'Coton', 'Toile', 'Python']
    saisons = ['SS25', 'FW25', 'SS26']

    pays_asie = ['Chine', 'Japon', 'Corée du Sud', 'Singapour']
    pays_europe = ['France', 'Italie', 'Royaume-Uni', 'Allemagne', 'Suisse', 'Espagne']
    pays_cibles = pays_europe + pays_asie
    
    # La Chine et le Japon absorbent une part massive de l'inventaire mondial
    poids_pays = [15, 10, 10, 5, 5, 5, 25, 15, 7, 3] 
    canaux_vente = ['Boutique Physique', 'E-commerce', 'Outlet', 'Vente Privée']

    # ==========================================
    # 2. GÉNÉRATION DES DONNÉES
    # ==========================================
    data = []
    today = pd.Timestamp.now().date()

    for i in range(n_products):
        # --- Caractéristiques Produit ---
        cat = random.choice(list(categories.keys()))
        conf = categories[cat]
        
        is_core = random.random() < 0.7
        couleur = random.choice(couleurs_core) if is_core else random.choice(couleurs_fashion)
        matiere = random.choice(matieres)
        taille = random.choice(conf['tailles'])
        saison = random.choice(saisons)
        
        # --- Localisation & Canal ---
        pays = random.choices(pays_cibles, weights=poids_pays)[0] 
        region = 'Asie' if pays in pays_asie else 'Europe'
        canal = random.choices(canaux_vente, weights=[60, 30, 5, 5])[0]

        # Logistique Inversée (Retours)
        prob_retour = 0.30 if canal == 'E-commerce' else 0.05
        est_retourne = 1 if random.random() < prob_retour else 0
        
        # --- Temporalité Initiale ---
        date_entree = fake.date_between(start_date='-2y', end_date='now')
        jours_en_rayon_theorique = (today - date_entree).days
        
        # ==========================================
        # 3. ALGORITHME DE VENTE (PROBABILITÉS)
        # ==========================================
        base_prob = min(0.95, (jours_en_rayon_theorique / 150))
        
        # Biais Produit
        if is_core: base_prob += 0.15 
        else: base_prob -= 0.20 
        
        if matiere in ['Toile', 'Python'] and cat == 'Manteaux': base_prob -= 0.3 
        if matiere in ['Cachemire'] and cat == 'Manteaux': base_prob += 0.2 

        # Biais Culturel & Géographique
        if pays == 'Japon' and is_core: base_prob += 0.20
        if pays == 'Japon' and not is_core: base_prob -= 0.30
        if pays == 'Chine' and not is_core: base_prob += 0.15
        if pays == 'Royaume-Uni' and not is_core: base_prob += 0.10
        if pays == 'Suisse' and matiere == 'Cachemire': base_prob += 0.20
        if pays == 'Singapour' and cat == 'Manteaux': base_prob -= 0.50

        # Biais Canal
        if canal in ['Outlet', 'Vente Privée']: base_prob += 0.40 
        if canal == 'E-commerce': base_prob += 0.05 

        # --- Prise de Décision ---
        est_vendu = 1 if random.random() < base_prob else 0
        date_vente = None
        
        if est_vendu:
            # On simule une vente rapide ou lente
            max_jours = max(1, int(min(120, jours_en_rayon_theorique)))
            jours_final = random.randint(1, max_jours)
            
            # Déduction de la date de vente exacte
            date_vente_calc = date_entree + timedelta(days=jours_final)
            if date_vente_calc > today: # Sécurité : pas de vente dans le futur
                date_vente_calc = today
            date_vente = date_vente_calc
        else:
            jours_final = jours_en_rayon_theorique

        # Pénalité logistique si le produit a été retourné
        if est_retourne:
            jours_final += random.randint(10, 25)

        # ==========================================
        # 4. ENREGISTREMENT
        # ==========================================
        data.append({
            'product_id': f"LX-{100000 + i}",
            'categorie': cat,
            'saison': saison,
            'couleur': couleur,
            'matiere': matiere,
            'taille': taille,
            'pays': pays,
            'region': region, # Nouvelle colonne pour grouper
            'canal_vente': canal,
            'est_retourne': est_retourne,
            'prix_original': round(random.uniform(*conf['prix']), -1),
            'marge_pct': random.randint(*conf['marge']),
            'trafic_web': random.randint(50, 15000),
            'jours_en_rayon': jours_final,
            'est_vendu': est_vendu,
            'date_entree': date_entree,
            'date_vente': date_vente # Nouvelle colonne pour les séries temporelles
        })

    # ==========================================
    # 5. EXPORT VERS SQLITE
    # ==========================================
    df = pd.DataFrame(data)
    
    # Sécurité finale sur les valeurs aberrantes
    df['jours_en_rayon'] = df['jours_en_rayon'].apply(lambda x: max(1, x))

    conn = sqlite3.connect('luxury_inventory.db')
    df.to_sql('inventory', conn, if_exists='replace', index=False)
    conn.close()
    
    print(f"✅ Base de données V4 générée avec succès ! ({n_products} produits)")

if __name__ == "__main__":
    generate_luxury_data(200000)