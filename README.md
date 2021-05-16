# pyFortiManagerAPI

A Python wrapper for the FortiManager REST API.
### *** Video Tutorial to use the package is available on [YouTube](https://www.youtube.com/watch?v=4o7-AYPwuSM) ***

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install pyFortiManagerAPI.

```shell script
pip install pyFortiManagerAPI
```

## Getting Started

1. Creating Instance of the Module

```python
import pyFortiManagerAPI
fortimngr = pyFortiManagerAPI.FortiManager(host="", 
                                           username="",
                                           password="")
```

Required settings:
- host: Management Ip address of your FortiManager
- username/password: Specify your credentials to log into the device.

Optional settings:
- adom: Default is adom=root.
- protocol: Default is protocol=https. If set to protocol=http, then verify=False is set automatically.
- verify: Default is verify=True. If your Fortimanager has a self-signed certificate, set verify=False.


# User Operations : Adoms
### 1) Get all adoms from the FortiManager.
```python
>>> fortimngr.get_adoms()
```
```python
>>> fortimngr.get_adoms(name="root")
```
- ## Parameters
* name: Can get specific adom using name as a filter.

### 2) Set to different Adom
```python
>>> fortimngr.set_adom("adom_name")
```
- ## Parameters
* name of the admon you want to switch to.

# User Operations : Policy Package
### 3) Get all the policy packages configured on FortiManager.
```python
>>> fortimngr.get_policy_packages()
```
```python
>>> fortimngr.get_policy_packages(name="default")
```
- ## Parameters
* name: Can get specific package using name as a filter.


### 4) Add your own policy package in FortiManager.
```python
>>> fortimngr.add_policy_package(name="TestPackage")
```
- ## Parameters
* name: Specify the Package Name.


# User Operations : Address Objects

### 5) Get all address objects from FortiManager.

```python
>>> fortimngr.get_firewall_address_objects()
```

### 6) Get specific address object from FortiManager using "name" Filter.

```python
>>> fortimngr.get_firewall_address_objects(name="YourObjectName")
```

- ## Parameters

* name: Specify object name that you want to see.

### 7) Create an address object.

```python
>>> fortimngr.add_firewall_address_object(name="TestObject",
                                          associated_interface="any",
                                          subnet=["1.1.1.1", "255.255.255.255"]
                                          )
```

- ## Parameters

* name: Specify object name that is to be created
* associated_interface: Provide interface to which this object belongs if any. {Default is kept any}
* subnet: Specify the subnet in a list format eg.["1.1.1.1", "255.255.255.255"]

### 8) Update address object.

```python
>>> fortimngr.update_firewall_address_object(name="TestObject",
                                             associate_interface="port1",
                                             comment="Updated using API",
                                             subnet=["2.2.2.2","255.255.255.255"]
                                             )
```

- ## Parameters

* name: Enter the name of the object that needs to be updated
* data: You can get the **kwargs parameters with "show_params_for_object_update()" method

### 9) Delete address object.

```python
>>> fortimngr.delete_firewall_address_object(object_name="TestObject")
```

- ## Parameters

* object_name: Specify the Object name you want to delete.

---

# User Operations : Address Groups

### 10) Get all address groups.

```python
>>> fortimngr.get_address_groups()
```

### 11) Get specific address group.

```python
>>> fortimngr.get_address_groups(name="TestGroup")
```

- ## Parameters

* name: Specify the name the address group.

### 12) Create your own address group.

```python
>>> fortimngr.add_address_group(name="Test_Group",
                                members=["TestObject1"])
```

- ## Parameters

* name: Enter the name of the address group. eg."Test_Group"
* members: pass your object names as members in a list eg. ["TestObject1", "TestObject2"]
  > Note: An address group should consist atleast 1 member.

### 13) Update the address group.

```python
>>> fortimngr.update_address_group(name="Test_Group",
                                   object_name="TestObject3",
                                   do="add")
```

- ## Parameters

* name: Specify the name of the Address group you want to update
* object_name: Specify name of the object you wish to update(add/remove) in Members List
* do: Specify if you want to add or remove the object from the members list
  do="add" will add the object in the address group
  do="remove" will remove the object from address group

### 14) Delete the address group.

```python
>>> fortimngr.delete_address_group(name="Test_group")
```

- ## Parameters

* name: Specify the name of the address group you wish to delete

---

# User Operations : Policies

### 15) Get all the policies in your Policy Package.

```python
>>> fortimngr.get_firewall_policies(policy_package_name="YourPolicyPackageName")
```

- ## Parameters

* policy_package_name: Enter the policy package name.

### 16) Get specific policiy in your Policy Package using PolicyID filter.

```python
>>> fortimngr.get_firewall_policies(policy_package_name="YourPolicyPackageName", policyid=3)
```

- ## Parameters

* policy_package_name: Enter the policy package name.
* policyid: Can filter and get the policy you want using policyID

### 17) Create your own policy in your Policy Package.

```python
>>> fortimngr.add_firewall_policy(policy_package_name="YourPolicyPackageName",
                                  name="YourPolicyName",
                                  source_interface="port1",
                                  source_address="all",
                                  destination_interface="port2",
                                  destination_address="all",
                                  service="ALL_TCP",
                                  logtraffic=2
                                  )

```

- ## Parameters

* policy_package_name: Enter the name of the policy package eg. "default"
* name: Enter the policy name in a string format eg. "Test Policy"
* source_interface: Enter the source interface in a string format eg. "port1"
* source_address: Enter the src. address object name in string format eg. "LAN_10.1.1.0_24"
* destination_interface: Enter the source interface in a string format eg. "port2"
* destination_address: Enter the dst. address object name eg. "WAN_100.25.1.63_32"
* service: Enter the service you want to permit or deny in string eg. "ALL_UDP"
* schedule: Schedule time is kept 'always' as default.
* action: Permit(1) or Deny(0) the traffic. Default is set to Permit.
* logtraffic: Specify if you need to log all traffic or specific in int format.
*                  logtraffic=0  Means No Log
                   logtraffic=1  Means Log Security Events
                   logtraffic=2  Means Log All Sessions

### 18) Update the policy in your Policy Package.

```python
>>> fortimngr.update_firewall_policy(policy_package_name="YourPolicyPackageName",
                                     policyid=10,
                                     source_interface="port2",
                                     action=1,
                                     )
```

- ## Parameters

* policy_package_name: Enter the policy package name in which you policy belongs.
* policyid: Enter the Policy ID you want to edit
* data: You can get the **kwargs parameters with "show_params_for_policy_update()" method

### 19) Delete the policy in your Policy Package.

```python
>>> fortimngr.delete_firewall_policy(policy_package_name="YourPolicyPackageName",
                                     policyid=10)
```

- ## Parameters

* policy_package_name: Enter the policy package name in which you policy belongs
* policyid: Enter the policy ID of the policy you want to delete



### 20) Move Firewall Policy.
```python
>>> fortimngr.move_firewall_policy(policy_package_name="LocalLab",
                                   move_policyid=10, 
                                   option="after", 
                                   policyid=2)
```
- ## Parameters
*  policy_package_name: Enter the policy package name in which you policy belongs.
*  move_policyid: Enter the policy ID of the policy you want to move.
*  option: Specify if you want to move the policy above("before") the target policy or below("after") {default: before}.
*  policyid: Specify the target policy.
---


# User Operations : Installing the Policy Package.

### 21) Installing the Policy Package.

```python
>>> fortimngr.install_policy_package(package_name="Your Policy Package name")

```

- ## Parameters

* package_name: Enter the package name you wish to install

---

# Show Params for updation of Policies and Objects.

### 22) Parameters for updating Address Object.
```python
>>> fortimngr.show_params_for_object_update()
```
        Parameters to create/update address object:

        PARAMETERS                   FIREWALL OBJECT SETTINGS
        allow_routing(int)          : Static Route Configuration
        associated_interface(str)   : Interface
        comment(str)                : Comments
        object_name(str)            : Address Name
        subnet[list]                : IP/Netmask
        object_type(int)            : Type
### 23) Parameters for updating Policy.
```python
>>> fortimngr.show_params_for_policy_update()
```
        Parameters to create/update Policy:

        PARAMETERS                       FIREWALL POLICY SETTINGS
        name(str)                       : Name
        source_interface(str)           : Incoming Interface
        source_address(str)             : Source Address
        destination_interface(str)      : Destination Interface
        destination_address(str)        : Destination Address
        service(str)                    : Service
        schedule(str)                   : Schedule
        action(int)                     : Action
        logtraffic(int)                 : Log Traffic
        comment(str)                    : Comments

## Future Tasks
- This module is tested on Fortimanager v6.2.2 on "root" adom. It still doesn't support multiple Adoms. So I will try to get this working for Multiple adoms too.(This task is now achieved in version v0.1)
- To update any object or firewall policies we need to pass data in Dictonary and this seems to be slightly complicated. I will try to simplify this too. (This task is now achieved in version v0.0.44) 
- To get, add, update and delete adoms, devices and interfaces.


## Contributing
- Being new to Python and this being my first publish, to get this module fully working for all of us, the Pull requests are welcome.

## License
[MIT](https://github.com/akshaymane920/pyFortiManagerAPI/blob/master/LICENSE.txt)
