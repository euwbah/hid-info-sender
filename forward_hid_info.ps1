echo "Hardware utilization stats forwarder for Sofle RGB."
echo "Starting in dir: $PSScriptRoot"
cd $PSScriptRoot
py forward_hid_info.py
pause