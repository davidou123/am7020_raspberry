#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# sim7020_nb.py
# @Author : Zack Huang ()
# @Link   : zack@atticedu.com
# @Date   : 2020/11/5 下午3:05:31

from sim7020.sim7020_modem import SIM7020Modem


class SIM7020NB(SIM7020Modem):
    def __init__(self, port, baudrate, reset_pin, dump_at_cmd=False):
        super(SIM7020NB, self).__init__(
            port, baudrate, reset_pin, dump_at_cmd)

    def setAPN(self, apn):
        # Set Default PSD Connection Settings. refer AT CMD 3.2.46
        self.sendAT("*MCGDEFCONT=\"IP\",\"", apn, "\"")
        return (self.waitResponse() == 1)

    def setBand(self, band):
        # Get and Set Mobile Operation Band. refer AT CMD 5.2.4
        self.sendAT("+CBAND=", band)
        return (self.waitResponse() == 1)

    def chkSimCard(self):
        # Enter PIN. refer AT CMD 3.2.11
        self.sendAT("+CPIN?")
        status = self.waitResponse(
            1, "READY", "SIM PIN", "SIM PUK", "NOT INSERTED", "NOT READY")
        self.waitResponse()
        return (status == 1)

    def init(self):
        self.restart()
        if(not self.testAT()):
            return False
        # Echo Off. refer AT CMD 2.2.1
        self.sendAT("E0")
        self.waitResponse()

        # Request TA Revision Identification of Software Release. refer AT CMD 3.2.4
        self.sendAT("+CGMR")
        self.waitResponse()

        # Control the Data Output Format. refer AT CMD 5.2.18
        self.sendAT("+CREVHEX=0")
        return (self.waitResponse() == 1)

    def chkNet(self):
        # EPS Network Registration Status. refer AT CMD 3.2.47
        self.sendAT("+CEREG?")
        self.waitResponse(1, "+CEREG: 0,")
        try:
            status = self.streamGetIntBefore('\r')
        except IndexError:
            return False#跳過這次迴圈，重新while一次
        self.waitResponse()
        return (status == 1)

    def nbiotConnect(self, apn, band, bs_code=0):
        if((not self.chkSimCard()) or (not self.setAPN(apn)) or (not self.setBand(band))):
            return False

        if(bs_code > 0):
            # Operator Selection. refer AT CMD 3.2.10
            self.sendAT("+COPS=1,2,\"", bs_code, "\"")
            return (self.waitResponse(120) == 1)
        return True

    def waitForNetwork(self):
        return self.chkNet()

    def ParseSubMsg(self):
        pass
