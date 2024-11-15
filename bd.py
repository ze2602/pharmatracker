import mysql.connector #pip install mysql-connector-python

def conectaDB():
    con = mysql.connector.connect(host='botsdev.mysql.dbaas.com.br', database='botsdev', user='botsdev', password='Ba7a7a-fri7@')
    if con.is_connected():
        #print('Deu certo')
        mycursor = con.cursor() 
        mycursor.execute("Show tables;") 
        myresult = mycursor.fetchall() 
        for x in myresult: 
            #print(x)
            pass
    #	mycursor.execute("SELECT table_name FROM information_schema.tables;") 
    #	myresult = mycursor.fetchall() 
    #	for x in myresult: 
    #		print(x) 	    
        consulta_sql = "select * from bots"
        cursor = con.cursor()
        cursor.execute(consulta_sql)
        linhas = cursor.fetchall()
        #print("Número total de registros retornados: ", cursor.rowcount)
        #print("\nMostrando os bots cadastrados")
        for linha in linhas:
            #print("Id:", linha[0])
            #print("Name:", linha[1])
            #print("Descri:", linha[2], "\n")
            pass
    #	insere_registro = "INSERT INTO bots (name, descr) VALUES ('busca_ECAC', 'Baixa diagnósticos fiscais de clientes')"
    #	cursor.execute(insere_registro)
    #	con.commit()
        con.close()
    else:
        pass
        #print('Erro Conexão')

def OpenTable(sql):
    con = mysql.connector.connect(host='botsdev.mysql.dbaas.com.br', database='botsdev', user='botsdev', password='Ba7a7a-fri7@')
    if con.is_connected():
        mycursor = con.cursor()
        mycursor.execute(sql) 
        myresult = mycursor.fetchall()

    else:
        myresult = 'ERRO DB'
    con.close()
    return myresult

def InsereRegistro(sql):
    con = mysql.connector.connect(host='botsdev.mysql.dbaas.com.br', database='botsdev', user='botsdev', password='Ba7a7a-fri7@')
    if con.is_connected():
        mycursor = con.cursor()
        mycursor.execute(sql) 
        myresult = 'Gravado'

    else:
        myresult = 'ERRO DB'
    con.commit()
    con.close()
    return myresult

def SalvarRegistro(sql):
    con = mysql.connector.connect(host='botsdev.mysql.dbaas.com.br', database='botsdev', user='botsdev', password='Ba7a7a-fri7@')
    if con.is_connected():
        mycursor = con.cursor()
        mycursor.execute(sql) 
        myresult = 'Gravado'

    else:
        myresult = 'ERRO DB'
    con.commit()
    con.close()
    return myresult