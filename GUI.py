import tkinter as tk
from tkinter import filedialog

def open_directory():
    directory=filedialog.askdirectory()
    if directory:
        dir_path.delete(0,tk.END)
        dir_path.insert(0,directory)

root = tk.Tk()  # create parent window
root.title('BLINDER - Blinding files for data analysis')
root.minsize(500,200)
root.geometry('500x200+550+300')

tk.Label(root,text='File directory').grid(row=0,column=0,padx=5, pady=5,sticky='E')
dir_path=tk.Entry(root,bd=1,relief=tk.FLAT)
dir_path.grid(row=0,column=1,padx=5, pady=5)
tk.Button(root, text="Browse", command=open_directory,relief=tk.RAISED).grid(row=0,column=2,padx=5, pady=5)

tk.Label(root,text='File suffix').grid(row=1,column=0,padx=5, pady=5,sticky='E')
file_suffix=tk.Entry(root,bd=1,relief=tk.FLAT)
file_suffix.grid(row=1,column=1,padx=5, pady=5)

tk.Button(root,text='Start Blinding Data!',relief=tk.RAISED).grid(row=2,column=0,padx=5, pady=5)
tk.Button(root,text='Cancel',command=root.quit,relief=tk.RAISED).grid(row=2,column=2,padx=5, pady=5)

root.mainloop()

# Add progreass bar
# Add calculations