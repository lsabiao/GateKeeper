import sys
import sqlite3
import pickle

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



class Table:
    '''
       representa uma tabela, com seus campos e estrutura
    '''
    def __init__(self,name):
        self.name = name
        self.sql = ""
        self.fields = []
    
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
                    print("    Strange relationship found.")
                    print("        {0}".format(r.replace("FK","FOREIGN KEY")))
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

            
                print("    field: {0} of type {1} found.".format(f.name,f.type))
                fields.append(f)
        #TODO testar isso com todos os tipos de fields possiveis
        return fields

def build():
    print("Building...")
    
    print("Fetching from {0}".format(_db_))
    f = Fetcher()
    
    print("Fetching tables...")
    setOfTables = f.fetchTables()
    
    print("\nflushing... as 'pre.gk'")
    with open('pre.gk','wb') as ser:
        pickle.dump(setOfTables,ser,2)

    print("Creating config file.")
    '''
    the config file:

    [table-name]

    field  - create,read,update,delete
    #field - read-only
    @field - create and read
    $field - create,read and update

    '''

    

    print("Build complete.") 


if __name__ == "__main__":
    print(asciimsg)
    try:
        #let's parse the args
        if(sys.argv[1] =="build"):
            build()
        elif(sys.argv[1] == "run"):
            pass
        else:
            raise
    except:
        #TODO apagar
        raise
        print("Options are 'build' or 'run'")

