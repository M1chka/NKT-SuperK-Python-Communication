# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 10:53:47 2017

@author: Michail Vlassov
@company: Single Quantum
"""
import serial
import struct
import binascii
import numpy as np


######FUNCTIONS#########
def crcsplit(decarray): #Finds lowest and highest crc from data and converts it to a hex string, also decimal array to hex string#
    import crcmod
    xmodem_crc_func = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0x0000, xorOut=0x0000)
    for idx, val in enumerate(decarray):
        decarray[idx]=format(decarray[idx],'x')
        if len(decarray[idx])==1:
            decarray[idx]='0%s'%decarray[idx]
        decarray[idx]=decarray[idx].upper()
    outputcrc=xmodem_crc_func(binascii.unhexlify("".join(decarray)))
    arrayout="".join(decarray)
    crc=tuple([ ord(x) for x in struct.pack('<H',outputcrc)])
    hi=format(crc[1],'x').upper()
    lo=format(crc[0],'x').upper()
    return hi,lo,arrayout

def longtoarray(value): #Converts a Long value to a decimal array#
    tup=tuple([ ord(x) for x in struct.pack('<L',value)])
    X=np.asarray(tup)
    X=np.ma.masked_equal(X,0)
    X=X.compressed()
    X=X.tolist()
    return X

def strtoarray(string): #Converts a string value to a decimal array#
    tup=tuple([ ord(x) for x in struct.pack('%ss'%len(string),string)])
    X=np.asarray(tup)
    X=np.ma.masked_equal(X,0)
    X=X.compressed()
    X=X.tolist()
    return X

def readorwrite(write): #Makes telegram value for writing or reading#
    if write == 1:
        rdorwrt=5
    else:
        rdorwrt=4 
    return rdorwrt

def readline(a_serial, eol=binascii.unhexlify("0A")): #Reads respons until 0A value#
    leneol = len(eol)
    line = bytearray()
    while True:
        c = a_serial.read(1)
        if c:
            line += c
            if line[-leneol:] == eol:
                break
        else:
            break
    return bytes(line)

def mail_to_array(mail): #converts ASCII string to readable HEX string array#
    telegram=binascii.hexlify(mail)
    telegramar=[telegram[i:i+2] for i in range(0,len(telegram),2)]
    del telegramar[-1]
    del telegramar[0]
    return telegramar

def str_or_long(n): #sends string or long#
    if n==1:
        return strtoarray(stringval)
    else:
        return longtoarray(longval)

######FUNCTIONS#########

    
###read settings###
port='COM13'    #USB port##
Dest=15         #Destination adress##
Reg="30"        #Registry adress (Hex)##
src=162         #Source number ##
write=1         #Do you want to read or write?, 1=write, 0=read##
longval=3         #Long Value#
stringval="hey"    #String Value#
stringon=0      #Do you want to send a string or a long? , 0=long, 1=string##
####################


##Put all data in an array###
Data=[Dest,src,readorwrite(write),int(Reg, 16)]+str_or_long(stringon)
#Finding highest and lowest 16bit crc and building data string##
high,low,arrayout =crcsplit(Data)
print("Find lowest and highest crc")
#Building a ASCII telegram string from all data and##
print("Building telegram")
Telegram=binascii.unhexlify("".join(["0D","%s"%(arrayout),"%s"%(high),"%s"%(low),"0A"]))
print(binascii.hexlify(Telegram))
print("Telegram build!")
#Setting up Connection to Laser#
print("Connecting to SuperK Extreme")
ser = serial.Serial(port, 115200,parity=serial.PARITY_NONE, rtscts=1,bytesize=8,stopbits=serial.STOPBITS_ONE)
ser.timeout=50
print("Connected")
#Sending the ASCII telegram to the laser#
print("Sending Telegram")
ser.write(Telegram)
#Receiving respons ASCII string#
print("Waiting for a respons")
mail=readline(ser)
print("Telegram Received!")
#closing connection to laser#
print("Closing Conversation")
ser.close()   
print("Closed")
#converting telegram string to readable Hex array#
telegramar=mail_to_array(mail)
print(telegramar)