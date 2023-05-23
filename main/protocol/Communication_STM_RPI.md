# Protocol de communication entre le Raspberry Pi et le STM32

## Informations générales

* __Liaison__: _`uart`_
* __Séparateur de commandes__: _`,`_
* __Séparateur de valeurs__: _`&`_
* __Caractère de fin__: _`$`_

## Liste des capteurs:
* `UR1` et `UR2` _Capteurs ultrason_
* `IR1` et `IR2` _Catpeurs infrarouge_
* `SERV1` et `SERV_LED` _Servo Moteurs 1 (base) et Led_
* `ENCR` et `ENCL` _Encodage des roues RIGHT and LEFT_
* `MOTR` et `MOTL` _Vitesse de rotation des roues RIGHT and LEFT_

## Les commandes:

Un commande est une chaine de caractère transmise entre le RPi et le STM32*.
Une commande est structuré de la manière suivant: 

* `cmd_id` _Numéro de la commande_ (unsigned char)
* `cmd_values` _Valeurs de la commande_

_Il est possible d'envoyer plusieurs commandes séparées par des virgules_

> Exemple: `cmd = 0&14&15$` &Rightarrow; `cmd_id = 0` et `cmd_values = [14,15]`

## Tableau des commandes

| ID | Value 1 | Value 2 | Description |
| :-: | :-: | :-: | :-: |
| 0 | int | int | Permet de définir la vitesse de rotation des roues |
| 1 | float | - | Force stop |
| 2 | float | - | Description de la commande 2 |
| 3 | float | - | Description de la commande 3 |
| 4 | float | - | Description de la commande 4 |
| 5 | float | - | Description de la commande 5 |