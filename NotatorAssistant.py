import string
import configparser
import time
import threading
import xml.etree.ElementTree as ET
from xml.dom import minidom
import tkinter as tk
from tkinter import ttk, simpledialog
import keyboard
import mouse

class SnippetDialog(simpledialog.Dialog):
    def __init__(self, master, title, initial_values=None):
        """
        Initialize the SnippetDialog class.

        Parameters:
        - master: The parent window or frame of the dialog.
        - title: The title of the dialog window.
        - initial_values: (optional) Initial values for the dialog fields.

        Returns:
        None
        """
        self.initial_values = initial_values
        super().__init__(master, title)
   
    def body(self, master):
        """
        Create the body of the dialog window.

        Parameters:
        - master: The parent window or frame of the dialog.

        Returns:
        The widget that should have initial focus (in this case, keyword_entry).
        """
        # Create labels and entry widgets for entering keyword and text
        tk.Label(master, text="Enter Keyword:").grid(row=0, column=0) 
        tk.Label(master, text="Enter Text:").grid(row=1, column=0) 

        self.keyword_entry = tk.Entry(master) # Entry widget for entering keyword
        self.keyword_entry.grid(row=0, column=1, sticky="w") # Position keyword entry widget
       
        self.text_entry = tk.Text(master, height=10, width=96) # Text widget for entering text
        self.text_entry.grid(row=1, column=1) # Position text entry widget
       
        # Bind the Enter key to insert a newline instead of closing the dialog
        self.text_entry.bind("<Return>", self.handle_return)

        if self.initial_values:
            # If initial values are provided, set them in the entry widgets
            self.keyword_entry.insert(0, self.initial_values.get('keyword', ''))
            self.text_entry.insert(tk.END, self.initial_values.get('text', ''))
       
        return self.keyword_entry

    def handle_return(self, event):
        """
        Handle the Return key press event.

        Parameters:
        - event: The event object representing the key press.

        Returns:
        "break" to prevent the default behavior of closing the dialog.
        """
        # Insert a newline character when the Enter key is pressed
        self.text_entry.insert(tk.INSERT, "\n")
       
        # Prevent the default behavior of the Enter key (closing the dialog)
        return "break"

    def apply(self):
        """
        Apply the values entered in the dialog.

        Parameters:
        None

        Returns:
        None
        """
        # Get the entered keyword and text
        keyword = self.keyword_entry.get()
        text = self.text_entry.get("1.0", tk.END).strip()
        self.result = (keyword, text) # Set the result attribute with the entered values
       
class SettingsDialog(simpledialog.Dialog):
    def __init__(self, master, title, initial_values=None):
        """
        Initialize the SettingsDialog class.

        Parameters:
        - master: The parent window or frame of the dialog.
        - title: The title of the dialog window.
        - initial_values: (optional) Initial values for the dialog fields.

        Returns:
        None
        """
        self.initial_values = initial_values
        super().__init__(master, title)

    def body(self, master):
        """
        Create the body of the dialog window.

        Parameters:
        - master: The parent window or frame of the dialog.

        Returns:
        The widget that should have initial focus (in this case, timeout_value_entry).
        """
        # Create labels and entry widgets for configuring settings
        tk.Label(master, text="Keyword is case sensitive:", anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(master, text="Reset on backspace:", anchor="w").grid(row=1, column=0, sticky="w")
        tk.Label(master, text="Reset on click:", anchor="w").grid(row=2, column=0, sticky="w")
        tk.Label(master, text="Reset on tab:", anchor="w").grid(row=3, column=0, sticky="w")
        tk.Label(master, text="Timeout value (seconds):", anchor="w").grid(row=4, column=0, sticky="w")

        # Create BooleanVar and StringVar variables to hold settings values
        self.keyword_case_sensitive_var = tk.BooleanVar()
        self.reset_on_backspace_var = tk.BooleanVar()
        self.reset_on_click_var = tk.BooleanVar()
        self.reset_on_tab_var = tk.BooleanVar()
        self.timeout_value_var = tk.StringVar()

        # Create Checkbuttons and Entry widget to configure settings
        self.keyword_case_sensitive_checkbox = tk.Checkbutton(master, variable=self.keyword_case_sensitive_var)
        self.keyword_case_sensitive_checkbox.grid(row=0, column=1, sticky="e")

        self.reset_on_backspace_checkbox = tk.Checkbutton(master, variable=self.reset_on_backspace_var)
        self.reset_on_backspace_checkbox.grid(row=1, column=1, sticky="e")

        self.reset_on_click_checkbox = tk.Checkbutton(master, variable=self.reset_on_click_var)
        self.reset_on_click_checkbox.grid(row=2, column=1, sticky="e")

        self.reset_on_tab_checkbox = tk.Checkbutton(master, variable=self.reset_on_tab_var)
        self.reset_on_tab_checkbox.grid(row=3, column=1, sticky="e")
        
        self.timeout_value_entry = tk.Entry(master, textvariable=self.timeout_value_var, width=2)
        self.timeout_value_entry.grid(row=4, column=1)

        if self.initial_values:
            # If initial values are provided, set them in the entry widgets
            self.keyword_case_sensitive_var.set(self.initial_values.get('keyword_case_sensitive', False))
            self.reset_on_backspace_var.set(self.initial_values.get('reset_on_backspace', False))
            self.reset_on_click_var.set(self.initial_values.get('reset_on_click', False))
            self.reset_on_tab_var.set(self.initial_values.get('reset_on_tab', False))
            self.timeout_value_var.set(self.initial_values.get('timeout_value', ''))

        return self.timeout_value_entry # Return the timeout value entry widget for initial focus

    def apply(self):
        """
        Apply the values entered in the dialog.

        Parameters:
        None

        Returns:
        None
        """
        # Get the entered settings values
        keyword_case_sensitive = self.keyword_case_sensitive_var.get()
        reset_on_backspace = self.reset_on_backspace_var.get()
        reset_on_click = self.reset_on_click_var.get()
        reset_on_tab = self.reset_on_tab_var.get()
        timeout_value = self.timeout_value_var.get()    

        self.result = {'case_sensitive': keyword_case_sensitive, 'backspace': reset_on_backspace, 'click': reset_on_click,  'tab': reset_on_tab, 'timeout': timeout_value}

class NotatorAssistant:
    def __init__(self, root, snippets_data, settings_data):
        """
        Initialize the NotatorAssistant class.

        Parameters:
        - root: The root Tkinter window.
        - snippets_data: Dictionary containing snippet data.
        - settings_data: Dictionary containing application settings.

        Returns:
        None
        """
        # Initialize the NotatorAssistant class with the given root window
        # Set the root window title
        self.root = root
        self.root.title("Notator Assistant")

        # Set the icon for the root window
        icon_path = "feather_quill_pen_write_sign_icon_124655.ico"
        root.iconbitmap(icon_path)

        self.current_word = ""  # Track the currently typed word
        self.snippets_data = snippets_data
        self.settings_data = settings_data
       

        # Create and pack three frames for organizing widgets
        self.frame1 = tk.Frame(root, padx=10, pady=5)
        self.frame2 = tk.Frame(root, padx=10, pady=5)
        self.frame3 = tk.Frame(root, padx=10, pady=5)

        self.frame1.pack(side="top", fill="both", expand=True)
        self.frame2.pack(side="top", fill="both", expand=True)
        self.frame3.pack(side="top", fill="both", expand=True)

        # Buttons for snippet management
        self.add_button = tk.Button(self.frame1, text="Add Snippet", command=self.add_snippet)
        self.add_button.pack(side='left', padx=2)

        self.edit_button = tk.Button(self.frame1, text="Edit Snippet", command=self.edit_snippet)
        self.edit_button.pack(side='left', padx=2)

        self.remove_button = tk.Button(self.frame1, text="Remove Snippet", command=self.remove_snippet)
        self.remove_button.pack(side='left', padx=2)

        self.clear_button = tk.Button(self.frame1, text="Clear Jam", command=self.clear_modifiers)
        self.clear_button.pack(side='right', padx=2)

        # Treeview for displaying snippets with scrollbar
        self.tree = ttk.Treeview(self.frame2, columns=('Keyword', 'Text'), show='headings', yscrollcommand=self.tree_yview)
        self.tree.heading('Keyword', text='Keyword', command=lambda: self.sort_treeview('Keyword', False))
        self.tree.heading('Text', text='Text', command=lambda: self.sort_treeview('Text', False))
        self.tree.column('Keyword', width=100)
        self.tree.column('Text', width=800)

        # Populate the Treeview with snippet data
        for keyword, text in snippets_data.items():
            # Display only the first line of multiline text
            display_text = self.extract_first_line(text)
            self.tree.insert('', 'end', values=(keyword, display_text))

        # Scrollbar for the Treeview
        self.tree_scrollbar = ttk.Scrollbar(self.frame2, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)

        # Pack the Treeview and scrollbar
        self.tree.pack(side="left", pady=5)
        self.tree_scrollbar.pack(side="left", fill="y", pady=5)

        # Text widget for displaying snippet details with scrollbar
        self.text_display = tk.Text(self.frame3, height=10, width=112, wrap='word', state='disabled')

        # Scrollbar for the Text widget
        self.text_scrollbar = ttk.Scrollbar(self.frame3, orient="vertical", command=self.text_display_yview)
        self.text_display.configure(yscrollcommand=self.text_scrollbar.set)

        # Pack the Text widget and scrollbar
        self.text_display.pack(side="left", pady=5)
        self.text_scrollbar.pack(side="left", fill="y", pady=5)

        # Register the keyboard events
        keyboard.on_press(self.on_key_press)

        # Bind the TreeView selection event to update the Text widget
        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)

        # Bind the window close event to the method that unhooks the keyboard
        root.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # Initialize the timeout timer
        self.timeout_timer = None
        self.timeout_duration = 5  # Timeout duration in seconds

        # Start the timeout timer thread
        self.start_timeout_timer()

        # Bind left mouse button click event to reset_current_word
        mouse.on_click(self.on_mouse_click)
        
        self.create_menu()

    def create_menu(self):
        """
        Create the menu bar for the application.

        Parameters:
        None

        Returns:
        None
        """
        # Create a menu bar
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # Create a File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Add File menu options
        file_menu.add_command(label="Add Snippet", command=self.add_snippet)
        file_menu.add_command(label="Edit Snippet", command=self.edit_snippet)
        file_menu.add_command(label="Remove Snippet", command=self.remove_snippet)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_window_close)

        # Create an Options menu
        options_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Options", menu=options_menu)

        # Add Options menu options
        options_menu.add_command(label="Settings", command=self.edit_settings)

    def start_timeout_timer(self):
        """
        Start the timeout timer thread.

        Parameters:
        None

        Returns:
        None
        """
        self.timeout_timer = threading.Timer(int(self.settings_data.get('Settings', 'timeout_value')), self.reset_current_word)
        self.timeout_timer.start()

    def reset_timeout_timer(self):
        """
        Reset the timeout timer.

        Parameters:
        None

        Returns:
        None
        """
        if self.timeout_timer:
            self.timeout_timer.cancel()
        self.start_timeout_timer()

    def reset_current_word(self):
        """
        Reset the current word when the timeout occurs.

        Parameters:
        None

        Returns:
        None
        """
        self.current_word = ""

    def extract_first_line(self, text):
        """
        Extract the first line of the text.

        Parameters:
        - text: The text content to extract the first line from

        Returns:
        - first_line: The first line of the provided text
        """
        first_line = text.split('\n')[0]
        return first_line

    def edit_settings(self):
        """
        Open the SettingsDialog to edit application settings.

        Parameters:
        None

        Returns:
        None
        """
        initial_values = {
            'keyword_case_sensitive': self.settings_data.get('Settings', 'keyword_case_sensitive'),
            'reset_on_backspace': self.settings_data.get('Settings', 'reset_on_backspace'),
            'reset_on_click': self.settings_data.get('Settings', 'reset_on_click'),
            'reset_on_tab': self.settings_data.get('Settings', 'reset_on_tab'),
            'timeout_value': self.settings_data.get('Settings', 'timeout_value')
        }

        dialog = SettingsDialog(self.root, "Settings", initial_values=initial_values)
        result = dialog.result

        if result:
            # Update the settings_data dictionary
            self.settings_data['Settings']['keyword_case_sensitive'] = str(result['case_sensitive'])
            self.settings_data['Settings']['reset_on_backspace'] = str(result['backspace'])
            self.settings_data['Settings']['reset_on_click'] = str(result['click'])
            self.settings_data['Settings']['reset_on_tab'] = str(result['tab'])
            self.settings_data['Settings']['timeout_value'] = result['timeout']

            # Save the updated settings to the INI file (if needed)
            self.save_settings_to_ini()

    def save_settings_to_ini(self):
        """
        Save the settings to the INI file.

        Parameters:
        None

        Returns:
        None
        """
        try:
            with open(ini_file, 'w') as configfile:  # Open the INI file for writing
                self.settings_data.write(configfile)  # Write the settings to the INI file
        except FileNotFoundError as e:
            # Handle file not found error
            print(f"Error saving settings to INI file: {e}")


    def add_snippet(self):
        """
        Open the SnippetDialog to add a new snippet.

        Parameters:
        None

        Returns:
        None
        """
        dialog = SnippetDialog(self.root, "Add Snippet")
        result = dialog.result

        if result:
            keyword, text = result

            # Check if the keyword contains spaces
            if ' ' in keyword:
                tk.messagebox.showinfo("Invalid Keyword", "The keyword cannot contain spaces. Please choose a different keyword.")
                return

            if keyword != "":
                # Check if the keyword already exists in the snippets_data dictionary
                if keyword in self.snippets_data:
                    tk.messagebox.showinfo("Duplicate Keyword", f"The keyword '{keyword}' already exists. Please choose a different keyword.")
                else:
                    # Add the new snippet to the snippets_data dictionary
                    self.snippets_data[keyword] = text

                    # Display only the first line of multiline text
                    display_text = self.extract_first_line(text)

                    # Insert the new snippet into the TreeView
                    self.tree.insert('', 'end', values=(keyword, display_text))

                    # Add the new snippet to the XML file
                    self.save_snippet_to_xml(keyword, text)
    
    def edit_snippet(self):
        """
        Open the SnippetDialog to edit an existing snippet.

        Parameters:
        None

        Returns:
        None
        """
        selected_item = self.tree.selection()

        if selected_item:
            keyword, text = self.tree.item(selected_item, 'values')
            fulltext = self.snippets_data.get(keyword, "")

            # Pre-populate the dialog with the selected snippet values
            initial_values = {'keyword': keyword, 'text': fulltext}
            dialog = SnippetDialog(self.root, "Edit Snippet", initial_values=initial_values)
            result = dialog.result

            if result:
                new_keyword, new_text = result

                # Update the snippets_data dictionary
                self.snippets_data.pop(keyword, None)
                self.snippets_data[new_keyword] = new_text

                # Display only the first line of multiline text
                display_text = self.extract_first_line(new_text)

                # Update the TreeView with the new keyword and text
                self.tree.item(selected_item, values=(new_keyword, display_text))

                # Update the text_display with the new keyword and text
                self.text_display.config(state='normal')  # Enable editing temporarily
                self.text_display.delete(1.0, tk.END)
                self.text_display.insert(tk.END, f"{new_text}")
                self.text_display.config(state='disabled')  # Disable editing again

                # Update the XML file (if needed)
                self.update_snippet_in_xml(keyword, new_keyword, new_text)
               
    def remove_snippet(self):
        """
        Remove the selected snippet from the TreeView.

        Parameters:
        None

        Returns:
        None
        """
        selected_item = self.tree.selection()

        if selected_item:
            keyword, _ = self.tree.item(selected_item)['values']

            # Remove the snippet from the snippets_data dictonary
            snippets_data.pop(keyword, None)

            # Remove the snippet from the TreeView
            self.tree.delete(selected_item)

            # Remove the snippet from the XML file
            self.remove_snippet_from_xml(keyword)

    def save_snippet_to_xml(self, keyword, text):
        """
        Save a new snippet to the XML file.

        Parameters:
        - keyword: The keyword of the snippet.
        - text: The text content of the snippet.

        Returns:
        None
        """
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Create a new 'snippet' element
        new_snippet = ET.Element('snippet')

        # Create 'keyword' and 'text' sub-elements
        ET.SubElement(new_snippet, 'keyword').text = keyword
        ET.SubElement(new_snippet, 'text').text = text

        # Append the new snippet to the root
        root.append(new_snippet)

        # Convert the XML tree to a formatted string with newline and indents
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")

        # Remove empty lines
        xml_str = '\n'.join([line for line in xml_str.split('\n') if line.strip()])

        # Write the formatted XML string to the XML file
        with open(xml_file, 'w') as file:
            file.write(xml_str)

    def update_snippet_in_xml(self, old_keyword, new_keyword, new_text):
        """
        Update an existing snippet in the XML file.

        Parameters:
        - old_keyword: The old keyword of the snippet to be updated.
        - new_keyword: The new keyword for the updated snippet.
        - new_text: The new text content for the updated snippet.

        Returns:
        None
        """
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for snippet in root.findall('snippet'):
            if snippet.find('keyword').text == old_keyword:
                # Update the keyword and text of the snippet
                snippet.find('keyword').text = new_keyword
                snippet.find('text').text = new_text
                break

        # Convert the XML tree to a formatted string with newline and indents
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")

        # Remove empty lines
        xml_str = '\n'.join([line for line in xml_str.split('\n') if line.strip()])

        # Write the formatted XML string to the XML file
        with open(xml_file, 'w') as file:
            file.write(xml_str)

    def remove_snippet_from_xml(self, keyword):
        """
        Remove a snippet from the XML file.

        Parameters:
        - keyword: The keyword of the snippet to be removed.

        Returns:
        None
        """
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for snippet in root.findall('snippet'):
            if snippet.find('keyword').text == keyword:
                root.remove(snippet)
                break

        # Convert the XML tree to a formatted string with newline and indents
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")

        # Remove empty lines
        xml_str = '\n'.join([line for line in xml_str.split('\n') if line.strip()])

        # Write the formatted XML string to the XML file
        with open(xml_file, 'w') as file:
            file.write(xml_str)

    def sort_treeview(self, col, reverse):
        """
        Sort the Treeview when a column header is clicked.

        Parameters:
        - col: The column to sort by.
        - reverse: True to sort in reverse order, False otherwise.

        Returns:
        None
        """
        data = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        data.sort(reverse=reverse)

        for index, (val, item) in enumerate(data):
            self.tree.move(item, '', index)

        # Switch the sort order for the next click
        self.tree.heading(col, command=lambda: self.sort_treeview(col, not reverse))

    def on_tree_click(self, event):
        """
        Update the Text widget with the full text of the selected item in the TreeView.

        Parameters:
        - event: The mouse event object.

        Returns:
        None
        """
        selected_item = self.tree.selection()
        if selected_item:
            keyword, text = self.tree.item(selected_item)['values']
            fulltext = self.snippets_data.get(keyword, "")
            self.text_display.config(state='normal')  # Enable editing temporarily
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(tk.END, f"{fulltext}")
            self.text_display.config(state='disabled')  # Disable editing again

    def tree_yview(self, *args):
        """
        Callback for the embedded scrollbar in the Treeview.

        Parameters:
        - *args: Variable number of arguments passed to the callback.

        Returns:
        None
        """
        self.tree.yview(*args)

    def text_display_yview(self, *args):
        """
        Callback for the embedded scrollbar in the Text widget.

        Parameters:
        - *args: Variable number of arguments passed to the callback.

        Returns:
        None
        """
        self.text_display.yview(*args)

    def on_mouse_click(self):
        """
        Handle left mouse button click event.

        Parameters:
        None

        Returns:
        None
        """
        # Reset the current word when the left mouse button is clicked
        self.reset_current_word()

    def on_key_press(self, event):
        """
        Handle key press events.

        Parameters:
        - event: The keyboard event object.

        Returns:
        None
        """
        if self.current_word is None:
            self.reset_current_word()
        
        if event.name == 'space':
            # check for matching keyword and expand text snippet
            for keyword, text in self.snippets_data.items():
                if (self.settings_data.get('Settings', 'keyword_case_sensitive') == "False"):
                    keyword = keyword.lower()
                    self.current_word = self.current_word.lower()
                if keyword == self.current_word:
                    # remove characters equal to the length of the keyword from the current word plus one for the space
                    for _ in range(len(keyword) + 1):
                        keyboard.press('backspace')
                        keyboard.release('backspace')
                        self.root.after(10)
                       
                    # write the expanded text
                    keyboard.write(text)

            self.reset_current_word()  # Reset the current word
            self.reset_timeout_timer()  # Reset the timeout timer when space is pressed
           
        elif event.name == 'enter':
            self.reset_current_word()  # Reset the current word on pressing Enter
            self.reset_timeout_timer()  # Reset the timeout timer when Enter is pressed

        elif event.name == 'tab':
            if (self.settings_data.get('Settings', 'reset_on_tab') == "True"):
                self.reset_current_word()
       
        elif event.name == 'backspace':
            if (self.settings_data.get('Settings', 'reset_on_backspace') == "True"):
                self.reset_current_word()
            else:
                self.current_word = self.current_word[:-1]  # Remove the last character when backspace is pressed
                self.reset_timeout_timer()  # Reset the timeout timer when backspace is pressed
   
        elif event.name in string.printable:
            self.current_word += event.name  # Add the pressed key to the current word
            self.reset_timeout_timer()  # Reset the timeout timer when a printable character is pressed

    def clear_modifiers(self):
        """
        Workaround for known issue with program after Windows lockscreen unlock.

        Parameters:
        None

        Returns:
        None
        """
        keyboard.release('alt')
        self.root.after(10)
        keyboard.release('ctrl')
        self.root.after(10)
        keyboard.release('shift')
        self.root.after(10)

    def on_window_close(self):
        """
        Removes all keyboard and mouse hooks when the window is closed.

        Parameters:
        None

        Returns:
        None
        """
        keyboard.unhook_all()
        mouse.unhook_all()
        self.root.destroy()

def read_snippets_from_xml(xml_file):
    """
    Read snippets from an XML file and return a dictionary of keywords and texts.

    Parameters:
    - xml_file: The path to the XML file containing snippets.

    Returns:
    - snippets_data: A dictionary containing keywords as keys and corresponding text snippets as values.
                     Returns an empty dictionary if there's an error reading the XML file.
    """
    try:
        snippets_data = {}  # Initialize an empty dictionary to store snippets
        tree = ET.parse(xml_file)  # Parse the XML file
        root = tree.getroot()  # Get the root element of the XML tree

        # Iterate through each 'snippet' element in the XML
        for element in root.findall('snippet'):
            keyword = element.find('keyword').text  # Extract the keyword from the 'keyword' sub-element
            text = element.find('text').text  # Extract the text content from the 'text' sub-element
            snippets_data[keyword] = text  # Add the snippet to the dictionary with keyword as key and text as value

        return snippets_data  # Return the dictionary of snippets
    except (FileNotFoundError, ET.ParseError) as e:
        # Handle file not found or parsing errors
        print(f"Error reading XML file: {e}")
        return {}  # Return an empty dictionary if there's an error
   
def read_settings_from_ini(ini_file):
    """
    Read settings from an INI file and return a configparser object.

    Parameters:
    - ini_file: The path to the INI file containing settings.

    Returns:
    - settings_data: A configparser.ConfigParser object containing the settings read from the INI file.
                     Returns an empty ConfigParser object if there's an error reading the INI file.
    """
    try:
        config = configparser.ConfigParser()  # Initialize a ConfigParser object
        config.read(ini_file)  # Read the settings from the INI file

        return config  # Return the ConfigParser object containing the settings
    except (FileNotFoundError, configparser.Error) as e:
        # Handle file not found or parsing errors
        print(f"Error reading INI file: {e}")
        return configparser.ConfigParser()  # Return an empty ConfigParser object if there's an error

if __name__ == "__main__":
    xml_file = "snippets.xml"
    ini_file = "settings.ini"

    snippets_data = read_snippets_from_xml(xml_file)
    settings_data = read_settings_from_ini(ini_file)
   
    root = tk.Tk()
    root.resizable(False, False)
    app = NotatorAssistant(root, snippets_data, settings_data)
    root.mainloop()
