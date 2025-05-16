import threading
import time


from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

driver.get("https://flipster.io/en/trade/perpetual/BTCUSDT.PERP")

tradeCnt = None  # 거래횟수
tradeQuantity = None  # 거래수량
firstYn = True  # 시작여부
tFlag = None
vFlag = None  # 검증flag
strAmt = None  # 시작가
closeTgtLowerAmt = None  # close목표가(Lower)
closeTgtUpperAmt = None  # close목표가(Upper)
tradeTgtUpperAmt = None  # trade목표가(Upper)
tradeTgtLowerAmt = None  # trade목표가(Lower)
tradeTgtNextAmt = None  # trade목표가(Next)
buyButton = None  # 매수버튼(Long)
sellButton = None  # 매도버튼(Short)
closeAllButton = None  # CloseAll버튼
tradeQuantityInputMask = None  # 거래수량입력마스크
num = None  # 현재가


# setInterval
def set_interval(func, sec):
    global t

    def func_wrapper():
        if tFlag:
            print('tFlag')
            set_interval(func, sec)
            func()

    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

#
def getMoney():
    global driver, wait
    wait = WebDriverWait(driver, 10)

    # 로그인 버튼 클릭
    # link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Log in")))
    # link.click()

    inp = input('test')

    # 변수 초기화
    init()
    # 금액검증,주문(1초 간격)
    set_interval(chkAmtAndOrder, 1)

    # link = driver.find_element(By.LINK_TEXT, "Log in")


# 변수 초기화
def init():
    global tFlag, t, tradeCnt, tradeQuantity, firstYn, vFlag, strAmt, closeTgtLowerAmt, closeTgtUpperAmt, tradeTgtUpperAmt, tradeTgtLowerAmt, tradeTgtNextAmt, buyButton, sellButton, closeAllButton, tradeQuantityInputMask, num
    t = None
    tFlag = True
    tradeCnt = 1  # 거래횟수
    tradeQuantity = 1  # 거래수량
    firstYn = True  # 시작flag
    strAmt = None  # 시작가
    closeTgtLowerAmt = None  # close목표가(Lower)
    closeTgtUpperAmt = None  # close목표가(Upper)
    tradeTgtUpperAmt = None  # trade목표가(Upper)
    tradeTgtLowerAmt = None  # trade목표가(Lower)
    tradeTgtNextAmt = None  # trade목표가(Next)
    # buyButton              = document.querySelectorAll('.orderForm_col__XHn8r button')[0]         # 매수버튼(Long)
    buyButton = driver.find_elements(By.CSS_SELECTOR, '.orderForm_col__XHn8r button')[0]
    # sellButton             = document.querySelectorAll('.orderForm_col__XHn8r button')[1]        # 매도버튼(Short)
    sellButton = driver.find_elements(By.CSS_SELECTOR, '.orderForm_col__XHn8r button')[1]
    # closeAllButton         = document.querySelectorAll('.positionSection_header__D6TLR button')[2].click()    # CloseAll버튼
    closeAllButton = driver.find_elements(By.CSS_SELECTOR, '.positionSection_header__D6TLR button')[2]
    # tradeQuantityInputMask = document.querySelectorAll('.formItem_controlWrapper__HfJ5O input')[0]
    tradeQuantityInputMask = driver.find_elements(By.CSS_SELECTOR, '.formItem_controlWrapper__HfJ5O input')[0]
    num = None  # 현재가

    # 초기값 설정
    strAmt = getAmt()
    tradeTgtUpperAmt = strAmt
    tradeTgtLowerAmt = strAmt * (1 - (0.0005 * 1))
    closeTgtUpperAmt = strAmt * (1 + (0.0005 * 1))
    closeTgtLowerAmt = strAmt * (1 - (0.0005 * 2))
    tradeTgtNextAmt = tradeTgtLowerAmt


# 현황출력
def printConsole():
    global firstYn, num, closeTgtUpperAmt, closeTgtLowerAmt, tradeTgtUpperAmt, tradeTgtLowerAmt, tradeTgtNextAmt
    if firstYn:
        print('01.현재가 검증 시작')
        print('02.현재가 조회' + ':' + str(num))
        print('03.close목표가(upper) 조회' + ':' + str(closeTgtUpperAmt))
        print('03.close목표가(lower) 조회' + ':' + str(closeTgtLowerAmt))
        print('04.trade목표가(upper) 조회' + ':' + str(tradeTgtUpperAmt))
        print('04.trade목표가(lower) 조회' + ':' + str(tradeTgtLowerAmt))
    else:
        print('02.현재가 조회' + ':' + str(num))

    if tradeTgtNextAmt is not None:
        print('02.next목표가 조회' + ':' + str(tradeTgtNextAmt))


# 주문
def placeOrder(arg):
    global tradeQuantity, tradeQuantityInputMask, tradeCnt
    while tradeQuantityInputMask.get_attribute("value") != '0':
        tradeQuantityInputMask.send_keys(Keys.BACKSPACE)
    tradeQuantityInputMask.send_keys(str(tradeQuantity))
    buttonClick(arg)
    tradeCnt = tradeCnt + 1
    tradeQuantity = tradeQuantity * 2

# 거래주문
def buttonClick(arg):
    if arg == 'buy':
        buyButton.click()
        print('[' + str(tradeCnt) + '회차] : Buy (' + str(tradeQuantity) + ' usdt)')
    elif arg == 'sell':
        sellButton.click()
        print('[' + str(tradeCnt) + '회차] : Sell (' + str(tradeQuantity) + ' usdt)')


# 현재가 조회
def getAmt():
    global num
    num = float(driver.find_element(By.CSS_SELECTOR, '.price_price__Um1mf span').text.replace(',', ''))
    return num


# 현재가 검증 및 주문
def chkAmtAndOrder():
    global tFlag, num, closeTgtUpperAmt, closeTgtLowerAmt, tradeTgtNextAmt, tradeTgtUpperAmt, tradeTgtLowerAmt, firstYn
    printConsole()
    num = getAmt()
    if firstYn:
        placeOrder('buy')
        firstYn = False

    # close체크
    if num >= closeTgtUpperAmt or num <= closeTgtLowerAmt:
        print('09.closeAll')
        closeAllButton.click()
        # t.cancle()  # 반복중지
        tFlag = False
        time.sleep(5)
        driver.refresh()
        time.sleep(5)
        init()  # 변수 초기화
        getMoney()

    # trade체크
    if tradeTgtNextAmt is not None:
        if num >= tradeTgtNextAmt and tradeTgtNextAmt == tradeTgtUpperAmt:
            tradeTgtNextAmt = tradeTgtLowerAmt
            placeOrder('buy')
        elif num <= tradeTgtNextAmt and tradeTgtNextAmt == tradeTgtLowerAmt:
            tradeTgtNextAmt = tradeTgtUpperAmt
            placeOrder('sell')
    else:
        if num >= tradeTgtUpperAmt:
            tradeTgtNextAmt = tradeTgtLowerAmt
            placeOrder('buy')
        elif num <= tradeTgtLowerAmt:
            tradeTgtNextAmt = tradeTgtUpperAmt
            placeOrder('sell')




# 실행
getMoney()
