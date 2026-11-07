#define AppName "FX Hotkeys"
#define AppVersion "1.0.0"
#define AppExe "FXHotkeys.exe"

[Setup]
AppId={{6F1D2C54-8B7A-4E39-9A51-0C4E7B1A2D30}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={autopf}\FXHotkeys
DefaultGroupName={#AppName}
OutputDir=installer_output
OutputBaseFilename=FXHotkeys-Setup
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\{#AppExe}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
DisableProgramGroupPage=yes

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked
Name: "startup"; Description: "Start FX Hotkeys with Windows"; Flags: unchecked

[Files]
Source: "dist\FXHotkeys\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "FXHotkeys"; ValueData: """{app}\{#AppExe}"" --tray"; Flags: uninsdeletevalue; Tasks: startup

[Run]
Filename: "{app}\{#AppExe}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
