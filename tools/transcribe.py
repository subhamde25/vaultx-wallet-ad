# usage: python -I transcribe.py <audio> <out.json>  — word-level timestamps via faster-whisper
import sys, json
from faster_whisper import WhisperModel
import subprocess, numpy as np
pcm = subprocess.run(['ffmpeg','-v','error','-i',sys.argv[1],'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True,check=True).stdout
audio = np.frombuffer(pcm, np.float32)
m = WhisperModel(sys.argv[3] if len(sys.argv) > 3 else 'medium.en', device='cpu', compute_type='int8')
segs, _ = m.transcribe(audio, word_timestamps=True, vad_filter=False, beam_size=5,
    initial_prompt="VaultX Wallet, crypto, swaps, portfolio, biometric, encryption.")
words = [{'w': w.word.strip(), 's': round(w.start, 3), 'e': round(w.end, 3)} for s in segs for w in s.words]
json.dump(words, open(sys.argv[2], 'w'), indent=0)
print(' '.join(w['w'] for w in words)); print(len(words), 'words')
