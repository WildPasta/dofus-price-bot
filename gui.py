# Standard library imports
import json
import sys

# Third party imports
from tkinter import *
from tkinter import messagebox
from tkinter import ttk

def load_recipes(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        data = json.load(f)
    names = [recipe['name'] for recipe in data]
    names.sort()
    return names

def create_window():
    item_requested = list()
    root = Tk()
    root.title("Dofus Cooker")
    root.geometry("600x600")
    root.config(bg='#DFE7F2')
    style = ttk.Style(root)
    style.theme_use('clam')

    def on_ok_button_click():
        if added_items.size() == 0:
            messagebox.showinfo("No item selected", "Please select at least one item")
        else:
            root.destroy()
    
    def on_add_button_click():
        item_requested.append(my_entry.get())
        added_items.delete(0, END)
        for item in item_requested:
            added_items.insert(END, item)
        return
    
    def on_delete_button_click():
        selected_item = added_items.curselection()
        if selected_item:
            added_items.delete(selected_item[0])
            item_requested.pop(selected_item[0])
        return

    # Update the listbox
    def update(data):
        # Clear the listbox
        global_item_list.delete(0, END)

        # Add items to our listbox
        for item in data:
            global_item_list.insert(END, item)

    # Update entry box with listbox clicked
    def fillout(event):
        # Delete entrybox content
        my_entry.delete(0, END)

        # Add clicked list item to entry box
        my_entry.insert(0, global_item_list.get(ACTIVE))

    # create function to check entry vs listbox
    def check(event):
        # grab what is typed
        typed = my_entry.get()
        if typed == '':
            data = items
        else:
            data = list()
            for item in items:
                if typed.lower() in item.lower():
                    data.append(item)
        update(data)

    my_label = Label(root, text="Start typing...", font=("Helvetica", 14), fg="black")
    my_label.pack(pady=20)

    my_entry = ttk.Entry(root, font=("Helvetica", 20))
    my_entry.pack()

    global_item_list = Listbox(root, width=50)
    global_item_list.pack(pady=40)

    add_button = ttk.Button(root, text="ADD", command=on_add_button_click)
    add_button.pack(padx=20)

    ok_button = ttk.Button(root, text="OK", command=on_ok_button_click)
    ok_button.pack(pady=20)

    delete_button = ttk.Button(root, text="DELETE", command=on_delete_button_click)
    delete_button.pack(padx=20, side=BOTTOM)

    added_items = Listbox(root, height=5, width=50)
    added_items.pack(pady=10, side=BOTTOM)


    items = load_recipes("equipment_recipes.json")

    # Add the items to our list
    update(items)

    # Bind the listbox on click
    global_item_list.bind("<<ListboxSelect>>", fillout)

    # Create a binding on the entry box
    my_entry.bind("<KeyRelease>", check)

    root.mainloop()
    
    return item_requested

def ending_message():
    messagebox.showinfo("Finished", "The search has finished!")

# from tkinter.ttk import Progressbar
# from time import sleep
# def create_progress_bar():
#     root = Tk()
#     root.title("Search progress")
#     root.attributes('-topmost', True)
#     root.attributes('-alpha', 0.8)

#     screen_width = root.winfo_screenwidth()
#     screen_height = root.winfo_screenheight()
#     root.geometry(f"300x75+{screen_width-350}+{screen_height-200}")

#     # Create a DoubleVar variable to store the progress value
#     progress_value = DoubleVar()

#     progress_bar = Progressbar(root, orient="horizontal", length=180, mode="determinate", variable=progress_value, maximum=100)
#     progress_bar.pack(pady=10)

#     progress_label = Label(root, text='')
#     progress_label.pack()

#     # Position the window in the bottom right corner
#     def loop_function():
#         for i in range(1, 101):
#             sleep(1)
#             progress_value.set(i)
#             progress_str = str(int(progress_value.get())) + '%'
#             progress_label.config(text=progress_str)

#             progress_bar.update()
#             progress_label.update()
            
#     # Call the loop function
#     loop_function()
#     root.mainloop()

if __name__ == "__main__":
    sys.exit(create_window())