# Dynamic Pairs

Dynamic pairs is the convenient way to write tests that require some comparison between different devices.

The concept of 2 similar network devices working together and providing redundancy is very common to modern networks (see VRRP, MC-LAG, EVPN Active-Active, BNG Session sync, etc.). Dynamic pairs could be used in these scenarios to compare configuration (or any other param) between the devices.


## How to define a dynamic pair

Dynamic pairs are defined under **Selector** instance (**Dynamic Pairs** field).
The main idea is to define some kind of rule which can definitely match one device with another within one Selector.

#### By Name

This mechanism relies completely on **Device Name Filter** field to form a dynamic pair.
This option can be used if you have almost similar device names inside your pair with one little difference.

Let's suppose that we have four devices:

* dsw01-a
* dsw01-b
* dsw02-a
* dsw02-b

So, we want pairs `dws01-a - dsw01-b` and `dsw02-a - dsw02-b`. To do this we have to define the following name filter: `dsw[0-9]+-([ab])`.

The key point is the round brackets. These round brackets define the variable part **inside** dynamic pair.

The whole algorithm:

1. Select a device, e.g. **asw01-a**
2. Match device against name filter and find which part of the name matches the expression inside round brackets. In our case this is `a`.
3. In `dsw01-a` swap `a` to an expression inside the brackets. Result: `dsw01-[ab]`
4. Apply the new name filter retrieved at step 3 to all the devices inside the selector.
5. Exclude our target device (dsw01-a) from the filter
6. Return the first device matching criteria. This is the dynamic pair for our target device dsw01-a. In our example this would be **dsw01-b**.


In our previous example dynamic pair members have a common part of the name inside the pair. This common part was `dsw01` for first pair and `dsw02` for the second pair.

**By name** mechanism has a drawback: it can't make dynamic pairs for devices which have no this "common part" demultiplexer.

Consider these devices:

* asw01
* asw02
* asw03
* asw04
* asw05
* asw06

If you want to make pairs asw01 - asw02, asw03 - asw04, asw05 - asw06 you can't use **By Name** mechanism.

This is where **By tag** comes to scene

#### By Tag

This way is more explicit comparing to the **By name**.
You have to tie each pair of devices with its own unique **Tag** and then specify **tag prefix** value inside the selector.

Consider the example:

* asw01 - asw02 pair
* asw03 - asw04 pair

To make dynamic pairs we have to:
* create **dp-pair1** tag and bind it to both asw01 and asw02
* create **dp-pair2** tag and bind it to both asw03 and asw04
* set **Dynamic Pair Tag Prefix** value to **dp-**. This is how selector understands which tags to consider for dynamic pairs bindings.

!!! note
    Tag prefix is just a condition to select the tags (device may have a lot of tags and most of them should not be used for dynamic pairs). You can use any value you want but **dp-** is a good default approach.


### How to check dynamic pairs
Dynamic pair values can be checked via web GUI at selector detail page, **Bound Devices** table.

Moreover, each [Test Result](../entities/results_and_reports.md) outputs the dynamic pair value.


## How to use dynamic pairs

Simply call `device.dynamic_pair` in your test expression to have access to dynamic pair.
**dynamic_pair** has all the same attributes as the device itself.

For instance, the test that checks the configuration of **Port-Channel1** is exactly the same on both devices:
```
device.config['interfaces']['Port-Channel1'] == device.dynamic_pair.config['interfaces']['Port-Channel1']
```
