[Setup]
AppName=FundSellingApp
AppVersion=1.0
DefaultDirName={pf}\FundSellingApp
DefaultGroupName=FundSellingApp
OutputBaseFilename=FundSellingInstaller
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\FundSellingApp"; Filename: "{app}\Fundselling.exe"

[Run]
Filename: "{app}\Fundselling.exe"; Description: "Launch FundSellingApp"; Flags: nowait postinstall
