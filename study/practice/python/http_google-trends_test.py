from pytrends.request import TrendReq

pytrend = TrendReq(hl="ko", tz=540)
pytrend.build_payload(["SaaS"], timeframe="today 1-m")

df = pytrend.interest_over_time()
print(df)