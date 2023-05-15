import sys
import etcd3
import threading
import time

cliente = sys.argv[1]
lider = None
lease = None
etcd = etcd3.client(host='localhost', port=2379)


def atualiza_lease():
    # Utiliza as variáveis globais
    global lider
    global cliente
    global etcd

    # Enquanto for o líder, atualiza o lease
    while lider == cliente:
        # Atualiza o lease a cada 3 segundos
        time.sleep(1)
        etcd.put(key='/lider', value=cliente, lease=etcd.lease(25))


executando = True

while executando:

    # Tenta adicionar uma chave para ser o líder
    resultado = etcd.put_if_not_exists(key='/lider', 
                                      value=cliente, lease=etcd.lease(30))

    # Se for o líder
    if resultado:
        print('Eu sou o líder: {}!'.format(cliente))
        lider = cliente

        # Inicia a thread para atualizar o lease
        threading.Thread(target=atualiza_lease).start()

        # Espera o usuário apertar algum botão para finalizar
        input('Aperte qualquer botão para finalizar...')
        # Finaliza as variáveis, avisando a thread que não é mais o lider
        lider = None
        executando = False
        exit(0)
    
    # Se não for o líder
    else:
        # Pega o valor da chave líder
        lider = etcd.get('/lider')[0].decode('utf-8')
        print('O líder é {}'.format(lider))

        # Enquanto tiver um líder
        while lider:
            time.sleep(5)
            # Verifica se o líder ainda é o mesmo ou se não existe mais
            resultado = etcd.get('/lider')
            if resultado[0] == None or resultado[0].decode('utf-8') != lider:
                # Se não for mais o líder, finaliza o loop para tentar ser o líder
                lider = None
                break