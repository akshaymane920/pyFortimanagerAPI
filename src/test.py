import pyFortiManagerAPI

fortimgr = pyFortiManagerAPI.FortiManager(host="fortimanager.zaxbys.com",username="zaxapi",password="gFJqbQ2hiiWrLNb33vM",adom="root",verify=False)

print(fortimgr.get_script_output("ZAX-ORC01-FW01", "Corp_Stores"))
