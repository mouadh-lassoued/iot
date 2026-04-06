# Serre Intelligente Connectée (TP2)

## Structure

- `config.py` : configuration centrale MQTT, topics, seuils et plages.
- `sensors/` : capteurs modulaires (température sol, humidité, luminosité, niveau d'eau).
- `actuators/` : actionneurs intelligents (irrigation, éclairage).
- `controller.py` : base pour la phase contrôleur (TP3).
- `logs/` : dossier de logs.

## Lancement des capteurs

```bash
python -m greenhouse.sensors.temp_soil
python -m greenhouse.sensors.humidity
python -m greenhouse.sensors.light
python -m greenhouse.sensors.water
```

## Lancement des actionneurs

```bash
python -m greenhouse.actuators.irrigation
python -m greenhouse.actuators.lighting
```
