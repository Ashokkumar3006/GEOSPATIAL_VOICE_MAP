from flask import Flask, render_template, request, jsonify
import folium
import speech_recognition as sr
import requests
app = Flask(__name__)
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Error with request; {e}"
def get_coordinates(place_name):
    params = {
        'q': place_name,
        'format': 'json'
    }
    response = requests.get(NOMINATIM_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['lat'], data[0]['lon']
    return None, None

@app.route('/')
def index():
    m = folium.Map(location=[45.5236, -122.6750], zoom_start=50)
    return render_template('index.html', folium_map=m._repr_html_())

@app.route('/voice', methods=['POST'])
def voice_command():
    data = request.get_json()
    command = data.get('command').lower()
    print(f"Received command: {command}")

    if 'zoom in' in command:
        response = {'action': 'zoom_in'}
    elif 'zoom out' in command:
        response = {'action': 'zoom_out'}
    elif 'move left' in command:
        response = {'action': 'move_left'}
    elif 'move right' in command:
        response = {'action': 'move_right'}
    elif 'move up' in command:
        response = {'action': 'move_up'}
    elif 'move down' in command:
        response = {'action': 'move_down'}
    elif 'navigate to' in command:
        place_name = command.split('navigate to')[-1].strip()
        lat, lon = get_coordinates(place_name)
        if lat and lon:
            response = {'action': 'navigate', 'lat': lat, 'lon': lon}
        else:
            response = {'action': 'unrecognized'}
    else:
        response = {'action': 'unrecognized'}
    return jsonify(response)
if __name__ == '__main__':
    app.run(debug=True)
