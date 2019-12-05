## Test Net Wallet

# Testing wallet for test coins on testnet blockchains


I was able to create a function that would pass all the necessary info into the send_tx function so that the input to generate the transaction is only, the coin type, the “to” account, and the amount to send.

Below are the screenshots where I sent test ETH over my own blockchain, and then retrieved the transaction details using web3:

![SendingETH](/images/send_eth.png)

![SendingETH](/images/send_eth1.png)


Below are the screenshots where I Sent test BTC and then retrieved the transaction details using block cypher:

![SendingETH](/images/send_btctest.png)

![SendingETH](/images/send_btctest1.png)

I also wrote a function that would check the balance for either BTCTEST or ETH, so that I would not have to type in the bit or web3 functions in their entirety.

![SendingETH](/images/chk_bal.png)
