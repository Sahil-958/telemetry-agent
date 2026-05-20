Set objShell = CreateObject("WScript.Shell")
' Get the directory of this VBScript
strPath = Left(WScript.ScriptFullName, Len(WScript.ScriptFullName) - Len(WScript.ScriptName))
' Set the working directory to that path
objShell.CurrentDirectory = strPath
' Run the python service
objShell.Run "python win_svc.py", 0, False
