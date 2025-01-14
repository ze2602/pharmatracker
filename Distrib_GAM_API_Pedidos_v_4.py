# Biblioteca para Uso e Manipulação de Data e Hora
import time
import datetime
from datetime import datetime

import requests

import bd
import enviaemail as email


def IniciaBot_GAM_API_Pedidos(CodEmpresa, token):

    Registros = []
    # Monta o Header para consultas
    headers = {
        'accept': '*/*',
        'Authorization': f'Bearer {token}', 
        'Content-Type': 'application/json',
    }
    #print('header:', headers)

    Hoje = datetime.now()
    Hoje = Hoje.strftime('%Y-%m-%d')

    Dia = datetime.now()
    Dia = Dia.strftime('%d/%m/%Y')
    Hora = datetime.now().strftime('%H:%M')
    #print('Hoje: ', Hoje)

    # Busca CNPJ da Empresa
    SqlEmpreaa = 'select * from tb_empresas where id = ' + str(CodEmpresa)
    DadosEmpresa = bd.OpenTable(SqlEmpreaa)
    CNPJEmpresa = DadosEmpresa[0][3]
    NomeEmpresa = DadosEmpresa[0][1]
    print('==================================================================================================================')
    print('Empresa: ', CodEmpresa, 'CNPJ: ', CNPJEmpresa, ' - ', NomeEmpresa)
    CNPJFormatado = CNPJEmpresa
    CNPJEmpresa = CNPJEmpresa.replace('.','')
    CNPJEmpresa = CNPJEmpresa.replace('-','')
    CNPJEmpresa = CNPJEmpresa.replace('/','')

    # Seleciona os registros da empresa em questão, cuja data de início das operações seja menor ou igual a data atual
    Sql = 'select farmacus_Pedidos.id, ean, farmacus_prods.descri, qtde, precoMax, Distrib, acao, DataInicio from farmacus_Pedidos INNER JOIN farmacus_prods ON farmacus_Pedidos.ean = farmacus_prods.ean1 where (empresa = ' + str(CodEmpresa) + ') and (DataInicio <= "' + Hoje + '") order by farmacus_Pedidos.id '
    lstPedidos = bd.OpenTable(Sql)
    QtdeItens = len(lstPedidos)

    if QtdeItens > 0:
        Continuar = True
    else:
        Continuar = False

    if Continuar:

        Contador = 0
        Primeiro = True
        Acoes = []

        aItem = []
        aEAN = []
        aDescri = []
        aQtde = []
        aPrecoMax = []
        aPrecoDistrib = []
        aDistrib = []
        aAcao = []
        aStatus = []
        aComprado = []
        aQtdeComprada = []

        # Seleciona os códigos EAN dos produtos a serem consultados
        while Continuar:
            prodItem = lstPedidos[Contador][0]
            prodCodigo = lstPedidos[Contador][1]
            prodDescri = lstPedidos[Contador][2]
            prodQtde = lstPedidos[Contador][3]
            prodPrecoMax = lstPedidos[Contador][4] # Função para verificar preço da distribuidora
            prodDistrib = lstPedidos[Contador][5] 
            prodAcao = lstPedidos[Contador][6] # Verificar se é para comprar ou consultar

            if (prodDistrib == 'TODAS') or (prodDistrib == 'GAM'):
                aItem.append(prodItem)
                aEAN.append(prodCodigo)
                aDescri.append(prodDescri)
                aQtde.append(prodQtde)
                aPrecoMax.append(prodPrecoMax)
                aPrecoDistrib.append(0)
                aAcao.append(prodAcao)
                aStatus.append('Não Encontrado')
                aComprado.append('NÃO')
                aQtdeComprada.append(0)
                
                #aDatIni.append(prodDatIni)
            Contador += 1
            if Contador >= QtdeItens:
                break

        # Consulta via API

        # # Consulta Código da Empresa na Distribuidora
        # json_Empresa = {
        #     'cnpj': CNPJEmpresa,
        # }
        # #print('json Empresa:', json_Empresa)
        # responseEmpresa = requests.post('https://j16.gam.com.br:8584/busca-cliente', headers=headers, json=json_Empresa)  
        

        #print('EANs:', aEAN)

        # Consultar Produtos pelos códigos EAN    
        json_produtos = {
            "nuCnpjCliente": CNPJEmpresa,
            "eans":aEAN,
            "verificaProjetoConexao": False,
        }

        #print('json Produtos:', json_produtos)

        responseProdutos = requests.post('http://apitomcat.gam.com.br:8280/ApiPedidos/api/produtos/listar-eans', headers=headers, json=json_produtos)
        if responseProdutos.status_code == 200:
            #print('Resposta: ', responsePreco)
            dataProdutos = responseProdutos.json()
            #print('Retorno: ', dataProdutos)
            #print('Tamanho: ', len(dataProdutos.get('produtos')))


    ####### Agora tem que selecionar os itens que possuem estoque
            itensComprar = []
            ItensRetornados = dataProdutos.get('produtos')
            for ItemRetornado in ItensRetornados:
                codEAN = ItemRetornado.get('cdGtin')
                PrecoProduto = ItemRetornado.get('vlProduto')
                temEstoque = ItemRetornado.get('possuiEstoque')

                Acao = 'CONSULTAR'
                if str(codEAN) in aEAN:

                    # Acho o índice na array
                    # print('achei o EAN na lista')                    
                    indice = aEAN.index(str(codEAN))

                    # Grava Dados da Consulta
                    aPrecoDistrib[indice] = PrecoProduto


                    PrecoMax = aPrecoMax[indice]
                    QtdeComprar = aQtde[indice]
                    Acao = aAcao[indice]

                    if ItemRetornado.get('possuiEstoque'):
                        # print('Esse Item tem estoque: ', ItemRetornado)
                        # Verificar se o preço da distribuidora está OK
                        #print('Código EAN: ', codEAN, ' - Tipo: ', type(codEAN))
                        #print('Preço     : ', PrecoProduto, ' - Tipo: ', type(PrecoProduto))

                        if ((PrecoMax == 0) or (PrecoMax >= PrecoProduto)):
                            if (Acao == 'COMPRAR'): 
                                # Inclui o produto na array de itens a serem comprados
                                # print('Preço atende as condições do cliente e é para comprar')
                                Item = {"cdGtin": codEAN,"qtPedido": QtdeComprar}
                                itensComprar.append(Item)
                                aStatus[indice] = 'Tudo Ok. Vai Pedir'
                            else:
                                aStatus[indice] = 'CONSULTA: Tem em estoque'
                        else:
                            aStatus[indice] = 'Tem estoque mas o preço é superior ao preço máximo definido'
                    else:
                        aStatus[indice] = 'Não tem estoque'
                        #print('Esse Item NÃO tem estoque: ', ItemRetornado)
                else:
                    #print('NÃO achei o EAN na lista')
                    PrecoMax = 9999999999.99

            #print('Itens a Comprar: ', itensComprar)


            # Gerar itens para o pedido
            # RETIRAR ESSE TEXTO=============================
            # Item = {"cdGtin": '5000456028387',"qtPedido": 10}
            # itensComprar.append(Item)
            # RETIRAR ESSE TEXTO=============================
            if len(itensComprar) > 0:
                #print('Itens a comprar: ', itensComprar)
                GerarPedido(CNPJEmpresa, itensComprar, headers, CodEmpresa, CNPJFormatado, aDescri, aEAN)

            regs = len(aEAN)
            cont = 0
            while True:
                print('EAN: ', aEAN[cont], ' - ', aAcao[cont], ' - ', aDescri[cont], 'Qtde: ', aQtde[cont], ' Preço Máximo:', aPrecoMax[cont],  ' - Preço Distribuidora: ', aPrecoDistrib[cont], ' - ', aStatus[cont])
                cont += 1
                if cont >= regs:
                    break
        else:
            print('Erro ao fazer a solicitação (lista-preco):', responseProdutos.status_code)
            return False

        for Registro in Registros:
            print(Registro)

        #input('Teste')
    else:
        print('Empresa não possui itens a serem adquiridos')
    return True








def GerarPedido(CNPJCliente, Produtos, headersPedido, CodEmpresa, CNPJFormatado, aDescri, aEAN):
    # Variáveis 
    Hoje = datetime.now()
    Hoje = Hoje.strftime('%Y-%m-%d')

    Dia = datetime.now()
    Dia = Dia.strftime('%d/%m/%Y')
    Hora = datetime.now().strftime('%H:%M')


    # Busca número do próximo pedido
    Sql = 'select NumPedido from farmacus_params'
    Farmacus = bd.OpenTable(Sql)
    NumPedido = Farmacus[0][0] 


    NumPedidoSTR = '000000' + str(NumPedido)
    LenNumPedido = len(NumPedidoSTR)

    NumPedidoFTrack = 'trk' + NumPedidoSTR[LenNumPedido-6:]    
    #print('Número do Pedido: ', NumPedidoFTrack)


    NovoPedido = NumPedido + 1
    Sql = "UPDATE farmacus_params SET "
    Sql += "NumPedido = "+ str(NovoPedido) 
    Sql += " where id = 1"

    #UPDATE `farmacus_params` SET `NumPedido` = '2601' WHERE `farmacus_params`.`id` = 1;

    Gravou = bd.InsereRegistro(Sql)

    json_Pedido = {
	"nuCnpjCliente": CNPJCliente,
	"cdPedidoCliente": NumPedidoFTrack,
	"produtos": Produtos,
    "verificaProjetoConexao": False,
	"projetoRav": False,
	"consideraPrecoEspecial": False
    }

    #print('json_Pedido: ', json_Pedido)

    #input('Vai enviar o pedido....')

    responsePedido = requests.post('http://apitomcat.gam.com.br:8280/ApiPedidos/api/pedido/gerar', headers=headersPedido, json=json_Pedido)
    if responsePedido.status_code == 200:
        # Obtem número do pedido da Distribuidora 
        dataPedidos = responsePedido.json()
        #print('Retorno: ', dataPedidos)
        NumPedidos = dataPedidos.get('pedidos')
        NumPedidoDistr = NumPedidos[0].get('cdPedidoGam')
        msgPedidoDistr = NumPedidos[0].get('msg')
        print('Pedido Distr: ', NumPedidoDistr)
        print('    Mensagem: ', msgPedidoDistr)

        if msgPedidoDistr != 'PEDIDO PROCESSADO COM SUCESSO':
            print('********************************************************************')
            print('Problemas no envio do pedido:', msgPedidoDistr)
            print('********************************************************************')
            return False

        # Aguarda 5 segundos...
        time.sleep(5)
    
        # Consultar Pedido
        json_ConsultaPedido = {
        "nuCnpjCliente": CNPJCliente,
	    "cdPedidoGam": NumPedidoDistr        
        }
        #print('json_ConsultaPedido: ', json_ConsultaPedido)

        responseConsultaPedido = requests.post('http://apitomcat.gam.com.br:8280/ApiPedidos/api/pedido/consultar', headers=headersPedido, json=json_ConsultaPedido)
        if responseConsultaPedido.status_code == 200:
            dataConsultaPedidos = responseConsultaPedido.json()
            #print('Dados Consulta Pedidos: ', dataConsultaPedidos)
            statusPedidoDistr = dataConsultaPedidos.get('status')
            prodsPedidoDistr = dataConsultaPedidos.get('produtos')
            #print('Status do Pedido: ', statusPedidoDistr)
            #print('Produtos  Pedido: ', prodsPedidoDistr)
            # INSERIR NOVO TRECHO AQUI:


            ##### NOVO TRECHO

            CorpoEmail = f"""
Prezado Cliente,

Informamos que os itens abaixo foram adquiridos junto à distribuidora GAM em {Dia} às {Hora}:

""" 
            
            #print(CorpoEmail)
            EnviarEmail = False
            for ItemPedido in prodsPedidoDistr:
                xEAN = ItemPedido.get('cdGtin')
                xQtdPed = ItemPedido.get('qtSolicitada')
                xQtdAte = ItemPedido.get('qtAtendida')
                xPrecoU = ItemPedido.get('vlPrecoUnitario')
                xAtendido = ItemPedido.get('dsMotivo')
                #print('Produto: ', xEAN, ' Qtde Pedida: ', xQtdPed, ' Qtde Atendida: ', xQtdAte, ' Preço: ', xPrecoU)
                if (xQtdAte > 0): # and (xAtendido == 'ATENDIDO'):
                    EnviarEmail = True
                    ### EXCLUIR
                    #xQtdPed = 50
                    ### EXCLUIR

                    # Busca dados tabela farmacus_Pedidos
                    Sql = "select * from farmacus_Pedidos where empresa = " + str(CodEmpresa) + " and ean = '" + str(xEAN) + "'"
                    #print('SQL: ', Sql)
                    DadosOriginais = bd.OpenTable(Sql)
                    #print('Dados Originais: ')
                    #print(DadosOriginais)
                    #input('Aguardando...')

                    # Atualizar tabela farmacus_Pedidos
                    xQtdSld = xQtdPed - xQtdAte
                    if xQtdSld > 0:
                        Sql = "UPDATE farmacus_Pedidos SET "
                        Sql += "qtde = "+ str(xQtdSld) 
                        Sql += " where empresa = " + str(CodEmpresa) + " and ean = '" + str(xEAN) + "'"
                        xLog = 'Compra Parcial'
                    elif xQtdSld == 0:
                        Sql = "DELETE FROM farmacus_Pedidos "
                        Sql += " where empresa = " + str(CodEmpresa) + " and ean = '" + str(xEAN) + "'"
                        xLog = 'Compra Total'
                    Gravou = bd.InsereRegistro(Sql)

                    # Atualizar tabela farmacus_LogPedidos
                    Sql = 'INSERT INTO farmacus_LogPedidos ('
                    Sql += 'id_Pedidos, ' 
                    Sql += 'empresa, ' 
                    Sql += 'user, '
                    Sql += 'ean, '
                    Sql += 'qtde, '
                    Sql += 'precoMax, ' 
                    Sql += 'distr, '
                    Sql += 'acao, '
                    Sql += 'DataInicio, ' 
                    Sql += 'LOG, '
                    Sql += 'compra_pedido, '
                    Sql += 'compra_qtde, '
                    Sql += 'compra_distr, '
                    Sql += 'compra_preco, '
                    Sql += 'compra_data)'
                    Sql += 'VALUES ('
                    Sql += str(DadosOriginais[0][0]) + ', '  	    # id_Pedidos
                    Sql += str(CodEmpresa) + ', ' 				    # empresa
                    Sql += '"PharmaTrackerAPIGAM", '                # idUser
                    Sql += '"' + str(DadosOriginais[0][2]) + '", '  # ean
                    Sql += str(DadosOriginais[0][3]) + ', ' 		# qtde
                    Sql += str(DadosOriginais[0][4]) + ', ' 		# precoMax
                    Sql += '"' + DadosOriginais[0][5] + '", ' 		# distrib
                    Sql += '"COMPRAR", ' 		                    # acao
                    Sql += '"' + str(DadosOriginais[0][8]) + '", '  # DataIni
                    Sql += '"' + xLog + '", ' 		                # LOG
                    Sql += '"' + str(NumPedidoDistr) + '", ' 		# compra_pedido
                    Sql += str(xQtdAte) + ', ' 		                # compra_qtde
                    Sql += '"GAM", ' 							    # compra_distr
                    Sql += str(xPrecoU) + ', ' 		                # compra_preco
                    Sql += '"' + str(datetime.now()) + '"' 		    # compra_data
                    Sql += ')'
                    Gravou = bd.InsereRegistro(Sql)

                    if str(xEAN) in aEAN:
                        # Acho o índice na array
                        indice = aEAN.index(str(xEAN))

                    CorpoEmail += 'Código: ' + str(xEAN) + '\n'
                    CorpoEmail += 'Descrição: ' + aDescri[indice] + '\n' # PRECISA MUDAR PARA DESCRIÇÃO
                    CorpoEmail += 'Qtd. Comprada: ' + str(xQtdAte) + '\n'
                    CorpoEmail += 'Preço : ' + str(xPrecoU) + '\n\n'

            if EnviarEmail:
                # Busca o Email da Empresa
                SqlEmail = 'select Emails from farmacus_acessos where empresa = ' + str(CodEmpresa)
                DadosEmail = bd.OpenTable(SqlEmail)
                xEmailEmpresa = DadosEmail[0][0]

                CorpoEmail += f'Faturado para o CNPJ: {CNPJFormatado} \n'
                CorpoEmail += f'Número do Pedido: {NumPedidoDistr} \n\n'

                CorpoEmail += 'Sds. \n'

                CorpoEmail += 'Equipe Pharma Tracker \n'

                CorpoEmail += '\n Esta é uma mensagem automática e não deve ser respondida. \n'

                print(CorpoEmail)
                xEmailDestino = 'kolmo.tech@gmail.com'
                xEmailOculto = 'ze2602@gmail.com,nilton117@terra.com.br'
                if len(xEmailEmpresa) > 0:
                    xEmailDestino += (',' + xEmailEmpresa) # Inclui o email da empresa na lista de destinatários

                xMsgTitulo = 'AVISO PHARMATRACKER'        
                RetornoEmail = email.EnviaEmailSemAnexo(xEmailDestino, xMsgTitulo, CorpoEmail, xEmailOculto)
                print('Retorno E-mail: ', RetornoEmail)
            ##### NOVO TRECHO
            log_message = f"[{datetime.now()}] Consulta bem-sucedida!\n"
        else:
            print('Erro ao consultar o pedido (pedido/consultar):', responsePedido.status_code)
            log_message = f"[{datetime.now()}] Erro ao consultar o pedido (pedido/consultar): {str(responsePedido.status_code)}\n"             

    else:
        print('Erro ao enviar o pedido (pedido/gerar):', responsePedido.status_code) 
        log_message = f"[{datetime.now()}] Erro ao enviar o pedido (pedido/gerar): {str(responsePedido.status_code)}\n"             
    # Gravar Log
    
    with open("execucoes.log", "a") as log_file:
        log_file.write(log_message)
    print(log_message)    



    #print('json Pedido: ', json_Pedido)

    # Falta Enviar Pedido para Distribuidora

def GeraTokenGAM():
    # Dados para acesso à API da GAM
    url = 'http://apitomcat.gam.com.br:8280/ApiPedidos/api/token/gerar'
    headers = {
        'accept': '*/*',
        'Content-Type': 'application/json',
    }
    json_data = {
        'username': 'kolmo',
        'password': 'uMolAUkW',
    }
   
    # Obtem Token para acesso
    try:
        response = requests.post(url, headers=headers, json=json_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            HoraToken = datetime.now()
            print('Token gerado em: ', HoraToken)
        else:
            print('Erro ao fazer a solicitação de geração do Token:', response.status_code)    
            HoraToken = None
            token = None
    except Exception as e:
        print('Erro: ', e)
        print('Data/hora: ', datetime.now(), ' - Erro de conexão com servidor GAM. Aguardando 5 minutos para reconectar...')
        log_message = f"[{datetime.now()}] Erro de conexão com servidor GAM: {str(e)}\n"
        # Salvar no arquivo de log
        with open("execucoes.log", "a") as log_file:
            log_file.write(log_message)
        print(log_message)
        time.sleep(300)
        HoraToken = None
        token = None

    return token, HoraToken
    
# # Define tempo entre uma consulta e outra 
# MinutosEspera = 20 # Informar em minutos
# TempoEspera = (60*MinutosEspera) # Converte para Segundos

# # Define tempo de validade do Tonken (em horas)
# HorasValidadeToken = 2 # Informar em Horas
# TempoValidadeToken = (60*HorasValidadeToken) # Converte para Minutos
# UltimoToken = None
# Token = None
# while True:
#     # Controle Tempo de Validade do token
#     if (Token == None):
#         Token, UltimoToken = GeraTokenGAM()

#     if Token != None:
#         HoraAtual = datetime.now()
#         print('Hora Token: ', UltimoToken, ' Tipo: ',type(UltimoToken))
#         print('Hora Atual: ', HoraAtual, ' Tipo: ',type(HoraAtual))
#         TempoToken = ((HoraAtual - UltimoToken).total_seconds()) / 60
#         print('Tempo uso do Token: ', TempoToken, ' minutos')
#         if TempoToken > TempoValidadeToken: #TempoValidadeToken:
#             print('Gerar novo Token')
#             Token = None
    

#     # # Dados para acesso à API da GAM
#     # url = 'http://apitomcat.gam.com.br:8280/ApiPedidos/api/token/gerar'
#     # headers = {
#     #     'accept': '*/*',
#     #     'Content-Type': 'application/json',
#     # }
#     # json_data = {
#     #     'username': 'kolmo',
#     #     'password': 'uMolAUkW',
#     # }
#     # # Obtem Token para acesso
#     # response = requests.post(url, headers=headers, json=json_data)

#     # if response.status_code == 200:
#     if Token != None:
#         # data = response.json()
#         # token = data.get("token")
#         #print('Token: ', token)
#         # Incluir LOOP para verificar todas as empresas que possuem pedidos

#         for Empresa in range(6):
#             if Empresa >= 2 and Empresa <= 3:
#             #if Empresa >= 100: # EXCLUIR ********************************************************
#                 IniciaBot_GAM_API_Pedidos(Empresa, Token)

#         print('Última Consulta: ', datetime.now())
#         print('Aguardando: ', (TempoEspera/60), ' minutos')
#         time.sleep(TempoEspera)        

#         print('==================================================================================================================')
#     break

Token, UltimoToken = GeraTokenGAM()
for Empresa in range(6):
    if (Empresa >= 2 and Empresa <= 3) or (Empresa == 6):
        IniciaBot_GAM_API_Pedidos(Empresa, Token)
print('Última Consulta: ', datetime.now())
