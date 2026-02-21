#!/usr/bin/env python3
import os
import json
import numpy as np
import soundfile as sf
import onnxruntime as ort
import re
from huggingface_hub import hf_hub_download
import phonemizer

class SpeedTesterKittenTTS:
    def __init__(self, repo_id):
        print(f"\n--- Initializing {repo_id} ---")
        config_path = hf_hub_download(repo_id, "config.json")
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
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
        
    def generate(self, text: str, voice: str, speed: float = 1.0) -> np.ndarray:
        voice_id = self.voice_map.get(voice, voice)
        phonemes = self._phonemizer.phonemize([text])[0]
        tokens = [self._word_index_dictionary[c] for c in ' '.join(re.findall(r"\w+|[^\w\s]", phonemes)) if c in self._word_index_dictionary]
        input_ids = np.array([[0] + tokens + [0]], dtype=np.int64)
        
        ref_id = min(len(text), self._voices[voice_id].shape[0] - 1)
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

# Configuration for the Speed Stress Test
models_to_test = [
    "KittenML/kitten-tts-mini-0.8",
    "KittenML/kitten-tts-micro-0.8",
    "KittenML/kitten-tts-nano-0.8",
    "KittenML/kitten-tts-nano-0.8-int8"
]

voices_to_test = ['Bella', 'Jasper', 'Luna', 'Bruno', 'Rosie', 'Hugo', 'Kiki', 'Leo']
speeds_to_test = [1.5, 2.0, 2.5, 3.0, 3.5]

test_sentence = "The quick brown fox jumps over the lazy dog. We are testing how well this text to speech model maintains legibility at very high playback speeds."
output_root = "speed_stress_tests"

if not os.path.exists(output_root):
    os.makedirs(output_root)

print("Starting Extreme Speed Test (1.5x - 3.5x)...")

for model_repo in models_to_test:
    model_name = model_repo.split('/')[-1].replace('.', '_')
    tts = SpeedTesterKittenTTS(model_repo)
    
    for speed in speeds_to_test:
        speed_folder = os.path.join(output_root, f"speed_{str(speed).replace('.', '_')}")
        if not os.path.exists(speed_folder):
            os.makedirs(speed_folder)
            
        print(f"  Testing Speed {speed}x...")
        for voice in voices_to_test:
            filename = f"{model_name}_{voice}.wav"
            path = os.path.join(speed_folder, filename)
            
            if os.path.exists(path):
                continue
                
            try:
                audio = tts.generate(test_sentence, voice, speed)
                sf.write(path, audio.flatten(), 24000)
            except Exception as e:
                print(f"    Error with {voice} at {speed}x: {e}")

print("\nAll speed samples generated! Check 'speed_stress_tests/' folder.")
