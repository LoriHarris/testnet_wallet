
#Dependencies
from constants import *
import os
from dotenv import load_dotenv
import subprocess
import json
from pprint import pprint
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy
from eth_account import Account
from bit import wif_to_key, PrivateKeyTestnet
from bit.network import NetworkAPI
from pathlib import Path
from getpass import getpass

#Setting function dependent variables
load_dotenv()
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)
mnemonic = os.getenv('MNEMONIC')
command = f'php hd-wallet-derive/hd-wallet-derive.php -g --mnemonic="{mnemonic}" --cols=path,address,privkey,pubkey --numderive=3 --format=jsonpretty'

#Initializing subprocess
p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
p_status = p.wait()
keys = json.loads(output)

#Wallet code:

#Checks balance for either account, eth or btctest
def check_balance(coin):
    if coin == ETH:
        balance = w3.eth.getBalance(priv_key_to_account(ETH).address)
    elif coin == BTCTEST:
        balance = priv_key_to_account(BTCTEST).get_balance()
    return balance

#Obtains wallet information to be used in priv_key_to_account()
def derive_wallets(coins=[],numderive=3):
    coin_dict ={}
    for coin in coins:
        command = f'php hd-wallet-derive/hd-wallet-derive.php -g --mnemonic="{mnemonic}" --cols=all --coin={coin} --numderive={numderive} --format=jsonpretty'
        p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        p_status = p.wait()
        keys = json.loads(output)
        coin_dict[coin]=keys
  
    return coin_dict

#Obtains key/account information to be used in send_tx()
def priv_key_to_account(coin):
    coins=derive_wallets(coins=[BTCTEST, ETH])
    if coin == 'eth':
        with open(Path("../key")) as keyfile:
            encrypted_key = keyfile.read()
            private_key = w3.eth.account.decrypt(
                encrypted_key, getpass("Enter keystore password: ")
            )
            key = Account.from_key(private_key)
    elif coin == 'btc-test':
        key = PrivateKeyTestnet(coins['btc-test'][0]['privkey'])
    return key
    
#Creates the transaction to use inside send_tx()
def create_tx(coin, account, to, amount):
    if coin == 'eth':
        gasEstimate = w3.eth.estimateGas(
        {"from": account.address, "to": to, "value": amount}
    )
        info = {
        "from": account.address,
        "to": to,
        "value": amount,
        "gasPrice": w3.eth.gasPrice,
        "gas": gasEstimate,
        "nonce": w3.eth.getTransactionCount(account.address),
    }
    elif coin == 'btc-test':
        info = PrivateKeyTestnet.prepare_transaction(str(account.address), [(to, amount, BTC)])
 
    return info    

#Utilizes all previous function except 'check_balance()' to send the transaction and print the transaction #
def send_tx(coin, to, amount):
    account = priv_key_to_account(coin)
    tx = create_tx(coin, account, to, amount)
    if coin == 'eth':
        signed_tx = account.signTransaction(tx)
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction).hex()
    elif coin == 'btc-test':
        signed_tx = account.sign_transaction(tx)
        result = NetworkAPI.broadcast_tx_testnet(signed_tx)
        transaction = account.get_transactions()[0]
        print(transaction)
    return result

