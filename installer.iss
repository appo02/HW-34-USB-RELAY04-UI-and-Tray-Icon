; ============================================================
; USB-RELAY04 Control Suite — Inno Setup Installer Script
; ============================================================
; Compile with Inno Setup 6+  (https://jrsoftware.org/isinfo.php)
;
; Before compiling, run:  python build_installer.py
; That produces dist/USB-RELAY04/ with all .exe and data files.
; ============================================================

#define MyAppName      "USB-RELAY04 Control Suite"
#define MyAppVersion   "1.0.0"
#define MyAppPublisher "appo02"
#define MyAppURL       "https://github.com/appo02/HW-34-USB-RELAY04-UI-and-Tray-Icon"
#define MyAppExeName   "usb_relay_hw34_gui.exe"
#define MyTrayExeName  "relay_tray.exe"
#define MyCLIExeName   "usb_relay_hw34_cli.exe"

[Setup]
AppId={{E8F3A1B2-4C5D-6E7F-8A9B-0C1D2E3F4A5B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
DefaultDirName={autopf}\USB-RELAY04
DefaultGroupName=USB-RELAY04
OutputDir=installer_output
OutputBaseFilename=USB-RELAY04_Setup_{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
SetupIconFile=
UninstallDisplayIcon={app}\{#MyAppExeName}
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
LicenseFile=
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Types]
Name: "full";    Description: "Full installation (GUI + Tray + CLI + Driver)"
Name: "compact"; Description: "Compact (GUI + Tray only)"
Name: "custom";  Description: "Custom installation"; Flags: iscustom

[Components]
Name: "main";      Description: "GUI Application";           Types: full compact custom; Flags: fixed
Name: "tray";      Description: "System Tray Quick-Control";  Types: full compact custom
Name: "cli";       Description: "Command-Line Interface";     Types: full custom
Name: "driver";    Description: "PL2303 USB-Serial Driver";   Types: full custom

[Files]
; Main GUI
Source: "dist\USB-RELAY04\usb_relay_hw34_gui.exe"; DestDir: "{app}"; Flags: ignoreversion; Components: main
; Tray app
Source: "dist\USB-RELAY04\relay_tray.exe";          DestDir: "{app}"; Flags: ignoreversion; Components: tray
; CLI
Source: "dist\USB-RELAY04\usb_relay_hw34_cli.exe";  DestDir: "{app}"; Flags: ignoreversion; Components: cli
; Config
Source: "dist\USB-RELAY04\relay_mapping.cfg";       DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist uninsneveruninstall
; Docs
Source: "dist\USB-RELAY04\README.txt";              DestDir: "{app}"; Flags: ignoreversion
; Driver
Source: "dist\USB-RELAY04\Driver\*";                DestDir: "{app}\Driver"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: driver

[Dirs]
Name: "{app}"; Permissions: users-modify

[Icons]
; Start Menu
Name: "{group}\USB-RELAY04 GUI";          Filename: "{app}\{#MyAppExeName}";  WorkingDir: "{app}"
Name: "{group}\USB-RELAY04 Tray Control"; Filename: "{app}\{#MyTrayExeName}"; WorkingDir: "{app}"; Components: tray
Name: "{group}\Configuration";            Filename: "{app}\relay_mapping.cfg"
Name: "{group}\README";                   Filename: "{app}\README.txt"
Name: "{group}\Uninstall USB-RELAY04";    Filename: "{uninstallexe}"

; Desktop
Name: "{autodesktop}\USB-RELAY04 GUI";          Filename: "{app}\{#MyAppExeName}";  WorkingDir: "{app}"; Tasks: desktopicon
Name: "{autodesktop}\USB-RELAY04 Tray Control"; Filename: "{app}\{#MyTrayExeName}"; WorkingDir: "{app}"; Tasks: desktopicon; Components: tray

[Tasks]
Name: "desktopicon";    Description: "Create desktop shortcuts";                         GroupDescription: "Additional shortcuts:"
Name: "startup_tray";   Description: "Start Tray Control automatically on Windows login"; GroupDescription: "Startup:"; Components: tray

[Run]
; Launch GUI after install
Filename: "{app}\{#MyAppExeName}"; Description: "Launch USB-RELAY04 GUI"; Flags: nowait postinstall skipifsilent
; Launch tray after install
Filename: "{app}\{#MyTrayExeName}"; Description: "Launch Tray Control"; Flags: nowait postinstall skipifsilent unchecked; Components: tray

[Registry]
; Auto-start tray on login (only if user checked the task)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "USB-RELAY04-Tray"; ValueData: """{app}\{#MyTrayExeName}"""; Flags: uninsdeletevalue; Tasks: startup_tray

[UninstallRun]
; Kill tray app before uninstall
Filename: "taskkill.exe"; Parameters: "/F /IM relay_tray.exe"; Flags: runhidden; RunOnceId: "KillTray"

[UninstallDelete]
Type: files; Name: "{app}\*.log"

[Code]
// Show a post-install note about driver installation
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if WizardIsComponentSelected('driver') then
    begin
      MsgBox(
        'The PL2303 USB-Serial driver has been copied to:' + #13#10 +
        ExpandConstant('{app}\Driver') + #13#10#13#10 +
        'If you have not installed it yet, please navigate there and ' +
        'run the installer as Administrator before using the relay.',
        mbInformation, MB_OK
      );
    end;
  end;
end;
