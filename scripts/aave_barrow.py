from brownie.network import account
from brownie import config, network
from scripts.tooling import get_account
from scripts.get_weth import get_weth

# id="testing_account"
def main():
    account = get_account()
    erc20_weth_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        tx = get_weth()
