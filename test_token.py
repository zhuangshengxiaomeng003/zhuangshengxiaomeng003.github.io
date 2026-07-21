import tushare as ts

# 【重点】请把这行改成你的真实Token（不要带任何中文字）
ts.set_token('430c4e77854564e771625cb3cf006a93c4a6f6603693461d43c53fca')
pro = ts.pro_api()

# 试着拉取最简单的行情数据（1行数据）
try:
    df = pro.daily(ts_code='000001.SZ', start_date='20260701', end_date='20260720')
    if df is not None and len(df) > 0:
        print("✅ 恭喜！Token 有效，连接成功！")
    else:
        print("⚠️ Token 有效，但没有获取到数据，可能股票代码或者日期有问题")
except Exception as e:
    print(f"❌ 连接失败！错误信息：{e}")
