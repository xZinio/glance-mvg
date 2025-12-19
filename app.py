from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

COLORS = {
    'UBAHN': '#006cb3',      
    'BUS_GREEN': '#005f50',  
    'BUS_ORANGE': '#ef7c00', 
    'SBAHN': '#4F782D',
    'TRAM': '#D82020'
}

def get_station_id(station_name):
    known = {'Alte Heide': 'de:09162:80'}
    if station_name in known: return known[station_name]

    try:
        url = "https://www.mvg.de/api/bgw-pt/v3/locations"
        r = requests.get(url, params={'query': station_name}, verify=False, timeout=5)
        for loc in r.json():
            if loc.get('type') == 'STATION': return loc['globalId']
    except Exception as e:
        print(f"Search Error: {e}")
        return None

@app.route('/departures')
def departures():
    station_name = request.args.get('station', 'Studentenstadt')

    if station_name == 'Alte Heide':
        allowed_lines = ['U6']
    else:
        allowed_lines = ['U6', 'X35', 'X36', '50']

    station_id = get_station_id(station_name)
    if not station_id: return jsonify([])

    try:
        url = "https://www.mvg.de/api/bgw-pt/v3/departures"
        params = {
            'globalId': station_id,
            'limit': 80,
            'transportTypes': 'UBAHN,BUS,TRAM,SBAHN'
        }

        r = requests.get(url, params=params, verify=False, timeout=5)
        data = r.json()

        results = []
        current_time_ts = time.time() * 1000

        for dep in data:
            label = dep.get('label')

            if label not in allowed_lines: continue

            d_time = dep.get('realtimeDepartureTime', dep.get('plannedDepartureTime'))
            if d_time < current_time_ts: continue

            minutes = int((d_time - current_time_ts) / 60000)

            if label == '50':
                color = COLORS['BUS_ORANGE']
            elif label.startswith('U'):
                color = COLORS['UBAHN']
            elif label.startswith('X'):
                color = COLORS['BUS_GREEN']
            else:
                color = COLORS['BUS_GREEN']

            results.append({
                "line": label,
                "dest": dep['destination'],
                "minutes": minutes,
                "timeStr": "Now" if minutes < 1 else f"{minutes} min",
                "color": color
            })

            if len(results) >= 6: break

        return jsonify(results)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify([])

if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings()
    app.run(host='0.0.0.0', port=5000)