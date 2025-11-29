# 🚀 Quick Start - TravelMate

## Problèmes Courants et Solutions

### ❌ Erreur 404 sur /categories
**Solution:** L'endpoint a changé vers `/destinations/categories/list`

Le frontend a été mis à jour automatiquement dans l'artifact.

### 🔵 Fond bleu au lieu de fond sombre
**Solution:** Le CSS a été corrigé dans l'artifact.

---

## ✅ Setup Étape par Étape

### 1. Structure des Dossiers

```bash
cd backend

# Créer tous les dossiers
mkdir -p auth destinations trips reviews external social

# Créer les __init__.py
touch auth/__init__.py
touch destinations/__init__.py
touch trips/__init__.py
touch reviews/__init__.py
touch external/__init__.py
touch social/__init__.py
```

### 2. Copier les Fichiers

Copier dans l'ordre depuis les artifacts Claude :

**Racine backend/ :**
1. `config.py`
2. `database.py`
3. `models.py`
4. `main.py`
5. `requirements.txt`

**auth/ :**
6. `auth/utils.py`
7. `auth/routes.py`

**destinations/ :**
8. `destinations/mock_data.py`
9. `destinations/routes.py`

**trips/ :**
10. `trips/routes.py`

**reviews/ :**
11. `reviews/routes.py`

**external/ :**
12. `external/weather.py`
13. `external/flights.py`
14. `external/hotels.py`

**social/ :**
15. `social/routes.py`

### 3. Vérifier la Structure

```bash
# Exécuter le script de vérification
python check_setup.py
```

Si tout est ✅, continuer. Sinon, copier les fichiers manquants.

### 4. Installer les Dépendances

```bash
# Créer environnement virtuel
python -m venv venv

# Activer
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate  # Windows

# Installer
pip install -r requirements.txt
```

### 5. Démarrer le Backend

```bash
# Option 1: Direct
python main.py

# Option 2: Uvicorn avec reload
uvicorn main:app --reload
```

Vous devriez voir :
```
🚀 Starting TravelMate API...
✅ Database initialized
✅ Mock data loaded
🌍 API running at http://localhost:8000
📚 Documentation at http://localhost:8000/docs
```

### 6. Tester les Endpoints

Ouvrir http://localhost:8000/docs

Tester :
- ✅ `GET /` - Root
- ✅ `GET /health` - Health check
- ✅ `GET /destinations` - Liste des destinations
- ✅ `GET /destinations/categories/list` - Catégories

### 7. Démarrer le Frontend

```bash
cd ../frontend

# Si pas encore créé
npm create vite@latest . -- --template react
npm install

# Remplacer les fichiers
# - src/App.jsx (depuis artifact)
# - src/App.css (depuis artifact)

# Démarrer
npm run dev
```

Ouvrir http://localhost:5173

---

## 🐛 Debugging

### Backend ne démarre pas

**Erreur: "No module named 'X'"**
```bash
# Vérifier que vous êtes dans le venv
which python  # Doit pointer vers venv/bin/python

# Réinstaller
pip install -r requirements.txt
```

**Erreur: "Cannot import name 'router'"**
- Vérifier que tous les `__init__.py` existent
- Vérifier les noms de fichiers (pas de fautes de frappe)

### Frontend affiche une erreur

**404 sur les categories**
- Vérifier que le backend tourne sur le port 8000
- Vérifier que l'artifact `App.jsx` a été copié (avec la correction)

**Fond bleu**
- Vérifier que l'artifact `App.css` a été copié (avec la correction)

**CORS Error**
```python
# Dans config.py, vérifier :
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]
```

---

## 🎯 Points de Vérification Rapide

### Backend
```bash
# Test rapide
curl http://localhost:8000/
curl http://localhost:8000/destinations/categories/list
```

### Frontend
1. Ouvrir http://localhost:5173
2. Vous devriez voir la navbar sombre
3. Les catégories devraient s'afficher
4. Les destinations devraient charger

---

## 📝 Structure Finale Attendue

```
backend/
├── venv/                    # Environnement virtuel
├── travel.db               # Base de données (auto-créée)
├── config.py
├── database.py
├── models.py
├── main.py
├── requirements.txt
├── check_setup.py          # Script de vérification
├── auth/
│   ├── __init__.py
│   ├── utils.py
│   └── routes.py
├── destinations/
│   ├── __init__.py
│   ├── mock_data.py
│   └── routes.py
├── trips/
│   ├── __init__.py
│   └── routes.py
├── reviews/
│   ├── __init__.py
│   └── routes.py
├── external/
│   ├── __init__.py
│   ├── weather.py
│   ├── flights.py
│   └── hotels.py
└── social/
    ├── __init__.py
    └── routes.py
```

---

## 💡 Conseils

1. **Toujours vérifier** que vous êtes dans le venv avant d'installer
2. **Utiliser check_setup.py** pour vérifier la structure
3. **Consulter /docs** pour tester les endpoints
4. **Les logs sont votre ami** - regarder la console backend

---

## ✅ Checklist Finale

- [ ] Tous les dossiers créés
- [ ] Tous les `__init__.py` créés
- [ ] Tous les fichiers .py copiés
- [ ] `requirements.txt` installé
- [ ] Backend démarre sans erreur
- [ ] `/docs` accessible
- [ ] Frontend démarre
- [ ] Destinations chargent
- [ ] Catégories s'affichent

Si tout est ✅, vous êtes prêt ! 🎉