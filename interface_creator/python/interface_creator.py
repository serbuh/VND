import os
script_folder = os.path.dirname(os.path.abspath(__file__))

try:
    import PySimpleGUI as sg
except:
    print("ERROR: No module PySimpleGUI. Please install:\npython -m venv env\nenv\\Scripts\\activate\npython -m pip install PySimpleGUI\nor\npython -m pip install .\\installs\\PySimpleGUI-4.60.5-py3-none-any.whl\n\nPress any key to exit")
    input()
    exit()

from interface_creator.python.generate_telemetry_json import JSON_Creator
from telemetry_server.config_parser import TelemServerConfig


class InterfaceCreatorGUI():
    def __init__(self):
        # Get the interfaces files folder
        self.interfaces_folder = os.path.join(script_folder, "examples")
        interface_file = os.path.join(script_folder, "..", "..", "openmct", "telemetry_plugin", "openmct_interface.json")
        port_file = os.path.join(script_folder, "..", "..", "telemetry_server", "server_config.ini")
		# Check existence of interfaces folder
        if not os.path.exists(self.interfaces_folder):
            sg.popup_cancel(f'Folder does not exist!: {self.interfaces_folder}')
            return
        
        # Object that works with files (interface, ports)
        self.json_creator = JSON_Creator(interface_file, port_file)

        # Get list of interface examples
        self.file_paths, self.filenames_only = JSON_Creator.get_files_from_folder(self.interfaces_folder)
        
        if len(self.file_paths) == 0:
            sg.popup(f'No config files in folder {self.interfaces_folder}')
            return

        # Read config
        self.cfg = TelemServerConfig(os.path.join("telemetry_server", "server_config.ini"))
        self.cfg.print_summary()

        # Menu layout
        menu_content = [['File', ['Open Folder', 'Exit']], ['Help', ['About', ]]]
        menu = sg.Menu(menu_content)

        # Select port
        label_width = 18
        config_layout = [[
            sg.Text('Listening for telemetry on', size=(label_width, 1)),
            sg.Input(self.cfg.telem_ip, enable_events=True, size=(15, 1), key='-telem_ip-', justification='left'),
            sg.Text(':'),
            sg.Input(self.cfg.telem_port, enable_events=True, size=(5, 1), key='-telem_port-', justification='left'),
        ],
        [
            sg.Text('Listening for video on', size=(label_width, 1)),
            sg.Input(self.cfg.video_ip, enable_events=True, size=(15, 1), key='-video_ip-', justification='left'),
            sg.Text(':'),
            sg.Input(self.cfg.video_port, enable_events=True, size=(5, 1), key='-video_port-', justification='left'),
        ],
        [
            sg.Text('Browser port', size=(label_width, 1)),
            sg.Input("localhost", enable_events=True, size=(15, 1), readonly=True, text_color="grey", justification='left'),
            sg.Text(':'),
            sg.Input(self.cfg.browser_port, enable_events=True, size=(5, 1), key='-browser_port-', justification='left'),
        ],
        [
            sg.Button("Update"),
        ]]
        config_frame = sg.Frame("Server Config", config_layout)

        # File list
        col_files_list = [
            [sg.Button('New', key='-NEW_BTN-', size=(8, 1), button_color="green"), sg.FileBrowse(enable_events=True, size=(8, 1), button_color="green", key="-BROWSE-", target="-BROWSE-", file_types=(("TXT Files", "*.txt"),) )],
            [sg.Text(f'File 1 of {len(self.file_paths)}', key='-FILENUM-')],
            [sg.Listbox(values=self.filenames_only, size=(30, 15), key='-LISTBOX-', enable_events=True)],
        ]
        # Content of file
        col_file_content = [
            [sg.Button('Use this', key='-USE_THIS_BTN-', size=(8, 1), disabled=True, button_color="green")],
            [sg.Text("Select something", key='-FILENAME-')],
            [sg.Multiline("", size=(80, 16), key='-MULTILINE-')],
        ]
        files_frame = sg.Frame("Select interface", [[sg.Col(col_files_list), sg.Col(col_file_content, vertical_alignment="top")]])
        
        # Exit
        col_exit_content = [[sg.Button('Exit', size=(8, 1), button_color="red")]]
        col_exit = sg.Col(col_exit_content, justification="right")

        layout = [[menu], [config_frame], [files_frame], [col_exit]]

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
            elif event in ('MouseWheel:Down', 'Down:40') and filenum < len(self.file_paths)-1:
                filenum += 1
                filepath = os.path.join(self.interfaces_folder, self.filenames_only[filenum])
                self.window['-LISTBOX-'].update(set_to_index=filenum, scroll_to_index=filenum)
                self.update_selected_filename(filenum, filepath)
            elif event in ('MouseWheel:Up', 'Up:38') and filenum > 0:
                filenum -= 1
                filepath = os.path.join(self.interfaces_folder, self.filenames_only[filenum])
                self.window['-LISTBOX-'].update(set_to_index=filenum, scroll_to_index=filenum)
                self.update_selected_filename(filenum, filepath)
            elif event == '-LISTBOX-':
                filepath = os.path.join(self.interfaces_folder, values['-LISTBOX-'][0])
                filenum = self.file_paths.index(filepath)
                self.update_selected_filename(filenum, filepath)
            elif event == '-USE_THIS_BTN-':
                self.popup_generate(self.window['-MULTILINE-'].get())
            elif event == '-NEW_BTN-':
                self.popup_generate("")
            elif event == '-BROWSE-':
                browse_filepath = values['-BROWSE-']
                with open(browse_filepath, "rt", encoding='utf-8') as f:
                    text = f.read()
                self.popup_generate(text)
            elif event == 'Update':
                self.cfg.browser_port = self.window["-browser_port-"].get()
                self.cfg.telem_ip     = self.window["-telem_ip-"].get()
                self.cfg.telem_port   = self.window["-telem_port-"].get()
                self.cfg.video_ip     = self.window["-video_ip-"].get()
                self.cfg.video_port   = self.window["-video_port-"].get()
                self.cfg.write_to_file()
            elif event == 'Exit':
                break
            # ----------------- Menu choices -----------------
            elif event == 'Open Folder':
                newfolder = sg.popup_get_folder('New folder', no_window=True)
                if newfolder is None:
                    continue
                
                self.file_paths, self.filenames_only = JSON_Creator.get_files_from_folder(newfolder)

                self.window['-LISTBOX-'].update(values=self.filenames_only)
                self.window.refresh()

                filenum = 0

            elif event == 'About':
                sg.popup('Wa wa wee wa',
                        'Very nice!')

        self.window.close()

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

        self.window['-USE_THIS_BTN-'].update(disabled=False)

    def popup_generate(self, text):
        text = text.rstrip("\n") # Remove newline at the end (they appear in some versions of python/PySimpleGUI)
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
                # send text to generate_telemetry_json
                success = self.json_creator.generate_json_from_lines(final_text)
                break
        win.close()
    
    def popup_browse(self):
        layout = [
            [],
        ]
        win = sg.Window("Generate", layout, modal=True, finalize=True)

        while True:
            event, values = win.read()
            if event == sg.WINDOW_CLOSED:
                break
            elif event == 'Write':
                final_text = win['-FINAL_CONTENT-'].get()
                # send text to generate_telemetry_json
                success = self.json_creator.generate_json_from_lines(final_text)
                break
        win.close()


if __name__ == '__main__':
    gui = InterfaceCreatorGUI()
    gui.loop()