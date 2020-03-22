import json
import socket
import time

from threading import Thread

import pygame 


class Client(object):

    def __init__(self, server_path, name):
        self.players_props = {}
        self.name = name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip, self.port = server_path.split(':')

    def _send_to_server(self, data):
       self.socket.sendto(data, (self.ip, int(self.port))) 

    def _handle_client_events(self):
        event = pygame.event.wait()

        if event.type == pygame.QUIT:
            return False

        elif event.type == pygame.KEYDOWN:
            
            payload = {'name': self.name}
            
            if event.key == 273:
                payload['action'] = 'up'
            elif event.key == 274:
                payload['action'] = 'down'
            elif event.key == 275:
                payload['action'] = 'right'
            elif event.key == 276:
                payload['action'] = 'left'
            elif event.key == 32:
                payload['action'] = 'deploy_bomb'

            if 'action' in payload:
                self._send_to_server(json.dumps(payload).encode('utf-8'))

        return True

    def _bomb_cycle(self, name):
        time.sleep(3)
        payload = {'name': name, 'action': 'explode_bomb'}
        self._send_to_server(json.dumps(payload).encode('utf-8'))

    def _update_player(self, decoded_data):
        player_name = decoded_data['name']
        server_x = decoded_data['x']
        server_y = decoded_data['y']
        bombs = decoded_data['bombs']

        if player_name not in self.players_props:
            self.players_props[player_name] = {'bombs': []}

        self.players_props[player_name]['x'] = server_x
        self.players_props[player_name]['y'] = server_y

        if len(bombs) > len(self.players_props[player_name]['bombs']):
            self.players_props[player_name]['bombs'] = bombs

            bomb_cycle = Thread(target=self._bomb_cycle, args=(player_name, ))
            bomb_cycle.start()
        elif len(bombs) < len(self.players_props[player_name]['bombs']):
            try:
                self.players_props[player_name]['bombs'].pop(0)
            except IndexError:
                pass
        
    def _rcv_from_server(self):
        
        while True:
            data, _ = self.socket.recvfrom(4096)
            decoded_data = json.loads(data)

            print(decoded_data)
            self._update_player(decoded_data)

    def _draw_map(self, window):
        window.fill((0, 255, 0, 255))

        surface = pygame.Surface((40, 40))
        for i in range(15):
            window.blit(surface, (i * 40, 0))
            window.blit(surface, (0, i * 40))
            window.blit(surface, (14 * 40, i * 40))
            window.blit(surface, (i * 40, 14 * 40))

    def _draw(self, window):
        while True: 
            self._draw_map(window)

            for player_name in self.players_props:
                pos_x = self.players_props[player_name]['x']
                pos_y = self.players_props[player_name]['y']
                bombs = self.players_props[player_name]['bombs']

                pygame.draw.circle(
                    window,
                    (255, 255, 255, 255),
                    (pos_x, pos_y),
                    20)

                if bombs:
                    for bomb in bombs:
                        pygame.draw.circle(
                            window,
                            (0, 0, 0),
                            (bomb['x'], bomb['y']),
                            20)

            pygame.display.update()


    def run(self):
        pygame.init()
        window = pygame.display.set_mode((600, 600))

        rcv = Thread(target=self._rcv_from_server)
        rcv.start()

        draw = Thread(target=self._draw, args=(window, ))
        draw.start()

        while True:
            keep_running = self._handle_client_events()
            if not keep_running:
                break
            
            print(self.players_props)

        pygame.quit()

