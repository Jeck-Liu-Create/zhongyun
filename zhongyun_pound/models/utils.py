import pytz
import datetime
""" 实现utc时间转本地时间 """


def UtcToLocal(utctime):
    utc_time = utctime
    local_tz = pytz.timezone('Asia/Shanghai')  # 设置本地时区
    local_time = utc_time.astimezone(local_tz)
    return local_time


def LocalToUtc(local_date):
    local_tz = pytz.timezone('Asia/Shanghai')

    # 将本地日期转换为本地日期时间
    local_datetime = local_tz.localize(datetime.datetime.combine(local_date, datetime.time.min))

    # 将本地日期时间转换为UTC日期时间
    utc_datetime = local_datetime.astimezone(pytz.utc)

    # 仅获取UTC日期部分
    utc_date = utc_datetime.date()

    return utc_date

