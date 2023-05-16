import pytz

""" 实现utc时间转本地时间 """


def UtcToLocal(utctime):
    utc_time = utctime
    local_tz = pytz.timezone('Asia/Shanghai')  # 设置本地时区
    local_time = utc_time.astimezone(local_tz)
    return local_time
