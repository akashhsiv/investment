def calculate_investment(stocks, investment_amount):
    """
    Calculate the investment amount for each stock based on weightage.
    """
    stocks['investment'] = stocks['weightage'] * investment_amount / 100
    return stocks

def calculate_shares(data, investment_amount):
    """
    Calculate the number of shares that can be bought each day.
    """
    data['Shares'] = investment_amount / data['Close']
    return data
