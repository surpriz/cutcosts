# Guide de Résolution - Erreur Alembic Migration

## Problème Rencontré

### Symptôme
```
ERROR [alembic.util.messaging] Can't locate revision identified by '004_payment_reminders'
FAILED: Can't locate revision identified by '004_payment_reminders'
```

### Cause
La table `alembic_version` de la base de données en production contient une référence à une migration (`004_payment_reminders`) qui a été supprimée du code source.

Cela se produit quand :
1. Une migration a été créée et appliquée en production
2. Cette migration a ensuite été supprimée du code (ou renommée)
3. La base de données pointe toujours vers l'ancienne migration

## Solution Rapide

### Étape 1: Connexion au VPS

```bash
ssh administrator@VPS_IP
cd /opt/cloudwaste
```

### Étape 2: Exécuter le script de réparation

```bash
bash deployment/fix-alembic-version.sh
```

Ce script va :
1. ✅ Vérifier la version actuelle dans `alembic_version`
2. ✅ Remplacer `004_payment_reminders` par `003_add_password_reset`
3. ✅ Vérifier que les migrations sont synchronisées
4. ✅ Appliquer les migrations manquantes si nécessaire

### Étape 3: Redéployer

```bash
bash deployment/zero-downtime-deploy.sh
```

## Solution Manuelle (si le script échoue)

### Option A: Via SQL Direct

```bash
# 1. Charger les variables d'environnement
cd /opt/cloudwaste
source .env.prod

# 2. Vérifier la version actuelle
docker compose -f deployment/docker-compose.prod.yml exec postgres psql -U cloudwaste -d cloudwaste -c "SELECT * FROM alembic_version;"

# 3. Mettre à jour vers la bonne version
docker compose -f deployment/docker-compose.prod.yml exec postgres psql -U cloudwaste -d cloudwaste -c "UPDATE alembic_version SET version_num = '003_add_password_reset';"

# 4. Vérifier la mise à jour
docker compose -f deployment/docker-compose.prod.yml exec postgres psql -U cloudwaste -d cloudwaste -c "SELECT * FROM alembic_version;"
```

### Option B: Via Alembic Stamp

```bash
# 1. Stamp la base avec la bonne version (sans appliquer de changements)
docker compose -f deployment/docker-compose.prod.yml run --rm backend alembic stamp 003_add_password_reset

# 2. Vérifier
docker compose -f deployment/docker-compose.prod.yml run --rm backend alembic current

# 3. Appliquer les migrations manquantes
docker compose -f deployment/docker-compose.prod.yml run --rm backend alembic upgrade head
```

## Vérification Post-Fix

### 1. Vérifier la version Alembic

```bash
docker compose -f deployment/docker-compose.prod.yml run --rm backend alembic current
```

**Attendu:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
003_add_password_reset (head)
```

### 2. Vérifier les migrations

```bash
docker compose -f deployment/docker-compose.prod.yml run --rm backend alembic check
```

**Attendu:**
```
Target database is up to date
```

### 3. Tester le backend

```bash
curl https://cutcosts.tech/api/v1/health
```

**Attendu:** HTTP 200

## Chaîne de Migrations Actuelle

Voici l'ordre correct des migrations (dernier commit bd49d1b) :

```
34cd18400c61 (base) → create_users_table
ea68df898a6b → create_cloud_accounts_table
92aa66830ad2 → create_scans_and_orphan_resources_tables
4661d3e99224 → add_detection_rules_table
4841b81d124e → add_scheduled_scan_settings
8bfa51fe1573 → add_attached_volume_detection_rules
0b5aea06d0d5 → add_azure_public_ip_detection_rule
4766abf4c8b9 → add_phase1_detection_rules_azure
5a7f3b9c2e4d → add_vm_phase_a_detection_rules_azure
80509e943789 → add_resource_groups_to_cloud_accounts
f9e2c8d4a1b3 → add_chat_tables
cb0146578cde → add_email_verification_fields

# Deux branches parallèles :
│
├─→ 509cd9b0ecb0 → add_email_scan_notifications_field
│   └─→ 4e275083c57b → add_pricing_cache_table
│       └─→ da2ffc63d747 → add_microsoft365_provider_support
│           └─→ a1b2c3d4e5f6 → add_ml_data_collection_tables
│               ├─→ 202511111200 → add_celery_task_id_to_scan
│               └─→ b2c3d4e5f6a7 → add_all_cloud_resources_table
│                   └─→ c3d4e5f6a7b8 → merge_heads (202511111200 + b2c3d4e5f6a7)
│                       └─→ e69a1f8c1fa1 → add_inventory_scan_type
│
└─→ add_subscription_tables (001_add_subscriptions) → add subscription tables

# Merge final :
002_merge_heads → merge (001_add_subscriptions + e69a1f8c1fa1)
003_add_password_reset → add password reset fields (HEAD)
```

## Comment Éviter ce Problème à l'Avenir

### ❌ NE JAMAIS FAIRE

1. **Supprimer une migration après l'avoir appliquée en production**
   ```bash
   # DANGER - Ne jamais faire ça !
   git rm backend/alembic/versions/004_payment_reminders.py
   git commit -m "remove migration"
   ```

2. **Renommer une révision après l'avoir appliquée**
   ```python
   # DANGER - Ne jamais changer ça après application !
   revision: str = '004_payment_reminders'  # → '004_new_name'
   ```

### ✅ BONNE PRATIQUE

1. **Si une migration pose problème, créez un downgrade puis une nouvelle migration**
   ```bash
   # 1. Downgrade en production
   alembic downgrade -1

   # 2. Créez une nouvelle migration correcte
   alembic revision --autogenerate -m "fix previous migration"

   # 3. Appliquez la nouvelle
   alembic upgrade head
   ```

2. **Testez TOUJOURS les migrations en local avant production**
   ```bash
   # Local
   docker-compose exec backend alembic upgrade head
   docker-compose exec backend alembic downgrade -1
   docker-compose exec backend alembic upgrade head
   ```

3. **Gardez les migrations en production indéfiniment**
   - Une fois appliquée en prod, une migration doit rester dans le code
   - Même si vous n'en avez plus besoin
   - La base de données en a besoin pour la traçabilité

## Logs de Débogage

### Voir l'historique des migrations appliquées

```bash
docker compose -f deployment/docker-compose.prod.yml exec postgres psql -U cloudwaste -d cloudwaste -c "SELECT * FROM alembic_version;"
```

### Voir toutes les migrations disponibles

```bash
docker compose -f deployment/docker-compose.prod.yml run --rm backend alembic history
```

### Voir les migrations non appliquées

```bash
docker compose -f deployment/docker-compose.prod.yml run --rm backend alembic heads
docker compose -f deployment/docker-compose.prod.yml run --rm backend alembic current
```

## Support

Si le problème persiste :

1. **Consultez les logs du backend**
   ```bash
   docker logs cloudwaste_backend --tail 100
   ```

2. **Vérifiez l'état de la base de données**
   ```bash
   bash deployment/diagnose.sh
   ```

3. **Contactez l'équipe de développement** avec :
   - Logs complets du déploiement
   - Résultat de `alembic current`
   - Résultat de `SELECT * FROM alembic_version`

---

**Dernière mise à jour:** 2025-12-24
**Auteur:** Claude Code
**Statut:** Testé et validé
