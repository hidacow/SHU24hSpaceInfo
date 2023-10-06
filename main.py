import getpass
from util import *
from apis import *


# If you run in Jetbrains IDE,
# Go to 'Edit Configurations' and then select 'Emulate terminal in output console'.

# Settings
VER = "1.1"
MENUS = [
    "Enter seat number and see its status",
    "Select a sector and list status of all seats",
    "Enter seat number and see recent and upcoming bookings",
    "Check Booking History of a seat",
    "Check Empty seats in a sector",
    "Reserve a seat",
    "See my recent reservations",
    "Cancel my reservation"
]

def printmainmenu():
    print("--------------------")
    for i in range(len(MENUS)):
        print("%d. %s" % (i+1, MENUS[i]))
    print("--------------------")
    print("0. Exit")
    print()
    return getchoice(0, len(MENUS))

if __name__ == '__main__':
    print("SHU24hSpaceInfoChecker V" + VER)
    print()
    try:
        api = SHU24hAPI()
    except Exception as e:
        username = input("User:")
        password = getpass.getpass("Password:")
        api = SHU24hAPI(username, encryptPass(password))
    
    #img = api.getQRCode(api.roomdic["C-045"]["id"])
    #img.show()
    
    def getseatnum(prompt: str) -> str:
        while True:
            sel = input(prompt + ":")
            if api.isseatvalid(sel):
                return sel
            print("Invalid input or not exist!")

    while True:
        sel = printmainmenu()
        if sel == 0:
            exit(0)
        if sel == 1:
            seatnum = getseatnum("Please Enter Seat Number")
            if api.roomdic[seatnum]["disabled"]:
                print("Sorry, Seat %s is disabled by admin." % seatnum)
            else:
                seat = api.getSeatInfo(api.roomdic[seatnum]["id"])
                print(api.roomdic[seatnum]["id"])
                print(seat["seatName"], seat["current"], seat["upcoming"], sep='\t')
        if sel == 2:
            sector = getsector("Please Enter [A/B/C/ALL]")
            print("Choose 0 for Today, 1 for Tomorrow.")
            cho = getchoice(0, 1)
            if cho == 0:
                data = api.getAreaMeetings(eval("SECTOR_" + sector + "_ID"), datenow(), datenow())
            else:
                data = api.getAreaMeetings(eval("SECTOR_" + sector + "_ID"), datetomorrow(), datetomorrow())
            for room_name, meetings in data.items():
                print(room_name + ":")
                for meeting in meetings:
                    print("\t"+str(meeting))
            # if sector == "ALL":
            #     seats = api.roomdic
            # else:
            #     seats = api.getSeatsInSector(eval("SECTOR_" + sector + "_ID"))
            # for seat in seats.values():
            #     if seat["disabled"]:
            #         continue
            #     randomsleep()
            #     seat = api.getSeatInfo(seat["id"])
            #     print(seat["seatName"], seat["current"], seat["upcoming"], sep='\t')
        if sel == 3:
            seatnum = getseatnum("Please Enter Seat Number")
            if api.roomdic[seatnum]["disabled"]:
                print("Sorry, Seat %s is disabled by admin." % seatnum)
            else:
                history = api.getBookHistory(api.roomdic[seatnum]["id"], datenow(), datetomorrow())
                print(seatnum)
                for booking in history:
                    print("%s %s (%s~%s)" % (booking.ownerXgh,booking.ownerName,booking.beginTime,booking.endTime))
        if sel == 4:
            seatnum = getseatnum("Please Enter Seat Number")
            startdate = inputdate("Please Enter Start Date")
            enddate = inputdate("Please Enter End Date")
            if api.roomdic[seatnum]["disabled"]:
                print("Sorry, Seat %s is disabled by admin." % seatnum)
            else:
                history = api.getBookHistory(api.roomdic[seatnum]["id"], startdate, enddate)
                print(seatnum)
                for booking in history:
                    print("%s %s (%s~%s)" % (booking.ownerXgh,booking.ownerName,booking.beginTime,booking.endTime))
        if sel == 5:
            sector = getsector("Please Enter [A/B/C/ALL]")
            start,end = inputtimelength("Please Enter Time Range")
            if sector == "ALL":
                data = api.getAvailableSeats(SECTOR_A_ID, formatdatetime(start), formatdatetime(end))
                data += api.getAvailableSeats(SECTOR_B_ID, formatdatetime(start), formatdatetime(end))
                data += api.getAvailableSeats(SECTOR_C_ID, formatdatetime(start), formatdatetime(end))
            else:
                data = api.getAvailableSeats(eval("SECTOR_" + sector + "_ID"), formatdatetime(start), formatdatetime(end))
            print()
            print("Empty Seats in Sector %s in time range %s ~ %s:" % (sector,formatdatetime(start), formatdatetime(end)))
            for seat in data:
                if not seat["isBooked"] and not seat["disabled"]:
                    print(seat["name"])
        if sel == 6:
            seatnum = getseatnum("Please Enter Seat Number")
            start,end = inputtimelength("Please Enter Time Range")
            print("Is this correct?")
            print("Seat: %s" % seatnum)
            print("Time: %s ~ %s" % (formatdatetime(start), formatdatetime(end)))
            if not getyesno("Confirm"):
                continue
            print()
            try:
                data = api.bookSeat(seatnum, start, end)
            except Exception as e:
                print("Falied due to: %s" % type(e).__name__)
                data = e
            print(data)
        if sel == 7:
            data = api.getMyRecentBookings()
            for booking in data:
                print(booking.beginTime[:11],booking.roomName,booking,booking.status,booking.id)
        if sel == 8:
            id = input("Please Enter Booking ID: ")
            print(api.cancelBooking(id))

        print()
