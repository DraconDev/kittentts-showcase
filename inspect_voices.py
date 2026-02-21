#!/usr/bin/env python3
import numpy as np
import json
from huggingface_hub import hf_hub_download

model_repo = "KittenML/kitten-tts-mini-0.8"

print(f"Inspecting voices for {model_repo}...")

# Download voices.npz
voices_path = hf_hub_download(repo_id=model_repo, filename="voices.npz")
voices = np.load(voices_path)

# Download config.json for aliases
config_path = hf_hub_download(repo_id=model_repo, filename="config.json")
with open(config_path, 'r') as f:
    config = json.load(f)

aliases = config.get("voice_aliases", {})
rev_aliases = {v: k for k, v in aliases.items()}

for voice_id in voices.files:
    data = voices[voice_id]
    friendly_name = rev_aliases.get(voice_id, "Unknown")
    print(f"Voice: {voice_id} ({friendly_name}) | Shape: {data.shape}")
