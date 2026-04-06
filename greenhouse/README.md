# Serre Intelligente Connectée (TP2 + TP3)

## Structure

- `config.py` : configuration centrale MQTT, topics, seuils et plages.
- `sensors/` : capteurs modulaires (température sol, humidité, luminosité, niveau d'eau).
- `actuators/` : actionneurs intelligents (irrigation, éclairage).
- `controller.py` : contrôleur central avec règles métier (irrigation, éclairage, alertes).
- `node-red-flow-serre.json` : flow de base importable dans Node-RED.
- `logs/` : dossier de logs (`greenhouse.log`).

## Démarrage des composants

```bash
python -m greenhouse.sensors.temp_soil
python -m greenhouse.sensors.humidity
python -m greenhouse.sensors.light
python -m greenhouse.sensors.water
python -m greenhouse.actuators.irrigation
python -m greenhouse.actuators.lighting
python -m greenhouse.controller
```

## Règles métier implémentées (contrôleur)

1. **Irrigation automatique** :
   - SI `humidity < 40` ET `water > 20` ALORS irrigation = `ON`, sinon `OFF`.
2. **Éclairage automatique** :
   - SI `light < 300` ET heure dans `[08:00, 18:00[` ALORS éclairage = `ON`, sinon `OFF`.
3. **Alerte température critique** :
   - SI `temp_soil > 32` ALORS publication d'une alerte `CRITICAL` sur `greenhouse/alerts`.

## Node-RED

- Importer `greenhouse/node-red-flow-serre.json` via **Menu → Import**.
- Le flow inclut 3 entrées MQTT de base : capteurs, états actionneurs et alertes.
