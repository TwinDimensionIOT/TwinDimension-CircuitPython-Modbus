# CircuitPython Modbus library

[![Discord](https://img.shields.io/discord/1016500444379496478)](https://discord.com/channels/1016500444379496478)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?logo=linkedin&logoColor=white)](https://www.linkedin.com/company/twindimension)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

CircuitPython ModBus TCP and RTU library supporting client and host mode

>ToDo
>* general cleanup (project divergence / micropython incompatibility)
>* update test cases
>* update docs
>* ...
---------------

## General

Forked from [micropython-modbus][ref-brainelectronics-micropython-modbus], based on
[PyCom Modbus][ref-pycom-modbus] and extended with other functionalities to
become a powerfull MicroPython library

📚 The latest documentation is available at
[MicroPython Modbus ReadTheDocs][ref-rtd-micropython-modbus] 📚

<!-- MarkdownTOC -->

- [Quickstart](#quickstart)
    - [Install package on board with mip or upip](#install-package-on-board-with-mip-or-upip)
    - [Request coil status](#request-coil-status)
        - [TCP](#tcp)
        - [RTU](#rtu)
    - [Install additional MicroPython packages](#install-additional-micropython-packages)
- [Usage](#usage)
- [Supported Modbus functions](#supported-modbus-functions)
- [Credits](#credits)

<!-- /MarkdownTOC -->

## Quickstart

This is a quickstart to install the `micropython-modbus` library on a
MicroPython board.

A more detailed guide of the development environment can be found in
[SETUP](SETUP.md), further details about the usage can be found in
[USAGE](USAGE.md), descriptions for testing can be found in
[TESTING](TESTING.md) and several examples in [EXAMPLES](EXAMPLES.md)

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install 'rshell>=0.0.30,<1.0.0'
pip install 'mpremote>=0.4.0,<1'
```

### Install package on board with mip or upip

```bash
rshell -p /dev/tty.SLAB_USBtoUART --editor nano
```

Inside the [rshell][ref-remote-upy-shell] open a REPL and execute these
commands inside the REPL

```python
import machine
import network
import time
import mip
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect('SSID', 'PASSWORD')
time.sleep(1)
print('Device connected to network: {}'.format(station.isconnected()))
mip.install('github:brainelectronics/micropython-modbus')
print('Installation completed')
machine.soft_reset()
```

For MicroPython versions below 1.19.1 use the `upip` package instead of `mip`

```python
import machine
import network
import time
import upip
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect('SSID', 'PASSWORD')
time.sleep(1)
print('Device connected to network: {}'.format(station.isconnected()))
upip.install('micropython-modbus')
print('Installation completed')
machine.soft_reset()
```

### Request coil status

After a successful installation of the package and reboot of the system as
described in the [installation section](#install-package-on-board-with-pip)
the following commands can be used to request a coil state of a target/client
device. Further usage examples can be found in the
[examples folder][ref-examples-folder] and in the [USAGE chapter](USAGE.md)

#### TCP

```python
from ummodbus.tcp import ModbusTCPMaster

tcp_device = ModbusTCPMaster(
    slave_ip='172.24.0.2',  # IP address of the target/client/slave device
    slave_port=502,         # TCP port of the target/client/slave device
    # timeout=5.0           # optional, timeout in seconds, default 5.0
)

# address of the target/client/slave device on the bus
slave_addr = 10
coil_address = 123
coil_qty = 1

coil_status = host.read_coils(
    slave_addr=slave_addr,
    starting_addr=coil_address,
    coil_qty=coil_qty)
print('Status of coil {}: {}'.format(coil_status, coil_address))
```

For further details check the latest
[MicroPython Modbus TCP documentation example][ref-latest-tcp-docs-example]

#### RTU

```python
from umodbus.serial import Serial as ModbusRTUMaster

host = ModbusRTUMaster(
    pins=(25, 26),      # given as tuple (TX, RX), check MicroPython port specific syntax
    # baudrate=9600,    # optional, default 9600
    # data_bits=8,      # optional, default 8
    # stop_bits=1,      # optional, default 1
    # parity=None,      # optional, default None
    # ctrl_pin=12,      # optional, control DE/RE
    # uart_id=1         # optional, see port specific documentation
)

# address of the target/client/slave device on the bus
slave_addr = 10
coil_address = 123
coil_qty = 1

coil_status = host.read_coils(
    slave_addr=slave_addr,
    starting_addr=coil_address,
    coil_qty=coil_qty)
print('Status of coil {}: {}'.format(coil_address, coil_status))
```

For further details check the latest
[MicroPython Modbus RTU documentation example][ref-latest-rtu-docs-example]

### Install additional MicroPython packages

To use this package with the provided [`boot.py`][ref-package-boot-file] and
[`main.py`][ref-package-boot-file] file, additional modules are required,
which are not part of this repo/package. To install these modules on the
device, connect to a network and install them via `upip` as follows

```python
# with MicroPython version 1.19.1 or newer
import mip
mip.install('github:brainelectronics/micropython-modules')

# before MicroPython version 1.19.1
import upip
upip.install('micropython-brainelectronics-helpers')
```

Check also the README of the
[brainelectronics MicroPython modules][ref-github-be-mircopython-modules], the
[INSTALLATION](INSTALLATION.md) and the [SETUP](SETUP.md) guides.

## Usage

See [USAGE](USAGE.md) and [DOCUMENTATION](DOCUMENTATION.md)

## Supported Modbus functions

Refer to the following table for the list of supported Modbus functions.

| ID | Description |
|----|-------------|
| 1  | Read coils |
| 2  | Read discrete inputs |
| 3  | Read holding registers |
| 4  | Read input registers |
| 5  | Write single coil |
| 6  | Write single register |
| 15 | Write multiple coils |
| 16 | Write multiple registers |

## Credits

Big thank you to [giampiero7][ref-giampiero7] for the initial implementation
of this library.

* **sfera-labs** - *Initial work* - [giampiero7][ref-sferalabs-exo-sense]
* **pycom** - *Initial Modbus work* - [pycom-modbus][ref-pycom-modbus]
* **pfalcon** - *Initial MicroPython unittest module* - [micropython-unittest][ref-pfalcon-unittest]

<!-- Links -->
[ref-brainelectronics-micropython-modbus]: https://github.com/brainelectronics/micropython-modbus
[ref-sferalabs-exo-sense]: https://github.com/sfera-labs/exo-sense-py-modbus
[ref-pycom-modbus]: https://github.com/pycom/pycom-modbus
[ref-rtd-micropython-modbus]: https://micropython-modbus.readthedocs.io/en/latest/
[ref-remote-upy-shell]: https://github.com/dhylands/rshell
[ref-examples-folder]: https://github.com/brainelectronics/micropython-modbus/tree/develop/examples
[ref-latest-rtu-docs-example]: https://micropython-modbus.readthedocs.io/en/latest/EXAMPLES.html#rtu
[ref-latest-tcp-docs-example]: https://micropython-modbus.readthedocs.io/en/latest/EXAMPLES.html#tcp
[ref-package-boot-file]: https://github.com/brainelectronics/micropython-modbus/blob/c45d6cc334b4adf0e0ffd9152c8f08724e1902d9/boot.py
[ref-package-main-file]: https://github.com/brainelectronics/micropython-modbus/blob/c45d6cc334b4adf0e0ffd9152c8f08724e1902d9/main.py
[ref-github-be-mircopython-modules]: https://github.com/brainelectronics/micropython-modules
[ref-giampiero7]: https://github.com/giampiero7
[ref-pfalcon-unittest]: https://github.com/pfalcon/pycopy-lib/blob/56ebf2110f3caa63a3785d439ce49b11e13c75c0/unittest/unittest.py
