# cliente_corrigido.py

import socket
import time
import sys

HOST = "127.0.0.1"
PORT = 65432
timeoutDelay = 5

# Loop principal
while True:
    try:
        # 1. Cria um NOVO socket a cada tentativa dentro do loop.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("Tentando se conectar ao servidor...")
            s.connect((HOST, PORT))
            # Se chegou aqui, a conexão de rede foi um sucesso.
            # Agora, vamos ver o que a aplicação do servidor nos diz.
            resposta_inicial = s.recv(1024).decode('utf-8').strip()

            # 2. Verifica se a resposta é uma mensagem de erro do servidor
            if resposta_inicial.startswith("ERRO:"):
                print(f"O servidor recusou a conexão com a mensagem: '{resposta_inicial}'")
                # Lança um erro personalizado para ser capturado abaixo e acionar a retentativa
                raise ConnectionAbortedError("Servidor ocupado, tentando novamente.")
            
            # Conexão bem-sucedida
            print(f"Servidor disse: '{resposta_inicial}'")
            print("Conexão estabelecida com sucesso! Digite 'QUIT' para sair.")
            
            # Loop de envio/recebimento de mensagens
            while True:
                msg = input("Por favor, digite sua mensagem: ")

                try:
                    s.sendall(f"{msg}\n".encode('utf-8'))
                    if msg.upper() == 'QUIT':
                        print("Encerrando a conexão com o servidor...")
                        sys.exit(0) # Sai do programa completamente

                    data = s.recv(1024)
                    if not data:
                        print("O servidor encerrou a conexão.")
                        break
                    
                    resposta_servidor = data.decode('utf-8').strip()
                    print(f"Resposta do servidor: '{resposta_servidor}'")

                except (BrokenPipeError, ConnectionResetError):
                    print("Erro: A conexão com o servidor foi perdida.")
                    break # Sai do loop de mensagens para tentar reconectar            
                    # Se saiu do loop de mensagens (por perda de conexão), vai tentar reconectar
                    # A menos que o usuário tenha digitado QUIT e saído com sys.exit()

    except ConnectionRefusedError:
        # Cenário 1: Servidor totalmente offline
        print("Erro: A conexão foi recusada. O servidor parece estar offline.")
    
    except KeyboardInterrupt:
        print("\nCliente encerrado pelo usuário.")
        break # Sai do loop principal

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

    # 3. Bloco de espera para a próxima tentativa
    print(f"Tentando novamente em {timeoutDelay} segundos...")
    try:
        time.sleep(timeoutDelay)
    except KeyboardInterrupt:
        print("\nCliente encerrado pelo usuário.")
        break # Sai do loop principal

print("Cliente desconectado.")