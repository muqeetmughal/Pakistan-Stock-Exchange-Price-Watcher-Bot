import requests_instance
import requests
from bs4 import BeautifulSoup
import json, os
import concurrent.futures
import time
from colorama import Fore, Back, Style, init
import datetime

# init(autoreset=True)x
class Utils:

    def __init__(self) -> None:
        pass

    def colored_value(self, color, text):
        return Style.RESET_ALL + color + str(text) + Style.RESET_ALL

    def _parse_html(self, response: requests.Response) -> BeautifulSoup:
        return BeautifulSoup(response.content, "html.parser")

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")


class PSXTrader(Utils):

    def __init__(self) -> None:
        self.client = requests_instance.HttpClient("https://dps.psx.com.pk")
        self.last_values = {}

    # https://dps.psx.com.pk/symbols
    # https://dps.psx.com.pk/company/reports/AVN
    # https://dps.psx.com.pk/timeseries/int/AVN
    # https://dps.psx.com.pk/timeseries/eod/AVN

    def get_stock_info(self, symbol: str):
        response = self.client.get(f"/company/{symbol}")
        soup = self._parse_html(response)
        # company = soup.select_one("#quote")

        company_name = soup.select_one(
            "#quote > div.company__quote > div.quote__details > div.quote__name"
        )
        sector = soup.select_one(
            "#quote > div.company__quote > div.quote__details > div.quote__sector > span"
        )
        price = soup.select_one(
            "#quote > div.company__quote > div.quote__details > div.quote__price > div.quote__close"
        )
        price_in_float = float(
            str(price.text).replace("Rs.", "").replace(",", "").strip()
        )
        change_value = soup.select_one(
            "#quote > div.company__quote > div.quote__details > div.quote__price > div.quote__change.change__text--pos > div.change__value"
        )
        change_percentage = soup.select_one(
            "#quote > div.company__quote > div.quote__details > div.quote__price > div.quote__change.change__text--pos > div.change__percent"
        )
        data = {
            "company_name": company_name.text.strip() if company_name else None,
            "sector": sector.text.strip() if sector else None,
            "price": price_in_float,
            "change_value": change_value.text.strip() if change_value else None,
            "change_percentage": (
                change_percentage.text.strip() if change_percentage else None
            ),
            "symbol": symbol,
        }
        # print(json.dumps(data))
        # print(data)
        return data

    def print_output(self):
        self.clear_screen()

        print(f"Symbol\tGoal\tPrice\tTarget\tPurchase\tDiffernce\t\tBuy\t\tSell\tUpdated At")
        # statement = ""
        data = self.last_values
        for symbol, stock in data.items():

            new_price = stock["price"]
            looking_for = stock["looking_for"]
            target_price = stock["target_price"]

            price_color = Fore.WHITE
            looking_for_bg_color = Back.WHITE
            
            buying_recommended = None
            selling_recommended = None
            
            if looking_for == "BUY":
                # looking_for_bg_color = Back.RED

                if new_price >= target_price:
                    price_color = Fore.RED
                    buying_recommended = "❌"
                else:
                    price_color = Fore.GREEN
                    buying_recommended = "✅"

            elif looking_for == "SELL":
                # looking_for_bg_color = Back.GREEN
                if new_price >= target_price:
                    price_color = Fore.GREEN
                    selling_recommended = "✅"
                else:
                    price_color = Fore.RED
                    selling_recommended = "❌"

            profit_loss = stock["price"] - stock["purchase_price"]
            if profit_loss < 0:
                profit_loss_color = Fore.RED
            else:
                profit_loss_color = Fore.GREEN
            formatted_profit_loss = format(abs(profit_loss), ".2f")

            statement = f"{self.colored_value(Fore.BLUE,symbol)}\t{self.colored_value(looking_for_bg_color, looking_for)}\t{self.colored_value(price_color,new_price)}\t{self.colored_value(Fore.CYAN,target_price)}\t{self.colored_value(Fore.BLUE,stock['purchase_price'])}\t\t{self.colored_value(profit_loss_color,formatted_profit_loss)}\t\t\t{buying_recommended}\t\t{selling_recommended}\t{stock["last_update"]}"
            print(statement)

    def monitor_stock(self, stock):
        while True:
            try:
                symbol = stock["symbol"]
                # target_price = stock['target_price']
                # looking_for = stock['looking_for']

                new_data = self.get_stock_info(symbol)

                self.last_values[symbol] = {
                    **stock,
                    **new_data,
                    "last_update": datetime.datetime.now()  # Store the last update time for comparison in future.
                }

                self.print_output()
           
            except Exception as e:
                print(f"Error monitoring {stock}: {e}")
                raise e
            time.sleep(3)  # Sleep for 60 seconds before next check

    def fetch_and_monitor_stock(self, stock):
        # print(f"Thread Number: {thread_number} for stock {stock}")
        self.monitor_stock(stock)


if __name__ == "__main__":
    psx = PSXTrader()
    THREADS_PER_WATCHER = 2
    WAIT_TIME = 1

    watchers = [
        {
            "symbol": "PTC",
            "target_price": 13.40,
            "purchase_price": 13.28,
            "looking_for": "SELL",
        },
        {
            "symbol": "KEL",
            "target_price": 4.98,
            "purchase_price": 4.96,
            "looking_for": "SELL",
        },
        {
            "symbol": "NETSOL",
            "target_price": 139.50,
            "purchase_price": 138.53,
            "looking_for": "SELL",
        },
    ]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for stock in watchers:
            # print(stock)
            # symbol = watchers['symbol']
            # target_price = watchers
            # Create multiple threads for each stock
            for i in range(THREADS_PER_WATCHER):  # Number of threads per stock
                # thread_number = i+1
                futures.append(executor.submit(psx.fetch_and_monitor_stock, stock))

    # This will keep the main thread alive to keep the monitoring running
    try:
        while True:
            time.sleep(WAIT_TIME)
            continue
    except KeyboardInterrupt:
        print("Monitoring stopped.")
