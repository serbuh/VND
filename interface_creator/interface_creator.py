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
        if not os.path.exists(self.interfaces_folder):
            sg.popup_cancel(f'Folder does not exist!: {self.interfaces_folder}')
            return

        # Get list of interface examples
        self.get_files_from_folder(self.interfaces_folder)
        
        if len(self.file_paths) == 0:
            sg.popup(f'No config files in folder {self.interfaces_folder}')
            return

        # Menu layout
        menu = [['File', ['Open Folder', 'Exit']], ['Help', ['About', ]]]

        # Select port
        row_port_selection = [
            [sg.Text('Select a port'),
                sg.Input('', enable_events=True, key='-PORT_INPUT-', expand_x=True, justification='left'),
                sg.Button("Update")],
        ]

        # File list column
        col_files_list = [
            [sg.Text('Select interface')],
            [sg.Listbox(values=self.filenames_only, size=(30, 30), key='-LISTBOX-', enable_events=True)],
            [sg.Button('Prev', size=(8, 2)), sg.Button('Next', size=(8, 2)),
                sg.Text('File 1 of {}'.format(len(self.file_paths)), size=(15, 1), key='-FILENUM-')]
        ]

        # define layout, show and read the window
        col_file_content = [
            [sg.Text("Select something", key='-FILENAME-')],
            [sg.Multiline("", size=(80, 32), key='-MULTILINE-')],
            [sg.Button('Generate', size=(8, 2))],
        ]

        layout = [[sg.Menu(menu)], row_port_selection, [sg.Col(col_files_list), sg.Col(col_file_content, vertical_alignment="top")]]

        self.window = sg.Window('Config Generator', layout, return_keyboard_events=True, use_default_focus=False)
    
    def loop(self):
        # loop reading the user input and displaying text, filepath
        filenum, filepath, filename = 0, self.file_paths[0], self.filenames_only[0]
        while True:

            event, values = self.window.read()

            # --------------------- Button & Keyboard ---------------------
            if event == sg.WIN_CLOSED:
                break
            elif event in ('Next', 'MouseWheel:Down', 'Down:40', 'Next:34') and filenum < len(self.file_paths)-1:
                filenum += 1
                filepath = os.path.join(self.interfaces_folder, self.filenames_only[filenum])
                self.window['-LISTBOX-'].update(set_to_index=filenum, scroll_to_index=filenum)
            elif event in ('Prev', 'MouseWheel:Up', 'Up:38', 'Prior:33') and filenum > 0:
                filenum -= 1
                filepath = os.path.join(self.interfaces_folder, self.filenames_only[filenum])
                self.window['-LISTBOX-'].update(set_to_index=filenum, scroll_to_index=filenum)
            elif event == 'Exit':
                break
            elif event == '-LISTBOX-':
                filepath = os.path.join(self.interfaces_folder, values['-LISTBOX-'][0])
                filenum = self.file_paths.index(filepath)
            
            # Generate
            if event == 'Generate':
                self.popup_generate(self.window['-MULTILINE-'].get())
            
            # Get file name (w/o path)
            filename = self.filenames_only[filenum]

            # ----------------- Menu choices -----------------
            if event == 'Open Folder':
                newfolder = sg.popup_get_folder('New folder', no_window=True)
                if newfolder is None:
                    continue
                
                self.get_files_from_folder(newfolder)

                self.window['-LISTBOX-'].update(values=self.filenames_only)
                self.window.refresh()

                filenum = 0
            elif event == 'About':
                sg.popup('Wa wa wee wa',
                        'Very nice!')

            # Update multiline with the text
            try:
                with open(filepath, "rt", encoding='utf-8') as f:
                    text = f.read()
                self.window['-MULTILINE-'].update(text)
            except Exception as e:
                print("Error: ", e)
                
            # update window with filepath
            self.window['-FILENAME-'].update(filename)

            # update page display
            self.window['-FILENUM-'].update('File {} of {}'.format(filenum + 1, len(self.file_paths)))

        self.window.close()

    def get_files_from_folder(self, interfaces_folder):
        self.file_paths = [os.path.join(interfaces_folder, f) for f in os.listdir(interfaces_folder) if f.lower().endswith('.txt')]
        self.filenames_only = [f for f in os.listdir(interfaces_folder) if f.lower().endswith('.txt')]

    def popup_generate(self, text):
        layout = [
            [sg.Multiline(text, size=(80, 32), key='-FINAL_CONTENT-'),],
            [sg.Button("Write")],
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