# BidSecure: A Secure Blockchain Auction System

BidSecure is a secure online auction platform leveraging blockchain technology for transparent, tamper-proof bidding. It integrates a Django-based backend with Solidity smart contracts deployed via Truffle, and IPFS for decentralized storage.

---

## 🚀 Features

- ✅ Smart contract-based auction using Solidity
- ✅ Secure bidder registration & login
- ✅ Real-time bidding and highest bid tracking
- ✅ IPFS integration for file storage
- ✅ Django backend with SQLite database
- ✅ Interactive frontend with HTML/CSS/JS templates

---

## 🛠️ Technologies Used

- **Solidity** – Smart Contracts  
- **Truffle** – Blockchain development framework  
- **Django** – Backend web framework  
- **SQLite** – Local database  
- **IPFS** – Distributed file system  
- **HTML/CSS/JavaScript** – Frontend

---

## 🧪 Project Structure

BidSecure/
├── contracts/ # Solidity smart contracts
│ └── Bidding.sol
├── backend/ # Django backend
│ ├── manage.py
│ ├── db.sqlite3
│ ├── Bidding/
│ └── BiddingApp/
├── ipfs/ # IPFS-related files
│ ├── ipfs.exe
│ ├── Start_IPFS.bat
│ └── runServer.bat
├── blockchain/ # Truffle project
│ └── hello-eth/
├── requirements.txt
├── SCREENS.docx
└── README.md
