#!/usr/bin/env python
import os
try:
    import PySimpleGUI as sg
except:
    print("ERROR: No module PySimpleGUI. Please install:\npython -m venv env\nenv\\Scripts\\activate\npython -m pip install PySimpleGUI\nor\npython -m pip install .\\installs\\PySimpleGUI-4.60.5-py3-none-any.whl\n\nPress any key to exit")
    input()
    exit()

from generate_from_list import generate_openmct_json

class InterfaceCreatorGUI():
    def __init__(self):
        # Get the interfaces files folder
        self.interfaces_folder = os.path.join(".", "examples")
        self.port_file = os.path.join("..", "..", "telemetry_server", "port_config.txt")
        
        # Check existence of interfaces folder
        if not os.path.exists(self.interfaces_folder):
            sg.popup_cancel(f'Folder does not exist!: {self.interfaces_folder}')
            return
        
        # Get list of interface examples
        self.file_paths, self.filenames_only = self.get_files_from_folder(self.interfaces_folder)
        
        if len(self.file_paths) == 0:
            sg.popup(f'No config files in folder {self.interfaces_folder}')
            return

        # Check existence of port config file
        if not os.path.exists(self.port_file):
            sg.popup_cancel(f'Port config file does not exist!: {self.port_file}')
            return

        port_input = self.get_port_from_file()

        # Menu layout
        menu = [['File', ['Open Folder', 'Exit']], ['Help', ['About', ]]]

        # Select port
        row_port_selection = [
            [sg.Text('Select a port'),
                sg.Input(port_input, enable_events=True, key='-PORT_INPUT-', justification='left'),
                sg.Button("Update Port")],
        ]

        # File list column
        col_files_list = [
            [sg.Text('Select interface')],
            [sg.Listbox(values=self.filenames_only, size=(30, 30), key='-LISTBOX-', enable_events=True)],
            [sg.Button('Prev', size=(8, 1)), sg.Button('Next', size=(8, 1)),
                sg.Text('File 1 of {}'.format(len(self.file_paths)), size=(15, 1), key='-FILENUM-')]
        ]
        
        # define layout, show and read the window
        col_file_content = [
            [sg.Text("Select something", key='-FILENAME-')],
            [sg.Multiline("", size=(80, 32), key='-MULTILINE-')],
            [sg.Button('Generate', key='-GEN_BTN-', size=(8, 1), disabled=True), sg.Push(), sg.Button('Exit', size=(8, 1), button_color="red")],
        ]

        layout = [[sg.Menu(menu)], row_port_selection, [sg.Col(col_files_list), sg.Col(col_file_content, vertical_alignment="top")]]

        self.window = sg.Window('Config Generator', layout, return_keyboard_events=True, use_default_focus=False)
    
    def loop(self):
                    
        # loop reading the user input and displaying text, filepath
        filenum, filepath, filename = 0, self.file_paths[0], self.filenames_only[0]
        while True:
            event, values = self.window.read()
            #print(event)

            # --------------------- Window ---------------------
            if event == sg.WIN_CLOSED:
                break
            # --------------------- Buttons ---------------------
            elif event in ('Next', 'MouseWheel:Down', 'Down:40', 'Next:34') and filenum < len(self.file_paths)-1:
                filenum += 1
                filepath = os.path.join(self.interfaces_folder, self.filenames_only[filenum])
                self.window['-LISTBOX-'].update(set_to_index=filenum, scroll_to_index=filenum)
                self.update_selected_filename(filenum, filepath)
            elif event in ('Prev', 'MouseWheel:Up', 'Up:38', 'Prior:33') and filenum > 0:
                filenum -= 1
                filepath = os.path.join(self.interfaces_folder, self.filenames_only[filenum])
                self.window['-LISTBOX-'].update(set_to_index=filenum, scroll_to_index=filenum)
                self.update_selected_filename(filenum, filepath)
            elif event == '-LISTBOX-':
                filepath = os.path.join(self.interfaces_folder, values['-LISTBOX-'][0])
                filenum = self.file_paths.index(filepath)
                self.update_selected_filename(filenum, filepath)
            elif event == '-GEN_BTN-':
                self.popup_generate(self.window['-MULTILINE-'].get())
            elif event == 'Update Port':
                port = self.window["-PORT_INPUT-"].get()
                self.set_port_to_file(port)
            elif event == 'Exit':
                break
            # ----------------- Menu choices -----------------
            elif event == 'Open Folder':
                newfolder = sg.popup_get_folder('New folder', no_window=True)
                if newfolder is None:
                    continue
                
                self.file_paths, self.filenames_only = self.get_files_from_folder(newfolder)

                self.window['-LISTBOX-'].update(values=self.filenames_only)
                self.window.refresh()

                filenum = 0

            elif event == 'About':
                sg.popup('Wa wa wee wa',
                        'Very nice!')

        self.window.close()
    
    def get_port_from_file(self):
        with open(self.port_file, "rt", encoding='utf-8') as f:
            port_input = f.read()
            port_input = str(int(port_input))
        return port_input

    def set_port_to_file(self, port):
        with open(self.port_file, "wt", encoding='utf-8') as f:
            print(f"Setting port to {port}")
            f.write(port)

    def update_selected_filename(self, filenum, filepath):
        # Get file name (w/o path)
        filename = self.filenames_only[filenum]

        # update window with filepath
        self.window['-FILENAME-'].update(filename)

        # update page display
        self.window['-FILENUM-'].update('File {} of {}'.format(filenum + 1, len(self.file_paths)))

        # Update multiline with the text
        try:
            with open(filepath, "rt", encoding='utf-8') as f:
                text = f.read()
            self.window['-MULTILINE-'].update(text)
        except Exception as e:
            print("Error: ", e)

        self.window['-GEN_BTN-'].update(disabled=False)

    def get_files_from_folder(self, interfaces_folder):
        file_paths = [os.path.join(interfaces_folder, f) for f in os.listdir(interfaces_folder) if f.lower().endswith('.txt')]
        filenames_only = [f for f in os.listdir(interfaces_folder) if f.lower().endswith('.txt')]
        return file_paths, filenames_only

    def popup_generate(self, text):
        layout = [
            [sg.Multiline(text, size=(80, 32), key='-FINAL_CONTENT-'),],
            [sg.Button("Write", button_color="green")],
        ]
        win = sg.Window("Generate", layout, modal=True, finalize=True)

        while True:
            event, values = win.read()
            if event == sg.WINDOW_CLOSED:
                break
            elif event == 'Write':
                final_text = win['-FINAL_CONTENT-'].get()
                # send text to generate_from_list
                generate_openmct_json(final_text)
                break
        win.close()


if __name__ == '__main__':
    gui = InterfaceCreatorGUI()
    gui.loop()