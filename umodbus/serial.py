#!/usr/bin/env python
#
# Copyright (c) 2019, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#

# system packages
from digitalio import DigitalInOut, Direction
from busio import UART
    
import struct
from . import time_ex

# custom packages
from . import const as Const
from . import functions
from .common import Request, CommonModbusFunctions
from .common import ModbusException
from .modbus import Modbus

# typing not natively supported on MicroPython
from .typing import List, Optional, Union


class ModbusRTU(Modbus):
    """
    Modbus RTU client class

    :param      tx_pin:           The tx pin
    :type       tx_pin:           int
    :param      rx_pin:           The rx pin
    :type       rx_pin:           int
    :param      addr:             The address of this device on the bus
    :type       addr:             int
    :param      baudrate:         The baudrate, default 9600
    :type       baudrate:         int
    :param      data_bits:        The data bits, default 8
    :type       data_bits:        int
    :param      stop_bits:        The stop bits, default 1
    :type       stop_bits:        int
    :param      parity:           The parity, default None
    :type       parity:           Optional[int]
    :param      de_not_re_pin:    The control pin
    :type       de_not_re_pin:    int
    :param      re_de_delay:    
    :type       re_de_delay:      int
    :param      de_re_delay:
    :type       de_re_delay:      int
    """
    def __init__(self,
                 tx_pin: int = None,
                 rx_pin: int = None,
                 addr: int = 1,
                 baudrate: int = 9600,
                 data_bits: int = 8,
                 stop_bits: int = 1,
                 parity: Optional[int] = None,
                 de_not_re_pin: int = None,
                 re_de_delay: int = 200,
                 de_re_delay: int = 100):
        super().__init__(
            # set itf to Serial object, addr_list to [addr]
            Serial(tx_pin=tx_pin,
                   rx_pin=rx_pin,
                   baudrate=baudrate,
                   data_bits=data_bits,
                   stop_bits=stop_bits,
                   parity=parity,
                   de_not_re_pin=de_not_re_pin,
                   re_de_delay=re_de_delay,
                   de_re_delay=de_re_delay),                   
            [addr]
        )


class Serial(CommonModbusFunctions):
    def __init__(self,
                 tx_pin: int = None,
                 rx_pin: int = None,
                 baudrate: int = 9600,
                 data_bits: int = 8,
                 stop_bits: int = 1,
                 parity=None,
                 de_not_re_pin: int = None,
                 re_de_delay: int = 200,
                 de_re_delay: int = 100):
        """
        Setup Serial/RTU Modbus

        :param      tx_pin:           The tx pin
        :type       tx_pin:           int
        :param      rx_pin:           The rx pin
        :type       rx_pin:           int
        :param      baudrate:         The baudrate, default 9600
        :type       baudrate:         int
        :param      data_bits:        The data bits, default 8
        :type       data_bits:        int
        :param      stop_bits:        The stop bits, default 1
        :type       stop_bits:        int
        :param      parity:           The parity, default None
        :type       parity:           Optional[int]
        :param      de_not_re_pin:    The control pin
        :type       de_not_re_pin:    int
        :param      re_de_delay:    
        :type       re_de_delay:      int
        :param      de_re_delay:
        :type       de_re_delay:      int        
        """
        self._uart = UART(tx=tx_pin,
                          rx=rx_pin,
                          rs485_dir= de_not_re_pin if de_not_re_pin is not None and (re_de_delay is None and de_re_delay is None) else None,
                          rs485_invert=False,
                          baudrate=baudrate,
                          bits=data_bits,
                          parity=parity,
                          stop=stop_bits)
                     
        self._re_de_delay = re_de_delay
        self._de_re_delay = de_re_delay
        
        if de_not_re_pin is None or (re_de_delay is None and de_re_delay is None):
            self._de_not_re_pin = None
        else:
            self._de_not_re_pin = DigitalInOut(de_not_re_pin)
            self._de_not_re_pin.switch_to_output()
            self._de_not_re_pin.value = False
            
        # timing of 1 character in microseconds (us)
        self._t1char = 1000000 * (data_bits + stop_bits + 2) // baudrate

        # inter-frame delay in microseconds (us)
        # - <= 19200 bps: 3.5x timing of 1 character
        # - > 19200 bps: 1750 us
        if baudrate <= 19200:
            self._inter_frame_delay = 3500 * self._t1char / 1000
        else:
            self._inter_frame_delay = 1750

    def _calculate_crc16(self, data: bytearray) -> bytes:
        """
        Calculates the CRC16.

        :param      data:        The data
        :type       data:        bytearray

        :returns:   The crc 16.
        :rtype:     bytes
        """
        crc = 0xFFFF

        for char in data:
            crc = (crc >> 8) ^ Const.CRC16_TABLE[((crc) ^ char) & 0xFF]

        return struct.pack('<H', crc)

    def _exit_read(self, response: bytearray) -> bool:
        """
        Return on modbus read error

        :param      response:    The response
        :type       response:    bytearray

        :returns:   State of basic read response evaluation,
                    True if entire response has been read
        :rtype:     bool
        """
        response_len = len(response)
        if response_len >= 2 and response[1] >= Const.ERROR_BIAS:
            if response_len < Const.ERROR_RESP_LEN:
                return False
        elif response_len >= 3 and (Const.READ_COILS <= response[1] <= Const.READ_INPUT_REGISTER):
            expected_len = Const.RESPONSE_HDR_LENGTH + 1 + response[2] + Const.CRC_LENGTH
            if response_len < expected_len:
                return False
        elif response_len < Const.FIXED_RESP_LEN:
            return False

        return True

    def _uart_read(self, response_timeout: int = 1) -> bytearray:
        """
        Read incoming slave response from UART

        :returns:   Read content
        :rtype:     bytearray
        """
        response = bytearray()
                  
        # first byte with response_timeout
        self._uart.timeout = response_timeout
        
        r = self._uart.read(1)  # read / wait for first
        if r is not None:
            # append the new read stuff to the buffer
            response.extend(r)
            
            # next byte's with inter_frame_delay
            self._uart.timeout = self._inter_frame_delay / 1e6  # in seconds
            r = self._uart.read()  # read / wait for next
            if r is not None:
                response.extend(r)
            
        return response

    def _uart_read_frame(self, timeout: Optional[int] = None) -> bytearray:
        """
        Read a Modbus frame

        :param      timeout:  The timeout
        :type       timeout:  Optional[int]

        :returns:   Received message
        :rtype:     bytearray
        """
        received_bytes = bytearray()
        
        # set default timeout to at twice the inter-frame delay
        if timeout == 0 or timeout is None:
            timeout = 2 * self._inter_frame_delay / 1e6  # in seconds
        self._uart.timeout = timeout
        
        r = self._uart.read(1)  # read / wait for first byte
        if r is not None:
            # append the new read stuff to the buffer
            received_bytes.extend(r)
            
            # next byte's with frame_timeout
            self._uart.timeout = self._inter_frame_delay / 1e6  # in seconds
            r = self._uart.read()  # read / wait for next byte's
            if r is not None:
                received_bytes.extend(r)

        return received_bytes


    def _send(self, modbus_pdu: bytes, slave_addr: int) -> None:
        """
        Send Modbus frame via UART

        If a flow control pin has been setup, it will be controlled accordingly

        :param      modbus_pdu:  The modbus Protocol Data Unit
        :type       modbus_pdu:  bytes
        :param      slave_addr:  The slave address
        :type       slave_addr:  int
        """
        # modbus_adu: Modbus Application Data Unit
        # consists of the Modbus PDU, with slave address prepended and checksum appended
        modbus_adu = bytearray()
        modbus_adu.append(slave_addr)
        modbus_adu.extend(modbus_pdu)
        modbus_adu.extend(self._calculate_crc16(modbus_adu))

        if self._de_not_re_pin is not None:
            self._de_not_re_pin.value = True
            # wait until the control pin really changed
            # 85-95us (ESP32 @ 160/240MHz)
            time_ex.sleep_us(self._re_de_delay)
            
        # the timing of this part is critical:
        # - if we disable output too early,
        #   the command will not be received in full
        # - if we disable output too late,
        #   the incoming response will lose some data at the beginning
        # easiest to just wait for the bytes to be sent out on the wire

        send_start_time = time_ex.ticks_us()
        # 360-400us @ 9600-115200 baud (measured) (ESP32 @ 160/240MHz)
        self._uart.write(modbus_adu)

        if self._de_not_re_pin is not None:
            sleep_time_us = self._t1char * len(modbus_adu) + self._de_re_delay # total frame time in us + de_re_delay
            sleep_time_us -= time_ex.ticks_us() - send_start_time
            if sleep_time_us > 0:
                time_ex.sleep_us(sleep_time_us)
            self._de_not_re_pin.value = False


    def _send_receive(self,
                      modbus_pdu: bytes,
                      slave_addr: int,
                      count: bool) -> bytes:
        """
        Send a modbus message and receive the reponse.

        :param      modbus_pdu:  The modbus Protocol Data Unit
        :type       modbus_pdu:  bytes
        :param      slave_addr:  The slave address
        :type       slave_addr:  int
        :param      count:       The count
        :type       count:       bool

        :returns:   Validated response content
        :rtype:     bytes
        """
        # flush the Rx FIFO buffer
        self._uart.read()

        self._send(modbus_pdu=modbus_pdu, slave_addr=slave_addr)

        return self._validate_resp_hdr(response=self._uart_read(),
                                       slave_addr=slave_addr,
                                       function_code=modbus_pdu[0],
                                       count=count)

    def _validate_resp_hdr(self,
                           response: bytearray,
                           slave_addr: int,
                           function_code: int,
                           count: bool) -> bytes:
        """
        Validate the response header.

        :param      response:       The response
        :type       response:       bytearray
        :param      slave_addr:     The slave address
        :type       slave_addr:     int
        :param      function_code:  The function code
        :type       function_code:  int
        :param      count:          The count
        :type       count:          bool

        :returns:   Modbus response content
        :rtype:     bytes
        """
        if len(response) == 0:
            raise OSError('no data received from slave')

        resp_crc = response[-Const.CRC_LENGTH:]
        expected_crc = self._calculate_crc16(
            response[0:len(response) - Const.CRC_LENGTH]
        )

        if ((resp_crc[0] is not expected_crc[0]) or
                (resp_crc[1] is not expected_crc[1])):
            raise OSError('invalid response CRC')

        if (response[0] != slave_addr):
            raise ValueError('wrong slave address')

        if (response[1] == (function_code + Const.ERROR_BIAS)):
            raise ValueError('slave returned exception code: {:d}'.
                             format(response[2]))

        hdr_length = (Const.RESPONSE_HDR_LENGTH + 1) if count else \
            Const.RESPONSE_HDR_LENGTH

        return response[hdr_length:len(response) - Const.CRC_LENGTH]

    def send_response(self,
                      slave_addr: int,
                      function_code: int,
                      request_register_addr: int,
                      request_register_qty: int,
                      request_data: list,
                      values: Optional[list] = None,
                      signed: bool = True) -> None:
        """
        Send a response to a client.

        :param      slave_addr:             The slave address
        :type       slave_addr:             int
        :param      function_code:          The function code
        :type       function_code:          int
        :param      request_register_addr:  The request register address
        :type       request_register_addr:  int
        :param      request_register_qty:   The request register qty
        :type       request_register_qty:   int
        :param      request_data:           The request data
        :type       request_data:           list
        :param      values:                 The values
        :type       values:                 Optional[list]
        :param      signed:                 Indicates if signed
        :type       signed:                 bool
        """
        modbus_pdu = functions.response(
            function_code=function_code,
            request_register_addr=request_register_addr,
            request_register_qty=request_register_qty,
            request_data=request_data,
            value_list=values,
            signed=signed
        )
        self._send(modbus_pdu=modbus_pdu, slave_addr=slave_addr)

    def send_exception_response(self,
                                slave_addr: int,
                                function_code: int,
                                exception_code: int) -> None:
        """
        Send an exception response to a client.

        :param      slave_addr:      The slave address
        :type       slave_addr:      int
        :param      function_code:   The function code
        :type       function_code:   int
        :param      exception_code:  The exception code
        :type       exception_code:  int
        """
        modbus_pdu = functions.exception_response(
            function_code=function_code,
            exception_code=exception_code)
        self._send(modbus_pdu=modbus_pdu, slave_addr=slave_addr)

    def get_request(self,
                    unit_addr_list: List[int],
                    timeout: Optional[int] = None) -> Union[Request, None]:
        """
        Check for request within the specified timeout

        :param      unit_addr_list:  The unit address list
        :type       unit_addr_list:  Optional[list]
        :param      timeout:         The timeout
        :type       timeout:         Optional[int]

        :returns:   A request object or None.
        :rtype:     Union[Request, None]
        """
        req = self._uart_read_frame(timeout=timeout)

        if len(req) < 8:
            return None

        if req[0] not in unit_addr_list:
            return None

        req_crc = req[-Const.CRC_LENGTH:]
        req_no_crc = req[:-Const.CRC_LENGTH]
        expected_crc = self._calculate_crc16(req_no_crc)

        if (req_crc[0] != expected_crc[0]) or (req_crc[1] != expected_crc[1]):
            return None

        try:
            request = Request(interface=self, data=req_no_crc)
        except ModbusException as e:
            self.send_exception_response(
                slave_addr=req[0],
                function_code=e.function_code,
                exception_code=e.exception_code)
            return None

        return request


