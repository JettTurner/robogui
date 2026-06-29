; InbetweenAnimation RoboGUI Installer Script

[Setup]
AppId={{B3C9D2A1-8F11-4A2C-9B11-00AABBCCDDEE}
AppName=InbetweenAnimation RoboGUI
AppVersion=1.0.2
AppPublisher=InbetweenAnimation
AppPublisherURL=https://inbetweenanimation.com
AppSupportURL=https://inbetweenanimation.com
AppUpdatesURL=https://inbetweenanimation.com

DefaultDirName={autopf}\InbetweenAnimation\RoboGUI
DefaultGroupName=InbetweenAnimation
UninstallDisplayIcon={app}\ROBOGUI.exe
OutputDir=dist
OutputBaseFilename=InbetweenAnimation_RoboGUI_Installer
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=icon\robogui.ico
PrivilegesRequired=admin

[Files]
Source: "dist\ROBOGUI.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\InbetweenAnimation RoboGUI"; Filename: "{app}\ROBOGUI.exe"
Name: "{userdesktop}\RoboGUI"; Filename: "{app}\ROBOGUI.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\ROBOGUI.exe"; Description: "Launch RoboGUI"; Flags: nowait postinstall skipifsilent