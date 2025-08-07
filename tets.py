# -*- coding: utf-8 -*-
import time
import re
import requests
from datetime import datetime

def get_stock_data(stock_code):
    url = f"http://hq.sinajs.cn/list=sz{stock_code}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": "http://finance.sina.com.cn"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gbk'
        if response.status_code == 200:
            data = response.text
            if 'var hq_str_sz' in data:
                stock_info = data.split('"')[1].split(',')
                if len(stock_info) >= 32:
                    stock_name = stock_info[0]
                    current_price = float(stock_info[3])
                    yesterday_close = float(stock_info[2])
                    open_price = float(stock_info[1])
                    high_price = float(stock_info[4])
                    low_price = float(stock_info[5])
                    change_amount = current_price - yesterday_close
                    change_percent = (change_amount / yesterday_close) * 100
                    return {
                        'type': 'stock',
                        'stock_code': stock_code,
                        'stock_name': stock_name,
                        'current_price': current_price,
                        'yesterday_close': yesterday_close,
                        'open_price': open_price,
                        'high_price': high_price,
                        'low_price': low_price,
                        'change_amount': change_amount,
                        'change_percent': change_percent,
                        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                else:
                    print("数据格式错误或股票代码不存在")
                    return None
            else:
                print("获取数据失败，可能是股票代码错误")
                return None
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"获取数据时出错: {e}")
        return None

def get_futures_data(futures_code):
    def safe_float(val):
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    url = f"http://hq.sinajs.cn/list=hf_{futures_code.upper()}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": "http://finance.sina.com.cn"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'gbk'
        if resp.status_code == 200:
            data = resp.text
            info = data.split('"')[1].split(',')
            if len(info) > 13:
                current_price = safe_float(info[0])
                open_price = safe_float(info[8])
                high_price = safe_float(info[4])
                low_price = safe_float(info[5])
                yesterday_close = 1#h获取不到数据
                change_amount = current_price - yesterday_close
                update_time = info[6]
                change_percent = (change_amount / yesterday_close) * 100
                futures_name = info[13] if len(info) > 13 else futures_code.upper()

                return {
                    'type': 'futures',
                    'futures_code': futures_code.upper(),
                    'futures_name': futures_name,
                    'current_price': current_price,
                    'yesterday_close': yesterday_close,
                    'open_price': open_price,
                    'high_price': high_price,
                    'low_price': low_price,
                    'change_amount': change_amount,
                    'change_percent': change_percent,
                    'update_time': update_time
                }
            else:
                print("期货数据格式异常")
                return None
        else:
            print(f"请求失败，状态码: {resp.status_code}")
            return None
    except Exception as e:
        print(f"获取期货数据时出错: {e}")
        return None

def get_data(code):
    if re.fullmatch(r'\d+', code):
        return get_stock_data(code)
    else:
        return get_futures_data(code)

def format_data(data):
    if data is None:
        return "无法获取数据"
    if data.get('type') == 'stock':
        change_symbol = "+" if data['change_amount'] >= 0 else ""
        color = "📈" if data['change_amount'] >= 0 else "📉"
        return f"""
{color} {data['stock_name']} ({data['stock_code']})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 当前价格: {data['current_price']:.3f} 元
📊 涨跌金额: {change_symbol}{data['change_amount']:.3f} 元
📈 涨跌幅度: {change_symbol}{data['change_percent']:.5f}%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 昨收价格: {data['yesterday_close']:.3f} 元
🌅 开盘价格: {data['open_price']:.3f} 元
⬆️  最高价格: {data['high_price']:.3f} 元
⬇️  最低价格: {data['low_price']:.3f} 元
🕐 更新时间: {data['update_time']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
    if data.get('type') == 'futures':
        change_symbol = "+" if data['change_amount'] >= 0 else ""
        color = "📈" if data['change_amount'] >= 0 else "📉"
        return f"""
{color} {data['futures_name']} ({data['futures_code']})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 当前价格: {data['current_price']:.3f}
📊 涨跌金额: {change_symbol}{data['change_amount']:.3f}
📈 涨跌幅度: {change_symbol}{data['change_percent']:.5f}%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 昨收价格: {data['yesterday_close']:.3f}
🌅 开盘价格: {data['open_price']:.3f}
⬆️  最高价格: {data['high_price']:.3f}
⬇️  最低价格: {data['low_price']:.3f}
🕐 更新时间: {data['update_time']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """

def monitor(code, interval=5):
    print(f"开始监控 {code}，刷新间隔 {interval} 秒")
    print("按 Ctrl+C 停止监控\n")
    try:
        while True:
            data = get_data(code)
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
            print(format_data(data))
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n监控已停止")

if __name__ == "__main__":
    code = input("请输入股票代码或期货代码（如159659或NQ）: ").strip()
    print("获取数据...")
    data = get_data(code)
    print(format_data(data))
    choice = input("\n是否开始实时监控？(y/n): ").lower()
    if choice == 'y':
        interval = input("请输入刷新间隔（秒，默认5秒）: ")
        try:
            interval = int(interval) if interval else 5
        except:
            interval = 5
        monitor(code, interval)