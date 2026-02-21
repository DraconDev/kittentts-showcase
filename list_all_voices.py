#!/usr/bin/env python3
import json
from huggingface_hub import hf_hub_download

models = [
    "KittenML/kitten-tts-mini-0.8",
    "KittenML/kitten-tts-micro-0.8",
    "KittenML/kitten-tts-nano-0.8",
    "KittenML/kitten-tts-nano-0.8-int8"
]

print(f"{'Model Name':<35} | {'Voices':<20} | {'Aliases'}")
print("-" * 80)

for model_repo in models:
    try:
        # Download config.json to see the metadata
        config_path = hf_hub_download(repo_id=model_repo, filename="config.json")
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # In the current implementation, available_voices is hardcoded in the class,
        # but let's see what's in the config.
        aliases = config.get("voice_aliases", {})
        
        # We know from the code that the base voices are currently:
        base_voices = [
            'expr-voice-2-m', 'expr-voice-2-f', 'expr-voice-3-m', 'expr-voice-3-f', 
            'expr-voice-4-m', 'expr-voice-4-f', 'expr-voice-5-m', 'expr-voice-5-f'
        ]
        
        alias_str = ", ".join([f"{k}->{v}" for k, v in aliases.items()]) if aliases else "None"
        voice_count = len(base_voices)
        
        print(f"{model_repo:<35} | {voice_count} voices found | {alias_str}")
        
    except Exception as e:
        print(f"Error checking {model_repo}: {e}")
