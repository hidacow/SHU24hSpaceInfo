import requests
import json
from util import formattime

# Base Urls
_host = "there.shu.edu.cn"
_baseurl = "https://%s/" % _host
_oauthurl = "login-oauth2"
_profileurl = "api/v3/my/profile"
_meetinfourl = "api/v2.0/meetings/%s"
_roominfourl = "api/v2.0/meeting-rooms/%s"
_roomuseinfourl = "api/v2.0/meeting-rooms/%s/meetings?start=%s&end=%s"
_allseatsurl = "api/v2.0/settings?officeAreaId=%s&roomType=STATION"
_qrcodeurl = "http://there.shu.edu.cn/m/rooms/%s?from=qrcode&corpAppId=ww11e357f7fc0275e7"


SECTOR_ALL_ID = "7pcMcUCRxXE6fzXhLp7za7"
SECTOR_A_ID = "WyN53UzbmRsLjpR1t1ttWL"
SECTOR_B_ID = "DsNjTXf8icSMh3SXB5HPge"
SECTOR_C_ID = "YLyBwnQ7frVRt49UMSCtnX"


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
    createdAt = ""

    def __init__(self, info):
        self.id = info["id"]
        self.ownerName = info["ownerName"]
        self.ownerXgh = info.get("ownerJobNumber","--------")
        self.ownerDeptName = info["ownerDeptName"]
        self.beginTime = info["beginTime"]
        self.endTime = info["endTime"]
        self.checkInAt = info.get("checkInAt", "Not Checked In")
        self.roomId = info["roomId"]
        self.roomName = info["roomName"]
        self.createdAt = info["createdAt"]

    def __str__(self):
        return "%s %s (%s~%s)" % (self.ownerXgh,self.ownerName,formattime(self.beginTime),formattime(self.endTime))


class SHU24hAPI:
    session = requests.Session()
    username = ""
    roomsdic = {}

    def __init__(self, username, encryptpwd):
        # self.session.verify = False
        # self.session.trust_env = True
        # self.session.proxies = {
        #     "http": "http://127.0.0.1:12347",
        #     "https": "http://127.0.0.1:12347"
        # }
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
        print(r.url)
        if _host not in r.url:
            if "too many requests" in r.text:
                raise RuntimeError(2, f"Too many Requests, try again later")
            raise RuntimeError(2, f"Login Failed")
        else:
            print("Login Successful:" + username)
        self.username = username

    def getjson(self, url: str):
        r = self.session.get(_baseurl + url)
        assert r.status_code == 200
        res_json = json.loads(r.text)
        assert res_json["code"] == 0
        return res_json["data"]

    def getLoginUserProfile(self):
        info = self.getjson(_profileurl)
        return info["jobnumber"], info["name"]

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
