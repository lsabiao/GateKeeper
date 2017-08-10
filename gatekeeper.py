#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import sqlite3

#ujson is fasters
try:
    import ujson as json
except:
    import json

#colorama for Colors
try:
    import colorama
    colorama.init()
    cRED = colorama.Fore.RED
    cBLUE = colorama.Fore.BLUE
    cGREEN = colorama.Fore.GREEN
    cYELLOW = colorama.Fore.YELLOW
    cBRIGHT = colorama.Style.BRIGHT
    cRESET_ALL = colorama.Style.RESET_ALL

except:
    import platform
    if(platform.system() == "Linux"):
        cRED = "\033[31m"
        cBLUE = "\033[34m"
        cGREEN = "\033[32m"
        cYELLOW = "\033[33m"
        cBRIGHT = "\033[37;1m"
        cRESET_ALL = "\033[0m"

    else:
        cRED = ""
        cBLUE = ""
        cGREEN = ""
        cYELLOW = ""
        cBRIGHT = ""
        cRESET_ALL = ""

secToken = ""
try:
    from jose import jwt
    jwtEnabled = True
except:
    print "{red}python-jose is not avaible!".format(red=cRED)
    print "run {bright} pip install python-jose {reset}{red} to enable jwt{reset}".format(bright=cBRIGHT,red=cRED,reset=cRESET_ALL)
    jwtEnabled = False

jwtEnabled = False #not implemented... yet

#TODO JWT
#   desempacotar o jwt recebido
#   empacotar todo o output
#   get e delete nao tem body para jwt, oque faremos?
#TODO desabilitar o jwt por parametro

_ver_ = "0.7"
#TODO SQL INJECTION
#   escapar todos os caracteres em todas as queries


#TODO FOREIGN KEY
#   pegar a relação entre duas tablelas
#   pegar o resultado na outra tabela e adicionar ao dict atual

#TODO SELECT FILTERS
#   avaliar a possibilidade

asciimsg ='''
welcome to the{0} _         _   __
              | |       | | / /
  __ _   __ _ | |_  ___ | |/ /   ___   ___  _ __    ___  _ __
 / _` | / _` || __|/ _ \|    \  / _ \ / _ \| '_ \  / _ \| '__|
| (_| || (_| || |_|  __/| |\  \|  __/|  __/| |_) ||  __/| |
 \__, | \__,_| \__|\___|\_| \_/ \___| \___|| .__/  \___||_|
  __/ |                                    | |
 |___/{1}
'''.format(cBLUE,cRESET_ALL)

#path to the sqlite
_db_ = "dedig.sqlite"

#ANSI Colors


#config's header
header = "***the gateKeeper's config file***"

class Server:
    '''
        baseado no Arauto: 'http://github.com/lsabiao/arauto

        O servidor deve pegar o request e procurar um endpoint adequado
        entao deve ver se o verbo de requisicao esta disponivel

        se nao for disponivel retornar erro (404?)
        caso seja disponivel processar as queries e devolvar os dados como json

        se nao for um get, retornar o http code equivalente

        200 - ok
        201 - created

        304 - not modified

        401 - bad request
        403 - forbidden
        405 - method not allowed
        409 - conflict

        500 - server error

    '''
    def __init__(self,port,endpoints):
        self.host = ""
        self.port = port
        self.endpoints = endpoints


    def run(self):
        import socket

        self.location = socket.gethostbyaddr(socket.gethostbyname(socket.gethostname()))[0]
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.host,self.port))
        self.s.listen(10)

        self.ip = socket.gethostbyaddr(socket.gethostbyname(socket.gethostname()))
        self.ip = self.ip[2][0]

        print("Server Running on {0}:{1}\n".format(cGREEN+self.ip,cYELLOW+str(self.port)+cRESET_ALL))

        while True:
            #the loop
            self.conn, self.addr = self.s.accept()
            self.data = self.conn.recv(1024)
            try:
                #pegar o caminho
                self.url = self.getUrl(self.data)
                #the request URL Arguments
                try:
                    self.arguments = self.getUrlArgs(self.data)
                except:
                    self.arguments = ""
                #the request Method
                self.method = self.data.split(b" ")[0].decode()

                #the headers
                try:
                    self.headers = self.getHeaders(self.data)
                except:
                    raise
                    self.headers = None

                self.body = self.getBody(self.data)
                #find the endpoint
                code = 404
                payload = "Not Found"
                exists = False

                for a in self.endpoints:
                    if(self.url == a.url):
                        exists = True

                #THE Index returns the list of endpoints
                if(self.method == "GET" and (self.url=="/" or self.url == "index.html")):
                    exists == False
                    prep = []
                    for f in self.endpoints:
                        aux = {"url":f.url,"get":f.get,"post":f.post,"delete":f.delete,"patch":f.patch}
                        prep.append(aux)
                        payload = json.dumps(prep,ensure_ascii=False)
                        code = 200


                for point in self.endpoints:
                    if(exists == False):
                        break

                    #authentication
                    if(jwtEnabled):
                        pass
                    else:
                        try:
                            if(self.headers["Auth"] != secToken):
                                code = 403
                                payload = "Auth Error"
                                break
                        except:

                            code = 403
                            payload = "Auth Error"
                            break

                    #routing the method
                    #THE SELECT ENDPOINT
                    if(self.method == "GET"):
                        if(point.get == True):
                            code = 200
                            payload = point.returnGet(self.arguments)
                            break

                    #THE INSERT ENDPOINT
                    elif(self.method == "POST"):
                        if(point.post == True):
                            job = point.returnPost(self.body)
                            if(job[0] == True):
                                code = 201
                                payload = job[1] #table/id
                                break
                            elif(job[0] == None): #json parser error
                                code = 401
                                payload = "Error while parsing the JSON"
                                break
                            elif(job[0] == False):
                                code = 409 #conflict
                                payload = job[1]
                                break

                    #THE DELETE ENDPOINT
                    elif(self.method == "DELETE"):
                        payload = ""
                        if(self.arguments == ""):
                            code = 405
                            break
                        elif(point.delete == True):
                            if(point.returnDelete(self.arguments)):
                                code = 200
                                break
                            else:
                                code = 304
                                break

                    #THE UPDATE ENDPOINT
                    elif(self.method == "PATCH"):
                        if(point.patch == True):
                            if(self.arguments == ""):
                                code = 401
                                payload = ""
                                break
                            if(self.body == ""):
                                code = 204
                                payload = "no body found"
                                break
                            job = point.returnPatch(self.arguments,self.body)
                            if(job[0] == True):
                                code = 201
                                payload = ""
                                break
                            elif(job[0] == False):
                                code = 404
                                payload = ""
                                break
                            elif(job[0] == None): #json parser error
                                code = 401
                                payload = "Error while parsing the JSON"
                                break
                #COLORS!!!
                if(self.method == "GET"):
                    meth = "{cor}{metodo}{reset}".format(cor=cGREEN,metodo=self.method,reset=cRESET_ALL)
                elif(self.method == "POST"):
                    meth = "{cor}{metodo}{reset}".format(cor=cBLUE,metodo=self.method,reset=cRESET_ALL)
                elif(self.method == "DELETE"):
                    meth = "{cor}{metodo}{reset}".format(cor=cRED,metodo=self.method,reset=cRESET_ALL)
                elif(self.method == "PATCH"):
                    meth = "{cor}{metodo}{reset}".format(cor=cYELLOW,metodo=self.method,reset=cRESET_ALL)

                if((code >= 200) and (code < 300)):
                    cCode = cGREEN+str(code)+cRESET_ALL
                elif((code >= 300) and (code < 400)):
                    cCode = cBLUE+str(code)+cRESET_ALL
                elif((code >= 400 ) and (code < 500)):
                    cCode = cYELLOW+str(code)+cRESET_ALL
                else:
                    cCode = cRED+str(code)+cRESET_ALL

                #payload = payload.encode('utf-8')
                print("{0} requested {1} /{2}/{3} - {4}".format(self.addr[0],meth,self.url,self.arguments,cCode))
                self.response = self.makeResponse(code,payload)
                self.conn.sendall(self.response)
                self.conn.close()
            except:
                raise
                self.response = self.makeResponse(500,"error")
                print(cRED+("{0} requested {1} /{2}/{3} - {4}".format(self.addr[0],self.method,self.url,self.arguments,500))+cRESET_ALL)
                self.conn.sendall(self.response)
                self.conn.close()

    def getUrl(self,url):
        #get the path from the get URL
        url = url.split(b"\r\n")[0]
        arg = url.split(b" ")[1]
        arg = arg.lstrip(b"/")
        arg = arg.split("/")[0]

        if(arg == b""):
            arg = b"index.html"
            return arg.decode()
        return arg.decode()

    def getUrlArgs(self,url):
        url = url.split(b"\r\n")[0]
        arg = url.split(b" ")[1]
        arg = arg.lstrip(b"/")
        #arg is path/arguments
        ret = arg.split("/")
        return ret[1].decode()

    def getBody(self,request):
        #BIIIIIIRL!!!
        #multiline?
        data = request.split(b"\r\n")[-1]
        return data

    def getHeaders(self,request):
        data = request.split(b"\r\n")[1:]
        #must be between the [1] and the blank one
        #let's find the blank one
        try:
            blankOne = data.index(b"\r\n")
        except:
            blankOne = (len(data)-2)
        #create the dict
        heads = {}
        for h in data[0:blankOne]:
            try:
                aux = h.split(":")
                heads[aux[0]] = aux[1].strip()
            except:
                continue
        return heads


    def makeResponse(self,status,arg):
        import datetime
        date = datetime.datetime.now()
        template = "HTTP/1.1 {status}\r\nLocation: {location}\r\nDate:{date}\r\nServer: {server}\r\nContent-Type: application/json\r\nContent-Length: {size}\r\nConnection: close\r\n\r\n{body}".format(status=status,location=self.location,date=date,server="gateKeeper "+_ver_,size=len(arg),body=arg)
        return template

class Endpoint:
    '''
        representa um endpoint
        deve implementar GET/POST/DELETE/PATCH
    '''
    def __init__(self, table):
        self.url = table.name

        self.table = table

        self.get = table.read
        self.post = table.create
        self.delete = table.delete
        self.patch = table.update

        self.pk = self.findPk()

    def findPk(self):
        for f in self.table.fields:
            if(f.pk):
                return f

        return None

    def prepareDatabase(self):
        self.conn = sqlite3.connect(_db_)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

        return (self.conn, self.cur)

    def __str__(self):
        return "/{0} [GET:{1} POST:{2} DELETE:{3} PATCH:{4}]".format(self.url,self.get, self.post,self.delete,self.patch)

    def returnGet(self, filtro = None):
        fieldNames = []

        for tab in self.table.fields:
            fieldNames.append(tab.name)

        #criar o objeto retornavel
        maker = ReturnableMaker(fieldNames)

        conn, cur = self.prepareDatabase()
        query = "SELECT * FROM {tableName}".format(tableName=self.url)
        cur.execute(query)
        pre = cur.fetchall()
        conn.close()

        payload = []
        for p in pre:
            payload.append(maker.createReturnable(p))

        if(payload == []):
            return ""
        return json.dumps(payload,ensure_ascii=False).encode('utf-8')

    def returnPost(self, data):
        #parse the Json
        try:
            payload = json.loads(data,'utf-8')
            preCols = payload.keys()

            cols = u""
            for c in preCols:
                cols += c+u", "
            cols = cols.rstrip(u", ")

            vals = u""
            for k in preCols:
                #is this a string
                if(isinstance(payload[k],basestring)):
                        vals += u"'"+unicode(payload[k])+u"', "
                else:
                    vals += unicode(payload[k])+u", "
            vals = vals.rstrip(u", ")
        except:
            raise
            return (None,None)

        #SQL TIME!
        query = u"INSERT INTO {tableName}({cols}) VALUES({vals})".format(tableName = self.url, cols = cols, vals = vals)

        conn, cur = self.prepareDatabase()
        try:
            ret = cur.execute(query)
            conn.commit()
            conn.close()
            return (True,"/"+self.url+"/"+str(cur.lastrowid))
        except sqlite3.IntegrityError as e:
            conn.close()
            return (False,str(e))

    def returnDelete(self, idPk):
        conn, cur = self.prepareDatabase()
        query = "DELETE FROM {tableName} WHERE {PK} = {ID}".format(tableName = self.url, PK = self.pk.name, ID = idPk)
        ret = cur.execute(query)
        if(ret.rowcount>0):
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False

    def returnPatch(self, idPk, data):
        try:
            payload = json.loads(data)
            pq = u""
            for k in payload.keys():
                if(isinstance(payload[k],basestring)):
                    s = u"'{0}'".format(payload[k])
                else:
                    s = u"{0}".format(payload[k])
                pq+=u"{0}={1}, ".format(k,s)
            pq = pq.rstrip(u", ")
        except:
            raise
            return (None, None)

        query = u"UPDATE {tableName} SET {preQuery} WHERE {PK} = {ID}".format(tableName = self.url,preQuery = pq, PK = self.pk.name, ID = idPk)
        conn, cur = self.prepareDatabase()
        try:
            ret = cur.execute(query)
            if(ret.rowcount == 0):
                conn.close()
                return (False,"")
            conn.commit()
            conn.close()
            return (True,"")
        except sqlite3.IntegrityError as e:
            conn.close()
            return (True,str(e))

class Table:
    '''
       representa uma tabela, com seus campos e estrutura
    '''
    def __init__(self,name):
        self.name = name
        self.sql = ""
        self.fields = []

        self.create = False
        self.read   = True #you can always read a table
        self.update = False
        self.delete = False

    def setPermissions(self,number):
        '''
            duc
            000 = 0
            001 = 1
            010 = 2
            011 = 3
            100 = 4
            101 = 5
            110 = 6
            111 = 7
        '''

        #transform the number into the mask
        pre = "{0:b}".format(int(number)).zfill(3)

        if(pre[2] == "1"):
            self.create = True
        if(pre[1] == "1"):
            self.update = True
        if(pre[0] == "1"):
            self.delete = True


    def serialize(self,f):
        try:
            f.write("\n[{0}]-7\n".format(self.name))
            for c in self.fields:
                mask = "!"
                if(c.pk):
                    mask = "#"

                rel = ""
                if(c.relation is not None):
                    rel="({0})".format(c.relation)

                f.write("{1}{0}{2}-{3}\n".format(c.name,mask,rel,c.type))

            return True
        except:
            raise
            return False


    def __str__(self):
        return self.name

class Field:
    '''
        representa um campo da tabela
    '''
    def __init__(self):
        self.name = ""
        self.type = ""
        self.null = False
        self.pk = False
        self.relation = None
        self.AI = False

    def __str__(self):
        try:
            pre = self.relation.replace(";","(")+")"
        except:
            pre = "None"
        return "{0} ({1}) PK:{2} null:{3} REFERENCES {4}".format(self.name,\
                self.type,self.pk,self.null,pre)

class ReturnableMaker:
    '''

    '''
    def __init__(self,headerList):
        self.headers = []
        for header in headerList:
            self.headers.append(header)

    def createReturnable(self,*args):

        if(len(args[0]) == len(self.headers)):
            r = {}
            for ar in range(len(args[0])):
                r[self.headers[ar]] = args[0][ar]
            return r
        else:
            raise RuntimeWarning('Number of headers is different then the number of fields')

class Fetcher:
    '''
        encontra e processa os valores que estao no banco de dados
    '''
    def __init__(self):
        self.conn = sqlite3.connect(_db_)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        self.verbose = False


    def fetchTables(self):
        #Get all the tables from this database

        removes = ['sqlite_sequence']
        self.cur.execute("select name,sql from sqlite_master where type='table'")
        pre = self.cur.fetchall()

        tables = []
        for t in pre:
            if((t[0]) not in removes):
                #a new table is created
                aux = Table(t[0])
                aux.sql = t[1]
                if(self.verbose):
                    print("\nfound table: '{0}'.".format(cGREEN+str(aux)+cRESET_ALL))
                #fetch the fields from the new table
                aux.fields = self.fetchFields(aux)
                #append to the return
                tables.append(aux)

        return tables

    def fetchFields(self,table):
        #get all the fields from the 'table'
        fields = []
        #delete all behind '(' and after ')'
        ini = (table.sql.find("(")+1)

        #fields only
        formated = table.sql[ini:-1].strip()
        rows = formated.split("\n")
        for r in rows:
            #normalize all lines
            r = ' '.join(r.strip().split())
            r = r.replace("NOT NULL","NOT_NULL")
            r = r.replace("PRIMARY KEY","PK")
            r = r.replace("FOREIGN KEY","FK ")
            r = r.replace(",","")
            info = r.split(" ")
            f = Field()
            #get the field name
            #always the first, except when FOREIGN
            if(info[0] == "FK"):
                fi = info[1].replace("(`","")
                fi = fi.replace("`)","")

                found = None
                for fetchedField in fields:
                    if(fetchedField.name == fi):
                        found = fetchedField
                if(found is None):
                    #ohhh boy.
                    raise

                #get the table and field
                try:
                    tab,row = info[3].replace(")","").split("(")
                except:
                    if(self.verbose):
                        print("    {0}warning{1}: strange relationship found.".format(cRED,cRESET_ALL))
                        print("        [{0}]".format(r.replace("FK","FOREIGN KEY")))
                        print("        ignoring...")
                    #something went wrong.
                    #ignoring
                    continue

                found.relation = "{0};{1}".format(tab,row)
                if(self.verbose):
                    print("    {yellow}relationship{reset}: between the ({blue}{0}{reset}) and the table '{green}{1}{reset}({blue}{2}{reset})'".\
                        format(found.name,tab,row,blue=cBLUE,reset=cRESET_ALL,green=cGREEN,red=cRED,yellow=cYELLOW))
                continue
            elif(info[0][0] == "`"):
                f.name = info[0].replace("`","")

                #get the type of the field
                #always the seccond one
                if(info[1] == "BLOB"):
                    #ignore BLOB fields
                    if(self.verbose):
                        print()
                        print("    {red}Warning{reset}: field: {0} of type BLOB found.".format(f.name,red=cRED,reset=cRESET_ALL))
                        print("        ignoring....")
                    continue
                f.type = info[1]

                #is this field not null?
                if("NOT_NULL" in info):
                    f.null = False

                #is this field a primary key?
                if("PK" in info):
                    f.pk = True

                if("AUTOINCREMENT" in info):
                    f.AI = True
                if(self.verbose):
                    print("    field: {blue}{0}{reset} of type {colort}{1}{reset} found.".format(f.name,f.type,blue=cBLUE,reset=cRESET_ALL,colort = cBRIGHT))
                fields.append(f)
        return fields

def build(readOnly = False):
    '''
        build the config file
    '''
    if(readOnly == False):
        print("Building...")
        print("database: {bright}{0}{reset}".format(_db_,bright=cBRIGHT,reset=cRESET_ALL))
    f = Fetcher()
    f.verbose = not readOnly
    if(readOnly == False):
        print("Fetching tables...")
        print("\n")
    setOfTables = f.fetchTables()


    if(readOnly == False):
        print("\nCreating {bright}config file{reset}.".format(bright=cBRIGHT,reset=cRESET_ALL))
        f = open("build.gk","w")
        print("    Writing {red}headers{reset}\n".format(red=cRED,reset=cRESET_ALL))

        f.write(header)
        f.write("\n")

        #create the token
        import hashlib
        import random
        size = 24
        preToken = ""
        for c in xrange(size):
            aux = chr(random.randint(34,122))
            preToken+= aux
        token = hashlib.sha256()
        token.update(preToken)
        f.write("token: {}".format(token.hexdigest()))
        f.write("\n\n")
        for tab in setOfTables:
            print("    writing table: {green}{0}{reset}".format(tab,green=cGREEN,reset=cRESET_ALL))
            tab.serialize(f)


    if(readOnly == False):

        print("\n")
        print("{bright}Build complete.{reset}\n".format(bright=cBRIGHT,reset=cRESET_ALL))

def parse(configFile='build.gk'):
    global secToken
    print("reading: {bright}{0}{reset}".format(configFile,bright=cBRIGHT,reset=cRESET_ALL))
    try:
        f = open(configFile,'r').read().split("\n")
    except:
        print("{red}File not found.{reset}".format(red=cRED,reset=cRESET_ALL))
        sys.exit(1)

    #tables array
    allTables = []
    print("Parsing...")
    currentTable = None
    for line in f:
        if(line.startswith("token: ")):
            secToken = line.split(":")[1].strip()
        line = line.strip()
        try:
            #is it a blank line?
            line[1]
        except:
            continue
        if(line[0] == "["):
            #a new table
            if(currentTable is not None):
                allTables.append(currentTable)

            currentTable = Table(line[1:-3])
            mask = line[-1]
            currentTable.setPermissions(mask)
            print(".{green}{0}{reset}".format(currentTable,green=cGREEN,reset=cRESET_ALL))
        elif((line[0] == "!") or (line[0] == "#")):
            #create,read,update,delete field
            #prepare the field
            pre = line[1:].split("-")

            nf = Field()
            nf.name = pre[0]
            nf.type = pre[1]
            if(line[0] == "#"):
                nf.pk = True

            if(currentTable is not None):
                currentTable.fields.append(nf)
            else:
                #it's a field outside a table.
                print("{red}Parser Error{reset}: Field {0} outside a table".format(pre[0],red=cRED,reset=cRESET_ALL))
                sys.exit(1)
    #last table
    if(currentTable is not None):
        allTables.append(currentTable)

    #prepare the endpoints
    endPoints = []

    for tab in allTables:
        endPoints.append(Endpoint(tab))

    return endPoints

def run(endpoints,port = 8088):
    '''
    '''
    web = Server(port,endpoints)
    web.run()

if __name__ == "__main__":
    try:
        a = sys.argv[1]
    except:
        print("Options are '{0}build{1}', '{0}run{1}' or '{0}buildrun{1}'".format(cBRIGHT,cRESET_ALL))
    try:
        #let's parse the args
        if(sys.argv[1] == "build"):
            print(asciimsg)
            build()
        elif(sys.argv[1] == "run"):
            #print(asciimsg)
            e = parse()
            run(e)
        elif(sys.argv[1] == "buildrun"):
            print(asciimsg)
            build()
            e = parse()
            run(e)
        else:
            print("Options are '{0}build{1}', '{0}run{1}' or '{0}buildrun{1}'".format(cBRIGHT,cRESET_ALL))

    except:
        raise
