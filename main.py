import tkinter as tk
from tkinter import ttk
from tkinter import *
import sqlite3
import tkinter.messagebox

g_master_table_name = 'Master'
g_detail_table_name = 'Detail'
g_password = 'password'

def run_query(query, parameters = ()):
    db_name = 'database.db'
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        result = cursor.execute(query, parameters)
        conn.commit()
    return result

def init_table():
    # check  master and detail tables are existing in DB
    query = f'CREATE TABLE IF NOT EXISTS {g_master_table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, name text NOT NULL, type text NOT NULL, description text default NULL);'
    run_query(query)
    query = f'CREATE TABLE IF NOT EXISTS {g_detail_table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, name text NOT NULL, type text NOT NULL, description text default NULL , master_id INTERGER NOT NULL, FOREIGN KEY(master_id) REFERENCES {g_master_table_name}(id));'
    run_query(query)

master_type_list = (   
                'MType1', 
                'MType2',
                'MType3'
            )

detail_type_list = (   
                'DType1', 
                'DType2',
                'DType3'
            )

class Master:
    def __init__(self, frame_container, frame_detail):

        # Creating a User role container
        user_role_frame = LabelFrame(frame_container, text = 'Select the role')
        user_role_frame.grid(row = 0, column = 0)
        
        # user is selectd as default
        self.var = IntVar()
        self.var.set(2)                             
        self.R1 = Radiobutton(user_role_frame, text="Admin", variable=self.var, value=1, command=self.select_admin)
        self.R1.pack( anchor = W )
        

        self.R2 = Radiobutton(user_role_frame, text="User", variable=self.var, value=2, command=self.select_user)
        self.R2.pack( anchor = W )

        # Creating a Frame Container 
        frame = LabelFrame(frame_container, text = 'Register new master')
        frame.grid(row = 0, column = 0, columnspan = 5, pady = 10)

        # Name Input
        Label(frame, text = 'Name: ').grid(row = 1, column = 0)
        self.name = Entry(frame)
        self.name.focus()
        self.name.grid(row = 1, column = 1)

        # type combobox
        Label(frame, text = 'Type: ').grid(row = 2, column = 0)
        n = tk.StringVar()
        self.type = ttk.Combobox(frame, width = 17, textvariable = n)
        
        # Adding combobox drop down list
        self.type['values'] = master_type_list
        self.type.grid(column = 1, row = 2)
        self.type.current()

        # Description Input
        Label(frame, text = 'Description: ').grid(row = 3, column = 0)
        self.description = Entry(frame)
        self.description.grid(row = 3, column = 1)

        # Button Add Master 
        self.add_btn = ttk.Button(frame, text = 'Save Master', command = lambda frame_detail = frame_detail :self.add_Master(frame_detail))
        self.add_btn.grid(row = 4, columnspan = 2, sticky = W + E)
        # self.add_btn['state'] = 'disabled'

        # Output Messages 
        self.message = Label(frame_container, text = '', fg = 'red')
        self.message.grid(row = 3, column = 1, columnspan = 2, sticky = W + E)

        # Table
        self.tree = ttk.Treeview(frame_container, height = 15, columns = (0,1,2), show='headings')
        self.tree.grid(row = 4, column = 0, columnspan = 3)
        self.tree.heading(0, text = 'NAME',          anchor = CENTER, command=lambda _col=0: self.treeview_sort_column(self.tree, _col, False))
        self.tree.heading(1, text = 'TYPE',          anchor = CENTER, command=lambda _col=1: self.treeview_sort_column(self.tree, _col, False))
        self.tree.heading(2, text = 'DESCRIPTION',   anchor = CENTER, command=lambda _col=2: self.treeview_sort_column(self.tree, _col, False))

        self.tree.column(0, anchor = 'center')
        self.tree.column(1, anchor = 'center')
        self.tree.column(2, anchor = 'center')

        # Buttons
        self.del_btn = ttk.Button(frame_container, text = 'DELETE', command = lambda frame_detail = frame_detail: self.delete_Master(frame_detail))
        self.del_btn.grid(row = 5, column = 1, sticky = W + E)

        self.edit_btn = ttk.Button(frame_container, text = 'EDIT', command = self.edit_Master)
        self.edit_btn.grid(row = 5, column = 2, sticky = W + E)

        # Filling the Rows
        self.get_Masters()

        # disable all buttons
        self.select_user()
    

    # select admin option
    def select_admin(self):
        self.pwd_prompt = Toplevel()
        self.pwd_prompt.title("Enter password")
        self.pwd_prompt.minsize(200, 100)

        Label(self.pwd_prompt, text='password').grid(row = 0, column = 2, padx=100)
        
        pwd_input = Entry(self.pwd_prompt, show="*")
        pwd_input.grid(row =  1, column = 2, pady = 2)
        

        confirm_btn = ttk.Button(self.pwd_prompt, text = 'OK', command = lambda : self.check_admin_password(pwd_input.get().strip()))
        confirm_btn.grid(row = 2, column = 2, pady = 1) 
        
        self.pwd_prompt.mainloop()
        
    # check admin password and allow the buttons
    def check_admin_password(self, pwd):
        if pwd == g_password:
            self.pwd_prompt.destroy()
            self.add_btn['state'] = 'enable'
            self.del_btn['state'] = 'enable'
            self.edit_btn['state'] = 'enable'
            self.message['text'] = ''
            
        else:
            self.message['fg'] = 'red'
            self.message['text'] = 'Password is not correct !'

    # select normal user option
    def select_user(self):
        self.add_btn['state'] = 'disabled'
        self.del_btn['state'] = 'disabled'
        self.edit_btn['state'] = 'disabled'

    # tree view sorting function
    def treeview_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda _col=col: self.treeview_sort_column(tv, _col, not reverse))

    # Get Masters from Database
    def get_Masters(self):
        # cleaning Table 
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
        # getting data
        query = f'SELECT * FROM {g_master_table_name} ORDER BY id ASC'
        db_rows = run_query(query)
        index = 0
        # filling data
        for row in db_rows:
            self.tree.insert('', index = index, values = (row[0], row[1], row[2], row[3]))
            index += 1

    # User Input Validation
    def validation(self):
        return len(self.name.get()) != 0 and len(self.type.get()) != 0

    def add_Master(self, frame_detail):
        if self.validation():
            query = f'SELECT count(*) FROM {g_master_table_name} WHERE name = ?'
            parameters = (self.name.get().strip(),)
            name_existance = run_query(query, parameters).fetchone()
           
            # check same name existance
            if name_existance[0]:                                        
                self.message['fg'] = 'red'
                self.message['text'] = 'Master {} is already added. please insert another name !'.format(self.name.get().strip())
            else:
                query = f'INSERT INTO {g_master_table_name} (name, type, description)  VALUES(?, ?, ?)'
                parameters =  (self.name.get().strip(), self.type.get().strip(), self.description.get().strip())
                run_query(query, parameters)
                
                self.message['fg'] = 'green'
                self.message['text'] = 'Master {} added Successfully'.format(self.name.get())

                self.name.delete(0, END)
                self.type.delete(0, END)
                self.description.delete(0, END)
                
                #refresh Detail tab 
                Detail(frame_detail)
                
        else:
            self.message['fg'] = 'red'
            self.message['text'] = 'Name and type are required'
        self.get_Masters()

    def delete_Master(self, frame_detail):
        self.message['text'] = ''
        
        curItem = self.tree.focus()
        master_oject = self.tree.item(curItem)                      

        if master_oject['values']:
            self.get_Masters()
            self.message['text'] = ''
            
            master_id =  master_oject['values'][0]
            master_name =  master_oject['values'][1]
            query = f'DELETE FROM {g_master_table_name} where id = ?'
            run_query(query, (master_id,))
            query = f'DELETE FROM {g_detail_table_name} where master_id = ?'
            run_query(query, (master_id,))
            self.message['fg'] = 'green'
            self.message['text'] = 'Record {} deleted successfully'.format(master_name)
            
            self.get_Masters()
            Detail(frame_detail)
        else: 
            self.message['fg'] = 'red'
            self.message['text'] = 'Please select a record'
            return

    def edit_Master(self):
        self.message['text'] = ''
        
        # get selected Master object
        curItem = self.tree.focus()
        master_oject = self.tree.item(curItem)                      

        if master_oject['values']:
            
            self.message['text'] = ''
            
            master_id =  master_oject['values'][0]
            master_name =  master_oject['values'][1]
            master_type =  master_oject['values'][2]
            master_descrition =  master_oject['values'][3]

           
            self.edit_wind = Toplevel()
            self.edit_wind.title('Edit Master')
            self.edit_wind.minsize(250,120)
            
            # Name
            Label(self.edit_wind, text = 'Name:').grid(row = 0, column = 1)
            u_name = Entry(self.edit_wind, textvariable = StringVar(self.edit_wind, value = master_name))
            u_name.grid(row = 0, column = 2)
            
            # type 
            Label(self.edit_wind, text = 'Type:').grid(row = 1, column = 1)
            n = tk.StringVar()
            u_type = ttk.Combobox(self.edit_wind, width = 17, textvariable = n)
            
            # Adding combobox drop down list
            u_type['values'] = master_type_list
            u_type.grid(column = 2, row = 1)
            try :
                type_of_index = master_type_list.index(master_type)
                u_type.current(type_of_index)                  
            except:
                u_type.current()
            
            # descrition
            Label(self.edit_wind, text = 'Desctiption :').grid(row = 2, column = 1)
            u_description = Entry(self.edit_wind, textvariable = StringVar(self.edit_wind, value = master_descrition))
            u_description.grid(row = 2, column = 2)

            Button(self.edit_wind, text = 'Update', command = lambda: self.edit_records(master_id, u_name.get().strip(), u_type.get().strip(), u_description.get().strip())).grid(row = 3, column = 2, sticky = W)
            self.edit_wind.mainloop()

           
        else: 
            self.message['fg'] = 'red'
            self.message['text'] = 'Please select a record'
            return
        
    def edit_records(self, id, new_name, new_type, new_description):
        # must add chck module for name
        query = f'SELECT count(*) FROM {g_master_table_name} WHERE name = ? and id != ?'
        parameters = (new_name,id)
        name_existance = run_query(query, parameters).fetchone()
        
        # check same name existance
        if name_existance[0]:                                        
            self.message['fg'] = 'red'
            self.message['text'] = 'Master {} is already added. please insert another name !'.format(new_name)
        else:
            query = f'UPDATE {g_master_table_name} SET name = ?, type = ? , description = ? WHERE id= ?'
            parameters = (new_name, new_type, new_description , id)
            run_query(query, parameters)
            self.edit_wind.destroy()
            self.message['fg'] = 'green'
            self.message['text'] = 'Record {} updated successfully'.format(new_name)
            self.get_Masters()

class Detail:
    def __init__(self, frame_container):

        # Creating a User role container
        user_role_frame = LabelFrame(frame_container, text = 'Select the role')
        user_role_frame.grid(row = 0, column = 0)
        
        # admin is selectd as default
        self.var = IntVar()
        self.var.set(2)                                      
        self.R1 = Radiobutton(user_role_frame, text="Admin", variable=self.var, value=1, command=self.select_admin)
        self.R1.pack( anchor = W )
        

        self.R2 = Radiobutton(user_role_frame, text="User", variable=self.var, value=2, command=self.select_user)
        self.R2.pack( anchor = W )

        # Creating a Frame Container 
        frame = LabelFrame(frame_container, text = 'Register new detail')
        frame.grid(row = 0, column = 0, columnspan = 5, pady = 10)

        # Name Input
        Label(frame, text = 'Name: ').grid(row = 1, column = 0)
        self.name = Entry(frame)
        self.name.focus()
        self.name.grid(row = 1, column = 1)

        # type combobox
        Label(frame, text = 'Type: ').grid(row = 2, column = 0)
        n = tk.StringVar()
        self.type = ttk.Combobox(frame, width = 17, textvariable = n)
        
        # Adding combobox drop down list
        self.type['values'] = detail_type_list
        self.type.grid(column = 1, row = 2)
        self.type.current()

        # Description Input
        Label(frame, text = 'Description: ').grid(row = 3, column = 0)
        self.description = Entry(frame)
        self.description.grid(row = 3, column = 1)

        # Master name Input
        Label(frame, text = 'Master name: ').grid(row = 4, column = 0)
        n = tk.StringVar()
        self.m_name = ttk.Combobox(frame, width = 17, textvariable = n)
        
        master_name_list = self.get_master_name_list()

        self.m_name['values'] = master_name_list
        self.m_name.grid(row = 4, column = 1)
        self.m_name.current()

        # Button Add Detail 
        self.add_btn = ttk.Button(frame, text = 'Save Detail', command = self.add_Detail)
        self.add_btn.grid(row = 5, columnspan = 2, sticky = W + E)
        # self.add_btn['state'] = 'disabled'

        # Output Messages 
        self.message = Label(frame_container, text = '', fg = 'red')
        self.message.grid(row = 3, column = 1, columnspan = 2, sticky = W + E)

        # Table
        self.tree = ttk.Treeview(frame_container, height = 15, columns = (0,1,2,3), show='headings')
        self.tree.grid(row = 4, column = 0, columnspan = 4)
        self.tree.heading(0, text = 'NAME',          anchor = CENTER, command=lambda _col=0: self.treeview_sort_column(self.tree, _col, False))
        self.tree.heading(1, text = 'TYPE',          anchor = CENTER, command=lambda _col=1: self.treeview_sort_column(self.tree, _col, False))
        self.tree.heading(2, text = 'DESCRIPTION',   anchor = CENTER, command=lambda _col=2: self.treeview_sort_column(self.tree, _col, False))
        self.tree.heading(3, text = 'Master_ID',     anchor = CENTER, command=lambda _col=3: self.treeview_sort_column(self.tree, _col, False))

        self.tree.column(0, anchor = 'center')
        self.tree.column(1, anchor = 'center')
        self.tree.column(2, anchor = 'center')
        self.tree.column(3, anchor = 'center')

        # Buttons
        self.del_btn = ttk.Button(frame_container, text = 'DELETE', command = self.delete_Detail)
        self.del_btn.grid(row = 5, column = 1, sticky = W + E)

        self.edit_btn = ttk.Button(frame_container, text = 'EDIT', command = self.edit_Detail)
        self.edit_btn.grid(row = 5, column = 2, sticky = W + E)

        # Filling the Rows
        self.get_Details()
        self.select_user()
    
    def get_master_name_list(self):
        name_list = ()
        query = f'SELECT name FROM {g_master_table_name}'
        db_rows = run_query(query)
        for row in db_rows:
            name_list += (row[0],)
        return name_list

       # select admin option
    
    # select admin option
    def select_admin(self):
        self.pwd_prompt = Toplevel()
        self.pwd_prompt.title("Enter password")
        self.pwd_prompt.minsize(200, 100)

        Label(self.pwd_prompt, text='password').grid(row = 0, column = 2, padx=100)
        
        pwd_input = Entry(self.pwd_prompt, show="*")
        pwd_input.grid(row =  1, column = 2, pady = 2)
        

        confirm_btn = ttk.Button(self.pwd_prompt, text = 'OK', command = lambda : self.check_admin_password(pwd_input.get().strip()))
        confirm_btn.grid(row = 2, column = 2, pady = 1) 
        
        self.pwd_prompt.mainloop()
        
    # check admin password and allow the buttons
    def check_admin_password(self, pwd):
        if pwd == g_password:
            self.pwd_prompt.destroy()
            self.add_btn['state'] = 'enable'
            self.del_btn['state'] = 'enable'
            self.edit_btn['state'] = 'enable'
            self.message['text'] = ''
            
        else:
            self.message['fg'] = 'red'
            self.message['text'] = 'Password is not correct !'


    # select normal user option
    def select_user(self):
        self.add_btn['state'] = 'disabled'
        self.del_btn['state'] = 'disabled'
        self.edit_btn['state'] = 'disabled'

    # tree view sorting function
    def treeview_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda _col=col: self.treeview_sort_column(tv, _col, not reverse))

    # Get Details from Database
    def get_Details(self):
        # cleaning Table 
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
        # getting data
        query = f'SELECT id, name, type, description, master_id FROM {g_detail_table_name} ORDER BY id ASC'
        db_rows = run_query(query)
        index = 0
        # filling data
        for row in db_rows:
            self.tree.insert('', index = index, values = (row[0], row[1], row[2], row[3], row[4]))
            index += 1

    # User Input Validation
    def validation(self):
        return len(self.name.get()) != 0 and len(self.type.get()) != 0 and len(self.m_name.get()) != 0

    def add_Detail(self):
        if self.validation():
            query = f'SELECT count(*) FROM {g_detail_table_name} WHERE name = ?'
            parameters = (self.name.get().strip(),)
            name_existance = run_query(query, parameters).fetchone()
           
            # check same name existance
            if name_existance[0]:                                        
                self.message['fg'] = 'red'
                self.message['text'] = 'Detail {} is already added. please insert another name !'.format(self.name.get().strip())
            else:
                query = f'INSERT INTO {g_detail_table_name} (name, type, description, master_id)  VALUES(?, ?, ?, (SELECT id from {g_master_table_name} where name = ?))'
                parameters =  (self.name.get().strip(), self.type.get().strip(), self.description.get().strip(), self.m_name.get().strip())
                run_query(query, parameters)
                
                self.message['fg'] = 'green'
                self.message['text'] = 'Detail {} added successfully'.format(self.name.get())

                self.name.delete(0, END)
                self.type.delete(0, END)
                self.description.delete(0, END)
        else:
            self.message['fg'] = 'red'
            self.message['text'] = 'Name, type and parent master are required'
        self.get_Details()

    def delete_Detail(self):
        self.message['text'] = ''
        
        curItem = self.tree.focus()
        Detail_oject = self.tree.item(curItem)                     

        if Detail_oject['values']:
            self.get_Details()
            self.message['text'] = ''
            
            Detail_id =  Detail_oject['values'][0]
            Detail_name =  Detail_oject['values'][1]
            query = f'DELETE FROM {g_detail_table_name} WHERE id = ?'
            run_query(query, (Detail_id, ))
            self.message['fg'] = 'green'
            self.message['text'] = 'Record {} deleted successfully'.format(Detail_name)
            
            self.get_Details()
        else: 
            self.message['fg'] = 'red'
            self.message['text'] = 'Please select a record'
            return

    def edit_Detail(self):
        self.message['text'] = ''

        # get selected detail object
        curItem = self.tree.focus()
        Detail_oject = self.tree.item(curItem)                      

        if Detail_oject['values']:
            
            self.message['text'] = ''
            
            Detail_id =  Detail_oject['values'][0]
            Detail_name =  Detail_oject['values'][1]
            Detail_type =  Detail_oject['values'][2]
            Detail_descrition =  Detail_oject['values'][3]
            Detail_master_id =  Detail_oject['values'][4]
            
            query = f"select name from {g_master_table_name} where id = ?"
            result_row = run_query(query, (Detail_master_id,))
            result = result_row.fetchone()
            Detail_master_name = result[0]
           
            self.edit_wind = Toplevel()
            self.edit_wind.title('Edit Detail')
            self.edit_wind.minsize(250,120)

            # Name
            Label(self.edit_wind, text = 'Name:').grid(row = 0, column = 1)
            u_name = Entry(self.edit_wind, textvariable = StringVar(self.edit_wind, value = Detail_name))
            u_name.grid(row = 0, column = 2)
            
            # type 
            Label(self.edit_wind, text = 'Type:').grid(row = 1, column = 1)
            n = tk.StringVar()
            n.set(Detail_type)
            u_type = ttk.Combobox(self.edit_wind, width = 17, textvariable = n)
            
            # Adding combobox drop down list
            u_type['values'] = detail_type_list
            u_type.grid(column = 2, row = 1)
            
            Label(self.edit_wind, text = 'Desctiption :').grid(row = 2, column = 1)
            u_description = Entry(self.edit_wind, textvariable = StringVar(self.edit_wind, value = Detail_descrition))
            u_description.grid(row = 2, column = 2)

             # Master name Input
            Label(self.edit_wind, text = 'Master name: ').grid(row = 3, column = 1)
            master_string = tk.StringVar()
            master_string.set(Detail_master_name)
            u_mname = ttk.Combobox(self.edit_wind, width = 17, textvariable = master_string)
            
            master_name_list = self.get_master_name_list()

            u_mname['values'] = master_name_list
            u_mname.grid(row = 3, column = 2)
            u_mname.current()

            Button(self.edit_wind, text = 'Update', command = lambda: self.edit_records(Detail_id, u_name.get().strip(), u_type.get().strip(), u_description.get().strip(), u_mname.get().strip())).grid(row = 4, column = 2, sticky = W)
            self.edit_wind.mainloop()

           
        else: 
            self.message['fg'] = 'red'
            self.message['text'] = 'Please select a record'
            return
        
    def edit_records(self, id, new_name, new_type, new_description, new_master_name_string):
        # must add chck module for name
        query = f'SELECT count(*) FROM {g_detail_table_name} WHERE name = ? and id != ?'
        parameters = (new_name,id)
        name_existance = run_query(query, parameters).fetchone()
        
        # check same name existance
        if name_existance[0]:                                        
            self.message['fg'] = 'red'
            self.message['text'] = 'Detail {} is already added. please insert another name !'.format(new_name)
        else:
            query = f'UPDATE {g_detail_table_name} SET name = ?, type = ? , description = ? , master_id= (select id from {g_master_table_name} where name = ? )WHERE id= ?'
            parameters = (new_name, new_type, new_description , new_master_name_string, id)
            run_query(query, parameters)
            self.edit_wind.destroy()
            self.message['fg'] = 'green'
            self.message['text'] = 'Record {} updated successfully'.format(new_name)
            self.get_Details()

# call back function to open help window as top level
def helloCallBack():
        help_window = Toplevel()
        help_window.title("Help window")
        help_window.minsize(500, 200)
        Label(help_window, text = 'This is help window').grid(row = 0, column = 1)


if __name__ == '__main__':
    init_table()
    window = Tk()
    window.title("Master-Detail CRUD Template")

    help_btn = ttk.Button(window, text ="Help", command = helloCallBack)
    help_btn.pack()
    
    # create a notebook
    notebook = ttk.Notebook(window)
    notebook.pack(pady=10, expand=True)

    # create frames
    frame_master = ttk.Frame(notebook, width=800, height=500)
    frame_detail = ttk.Frame(notebook, width=800, height=500)

    frame_master.pack(fill='both', expand=True)
    frame_detail.pack(fill='both', expand=True)

    # add frames to notebook
    notebook.add(frame_master, text='Master')
    notebook.add(frame_detail, text='Detail')

    # add Master to frame_master
    Master(frame_master, frame_detail)
    Detail(frame_detail)


    window.mainloop()



