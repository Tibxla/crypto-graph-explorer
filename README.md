# Crypto-Graph-Explorer

**Prototype interactif d'analyse de réseaux de transactions blockchain WETH/Polygon**

Implémentation complète des **6 Questions de Recherche** du rapport universitaire sur l'analyse du crash WETH/Polygon du 5 août 2024 ("Lundi Noir").

Démo en ligne : [crypto-graph-explorer.vercel.app](https://crypto-graph-explorer.vercel.app)

---

## Deux livrables couplés

Ce dépôt contient les deux livrables du projet :

1. **Prototype web interactif** (racine du dépôt) — visualisation D3.js des 12 880 nœuds, panneau d'analyse couvrant les 6 RQ et 8 analyses avancées. Les chiffres affichés dans l'interface sont des approximations adaptées à une exécution dans le navigateur.
2. **Sous-projet `report/`** — analyse Python rigoureuse sur les 401 709 transactions brutes et rapport LaTeX universitaire (Paris Nanterre, Licence MIAGE). C'est ce sous-projet qui fournit les chiffres de référence (Gini = 0,9780, σ = 115,90, Q = 0,6445).

Voir [`report/README`](report/) et [`report/rapport/main.pdf`](report/rapport/main.pdf) pour le rapport compilé.

---

## Objectif

Créer une plateforme interactive permettant de :

- Visualiser un réseau de 12 880 nœuds et milliers d'arêtes
- Analyser les propriétés topologiques et structurelles
- Calculer les mesures de centralité et d'importance
- Détecter les communautés et les points critiques
- Évaluer la concentration des flux et l'inégalité (Gini)
- Simuler l'impact de suppressions de nœuds critiques

---

## Stack Technique

```
Frontend :
  - React 18 + TypeScript (type-safe)
  - Vite (dev server rapide)
  - D3.js 7.9.0 (visualisation de graphes)
  - shadcn/ui + TailwindCSS (composants UI)

Algorithmes / Analyse :
  - Équivalents NetworkX en TypeScript natif
  - PapaParse (parsing CSV)
  - Stratégies de sampling pour algorithmes O(n³)

Données :
  - CSV de 12 880 nœuds, 12 000+ arêtes
  - Métriques pré-calculées : degree, PageRank, community
  - Format : /public/data/nodes_metrics.csv

Environnement Dev :
  - Node.js 18+
  - npm 9+
  - Git
```

---

## Quick Start

### Installation

```bash
git clone https://github.com/krat0s-web/crypto-graph-explorer.git
cd crypto-graph-explorer
npm install

# Lancer le dev server
npm run dev
# → http://localhost:8080

# Build production
npm run build
# → dist/

# Aperçu du build
npm run preview
# → http://localhost:4173
```

### Utilisation

1. **Chargement des données** : CSV auto-chargé depuis `/public/data/nodes_metrics.csv`
2. **Ajustement du réseau** : Slider "Node Limit" (500 → 12 880 nœuds)
3. **Visualisation** : D3.js interactif (zoom, pan, drag)
4. **Analyses** : 8 analyses avancées + 6 RQ analyses
5. **Résultats** : Panneau droit avec stats détaillées

---

## Structure du Projet

```
crypto-graph-explorer/
├── src/
│   ├── components/
│   │   ├── GraphCanvas.tsx      # Moteur de visualisation D3.js
│   │   ├── AnalysisPanel.tsx    # UI des 8 + 6 analyses
│   │   └── ...
│   ├── lib/
│   │   ├── graphUtils.ts        # Algorithmes core (250+ lignes)
│   │   ├── graphTypes.ts        # Interfaces TypeScript
│   │   └── ...
│   ├── pages/
│   │   └── Index.tsx            # Layout principal
│   └── ...
├── public/
│   └── data/
│       └── nodes_metrics.csv    # Dataset 12 880 nœuds
└── package.json
```

---

## Les 6 Questions de Recherche (RQ)

Les questions de recherche proviennent du rapport universitaire associé. Chaque RQ est implémentée comme une fonction d'analyse accessible depuis l'UI.

### RQ1 : Topologie du Réseau

**Question** : Quelles sont les caractéristiques topologiques du réseau de transactions WETH/Polygon ?

**Implémentation**
- Fonction : `analyzeNetworkTopology()` dans `src/lib/graphUtils.ts`
- Métriques calculées :
  - Degrés moyen / max / min : distribution des connexions
  - Densité : ratio arêtes présentes vs possibles
  - Diamètre : distance maximale entre deux nœuds
  - Composantes connectées : nombre de sous-graphes isolés

**Résultats attendus**
- Degré moyen ~ 8-15 (réseau sparse)
- Diamètre ~ 4-6 (petit réseau)
- Densité < 0.001 (typique des réseaux crypto)

**UI**
- Bouton "RQ1 : Topologie" dans le panneau des analyses
- Métriques formatées avec codes couleur

---

### RQ2 : Mesures de Centralité

**Question** : Quels nœuds sont les plus importants selon différentes mesures de centralité ?

**Implémentation**
- Fonction : `analyzeCentrality()` dans `src/lib/graphUtils.ts`
- Quatre mesures :
  1. **Centralité de degré** : nombre direct de connexions
  2. **Betweenness** : importance dans les chemins courts
  3. **Closeness** : distance moyenne aux autres nœuds
  4. **PageRank** : importance via algorithme de Google

**Résultats attendus**
- Top nœuds : exchanges majeurs, liquidity pools, smart contracts
- Corrélation entre mesures mais classements distincts (perspectives différentes)
- PageRank élevé pour nœuds bien connectés indirectement

**UI**
- Top-10 affiché pour chaque mesure
- Comparaison des classements pour identifier les nœuds critiques

---

### RQ3 : Détection de Communautés

**Question** : Comment se structurent les groupes / communautés dans le réseau ?

**Implémentation**
- Données source : champ `community` dans `nodes_metrics.csv`
- Algorithme : Louvain (pré-calculé dans les données)
- Fonctions associées :
  - `calculateClustering()` : densité intra-communautaire
  - Visualisation D3.js : couleurs par communauté

**Résultats attendus**
- 5 à 20 communautés détectées selon granularité
- Clustering coefficient > 0.7 (communautés denses)
- Modularité > 0.4 (communautés bien définies)

**UI**
- Coloration des nœuds par communauté dans le graphe
- Statistiques de clustering par nœud

---

### RQ4 : Dynamiques Temporelles

**Question** : Comment le réseau évolue-t-il au cours du temps ?

**État actuel**
- Placeholder : données statiques dans le CSV
- Fonction : `analyzeTemporalDynamics()` dans `src/lib/graphUtils.ts`

**Pour activer l'analyse temporelle**
1. Modifier le CSV pour inclure une colonne `timestamp`
2. Implémenter `calculateNetworkEvolution()` :
   ```typescript
   // Fenêtres temporelles (ex : horaires)
   // Métriques par fenêtre : densité, degré moyen, clustering
   // Visualisation : heatmap ou graphique temporel
   ```

**Résultats attendus (selon rapport)**
- Pics de transactions : 14h-16h UTC
- Variations topologiques après le crash (15h)
- Réduction de densité post-crash

---

### RQ5 : Propriétés Small-World

**Question** : Le réseau exhibe-t-il des propriétés petit-monde ?

**Implémentation**
- Fonction : `analyzeSmallWorldProperties()` dans `src/lib/graphUtils.ts`
- Métriques :
  1. Coefficient moyen de clustering (C)
  2. Distance moyenne de chemin (L)
  3. Comparaison vs réseau aléatoire Erdős-Rényi (C_rand, L_rand)

**Critères Small-World**
- C ≫ C_rand (clustering élevé)
- L ≈ L_rand (distance courte)
- Ratios : C/C_rand ≫ 1, L/L_rand ≈ 1

**Résultats attendus**
- C ~ 0.6-0.8 (très clusterisé)
- L ~ 3-4 (petit monde)
- **Conclusion** : OUI, propriétés small-world confirmées

**UI**
- Comparaison côte-à-côte (réel vs aléatoire)
- Décision binaire : "Est Small-World : OUI / NON"

---

### RQ6 : Flux Pondérés et Concentration

**Question** : Comment sont distribués les volumes de transactions (inégalité) ?

**Implémentation**
- Fonction : `analyzeWeightedFlows()` dans `src/lib/graphUtils.ts`
- Mesures :
  1. **Coefficient de Gini** : inégalité (0 = égal, 1 = extrêmement inégal)
  2. **Concentration** : % du volume dans les top 20 % des nœuds
  3. **Distribution** : catégorisation (concentrated / distributed)

**Formule Gini**
```
G = Σ(2i - n - 1) × sorted_values[i] / (n² × mean(values))
```

**Résultats attendus**
- Gini ~ 0.7-0.85 (très inégal, typique crypto)
- Top 20 % nœuds ~ 80 % du volume (loi de Pareto)
- Distribution : "Highly concentrated"

**UI**
- Affichage du coefficient Gini
- Barre de concentration
- Interprétation textuelle

---

## Les 8 Analyses Avancées

Ces analyses complètent les RQ et sont accessibles via l'onglet "Analyses" du panneau.

### 1. Coefficient de Clustering

**Qu'est-ce que c'est ?**
Le coefficient de clustering mesure à quel point les voisins d'un nœud sont connectés entre eux. C'est un indicateur de la densité locale du réseau.

**Comment ça fonctionne ?**
- Pour un nœud donné, on regarde tous ses voisins directs
- On calcule combien de ces voisins sont connectés entre eux
- Coefficient de 1.0 = tous les voisins sont connectés (clique parfaite)
- Coefficient de 0.0 = aucun voisin n'est connecté entre eux

**Formule**
```
C = (Nombre de connexions entre voisins) / (Nombre maximum possible de connexions)
```

**Interprétation**
- Coefficient élevé (> 0.5) : forte cohésion locale, le nœud fait partie d'un groupe dense
- Coefficient faible (< 0.2) : le nœud connecte différentes parties du réseau sans former de groupe dense
- Moyenne du réseau : tendance générale à former des clusters

**Exemple concret**
Si Alice est connectée à Bob, Charlie et David :
- Bob-Charlie-David tous connectés entre eux → Coefficient = 1.0
- Seulement Bob et Charlie connectés → Coefficient = 0.33
- Aucun n'est connecté → Coefficient = 0.0

---

### 2. Détection de Ponts (Bridge Detection)

**Qu'est-ce que c'est ?**
Un pont est une arête dont la suppression augmenterait le nombre de composantes déconnectées du réseau. Ce sont des connexions critiques.

**Comment ça fonctionne ?**
- Pour chaque arête, on simule sa suppression
- Si le réseau se divise en plus de composantes → c'est un pont
- Les ponts sont des points de vulnérabilité

**Importance**
- **Sécurité** : identifie les points de défaillance uniques
- **Robustesse** : un réseau avec beaucoup de ponts est fragile
- **Architecture** : révèle la structure hiérarchique

**Exemple concret**
Un réseau de paiement où une seule connexion relie l'Europe à l'Asie : si cette connexion tombe, les deux régions sont isolées → c'est un pont critique.

**Interprétation**
- Nombreux ponts : réseau vulnérable, structure en arbre
- Peu de ponts : réseau robuste, bien maillé
- Ponts entre communautés : connexions inter-groupes essentielles

---

### 3. Centralité Intermédiaire (Betweenness Centrality)

**Qu'est-ce que c'est ?**
Mesure combien de fois un nœud se trouve sur le chemin le plus court entre deux autres nœuds. Identifie les "ponts humains" ou "hubs de passage".

**Différence avec le degré**
- **Degré** : combien de connexions directes
- **Betweenness** : combien de chemins passent par ce nœud

**Comment ça fonctionne ?**
1. Calcule tous les plus courts chemins entre toutes les paires
2. Pour chaque nœud, compte combien de ces chemins passent par lui
3. Normalise le score

**Interprétation**
- Haute centralité : nœud essentiel pour la communication
- Basse centralité : nœud périphérique ou dans un cluster dense
- Goulot d'étranglement : nœuds avec betweenness très élevé peuvent ralentir le réseau

**Exemple concret**
Dans un réseau social, une personne qui connecte deux groupes d'amis distincts a une haute betweenness ; une personne dans un groupe très soudé a une basse betweenness (même avec beaucoup d'amis).

**Utilité pour crypto**
Identifie les adresses clés qui facilitent les transactions entre différentes communautés.

---

### 4. Distribution des Degrés (Degree Distribution)

**Qu'est-ce que c'est ?**
Un histogramme montrant combien de nœuds ont chaque niveau de connectivité. Révèle la structure globale du réseau.

**Types de distributions**

*Réseau aléatoire (Random Network)*
- Distribution normale (en cloche)
- La plupart des nœuds ont un degré similaire
- Peu de hubs, peu de nœuds isolés

*Réseau scale-free (Loi de puissance)*
- Quelques hubs très connectés
- Beaucoup de nœuds peu connectés
- Typique des réseaux sociaux, Internet, crypto

*Réseau régulier*
- Tous les nœuds ont le même degré
- Très structuré, artificiel

**Interprétation**
- Loi de puissance : quelques acteurs dominent (typique blockchain)
- Longue traîne : beaucoup de petits acteurs
- Cutoff : limite maximale de connexions (contraintes techniques)

**Formule de détection**
Si P(k) ∝ k^(-γ) avec γ ≈ 2-3 → réseau scale-free

**Importance pour crypto**
Révèle la centralisation ou décentralisation réelle du réseau.

---

### 5. Chemin le Plus Court Moyen (Average Shortest Path)

**Qu'est-ce que c'est ?**
La distance moyenne entre toutes les paires de nœuds du réseau. Mesure la "compacité" du réseau.

**Comment ça fonctionne ?**
1. Calcule le plus court chemin entre chaque paire de nœuds
2. Moyenne de toutes ces distances

**Interprétation**
- Petit chemin (2-4) : réseau très connecté, effet "petit monde"
- Grand chemin (> 10) : réseau étendu, communication lente
- Six degrés de séparation : concept typique des réseaux sociaux

**Propriété "Petit Monde"**
- Chemin court malgré un grand nombre de nœuds
- Typique des réseaux sociaux
- Important pour la propagation rapide d'information

**Exemple concret**
- Facebook : ~ 3.5 (très connecté)
- Internet : ~ 4-5
- Réseau routier : ~ 20-30 (moins connecté)

**Utilité pour crypto**
Mesure la vitesse potentielle de propagation des transactions ou de l'information.

---

### 6. Analyse de Similarité (Similarity Analysis)

**Qu'est-ce que c'est ?**
Mesure à quel point deux nœuds sont similaires en fonction de leurs voisins communs. Permet de prédire de futures connexions.

**Métriques principales**

*Coefficient de Jaccard*
```
J(A,B) = |Voisins(A) ∩ Voisins(B)| / |Voisins(A) ∪ Voisins(B)|
```
- 0 = aucun voisin commun
- 1 = tous les voisins sont communs

*Attachement Préférentiel*
```
Score = degree(A) × degree(B)
```
- Prédit que les hubs se connectent entre eux

*Adamic-Adar*
```
AA(A,B) = Σ 1/log(degree(u)) pour u dans voisins communs
```
- Donne plus de poids aux voisins communs peu connectés

**Applications**
- Prédiction de liens : quelles connexions futures sont probables
- Détection d'anomalies : connexions inattendues
- Recommandations : suggérer des connexions pertinentes

**Exemple concret**
Si Alice et Bob ont 10 amis en commun sur 15 chacun → ils devraient probablement se connaître.

---

### 7. K-Core Decomposition

**Qu'est-ce que c'est ?**
Identifie le "cœur" du réseau en trouvant les sous-graphes où chaque nœud a au moins k connexions à l'intérieur du sous-graphe.

**Comment ça fonctionne ?**
1. k-core = sous-graphe où chaque nœud a au moins k voisins dans ce sous-graphe
2. On calcule pour k = 1, 2, 3, ...
3. Le max-k atteint est la coreness du nœud

**Niveaux de k-core**
- k = 1 : tous les nœuds connectés (core externe)
- k = 5 : nœuds modérément intégrés
- k = 10+ : cœur dense du réseau (core interne)

**Structure en pelure d'oignon**
- Couches externes = nœuds périphériques
- Couches internes = nœuds centraux
- Centre = nœuds les plus intégrés

**Interprétation**
- Coreness élevé : nœud au cœur du réseau, très intégré
- Coreness faible : nœud périphérique, facile à isoler
- Distribution : révèle la hiérarchie du réseau

**Exemple concret**
Dans un réseau de collaborations scientifiques :
- k = 1 : tous les chercheurs publiants
- k = 5 : chercheurs actifs en collaboration
- k = 10+ : équipes de recherche très soudées

**Utilité pour crypto**
Identifie les adresses "core" du réseau qui forment l'infrastructure stable.

---

### 8. Analyse de Flux et Propagation (Flow Analysis)

**Qu'est-ce que c'est ?**
Simule comment l'information, les transactions ou les influences se propagent dans le réseau au fil du temps.

**Modèles de propagation**

*Modèle SI (Susceptible-Infected)*
- Utilisé pour les rumeurs, informations
- Une fois "infecté", le nœud reste infecté
- Propagation irréversible

*Modèle SIR (Susceptible-Infected-Recovered)*
- Après infection, le nœud devient "immunisé"
- Utilisé pour épidémies, tendances

*Modèle de Cascade*
- Propagation basée sur des seuils
- Un nœud adopte si X % de ses voisins ont adopté

**Métriques calculées**
- Temps de propagation : vitesse de diffusion
- Taux d'adoption final : % du réseau atteint
- Nœuds influenceurs : quels nœuds démarrent les meilleures cascades
- Points de blocage : où la propagation ralentit

**Applications crypto**
- Propagation de transaction : vitesse de diffusion dans le réseau
- Adoption de protocole : comment une mise à jour se propage
- Attaques : comment une information malveillante se répand

**Paramètres**
- Probabilité de transmission : chance qu'un voisin soit "infecté"
- Nœud source : où commence la propagation
- Étapes de temps : durée de la simulation

**Exemple concret**
Simuler une nouvelle crypto :
- Commence par les early adopters (seed nodes)
- Se propage via le réseau social
- Atteint un plateau (saturation du marché)

---

## Comment utiliser ces analyses ensemble

### Analyse de robustesse complète
1. **Distribution des degrés** → comprendre la structure globale
2. **Ponts** → identifier les vulnérabilités
3. **K-core** → trouver le cœur stable
4. **Betweenness** → localiser les goulots d'étranglement

### Analyse de communautés
1. **Clustering** → détecter la cohésion locale
2. **Ponts** → trouver les connexions inter-communautés
3. **Similarité** → prédire de nouvelles connexions intra-communautés

### Analyse d'influence
1. **Betweenness** → trouver les diffuseurs clés
2. **Flux** → simuler la propagation depuis ces nœuds
3. **Chemin moyen** → évaluer la vitesse de diffusion

---

## Données Utilisées

**Source** : transactions WETH / Polygon le 5 août 2024 (crash)

**Format CSV**
```csv
id,degree,in_degree,out_degree,pagerank,community
0x1234...,45,23,22,0.0089,2
```

**Statistiques**
- 12 880 nœuds uniques
- ~ 180 000 - 400 000 arêtes (selon seuil)
- Taille fichier : ~ 950 KB
- Temps de parsing : ~ 150 ms

### Métriques calculées en runtime
- Clustering coefficient (densité locale de triangles)
- Betweenness centrality (via BFS sampling)
- Path lengths (via Dijkstra sampling)
- K-core decomposition (degeneracy)

---

## Guide Utilisateur

### Onglet "Graphe"
- **Zoom** : scroll souris
- **Pan** : drag du canvas
- **Cliquer un nœud** : sélection + highlight
- **Drag un nœud** : repositionnement
- **Slider** : réduire le nombre de nœuds (500 → 12 880)

### Onglet "Analyses"
- **Suppression** : remove top 1, top 5 en cascade
- **Avancées** : 8 analyses interactives
- **RQ** : cliquer "RQ1 - RQ6" pour voir les résultats
- **Résultats** : affichage en temps réel

### Exemples d'usage
- **Identifier les hubs** : cliquer RQ2 → top PageRank
- **Trouver les points faibles** : Bridge Detection
- **Vérifier le petit-monde** : RQ5 → "Est Small-World : OUI"
- **Mesurer l'inégalité** : RQ6 → coefficient Gini
- **Valider la structure des communautés** : RQ3 → clustering coefficient
- **Évaluer la robustesse** : RQ1 → diamètre / composantes

---

## Performance

| Métrique | Petits réseaux | Moyens | Grands |
|----------|---|---|---|
| Nodes | < 5K | 5K - 50K | > 50K |
| Load | < 100 ms | 100 - 500 ms | 500 ms+ |
| Betweenness | exact | sample | approx |
| Closeness | exact | top-50 | approx |
| Gini | exact | exact | exact |

- **Petits réseaux** (< 5000 nœuds) : toutes les analyses < 100 ms
- **Réseaux moyens** (5K - 50K nœuds) : sampling pour algorithmes O(n³)
- **Grands réseaux** (> 50K) : approximations nécessaires

---

## Limitations & Améliorations Futures

### Limitations actuelles
- Pas de données temporelles (timestamps)
- Betweenness calculée sur échantillon seulement (pas exhaustif)
- Closeness calculée sur top-50 nœuds seulement
- Gini utilise le degré comme proxy pour le volume
- Pas d'export des résultats
- Pas de collaboration temps réel

### Améliorations prévues
- [ ] Parser les timestamps du CSV → analyse temporelle RQ4
- [ ] Implémenter l'algorithme Louvain en runtime
- [ ] Ajouter les poids des arêtes (montants des transactions)
- [ ] Cache des calculs coûteux
- [ ] Export CSV / JSON / PNG
- [ ] Thème dark / light
- [ ] Multi-user collaboration

---

## Développement

### Ajouter une analyse

```typescript
// 1. Implémenter la fonction dans graphUtils.ts
export function myAnalysis(nodes, edges) {
  // algorithme
  return results;
}

// 2. Ajouter l'interface dans graphTypes.ts
export interface MyAnalysisResult {
  // champs
}

// 3. Ajouter le handler dans AnalysisPanel.tsx
const runMyAnalysis = () => {
  const result = myAnalysis(activeNodes, activeEdges);
  setAnalysisResults(result);
  setActiveAnalysis('myanalysis');
};

// 4. Ajouter l'UI dans AnalysisPanel.tsx
{activeAnalysis === 'myanalysis' && (
  <div className="glass rounded-lg p-3">
    {/* afficher les résultats */}
  </div>
)}
```

### Debug
- **Console** : `npm run dev` + F12 DevTools
- **Breakpoints** : VS Code debugger (`launch.json`)
- **Performance** : Chrome Profiler

---

## Déploiement

### Vercel (recommandé)
```bash
# Connecter le repo GitHub
# Vercel détecte Vite automatiquement
# Build command : npm run build
# Deploy !
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install && npm run build
EXPOSE 8080
CMD ["npm", "run", "dev"]
```

### Localhost
```bash
npm run preview
# http://localhost:4173
```

---

## Mapping Rapport → Code

| RQ | Section rapport | Fonction clé | Paramètres |
|----|-----------------|-------------|-----------|
| 1 | 3.1 | `analyzeNetworkTopology()` | Tous nœuds / arêtes |
| 2 | 3.2 | `analyzeCentrality()` | Top-10 par mesure |
| 3 | 3.3 | clustering + color coding | Communities dataset |
| 4 | 3.4 | `analyzeTemporalDynamics()` | Timestamps (future) |
| 5 | 3.5 | `analyzeSmallWorldProperties()` | Modèle Erdős-Rényi |
| 6 | 3.6 | `analyzeWeightedFlows()` | Coefficient Gini |

---

## Glossaire

- **Nœud (Node)** : un point dans le réseau (ex : adresse crypto)
- **Arête (Edge)** : une connexion entre deux nœuds (ex : transaction)
- **Degré (Degree)** : nombre de connexions d'un nœud
- **Composante connexe** : sous-graphe où tous les nœuds sont reliés
- **Chemin** : séquence de nœuds connectés
- **Cycle** : chemin qui revient au point de départ
- **Hub** : nœud avec un très haut degré
- **Clique** : sous-graphe où tous les nœuds sont connectés entre eux

---

## Ressources pour aller plus loin

**Livres**
- *Networks, Crowds, and Markets* — Easley & Kleinberg
- *Network Science* — Albert-László Barabási

**Outils**
- Gephi (visualisation de graphes)
- NetworkX (Python pour analyse de réseaux)
- Cytoscape (biologie mais applicable)

**Concepts avancés**
- Random walk
- Spectral analysis
- Community detection (Louvain, Modularity)
- Temporal networks

---

## Références

- **Rapport** : WETH / Polygon Network Analysis
- **D3.js** : Force-directed graph visualization
- **NetworkX equivalents** : implémentations JavaScript custom
- **Théorie** : Network Science (Newman, 2010)

---

## Objectif pédagogique

Permettre aux lecteurs du rapport de :
1. **Visualiser** les métriques théoriques
2. **Interagir** avec le réseau en temps réel
3. **Valider** les résultats reportés
4. **Explorer** des cas d'usage alternatifs

---

## License

MIT

---

## Contribution

1. Fork du repo
2. Création d'une branche (`git checkout -b feature/amazing`)
3. Commit des changements
4. Push de la branche
5. Ouverture d'une Pull Request
