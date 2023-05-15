import threading
import etcd3
import time
import sys

cliente = sys.argv[1]
lider = None
lease = None
etcd = etcd3.client(host='localhost', port=2379)


def atualiza_lease():
    #utiliza as variáveis globais
    global lider
    global cliente
    global etcd

    #enquanto for o lider
    while lider == cliente:
        #atualiza o lease a cada 3 segundos
        time.sleep(3)
        etcd.put(key='/lider', value=cliente, lease=etcd.lease(25))


executando = True

while executando:

    #tenta adicionar uma chave para ser o lider    
    resultado = etcd.put_if_not_exists(key='/lider', 
                                      value=cliente, lease=etcd.lease(30))

    #se for o lider
    if resultado:
        print('Eu sou o líder: {}!'.format(cliente))
        leader = cliente

        #inicia a thread para atualizar o lease
        threading.Thread(target=atualiza_lease).start()

        #espera o usuário apertar algum botão para finalizar
        input('Aperte qualquer botão para finalizar...')
        #finaliza as variáveis, avisando a thread que não é mais o lider
        lider = None
        executando = False
        exit(0)
    
    #se não for o lider
    else:
        #pega o valor da chave lider
        lider = etcd.get('/lider')[0].decode('utf-8')
        print('O líder é {}'.format(lider))

        #enquanto tiver um lider
        while lider:
            time.sleep(5)
            #verifica se o lider ainda é o mesmo ou se não existe mais
            resultado = etcd.get('/lider')
            if resultado[0] == None or resultado[0].decode('utf-8') != lider:
                #se não for mais o lider, finaliza o loop para tentar ser o lider
                lider = None
                break