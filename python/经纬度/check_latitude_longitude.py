import requests


def send_api():
    url = "http://api.tianditu.gov.cn/geocoder"
    params = {
        "ds": '{"keyWord":  "浙江省宁波市宁海县西店镇樟树路67号"}',
        "tk": "e064499c60ad8938e93678f37d9ef08"
    }

    response = requests.get(url, params=params)
    data = response.json()
    print(data)


if __name__ == '__main__':
    send_api()
