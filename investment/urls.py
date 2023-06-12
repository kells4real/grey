from django.urls import path
from investment import views

urlpatterns = [
    path('portfolios/', views.portfolios),
    # Users investment summary for Admin
    path('update_sale/<int:pk>/<str:param>/', views.updateInvestmentSale),
    path('investment_summary/', views.adminSummary),
    path('profits/', views.getProfit),
    # Referrals
    path('referrals/', views.getReferrals),
    path('ref_bonus/', views.refBonus),
    path('sell/<int:pk>/', views.sellInvestment),
    path('refs/', views.refs),
    path('sold_investments/', views.investmentSales),
    # User investment information, also creates an investment
    path('investment/', views.InvestViewSet.as_view({'post': 'create', 'get': 'list'})),
    # Portfolio Crud for Admin
    path('portfolio/', views.PortfolioViewSet.as_view({'post': 'create'})),
    path('portfolio/<int:pk>/', views.PortfolioViewSet.as_view({'get': 'get', 'put': 'update', 'delete': 'destroy'})),
]
