import sys
import sqlite3


#path to the sqlite
_db_ = "test.sqlite"



class Table:
    '''
       representa uma tabela, com seus campos e estrutura
    '''
    def __init__(self,name):
        self.name = name
        self.fields = []
    
    def __str__(self):
        return self.name    

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
        self.cur.execute("select name from sqlite_master where type='table'")
        pre = self.cur.fetchall()

        tables = []
        for t in pre:
            if((t[0]) not in removes):
                #a new table is created
                aux = Table(t[0])
                print("\nfound '{0}' table.".format(aux))
                #fetch the fields from the new table
                aux.fields = self.fetchFields(aux)
                #append to the return
                tables.append(aux)
                
        return tables        

    def fetchFields(self,table):
        #get all the fields from the 'table'

        #TODO necessario saber se ha relacao com outra tabela.
        self.cur.execute("select * from {table}".format(table=table))
        fields = self.cur.fetchone().keys()
        print("    fields: {0}".format(fields))
        return fields

def build():
    print("Building...")
    print("Fetching from {0}".format(_db_))
    f = Fetcher()
    print("Fetching tables...")
    f.fetchTables()



if __name__ == "__main__":
    try:
        #let's parse the args
        if(sys.argv[1] == "build"):
            build()
        elif(sys.argv[1] == "run"):
            pass
        else:
            raise
    except:
        print("Options are 'build' or 'run'")

