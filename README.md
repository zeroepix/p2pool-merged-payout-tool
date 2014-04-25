P2POOL Merged Coin Payout Tool

This tool calculates the total value of alt-coins merge mined based on market prices,
and calculates the proportional payout per bitcoin mining address as reported by 
a running p2pool node. 

The proportion is calculated by total hash area over the given time frame (hour, day, month, week or year), 
excluding dead hashes. 

It gives prices in terms of each alt-currency that the server merge-mines, as well as in bitcoins,
so the miner can be paid in whichever coin is appropriate for the pool operator / miner.

Installation Requirements
-------------------------
The tool needs bitcoinrpc to run. To install:
git clone https://github.com/jgarzik/python-bitcoinrpc.git
cd python-bitcoinrpc
sudo ./setup build
sudo ./setup install

(check the github page above to see other notes if there are any installation problems)

To Run
------

Before running the tool, it needs to know the rpc details for the alt-coins running on the server.

cp config.example config
edit config
replace the values for rpcuser, rpcpass, rpcserver and rpcport as appropriate for your setup.

After that, just run the executable: ./payout.py

Command line options
--------------------

./payout.py <args>

-d	enable debug mode, printing out stages as they are calculated
-hour	show payout based on the last hour of server stats
-day	show payout based on the last day
-week	show payout based on the last week
-month 	default.
-year 	show payout based on the last year

Payout will always take the full current balance of each coin on the server at the time of running,
so after the tool is run, and miners are paid, the server operator should remove all coins from the 
default addresses. 
