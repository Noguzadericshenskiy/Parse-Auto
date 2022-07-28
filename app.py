import requests as req
import csv

from typing import List, Optional
from pydantic import BaseModel, ValidationError


url_post = 'https://auto.ru/-/ajax/desktop/listing/'

headers = {
  'Accept': '*/*',
  'Accept-Encoding': 'gzip, deflate, br',
  'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
  'Cache-Control': 'no-cache',
  'Connection': 'keep-alive',
  'Content-Length': '188',
  'content-type': 'application/json',
  'Cookie': 'spravka=dD0xNjU4OTE0NTE5O2k9OTMuODAuMTgxLjIyMjtEPUJCOTE5MThCQzExQjRBOTEzQ0UyNTk0MjY4NTg2RDBENzlDNzNFMUQxODNFM0Q0NDYzQzgwMDJFQUNGQjRENzU2RDgzRkZGNjt1PTE2NTg5MTQ1MTk1NDQwNzA4ODk7aD0xZmZhNTc3ODExNTc3NGFlN2JlMWJiNzViYTJiYTZjNA==; _ym_isad=1; _ym_uid=1620416280228431817; _ym_d=1658917550; _yasc=MSRhJVPda3i8o/DgjO0mbE7BB7ypzDAKYH1gp4jWwNUPjg==; autoru_sid=a%3Ag62e106d72797acaq2l2hvd2fhj2d5a2.e0d798634ae9c832d0444b5c2c1f17c4%7C1658914519743.604800.HGP955zH-wg0liEMLdkeAQ.2M89qSN5RObEtKzhHnlk-yOugh38Z0DI89V_5xF62oQ; autoruuid=g62e106d72797acaq2l2hvd2fhj2d5a2.e0d798634ae9c832d0444b5c2c1f17c4; suid=87b5d70db465c5086913e7ca1b7f1fab.badf18e5653570ed03ddee6336594566; yuidlt=1; yandexuid=8812838481634931485; my=YwA%3D; ys=wprid.1647412649439750-4322541963675918130-vla1-2655-vla-l7-balancer-8080-BAL-7279; crookie=dkzP377yo/Tlz6sGbYr4mbZ1ri85FlEhHNBLm6aPCNaYNN0XiCsdnrLpIkt16zKrdkAo42h0NszUzteYl6rx8VUoHJI=; cmtchd=MTY1ODkxNDUyMjUyOQ==; sso_status=sso.passport.yandex.ru:synchronized_no_beacon; gdpr=0; _csrf_token=a79b80c6268e740492ae80182e647a841b888ec44459febb; from=direct; from_lifetime=1658917550966; los=1',
  # 'Cookie': 'Cookie',
  'DNT': '1',
  'Host': 'auto.ru',
  'Origin': 'https://auto.ru',
  'Pragma': 'no-cache',
  'Referer': 'https://auto.ru/moskovskaya_oblast/cars/skoda/rapid/2018-year/used/transmission-automatic/',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'same-origin',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
  'x-client-app-version': '95.0.9767920',
  'x-client-date': '1658917553936',
  'x-csrf-token': 'a79b80c6268e740492ae80182e647a841b888ec44459febb',
  'x-page-request-id': '4ae54507491bdc40a30cd817bb866eee',
  'x-requested-with': 'XMLHttpRequest',
  'x-retpath-y': 'https://auto.ru/moskovskaya_oblast/cars/skoda/rapid/2018-year/used/transmission-automatic/'
}

params = {"catalog_filter": [
            {"mark": "SKODA",
            "model": "RAPID"}
            ],
          "category": "cars",
	      "geo_id": [1,],
          "page": 1,
	      "section": "used",
	      "transmission": ["ROBOT", "AUTOMATIC", "VARIATOR", "AUTO"],
	      "year_from": 2018,
	      "year_to": 2018
}


class Price(BaseModel):
    price: int
    currency: str

class State(BaseModel):
    mileage: int
    state_not_beaten: str


class Offers(BaseModel):
    status: str
    price_info: Optional[Price]
    state: Optional[State]


class Pagination(BaseModel):
    total_page_count: int
    total_offers_count: int
    page: int
    page_size: int
    to: int
    current: int


class Answer(BaseModel):
    offers: List[Offers]
    pagination: Optional[Pagination]


def add_head_to_file():
    with open("stat.csv", mode="w", encoding='utf-8') as w_file:
        file_writer = csv.writer(w_file, delimiter=" ", lineterminator="\r")
        file_writer.writerow(["price", "currency", "mileage", "state_not_beaten", "status"])
        file_writer.writerow(['', '', '', '', ''])


def save_date_to_file(date):
    with open("stat.csv", mode="a", encoding='utf-8') as w_file:
        file_writer = csv.writer(w_file, delimiter=" ", lineterminator="\r")
        for i_line in date.offers:
            try:
                file_writer.writerow([i_line.price_info.price,
                                     i_line.price_info.currency,
                                     i_line.state.mileage,
                                     i_line.state.state_not_beaten,
                                     i_line.status
                                      ])
            except ValueError as e:
                print(["ошибка данных", e])

def send_request(parameters):
    response = req.post(url_post, json=parameters, headers=headers)
    try:
        return Answer.parse_raw(response.text)

    except ValidationError as e:
        print(e.json())


def main():
    get_data = send_request(params)
    num_page = get_data.pagination.total_page_count
    add_head_to_file()
    save_date_to_file(get_data)

    if num_page > 1:
        for i_page in range(2, num_page+1):
            params['page'] = i_page
            get_data = send_request(params)
            save_date_to_file(get_data)


if __name__ == "__main__":
    main()
