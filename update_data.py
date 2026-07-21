import tushare as ts
import json
import pandas as pd
import datetime

# 【重要】请把下面这句话改成你的Tushare令牌
ts.set_token('430c4e77854564e771625cb3cf006a93c4a6f6603693461d43c53fca') 
pro = ts.pro_api()

# ------------------ 1. 分类映射表（告诉电脑哪个ETF属于哪一类） ------------------
CATEGORY_MAP = {
    '510300': {'category': '宽基', 'tag': 'broad'},
    '588000': {'category': '宽基', 'tag': 'broad'},
    '510500': {'category': '宽基', 'tag': 'broad'},
    '512880': {'category': '行业', 'tag': 'sector'},
    '512480': {'category': '行业', 'tag': 'sector'},
    '159819': {'category': '主题', 'tag': 'theme'},
    '159995': {'category': '主题', 'tag': 'theme'},
    '513180': {'category': '跨境', 'tag': 'cross'},
    '518880': {'category': '黄金', 'tag': 'gold'},
    '159985': {'category': '商品', 'tag': 'commodity'},
    # 如果你还想添加其他ETF，照着上面这个格式，在括号里添加 "代码前6位": {'category': '分类名', 'tag': '英文标签'}
}

def get_category(code):
    prefix = code[:6]
    if prefix in CATEGORY_MAP:
        return CATEGORY_MAP[prefix]['category'], CATEGORY_MAP[prefix]['tag']
    return '宽基', 'broad'  # 不认识的就默认归为宽基

# ------------------ 2. 获取最近两个交易日的日期 ------------------
today = datetime.datetime.now().strftime('%Y%m%d')
cal = pro.trade_cal(exchange='SSE', start_date='20260101', end_date=today)
cal = cal[cal['is_open'] == 1]['cal_date'].tolist()

if len(cal) >= 2:
    trade_date = cal[-1]   # 昨天（最新交易日）
    prev_date = cal[-2]    # 前天（上一个交易日）
else:
    print("⚠️ 交易日数据不足，使用备用日期")
    trade_date = '20260720'
    prev_date = '20260717'

print(f"📅 正在对比 {trade_date} 和 {prev_date} 的数据...")

# ------------------ 3. 获取份额和净值数据 ------------------
df_today = pro.etf_share_size(trade_date=trade_date)
df_prev = pro.etf_share_size(trade_date=prev_date)

if df_today is None or df_prev is None:
    print("❌ 获取数据失败，请检查网络或Token是否正确")
    exit(1)

# 合并两天的数据，计算差值
df = pd.merge(df_today, df_prev, on='ts_code', suffixes=('', '_prev'))
df['share_change'] = df['total_share'] - df['total_share_prev']  # 份额变化（万份）
df['flow_today'] = df['share_change'] * df['nav']               # 资金净流入 = 变化 × 净值（万元）

# ------------------ 4. 整理成网页需要的格式 ------------------
result = []
for _, row in df.iterrows():
    code = row['ts_code']
    category, tag = get_category(code)
    
    item = {
        'name': row['fund_name'],
        'code': code,
        'category': category,
        'categoryTag': tag,
        'prevShares': round(float(row['total_share_prev']), 2),
        'shareChange': round(float(row['share_change']), 2),
        'nav': round(float(row['nav']), 3),
        'flow60d': 0.0,  # 近60日数据较复杂，这里先给0，以后熟练了再完善
        'flowToday': round(float(row['flow_today']), 2)
    }
    result.append(item)

# ------------------ 5. 保存为 data.json 文件 ------------------
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"✅ 大功告成！已更新 {len(result)} 只ETF的数据，保存为 data.json")