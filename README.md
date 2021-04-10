# Compile Revolut Trading statements

A simple script to compile the monthly statements provided by Revolut for trading history. 
It provides the total gain/loss and the total dividend from downloaded pdf statements.

Note that: It's not a tax advice.

You should download all the statements (pdf files) and put them in a folder
Rename the statement as YYMM (for example 2004, for april 2020), so that they can be sorted automatically
Download the script in a script.py file next to the statements
Run the script: python script.py
The script will print the total gain or loss and the total dividends!

The gain / loss is calculated by averaging the price of actions bought and calculating the different of price of actions sold.
