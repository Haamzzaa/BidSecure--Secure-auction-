from django.shortcuts import render
from datetime import datetime
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
import json
from web3 import Web3, HTTPProvider
import ipfsApi
import base64
import sqlite3

global username, auctionList, bidList, usersList
global contract, web3
api = ipfsApi.Client(host='http://127.0.0.1', port=5001)
conn = sqlite3.connect('db.sqlite3') 
cursor = conn.cursor() 
#function to call contract
def getContract():
    global contract, web3
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'Bidding.json' #Bidding contract file
    deployed_contract_address = '0x566830441b4F982c1e759f98C9181f2c401BE744' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
getContract()

def getUsersList():
    global usersList, contract
    usersList = []
    count = contract.functions.getUserCount().call()
    for i in range(0, count):
        user = contract.functions.getUsername(i).call()
        password = contract.functions.getPassword(i).call()
        phone = contract.functions.getPhone(i).call()
        email = contract.functions.getEmail(i).call()
        utype = contract.functions.getUserType(i).call()
        usersList.append([user, password, phone, email, utype])

def getBidList():
    global bidList, contract
    bidList = []
    count = contract.functions.getBidCount().call()
    for i in range(0, count):
        auction_id = contract.functions.getBidAuctionId(i).call()
        bidder = contract.functions.getBidder(i).call()
        amount = contract.functions.getAmount(i).call()
        bid_date = contract.functions.getBidDate(i).call()
        bidList.append([auction_id, bidder, amount, bid_date])

def getAuctionList():
    global auctionList, contract
    auctionList = []
    count = contract.functions.getAuctionCount().call()
    for i in range(0, count):
        auction_name = contract.functions.getAuctionName(i).call()
        auction_id = contract.functions.getAuctionId(i).call()
        auction_details = contract.functions.getAuctionDetails(i).call()
        price = contract.functions.getPrice(i).call()
        start_date = contract.functions.getStartDate(i).call()
        end_date = contract.functions.getEnddate(i).call()
        filename = contract.functions.getFileName(i).call()
        hashcode = contract.functions.getHashcode(i).call()
        winner = contract.functions.getWinner(i).call()
        auctionList.append([auction_name, auction_id, auction_details, price, start_date, end_date, filename, hashcode, winner])
getUsersList()
getBidList()    
getAuctionList()

def getHighestBid(auction_id):
    name = ""
    price = float('-inf')  # Start with negative infinity for highest bid search
    
    # Connect to the database
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Safe query to fetch auction type using parameterized query
    cursor.execute("SELECT autype FROM auction WHERE aid=?", (auction_id,))
    actype = cursor.fetchone()
    conn.close()

    # Check if actype is valid, if not return None or handle the error
    if actype is None:
        print("Auction not found.")
        return None, None
    
    print("bidList====", str(bidList))
    print("str(actype[0])====", str(actype[0]))

    # If it's a regular auction (highest bid)
    if str(actype[0]) == "Auction":
        for blist in bidList:
            if blist[0] == auction_id:  # Check if the bid is for the current auction
                bid_price = float(blist[2])  # Convert bid price to float
                if bid_price > price:  # Compare to find highest bid
                    price = bid_price
                    name = blist[1]  # Store bidder's name

    # If it's a reverse auction (lowest bid)
    else:
        price = float('inf')  # Initialize to infinity for lowest bid search
        for blist in bidList:
            if blist[0] == auction_id:  # Check if the bid is for the current auction
                bid_price = float(blist[2])  # Convert bid price to float
                if bid_price < price:  # Compare to find lowest bid
                    price = bid_price
                    name = blist[1]  # Store bidder's name

    # If no bids are found, return a message or handle it
    if price == float('-inf'):
        print(f"No valid bids for auction {auction_id}.")
        return None, None
    elif price == float('inf'):
        print(f"No valid bids for auction {auction_id}.")
        return None, None

    return name, price         
        

def chooseWinner():
    global auctionList, bidList, contract
    current_date = datetime.now().date()
    #current_date = datetime.strptime('2024-11-13', "%Y-%m-%d").date()
    for i in range(len(auctionList)):
        auction = auctionList[i]
        start_date = datetime.strptime(auction[4], "%Y-%m-%d").date()
        end_date = datetime.strptime(auction[5], "%Y-%m-%d").date()
        print(str(current_date)+" "+str(start_date)+" "+str(end_date))
        if current_date >= start_date and end_date == current_date and auction[8] == '-':
            bidder_name, high_price = getHighestBid(auction[1])
            auction[8] = bidder_name+","+str(high_price)
            print(auction)
            contract.functions.updateWinner(i, bidder_name+","+str(high_price)).transact()

def BidAuction(request):
    if request.method == 'GET':
        global username
        auction_id = request.GET['aid']
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor() 
        cursor.execute("select autype from auction where aid='"+str(auction_id)+"'")
        actype=cursor.fetchone()
        conn.close() 
        output = '<tr><td><font size="3" color="black">Auction&nbsp;ID</td><td><input type="text" name="t1" size="15" value="'+auction_id+'" readonly/></td></tr>'
        output+='<tr><td><font size="3" color="black">Bidding&nbsp;Type</td><td><input type="text" name="t7" size="15" value="'+str(actype[0])+'" readonly/></td></tr>'
        context= {'data1':output}
        return render(request,'BidAuction.html', context)

def ViewAuction(request):
    if request.method == 'GET':
        global auctionList, username
        chooseWinner()
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Auctioner Name</font></th>'
        output+='<th><font size=3 color=black>Auction ID</font></th>'
        output+='<th><font size=3 color=black>Auction Details</font></th>'
        output+='<th><font size=3 color=black>Auction Price</font></th>'
        output+='<th><font size=3 color=black>Start Date</font></th>'
        output+='<th><font size=3 color=black>End Date</font></th>'
        output+='<th><font size=3 color=black>Product Image</font></th>'
        output+='<th><font size=3 color=black>Click Here to Bid</font></th>'
        for i in range(len(auctionList)):
            alist = auctionList[i]
            if alist[8] == "-":
                output+='<tr><td><font size=3 color=black>'+alist[0]+'</font></td>'
                output+='<td><font size=3 color=black>'+alist[1]+'</font></td>'
                output+='<td><font size=3 color=black>'+alist[2]+'</font></td>'
                output+='<td><font size=3 color=black>'+alist[3]+'</font></td>'
                output+='<td><font size=3 color=black>'+alist[4]+'</font></td>'
                output+='<td><font size=3 color=black>'+alist[5]+'</font></td>'
                img_name = alist[6]
                hashcode = alist[7]
                content = api.get_pyobj(hashcode)
                if os.path.exists('BiddingApp/static/files/'+img_name):
                    os.remove('BiddingApp/static/files/'+img_name)
                with open('BiddingApp/static/files/'+img_name, "wb") as file:
                    file.write(content)
                file.close()
                output += '<td><img src="static/files/'+img_name+'" width="200" height="200"/></td>'
                output+='<td><a href=\'BidAuction?aid='+alist[1]+'\'><font size=3 color=red>Click Here to Bid</font></a></td></tr>'
        output += "</table><br/><br/><br/><br/>"
        context= {'data':output}        
        return render(request,'BidderScreen.html', context)            

def ViewWinner(request):
    if request.method == 'GET':
        global auctionList, username
        chooseWinner()
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Auctioner Name</font></th>'
        output+='<th><font size=3 color=black>Auction ID</font></th>'
        output+='<th><font size=3 color=black>Auction Details</font></th>'
        output+='<th><font size=3 color=black>Auction Price</font></th>'
        output+='<th><font size=3 color=black>Start Date</font></th>'
        output+='<th><font size=3 color=black>End Date</font></th>'
        output+='<th><font size=3 color=black>Product Image</font></th>'
        output+='<th><font size=3 color=black>Winner Name</font></th>'
        output+='<th><font size=3 color=black>Highest Bid Price</font></th>'
        for i in range(len(auctionList)):
            alist = auctionList[i]
            if alist[0] == username:
                output+='<tr><td><font size=3 color=black>'+alist[0]+'</font></td>'
                output+='<td><font size=3 color=black>'+alist[1]+'</font></td>'
                output+='<td><font size=3 color=black>'+alist[2]+'</font></td>'
                output+='<td><font size=3 color=black>'+alist[3]+'</font></td>'
                output+='<td><font size=3 color=black>'+alist[4]+'</font></td>'
                output+='<td><font size=3 color=black>'+alist[5]+'</font></td>'
                img_name = alist[6]
                hashcode = alist[7]
                content = api.get_pyobj(hashcode)
                if os.path.exists('BiddingApp/static/files/'+img_name):
                    os.remove('BiddingApp/static/files/'+img_name)
                with open('BiddingApp/static/files/'+img_name, "wb") as file:
                    file.write(content)
                file.close()
                output += '<td><img src="static/files/'+img_name+'" width="200" height="200"/></td>'
                if alist[8] == "-":
                    output+='<td><font size=3 color=black>-</font></td>'
                    output+='<td><font size=3 color=black>-</font></td></tr>'
                else:
                    arr = alist[8].split(",")
                    output+='<td><font size=3 color=black>'+arr[0]+'</font></td>'
                    output+='<td><font size=3 color=black>'+arr[1]+'</font></td></tr>'
        output += "</table><br/><br/><br/><br/>"
        context= {'data':output}        
        return render(request,'AuctionScreen.html', context)
    

def BidAuctionAction(request):
    if request.method == 'POST':
        global bidList, username
        auction_id = request.POST.get('t1', False)
        price = request.POST.get('t2', False)
        current_date = str(datetime.now().date())
        
        msg = contract.functions.saveBid(auction_id, username, price, current_date).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
        bidList.append([auction_id, username, price, current_date])
        context= {'data':'Your bid accepted of amount = '+str(price)+'<br/><br/>'}
        return render(request, 'BidderScreen.html', context)

def ViewBidWinner(request):
    if request.method == 'GET':
        global auctionList, username
        chooseWinner()
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Auctioner Name</font></th>'
        output+='<th><font size=3 color=black>Auction ID</font></th>'
        output+='<th><font size=3 color=black>Auction Details</font></th>'
        output+='<th><font size=3 color=black>Auction Price</font></th>'
        output+='<th><font size=3 color=black>Start Date</font></th>'
        output+='<th><font size=3 color=black>End Date</font></th>'
        output+='<th><font size=3 color=black>Product Image</font></th>'
        output+='<th><font size=3 color=black>Winner Name</font></th>'
        output+='<th><font size=3 color=black>Highest Bid Price</font></th></tr>'
        for i in range(len(auctionList)):
            alist = auctionList[i]
            output+='<tr><td><font size=3 color=black>'+alist[0]+'</font></td>'
            output+='<td><font size=3 color=black>'+alist[1]+'</font></td>'
            output+='<td><font size=3 color=black>'+alist[2]+'</font></td>'
            output+='<td><font size=3 color=black>'+alist[3]+'</font></td>'
            output+='<td><font size=3 color=black>'+alist[4]+'</font></td>'
            output+='<td><font size=3 color=black>'+alist[5]+'</font></td>'
            img_name = alist[6]
            hashcode = alist[7]
            content = api.get_pyobj(hashcode)
            if os.path.exists('BiddingApp/static/files/'+img_name):
                os.remove('BiddingApp/static/files/'+img_name)
            with open('BiddingApp/static/files/'+img_name, "wb") as file:
                file.write(content)
            file.close()
            output += '<td><img src="static/files/'+img_name+'" width="200" height="200"/></td>'
            if alist[8] == "-":
                output+='<td><font size=3 color=black>-</font></td>'
                output+='<td><font size=3 color=black>-</font></td></tr>'
            else:
                arr = alist[8].split(",")
                output+='<td><font size=3 color=black>'+arr[0]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[1]+'</font></td></tr>'
        output += "</table><br/><br/><br/><br/>"
        context= {'data':output}        
        return render(request,'BidderScreen.html', context)    

def ViewHighestBidAction(request):
    if request.method == 'POST':
        global bidList, username
        auction_id = request.POST.get('t1', False)
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Auction ID</font></th>'
        output+='<th><font size=3 color=black>Bidder Name</font></th>'
        output+='<th><font size=3 color=black>Bid Amount</font></th>'
        output+='<th><font size=3 color=black>Bid Date</font></th></tr>'
        for i in range(len(bidList)):
            blist = bidList[i]
            if blist[0] == auction_id:
                output+='<tr><td><font size=3 color=black>'+blist[0]+'</font></td>'
                output+='<td><font size=3 color=black>'+blist[1]+'</font></td>'
                output+='<td><font size=3 color=black>'+blist[2]+'</font></td>'
                output+='<td><font size=3 color=black>'+blist[3]+'</font></td></tr>'
        output += "</table><br/><br/><br/><br/>"
        context= {'data':output}        
        return render(request,'AuctionScreen.html', context)            

def getAuctionerName(auction_id):
    name = ""
    for i in range(len(auctionList)):
        auction = auctionList[i]
        if auction[1] == auction_id:
            name = auction[0]
            break
    return name    

def ViewHighestBid(request):
    if request.method == 'GET':
        global bidList, username
        output = '<tr><td><font size="3" color="black">Choose&nbsp;Auction&nbsp;Id</td><td><select name="t1">'
        for i in range(len(bidList)):
            auction = bidList[i]
            if getAuctionerName(auction[0]) == username:
                output += '<option value="'+auction[0]+'">'+auction[0]+"</option>" 
        output += '</select></td></tr>'
        context= {'data1':output}
        return render(request, 'ViewHighestBid.html', context)

def AuctionItemsAction(request):
    if request.method == 'POST':
        global auctionList, username
        auction_details = request.POST.get('t1', False)
        price = request.POST.get('t2', False)
        start_date = request.POST.get('t3', False)
        end_date = request.POST.get('t4', False)
        actype=request.POST.get('actype',False)
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        start_date = str(start_date.strftime("%Y-%m-%d"))
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        end_date = str(end_date.strftime("%Y-%m-%d"))
        auction_id = str(len(auctionList) + 1)
        filename = request.FILES['t5'].name
        myfile = request.FILES['t5'].read()
        hashcode = api.add_pyobj(myfile)
        msg = contract.functions.saveAuction(username, auction_id, auction_details, price, start_date, end_date, filename, hashcode, "-").transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
        auctionList.append([username, auction_id, auction_details, price, start_date, end_date, filename, hashcode, "-"])
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor() 
        cursor.execute("insert into auction values('"+str(auction_id)+"','"+str(actype)+"')")
        conn.commit() 
        conn.close() 
        context= {'data':'Auction details addec to Blockchain with ID = '+str(auction_id)+'<br/><br/>'}
        return render(request, 'AuctionItems.html', context)        

def AuctionItems(request):
    if request.method == 'GET':
        return render(request,'AuctionItems.html', {})

def index(request):
    if request.method == 'GET':
        return render(request,'index.html', {})

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})
    
def AuctionLogin(request):
    if request.method == 'GET':
       return render(request, 'AuctionLogin.html', {})

def BidderLogin(request):
    if request.method == 'GET':
       return render(request, 'BidderLogin.html', {})

def RegisterAction(request):
    if request.method == 'POST':
        global usersList
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t6', False)
        usertype = request.POST.get('t8', False)
        status = "none"
        for i in range(len(usersList)):
            users = usersList[i]
            if username == users[0]:
                status = "exists"
                break
        if status == "none":
            msg = contract.functions.saveUser(username, password, contact, email, usertype).transact()
            tx_receipt = web3.eth.waitForTransactionReceipt(msg)
            usersList.append([username, password, contact, email, usertype])
            context= {'data':'Signup Process Completed<br/>'}
            return render(request, 'Register.html', context)
        else:
            context= {'data':'Given username already exists'}
            return render(request, 'Register.html', context)

def BidderLoginAction(request):
    if request.method == 'POST':
        global username, contract, usersList
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        status = 'none'
        for i in range(len(usersList)):
            ulist = usersList[i]
            user1 = ulist[0]
            pass1 = ulist[1]
            utype = ulist[4]
            if user1 == username and pass1 == password and utype == "Bidder":
                status = "success"
                break
        if status == 'success':
            output = 'Welcome '+username
            context= {'data':output}
            return render(request, "BidderScreen.html", context)
        if status == 'none':
            context= {'data':'Invalid login details'}
            return render(request, 'BidderLogin.html', context)
        
def AuctionLoginAction(request):
    if request.method == 'POST':
        global username, contract, usersList
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        status = 'none'
        for i in range(len(usersList)):
            ulist = usersList[i]
            user1 = ulist[0]
            pass1 = ulist[1]
            utype = ulist[4]
            if user1 == username and pass1 == password and utype == "Auctioner":
                status = "success"
                break
        if status == 'success':
            output = 'Welcome '+username
            context= {'data':output}
            return render(request, "AuctionScreen.html", context)
        if status == 'none':
            context= {'data':'Invalid login details'}
            return render(request, 'AuctionLogin.html', context)
