import time
import re
import requests
from datetime import datetime

class StockFuturesMonitor:
    def __init__(self):
        pass

    @staticmethod
    def get_stock_data(stock_code):
        # 自动判断交易所
        if stock_code.startswith(('60', '68', '90', '51', '50', '52', '56', '58')):
            exchange_prefix = 'sh'
        elif stock_code.startswith(('00', '30', '20', '15', '16', '17', '18', '12', '13', '14', '19')):
            exchange_prefix = 'sz'
        elif stock_code.startswith(('4', '8')):  # 新三板
            exchange_prefix = 'nq'  # 注意：新三板可能需要不同的API
        elif stock_code.startswith('11'):  # 可转债（上海）
            exchange_prefix = 'sh'
        elif stock_code.startswith('12'):  # 可转债（深圳）
            exchange_prefix = 'sz'
        else:
            # 默认深圳
            exchange_prefix = 'sz'

        # 新三板股票需要特殊处理
        if exchange_prefix == 'nq':
            return {'error': "暂不支持新三板股票查询"}

        url = f"http://hq.sinajs.cn/list={exchange_prefix}{stock_code}"

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
                if 'var hq_str_sz' in data or 'var hq_str_sh' in data:
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
                        return {'error': "数据格式错误或股票代码不存在"}
                else:
                    return {'error': "获取数据失败，可能是股票代码错误"}
            else:
                return {'error': f"请求失败，状态码: {response.status_code}"}
        except Exception as e:
            return {'error': f"获取数据时出错: {e}"}

    @staticmethod
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
                    yesterday_close = safe_float(info[7])
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
                    return {'error': "期货数据格式异常"}
            else:
                return {'error': f"请求失败，状态码: {resp.status_code}"}
        except Exception as e:
            return {'error': f"获取期货数据时出错: {e}"}
