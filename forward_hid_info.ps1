echo "Hardware utilization stats forwarder for Sofle RGB."
echo $PSScriptRoot
cd $PSScriptRoot
py forward_hid_info.py
pause