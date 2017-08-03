import sys
import sqlite3

try:
    import ujson as json
except:
    import json

_ver_ = "0.2"

asciimsg ='''
welcome to the _         _   __
              | |       | | / /
  __ _   __ _ | |_  ___ | |/ /   ___   ___  _ __    ___  _ __
 / _` | / _` || __|/ _ \|    \  / _ \ / _ \| '_ \  / _ \| '__|
| (_| || (_| || |_|  __/| |\  \|  __/|  __/| |_) ||  __/| |
 \__, | \__,_| \__|\___|\_| \_/ \___| \___|| .__/  \___||_|
  __/ |                                    | |
 |___/
'''

#path to the sqlite
_db_ = "test.sqlite"


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
        405 - method not allowed

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

        print("Server Running")

        while True:
            #the loop
            self.conn, self.addr = self.s.accept()
            self.data = self.conn.recv(1024)
            try:

                #pegar o caminho
                self.url = self.getUrl(self.data)
                try:
                    self.arguments = self.getArgs(self.data)
                except:
                    self.arguments = ""
                self.method = self.data.split(b" ")[0].decode()
                #find the endpoint
                code = 404
                payload = "Not Found"
                for point in self.endpoints:
                    if(point.url == self.url):
                        if(self.method == "GET"):
                            if(point.get == True):
                                code = 200
                                payload = point.returnGet(self.arguments)
                        elif(self.method == "POST"):
                            if(point.post == True):
                                code = 200
                                payload = ""
                        elif(self.method == "DELETE"):
                            payload = ""
                            if(self.arguments == ""):
                                code = 405
                                continue
                            elif(point.delete == True):
                                if(point.returnDelete(self.arguments)):
                                    code = 200
                                else:
                                    code = 304
                        elif(self.method == "PUT"):
                            if(point.put == True):
                                code = 200
                                payload = ""
                print("{0} requested {1} /{2}/{3} - {4}".format(self.addr[0],self.method,self.url,self.arguments,code))
                self.response = self.makeResponse(code,payload)
                self.conn.sendall(self.response)
                self.conn.close()
            except:
                raise
                self.response = self.makeResponse(500,"error")
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

    def getArgs(self,url):
        url = url.split(b"\r\n")[0]
        arg = url.split(b" ")[1]
        arg = arg.lstrip(b"/")
        #arg is path/arguments
        ret = arg.split("/")
        return ret[1].decode()

    def makeResponse(self,status,arg):
        import datetime
        date = datetime.datetime.now()
        template = "HTTP/1.1 {status}\r\nLocation: {location}\r\nDate:{date}\r\nServer: {server}\r\nContent-Type: application/json\r\nContent-Length: {size}\r\nConnection: close\r\n\r\n{body}".format(status="status",location=self.location,date=date,server="gateKeeper "+_ver_,size=len(arg),body=arg)
        return template.encode()

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
                if(c.PK):
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

class Endpoint:
    '''
        representa um endpoint
        deve implementar GET/POST/DELETE/PUT
    '''
    def __init__(self, table):
        self.url = table.name

        self.table = table

        self.get = table.read
        self.post = table.create
        self.delete = table.delete
        self.put = table.update

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
        return "/{0} [GET:{1} POST:{2} DELETE:{3} PUT:{4}]".format(self.url,self.get, self.post,self.delete,self.put)

    def returnGet(self, filtro = None):
        #TODO foreign keys
        #TODO filtros

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
        return json.dumps(payload)

    def returnPost(self, filtro = None):
        return

    def returnDelete(self, idPk) :
        conn, cur = self.prepareDatabase()
        query = "DELETE FROM {tableName} WHERE {PK} = {ID}".format(tableName = self.url, PK = self.pk.name, ID = idPk)
        ret = cur.execute(query)
        if(ret.rowcount>0):
            conn.commit()
            return True
        conn.close()
        return False

    def returnPut(self, filtro = None):
        return

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
                    print("\nfound table: '{0}'.".format(aux))
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
                    #TODO pegar automaticamente a PK da tabela
                    if(self.verbose):
                        print("    warning: strange relationship found.")
                        print("        [{0}]".format(r.replace("FK","FOREIGN KEY")))
                        print("        ignoring...")
                    #something went wrong.
                    #ignoring
                    continue

                found.relation = "{0};{1}".format(tab,row)
                if(self.verbose):
                    print("    relationship: between the ({0}) and the table '{1}({2})'".\
                        format(found.name,tab,row))
                continue
            elif(info[0][0] == "`"):
                f.name = info[0].replace("`","")

                #get the type of the field
                #always the seccond one
                if(info[1] == "BLOB"):
                    #ignore BLOB fields
                    if(self.verbose):
                        print("    field: {0} of type BLOB found.".format(f.name))
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
                    print("    field: {0} of type {1} found.".format(f.name,f.type))
                fields.append(f)
        #TODO testar isso com todos os tipos de fields possiveis
        return fields

def build(readOnly = False):
    '''
        build the config file
    '''
    if(readOnly == False):
        print("Building...")
        print("database: {0}".format(_db_))
    f = Fetcher()
    f.verbose = not readOnly
    if(readOnly == False):
        print("Fetching tables...")
        print("\n")
    setOfTables = f.fetchTables()


    if(readOnly == False):
        print("Creating config file.")
        f = open("build.gk","w")
        print("    Writing headers")

        f.write(header)
        f.write("\n\n")
        for tab in setOfTables:
            print("    writing table: {0}".format(tab))
            tab.serialize(f)

    if(readOnly == False):
        print("\n")
        print("Build complete.")

def parse(configFile='build.gk'):
    print("reading: {0}".format(configFile))
    try:
        f = open(configFile,'r').read().split("\n")
    except:
        print("File not found.")
        sys.exit(1)

    #tables array
    allTables = []
    print("Parsing...")
    currentTable = None
    for line in f:
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
            print(".{0}".format(currentTable))
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
                print("Parser Error: Field {0} outside a table".format(pre[0]))
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
    print(asciimsg)
    try:
        #let's parse the args
        if(sys.argv[1] == "build"):
            build()
        elif(sys.argv[1] == "run"):
            e = parse()
            build(True)

            #TODO implementar novas portas
            run(e)
        else:
            raise
    except:
        raise
        print("Options are 'build' or 'run'")
