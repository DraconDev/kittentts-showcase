#!/usr/bin/env python3
import os
import sys
from kittentts import KittenTTS

# Using only the newest 0.8 versions
models_to_test = [
    "KittenML/kitten-tts-mini-0.8",
    "KittenML/kitten-tts-micro-0.8",
    "KittenML/kitten-tts-nano-0.8",
    "KittenML/kitten-tts-nano-0.8-int8"
]

# 5 Test Scenarios
test_scenarios = [
    {
        "id": "1_pangram",
        "text": "The quick brown fox jumps over the lazy dog."
    },
    {
        "id": "2_conversational",
        "text": "Hello! I am one of the new high-quality voices. I can speak very naturally, don't you think? It's nice to meet you!"
    },
    {
        "id": "3_technical",
        "text": "The implementation uses an O N N X model with only fifteen million parameters, allowing it to run efficiently on C P Us."
    },
    {
        "id": "4_numbers_dates",
        "text": "Today is Saturday, February 21, 2026. The current temperature is 22 degrees Celsius, and the coordinates are 45.7 degrees North."
    },
    {
        "id": "5_narrative",
        "text": "Once upon a time, in a digital forest, a small kitten found a way to speak. It traveled through many circuits, sharing its voice with the world."
    }
]

# Friendly name mapping (confirmed from config)
friendly_voices = ['Bella', 'Jasper', 'Luna', 'Bruno', 'Rosie', 'Hugo', 'Kiki', 'Leo']

output_root = "comprehensive_tests"

print(f"Starting comprehensive testing of {len(models_to_test)} models across 5 scenarios...")

for model_name in models_to_test:
    clean_model_name = model_name.split('/')[-1].replace('.', '_')
    print(f"\n>>> Loading Model: {model_name}")
    
    try:
        tts = KittenTTS(model_name)
        
        for scenario in test_scenarios:
            scenario_id = scenario["id"]
            scenario_text = scenario["text"]
            
            # Create directory for this scenario
            scenario_dir = os.path.join(output_root, scenario_id)
            if not os.path.exists(scenario_dir):
                os.makedirs(scenario_dir)
            
            print(f"  Scenario {scenario_id}: '{scenario_text[:30]}...'")
            
            for voice in friendly_voices:
                output_file = os.path.join(scenario_dir, f"{clean_model_name}_{voice}.wav")
                
                # Check if already exists to skip (optional, but good for resuming)
                if os.path.exists(output_file):
                    continue
                
                tts.generate_to_file(
                    scenario_text,
                    output_file,
                    voice=voice,
                    speed=1.0
                )
                
    except Exception as e:
        print(f"Error with model {model_name}: {e}")

print(f"\nAll 5 test scenarios completed! Results are in '{output_root}/'")
