Utilisation de **$select[]** pour choisir les champs suivants :
- name: Le nom de l'objet.
- iconId: L'identifiant de l'icône de l'objet.
- description: La description de l'objet.
- typeId: L'identifiant du type d'objet.
- itemSetId: L'identifiant de l'ensemble d'objets auquel l'objet - appartient.
- level: Le niveau requis pour utiliser l'objet.
- criteria: Les critères associés à l'objet.
- realWeight: Le poids réel de l'objet.
- price: Le prix de l'objet.
- possibleEffects: Les effets possibles de l'objet.
- range: La portée de l'objet.
- apCost: Le coût en points d'action pour utiliser l'objet.
- minRange: La portée minimale de l'objet.
- criticalHitProbability: La probabilité de coup critique de l'objet.
- criticalHitBonus: Le bonus de coup critique de l'objet.
- castInLine: Indique si l'objet peut être lancé en ligne.
- castInDiagonal: Indique si l'objet peut être lancé en diagonale.
- castTestLos: Indique si la ligne de vue est testée lors du - lancement de l'objet.
- maxCastPerTurn: Le nombre maximal de lancers par tour pour - l'objet.
- importantNotice: Une notice importante associée à l'objet.
- lang: Ce paramètre spécifie la langue dans laquelle vous souhaitez que les données soient renvoyées

Exemple d'utilisation :
```bash
https://api.dofusdb.fr/items/2531?$select[]=name&$select[]=iconId&$select[]=description&$select[]=typeId&$select[]=itemSetId&$select[]=level&$select[]=criteria&$select[]=realWeight&$select[]=price&$select[]=possibleEffects&$select[]=range&$select[]=apCost&$select[]=minRange&$select[]=criticalHitProbability&$select[]=criticalHitBonus&$select[]=castInLine&$select[]=castInDiagonal&$select[]=castTestLos&$select[]=maxCastPerTurn&$select[]=importantNotice&lang=fr
```