import requests
import json
import time
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

def format_stock_data(data):
    """格式化输出股票数据"""
    if data is None:
        return "无法获取股票数据"
    
    change_symbol = "+" if data['change_amount'] >= 0 else ""
    color = "📈" if data['change_amount'] >= 0 else "📉"
    
    return f"""
{color} {data['stock_name']} ({data['stock_code']})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 当前价格: {data['current_price']:.5f} 元
📊 涨跌金额: {change_symbol}{data['change_amount']:.5f} 元
📈 涨跌幅度: {change_symbol}{data['change_percent']:.5f}%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 昨收价格: {data['yesterday_close']:.5f} 元
🌅 开盘价格: {data['open_price']:.5f} 元
⬆️  最高价格: {data['high_price']:.5f} 元
⬇️  最低价格: {data['low_price']:.5f} 元
🕐 更新时间: {data['update_time']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """

def monitor_stock(stock_code, interval=5):
    """
    实时监控股票价格
    stock_code: 股票代码
    interval: 刷新间隔（秒）
    """
    print(f"开始监控股票 {stock_code}，刷新间隔 {interval} 秒")
    print("按 Ctrl+C 停止监控\n")
    
    try:
        while True:
            data = get_stock_data(stock_code)
            
            # 清屏（Windows）
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print(format_stock_data(data))
            
            # 等待指定时间
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n监控已停止")

if __name__ == "__main__":
    stock_code = "159659"  # 股票代码
    
    # 获取单次数据
    print("获取股票数据...")
    data = get_stock_data(stock_code)
    print(format_stock_data(data))
    
    # 询问是否开始实时监控
    choice = input("\n是否开始实时监控？(y/n): ").lower()
    if choice == 'y':
        interval = input("请输入刷新间隔（秒，默认5秒）: ")
        try:
            interval = int(interval) if interval else 5
        except:
            interval = 5
        
        monitor_stock(stock_code, interval)