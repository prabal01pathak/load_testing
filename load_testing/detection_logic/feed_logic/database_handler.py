import os
import json
import mysql.connector as sqlcon


class DatabaseHandler():
    def __init__(self, credential_path):
        """ Connecting the DataBase

        Args:
            credential_path ([json]): Credential of database connection Server
        """
        
        self.credentials = json.loads(open(credential_path,'r').read())
        self.my_db = sqlcon.connect(
            host = self.credentials['host'],
            user = self.credentials['user'],
            password = self.credentials['password'],
            database = self.credentials['database']
        )
        self.db_cursor = self.my_db.cursor()
    

    def disconnect(self):
        """ Disconnecting the DataBase
        """
        self.my_db.close()

    def create(self, table, **kwargs):
        """ Creating the Table for DataBase

        Args:
            table ([table]): Database Table
        """
        sql_command = f'CREATE TABLE {table}('
        for key, value in kwargs.items():
            sql_command += key + " " + value + ", "
        sql_command = sql_command[:-2] + ");"

        print(sql_command)

        self.db_cursor.execute(sql_command)
        self.my_db.commit()


    def read(self, table, *args):
        """ Reading the DataBase

        Args:
            credential_path ([json]): Database Table
        """
        if len(args) == 0:
            sql_command = f'SELECT * FROM {table};'
        else:
            sql_command = args[0]

        self.db_cursor.execute(sql_command)
        result = self.db_cursor.fetchall()

""" Inserting elements into Database Table """
    def insert(self, table, **kwargs):
        """ Inserting into the DataBase

        Args:
            credential_path ([json]): Database Table
        """
        sql_command = f'INSERT INTO {table}('
        for key, _ in kwargs.items():
            sql_command += key + ", "
        sql_command = sql_command[:-2] + ") VALUES ("
        for _, value in kwargs.items():
            sql_command += f'{value}, '
        sql_command = sql_command[:-2] + ");"

        print(sql_command)
        self.db_cursor.execute(sql_command)
        self.my_db.commit()

""" Updating Database """ 
    def update(self, table, **kwargs):
        pass

""" Deleting from Database """
    def delete(self, table, **kwargs):
        pass

if __name__ == '__main__':
    credential_path = os.path.join('credentials','database_credentials.json')
    obj = DatabaseHandler(credential_path)
    # obj.create('test',po_no='INT PRIMARY KEY',customer='VARCHAR(255)')
    # obj.insert('test',po_no="1",customer="'asd'")
    # obj.read('test')
    
"""
MySQL Commands:

*** Creating Tables ***

CREATE TABLE basic_information(
    sale_no VARCHAR(20) PRIMARY KEY NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    style VARCHAR(50) NOT NULL,
    size VARCHAR(10) NOT NULL,
    towel_type VARCHAR(50) NOT NULL,
    piece_required INT NOT NULL
);

CREATE TABLE process_information(
    doff_id VARCHAR(20) PRIMARY KEY NOT NULL,
    sale_no VARCHAR(20) NOT NULL,
    batch_id VARCHAR(20) NOT NULL,
    date VARCHAR(50) NOT NULL,
    time VARCHAR(50) NOT NULL,
    piece_counted INT NOT NULL,
    FOREIGN KEY (sale_no) REFERENCES basic_information(sale_no)
);

*** Insert Rows ***

INSERT INTO basic_information(sale_no, customer_name, style, size, towel_type, piece_required) VALUES ('QWE1234','IKEA','BIG ONE','46x137','Bath',1800);

INSERT INTO process_information(doff_id, sale_no, batch_id, date, time, piece_counted) VALUES ('ASD123','QWE1234','ZXC555','1/3/2021','10:00',999);
INSERT INTO process_information(doff_id, sale_no, batch_id, date, time, piece_counted) VALUES ('ASD124','QWE1234','ZXC555','1/3/2021','11:00',333);

*** Delete Rows ***

DELETE * FROM basic_information;
DELETE * FROM process_information;

*** Drop Tables ***

DROP TABLE basic_information;
DROP TABLE process_information;

*** Get Basic Details from Basic Information Table with respect to Sale Number ***

SELECT * FROM basic_information WHERE sale_no = <input_sale_number>;

*** Get Batch Information from Process Table with respect to Sale Number ***

SELECT * FROM process_information WHERE sale_no = <input_sale_number>;

*** Calculating Remaining Count, Total Complete with respect to Sale Number, will be done with Queries from Basic Information Table and Process Table ***

total_needed = SELECT piece_required FROM basic_information WHERE sale_no = <input_sale_number>;
total_complete = SELECT SUM(piece_counted) FROM process_information WHERE sale_no = <input_sale_number>;

remaining = total_needed - total_complete
    
"""