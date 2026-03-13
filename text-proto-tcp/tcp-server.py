import socket
import threading

HOST = "127.0.0.1"
PORT = 3333
BUFFER_SIZE = 1024

class State:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def add(self, key, value):
        with self.lock:
            self.data[key] = value
        return "OK, inregistrare adaugata"

    def get(self, key):
        with self.lock:
            if key in self.data:
                return f"DATA {self.data[key]}"
            return "EROARE: cheie invalida"

    def remove(self, key):
        with self.lock:
            if key in self.data:
                value = self.data.pop(key)
                return f"OK {value} sters"
            return "EROARE: cheie invalida"

    def list(self):
        with self.lock:
            if not self.data:
                return "DATA|"
            pairs = [f"{k}={v}" for k, v in self.data.items()]
            return "DATA|" + ",".join(pairs)

    def count(self):
        with self.lock:
            return f"DATA {len(self.data)}"

    def clear(self):
        with self.lock:
            self.data.clear()
        return "Toate datele sterse"

    def update(self, key, value):
        with self.lock:
            if key in self.data:
                self.data[key] = value
                return "Date actualizate"
            return "EROARE: cheie invalida"

    def pop(self, key):
        with self.lock:
            if key in self.data:
                value = self.data.pop(key)
                return f"DATA {value}"
            return "EROARE: cheie invalida"

state = State()

def process_command(command):
    parts = command.split()
    if not parts:
        return "EROARE: comanda invalida"

    cmd = parts[0].upper()

    if cmd == "ADD":
        if len(parts) < 3:
            return "EROARE: comanda invalida"
        return state.add(parts[1], ' '.join(parts[2:]))

    if cmd == "GET":
        if len(parts) != 2:
            return "EROARE: comanda invalida"
        return state.get(parts[1])

    if cmd == "REMOVE":
        if len(parts) != 2:
            return "EROARE: comanda invalida"
        return state.remove(parts[1])

    if cmd == "LIST":
        return state.list()

    if cmd == "COUNT":
        return state.count()

    if cmd == "CLEAR":
        return state.clear()

    if cmd == "UPDATE":
        if len(parts) < 3:
            return "EROARE: comanda invalida"
        return state.update(parts[1], ' '.join(parts[2:]))

    if cmd == "POP":
        if len(parts) != 2:
            return "EROARE: comanda invalida"
        return state.pop(parts[1])

    if cmd == "QUIT":
        return "QUIT"

    return "EROARE: comanda necunoscuta"

def handle_client(client_socket):
    with client_socket:
        while True:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break

                command = data.decode('utf-8').strip()
                response = process_command(command)

                response_data = f"{len(response)} {response}".encode('utf-8')
                client_socket.sendall(response_data)

                if response == "QUIT":
                    break

            except Exception as e:
                client_socket.sendall(f"EROARE: {str(e)}".encode('utf-8'))
                break

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[SERVER] Listening on {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"[SERVER] Connection from {addr}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()
