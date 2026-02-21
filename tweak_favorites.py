#!/usr/bin/env python3
import os
import json
import numpy as np
import soundfile as sf
import onnxruntime as ort
import re
from huggingface_hub import hf_hub_download
import phonemizer

class AdjustableKittenTTS:
    def __init__(self, repo_id):
        print(f"Loading config for {repo_id}...")
        config_path = hf_hub_download(repo_id, "config.json")
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        print(f"Downloading model files...")
        model_file = self.config.get("model_file", "model.onnx")
        voices_file = self.config.get("voices", "voices.npz")
        
        self.model_path = hf_hub_download(repo_id, model_file)
        self.voices_path = hf_hub_download(repo_id, voices_file)
        
        self.voice_map = self.config.get("voice_aliases", {})
        
        self._phonemizer = phonemizer.backend.EspeakBackend(language="en-us", preserve_punctuation=True, with_stress=True)
        symbols = list('$;:,.!?¡¿—…"«»"" ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzɑɐɒæɓʙβɔɕçɗɖðʤəɘɚɛɜɝɞɟʄɡɠɢʛɦɧħɥʜɨɪʝɭɬɫɮʟɱɯɰŋɳɲɴøɵɸθœɶʘɹɺɾɻʀʁɽʂʃʈʧʉʊʋⱱʌɣɤʍχʎʏʑʐʒʔʡʕʢǀǁǂǃˈˌːˑʼʴʰʱʲʷˠˤ˞↓↑→↗↘\'̩\'ᵻ')
        self._word_index_dictionary = {symbol: i for i, symbol in enumerate(symbols)}
        self._voices = np.load(self.voices_path)
        self._session = ort.InferenceSession(self.model_path)
        
    def generate_with_style(self, text: str, voice: str, speed: float = 1.0, style_index: int = None) -> np.ndarray:
        voice_id = self.voice_map.get(voice, voice)
        
        phonemes = self._phonemizer.phonemize([text])[0]
        tokens = [self._word_index_dictionary[c] for c in ' '.join(re.findall(r"\w+|[^\w\s]", phonemes)) if c in self._word_index_dictionary]
        input_ids = np.array([[0] + tokens + [0]], dtype=np.int64)
        
        if style_index is None:
            ref_id = min(len(text), self._voices[voice_id].shape[0] - 1)
        else:
            ref_id = max(0, min(style_index, self._voices[voice_id].shape[0] - 1))
            
        style_embedding = self._voices[voice_id][ref_id:ref_id+1]
            
        outputs = self._session.run(None, {
            "input_ids": input_ids,
            "style": style_embedding,
            "speed": np.array([speed], dtype=np.float32),
        })
        
        audio = outputs[0]
        if audio.shape[-1] > 5000:
            audio = audio[..., :-5000]
            
        return audio

    def save_adjusted(self, text, path, voice, speed=1.0, style_index=None):
        audio = self.generate_with_style(text, voice, speed, style_index)
        sf.write(path, audio.flatten(), 24000)
        print(f"Saved: {path} (Speed: {speed}, Style: {style_index})")

# Configuration
favorites = ['Rosie', 'Kiki', 'Bruno']
speeds = [0.8, 1.0, 1.2]
sample_styles = [10, 50, 150, 300] 

test_text = "I am testing my new adjusted voice settings. How do I sound now?"
output_dir = "adjusted_favorites"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print("Initializing AdjustableKittenTTS...")
tts = AdjustableKittenTTS("KittenML/kitten-tts-mini-0.8")

for voice in favorites:
    print(f"\n--- Tweaking {voice} ---")
    voice_dir = os.path.join(output_dir, voice)
    if not os.path.exists(voice_dir):
        os.makedirs(voice_dir)
        
    for speed in speeds:
        for style in sample_styles:
            speed_str = str(speed).replace('.', '_')
            filename = f"{voice}_speed{speed_str}_style{style}.wav"
            path = os.path.join(voice_dir, filename)
            
            if os.path.exists(path):
                continue
                
            tts.save_adjusted(test_text, path, voice, speed=speed, style_index=style)

print("\nDone! Check 'adjusted_favorites/' folder.")
