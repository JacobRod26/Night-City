
import numpy as np
import sounddevice as sd
import soundfile as sf
import queue
import threading
import os

# Demucs imports
from demucs.pretrained import get_model
from demucs.apply import apply_model
import torch
  
# Path to your song (should be in the same folder as this script)
AUDIO_PATH = os.path.join(os.path.dirname(__file__), '02 llorarás.mp3')
if not os.path.exists(AUDIO_PATH):
    raise FileNotFoundError(f'Audio file not found: {AUDIO_PATH}')

# Parameters
BANDS = 32  # Number of bars
CHUNK = 1024  # Samples per frame

# Read audio file
sf_info = sf.info(AUDIO_PATH)
samplerate = sf_info.samplerate
channels = sf_info.channels

# Queue for audio data
q_audio = queue.Queue()

# Audio callback to stream audio and put data in queue
def audio_callback(outdata, frames, time, status):
    data, _ = sf.read(AUDIO_PATH, start=audio_callback.pos, stop=audio_callback.pos+frames, dtype='float32')
    if len(data) < frames:
        outdata[:len(data)] = data
        outdata[len(data):] = 0
        raise sd.CallbackStop()
    else:
        outdata[:] = data
    q_audio.put(data)
    audio_callback.pos += frames

audio_callback.pos = 0

# Visualization function

def process_and_print_instr_ratios():
    print('Printing instrAmp/ampTotal for each instrument per audio chunk:')
    # Load Demucs model once
    model = get_model('htdemucs')
    model.eval()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)
    stems = model.sources
    while True:
        if not q_audio.empty():
            data = q_audio.get()
            # Demucs expects shape (channels, samples)
            if data.ndim == 1:
                data = np.expand_dims(data, axis=1).T
            elif data.shape[1] > 2:
                data = data[:, :2]  # Use only first two channels if more
            else:
                data = data.T
            # Convert to torch tensor
            tensor = torch.tensor(data, dtype=torch.float32, device=device)
            with torch.no_grad():
                # Demucs expects (batch, channels, samples)
                tensor = tensor.unsqueeze(0)
                sources = apply_model(model, tensor, split=True, overlap=0.25)[0]
            instr_amps = {}
            amp_total = 0.0
            for i, stem in enumerate(stems):
                # sources shape: (sources, channels, samples)
                instr = sources[i].cpu().numpy()
                # Absolute amplitude (sum of abs values)
                instr_amp = np.sum(np.abs(instr))
                instr_amps[stem] = instr_amp
                amp_total += instr_amp
            # Print ratios
            if amp_total > 0:
                ratios = {stem: round(instr_amps[stem]/amp_total, 4) for stem in stems}
            else:
                ratios = {stem: 0.0 for stem in stems}
            print(ratios)
        else:
            if not stream.is_active():
                break

def main():
    # Start audio stream in a thread
    global stream
    stream = sd.OutputStream(
        samplerate=samplerate,
        channels=channels,
        callback=audio_callback,
        blocksize=CHUNK
    )
    t = threading.Thread(target=stream.start)
    t.start()


    # Process and print instrument amplitude ratios
    process_and_print_instr_ratios()

    stream.stop()
    stream.close()

if __name__ == '__main__':
    main()
