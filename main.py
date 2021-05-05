from tkinter import ttk
from tkinter import *

import sqlite3

def run_query(query, parameters = ()):
    db_name = 'database.db'
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        result = cursor.execute(query, parameters)
        conn.commit()
    return result

def init_table():
    Master_table_name = 'Master'
    Detail_table_name = 'Detail'

    # check the master and detail table exists in DB
    query = f'CREATE TABLE IF NOT EXISTS {Master_table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, name text NOT NULL, type text NOT NULL, description text default NULL);'
    run_query(query)
    query = f'CREATE TABLE IF NOT EXISTS {Detail_table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, name text NOT NULL, type text NOT NULL, description text default NULL , master_id INTERGER NOT NULL);'
    run_query(query)


class Master:
    # connection dir property
    db_name = 'database.db'

    def __init__(self, frame_container):
        # Initializations 
        # self.wind = window
        # self.wind.title('Masters Application')

        # Creating a Frame Container 
        frame = LabelFrame(frame_container, text = 'Register new Master')
        frame.grid(row = 0, column = 0, columnspan = 10, pady = 10)

        # Name Input
        Label(frame, text = 'Name: ').grid(row = 1, column = 0)
        self.name = Entry(frame)
        self.name.focus()
        self.name.grid(row = 1, column = 1)

        # type Input
        Label(frame, text = 'Type: ').grid(row = 2, column = 0)
        self.type = Entry(frame)
        self.type.grid(row = 2, column = 1)

        # Description Input
        Label(frame, text = 'Description: ').grid(row = 3, column = 0)
        self.description = Entry(frame)
        self.description.grid(row = 3, column = 1)

        # Button Add Master 
        ttk.Button(frame, text = 'Save Master', command = self.add_Master).grid(row = 4, columnspan = 2, sticky = W + E)

        # Output Messages 
        self.message = Label(frame_container, text = '', fg = 'red')
        self.message.grid(row = 3, column = 0, columnspan = 2, sticky = W + E)

        # Table
        self.tree = ttk.Treeview(frame_container, height = 10, columns = (0,1,2,3), show='headings')
        self.tree.grid(row = 4, column = 0, columnspan = 4)
        self.tree.heading(0, text = 'id',            anchor = CENTER)
        self.tree.heading(1, text = 'Name',          anchor = CENTER)
        self.tree.heading(2, text = 'type',          anchor = CENTER)
        self.tree.heading(3, text = 'description',   anchor = CENTER)

        # Buttons
        ttk.Button(frame_container, text = 'DELETE', command = self.delete_Master).grid(row = 5, column = 1, sticky = W + E)
        ttk.Button(frame_container, text = 'EDIT', command = self.edit_Master).grid(row = 5, column = 2, sticky = W + E)

        # Filling the Rows
        self.get_Masters()

    # Function to Execute Database Querys
    def run_query(self, query, parameters = ()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result

    # Get Masters from Database
    def get_Masters(self):
        # cleaning Table 
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
        # getting data
        query = 'SELECT * FROM Master ORDER BY id ASC'
        db_rows = self.run_query(query)
        index = 0
        # filling data
        for row in db_rows:
            self.tree.insert('', index = index, values = (row[0], row[1], row[2], row[3]))
            index += 1

    # User Input Validation
    def validation(self):
        return len(self.name.get()) != 0 and len(self.type.get()) != 0

    def add_Master(self):
        if self.validation():
            query = 'SELECT count(*) FROM Master WHERE name = ?'
            parameters = (self.name.get().strip(),)
            name_existance = self.run_query(query, parameters).fetchone()
           
            if name_existance[0]:                                        # check same name existance
                self.message['fg'] = 'red'
                self.message['text'] = 'Master {} is already added. please insert another name !'.format(self.name.get())
            else:
                query = 'INSERT INTO Master (name, type, description)  VALUES(?, ?, ?)'
                parameters =  (self.name.get().strip(), self.type.get(), self.description.get())
                self.run_query(query, parameters)
                
                self.message['fg'] = 'green'
                self.message['text'] = 'Master {} added Successfully'.format(self.name.get())

                self.name.delete(0, END)
                self.type.delete(0, END)
                self.description.delete(0, END)
        else:
            self.message['fg'] = 'red'
            self.message['text'] = 'Name and type is Required'
        self.get_Masters()

    def delete_Master(self):
        self.message['text'] = ''
        
        curItem = self.tree.focus()
        master_oject = self.tree.item(curItem)                      # json  of selected master

        if master_oject['values']:
            self.get_Masters()
            self.message['text'] = ''
            
            master_id =  master_oject['values'][0]
            master_name =  master_oject['values'][1]
            query = 'DELETE FROM Master WHERE id = ?'
            self.run_query(query, (master_id, ))
            self.message['fg'] = 'green'
            self.message['text'] = 'Record {} deleted Successfully'.format(master_name)
            
            self.get_Masters()
        else: 
            self.message['fg'] = 'red'
            self.message['text'] = 'Please select a Record'
            return

    def edit_Master(self):
        self.message['text'] = ''

        curItem = self.tree.focus()
        master_oject = self.tree.item(curItem)                      # json  of selected master

        if master_oject['values']:
            
            self.message['text'] = ''
            
            master_id =  master_oject['values'][0]
            master_name =  master_oject['values'][1]
            master_type =  master_oject['values'][2]
            master_descrition =  master_oject['values'][3]

           
            self.edit_wind = Toplevel()
            self.edit_wind.title = 'Edit Master'

            # Name
            Label(self.edit_wind, text = 'Name:').grid(row = 0, column = 1)
            u_name = Entry(self.edit_wind, textvariable = StringVar(self.edit_wind, value = master_name))
            u_name.grid(row = 0, column = 2)
            
            # type 
            Label(self.edit_wind, text = 'Type:').grid(row = 1, column = 1)
            u_type = Entry(self.edit_wind, textvariable = StringVar(self.edit_wind, value = master_type))
            u_type.grid(row = 1, column = 2)
            
            # descrition
            Label(self.edit_wind, text = 'Desctiption :').grid(row = 2, column = 1)
            u_description = Entry(self.edit_wind, textvariable = StringVar(self.edit_wind, value = master_descrition))
            u_description.grid(row = 2, column = 2)

            Button(self.edit_wind, text = 'Update', command = lambda: self.edit_records(master_id, u_name.get().strip(), u_type.get().strip(), u_description.get().strip())).grid(row = 3, column = 2, sticky = W)
            self.edit_wind.mainloop()

           
        else: 
            self.message['fg'] = 'red'
            self.message['text'] = 'Please select a Record'
            return
        
    def edit_records(self, id, new_name, new_type, new_description):
        # must add chck module for name
        query = 'UPDATE Master SET name = ?, type = ? , description = ? WHERE id= ?'
        parameters = (new_name, new_type, new_description , id)
        self.run_query(query, parameters)
        self.edit_wind.destroy()
        self.message['fg'] = 'green'
        self.message['text'] = 'Record {} updated successfully'.format(new_name)
        self.get_Masters()

if __name__ == '__main__':
    init_table()
    window = Tk()
    window.title("Master-Detail CRUD Template")
    # application = Master(window)

    # create a notebook
    notebook = ttk.Notebook(window)
    notebook.pack(pady=10, expand=True)

    # create frames
    frame_master = ttk.Frame(notebook, width=800, height=600)
    frame_detail = ttk.Frame(notebook, width=800, height=600)

    frame_master.pack(fill='both', expand=True)
    frame_detail.pack(fill='both', expand=True)

    # add frames to notebook
    notebook.add(frame_master, text='Master')
    notebook.add(frame_detail, text='Detail')

    # add Master to frame_master
    Master(frame_master)


    window.mainloop()