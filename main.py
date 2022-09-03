import getpass
from util import *
from apis import *


# If you run in Jetbrains IDE,
# Go to 'Edit Configurations' and then select 'Emulate terminal in output console'.

# Settings
VER = "1.0.0"

if __name__ == '__main__':
    print("SHU24hSpaceInfoChecker V" + VER)
    print()
    username = input("User:")
    password = getpass.getpass("Password:")
    api = SHU24hAPI(username, encryptPass(password))
    roomdic = api.getSeatsInSector(SECTOR_ALL_ID)


    def isseatvalid(seatn: str):
        return seatn in roomdic.keys()


    def getseatnum(prompt: str) -> str:
        while True:
            sel = input(prompt + ":")
            if isseatvalid(sel):
                return sel
            print("Invalid input or not exist!")

    while True:
        printmainmenu()
        sel = getchoice(0, 4)
        if sel == 0:
            exit(0)
        if sel == 1:
            seatnum = getseatnum("Please Enter Seat Number")
            if roomdic[seatnum]["disabled"]:
                print("Sorry, Seat %s is disabled by admin." % seatnum)
            else:
                seat = api.getSeatInfo(roomdic[seatnum]["id"])
                print(seat["seatName"], seat["current"], seat["upcoming"], sep='\t')
        if sel == 2:
            sector = getsector("Please Enter [A/B/C/ALL]")
            if sector == "ALL":
                seats = roomdic
            else:
                seats = api.getSeatsInSector(eval("SECTOR_" + sector + "_ID"))
            for seat in seats.values():
                if seat["disabled"]:
                    continue
                randomsleep()
                seat = api.getSeatInfo(seat["id"])
                print(seat["seatName"], seat["current"], seat["upcoming"], sep='\t')
        if sel == 3:
            seatnum = getseatnum("Please Enter Seat Number")
            if roomdic[seatnum]["disabled"]:
                print("Sorry, Seat %s is disabled by admin." % seatnum)
            else:
                history = api.getBookHistory(roomdic[seatnum]["id"], datenow(), datetomorrow())
                print(seatnum)
                for booking in history:
                    print("%s %s (%s~%s)" % (booking.ownerXgh,booking.ownerName,booking.beginTime,booking.endTime))
        if sel == 4:
            seatnum = getseatnum("Please Enter Seat Number")
            startdate = getdate("Please Enter Start Date")
            enddate = getdate("Please Enter End Date")
            if roomdic[seatnum]["disabled"]:
                print("Sorry, Seat %s is disabled by admin." % seatnum)
            else:
                history = api.getBookHistory(roomdic[seatnum]["id"], startdate, enddate)
                print(seatnum)
                for booking in history:
                    print("%s %s (%s~%s)" % (booking.ownerXgh,booking.ownerName,booking.beginTime,booking.endTime))

