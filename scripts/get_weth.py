from brownie import interface, config, network
from scripts.tooling import get_account


def get_weth():
    account = get_account(id="testing_account")
    print(network.show_active())
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": 0.1 * 10 ** 18})
    tx.wait(1)
    print("Recieved 0.1 Weth")

    # need abi and address or interface


def main():
    get_weth()


main()
