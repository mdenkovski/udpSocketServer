import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json

clients_lock = threading.Lock()
connected = 0

clients = {}

def connectionLoop(sock):
   while True:
      data, addr = sock.recvfrom(1024)
      data = str(data)
      if addr in clients:
         if 'heartbeat' in data:
            clients[addr]['lastBeat'] = datetime.now()
         elif 'update' in data:
            #print(data)
            data = data[2:-1]
            #print(data)
            cleanData = data.replace("update", "", 1).replace("\\", "")
            #print(cleanData)
            msg = json.loads(cleanData)
            #print(msg['posX'])
            clients[addr]['posX'] = msg['posX']
            clients[addr]['posY'] = msg['posY']
            clients[addr]['posZ'] = msg['posZ']
            #print("received update")
      else:
         if 'connect' in data:
            clients[addr] = {}
            clients[addr]['lastBeat'] = datetime.now()
            #clients[addr]['color'] = 0
            #posX = random.randrange(0,10)
            #posY = random.randrange(0,10)
            #posZ = random.randrange(0,10)
            clients[addr]['posX'] = 0
            clients[addr]['posY'] = 0
            clients[addr]['posZ'] = 0
            message = {"cmd": 0,"player":{"id":str(addr)}}
            m = json.dumps(message)
            sock.sendto(bytes(m,'utf8'), (addr[0],addr[1])) #tell the client who they are
            #print(m)
            # for c in clients:
            #    sock.sendto(bytes(m,'utf8'), (c[0],c[1]))
            #print("Address: " + addr[0])
            #print("client: " + str(addr[1]))
           
            #print("Player Connected: ", addr)
            #send updated client list to all clients
            GameState = {"cmd": 0, "players": []}
            for c in clients:
               player = {}
               player['id'] = str(c)
               #player['color'] = clients[c]['color']
               player['posX'] = clients[c]['posX']
               player['posY'] = clients[c]['posY']
               player['posZ'] = clients[c]['posZ']
               GameState['players'].append(player)
            s=json.dumps(GameState)
            print(s)
            #print("Sending gamestate to all clients: " , s)
            for c in clients:
               sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
            

               

def cleanClients(sock):
   while True:
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
            print('Dropped Client: ', c)
            message = {"cmd": 2,"player":{"id":str(c)}}
            m = json.dumps(message)
            #print(m)
            clients_lock.acquire()
            del clients[c]
            clients_lock.release()
            #send the remaining clients which client dropped
            #print(clients)
            for remainingClient in clients:
               sock.sendto(bytes(m,'utf8'), (remainingClient[0],remainingClient[1]))

      time.sleep(1)

def gameLoop(sock):
   while True:
      GameState = {"cmd": 1, "players": []}
      clients_lock.acquire()
      #print (clients)
      for c in clients:
         player = {}
         #clients[c]['color'] = {"R": random.random(), "G": random.random(), "B": random.random()}
         player['id'] = str(c)
         #player['color'] = clients[c]['color']
         player['posX'] =  clients[c]['posX']
         player['posY'] =  clients[c]['posY']
         player['posZ'] =  clients[c]['posZ']
         GameState['players'].append(player)
      s=json.dumps(GameState)
      #print(s)
      for c in clients:
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      clients_lock.release()
      time.sleep(0.0333333333)

def main():
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(cleanClients,(s,))
   while True:
      time.sleep(1)

if __name__ == '__main__':
   main()
