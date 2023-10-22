import datetime, time
import yaml

from StockTradeAppliation.message import Message
from StockTradeAppliation.model import Stock_trade, Token

# 1. config.yaml 파일 읽기
with open('config.yaml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)

APP_KEY = _cfg['APP_KEY']
APP_SECRET = _cfg['APP_SECRET']
ACCESS_TOKEN = ""
CANO = _cfg['CANO']
ACNT_PRDT_CD = _cfg['ACNT_PRDT_CD']
URL_BASE = _cfg['URL_BASE']


# 프로그램 시작
try:
    ACCESS_TOKEN = Token.get_access_token()

    # 매수 희망 종목
    symbol_list = ["005930","035720","000660","069500"]
    # 매수 완료한 종목 리스트
    bought_list = []

    # 현재 보유한 현금 - 조회하기
    total_cash = Stock_trade.get_balance()
    Message.send_message(f"주문 가능 현금 잔고: {total_cash}원")
    
    # 현재 보유한 주식 - 조회하기
    stock_dict = Stock_trade.get_stock_balance()

    for sym in stock_dict.keys():
        bought_list.append(sym)

    target_buy_count = 3 # 매수할 종목 수
    buy_percent = 0.33 # 종목당 매수 금액 비율
    buy_amount = total_cash * buy_percent  # 종목별 주문 금액 계산
    soldout = False


    """
        자동 매매 시작 
        0. [프로그램 시작 전 - 사전 작업]
            - 주말에는 자동 종료
            - 장이 시작하기 전 ; 잔여 수량은 전부 매도
        1. [매수]
        2. [일괄 매도] 
        3. [프로그램 종료] PM 03:20
    """
    Message.send_message("===[Program init]====================")
    while True:
        time_now = datetime.datetime.now()

        time_9 = time_now.replace(hour=9, minute=0, second=0, microsecond=0)
        time_start = time_now.replace(hour=9, minute=5, second=0, microsecond=0)
        time_sell = time_now.replace(hour=15, minute=15, second=0, microsecond=0)
        time_exit = time_now.replace(hour=15, minute=20, second=0,microsecond=0)
        today = datetime.datetime.today().weekday()

        # The program was shut down on the weekend.
        if today == 5 or today == 6:
            Message.send_message("===[Program Was Shut Down]====================")
            break

        # 0. [시작 전 사전 작업]
        # 잔여 수량 매도 - 남은 수량은 전부 판매
        if time_9 < time_now < time_start and soldout == False:
            for sym, qty in stock_dict.items():
                Stock_trade.sell(sym,qty)
            soldout = True
            bought_list = []
            stock_dict = Stock_trade.get_stock_balance()

        # 1. [매수 시작] AM 09:05 ~ PM 03:15
        if time_start < time_now < time_sell:
            for sym in symbol_list:
                if len(bought_list) < target_buy_count:
                    if sym in bought_list:
                        continue
                    target_price = Stock_trade.get_target_price(sym)
                    current_price = Stock_trade.get_current_price(sym)
                    if target_price < current_price:
                        buy_qty = 0  # 매수할 수량 초기화
                        buy_qty = int(buy_amount // current_price)
                        if buy_qty > 0:
                            Message.send_message(f"{sym} 목표가 달성({target_price} < {current_price}) 매수를 시도합니다.")
                            result = Stock_trade.buy(sym, buy_qty)
                            if result:
                                soldout = False
                                bought_list.append(sym)
                                Stock_trade.get_stock_balance()
                    time.sleep(1)
            time.sleep(1)
            if time_now.minute == 30 and time_now.second <= 5:
                Stock_trade.get_stock_balance()
                time.sleep(5)

        # 2. [일괄 매도] PM 03:15 ~ PM 03:20
        if time_sell < time_now < time_exit:
            if soldout == False:
                stock_dict = Stock_trade.get_stock_balance()
                for sym, qty in stock_dict.items():
                    Stock_trade.sell(sym, qty)
                soldout = True
                bought_list = []
                time.sleep(1)
        # [프로그램 종료] PM 03:20
        if time_exit < time_now:
            Message.send_message("===[Program Was Shut Down]====================")
            break

except Exception as e:
    Message.send_message(f"[오류] {e}")
    time.sleep(1)