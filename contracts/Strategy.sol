// SPDX-License-Identifier: AGPL-3.0
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import {ICurveFi} from "../interfaces/curve/ICurveFi.sol";
import {IUniswapV2Router02} from "../interfaces/uniswap/IUniswapV2Router.sol";
import {StrategyProxy} from "../interfaces/yearn/StrategyProxy.sol";

// These are the core Yearn libraries
import {
    BaseStrategy
} from "@yearnvaults/contracts/BaseStrategy.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/Address.sol";
import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import "@openzeppelin/contracts/math/Math.sol";


// Import interfaces for many popular DeFi projects, or add your own!
//import "../interfaces/<protocol>/<Interface>.sol";

contract Strategy is BaseStrategy {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    // Tokens
    IERC20 public ankrETH =  IERC20(address(0xE95A203B1a91a908F9B9CE46459d101078c2c3cb));
    IERC20 public CRV =  IERC20(address(0xD533a949740bb3306d119CC777fa900bA034cd52));
    IERC20 public ONX =  IERC20(address(0xE0aD1806Fd3E7edF6FF52Fdb822432e847411033));
    IERC20 public ANKR = IERC20(address(0x8290333ceF9e6D528dD5618Fb97a76f268f3EDD4));
    address public constant weth = address(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);

    // Dex variables
    mapping(address => address) public routers;
    address[] public crvPath;
    address[] public ankrPath;
    address[] public onxPath;

    // Curve contract
    address public gauge =  0x6d10ed2cF043E6fcf51A0e7b4C2Af3Fa06695707;
    ICurveFi public CurveStableSwap = ICurveFi(address(0xA96A65c051bF88B4095Ee1f2451C2A9d43F53Ae2));

    StrategyProxy public proxy = StrategyProxy(address(0x9a3a03C614dc467ACC3e81275468e033c98d960E));    

    constructor(address _vault) public BaseStrategy(_vault) {
        // You can set these parameters on deployment to whatever you want
        maxReportDelay = 43200;
        profitFactor = 2000;
        debtThreshold = 400*1e18;

        want.safeApprove(address(proxy), uint256(-1));
        ankrETH.approve(address(CurveStableSwap), uint256(-1));

        address uniswap = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D;
        address sushiswap = 0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F;
        routers[address(CRV)] = sushiswap;
        routers[address(ANKR)] = uniswap;
        routers[address(ONX)] = uniswap;
        CRV.approve(routers[address(CRV)], uint256(-1));
        ONX.safeApprove(routers[address(ONX)], uint256(-1));
        ANKR.approve(routers[address(ANKR)], uint256(-1));

        crvPath = new address[](2);
        crvPath[0] = address(CRV);
        crvPath[1] = weth;
        
        ankrPath = new address[](2);
        ankrPath[0] = address(ANKR);
        ankrPath[1] = weth;

        onxPath = new address[](2);
        onxPath[0] = address(ONX);
        onxPath[1] = weth;
    }


    //we get eth
    receive() external payable {}

    function name() external override view returns (string memory) {
        // Add your own name here, suggestion e.g. "StrategyCreamYFI"
        return "StrategyAnkerETHCurve";
    }

    function estimatedTotalAssets() public override view returns (uint256) {
        return proxy.balanceOf(gauge);
    }

    function prepareReturn(uint256 _debtOutstanding) internal override returns (uint256 _profit, uint256 _loss, uint256 _debtPayment) {
        // TODO: Do stuff here to free up any returns back into `want`
        // NOTE: Return `_profit` which is value generated by all positions, priced in `want`
        // NOTE: Should try to free up at least `_debtOutstanding` of underlying position

        uint256 gaugeTokens = proxy.balanceOf(gauge);

        if(gaugeTokens > 0){
            proxy.harvest(gauge);
            proxy.claimRewards(gauge, address(ANKR));
            proxy.claimRewards(gauge, address(ONX));
            // Get rewards tokens balance + sell for ETH
            uint256 crv_balance = CRV.balanceOf(address(this));
            uint256 ankr_balance = ANKR.balanceOf(address(this));
            uint256 onx_balance = ONX.balanceOf(address(this));
            if(crv_balance > 0){
                _sell(address(CRV), crv_balance);
            }
            if(ankr_balance > 0){
                _sell(address(ANKR), ankr_balance);
            }
            if(onx_balance > 0){
                _sell(address(ONX), onx_balance);
            }

            // Invest balances back into want
            uint256 eth_balance = address(this).balance;
            uint256 ankrEth_balance = ankrETH.balanceOf(address(this));
            if(eth_balance > 0 || ankrEth_balance > 0){
                CurveStableSwap.add_liquidity{value: eth_balance}([eth_balance, 0], 0);
            }
            _profit = want.balanceOf(address(this));
        }

        if(_debtOutstanding > 0){
            if(_debtOutstanding > _profit){
                uint256 stakedBal = proxy.balanceOf(gauge);
                proxy.withdraw(gauge, address(want), Math.min(stakedBal,_debtOutstanding - _profit));
            }
            _debtPayment = Math.min(_debtOutstanding, want.balanceOf(address(this)).sub(_profit));
        }
    }

    function adjustPosition(uint256 _debtOutstanding) internal override {
        uint256 _toInvest = want.balanceOf(address(this));
        want.safeTransfer(address(proxy), _toInvest);
        proxy.deposit(gauge, address(want));
    }

    function liquidatePosition(uint256 _amountNeeded) internal override returns (uint256 _liquidatedAmount, uint256 _loss) {
        uint256 wantBal = want.balanceOf(address(this));
        uint256 stakedBal = proxy.balanceOf(gauge);

        if(_amountNeeded > wantBal){
            proxy.withdraw(gauge, address(want), Math.min(stakedBal, _amountNeeded - wantBal));
        }
        _liquidatedAmount = Math.min(_amountNeeded, want.balanceOf(address(this)));

    }

    // NOTE: Can override `tendTrigger` and `harvestTrigger` if necessary
    function prepareMigration(address _newStrategy) internal override {
        // Because this strategy utilizes the proxy, gauge tokens will remain in the voter contract even after migration
        prepareReturn(proxy.balanceOf(gauge));
    }

    //sell all function
    function _sell(address token, uint256 amount) internal {
        if(token == address(CRV)){
            IUniswapV2Router02(routers[address(CRV)]).swapExactTokensForETH(amount, uint256(0), crvPath, address(this), now);
        }
        else if(token == address(ANKR)){
            IUniswapV2Router02(routers[address(ANKR)]).swapExactTokensForETH(amount, uint256(0), ankrPath, address(this), now);
        }
        else if(token == address(ONX)){
            IUniswapV2Router02(routers[address(ONX)]).swapExactTokensForETH(amount, uint256(0), onxPath, address(this), now);
        }else{
            require(false, "BAD SELL");
        }

    }

    function setDex(address _token, address _newDex) public onlyGovernance {
        routers[_token] = _newDex;
    }

    function setProxy(address _proxy) public onlyGovernance {
        proxy = StrategyProxy(_proxy);
    }

    function protectedTokens() internal override view returns (address[] memory) {
        address[] memory protected = new address[](1);
          protected[0] = address(gauge);
          return protected;
    }
}
