import base64
import rsa
from datetime import date, datetime, timedelta
from time import sleep
import random
from typing import Tuple

# SSO Pubkey
_keystr = '''-----BEGIN PUBLIC KEY-----
    MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDl/aCgRl9f/4ON9MewoVnV58OLOU2ALBi2FKc5yIsfSpivKxe7A6FitJjHva3WpM7gvVOinMehp6if2UNIkbaN+plWf5IwqEVxsNZpeixc4GsbY9dXEk3WtRjwGSyDLySzEESH/kpJVoxO7ijRYqU+2oSRwTBNePOk1H+LRQokgQIDAQAB
    -----END PUBLIC KEY-----'''


def encryptPass(passwd) -> str:
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(_keystr.encode('utf-8'))
    encryptpwd = base64.b64encode(rsa.encrypt(passwd.encode('utf-8'), pubkey)).decode()
    return encryptpwd


def formattime(time:str) -> str:
    t = datetime.strptime(time,"%Y-%m-%d %H:%M:%S")
    return date.strftime(t,"%H:%M")

def formatdatetime(dt:datetime) -> str:
    return date.strftime(dt,"%Y-%m-%d %H:%M:%S")

def dateyesterday() -> str:
    return date.strftime(date.today() - timedelta(days=1),"%Y-%m-%d")


def datenow() -> str:
    return date.strftime(date.today(),"%Y-%m-%d")


def datetomorrow():
    return date.strftime(date.today() + timedelta(days=1),"%Y-%m-%d")

def getchoice(l: int, r: int) -> int:
    while True:
        sel = input("Enter Choice[%d-%d]: " % (l, r))
        if not sel.isnumeric():
            print("Not a number!")
            continue
        if l <= int(sel) <= r:
            return int(sel)
        print("Invalid number!")


def getyesno(prompt: str) -> bool:
    while True:
        sel = input(prompt + "[Y/N]: ")
        if sel.lower() in {"y", "yes", "1"}:
            return True
        if sel.lower() in {"n", "no", "0"}:
            return False
        print("Invalid input!")


def getsector(prompt: str) -> str:
    while True:
        sel = input(prompt + ": ")
        sel.upper()
        if sel == 'A' or sel == 'B' or sel == 'C' or sel == 'ALL':
            return sel
        print("Invalid input!")

def getsectorfromseatname(seatname: str) -> str:
    try:
        s = seatname.split('-')[0]
        if s == 'A' or s == 'B' or s == 'C':
            return s
    except:
        pass
    return ''


def inputdate(prompt: str) -> str:
    while True:
        sel = input(prompt + ": ")
        try:
            datetime.strptime(sel, "%Y-%m-%d")
            return sel
        except ValueError:
            print("Invalid input!")

def inputtime(prompt: str) -> str:
    while True:
        sel = input(prompt + ": ")
        try:
            sel = '00:00' if sel == '24:00' else sel
            datetime.strptime(sel, "%H:%M")
            return sel
        except ValueError:
            print("Invalid input!")

def inputtimelength(prompt: str) -> Tuple[datetime,datetime]:
    while True:
        print(prompt+":")
        print("Choose 0 for Today, 1 for Tomorrow.")
        sel = getchoice(0,1)
        start = inputtime("Enter Start Time (eg. 08:00)")
        end = inputtime("Enter End Time (eg. 08:00)")
        res = checktimelength(start,end,sel)
        if res:
            return res
        print("Invalid time range (%s~%s)!" % (start,end))

def checktimelength(starttime: str, endtime: str, nextday: int =0) -> bool|Tuple[datetime,datetime]:
    try:
        endtime = '00:00' if endtime == '24:00' else endtime
        start = datetime.strptime(starttime, "%H:%M").time()
        end = datetime.strptime(endtime, "%H:%M").time()
        start = datetime.combine(date.today()+timedelta(days=nextday), start)
        end = datetime.combine(date.today()+timedelta(days=nextday), end)
        if endtime == '00:00':
            end = end + timedelta(days=1)
        assert start.minute == 0 or start.minute == 30
        assert end.minute == 0 or end.minute == 30
        if timedelta(minutes=30) <= end - start <= timedelta(hours=8):
            return start,end
        return False
    except:
        return False

def randomsleep():
    if random.random() < 0.02:
        sleep(1)
