import pandas as pd

dates = ["Jul 10 2026", "31/07/2026", "8 july", "2026-08-19"]
times = ["10:37 PM", "07:30 PM", "11:59 AM", "12:05 PM"]

for d in dates:
    print(f"Date: {d} -> {pd.to_datetime(d)}")
    
for t in times:
    print(f"Time: {t} -> {pd.to_datetime('2000-01-01 ' + t)}")
