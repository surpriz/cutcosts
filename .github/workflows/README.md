# Pipeline CI/CD CutCosts

Ce document explique l'architecture et le fonctionnement du pipeline CI/CD de CutCosts.

## Vue d'ensemble

Le pipeline automatise les tests et le déploiement à chaque push sur `master`:

```
Push sur master
      │
      ▼
┌─────────────────────────────────────────────────────────┐
│                      test.yml                           │
│  ┌──────────────────┐    ┌──────────────────┐          │
│  │  Backend Tests   │    │  Frontend Tests  │          │
│  │  - pytest        │    │  - npm lint      │          │
│  │  - coverage      │    │  - npm build     │          │
│  └──────────────────┘    └──────────────────┘          │
└─────────────────────────────┬───────────────────────────┘
                              │
              ❌ Échec        │        ✅ Succès
                 ↓            │            ↓
              [STOP]          │     ┌──────────────────────────────────────────────┐
              Pas de          │     │          deploy-production.yml               │
              déploiement     │     │  ┌────────────────┐  ┌────────────────────┐  │
                              │     │  │ Pre-Deploy     │→ │ Zero-Downtime      │  │
                              │     │  │ - disk space   │  │ - blue-green       │  │
                              │     │  │ - sentry sync  │  │ - health checks    │  │
                              │     │  └────────────────┘  └─────────┬──────────┘  │
                              │     │                                │             │
                              │     │                    ┌───────────┴─────────┐   │
                              │     │                    ▼                     ▼   │
                              │     │             ❌ Échec              ✅ Succès  │
                              │     │             [ROLLBACK]            [DEPLOYED] │
                              │     └──────────────────────────────────────────────┘
                              │
                              ▼
                       cutcosts.tech
```

---

## Workflows

### 1. `test.yml` - Tests Automatisés

**Fichier:** `.github/workflows/test.yml`

| Propriété | Valeur |
|-----------|--------|
| Déclencheur | Push sur `master`/`develop`, PR sur `master`, ou appelé par un autre workflow |
| Durée | ~4-5 minutes |
| Jobs | `backend-tests`, `frontend-tests` |

#### Backend Tests
- **Environnement:** Python 3.11, PostgreSQL 15, Redis 7
- **Actions:**
  1. Installation des dépendances (`requirements.txt` + `aiosqlite`)
  2. Linting avec `ruff` (non-bloquant)
  3. Tests avec `pytest` + couverture de code
  4. Upload rapport de couverture vers Codecov

#### Frontend Tests
- **Environnement:** Node.js 20
- **Actions:**
  1. Installation des dépendances (`npm ci`)
  2. Linting (`npm run lint`) - non-bloquant
  3. Type check (`npm run type-check`) - non-bloquant
  4. Build (`npm run build`) - **bloquant**

---

### 2. `deploy-production.yml` - Déploiement Production

**Fichier:** `.github/workflows/deploy-production.yml`

| Propriété | Valeur |
|-----------|--------|
| Déclencheur | Push sur `master` (après succès des tests) |
| Durée | ~2-3 minutes |
| Dépendance | `test.yml` doit passer |

#### Étapes de déploiement

1. **Run Tests** - Appelle `test.yml` et attend le succès
2. **Pre-Deploy Check**
   - Vérification de l'espace disque
   - Synchronisation des variables Sentry
3. **Zero-Downtime Deploy**
   - Connexion SSH au VPS
   - Blue-Green deployment
   - Health checks automatiques
4. **Post-Deployment Verification**
   - Vérification du frontend (HTTP 200)
   - Vérification de l'API health (`/api/v1/health`)

---

## Interprétation des résultats

### Sur GitHub Actions

Accédez aux runs via: **Actions** tab sur GitHub

#### Icônes de statut

| Icône | Signification |
|-------|---------------|
| ✅ Vert | Succès - tous les jobs ont passé |
| ❌ Rouge | Échec - un ou plusieurs jobs ont échoué |
| 🟡 Jaune | En cours d'exécution |
| ⚪ Gris | Annulé ou en attente |

#### Lecture des logs

1. Cliquez sur le workflow run
2. Sélectionnez le job qui a échoué
3. Développez l'étape qui a échoué (indiquée par ❌)
4. Les erreurs sont affichées en rouge dans les logs

### Scénarios courants

#### Tests Backend échouent
```
❌ Backend Tests
```
- Regardez les logs de l'étape "Run tests with coverage"
- Cherchez les `FAILED` tests
- Corrigez le code et re-pushez

#### Tests Frontend échouent
```
❌ Frontend Tests
```
- Généralement causé par l'étape "Build application"
- Erreurs TypeScript ou imports manquants
- Corrigez et re-pushez

#### Déploiement échoue
```
✅ Run Tests
❌ Deploy to VPS
```
- Le rollback est **automatique**
- L'application reste accessible (version précédente)
- Consultez les logs SSH pour identifier le problème

---

## Que faire en cas d'échec ?

### Tests échouent

1. **Ne pas paniquer** - le déploiement est bloqué, pas de risque pour la prod
2. **Lire les logs** - identifier le test ou l'étape qui échoue
3. **Corriger localement** - reproduire le problème, corriger
4. **Pusher la correction** - le pipeline se relance automatiquement

### Déploiement échoue

1. **L'application reste en ligne** - rollback automatique
2. **Consulter les logs SSH** - voir l'étape "Deploy to Production"
3. **Problèmes courants:**
   - Espace disque insuffisant → nettoyage Docker automatique
   - Health check échoue → vérifier les logs de l'application
   - Erreur de build → corriger le code

---

## Scripts associés

Ces scripts sont utilisés par le pipeline et peuvent être exécutés manuellement:

| Script | Emplacement | Description |
|--------|-------------|-------------|
| `zero-downtime-deploy.sh` | `deployment/` | Déploiement blue-green avec rollback |
| `smoke-tests.sh` | `deployment/` | Tests post-déploiement |
| `pre-deploy-check.sh` | `deployment/` | Validation des variables d'environnement |
| `sync-sentry-env.sh` | `deployment/` | Synchronisation des variables Sentry |

---

## Déploiement manuel

Si vous devez déclencher un déploiement manuellement:

1. Allez sur GitHub → Actions → "Deploy to Production"
2. Cliquez sur "Run workflow"
3. Sélectionnez la branche `master`
4. Cliquez sur "Run workflow"

Ou depuis la ligne de commande:
```bash
gh workflow run deploy-production.yml
```

---

## Configuration requise

### Secrets GitHub (Settings → Secrets → Actions)

| Secret | Description |
|--------|-------------|
| `VPS_HOST` | Adresse IP du serveur de production |
| `VPS_USER` | Utilisateur SSH pour le déploiement |
| `VPS_SSH_PRIVATE_KEY` | Clé SSH privée pour l'authentification |

### Variables d'environnement serveur

Les variables sont gérées dans `/opt/cloudwaste/.env` sur le serveur de production.

---

## Dépannage

### Le workflow ne se déclenche pas

- Vérifiez que vous pushez sur `master` ou `develop`
- Vérifiez que le fichier workflow est valide (pas d'erreur YAML)

### Tests passent localement mais échouent en CI

- Différences d'environnement (versions Python/Node)
- Variables d'environnement manquantes
- Base de données de test différente

### Déploiement timeout

- Vérifiez la connectivité SSH au serveur
- Vérifiez l'espace disque sur le serveur
- Le build Docker peut prendre du temps lors de grosses mises à jour

---

## Historique des changements

| Date | Changement |
|------|------------|
| 2025-12-09 | Ajout de `workflow_call` pour permettre l'appel par deploy-production.yml |
| 2025-12-08 | Création du pipeline CI/CD avec tests automatisés |
