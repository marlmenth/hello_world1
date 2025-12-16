$exePath = "$env:USERPROFILE\Downloads\test_exec.exe"

$source = @"
using System;
using System.Runtime.InteropServices;

namespace Native
{
    public class ProcessApi
    {
        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
        public struct STARTUPINFO
        {
            public int cb;
            public string lpReserved;
            public string lpDesktop;
            public string lpTitle;
            public int dwX;
            public int dwY;
            public int dwXSize;
            public int dwYSize;
            public int dwXCountChars;
            public int dwYCountChars;
            public int dwFillAttribute;
            public int dwFlags;
            public short wShowWindow;
            public short cbReserved2;
            public IntPtr lpReserved2;
            public IntPtr hStdInput;
            public IntPtr hStdOutput;
            public IntPtr hStdError;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct PROCESS_INFORMATION
        {
            public IntPtr hProcess;
            public IntPtr hThread;
            public uint dwProcessId;
            public uint dwThreadId;
        }

        [DllImport("kernel32.dll",
            EntryPoint = "CreateProcessW",
            SetLastError = true,
            CharSet = CharSet.Unicode)]
        public static extern bool CreateProcess(
            string lpApplicationName,
            string lpCommandLine,
            IntPtr lpProcessAttributes,
            IntPtr lpThreadAttributes,
            bool bInheritHandles,
            uint dwCreationFlags,
            IntPtr lpEnvironment,
            string lpCurrentDirectory,
            ref STARTUPINFO lpStartupInfo,
            out PROCESS_INFORMATION lpProcessInformation
        );
    }
}
"@

# Load type only once
if (-not ("Native.ProcessApi" -as [type])) {
    Add-Type -TypeDefinition $source
}

$CREATE_PRESERVE_CODE_AUTHZ_LEVEL = 0x02000000

$si = New-Object Native.ProcessApi+STARTUPINFO
$si.cb = [Runtime.InteropServices.Marshal]::SizeOf($si)

$pi = New-Object Native.ProcessApi+PROCESS_INFORMATION

$result = [Native.ProcessApi]::CreateProcess(
    $exePath,
    $null,
    [IntPtr]::Zero,
    [IntPtr]::Zero,
    $false,
    $CREATE_PRESERVE_CODE_AUTHZ_LEVEL,
    [IntPtr]::Zero,
    (Split-Path $exePath),
    [ref]$si,
    [ref]$pi
)

if ($result) {
    Write-Host "calc.exe launched successfully (PID: $($pi.dwProcessId))"
} else {
    $err = [Runtime.InteropServices.Marshal]::GetLastWin32Error()
    Write-Error "CreateProcess failed. Win32 error: $err"
}
