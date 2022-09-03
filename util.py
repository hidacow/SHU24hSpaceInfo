import base64
import rsa
from datetime import date, datetime, timedelta
from time import sleep
import random

# SSO Pubkey
_keystr = '''-----BEGIN PUBLIC KEY-----
    MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDl/aCgRl9f/4ON9MewoVnV58OLOU2ALBi2FKc5yIsfSpivKxe7A6FitJjHva3WpM7gvVOinMehp6if2UNIkbaN+plWf5IwqEVxsNZpeixc4GsbY9dXEk3WtRjwGSyDLySzEESH/kpJVoxO7ijRYqU+2oSRwTBNePOk1H+LRQokgQIDAQAB
    -----END PUBLIC KEY-----'''


def encryptPass(passwd):
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(_keystr.encode('utf-8'))
    encryptpwd = base64.b64encode(rsa.encrypt(passwd.encode('utf-8'), pubkey)).decode()
    return encryptpwd


def formattime(time:str):
    t = datetime.strptime(time,"%Y-%m-%d %H:%M:%S")
    return date.strftime(t,"%H:%M")


def dateyesterday():
    return date.strftime(date.today() - timedelta(days=1),"%Y-%m-%d")


def datenow():
    return date.strftime(date.today(),"%Y-%m-%d")


def datetomorrow():
    return date.strftime(date.today() + timedelta(days=1),"%Y-%m-%d")


def printmainmenu():
    print("--------------------")
    print("1. Enter seat number and see its status")
    print("2. Select a sector and list status of all seats")
    print("3. Enter seat number and see recent and upcoming bookings")
    print("4. Check Booking History of a seat")
    print("--------------------")
    print("0. Exit")
    print()


def getchoice(l: int, r: int) -> int:
    while True:
        sel = input("Enter Choice[%d-%d]:" % (l, r))
        if not sel.isnumeric():
            print("Not a number!")
            continue
        if l <= int(sel) <= r:
            return int(sel)
        print("Invalid number!")


def getyesno(prompt: str) -> bool:
    while True:
        sel = input(prompt + "[Y/N]:")
        if sel.lower() in {"y", "yes", "1"}:
            return True
        if sel.lower() in {"n", "no", "0"}:
            return False
        print("Invalid input!")


def getsector(prompt: str) -> str:
    while True:
        sel = input(prompt + ":")
        sel.upper()
        if sel == 'A' or sel == 'B' or sel == 'C' or sel == 'ALL':
            return sel
        print("Invalid input!")


def getdate(prompt: str) -> str:
    while True:
        sel = input(prompt + ":")
        try:
            datetime.strptime(sel, "%Y-%m-%d")
            return sel
        except ValueError:
            print("Invalid input!")

def randomsleep():
    if random.random() < 0.35:
        sleep(1)
