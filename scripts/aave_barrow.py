from brownie import (
    config,
    network,
    interface,
)
from scripts.tooling import get_account
from scripts.get_weth import get_weth
from web3 import Web3


AMOUNT = Web3.toWei(0.1, "ether")
# id="testing_account"
def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    lending_pool = get_lending_pool()
    print(lending_pool)
    approve_erc20(AMOUNT, lending_pool.address, erc20_address, account)
    print("Depositing...")
    tx = lending_pool.deposit(
        erc20_address, AMOUNT, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Deposited!")
    barrowable_eth, total_dept = get_barrowable_data(lending_pool, account)
    print("Barrowing Dai")
    dai_to_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    print(f"Latest Dai to Eth price is {dai_to_eth_price}")

    amount_to_barrow = (1 / dai_to_eth_price) * (barrowable_eth * 0.95)
    print(f"Barrowing {amount_to_barrow}")
    dai_address = config["networks"][network.show_active()]["dai_token"]
    tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_to_barrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    tx.wait(1)
    get_barrowable_data(lending_pool, account)
    repay_all(AMOUNT, lending_pool, account)
    print("repayed all depts")


def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)


def get_asset_price(price_feed_address):
    price_contract = interface.AggregatorV3Interface(price_feed_address)
    latest_price = price_contract.latestRoundData()[1]
    return float(Web3.fromWei(latest_price, "ether"))


def get_barrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_dept_eth,
        availible_barrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    availible_barrow_eth = Web3.fromWei(availible_barrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_dept_eth = Web3.fromWei(total_dept_eth, "ether")
    print(f"You have {total_collateral_eth} worth of eth deposited")
    print(f"You have {total_dept_eth} worth of eth barrowed")
    print(f"You can barrow {availible_barrow_eth} more eth")
    return (float(availible_barrow_eth), float(total_dept_eth))


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def approve_erc20(amount, spender_address, erc20_address, account):
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender_address, amount, {"from": account})
    tx.wait(1)
    print("Approved!")
