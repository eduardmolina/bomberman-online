import json
import socket
import time

from threading import Thread


class Server(object):
    
    def __init__(self, server_path):
        self.ip, self.port = server_path.split(':')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip, int(self.port)))
        self.players_props = {}
        self.connections = []

    def _process_data(self, data):
        player_name = data['name']
        action = data['action']

        if player_name not in self.players_props:
            self.players_props[player_name] = {
                'x': 300,
                'y': 300,
                'bombs': []
            }

        pos_x = self.players_props[player_name]['x']
        pos_y = self.players_props[player_name]['y']

        if action == 'up' and pos_y > 60:
            self.players_props[player_name]['y'] -= 60
        elif action == 'down' and pos_y < 540:
            self.players_props[player_name]['y'] += 60
        elif action == 'right' and pos_x < 540:
            self.players_props[player_name]['x'] += 60
        elif action == 'left' and pos_x > 60:
            self.players_props[player_name]['x'] -= 60
        elif action == 'deploy_bomb':
            self.players_props[player_name]['bombs'].append({
                'x': pos_x,
                'y': pos_y
            })
        elif action == 'explode_bomb':
            try:
                self.players_props[player_name]['bombs'].pop(0)
            except IndexError:
                pass

        return {
            'name': player_name,
            **self.players_props[player_name]
        }

    def _send_to_client(self, payload, address):
        self.socket.sendto(json.dumps(payload).encode('utf-8'), address)

    def run(self):
        
        while True:
            data, address = self.socket.recvfrom(4096)

            if address not in self.connections:
                self.connections.append(address)
            
            payload = self._process_data(json.loads(data))
            for address in self.connections:
                self._send_to_client(payload, address)
            
            print(data, address)

