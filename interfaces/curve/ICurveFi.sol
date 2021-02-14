// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;

interface ICurveFi {

    function add_liquidity(
        uint256[2] calldata amounts,
        uint256 min_mint_amount
    ) external payable;

    function remove_liquidity(uint256 _amount, uint256[2] calldata amounts) external;

    function balances(int128) external view returns (uint256);

    function get_dy(
        int128 from,
        int128 to,
        uint256 _from_amount
    ) external view returns (uint256);

    function calc_token_amount( uint256[2] calldata amounts, bool is_deposit) external view returns (uint256);
}

interface Zap {
    function remove_liquidity_one_coin(
        uint256,
        int128,
        uint256
    ) external;
}