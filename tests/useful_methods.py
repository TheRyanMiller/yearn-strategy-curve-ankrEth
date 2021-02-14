from itertools import count
from brownie import Wei, reverts, network
import brownie
import requests


def get_gas_price(confirmation_speed: str = "fast"):
    if "mainnet" not in network.show_active():
        return 10 ** 9  # 1 gwei
    data = requests.get("https://www.gasnow.org/api/v3/gas/price").json()
    return data["data"][confirmation_speed]

def printProxyStats(proxy, gauge, token, voter):
    print(f"\n----state of Voter Proxy----")

def printStrategyStats(strategy, currency, vault):
    decimals = currency.decimals()
    print(f"\n----state of {strategy.name()}----")

    print("Want:", currency.balanceOf(strategy)/  (10 ** decimals))
    print("Total assets estimate:", strategy.estimatedTotalAssets()/  (10 ** decimals))
    strState = vault.strategies(strategy)
    totalDebt = strState[5]/  (10 ** decimals)
    debtLimit = strState[2]/  (10 ** decimals)
    totalLosses = strState[7]/  (10 ** decimals)
    totalReturns = strState[6]/  (10 ** decimals)
    print(f"Total Strategy Debt: {totalDebt:.5f}")
    print(f"Strategy Debt Limit: {debtLimit:.5f}")
    print(f"Total Strategy Gains: {totalReturns}")
    print(f"Total Strategy losses: {totalLosses}")
    print("Harvest Trigger:", strategy.harvestTrigger(1000000 * 30 * 1e9))
    print(
        "Tend Trigger:", strategy.tendTrigger(1000000 * 30 * 1e9)
    )  # 1m gas at 30 gwei
    print("Emergency Exit:", strategy.emergencyExit())


def printVaultStats(vault, currency):
    decimals = currency.decimals()
    print(f"\n----state of {vault.name()} vault----")
    balance = vault.totalAssets()/  (10 ** decimals)
    print(f"Total Assets: {balance:.5f}")
    balance = vault.totalDebt()/  (10 ** decimals)
    print("Loose balance in vault:", currency.balanceOf(vault)/  (10 ** decimals))
    print(f"Total Debt: {balance:.5f}")

def printTokenBalances(tokens, strategy, voter_proxy, voter):
    print("\n---Token Balances in Strategy")
    print("Eth:",strategy.balance())
    for x in tokens:
        print(x.symbol()+":",x.balanceOf(strategy))
    print("---Token Balances in StrategyProxy")
    print("Eth:",voter_proxy.balance())
    for x in tokens:
        print(x.symbol()+":",x.balanceOf(voter_proxy))
    print("---Token Balances in Voter")
    print("Eth:",voter.balance())
    for x in tokens:
        print(x.symbol()+":",x.balanceOf(voter))