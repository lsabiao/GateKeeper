import sys
import sqlite3

asciimsg =r'''
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



class Table:
    '''
       representa uma tabela, com seus campos e estrutura
    '''
    def __init__(self,name):
        self.name = name
        self.sql = ""
        self.fields = []
        
        self.create = False
        self.read   = False
        self.update = False
        self.delete = False
   
    def serialize(self,f):
        try:
            f.write("[{0}]\n".format(self.name))
            for c in self.fields:
                mask = "!"
                if(c.AI):
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


class Endpoint:
    ''' 
        representa um endpoint
        deve implementar GET/POST/DELETE/PUT
    '''
    pass

class Fetcher:
    '''
        encontra e processa os valores que estao no banco de dados        
    '''
    def __init__(self):
        self.conn = sqlite3.connect(_db_)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
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
                    print("    warning: strange relationship found.")
                    print("        [{0}]".format(r.replace("FK","FOREIGN KEY")))
                    print("        ignoring...")
                    #something went wrong.
                    #ignoring
                    continue
 
                found.relation = "{0};{1}".format(tab,row)
                print("    relationship: between the ({0}) and the table '{1}({2})'".\
                        format(found.name,tab,row))
                continue
            elif(info[0][0] == "`"):
                f.name = info[0].replace("`","")
            
                #get the type of the field
                #always the seccond one
                if(info[1] == "BLOB"):
                    #ignore BLOB fields
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
            
                print("    field: {0} of type {1} found.".format(f.name,f.type))
                fields.append(f)
        #TODO testar isso com todos os tipos de fields possiveis
        return fields

def build():
    '''
        build the config file
    '''
    print("Building...")
    
    print("database: {0}".format(_db_))
    f = Fetcher()
    
    print("Fetching tables...")
    setOfTables = f.fetchTables()
    print("\n") 
    print("Creating config file.")
    
    f = open("build.gk","w")
    print("    Writing headers")
    f.write(header)
    f.write("\n\n")
    for tab in setOfTables:
        print("    writing table: {0}".format(tab))
        tab.serialize(f)

    
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
        try:
            #is it a blank line?
            line[1]
        except:
            continue
        if(line[0] == "["):
            #a new table
            if(currentTable is not None):
                allTables.append(currentTable)

            currentTable = Table(line[1:-1])

            #TODO Table permits
            currentTable.create = True
            currentTable.read = True
            currentTable.update = True
            currentTable.Delete = True

        elif((line[0] == "!") or (line[0] == "#")):
            #create,read,update,delete field
            #prepare the field
            pre = line[1:].split("-")            
            
            nf = Field()
            nf.name = pre[0]
            nf.type = pre[1]
            if(line[1] == "#"):
                nf.AI = True

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
    allEndPoints = []

if __name__ == "__main__":
    print(asciimsg)
    try:
        #let's parse the args
        if(sys.argv[1] == "build"):
            build()
        elif(sys.argv[1] == "run"):
            parse()
        else:
            raise
    except:
        raise
        print("Options are 'build' or 'run'")

