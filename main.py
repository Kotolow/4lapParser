import csv
import requests

FIELDNAMES = ["id", "title", "webpage", "old_price", "discount_price", "brand"]

COLUMN_MAPPING = {
    "id": "id товара",
    "title": "наименование",
    "webpage": "ссылка на товар",
    "old_price": "регулярная цена",
    "discount_price": "промо цена",
    "brand": "бренд"
}

PETERSBURG_CITY_CODE = '0000103664'
MOSCOW_CITY_CODE = '0000073738'


def make_request(city_code, page_id):
    cookies = {
        'selected_city_code': city_code,
    }

    headers = {
        'version-build': '186',
        'authorization': 'Basic NGxhcHltb2JpbGU6eEo5dzFRMyhy',
        'x-apps-build': '4.1.6(186)',
        'x-apps-os': '11',
        'x-apps-additionally': '404',
    }

    params = {
        'sort': 'popular',
        'category_id': 3,
        'page': page_id,
        'count': 10,
    }

    response = requests.get('https://4lapy.ru/api/goods_list_cached/', params=params, cookies=cookies, headers=headers)

    return response


def write_city_rows(city_code, csv_writer):
    initial_request = make_request(city_code, 1)
    json_dict = initial_request.json()
    data_dict = json_dict.get("data", [])
    total_pages = data_dict.get("total_pages", None)

    for page in range(1, total_pages + 1):
        request = make_request(city_code, page)
        page_dict = request.json().get("data", [])

        goods_list = page_dict.get("goods", [])
        for good in goods_list:

            price_dict = good.get("price")
            price = price_dict.get("actual")
            old_price = price_dict.get("old")
            if old_price == 0:
                old_price = price

            availability = good.get("isAvailable")

            if availability:
                row = {
                    "id": good.get("id"),
                    "title": good.get("title"),
                    "webpage": good.get("webpage"),
                    "old_price": old_price,
                    "discount_price": price,
                    "brand": good.get("brand_name"),
                }

                csv_writer.writerow(row)


out_f = open("output.csv", "w", encoding="utf-8")
out_f.write("Москва:\n")
csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
csv_writer.writerow(COLUMN_MAPPING)
write_city_rows(MOSCOW_CITY_CODE, csv_writer)

out_f.write("\nСанкт-Петербург:\n")
csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
csv_writer.writerow(COLUMN_MAPPING)
write_city_rows(PETERSBURG_CITY_CODE, csv_writer)

out_f.close()
