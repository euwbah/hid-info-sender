<# 
If (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))
{
  # Relaunch as an elevated process:
  Start-Process powershell.exe "-File",('"{0}"' -f (($MyInvocation.PSCommandPath)+$PSCommandPath)) -Verb RunAs
  exit
}
#>

echo "Hardware utilization stats forwarder for Sofle RGB."
echo "Starting in dir: $PSScriptRoot"
cd $PSScriptRoot
py forward_hid_info.py
