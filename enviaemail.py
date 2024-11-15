import smtplib
import os
import bd

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Tratamento de erros
import traceback

def EnviaEmailComAnexo(emailDestino, msgTitulo, msgCorpo, anexo, nomeAnexo):
    try:
        username = "atendimento@indicecontabilidade.com.br"
        password = "Cnpj15830529@"
        mail_from = "atendimento@indicecontabilidade.com.br"
        mail_to = emailDestino
        mail_subject = msgTitulo
        mail_body = msgCorpo 
        mail_attachment=anexo
        mail_attachment_name=nomeAnexo
        mimemsg = MIMEMultipart()
        mimemsg['From']=mail_from
        mimemsg['To']=mail_to
        mimemsg['Subject']=mail_subject
        mimemsg.attach(MIMEText(mail_body, 'plain'))
        with open(mail_attachment, "rb") as attachment:
            mimefile = MIMEBase('application', 'octet-stream')
            mimefile.set_payload((attachment).read())
            encoders.encode_base64(mimefile)
            mimefile.add_header('Content-Disposition', "attachment; filename= %s" % mail_attachment_name)
            mimemsg.attach(mimefile)
            connection = smtplib.SMTP(host='smtp.indicecontabilidade.com.br', port=587)
            connection.starttls()
            connection.login(username,password)
            connection.send_message(mimemsg)
            connection.quit()
        status = True
    except:
        status = False
    return(status)

def EnviaEmailSemAnexo(emailDestino, msgTitulo, msgCorpo, emailBCC=None): #, anexo, nomeAnexo):
    try:
        username = "no-reply@pharmatracker.com.br"
        password = "Ba7a7a-fri7@"
        mail_from = "no-reply@pharmatracker.com.br"
        mail_to = emailDestino
        mail_subject = msgTitulo
        mail_body = msgCorpo 
#        mail_attachment=anexo
#        mail_attachment_name=nomeAnexo
        mimemsg = MIMEMultipart()
        mimemsg['From']=mail_from
        mimemsg['To']=mail_to
        if emailBCC != None:
            mimemsg['Bcc']=emailBCC
        mimemsg['Subject']=mail_subject
        mimemsg.attach(MIMEText(mail_body, 'plain'))
#        with open(mail_attachment, "rb") as attachment:
#            mimefile = MIMEBase('application', 'octet-stream')
#            mimefile.set_payload((attachment).read())
#            encoders.encode_base64(mimefile)
#            mimefile.add_header('Content-Disposition', "attachment; filename= %s" % mail_attachment_name)
#            mimemsg.attach(mimefile)
        connection = smtplib.SMTP(host='smtp.pharmatracker.com.br', port=587)
        connection.starttls()
        connection.login(username,password)
        connection.send_message(mimemsg)
        connection.quit()
        status = True
    #except:
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        status = False
    return(status)

def enviaEMail():
    pass


def Teste():
    CorpoEmail = '''
Prezado Cliente,

Informamos que os itens abaixo foram adquiridos junto à distribuidora GAM em 24/10/2024 às 08:39:

Código: 5000456028387
Descrição: XIGDUO XR - (10 + 1000) MG COM REV LIB PROL CT BL AL/AL X 30
Qtd. Comprada: 3
Preço : 182.06

Faturado para o CNPJ: 82.986.720/0001-32
Número do Pedido: 553051

Sds.
Equipe Pharma Tracker

 Esta é uma mensagem automática e não deve ser respondida.
'''

    CNPJFormatado = '00.000.0000-00'
    NumPedidoDistr = '0000000'

    # Busca o Email da Empresa
    SqlEmail = 'select Emails from farmacus_acessos where empresa = ' + str(2)
    DadosEmail = bd.OpenTable(SqlEmail)
    xEmailEmpresa = DadosEmail[0][0]

    emailTeste = 'kolmo.tech@gmail.com'

    xEmailDestino = 'kolmo.tech@gmail.com'
    xEmailOculto = 'ze2602@gmail.com,nilton117@terra.com.br'
    if len(xEmailEmpresa) > 0:
        xEmailDestino += (',' + xEmailEmpresa) # Inclui o email da empresa na lista de destinatários

    xMsgTitulo = 'AVISO PHARMATRACKER'

    print('xEmailDestino: ', xEmailDestino)
    print('xMsgTitulo   : ', xMsgTitulo)
    print('xEmailOculto : ', xEmailOculto)
    print('Corpo        : ', CorpoEmail)

    #input('Aguardando...')

    RetornoEmail = EnviaEmailSemAnexo(xEmailDestino, xMsgTitulo, CorpoEmail, xEmailOculto)
    print('Retorno E-mail: ', RetornoEmail)


    # xEmailDestino = 'ze2602@gmail.com'
    # xMsgTitulo = 'AVISO PHARMATRACKER'
    # xCC = 'kolmo.tech@gmail.com'

    # Retorno = EnviaEmailSemAnexo(xEmailDestino, xMsgTitulo, xMsgCorpo, xCC)
    # print('Retorno do Email: ', Retorno)

# Retorno = Teste()
# print(Retorno)