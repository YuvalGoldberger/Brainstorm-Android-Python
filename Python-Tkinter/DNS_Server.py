import socket
import threading
import random

class DNS:
    def __init__(self):
        """
        * Runs the DNS Server and waits for clients
        """
        server = socket.socket()
        server.bind(('0.0.0.0', 11111))
        server.listen(100)
        self.dns = {}

        while True:
            client, address = server.accept()
            print(address, "connected")
            threading.Thread(target=self.clientHandler, args=(client, address), daemon=True).start()

    def clientHandler(self, client, address):
        """
        * Handles clients' requests (get / set)
        """
        cmd = client.recv(1024).decode()
        print("cmd", cmd)
        target = cmd.split(" ")[1].split("\n")[0]
        print(target)
        if "set" in cmd:
            code = self.setNewDNS(target)
            client.send(f'{code}\n'.encode())
            print(f'set {code} for {target}')
        elif "get" in cmd:
            ip = self.getIPByCode(target)
            if ip is None:
                client.send("Wrong Code\n".encode())
                print("client gave wrong code.")
            else:
                client.send(f'{ip}\n'.encode())
                print(f'given {ip} for {target}')
        else:
            pass

    def setNewDNS(self, ip):
        """
        * Sets a KEY for the IP Value and returns it.
        """
        code = str(random.randint(1000, 10000))
        while self.dns.get(code) is not None:
            code = str(random.randint(1000, 10000))
        self.dns[code] = ip
        print(f"dict is now: {self.dns}")
        return code
        
    def getIPByCode(self, code):
        """
        * Returns the IP for a given Key.
        """
        return self.dns.get(code)


if __name__ == '__main__':
    DNS()