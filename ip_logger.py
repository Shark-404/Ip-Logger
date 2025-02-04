from flask import Flask, request, jsonify
import platform
import psutil
import requests
from pyngrok import ngrok
from user_agents import parse  

app = Flask(__name__)

def get_location(ip):
    """ Obtiene la ubicación basada en la IP usando ipinfo.io """
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        data = response.json()
        return {
            "City": data.get("city", "Unknown"),
            "State": data.get("region", "Unknown"),
            "Country": data.get("country", "Unknown")
        }
    except:
        return {"City": "Unknown", "State": "Unknown", "Country": "Unknown"}

def get_system_info():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

    location = get_location(ip)

    user_agent = request.headers.get("User-Agent", "Unknown")
    parsed_ua = parse(user_agent)

    info = {
        "IP": ip,
        "City": location["City"],
        "State": location["State"],
        "Country": location["Country"],
        "Browser": parsed_ua.browser.family,
        "Browser Version": parsed_ua.browser.version_string,
        "Operating System": parsed_ua.os.family,
        "OS Version": parsed_ua.os.version_string,
        "User Agent": user_agent,
        "Node Name": platform.node(),
        "Release": platform.release(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "CPU Cores": psutil.cpu_count(logical=False),
        "Total CPU Usage": psutil.cpu_percent(interval=1),
        "Total Memory (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "Available Memory (GB)": round(psutil.virtual_memory().available / (1024 ** 3), 2),  
        "Used Memory (GB)": round(psutil.virtual_memory().used / (1024 ** 3), 2),
    }
    return info

@app.route("/")
def index():
    user_info = get_system_info()

    print("\n📥 Nueva conexión:")
    for key, value in user_info.items():
        print(f"{key}: {value}")
    
    return jsonify(user_info)

if __name__ == "__main__":
    public_url = ngrok.connect(5000).public_url
    print(f"🔗 Link público: {public_url}")
    
    app.run(host="0.0.0.0", port=5000)
