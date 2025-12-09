import sounddevice as sd
import json
import time
import paho.mqtt.client as mqtt

BROKER = "192.168.0.131"

# configuration params

SAMPLE_RATE = 44100
CHUNK = 2048
PAIR_SPAN = 3
PEAKS_PER_WINDOW = 5
RECORD_SECONDS = 10

all_peaks = []

# database lookup logic

def load_database(path="all_songs.json"):
    with open(path, "r") as f:
        return json.load(f)["songs"]

def build_lookup_table(songs):
    lookup = {}
    for song in songs:
        for fp in song["fingerprints"]:
            lookup.setdefault(fp["hash"], []).append(song["song_name"])
    return lookup

# fingerprint generation from audio

def generate_hashes_from_peaks(all_peaks):
    hashes = []
    for t in range(len(all_peaks)):
        for dt in range(1, PAIR_SPAN + 1):
            if t + dt >= len(all_peaks):
                break
            for f1 in all_peaks[t]:
                for f2 in all_peaks[t + dt]:
                    hashes.append(hash((int(f1), int(f2), dt)))
    return hashes
    
# matching to database (O(1) lookups) 

def match_fingerprints(test_hashes, lookup):
    votes = {}
    for h in test_hashes:
        if h in lookup:
            for song in lookup[h]:
                votes[song] = votes.get(song, 0) + 1
    if not votes:
        return None, 0
    best = max(votes, key=votes.get)
    return best, votes[best]
    
# mqtt 

def on_connect(client, userdata, flags, rc):
    client.subscribe("fft_results")

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    all_peaks.append(payload["peaks"])

# client setup

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.loop_start()


def main():
    songs = load_database()
    lookup = build_lookup_table(songs)

    print("Listening for 10 seconds...")

    start = time.time()
    while time.time() - start < RECORD_SECONDS:
    	# capture short audio chunk from input device
        audio = sd.rec(CHUNK, samplerate=SAMPLE_RATE, channels=1, dtype="float32")
        sd.wait()
        # publish raw samples to rpi for fft over mqtt
        client.publish("raw_audio", json.dumps({
            "samples": audio.flatten().tolist()
        }))

    print("Stopped listening.")
    print("Processing result...")

	# build hashes and match them to database
    hashes = generate_hashes_from_peaks(all_peaks)
    song, score = match_fingerprints(hashes, lookup)

    if song is None:
        print("Detected song: None")
        print("Score: 0")
    else:
        print(f"Detected song: {song}")
        print(f"Score: {score}")

    client.loop_stop()

if __name__ == "__main__":
    main()
