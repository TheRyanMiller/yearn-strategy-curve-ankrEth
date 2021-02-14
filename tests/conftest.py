import pytest
from brownie import config, Contract


@pytest.fixture
def dev(accounts):
    yield accounts[0]

@pytest.fixture
def rewards(accounts):
    yield accounts[1]

@pytest.fixture
def gov(accounts):
    yield accounts.at("0xfeb4acf3df3cdea7399794d0869ef76a6efaff52", force=True)

@pytest.fixture
def want(interface):
    #   ankrCRV
    #   ETH / ankrETH pool LPs
    yield interface.ERC20('0xaA17A236F2bAdc98DDc0Cf999AbB47D47Fc0A6Cf')

@pytest.fixture
def ankreth(interface):
    yield interface.ERC20('0xe95a203b1a91a908f9b9ce46459d101078c2c3cb')

@pytest.fixture
def onx(interface):
    yield interface.ERC20('0xe0ad1806fd3e7edf6ff52fdb822432e847411033')

@pytest.fixture
def crv(interface):
    yield interface.ERC20('0xD533a949740bb3306d119CC777fa900bA034cd52')

@pytest.fixture
def ankr(interface):
    yield interface.ERC20('0x8290333cef9e6d528dd5618fb97a76f268f3edd4')

@pytest.fixture
def whale(accounts):
    yield accounts.at('0x3547dfca04358540891149559e691b146c6b0043', force=True)

@pytest.fixture
def whale_ankr(accounts):
    yield accounts.at('0x24434ebF296C2F9cd59b14412aae5C4ca1d5Aad2', force=True)

@pytest.fixture
def whale_onx(accounts):
    yield accounts.at('0x0EAfE0776E95b97a7318337223B845442f7715F5', force=True)

@pytest.fixture
def whale_crv(accounts):
    yield accounts.at('0xF977814e90dA44bFA03b6295A0616a897441aceC', force=True)

@pytest.fixture
def vault(pm, gov, rewards, want, dev):
    Vault = pm(config["dependencies"][0]).Vault
    vault = gov.deploy(Vault)
    vault.initialize(want, gov, rewards, "", "", dev)
    vault.setDepositLimit(2 ** 256 - 1, {"from": gov})
    yield vault


@pytest.fixture
def strategist(accounts):
    yield accounts[0]

@pytest.fixture
def voter_proxy(interface):
    proxy = "0x9a3a03C614dc467ACC3e81275468e033c98d960E"
    yield Contract(proxy)
    #yield interface.StrategyProxy(proxy)

@pytest.fixture
def voter(interface):
    yield Contract("0xf147b8125d2ef93fb6965db97d6746952a133934")

@pytest.fixture
def keeper(accounts):
    yield accounts[4]

@pytest.fixture
def live_strategy(Strategy):
    strategy = Strategy.at('0x0')
    yield strategy

@pytest.fixture
def strategy(strategist, keeper, vault, Strategy, voter_proxy, interface):
    strategy = strategist.deploy(Strategy, vault)
    strategy.setKeeper(keeper)
    debt_ratio = 10_000
    yield strategy