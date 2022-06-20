import os
import sys
import traceback
import autocalc
import unitinbasedatafinder
import time
import re
import io

import PySimpleGUI as sg

def autocalcTool():
    defaultoutput = sys.stdout
    unitinbasedatafinder.loadAllUnitData()
    sg.theme("DarkBrown")

    lookuprow = [sg.Text("Lookup Unit ID: ", size=(15, 1)),
         sg.InputText("", k="-lookupunitid-", size=(5, 1)),
         sg.Button("Run", k="-runautocalc-"),
         sg.Text("", k="-unitidentity-", size=(30, 1))]

    outputarea = [[sg.Text("Unit Cost: ", size=(15, 1)), sg.Text("", size=(10, 1), key="-unitcost-")],
                  [sg.Text("Cmdr Cost: ", size=(15, 1)), sg.Text("", size=(10, 1), key="-cmdrcost-")],
        [sg.Multiline("", autoscroll=True, size=(100, 20), key="-OUTPUT-")]]

    layout = [lookuprow,
              *outputarea
            ]

    window = sg.Window(f"NNN Autocalc Tool", layout)

    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED or event == 'Quit':
            break

        if event == "-runautocalc-":
            try:
                sys.stdout = io.StringIO("===== BEGIN UNIT CALC =====\n\n")
                uid = int(values["-lookupunitid-"])
                unit = unitinbasedatafinder.get(uid)
                window["-unitidentity-"].update(f"{uid} - {unit.name}")
                unitcost = autocalc.unit(unit)
                window["-unitcost-"].update(str(unitcost))
                print("\n\n\n -------------------------------- \n\n\n")
                cmdrcost = autocalc.commander(unit)
                window["-cmdrcost-"].update(str(cmdrcost))
                window["-OUTPUT-"].update(sys.stdout.getvalue())
                sys.stdout.close()
                sys.stdout = defaultoutput
            except:
                window["-OUTPUT-"].update(traceback.format_exc())


    window.close()


if __name__ == "__main__":
    try:
        autocalcTool()
    except Exception as e:
        with open("autocalcGUIerror.txt", "w") as f:
            f.write(traceback.format_exc())
        raise e