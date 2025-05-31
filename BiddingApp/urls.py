from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
	       path('AuctionLogin.html', views.AuctionLogin, name="AuctionLogin"), 
	       path('BidderLogin.html', views.BidderLogin, name="BidderLogin"), 
	       path('Register.html', views.Register, name="Register"),
	       path('RegisterAction', views.RegisterAction, name="RegisterAction"),	
	       path('AuctionLoginAction', views.AuctionLoginAction, name="AuctionLoginAction"),
	       path('BidderLoginAction', views.BidderLoginAction, name="BidderLoginAction"),
	       path('AuctionItems', views.AuctionItems, name="AuctionItems"),
	       path('AuctionItemsAction', views.AuctionItemsAction, name="AuctionItemsAction"),
	       path('ViewHighestBid', views.ViewHighestBid, name="ViewHighestBid"),
	       path('ViewWinner', views.ViewWinner, name="ViewWinner"),
	       path('ViewAuction', views.ViewAuction, name="ViewAuction"),
	       path('BidAuction', views.BidAuction, name="BidAuction"), 
	       path('BidAuctionAction', views.BidAuctionAction, name="BidAuctionAction"), 	
	       path('ViewBidWinner.html', views.ViewBidWinner, name="ViewBidWinner"),
	       path('ViewHighestBidAction', views.ViewHighestBidAction, name="ViewHighestBidAction"),
]
