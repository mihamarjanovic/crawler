from flask import Flask, render_template, request
from requests import get
from datetime import datetime, timezone
import re
import time

app = Flask(__name__)


API_KEY = "7W65PINXYBZRYVWHZK11HV4U3574RYTAXV"
BASE_URL = "https://api.etherscan.io/api"
ETHER_VALUE = 10**18

def make_api_url(module, action, address, **kwargs):
    url = BASE_URL + f"?module={module}&action={action}&address={address}&apikey={API_KEY}"
    for key, value in kwargs.items():
        url += f"&{key}={value}"
    return url

def is_valid_address(address):
    return bool(re.match(r'^0x[a-fA-F0-9]{40}$', address))

def get_account_balance(address):
    url = make_api_url("account", "balance", address, tag="latest")
    try:
        response = get(url)
        data = response.json()
        if data["status"] == "1":
            return float(data["result"]) / ETHER_VALUE
    except Exception:
        pass
    return None

def get_transactions(address, start_block):
    get_transactions_url = make_api_url(
        "account", "txlist", address, startblock=start_block, endblock=99999999, page=1, offset=10000, sort="asc"
    )
    try:
        response = get(get_transactions_url)
        data = response.json()
        if data["status"] == "1":
            for tx in data["result"]:
                tx["value"] = float(tx["value"]) / ETHER_VALUE
                tx["gasCost"] = float(tx["gasUsed"]) * float(tx["gasPrice"]) / ETHER_VALUE
                tx["time"] = datetime.fromtimestamp(int(tx["timeStamp"]), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            return data["result"]
        return []
    except Exception:
        return []

def get_token_transactions(address, start_block):
    get_token_tx_url = make_api_url(
        "account", "tokentx", address, startblock=start_block, endblock=99999999, page=1, offset=10000, sort="asc"
    )
    try:
        response = get(get_token_tx_url)
        data = response.json()
        if data["status"] == "1":
            for tx in data["result"]:
                tx["value"] = float(tx["value"]) / 10**int(tx["tokenDecimal"])
                tx["time"] = datetime.fromtimestamp(int(tx["timeStamp"]), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            return data["result"]
        return []
    except Exception:
        return []

def get_block_by_date(date_str):
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        target_timestamp = int(target_date.timestamp())
        
        latest_block_url = make_api_url("proxy", "eth_blockNumber", "")
        response = get(latest_block_url)
        latest_block = int(response.json()["result"], 16)
        
        low, high = 0, latest_block
        while low <= high:
            mid = (low + high) // 2
            block_url = make_api_url("proxy", "eth_getBlockByNumber", "", tag=hex(mid))
            response = get(block_url)
            block = response.json()["result"]
            block_timestamp = int(block["timestamp"], 16)
            
            if block_timestamp < target_timestamp:
                low = mid + 1
            elif block_timestamp > target_timestamp:
                high = mid - 1
            else:
                return mid
            time.sleep(0.2)
        return low
    except Exception:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    transactions = []
    token_transactions = []
    balance = None
    address = ""
    start_block = ""
    error = ""

    if request.method == "POST":
        address = request.form.get("address", "").strip()
        start_block = request.form.get("start_block", "").strip()

        if not is_valid_address(address):
            error = "Invalid Ethereum address format."
        elif not start_block.isdigit():
            error = "Start block must be a number."
        else:
            transactions = get_transactions(address, int(start_block))
            token_transactions = get_token_transactions(address, int(start_block))
            balance = get_account_balance(address)

            if not transactions and not token_transactions and not error:
                error = "No transactions found or API error occurred."

    return render_template(
        "index.html",
        transactions=transactions,
        token_transactions=token_transactions,
        balance=balance,
        address=address,
        start_block=start_block,
        date="",  # still passed, but unused
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)