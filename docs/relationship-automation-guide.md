# Automatisation des Relations entre Objets d'Information et Entités

Guide complet pour automatiser la création de relations entre vos objets d'information (Commercial Assets) et différentes entités dans Microsoft Purview.

---

## Comparaison Rapide des Solutions

| Approche | Complexité | Idéale Pour | Commande |
|----------|-----------|------------|----------|
| **Solution 1** | ⭐ Très facile | 1-2 relations | `pvw relationship create` |
| **Solution 2** | ⭐⭐ Facile | Quelques relations | `pvw relationship create` (avec JSON array) |
| **Solution 2.5** | ⭐ Très facile | 5-100 relations | `pvw relationship bulk-create-csv` ✨ **RECOMMANDÉE** |
| **Solution 3** | ⭐⭐⭐ Modérée | 100+ relations avec logique custom | Script Python personnalisé |

---

## 🚀 Démarrage Rapide

Pour 90% des cas d'usage, voici la solution la plus simple:

```bash
# 1. Créer le fichier CSV (voir exemple ci-dessous)
# 2. Exécuter cette commande unique:
pvw relationship bulk-create-csv --csv-file entities_mapping.csv

# 3. Optionnel: Aperçu avant création
pvw relationship bulk-create-csv --csv-file entities_mapping.csv --dry-run
```

---

## Table des Matières

1. [Solution 1 : Relation Individuelle](#solution-1--relation-individuelle)
2. [Solution 2 : Opération en Masse (Bulk) - RECOMMANDÉE](#solution-2--opération-en-masse-bulk---recommandée)
3. [Solution 2.5 : Commande CLI CSV (PLUS FACILE!) ⭐](#solution-25--commande-cli-csv-plus-facile-)
4. [Solution 3 : Script Python pour Automatisation](#solution-3--script-python-pour-automatisation)
5. [Commandes Disponibles](#commandes-disponibles)
6. [Exemples Pratiques](#exemples-pratiques)

---

## Solution 1 : Relation Individuelle

Pour créer une seule relation à la fois, utilisez la commande CLI avec un fichier JSON.

### Étapes

#### 1. Créer le fichier JSON de relation

Créez un fichier `relationship.json` avec la structure suivante :

```json
{
  "typeName": "Objet Information_Table_Has",
  "end1": {
    "guid": "d286692e-30bb-48ba-ac49-f7372b12d225",
    "typeName": "Objet Information"
  },
  "end2": {
    "guid": "90d14acb-cf75-4729-9245-68f6f6f60000",
    "typeName": "mssql_table"
  },
  "attributes": {
    "name": "Relation Objet Information - Table"
  }
}
```

#### 2. Exécuter la commande de création

```bash
pvw relationship create --payload-file relationship.json
```

#### 3. Vérifier la relation créée

```bash
pvw relationship read --guid <relationship-guid>
```

### Avantages
- Simple pour quelques relations
- Contrôle précis de chaque relation

### Inconvénients
- Pas pratique pour plusieurs relations
- Répétitif et long

---

## Solution 2 : Opération en Masse (Bulk) - RECOMMANDÉE

Créez plusieurs relations en une seule opération API. **C'est la solution la plus efficace pour vos besoins.**

### Étapes

#### 1. Créer le fichier JSON avec tableau de relations

Créez un fichier `bulk_relationships.json` contenant un tableau de relations :

```json
[
  {
    "typeName": "Objet Information_Table_Has",
    "end1": {
      "guid": "d286692e-30bb-48ba-ac49-f7372b12d225",
      "typeName": "Objet Information"
    },
    "end2": {
      "guid": "90d14acb-cf75-4729-9245-68f6f6f60000",
      "typeName": "mssql_table"
    }
  },
  {
    "typeName": "Objet Information_Table_Has",
    "end1": {
      "guid": "d286692e-30bb-48ba-ac49-f7372b12d225",
      "typeName": "Objet Information"
    },
    "end2": {
      "guid": "8c680380-f21a-4a88-8651-06f6f6f60000",
      "typeName": "mssql_table"
    }
  },
  {
    "typeName": "Objet Information_Process_Has",
    "end1": {
      "guid": "d286692e-30bb-48ba-ac49-f7372b12d225",
      "typeName": "Objet Information"
    },
    "end2": {
      "guid": "autre-guid-process",
      "typeName": "mssql_procedure"
    }
  }
]
```

#### 2. Exécuter la création en masse

```bash
pvw relationship create --payload-file bulk_relationships.json
```

#### 3. Vérifier les résultats

```bash
# Lire une relation spécifique
pvw relationship read --guid <relationship-guid>
```

### Avantages
- **Efficace pour de nombreuses relations**
- Une seule requête API
- Moins d'erreurs de manipulation manuelle
- Idéal pour l'automatisation

### Inconvénients
- Nécessite de préparer le fichier JSON complet

---

## Solution 2.5 : Commande CLI CSV (PLUS FACILE!) ⭐

C'est la **meilleure solution pour la plupart des cas**. Une seule commande pour lire un CSV et créer les relations.

### Étapes

#### 1. Créer le fichier CSV

Créez un fichier `entities_mapping.csv` :

```csv
info_object_guid,target_entity_guid,target_entity_type,relationship_type
d286692e-30bb-48ba-ac49-f7372b12d225,90d14acb-cf75-4729-9245-68f6f6f60000,mssql_table,Objet Information_Table_Has
d286692e-30bb-48ba-ac49-f7372b12d225,8c680380-f21a-4a88-8651-06f6f6f60000,mssql_table,Objet Information_Table_Has
d286692e-30bb-48ba-ac49-f7372b12d225,autre-guid-process,mssql_procedure,Objet Information_Process_Has
```

**Colonnes CSV :**
- `info_object_guid` : GUID de l'objet d'information
- `target_entity_guid` : GUID de l'entité cible
- `target_entity_type` : Type de l'entité (mssql_table, mssql_procedure, etc.)
- `relationship_type` : Type de relation (Objet Information_Table_Has, etc.)

#### 2. Aperçu avant création (optionnel)

```bash
pvw relationship bulk-create-csv --csv-file entities_mapping.csv --dry-run
```

Résultat :
```
🔗 Bulk Create Relationships from CSV
CSV File: entities_mapping.csv

✓ Generated 3 relationship(s)

Preview:
  1. d286692e... → 90d14acb... (Objet Information_Table_Has)
  2. d286692e... → 8c680380... (Objet Information_Table_Has)
  3. d286692e... → autre-gui... (Objet Information_Process_Has)

[DRY RUN] Relationships would be created with the above data
```

#### 3. Créer les relations

```bash
pvw relationship bulk-create-csv --csv-file entities_mapping.csv
```

#### 4. Optionnel: Sauvegarder le JSON généré

```bash
pvw relationship bulk-create-csv --csv-file entities_mapping.csv --output-json relationships.json
```

### Avantages ✨
- **La solution la plus simple**
- Une seule commande
- Aperçu intégré avant création
- Validation du CSV automatique
- Formatage coloré et lisible
- Parfait pour l'automatisation et les scripts

### Options disponibles

| Option | Description | Exemple |
|--------|-------------|---------|
| `--csv-file` | **Requis** - Fichier CSV avec les mappings | `--csv-file entities_mapping.csv` |
| `--output-json` | Optionnel - Sauvegarder le JSON généré | `--output-json relationships.json` |
| `--dry-run` | Aperçu sans créer les relations | `--dry-run` |

---

Automatisez la génération des relations à partir d'un fichier CSV (approche avancée).

### Étapes

#### 1. Créer le fichier CSV de mapping

Créez un fichier `entities_mapping.csv` :

```csv
info_object_guid,target_entity_guid,target_entity_type,relationship_type
d286692e-30bb-48ba-ac49-f7372b12d225,90d14acb-cf75-4729-9245-68f6f6f60000,mssql_table,Objet Information_Table_Has
d286692e-30bb-48ba-ac49-f7372b12d225,8c680380-f21a-4a88-8651-06f6f6f60000,mssql_table,Objet Information_Table_Has
d286692e-30bb-48ba-ac49-f7372b12d225,autre-guid-process,mssql_procedure,Objet Information_Process_Has
```

**Colonnes CSV :**
- `info_object_guid` : GUID de l'objet d'information
- `target_entity_guid` : GUID de l'entité cible
- `target_entity_type` : Type de l'entité (mssql_table, mssql_procedure, etc.)
- `relationship_type` : Type de relation (Objet Information_Table_Has, etc.)

#### 2. Créer le script Python

Créez un fichier `create_relationships.py` :

```python
#!/usr/bin/env python3
"""
Script pour automatiser la création de relations entre objets d'information
et différentes entités dans Microsoft Purview.
"""

import json
import csv
import subprocess
import sys
from pathlib import Path

def read_csv_mapping(csv_file):
    """
    Lire le fichier CSV de mapping et retourner une liste de relations.
    
    Args:
        csv_file: Chemin vers le fichier CSV
        
    Returns:
        Liste des relations à créer
    """
    relationships = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                relationship = {
                    "typeName": row['relationship_type'],
                    "end1": {
                        "guid": row['info_object_guid'],
                        "typeName": "Objet Information"
                    },
                    "end2": {
                        "guid": row['target_entity_guid'],
                        "typeName": row['target_entity_type']
                    }
                }
                relationships.append(relationship)
        print(f"✓ {len(relationships)} relations lues depuis {csv_file}")
        return relationships
    except FileNotFoundError:
        print(f"✗ Fichier non trouvé: {csv_file}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Erreur lors de la lecture du CSV: {e}")
        sys.exit(1)

def save_relationships_json(relationships, output_file):
    """
    Sauvegarder les relations dans un fichier JSON.
    
    Args:
        relationships: Liste des relations
        output_file: Chemin du fichier de sortie
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(relationships, f, indent=2, ensure_ascii=False)
        print(f"✓ Relations sauvegardées dans {output_file}")
    except Exception as e:
        print(f"✗ Erreur lors de la sauvegarde: {e}")
        sys.exit(1)

def create_relationships_bulk(json_file):
    """
    Créer les relations en utilisant la commande CLI pvw.
    
    Args:
        json_file: Chemin du fichier JSON avec les relations
    """
    try:
        print(f"\n🔗 Création des relations en masse...")
        result = subprocess.run(
            ['pvw', 'relationship', 'create', '--payload-file', json_file],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print("✓ Création réussie!")
            print(result.stdout)
        else:
            print("✗ Erreur lors de la création:")
            print(result.stderr)
            sys.exit(1)
    except FileNotFoundError:
        print("✗ Commande 'pvw' non trouvée. Assurez-vous que pvw-cli est installé.")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Erreur: {e}")
        sys.exit(1)

def main():
    """Fonction principale"""
    print("=" * 60)
    print("Automatisation des Relations - Microsoft Purview")
    print("=" * 60)
    
    # Paramètres
    csv_file = 'entities_mapping.csv'
    json_file = 'relationships.json'
    
    # Vérifier que le fichier CSV existe
    if not Path(csv_file).exists():
        print(f"✗ Fichier CSV non trouvé: {csv_file}")
        sys.exit(1)
    
    # Étape 1: Lire le CSV
    print(f"\n📄 Lecture du fichier CSV: {csv_file}")
    relationships = read_csv_mapping(csv_file)
    
    # Étape 2: Sauvegarder en JSON
    print(f"\n💾 Génération du fichier JSON: {json_file}")
    save_relationships_json(relationships, json_file)
    
    # Étape 3: Créer les relations
    print()
    create_relationships_bulk(json_file)
    
    print("\n✓ Processus complété avec succès!")
    print(f"  - {len(relationships)} relations créées")
    print(f"  - Fichier JSON: {json_file}")

if __name__ == '__main__':
    main()
```

#### 3. Exécuter le script

```bash
# Rendre le script exécutable (sur Linux/Mac)
chmod +x create_relationships.py

# Exécuter
python create_relationships.py
```

#### 4. Résultats

Le script va :
1. Lire le fichier `entities_mapping.csv`
2. Générer un fichier `relationships.json`
3. Créer toutes les relations via la commande `pvw relationship create`
4. Afficher un résumé des opérations

---

## Commandes Disponibles

### Créer une ou plusieurs relations

```bash
# Relation individuelle
pvw relationship create --payload-file relationship.json

# Relations en masse
pvw relationship create --payload-file bulk_relationships.json
```

### ⭐ Créer à partir d'un fichier CSV (NOUVEAU!)

**Commande simplifiée et recommandée:**

```bash
# Création simple depuis CSV
pvw relationship bulk-create-csv --csv-file entities_mapping.csv

# Avec prévisualisation avant création (dry-run)
pvw relationship bulk-create-csv --csv-file entities_mapping.csv --dry-run

# Sauvegarder le JSON généré
pvw relationship bulk-create-csv --csv-file entities_mapping.csv --output-json generated_relationships.json

# Tout ensemble: Aperçu, Sauvegarde et Création
pvw relationship bulk-create-csv --csv-file entities_mapping.csv --output-json relationships.json
```

**Options:**
- `--csv-file` (requis): Chemin vers le fichier CSV
- `--output-json`: Optionnel, sauvegarde les relations générées en JSON
- `--dry-run`: Aperçu sans créer les relations

### Lire une relation

```bash
pvw relationship read --guid <relationship-guid>

# Avec informations étendues
pvw relationship read --guid <relationship-guid> --extended-info
```

### Mettre à jour une relation

```bash
pvw relationship put --payload-file relationship.json
```

### Supprimer une relation

```bash
pvw relationship delete --guid <relationship-guid>
```

### Afficher l'aide

```bash
pvw relationship --help

# Aide spécifique pour bulk-create-csv
pvw relationship bulk-create-csv --help
```

---

## Exemples Pratiques

### Exemple 1: Utiliser la nouvelle commande `bulk-create-csv` (PLUS SIMPLE!)

**Fichier CSV: `entities_mapping.csv`**

```csv
info_object_guid,target_entity_guid,target_entity_type,relationship_type
d286692e-30bb-48ba-ac49-f7372b12d225,90d14acb-cf75-4729-9245-68f6f6f60000,mssql_table,Objet Information_Table_Has
d286692e-30bb-48ba-ac49-f7372b12d225,8c680380-f21a-4a88-8651-06f6f6f60000,mssql_table,Objet Information_Table_Has
```

**Commandes:**

```bash
# 1. Aperçu avant création
pvw relationship bulk-create-csv --csv-file entities_mapping.csv --dry-run

# 2. Créer les relations directement
pvw relationship bulk-create-csv --csv-file entities_mapping.csv

# 3. Ou créer + Sauvegarder le JSON généré
pvw relationship bulk-create-csv --csv-file entities_mapping.csv --output-json relationships.json
```

**Résultat:**
```
🔗 Bulk Create Relationships from CSV
CSV File: entities_mapping.csv

✓ Generated 2 relationship(s)

Preview:
  1. d286692e... → 90d14acb... (Objet Information_Table_Has)
  2. d286692e... → 8c680380... (Objet Information_Table_Has)

Creating relationships...
  ✓ Created: Objet Information_Table_Has
  ✓ Created: Objet Information_Table_Has

Summary:
  Created: 2/2
```

### Exemple 2: Lier un objet d'information à plusieurs tables

**Fichier: `multiple_tables.json`**

```json
[
  {
    "typeName": "Objet Information_Table_Has",
    "end1": {
      "guid": "d286692e-30bb-48ba-ac49-f7372b12d225",
      "typeName": "Objet Information"
    },
    "end2": {
      "guid": "90d14acb-cf75-4729-9245-68f6f6f60000",
      "typeName": "mssql_table"
    },
    "attributes": {
      "name": "Personne morale - INTRVEX"
    }
  },
  {
    "typeName": "Objet Information_Table_Has",
    "end1": {
      "guid": "d286692e-30bb-48ba-ac49-f7372b12d225",
      "typeName": "Objet Information"
    },
    "end2": {
      "guid": "8c680380-f21a-4a88-8651-06f6f6f60000",
      "typeName": "mssql_table"
    },
    "attributes": {
      "name": "Personne morale - APPINEX"
    }
  }
]
```

**Commande:**
```bash
pvw relationship create --payload-file multiple_tables.json
```

### Exemple 2: Lier plusieurs objets d'information à une seule table

**Fichier: `multiple_info_objects.json`**

```json
[
  {
    "typeName": "Objet Information_Table_Has",
    "end1": {
      "guid": "guid-info-object-1",
      "typeName": "Objet Information"
    },
    "end2": {
      "guid": "90d14acb-cf75-4729-9245-68f6f6f60000",
      "typeName": "mssql_table"
    }
  },
  {
    "typeName": "Objet Information_Table_Has",
    "end1": {
      "guid": "guid-info-object-2",
      "typeName": "Objet Information"
    },
    "end2": {
      "guid": "90d14acb-cf75-4729-9245-68f6f6f60000",
      "typeName": "mssql_table"
    }
  }
]
```

### Exemple 3: Réseau complexe de relations

**Fichier CSV: `complex_mapping.csv`**

```csv
info_object_guid,target_entity_guid,target_entity_type,relationship_type
d286692e-30bb-48ba-ac49-f7372b12d225,90d14acb-cf75-4729-9245-68f6f6f60000,mssql_table,Objet Information_Table_Has
d286692e-30bb-48ba-ac49-f7372b12d225,8c680380-f21a-4a88-8651-06f6f6f60000,mssql_table,Objet Information_Table_Has
d286692e-30bb-48ba-ac49-f7372b12d225,guid-procedure-1,mssql_procedure,Objet Information_Process_Has
guid-info-object-2,90d14acb-cf75-4729-9245-68f6f6f60000,mssql_table,Objet Information_Table_Has
guid-info-object-2,guid-view-1,mssql_view,Objet Information_Has
```

**Exécution:**
```bash
python create_relationships.py
```

---

## Bonnes Pratiques

### ✓ À Faire

1. **Valider les GUIDs** avant de créer les relations
2. **Tester avec une petite relation** d'abord
3. **Garder le fichier JSON** pour traçabilité
4. **Utiliser la solution Bulk** pour de nombreuses relations
5. **Automatiser avec des scripts** pour des mises à jour régulières

### ✗ À Éviter

1. Ne pas utiliser de GUIDs invalides
2. Ne pas créer de relations en doublons
3. Ne pas modifier manuellement les fichiers JSON générés
4. Ne pas ignorer les erreurs lors de la création

---

## Dépannage

### Erreur: "GUID invalide"

```
Error: Invalid GUID format
```

**Solution:** Vérifiez que les GUIDs sont au format correct (UUID v4)

### Erreur: "Relation déjà existante"

```
Error: Relationship already exists
```

**Solution:** Vérifiez que la relation n'existe pas déjà avant de la créer

### Erreur: "Type de relation non reconnu"

```
Error: Unknown relationship type
```

**Solution:** Utilisez `pvw entity read --guid <guid>` pour voir les types de relations supportés

### La commande `pvw` n'est pas trouvée

```
Error: 'pvw' command not found
```

**Solution:** Installez ou mettez à jour pvw-cli:
```bash
pip install --upgrade pvw-cli
```

---

## Performance et Optimisation

### Pour des milliers de relations

1. **Divisez en lots** de 100-500 relations par fichier
2. **Utilisez l'option Bulk** (Solution 2)
3. **Automatisez avec Python** (Solution 3)
4. **Ajoutez des délais** entre les créations pour éviter le throttling

### Script pour diviser en lots

```python
import json

# Charger le fichier JSON
with open('relationships.json', 'r') as f:
    relationships = json.load(f)

# Diviser en lots de 100
batch_size = 100
for i in range(0, len(relationships), batch_size):
    batch = relationships[i:i+batch_size]
    filename = f'relationships_batch_{i//batch_size + 1}.json'
    with open(filename, 'w') as f:
        json.dump(batch, f, indent=2)
    print(f"Créé: {filename}")
```

---

## Ressources Additionnelles

- [Documentation Microsoft Purview - Relationships API](https://learn.microsoft.com/en-us/rest/api/purview/datamapdataplane/relationship)
- [pvw-cli GitHub Repository](https://github.com/Keayoub/pvw-cli)
- [Entity Types in Purview](https://learn.microsoft.com/en-us/purview/tutorial-classifications-author)

---

**Dernière mise à jour:** 2026-05-11

