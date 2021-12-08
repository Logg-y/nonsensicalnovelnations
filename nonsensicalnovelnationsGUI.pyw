import os
import queue
import subprocess
import sys
import threading
import nationals
import csv
import re
import traceback

import PySimpleGUI as sg

CLARGS = ["modname", "numnations", "numunits", "numcommanders", "pretendercount", "fixedseeds",
          "startnationid", "startunitid", "startsiteid", "output", "maxtotalpathspernation"]

ERA_PREFIXES = {1: "EA", 2: "MA", 3: "LA"}

proc = None
nationselection = None
outputqueue = queue.Queue()
vanillanations = []

ver = "v0.0.1"


def output_polling_thread(timeout=0.1):
    """
    Readline blocks, which means it can't be used in the main thread without making the interface periodically
    unresponsive.
    This gets around the issue by having a thread do it and write the values to a queue. The queue can be polled
    without blocking in the main thread safely.
    """
    global proc
    while 1:
        if proc.poll() is None:
            # nonsensicalnovelnations's console output is, because I was weird, to stderr and not stdout
            # it redirects its stdout to a file instead
            # this blocks until there is a new output line
            content = proc.stderr.readline()
            if len(content) > 0:
                #content += "\r\n"
                outputqueue.put(content)
        else:
            break


def spawn_worker_process(**kwargs):
    global proc
    # Should double for release and testing
    # and hopefully also work on unix...
    tmp = os.path.join(os.getcwd(), "nonsensicalnovelnations.exe")
    if os.path.isfile(tmp) and sys.platform.startswith("win"):
        paramlist = [tmp]
    else:
        if sys.platform.startswith("win"):
            paramlist = ["python", "nonsensicalnovelnations.py"]
        else:
            paramlist = ["python3", "nonsensicalnovelnations.py"]

    paramlist += ["-run", "1"]

    for key, paramval in kwargs.items():
        paramlist.append(f"-{key}")
        if key in ["fixedseeds"]:
            # This prevents the list being interpreted as a command line option if a negative value is first
            paramval = " " + paramval
        paramlist.append(f"{paramval}")
    outputqueue.put(f"Passing parameters: {paramlist}\n")

    proc = subprocess.Popen(
        paramlist, shell=False, cwd=os.getcwd(), bufsize=1,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,  # PyInstaller needs this or attempting the call throws "failed to execute script"
        universal_newlines=True)
    return proc


UP_ARROW = "˄"
DOWN_ARROW = "˅"

defaultfolder = os.path.join(os.getcwd(), "output")

def detectids(window, modlist):
    "Detect sensible starting IDs based on the mods."
    nationals.read_mods(modlist)
    startunitid = max(nationals.monsterids) + 1
    startnationid = max(nationals.nationids) + 1
    startsiteid = max(nationals.siteids) + 1
    window["-startunitid-"].update(value=str(startunitid))
    window["-startnationid-"].update(value=str(startnationid))
    window["-startsiteid-"].update(value=str(startsiteid))


def main():
    global proc
    sg.theme("DarkBrown")

    ["modname", "numnations", "numunits", "numcommanders", "pretendercount", "fixedseeds",
     "startnationid", "startunitid", "startsiteid"]

    output_left_col = [[
        sg.Text("Output Folder: ", k="-OutputFolderLabel-", pad=(7, 5), size=(10, 1)),
        sg.InputText(os.path.join(os.getcwd(), "output"), k="-output-", pad=(0, 0), size=(43, 1))
    ]]



    basic_category = [
        [sg.Text('Name of the mod. If left blank a rather unhelpful number will be generated at random.',
                 size=(50, 2), relief="ridge"),
         sg.InputText(key='-modname-', size=(50, 1))],
        [sg.Column(output_left_col),
         sg.FolderBrowse(initial_folder=defaultfolder, k="-FolderBrowser-")],
        [sg.Text('Number of nations to generate', size=(50, 1), relief="ridge"),
         sg.InputText(key='-numnations-', size=(4, 1), default_text=20)],
        [sg.Text('Number of non-commander units to generate per nation', size=(50, 1), relief="ridge"),
         sg.InputText(key='-numunits-', size=(4, 1), default_text=15)],
        [sg.Text('Number of commander units to generate per nation', size=(50, 1), relief="ridge"),
         sg.InputText(key='-numcommanders-', size=(4, 1), default_text=10)],
        [sg.Text('Number of pretender choices to generate per nation', size=(50, 1), relief="ridge"),
         sg.InputText(key='-pretendercount-', size=(4, 1), default_text=25)],
        [sg.Text('Maximum sum of non-magic paths (including randoms) allowed on one nation', size=(50, 2), relief="ridge"),
         sg.InputText(key='-maxtotalpathspernation-', size=(4, 1), default_text=15)],
        [sg.Text('Nation ID to start generating at', size=(50, 1), relief="ridge"),
         sg.InputText(key='-startnationid-', size=(4, 1), default_text=121)],
        [sg.Text('Unit ID to start generating at', size=(50, 1), relief="ridge"),
         sg.InputText(key='-startunitid-', size=(4, 1), default_text=3550)],
        [sg.Text('Site ID to start generating at', size=(50, 1), relief="ridge"),
         sg.InputText(key='-startsiteid-', size=(4, 1), default_text=1510)],
        [sg.Text('A list of seeds to generate from, separated by commas', size=(50, 1), relief="ridge"),
         sg.InputText(key='-fixedseeds-', size=(50, 1), default_text="")],
        [sg.Text('A list of mods to use to check for compatible IDs, separated by commas', size=(50, 2), relief="ridge"),
         sg.InputText(key='-modlist-', size=(50, 2), default_text="")],
        [sg.Button("Autodetect Good Starting IDs")],
    ]

    layout = [[sg.Text(UP_ARROW, k="-ToggleBasicOptionsArrow-", enable_events=True),
               sg.Text("Basic Options", enable_events=True, k="-ToggleBasicOptionsLabel-", font=("arial", 20))],
              [sg.pin(sg.Column(basic_category, k="-BasicOptions-"))],
              [sg.Button('Generate', size=(7, 1)), sg.Button('Quit', size=(7, 1))],
              [sg.Multiline("", autoscroll=True, size=(100, 7), key="-OUTPUT-")]]


    visibility = {"BasicOptions": True}
    window = sg.Window(f"NonsensicalNovelNations {ver}", layout)

    # Event Loop to process "events" and get the "values" of the inputs
    generating = False
    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED or event == 'Quit':
            break

        if generating:
            if proc is not None:
                while 1:
                    try:
                        new = outputqueue.get_nowait().strip()
                        old = window["-OUTPUT-"].Get().strip()
                        window["-OUTPUT-"].update(old + os.linesep + new)
                    except queue.Empty:
                        break

                if proc.poll() is not None:
                    generating = False

        if event == 'Generate':
            if generating:
                continue
            generating = True
            clargdict = {}
            for argname in CLARGS:
                argval = values[f"-{argname}-"]
                if argval.strip() != "":
                    clargdict[argname] = argval
            spawn_worker_process(**clargdict)
            outputthread = threading.Thread(target=output_polling_thread)
            outputthread.start()

        for section in ["BasicOptions"]:
            if event.startswith(f"-Toggle{section}"):
                newvis = not visibility[section]
                visibility[section] = newvis
                window[f"-Toggle{section}Arrow-"].update(UP_ARROW if newvis else DOWN_ARROW)
                window[f"-{section}-"].update(visible=newvis)
                break

        if event == "Autodetect Good Starting IDs":
            detectids(window, values["-modlist-"])

    window.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        with open("nonsensicalnovelnationsGUIerror.txt", "w") as f:
            f.write(traceback.format_exc())
        raise e