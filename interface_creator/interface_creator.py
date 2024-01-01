#!/usr/bin/env python
import os
try:
    import PySimpleGUI as sg
except:
    print("ERROR: No module PySimpleGUI. Please install:\npython -m venv env\nenv\\Scripts\\activate\npython -m pip install PySimpleGUI\nor\npython -m pip install .\installs\PySimpleGUI-4.60.5-py3-none-any.whl\n\nPress any key to exit")
    input()
    exit()

from generate_from_list import generate_openmct_json

def get_files_from_folder(folder):
    file_paths = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith('.txt')]
    filenames_only = [f for f in os.listdir(folder) if f.lower().endswith('.txt')]
    return file_paths, filenames_only

def popup_generate(text):
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

def main():

    # Get the configuration folder
    folder = os.path.join(".", "examples")
    if not os.path.exists(folder):
        sg.popup_cancel(f'Folder does not exist!: {folder}')
        return

    # Get list of interface examples
    file_paths, filenames_only = get_files_from_folder(folder)
    
    if len(file_paths) == 0:
        sg.popup(f'No config files in folder {folder}')
        return

    # Menu layout
    menu = [['File', ['Open Folder', 'Exit']], ['Help', ['About', ]]]

    # File list column
    col_files_list = [
        [sg.Text('Select a file')],
        [sg.Listbox(values=filenames_only, size=(30, 30), key='-LISTBOX-', enable_events=True)],
        [sg.Button('Prev', size=(8, 2)), sg.Button('Next', size=(8, 2)),
            sg.Text('File 1 of {}'.format(len(file_paths)), size=(15, 1), key='-FILENUM-')]
    ]

    # define layout, show and read the window
    col_file_content = [
        [sg.Text("Select something", key='-FILENAME-')],
        [sg.Multiline("", size=(80, 32), key='-MULTILINE-')],
        [sg.Button('Generate', size=(8, 2))],
    ]

    layout = [[sg.Menu(menu)], [sg.Col(col_files_list), sg.Col(col_file_content, vertical_alignment="top")]]

    window = sg.Window('Config Generator', layout, return_keyboard_events=True, use_default_focus=False)

    # loop reading the user input and displaying text, filepath
    filenum, filepath, filename = 0, file_paths[0], filenames_only[0]
    while True:

        event, values = window.read()

        # --------------------- Button & Keyboard ---------------------
        if event == sg.WIN_CLOSED:
            break
        elif event in ('Next', 'MouseWheel:Down', 'Down:40', 'Next:34') and filenum < len(file_paths)-1:
            filenum += 1
            filepath = os.path.join(folder, filenames_only[filenum])
            window['-LISTBOX-'].update(set_to_index=filenum, scroll_to_index=filenum)
        elif event in ('Prev', 'MouseWheel:Up', 'Up:38', 'Prior:33') and filenum > 0:
            filenum -= 1
            filepath = os.path.join(folder, filenames_only[filenum])
            window['-LISTBOX-'].update(set_to_index=filenum, scroll_to_index=filenum)
        elif event == 'Exit':
            break
        elif event == '-LISTBOX-':
            filepath = os.path.join(folder, values['-LISTBOX-'][0])
            filenum = file_paths.index(filepath)
        
        # Generate
        if event == 'Generate':
            popup_generate(window['-MULTILINE-'].get())
        
        # Get file name (w/o path)
        filename = filenames_only[filenum]

        # ----------------- Menu choices -----------------
        if event == 'Open Folder':
            newfolder = sg.popup_get_folder('New folder', no_window=True)
            if newfolder is None:
                continue
            
            file_paths, filenames_only = get_files_from_folder(newfolder)

            window['-LISTBOX-'].update(values=filenames_only)
            window.refresh()

            filenum = 0
        elif event == 'About':
            sg.popup('Wa wa wee wa',
                     'Very nice!')

        # Update multiline with the text
        try:
            with open(filepath, "rt", encoding='utf-8') as f:
                text = f.read()
            window['-MULTILINE-'].update(text)
        except Exception as e:
            print("Error: ", e)
            
        # update window with filepath
        window['-FILENAME-'].update(filename)

        # update page display
        window['-FILENUM-'].update('File {} of {}'.format(filenum + 1, len(file_paths)))

    window.close()

if __name__ == '__main__':
    main()