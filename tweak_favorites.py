#!/usr/bin/env python3
import os
import sys
import numpy as np
import soundfile as sf
from kittentts import KittenTTS

# We will subclass the internal model to allow manual style index selection
class AdjustableKittenTTS(KittenTTS):
    def generate_with_style(self, text, voice, speed=1.0, style_index=None):
        """
        Custom generate method that allows picking a specific style index (0-399)
        instead of defaulting to len(text).
        """
        model = self.model
        if voice in model.voice_aliases:
            voice = model.voice_aliases[voice]
            
        # If no style_index, it behaves like the original
        if style_index is None:
            ref_id = min(len(text), model.voices[voice].shape[0] - 1)
        else:
            # Override with our custom index
            ref_id = max(0, min(style_index, model.voices[voice].shape[0] - 1))
        
        # Prepare inputs as the original library does
        onnx_inputs = model._prepare_inputs(text, voice, speed)
        # Override the style embedding with our chosen index
        onnx_inputs["style"] = model.voices[voice][ref_id:ref_id+1]
        
        # Run inference
        outputs = model.session.run(None, onnx_inputs)
        audio = outputs[0][..., :-5000]
        return audio

    def save_adjusted(self, text, path, voice, speed=1.0, style_index=None):
        audio = self.generate_with_style(text, voice, speed, style_index)
        sf.write(path, audio, 24000)
        print(f"Saved: {path} (Speed: {speed}, Style: {style_index})")

# Configuration for the tweak session
favorites = ['Rosie', 'Kiki', 'Bruno']
speeds = [0.8, 1.0, 1.2]
# Picking some diverse style indices to sample the range
sample_styles = [10, 50, 150, 300] 

test_text = "I am testing my new adjusted voice settings. How do I sound now?"
output_dir = "adjusted_favorites"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print("Loading 'mini' model for best quality...")
# We use the mini-0.8 as it is the highest quality
tts = AdjustableKittenTTS("KittenML/kitten-tts-mini-0.8")

for voice in favorites:
    print(f"\n--- Tweaking {voice} ---")
    voice_dir = os.path.join(output_dir, voice)
    if not os.path.exists(voice_dir):
        os.makedirs(voice_dir)
        
    for speed in speeds:
        for style in sample_styles:
            # Use underscore instead of dot for speed in filename
            speed_str = str(speed).replace('.', '_')
            filename = f"{voice}_speed{speed_str}_style{style}.wav"
            path = os.path.join(voice_dir, filename)
            
            # Skip if file already exists to save time
            if os.path.exists(path):
                continue
                
            tts.save_adjusted(test_text, path, voice, speed=speed, style_index=style)

print("\nDone! Check 'adjusted_favorites/' folder to hear the differences.")
