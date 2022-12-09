#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
modbus script
"""

# system packages
import time

# custom packages

# typing not natively supported on MicroPython
from .typing import List, Optional
from .typing import Union
from .typing import dict_keys


class Modbus(object):
    def __init__(self, itf, addr_list: list):
        self._itf = itf
        self._addr_list = addr_list

        # modbus register types with their default value
        self._available_register_types = ['COILS', 'HREGS', 'IREGS', 'ISTS']
        self._register_dict = dict()
        for reg_type in self._available_register_types:
            self._register_dict[reg_type] = dict()
        self._default_vals = dict(zip(self._available_register_types,
                                      [False, 0, 0, False]))

        # registers which can be set by remote device
        self._changeable_register_types = ['COILS', 'HREGS']
        self._changed_registers = dict()
        for reg_type in self._changeable_register_types:
            self._changed_registers[reg_type] = dict()

    def add_coil(self,
                 address: int,
                 value: Union[bool, List[bool]] = False) -> None:
        """
        Add a coil to the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    Union[bool, List[bool]], optional
        """
        self._set_reg_in_dict(reg_type='COILS',
                              address=address,
                              value=value)

    def remove_coil(self, address: int) -> Union[None, bool, List[bool]]:
        """
        Remove a coil from the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int

        :returns:   Register value, None if register did not exist in dict
        :rtype:     Union[None, bool, List[bool]]
        """
        return self._remove_reg_from_dict(reg_type='COILS', address=address)

    def set_coil(self,
                 address: int,
                 value: Union[bool, List[bool]] = False) -> None:
        """
        Set the coil value.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    Union[bool, List[bool]], optional
        """
        self._set_reg_in_dict(reg_type='COILS',
                              address=address,
                              value=value)

    def get_coil(self, address: int) -> Union[bool, List[bool]]:
        """
        Get the coil value.

        :param      address:  The address (ID) of the register
        :type       address:  bool

        :returns:   Coil value
        :rtype:     Union[bool, List[bool]]
        """
        return self._get_reg_in_dict(reg_type='COILS',
                                     address=address)

    @property
    def coils(self) -> dict_keys:
        """
        Get the configured coils.

        :returns:   The dictionary keys.
        :rtype:     dict_keys
        """
        return self._get_regs_of_dict(reg_type='COILS')

    def add_hreg(self, address: int, value: Union[int, List[int]] = 0) -> None:
        """
        Add a holding register to the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    Union[int, List[int]], optional
        """
        self._set_reg_in_dict(reg_type='HREGS',
                              address=address,
                              value=value)

    def remove_hreg(self, address: int) -> Union[None, int, List[int]]:
        """
        Remove a holding register from the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int

        :returns:   Register value, None if register did not exist in dict
        :rtype:     Union[None, int, List[int]]
        """
        return self._remove_reg_from_dict(reg_type='HREGS', address=address)

    def set_hreg(self, address: int, value: Union[int, List[int]] = 0) -> None:
        """
        Set the holding register value.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    int or list of int, optional
        """
        self._set_reg_in_dict(reg_type='HREGS',
                              address=address,
                              value=value)

    def get_hreg(self, address: int) -> Union[int, List[int]]:
        """
        Get the holding register value.

        :param      address:  The address (ID) of the register
        :type       address:  int

        :returns:   Holding register value
        :rtype:     Union[int, List[int]]
        """
        return self._get_reg_in_dict(reg_type='HREGS',
                                     address=address)

    @property
    def hregs(self) -> dict_keys:
        """
        Get the configured holding registers.

        :returns:   The dictionary keys.
        :rtype:     dict_keys
        """
        return self._get_regs_of_dict(reg_type='HREGS')

    def add_ist(self,
                address: int,
                value: Union[bool, List[bool]] = False) -> None:
        """
        Add a discrete input register to the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    bool or list of bool, optional
        """
        self._set_reg_in_dict(reg_type='ISTS',
                              address=address,
                              value=value)

    def remove_ist(self, address: int) -> Union[None, bool, List[bool]]:
        """
        Remove a holding register from the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int

        :returns:   Register value, None if register did not exist in dict
        :rtype:     Union[None, bool, List[bool]]
        """
        return self._remove_reg_from_dict(reg_type='ISTS', address=address)

    def set_ist(self, address: int, value: bool = False) -> None:
        """
        Set the discrete input register value.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    bool or list of bool, optional
        """
        self._set_reg_in_dict(reg_type='ISTS',
                              address=address,
                              value=value)

    def get_ist(self, address: int) -> Union[bool, List[bool]]:
        """
        Get the discrete input register value.

        :param      address:  The address (ID) of the register
        :type       address:  int

        :returns:   Discrete input register value
        :rtype:     Union[bool, List[bool]]
        """
        return self._get_reg_in_dict(reg_type='ISTS',
                                     address=address)

    @property
    def ists(self) -> dict_keys:
        """
        Get the configured discrete input registers.

        :returns:   The dictionary keys.
        :rtype:     dict_keys
        """
        return self._get_regs_of_dict(reg_type='ISTS')

    def add_ireg(self, address: int, value: Union[int, List[int]] = 0) -> None:
        """
        Add an input register to the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    Union[int, List[int]], optional
        """
        self._set_reg_in_dict(reg_type='IREGS',
                              address=address,
                              value=value)

    def remove_ireg(self, address: int) -> Union[None, int, List[int]]:
        """
        Remove an input register from the modbus register dictionary.

        :param      address:  The address (ID) of the register
        :type       address:  int

        :returns:   Register value, None if register did not exist in dict
        :rtype:     Union[None, int, List[int]]
        """
        return self._remove_reg_from_dict(reg_type='IREGS', address=address)

    def set_ireg(self, address: int, value: Union[int, List[int]] = 0) -> None:
        """
        Set the input register value.

        :param      address:  The address (ID) of the register
        :type       address:  int
        :param      value:    The default value
        :type       value:    Union[int, List[int]], optional
        """
        self._set_reg_in_dict(reg_type='IREGS',
                              address=address,
                              value=value)

    def get_ireg(self, address: int) -> Union[int, List[int]]:
        """
        Get the input register value.

        :param      address:  The address (ID) of the register
        :type       address:  int

        :returns:   Input register value
        :rtype:     Union[int, List[int]]
        """
        return self._get_reg_in_dict(reg_type='IREGS',
                                     address=address)

    @property
    def iregs(self) -> dict_keys:
        """
        Get the configured input registers.

        :returns:   The dictionary keys.
        :rtype:     dict_keys
        """
        return self._get_regs_of_dict(reg_type='IREGS')

    def _set_reg_in_dict(self,
                         reg_type: str,
                         address: int,
                         value: Union[bool, int, List[bool], List[int]]) -> None:
        """
        Set the register value in the dictionary of registers.

        :param      reg_type:  The register type
        :type       reg_type:  str
        :param      address:   The address (ID) of the register
        :type       address:   int
        :param      value:     The default value
        :type       value:     Union[bool, int, List[bool], List[int]]

        :raise      KeyError:  No register at specified address found
        :returns:   Register value
        :rtype:     Union[bool, int, List[bool], List[int]]
        """
        if not self._check_valid_register(reg_type=reg_type):
            raise KeyError('{} is not a valid register type of {}'.
                           format(reg_type, self._available_register_types))

        self._register_dict[reg_type][address] = value

    def _remove_reg_from_dict(self,
                              reg_type: str,
                              address: int) -> Union[None, bool, int, List[bool], List[int]]:
        """
        Remove the register from the dictionary of registers.

        :param      reg_type:  The register type
        :type       reg_type:  str
        :param      address:   The address (ID) of the register
        :type       address:   int

        :raise      KeyError:  No register at specified address found
        :returns:   Register value, None if register did not exist in dict
        :rtype:     Union[None, bool, int, List[bool], List[int]]
        """
        if not self._check_valid_register(reg_type=reg_type):
            raise KeyError('{} is not a valid register type of {}'.
                           format(reg_type, self._available_register_types))

        return self._register_dict[reg_type].pop(address, None)

    def _get_reg_in_dict(self,
                         reg_type: str,
                         address: int) -> Union[bool, int, List[bool], List[int]]:
        """
        Get the register value from the dictionary of registers.

        :param      reg_type:  The register type
        :type       reg_type:  str
        :param      address:   The address (ID) of the register
        :type       address:   int

        :raise      KeyError:  No register at specified address found
        :returns:   Register value
        :rtype:     Union[bool, int, List[bool], List[int]]
        """
        if not self._check_valid_register(reg_type=reg_type):
            raise KeyError('{} is not a valid register type of {}'.
                           format(reg_type, self._available_register_types))

        if address in self._register_dict[reg_type]:
            return self._register_dict[reg_type][address]
        else:
            raise KeyError('No {} available for the register address {}'.
                           format(reg_type, address))

    def _get_regs_of_dict(self, reg_type: str) -> dict_keys:
        """
        Get all configured registers of specified register type.

        :param      reg_type:  The register type
        :type       reg_type:  str

        :raise      KeyError:  No register at specified address found
        :returns:   The configured registers of the specified register type.
        :rtype:     dict_keys
        """
        if not self._check_valid_register(reg_type=reg_type):
            raise KeyError('{} is not a valid register type of {}'.
                           format(reg_type, self._available_register_types))

        return self._register_dict[reg_type].keys()

    def _check_valid_register(self, reg_type: str) -> bool:
        """
        Check register type to be a valid modbus register

        :param      reg_type:  The register type
        :type       reg_type:  str

        :returns:   Flag whether register type is valid
        :rtype:     bool
        """
        if reg_type in self._available_register_types:
            return True
        else:
            return False

    @property
    def changed_registers(self) -> dict:
        """
        Get the changed registers.

        :returns:   The changed registers.
        :rtype:     dict
        """
        return self._changed_registers

    @property
    def changed_coils(self) -> dict:
        """
        Get the changed coil registers.

        :returns:   The changed coil registers.
        :rtype:     dict
        """
        return self._changed_registers['COILS']

    @property
    def changed_hregs(self) -> dict:
        """
        Get the changed holding registers.

        :returns:   The changed holding registers.
        :rtype:     dict
        """
        return self._changed_registers['HREGS']

    def _set_changed_register(self,
                              reg_type: str,
                              address: int,
                              value: Union[bool, int, List[bool], List[int]]) -> None:
        """
        Set the register value in the dictionary of changed registers.

        :param      reg_type:  The register type
        :type       reg_type:  str
        :param      address:   The address (ID) of the register
        :type       address:   int
        :param      value:     The value
        :type       value:     Union[bool, int, List[bool], List[int]]

        :raise      KeyError:  Register can not be changed externally
        """
        if reg_type in self._changeable_register_types:
            content = {'val': value, 'time': time.ticks_ms()}
            self._changed_registers[reg_type][address] = content
        else:
            raise KeyError('{} can not be changed externally'.format(reg_type))

    def _remove_changed_register(self,
                                 reg_type: str,
                                 address: int,
                                 timestamp: int) -> bool:
        """
        Remove the register from the dictionary of changed registers.

        :param      reg_type:  The register type
        :type       reg_type:  str
        :param      address:   The address (ID) of the register
        :type       address:   int
        :param      timestamp: The timestamp of the change in milliseconds
        :type       timestamp: int

        :raise      KeyError:  No register at specified address found
        :returns:   Result of removing register from dict
        :rtype:     bool
        """
        result = False

        if reg_type in self._changeable_register_types:
            _changed_register_timestamp = self._changed_registers[reg_type][address]['time']

            if _changed_register_timestamp == timestamp:
                self._changed_registers[reg_type].pop(address, None)
                result = True
        else:
            raise KeyError('{} is not a valid register type of {}'.
                           format(reg_type, self._changeable_register_types))

        return result

    def setup_registers(self,
                        registers: dict = dict(),
                        use_default_vals: Optional[bool] = False) -> None:
        """
        Setup all registers of the client

        :param      registers:         The registers
        :type       registers:         dict
        :param      use_default_vals:  Flag to use dummy default values
        :type       use_default_vals:  Optional[bool]
        """
        if len(registers):
            for reg_type, default_val in self._default_vals.items():
                if reg_type in registers:
                    for reg, val in registers[reg_type].items():
                        address = val['register']

                        if use_default_vals:
                            if 'len' in val:
                                value = [default_val] * val['len']
                            else:
                                value = default_val
                        else:
                            value = val['val']

                        if reg_type == 'COILS':
                            self.add_coil(address=address,
                                          value=value)
                        elif reg_type == 'HREGS':
                            self.add_hreg(address=address,
                                          value=value)
                        elif reg_type == 'ISTS':
                            self.add_ist(address=address,
                                         value=value)
                        elif reg_type == 'IREGS':
                            self.add_ireg(address=address,
                                          value=value)
                        else:
                            # invalid register type
                            pass
                else:
                    pass
