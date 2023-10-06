import pickle
import requests
import json
from util import *
import qrcode
import PIL

# Base Urls
_host = "there.shu.edu.cn"
_baseurl = "https://%s/" % _host
_oauthurl = "login-oauth2"
_profileurl = "api/v3/my/profile"
_meetinfourl = "api/v2.0/meetings/%s"
_roominfourl = "api/v2.0/meeting-rooms/%s"
_roomuseinfourl = "api/v2.0/meeting-rooms/%s/meetings?start=%s&end=%s"
_roomuseinfoallurl = "api/v2.0/meeting-rooms/day-meetings?start=%s&end=%s&officeAreaId=%s&showJoinStatus=true&roomType=STATION"
_allseatsurl = "api/v2.0/settings?officeAreaId=%s&roomType=STATION"
_qrcodeurl = "http://there.shu.edu.cn/m/rooms/%s?from=qrcode&corpAppId=ww11e357f7fc0275e7"
_bookurl = "api/v3/bookings"
_checkavailable = "api/v3/booking-status/areas/%s?begin=%s&end=%s"
_recentbookurl = "api/v3/my/bookings/recent"
_cancelbookurl = "api/v3/bookings/%s/cancel"


_bookpostdata = {"rooms": [{"id": "", "name": "", "officeAreaId": "", "disabled": False,
                            "showOrder": 0, "isBusy": False, "isBooked": False, "abilities": ["booking"]}],
                 "times":[{"startDate": "", "startTime": "", "endDate": "", "endTime": ""}],
                 "subject": "", "meetingMembers": [""]}

SECTOR_ALL_ID = "7pcMcUCRxXE6fzXhLp7za7"
SECTOR_A_ID = "WyN53UzbmRsLjpR1t1ttWL"
SECTOR_B_ID = "DsNjTXf8icSMh3SXB5HPge"
SECTOR_C_ID = "YLyBwnQ7frVRt49UMSCtnX"

class NetworkError(Exception):
    pass
class InvalidBookingError(Exception):
    pass
class RecentFailCooldown(Exception):
    pass
class TooManyRequests(Exception):
    pass
class ConflictError(Exception):
    pass
class CannotBookYetError(Exception):
    pass


class SHUBooking:
    id = ""
    ownerName = ""
    ownerXgh = ""
    ownerDeptName = ""
    beginTime = ""
    endTime = ""
    checkInAt = ""
    roomId = ""
    roomName = ""
    status = ""

    def __init__(self, info):
        self.id = info["id"]
        self.ownerName = info["ownerName"]
        self.ownerXgh = info.get("ownerJobNumber", "--------")
        self.ownerDeptName = info["ownerDeptName"]
        self.beginTime = info["beginTime"]
        self.endTime = info["endTime"]
        self.checkInAt = info.get("checkInAt", "Not Checked In")
        self.roomId = info["roomId"]
        self.roomName = info["roomName"]
        self.status = info.get("statusLabel", "")

    def __str__(self):
        return "%s %s (%s~%s)" % (self.ownerXgh, self.ownerName, formattime(self.beginTime), formattime(self.endTime))


class SHU24hAPI:
    session = requests.Session()
    username = ""
    userid = ""
    displayname = ""
    roomdic = {}

    def __init__(self, *args):
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                                     })
        if len(args) == 2:
            self.__init__login(args[0], args[1])
        elif len(args) == 0:
            self.__init__session()
        else:
            raise RuntimeError("Invalid Arguments")


    def __init__login(self,username,encryptpwd):
        print("Logging in...")
        try:
            r = self.session.get(_baseurl + _oauthurl)
        except Exception as emsg:
            print(str(emsg))
            print("\nUnable to connect:(\nPlease use VPN or check network settings")

            exit(1)
        if not r.url.startswith(
                ("https://oauth.shu.edu.cn/", "https://newsso.shu.edu.cn/", _baseurl)):
            raise RuntimeError(1, f"Unexpected Result")
        request_data = {"username": username, "password": encryptpwd}
        r = self.session.post(r.url, request_data)
        if _host not in r.url:
            if "too many requests" in r.text:
                raise RuntimeError(2, f"Too many Requests, try again later")
            raise RuntimeError(2, f"Login Failed")
        else:
            print("Login Successful:" + username)
            with open('session.db', 'wb') as f:
                pickle.dump(self.session.cookies, f)
        self.username = username
        self.roomdic = self.getSeatsInSector(SECTOR_ALL_ID)

    def __init__session(self):
        with open('session.db', 'rb') as f:
            self.session.cookies.update(pickle.load(f))
        loginname,name,id = self.getLoginUserProfile()
        self.username = loginname
        print("Login Successful:" + loginname)
        self.roomdic = self.getSeatsInSector(SECTOR_ALL_ID)

    def getjson(self, url: str, headers: dict = None):
        r = self.session.get(_baseurl + url,headers=headers)
        assert r.status_code == 200
        res_json = json.loads(r.text)
        assert res_json["code"] == 0
        return res_json["data"]

    def getLoginUserProfile(self):
        info = self.getjson(_profileurl)
        self.displayname = info["name"]
        self.userid = info["id"]
        return info["loginName"], info["name"], info["id"]

    def getSeatInfo(self, seatid: str):
        info = self.getjson(_roominfourl % seatid)
        dic = {"seatId": seatid, "seatName": info["name"]}
        current = info["deviceStatus"].get("currentMeeting", None)
        upcoming = info["deviceStatus"].get("nextMeeting", None)
        currentinfo = SHUBooking(current) if current is not None else None
        upcominginfo = SHUBooking(upcoming) if upcoming is not None else None
        dic["current"] = currentinfo
        dic["upcoming"] = upcominginfo
        return dic
    
    def isseatvalid(self, seatn: str):
        return seatn in self.roomdic.keys()

    def getBookingInfo(self, meetid: str):
        info = self.getjson(_meetinfourl % meetid)
        bookinfo = SHUBooking(info)
        return bookinfo

    def getSeatsInSector(self, sectorid: str):
        info = self.getjson(_allseatsurl % sectorid)
        dic = {}
        for item in info["meetingRooms"]["currentMeetingRooms"]:
            dic[item["name"]] = {"id": item["id"], "disabled": item["disabled"]}
        return dic

    def getBookHistory(self, seatid: str, start: str, end: str):
        info = self.getjson(_roomuseinfourl % (seatid, start, end))
        return [SHUBooking(item) for item in info]
    
    def cancelBooking(self, bookid: str):
        r = self.session.delete(_baseurl + _cancelbookurl % bookid)
        assert r.status_code == 200
        res_json = json.loads(r.text)
        if res_json["code"] == 0:
            return res_json["noticeMessage"]
        else:
            return res_json["warnMessage"]
    
    def getMyRecentBookings(self):
        info = self.getjson(_recentbookurl, headers={"x-room-type": "STATION"})
        return [SHUBooking(item) for item in info]

    def getAreaMeetings(self, sectorid: str, start: str, end: str):
        info = self.getjson(_roomuseinfoallurl % (start, end, sectorid))
        dic = {}
        for item in info:
            room_name = item["name"]
            dic[room_name] = [SHUBooking(_) for _ in item.get("meetings",[])]
        return dic

    def getAvailableSeats(self, sectorid: str, start: str, end: str):
        info = self.getjson(_checkavailable % (sectorid, start, end), headers={"x-room-type": "STATION"})
        return info["rooms"]

    def bookSeat(self, seatname:str,starttime: datetime, endtime: datetime):
        data = _bookpostdata
        sector = getsectorfromseatname(seatname)
        if sector:
            sectorid = eval("SECTOR_" + sector + "_ID")
        else:
            raise InvalidBookingError("Invalid Seat Name")
        data["rooms"][0]["id"] = self.roomdic[seatname]["id"]
        data["rooms"][0]["name"] = seatname
        data["rooms"][0]["officeAreaId"] = sectorid
        data["times"][0]["startDate"] = starttime.date().isoformat()
        data["times"][0]["startTime"] = datetime.strftime(starttime, "%H:%M")
        data["times"][0]["endDate"] = endtime.date().isoformat()
        data["times"][0]["endTime"] = datetime.strftime(endtime, "%H:%M")
        data["meetingMembers"][0] = self.userid
        data["subject"] = self.displayname
        try:
            r = self.session.post(_baseurl + _bookurl, json=data)
        except Exception as emsg:
            raise NetworkError(str(emsg))
        if r.status_code != 200:
            raise NetworkError(r.status_code)
        res_json = json.loads(r.text)
        if res_json["code"] == 0:
            return True, SHUBooking(res_json["data"][0])
        else:
            if any(x in res_json["warnMessage"] for x in ["时间不能在当前时间之前","不存在的资源","超过8小时"]):
                raise InvalidBookingError(res_json["warnMessage"])
            elif "15秒内" in res_json["warnMessage"]:
                raise RecentFailCooldown(res_json["warnMessage"])
            elif "只能提交一次" in res_json["warnMessage"]:
                raise TooManyRequests(res_json["warnMessage"])
            elif "请另选时间或办公工位" in res_json["warnMessage"]:
                raise ConflictError(res_json["warnMessage"])
            elif "不能预订超过2天的预订" in res_json["warnMessage"]:
                raise CannotBookYetError(res_json["warnMessage"])
            else:
                raise RuntimeError(res_json["warnMessage"])
        # 预订结束时间不能在当前时间之前
        # 不能预订超过2天的预订
        # 您的预订与XXX发起的预订XXX(XXX~XXX)冲突，请另选时间或办公工位
        # 不存在的资源
        # 不能预订超过8小时的预订
        # 同一资源15秒内预订提交冲突，请稍后再试
        # 同一用户10秒只能提交一次

    def getQRCode(self, seatid: str):
        url = _qrcodeurl % seatid
        print(url)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        return img

