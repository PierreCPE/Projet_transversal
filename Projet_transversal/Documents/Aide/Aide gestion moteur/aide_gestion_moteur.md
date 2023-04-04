# Aide pour le fonctionnement moteur.

Pour faire communiquer le 8051 avec le serializer :

1. La masse en B0 avec la masse du serializer
2. Le Rx (P0.1 = B12) du 8051 avec le Tx du serializer (fil blanc)
3. Le Tx (P0.0 = C12) du 8051 avec le Rx du serializer (fil vert)

On alimente le 8051 et on appuie sur le bouton poussoir

