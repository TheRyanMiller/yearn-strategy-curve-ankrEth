from itertools import count
from brownie import Wei, reverts
from brownie.convert import to_bytes
from useful_methods import genericStateOfStrat,genericStateOfVault
import brownie


def test_ops(want, strategy, crv, onx, ankreth, ankr, rewards, chain, vault, whale, gov, strategist, interface, voter_proxy, voter):
    rate_limit = 1_000_000_000 *1e18
    debt_ratio = 10_000
    vault.addStrategy(strategy, debt_ratio, rate_limit, 1000, {"from": gov})
    voter_proxy.approveStrategy(strategy.gauge(), strategy, {"from": gov})

    whalebefore = want.balanceOf(whale)
    want.approve(vault, 2 ** 256 - 1, {"from": whale} )
    vault.deposit(200e18, {"from": whale})

    strategy.harvest({'from': strategist})
    print("\n-----HARVEST1, Move LPs to strategy ----")
    genericStateOfStrat(strategy, want, vault)
    genericStateOfVault(vault, want)

    chain.sleep(2592000)
    chain.mine(1)

    strategy.harvest({'from': strategist})
    print("\n-----HARVEST2, Re-invest earnings ----")

    ankrethbal = ankreth.balanceOf(strategy)
    ethbal = strategy.balance()
    """
    assert ankrethbal <= 1
    assert ethbal <= 1
    assert crv.balanceOf(strategy) == 0
    assert ankr.balanceOf(strategy) == 0
    assert onx.balanceOf(strategy) == 0
    """
    print("ankrETH = ", ankrethbal/1e18)
    print("ETH = ", ethbal/1e18)

    print("\nVOTER BALANCES~~~~~~~~~~")
    print("CRV:",crv.balanceOf(voter))
    print("ANKR:",ankr.balanceOf(voter))
    print("ONX:",onx.balanceOf(voter))
    print("ANKRETH:",ankreth.balanceOf(voter))
    print("ETH:",voter.balance())
    print("PROXY BALANCES~~~~~~~~~~")
    print("CRV:",crv.balanceOf(voter_proxy))
    print("ANKR:",ankr.balanceOf(voter_proxy))
    print("ONX:",onx.balanceOf(voter_proxy))
    print("ANKRETH:",ankreth.balanceOf(voter_proxy))
    print("ETH:",voter_proxy.balance())
    print("STRAT BALANCES~~~~~~~~~~")
    print("CRV:",crv.balanceOf(strategy))
    print("ANKR:",ankr.balanceOf(strategy))
    print("ONX:",onx.balanceOf(strategy))
    print("ANKRETH:",ankreth.balanceOf(strategy))
    print("ETH:",strategy.balance())

    print("\nEstimated APR: ", "{:.2%}".format(((vault.totalAssets()-200*1e18)*12)/(200*1e18)))

    vault.withdraw({"from": whale})
    print("\nWithdraw")
    genericStateOfStrat(strategy, want, vault)
    genericStateOfVault(vault, want)
    print("Whale profit: ", (want.balanceOf(whale) - whalebefore)/1e18)
