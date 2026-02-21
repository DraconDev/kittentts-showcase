#!/usr/bin/env python3
"""Example script for KittenTTS usage."""

from kittentts import KittenTTS

# Initialize the TTS model
print("Loading KittenTTS model...")
tts = KittenTTS()

# Show available voices
print(f"Available voices: {tts.available_voices}")

# Generate speech from text
text = "Hello! This is a test of Kitten TTS, a lightweight text to speech model."
output_file = "output.wav"

print(f"Generating speech for: '{text}'")
tts.generate_to_file(text, output_file, voice='expr-voice-5-m', speed=1.0)

print(f"Audio saved to: {output_file}")
