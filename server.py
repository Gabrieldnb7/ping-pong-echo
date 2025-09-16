import socket
import threading

# Define o host como localhost e a porta
HOST = "0.0.0.0" # Aceita conexões de qualquer interface
PORT = 65432 # Porta escolhida

# 1. Cria uma trava (lock). Este objeto vai garantir que apenas uma thread 
#    (representando um cliente) seja executada na seção crítica por vez.
client_lock = threading.Lock()

def handle_client(conn, addr):
    """
    Função que será executada em uma nova thread para cada cliente.
    """
    print(f"Nova tentativa de conexão de {addr}")

    # 2. Tenta adquirir a trava de forma não-bloqueante.
    #    Se conseguir (retorna True), o servidor está livre.
    #    Se não conseguir (retorna False), o servidor está ocupado.
    if client_lock.acquire(blocking=False):
        print(f"Conexão de {addr} aceita. Servidor agora está ocupado.")
        try:
            # Envia uma mensagem de boas-vindas para o cliente saber que conectou
            conn.sendall("Conexão estabelecida. Bem-vindo!\n".encode('utf-8'))
            
            # O 'with' garante que a conexão será fechada ao final do bloco
            with conn:
                while True:
                    # Espera por dados do cliente (até 1024 bytes)
                    data = conn.recv(1024)
                    if not data:
                        print(f"Cliente {addr} desconectou inesperadamente.")
                        break

                    mensagem_cliente = data.decode('utf-8').strip()
                    print(f"Recebido de {addr}: '{mensagem_cliente}'")

                    if mensagem_cliente == 'QUIT':
                        print(f"Comando QUIT recebido de {addr}.")
                        break

                    # Envia a mesma mensagem de volta para o cliente (eco)
                    conn.sendall(data)
        except (ConnectionAbortedError, ConnectionResetError):
            print(f"Cliente {addr} desconectou.")

        except Exception as e:
            # Captura outros erros inesperados para não derrubar a thread
            print(f"Ocorreu um erro com o cliente {addr}: {e}")

        finally:
            # 3. CRÍTICO: Libera a trava ao final da comunicação.
            #    Isso permite que um novo cliente possa se conectar.
            #    O 'finally' garante que isso aconteça mesmo se ocorrer um erro.
            client_lock.release()
            print(f"Conexão com {addr} encerrada. Servidor está livre novamente.")
    else:
        # 4. Se não conseguiu a trava, o servidor está ocupado.
        print(f"Conexão de {addr} recusada: Servidor ocupado.")
        conn.sendall("ERRO: Servidor ocupado. Tente novamente mais tarde.\n".encode('utf-8'))
        conn.close() # Fecha a conexão com o cliente rejeitado

# Cria o socket do servidor
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Servidor escutando em {HOST}:{PORT}")

    # 5. Loop principal do servidor para aceitar conexões continuamente.
    while True:
        # Aceita uma nova conexão (bloqueante)
        conn, addr = s.accept()
        
        # 6. Cria e inicia uma nova thread para cuidar do cliente recém-conectado.
        #    O servidor principal volta imediatamente para o s.accept() para
        #    esperar por novas conexões (que poderão ser rejeitadas se a trava estiver ocupada).
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()