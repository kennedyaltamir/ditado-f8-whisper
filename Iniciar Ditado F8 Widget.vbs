Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

PythonExe = "C:\Users\Kennedy Oliveira\AppData\Local\Programs\Python\Python310\pythonw.exe"
ScriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
AppScript = FSO.BuildPath(ScriptDir, "ditado_f8_app.py")
Command = """" & PythonExe & """ """ & AppScript & """"

WshShell.Run Command, 0, False