import numpy as np
import json
import paho.mqtt.client as mqtt
from scipy.signal import find_peaks

# configuration params

BROKER_IP = "localhost"

SAMPLE_RATE = 44100
WINDOW_SIZE = 2048
PEAKS_PER_WINDOW = 5

client = mqtt.Client()

# peak extraction from data

def get_peaks(samples):
    fft_vals = np.fft.rfft(samples)
    magnitudes = np.abs(fft_vals)
    freqs = np.fft.rfftfreq(len(samples), 1 / SAMPLE_RATE)

    threshold = np.mean(magnitudes) * 2.5
    peaks, props = find_peaks(magnitudes, height=threshold)

    if len(peaks) == 0:
        return []

    strong_idx = np.argsort(props["peak_heights"])[::-1][:PEAKS_PER_WINDOW]
    strong_peaks = freqs[peaks[strong_idx]]

    return strong_peaks.tolist()

# mqtt

def on_connect(client, userdata, flags, rc):
    print("Pi connected to broker")
    client.subscribe("raw_audio")


def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    samples = np.array(payload["samples"], dtype=float)

    peaks = get_peaks(samples)

    client.publish("fft_results", json.dumps({"peaks": peaks}))
    print("Processed FFT and sent peaks:", peaks)
 
 # mqtt polling loop

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_IP, 1883, 60)
client.loop_forever()
