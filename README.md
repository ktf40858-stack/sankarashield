# SankaraShield — site v2

Reconstruction complète du site, **en local uniquement**. Le site en production
(`www.sankarashield.com`) et son dépôt `Desktop\sankarashield` ne sont pas touchés.

---

## Voir le site

```
cd C:\Users\Freddy\Desktop\sankarashield-v2
python -m http.server 8099
```

Puis ouvrir <http://localhost:8099/>

> Ne pas ouvrir les fichiers en `file://` : les chemins et le JSON du blog ne
> fonctionnent correctement que servis en HTTP.

---

## Structure

```
index.html          accueil (vente + preuve technique)
solutions.html      les 4 domaines : infrastructure, sécurité, déploiement, support
about.html          l'entreprise, le fondateur, section #careers pour les recruteurs
contact.html        formulaire d'envoi + email direct + recruteurs
404.html
blog/               133 articles générés + index avec recherche et filtres
assets/
  css/site.css      tout le design (aucun framework)
  js/site.js        nav mobile, header collant, apparition, envoi du formulaire
  img/              logo vert officiel, favicons, image Open Graph
  blog/             illustrations recompressées (1200 px + vignette 640 px)
  posts.json        index des articles (date, thème, tags)
tools/
  build_blog.py     génère les 133 articles + blog/index.html + sitemap.xml
  build_pages.py    génère les 5 pages statiques
CNAME               www.sankarashield.com — NE JAMAIS SUPPRIMER
sw.js               kill-switch du vieux service worker (voir plus bas)
robots.txt, sitemap.xml, favicon.ico
```

---

## Régénérer le site

Après avoir ajouté un article dans `C:\Users\Freddy\Desktop\Post\Sankarashield\<Mois>\` :

```
python tools\build_blog.py     # articles, index du blog, posts.json, sitemap
python tools\build_pages.py    # pages statiques (reprend les 3 derniers articles)
```

Toujours dans cet ordre : `build_pages.py` lit ce que `build_blog.py` a produit.

### Comment un article est lu

- **Titre** : première ligne réelle du `.txt` (les lignes de date, les séparateurs
  et les notes de rédaction sont ignorés). Au-delà de 118 caractères, coupe à la
  première phrase.
- **Sections** : les lignes encadrées de `─────` et les lignes tout en majuscules
  deviennent des titres de section.
- **Listes** : `LIBELLÉ — texte` et `LIBELLÉ` suivi du texte à la ligne.
- **Citation** : la question finale de l'article.
- **Date** : jour + mois lus dans le nom du fichier, sinon date de modification.
- **Image** : appariée par jour de semaine + quantième dans le même dossier ;
  la version `_with_logo` est préférée.
- **Thème** : classé automatiquement parmi 6 catégories par mots-clés.
- **Sans illustration** : une couverture est dessinée automatiquement (motif réseau
  unique par article, dérivé du slug, aux couleurs de la marque).

Les emojis, le markdown résiduel (`**gras**`) et les notes de rédaction
(« 2898 caractères — dans la cible ») sont retirés automatiquement.

---

## Le jour du déploiement

Rien n'est publié tant que ce n'est pas fait explicitement.

1. Dans `Desktop\sankarashield`, créer une branche : `git switch -c refonte-2026-09`
2. Vider le dossier **sauf `.git/`**
3. Copier tout le contenu de `sankarashield-v2` dedans (`CNAME` compris)
4. `git add -A && git commit && git switch main && git merge refonte-2026-09 && git push`
5. Vérifier **Settings → Pages → Enforce HTTPS**
6. Tester en navigation privée **et** dans un navigateur déjà venu sur le site

### Pourquoi `sw.js` doit être déployé

L'ancien site enregistrait un service worker `sankarashield-v3.0.0` en
**cache-first**. Tout navigateur déjà venu continuerait de servir les **anciennes
pages** depuis son cache après la refonte — supprimer `sw.js` ne suffit pas, le
worker reste enregistré. Le `sw.js` de ce dossier le remplace : il vide les
caches, se désenregistre et recharge les onglets ouverts.

**À garder en ligne au moins 60 jours après la bascule**, puis supprimer.

---

## Points volontairement laissés en attente

### ⚠️ Activer le formulaire de contact — 2 minutes, à faire une seule fois

Le formulaire est écrit et fonctionne, mais il lui manque **une clé d'accès** pour
livrer les messages. Sans elle, il affiche « Form not activated yet ».

1. Aller sur <https://web3forms.com> (gratuit, pas de compte à créer)
2. Saisir **contact@sankarashield.com** → la clé arrive par e-mail
3. Ouvrir `tools\build_pages.py`, remplacer la valeur de `WEB3FORMS_KEY`
4. `python tools\build_pages.py`

La clé est conçue pour être publique, il n'y a aucun risque à la mettre dans le HTML.
Elle ne permet que d'envoyer un message vers l'adresse qui la possède.

Aucune donnée n'est stockée sur le site : le message part directement dans la boîte.

| Sujet | État |
|---|---|
| Clé Web3Forms | **à générer et coller** (ci-dessus) |
| Téléphone | Volontairement absent (aucun faux numéro) |
| Version française | Prévue, non faite — cible Afrique |
| CV PDF | Pas encore mis en téléchargement |

---

## Ce que ce site ne fait pas

Aucun chiffre inventé, aucun logo de constructeur, aucun compteur de clients,
aucun numéro de téléphone fictif, aucun formulaire qui n'envoie nulle part.
Les noms de constructeurs cités le sont avec une mention explicite d'absence de
partenariat.
