from flask import Flask, jsonify
from flask_cors import CORS
import docker
import json
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

allowed_origins_env = os.getenv('ALLOWED_ORIGINS', '')

if allowed_origins_env:
    allowed_origins = allowed_origins_env.split(',')
else:
    allowed_origins = []

CORS(app, origins=allowed_origins, methods=["GET"], allow_headers=["Content-Type"])

docker_client = docker.from_env()
SERVER_LIST = "servers.json"

def get_container_status(container_name: str) -> str:
    try:
        container = docker_client.containers.get(container_name)
        status = container.status
        if status == "1":
            return "online"
        elif status == "2":
            return "offline"
        else:
            return "unknown"
    except docker.errors.NotFound:
        return "not_found"
    except Exception:
        return "error"

# READ servers.json
def load_servers() -> Dict[str, str]:
    try:
        with open(SERVER_LIST, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# GET CONTAINER STATUS
def get_status(container_name: str) -> str:
    try:
        container = docker_client.containers.get(container_name)
        status = container.status
        if status == "running":
            return "online"
        elif status == "exited":
            return "offline"
        else:
            return "unknown"
    except docker.errors.NotFound:
        return "not_found"
    except Exception:
        return "error"

# ALL SERVER STATUS
@app.route('/servers', methods=['GET'])
def get_servers():
    game_map = load_servers()
    
    servers_status = []
    for game_name, container_name in game_map.items():
        status = get_status(container_name)
        servers_status.append({
            "game": game_name,
            "container": container_name,
            "status": status
        })
    
    return jsonify({
        "servers": servers_status,
        "total": len(servers_status)
    }), 200
    
# GAME SPECIFIC STATUS
@app.route('/servers/<game_name>', methods=['GET'])
def get_server_status(game_name: str):
    game_map = load_servers()
    
    if game_name.lower() not in game_map:
        return jsonify({
            "error": "Server not found",
            "game": game_name
        }), 404
    
    container_name = game_map[game_name.lower()]
    status = get_container_status(container_name)
    
    return jsonify({
        "game": game_name,
        "container": container_name,
        "status": status
    }), 200
    
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "ramen-games-api"
    }), 200