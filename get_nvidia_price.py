"""
Fetch NVIDIA stock data from Yahoo Finance.

Install dependency if needed:
    pip install yfinance pandas
"""

from __future__ import annotations

import yfinance as yf #주가 검색 라이브러리
import requests #외부 사이트 크롤링
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
# %matplotlib inline


# Get Nowdays NVDA info
def get_nvidia_quote() -> dict:
    ticker = yf.Ticker("NVDA") #ticker.info로 해당 주식의 정보 확인 가능(주소, 기업소개, ir공시 사이트, 직원수, 임원 명단 등)
    history = ticker.history(period="5d", interval="1d")

    if history.empty:
        raise RuntimeError("No price data returned from Yahoo Finance.")

    latest = history.tail(1).iloc[0]
    return {
        "symbol": "NVDA",
        "date": history.tail(1).index[0].strftime("%Y-%m-%d"),
        "open": float(latest["Open"]),
        "high": float(latest["High"]),
        "low": float(latest["Low"]),
        "close": float(latest["Close"]),
        "volume": int(latest["Volume"]),
    }
def get_nvidia_data(month) -> pd.DataFrame:
    # month = float(input('Enter the month what you want to get the Ticker data (ex: 5): '))
    end_date = datetime.now()

    start_date = end_date - timedelta(days = 30*month)
    end_date = end_date.strftime("%Y-%m-%d")
    start_data = start_date.strftime("%Y-%m-%d")
    df = yf.download(yf.Ticker(input('Enter the Ticker you want to get the data (ex: NVDA): ')).info['symbol'], start=start_date, end=end_date, interval='1d').sort_index(ascending=True)
    # 2. 이동평균선(SMA) 및 볼린저 밴드 계산
    period = 30  # 기준 기간 (보통 20일을 가장 많이 씁니다)

    # 20일 이동평균선 (볼린저 밴드의 중심선이 됩니다)
    df['MA30'] = df['Close'].rolling(window=period).mean()

    # 20일 표준편차 계산
    df['STD30'] = df['Close'].rolling(window=period).std()

    # 상단 밴드 = 중심선 + (표준편차 * 2)
    df['Upper_Band'] = df['MA30'] + (df['STD30'] * 2)

    # 하단 밴드 = 중심선 - (표준편차 * 2)
    df['Lower_Band'] = df['MA30'] - (df['STD30'] * 2)
    df = df.reset_index()
    df.to_excel('nvidia_price.xlsx', index=False)  # Save to Excel
    return df

def get_datacenter_ppi(month) -> pd.DataFrame:
    # 1. 발급받은 API 키와 기본 설정
    API_KEY = "d874b2f1619ba63e84f9cd9929f1512393941f2a"
    # 인구조사국 건설 지출(VIP) API 엔드포인트
    BASE_URL = "https://api.census.gov/data/timeseries/eits/vip"

    # 2. 파라미터 설정 (데이터 항목 및 기간)
    # 예: 데이터 및 시리즈 코드, 카테고리 설정
    # 1. 현재 날짜 기준으로 지난 5개월의 'YYYY-MMM' 리스트 생성
    
    current_date = datetime.now()
    time_list = []

    for i in range(month+4): #입력값 + 4해야 5개월치 데이터 가져올 수 있음
        # 현재부터 1개월씩 과거로 이동 (0개월 전, 1개월 전, 2개월 전...)
        past_month = current_date - timedelta(days = 30*i)
        # Census API 형식인 'YYYY-M00' 형태로 포맷팅
        time_str = past_month.strftime("%Y-%m")
        time_list.append(time_str)
    params = {
        # "get": "category_code,data_type_code,seasonally_adj,cell_value,time",
        "get": "category_code,data_type_code,seasonally_adj,cell_value,time_slot_id",
        "for": "us:*",
        "time":time_list,
        # "time": "2026-04",
        "key": API_KEY
    }

    # 3. API 요청 및 데이터 처리
    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        # 4. Pandas DataFrame 변환
        df_ppi = pd.DataFrame(data[1:], columns=data[0])
        df_center = df_ppi[((df_ppi['category_code'] == 'A14XX')) & (df_ppi['data_type_code'] == 'P')] #office 투자비율(전월대비) datacenter 포함금액
        df_center.to_excel('datacenter_ppi.xlsx', index=False)  # Save to Excel
        # print(df_ppi.head())
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    return df_center

if __name__ == "__main__":
    quote = get_nvidia_quote()

    print(f"Symbol : {quote['symbol']}")
    print(f"Date   : {quote['date']}")
    print(f"Open   : {quote['open']:.2f}")
    print(f"High   : {quote['high']:.2f}")
    print(f"Low    : {quote['low']:.2f}")
    print(f"Close  : {quote['close']:.2f}")
    print(f"Volume : {quote['volume']:,}")
    month = int(input('Enter the month what you want to get the Ticker data (ex: 5): '))

    # 시간 순서대로 정렬
    df_center = get_datacenter_ppi(month)
    df_center = df_center.sort_values(by='time')

    # 4. 꺾은선 그래프(Line Plot) 그리기
    plt.figure(figsize=(10, 5))
    plt.plot(df_center['time'], df_center['cell_value'], marker='o', color='b', linestyle='-', linewidth=2)

    # 그래프 스타일 설정
    # plt.title("A14XX (Office) MoM Percent Change (P)", fontsize=14, pad=15)
    plt.title("A14XX (Office) Change (P)", fontsize=14, pad=15)
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("Percent Change (%)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)

    # # 각 점 위에 수치 표시하기
    # for x, y in zip(df_center['time'], df_center['cell_value']):
    #     plt.text(x, y + 0.1, f"{str(y)}%", ha='center', va='bottom', fontsize=10, fontweight='bold')

    # 그래프 출력
    plt.tight_layout()
    plt.savefig('datacenter_ppi.png')

    # 2. 시각화를 위해 인덱스(날짜)를 숫자로 다루기 편하게 리셋
    df_reset = get_nvidia_data(month)
    # ----------------------------------------------------
    # 1. 그래프 도화지 그리기
    fig, ax = plt.subplots(figsize=(14, 7))

    # 2. 기존 캔들차트 그리기 (반복문 코드)
    for i in range(len(df_reset)):
        row = df_reset.iloc[i]

        open_val = row['Open'].item()
        high_val = row['High'].item()
        low_val = row['Low'].item()
        close_val = row['Close'].item()

        if close_val >= open_val:
            color = 'red'
            bottom = open_val
            height = close_val - open_val
        else:
            color = 'blue'
            bottom = close_val
            height = open_val - close_val
            
        ax.vlines(i, low_val, high_val, color=color, linewidth=1)
        ax.add_patch(plt.Rectangle((i - 0.3, bottom), 0.6, height, color=color))

    # ----------------------------------------------------
    # 3. 🌟 이평선 및 볼린저 밴드 선 추가하기
    x_range = range(len(df_reset))

    # 30일 이동평균선 (중앙 점선 형태)
    ax.plot(x_range, df_reset['MA30'], label='MA 30', color='orange', linewidth=1.5, linestyle='--')

    # 볼린저 밴드 상한선 및 하한선
    ax.plot(x_range, df_reset['Upper_Band'], label='Upper Band', color='gray', linewidth=1, alpha=0.7)
    ax.plot(x_range, df_reset['Lower_Band'], label='Lower Band', color='gray', linewidth=1, alpha=0.7)

    # 볼린저 밴드 내부 채우기 (alpha로 반투명도 조절)
    ax.fill_between(x_range, df_reset['Lower_Band'], df_reset['Upper_Band'], color='gray', alpha=0.1)

    # ----------------------------------------------------
    # 4. 마무리 스타일링 및 축 설정
    date_series = df_reset['Date']
    labels = date_series.dt.strftime('%Y-%m-%d') if hasattr(date_series, 'dt') else date_series.iloc[:, 0].dt.strftime('%Y-%m-%d')

    step = max(1, len(df_reset) // 10)
    ax.set_xticks(range(0, len(df_reset), step))
    ax.set_xticklabels(labels.iloc[::step], rotation=45)

    plt.title("NVDA Candle Chart with Bollinger Bands & MA30")
    plt.grid(True, alpha=0.2)
    plt.legend(loc='upper left') # 범례 추가
    plt.tight_layout()
    plt.show()
