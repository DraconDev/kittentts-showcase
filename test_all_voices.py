#!/usr/bin/env python3
"""Generate test recordings for all KittenTTS voices."""

from kittentts import KittenTTS
import os

# Create output directory
os.makedirs("voices", exist_ok=True)

# Initialize the TTS model
print("Loading KittenTTS model...")
tts = KittenTTS()

# Test text
text = "Hello! This is a test of Kitten TTS. I hope you enjoy this voice demonstration."

print(f"Available voices: {tts.available_voices}")
print(f"\nGenerating audio for {len(tts.available_voices)} voices...\n")

for voice in tts.available_voices:
    output_path = f"voices/{voice}.wav"
    print(f"Generating: {voice}...", end=" ", flush=True)
    tts.generate_to_file(text, output_path, voice=voice, speed=1.0)
    print("✓")

print(f"\nAll voices saved to: voices/")
print("Files created:")
for voice in tts.available_voices:
    filepath = f"voices/{voice}.wav"
    size = os.path.getsize(filepath) / 1024  # KB
    print(f"  {voice}.wav ({size:.1f} KB)")
