import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

# 각 단지별 aptrank ID 매핑
APTS = [
    {"name": "관악산휴먼시아1단지", "id": 4241},
    {"name": "금천현대",            "id": 3688},
    {"name": "면목두산1단지",        "id": 957},
    {"name": "면목두산4,5단지",      "id": 960},
    {"name": "신내데시앙",           "id": 876},
    {"name": "신내6단지시영",        "id": 901},
    {"name": "신내4단지",            "id": 873},
    {"name": "신내9단지",            "id": 888},
    {"name": "동성1,2차",            "id": 894},
    {"name": "중화한신",             "id": 859},
    {"name": "중화동건영2차",        "id": 849},
    {"name": "푸른마을동아",         "id": 6234},
    {"name": "경남아너스빌",         "id": 1556},
    {"name": "중계무지개",           "id": 1554},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def parse_price(text):
    """'8.0억', '+1.2억' 형태에서 숫자 추출"""
    m = re.search(r'[\d.]+', text.replace(',', ''))
    return float(m.group()) if m else None

def scrape_apt(apt_id):
    url = f"https://www.aptrank.com/apt_detail.php?aptnameuid={apt_id}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        price = None
        prev = None
        
        # 테이블에서 "20평대 최고가 X억 1년전 대비 +Y억" 찾기
        for td in soup.find_all('td'):
            text = td.get_text(strip=True)
            # "20평대 최고가 8.0억1년전 대비 +1.2억" 패턴
            m = re.search(r'20평대 최고가\s*([\d.]+)억.*?1년전 대비\s*([+\-][\d.]+)억', text)
            if m:
                price = float(m.group(1))
                diff = float(m.group(2))
                prev = round(price - diff, 1)
                break
        
        return {"price": price, "prev": prev}
    except Exception as e:
        print(f"Error scraping {apt_id}: {e}")
        return {"price": None, "prev": None}

def main():
    results = {}
    for apt in APTS:
        print(f"Scraping {apt['name']} (id={apt['id']})...")
        data = scrape_apt(apt['id'])
        results[apt['name']] = {
            "price": data['price'],
            "prev": data['prev'],
            "updated": datetime.now().strftime("%Y-%m-%d")
        }
        print(f"  -> {data}")
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("data.json 저장 완료!")

if __name__ == "__main__":
    main()
