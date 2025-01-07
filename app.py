import sys
from scripts import test, 지역별주문수, 결제수단, 유저별주문

routes = {
    "test": test.test,
    "지역별주문수": 지역별주문수.지역별주문수,
    "결제수단": 결제수단.결제수단,
    "유저별주문": 유저별주문.유저별주문
}

def route_request(route):
    if route in routes:
        return routes[route]()
    else:
        print("올바르지 못한 라우트입니다.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        route = sys.argv[1]
        print(route_request(route))
    else:
        print("라우트를 제공해주세요.")
