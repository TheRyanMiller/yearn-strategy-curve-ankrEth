from itertools import count
from brownie import Wei, reverts
from brownie.convert import to_bytes
from useful_methods import printTokenBalances,printStrategyStats,printVaultStats
import brownie


def test_ops(want, strategy, crv, onx, ankreth, ankr, rewards, chain, vault, whale, gov, strategist, interface, voter_proxy, voter):
    tokens = [crv, onx, ankr, ankreth]
    rate_limit = 1_000_000_000 *1e18
    debt_ratio = 10_000
    vault.addStrategy(strategy, debt_ratio, rate_limit, 1000, {"from": gov})
    voter_proxy.approveStrategy(strategy.gauge(), strategy, {"from": gov})

    whalebefore = want.balanceOf(whale)
    whaledeposit = 200e18
    want.approve(vault, 2 ** 256 - 1, {"from": whale} )
    vault.deposit(whaledeposit, {"from": whale})
    print("\n****** Whale Deposit: "+ str(whaledeposit/1e18) +" ******")

    strategy.harvest({'from': strategist})
    print("\n****** HARVEST1, Move LPs to strategy ******")
    
    printVaultStats(vault, want)
    printStrategyStats(strategy, want, vault)

    """
        Here we fast-forward the chain to earn our rewards.
        NOTE: Bonus token rewards are distrubuted every 5 days. So we don't want to sleep for any more than that or else the APY will be inaccurate.
    """
    #chain.sleep(31540000) # fast forward 1 year
    #chain.sleep(2628000) # fast forward 1 month
    chain.sleep(86400) # fast forward 1 day

    chain.mine(1)

    strategy.harvest({'from': strategist})
    print("\n****** HARVEST2, Re-invest earnings ******")

    # APR = ((Total balance after 1 month - Principle) * 12months) / Principle
    print("\nEstimated APR: ", "{:.2%}".format(((
        vault.totalAssets()-whaledeposit)*365)
        /whaledeposit
    ))
    printTokenBalances(tokens, strategy, voter_proxy, voter)
    vault.withdraw({"from": whale}) # If no amount of shares is specified, default to all
    print("\n****** WITHDRAW ******")

    printVaultStats(vault, want)
    printStrategyStats(strategy, want, vault)

    print("\nWhale profit: ", (want.balanceOf(whale) - whalebefore)/1e18)
