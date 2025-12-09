# EE250 Final Project: Distributed Audio Fingerprinting & Recognition

## Team Member Names
- Shreya Nair  
- May Khan  

---

## How to Run the Project

1. **Install dependencies** (on both laptop and Raspberry Pi as needed):
```pip install sounddevice numpy scipy paho-mqtt flask flask-cors```
(Install `pyaudio` as well if any capture script uses it.)

2. **Start an MQTT broker** (e.g., Mosquitto) on your network.  
	- Note the broker’s IP address.

3. **Configure broker addresses in the code**:
	- In `mqtt_client.py` (laptop), set:
  	```
  	BROKER = "<broker-ip>"
  	```
	- In `fft_node.py` (Raspberry Pi), set:
 	```
  	BROKER_IP = "<broker-ip>"
  	```

4. **Place the fingerprint database**:  
	- Ensure `all_songs.json` is in the same directory as `mqtt_client.py`.

5. **Run the FFT / peak node on the Raspberry Pi**:
```python3 fft_node.py```

6. **Run the Flask API server on the laptop**:
```python3 api_server.py```
	- By default, this listens on `http://127.0.0.1:5000`.

7. **Open the web interface**  
   - With `api_server.py` running, open a browser and go to:  
     `http://127.0.0.1:5000`  
   - This loads the project’s main page.

8. **Start a recognition run from the page**  
   - On the website, click the button to start listening/recognition.  
   - The backend runs the MQTT-based recognizer script, processes the audio, and computes the best match.

9. **View the result**  
   - After the run finishes, the page updates to show the latest detected song and its score.

