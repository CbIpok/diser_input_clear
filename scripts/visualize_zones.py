#!/usr/bin/env python3
import os
import json
from src.visualization import plot_zones

def load_config():
    config_path = os.path.join("..","config", "zones.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    config = load_config()
    plot_zones(config)
