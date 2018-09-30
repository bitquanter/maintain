# -*- coding: utf-8 -*-

from __future__ import division

import math
import json
import logging
from collections import OrderedDict

import numpy as np
import pandas as pd
from cached_property import cached_property

YEAR_TRADING_DAYS = 365


class RiskCalculator(object):
    """风险指标计算器"""

    def __init__(self, cum_returns, orders, total_values, stock_classes, start_date=None):
        self.proto_cum_returns = cum_returns   # 每日的累计收益
        self.orders = orders                   # 下单记录
        self.total_values = total_values       # 每日市值
        self.stock_classes = stock_classes     # 每日持有多少只股票
        self.start_date = start_date           # 评分指标计算的开始时间
        self.log = logging.getLogger("RiskCalculator")

        self.__cache__ = {}

    @cached_property
    def cum_returns(self):
        if not self.start_date:
            return self.proto_cum_returns

        try:
            loc = self.proto_cum_returns.index.get_loc(self.start_date)
        except KeyError as e:
            self.log.exception("KeyError: %s" % e)
            return self.proto_cum_returns

        init_cash = self.proto_cum_returns.iat[(loc - 1)] + 1.0
        return (self.proto_cum_returns.iloc[loc:] + 1.0) / init_cash - 1

    @cached_property
    def proto_returns(self):
        net_values = self.proto_cum_returns + 1.0
        return net_values / net_values.shift().fillna(1.0) - 1.0

    @cached_property
    def returns(self):
        if not self.start_date:
            return self.proto_returns

        net_values = self.cum_returns + 1.0
        return net_values / net_values.shift().fillna(1.0) - 1.0

    @cached_property
    def mean_returns(self):
        _mean_returns = pd.Series(index=self.returns.index)
        for date in self.returns.index:
            curr_returns = self.returns[:date]
            _mean_returns[date] = curr_returns[:date].sum() / len(curr_returns)
        return _mean_returns

    @staticmethod
    def __calculate_return(cum_returns):
        """根据给定区间内的累计收益计算该区间内的总收益"""
        return (cum_returns[-1] + 1) / (cum_returns[0] + 1) - 1

    def calculate_half_year_return(self):
        """计算过去半年收益"""
        half_year_trad_days = int(YEAR_TRADING_DAYS / 2)
        if len(self.cum_returns) <= half_year_trad_days:
            return self.cum_returns[-1]
        return self.__calculate_return(self.cum_returns[-half_year_trad_days:])

    def calculate_year_return(self):
        """计算近一年的收益"""
        if len(self.cum_returns) <= YEAR_TRADING_DAYS:
            return self.cum_returns[-1]
        return self.__calculate_return(self.cum_returns[-YEAR_TRADING_DAYS:])

    @staticmethod
    def __calculate_annual_return(cum_returns):
        cum_return = cum_returns[-1]
        num_trade_days = len(cum_returns)
        return (1 + cum_return) ** (YEAR_TRADING_DAYS / num_trade_days) - 1

    def calculate_annual_return(self, is_proto=False):
        """计算年化收益"""
        if not self.start_date:
            if "proto_annual_return" not in self.__cache__:
                ret = self.__calculate_annual_return(self.proto_cum_returns)
                self.__cache__["proto_annual_return"] = ret
            return self.__cache__["proto_annual_return"]

        cum_returns = self.proto_cum_returns if is_proto else self.cum_returns
        return self.__calculate_annual_return(cum_returns)

    def calculate_monthly_return(self, is_proto=False):
        """计算当月收益"""
        returns = self.proto_returns if is_proto else self.returns
        early_day = returns.index[-1].replace(day=1)
        current_month_returns = returns[returns.index >= early_day]
        return (1 + current_month_returns).prod() - 1

    def calculate_year_volatility(self):
        """计算近一年的波动率"""
        year_returns = self.returns[-YEAR_TRADING_DAYS:]
        return np.std(year_returns, ddof=1) * math.sqrt(YEAR_TRADING_DAYS)

    def calculate_year_sharpe(self):
        """计算近一年的夏普率

        夏普率 = (近 12 个月年化收益 - 无风险利率(0.04)) / 近 12 个月收益波动率
        """
        year_volatility = self.calculate_year_volatility()  # 收益波动率
        if np.isclose(year_volatility, 0):
            return np.nan
        # 将收益年化
        if len(self.cum_returns) <= YEAR_TRADING_DAYS:
            annualized_return = self.calculate_annual_return()
        else:
            annualized_return = self.calculate_year_return()
        # 无风险利率，默认 0.04
        annualized_treasury_returns = 0.04
        return (annualized_return - annualized_treasury_returns) / year_volatility

    def calculate_downside_risk(self):
        """计算下行波动率"""
        rets = self.returns.round(8)
        mar = self.mean_returns.round(8)
        normalization_factor = YEAR_TRADING_DAYS
        mask = rets < mar
        downside_diff = rets[mask] - mar[mask]
        if len(downside_diff) <= 1:
            return 0.0
        return np.std(downside_diff, ddof=1) * math.sqrt(normalization_factor)

    def calculate_max_drawdown(self, period=None, is_proto=False):
        """计算最大回撤

        最大回撤 = Max(Px - Py) / Px  (P 表示净值, y > x)
        """
        returns = self.proto_returns if is_proto else self.returns
        returns = returns[-YEAR_TRADING_DAYS:] if period == "year" else returns

        compounded_returns = []
        if returns[0] < 0:
            # 设置初始的收益为0, 避免初始收益为负时, 最大回撤计算错误
            compounded_returns = [(0, returns.index[0])]

        cur_return = 0.0
        for date, r in returns.iteritems():
            try:
                cur_return += math.log(1.0 + r)
            except ValueError:
                self.log.debug("%s return, zeroing the returns", cur_return)
                cur_return = 0.0
            compounded_returns.append((cur_return, date))

        cur_max = None
        cur_max_date = None
        max_drawdown = None
        max_drawdown_period = None
        for cur, date in compounded_returns:
            if cur_max is None or cur > cur_max:
                cur_max = cur
                cur_max_date = date

            drawdown = (cur - cur_max)
            if max_drawdown is None or drawdown < max_drawdown:
                max_drawdown = drawdown
                max_drawdown_period = (cur_max_date, date)

        if max_drawdown is None:
            return 0.0, (None, None)

        return 1.0 - math.exp(max_drawdown), max_drawdown_period

    def calculate_turnover_ratio(self):
        """计算换手率

        先计算每日换手率:
            (当日买入总金额 + 当日卖出总金额) / (2 * 当日总资产)

        最终换手率为最近 60 天换手率均值
        """
        start_date = self.cum_returns.index[-60:][0]
        orders = self.orders[self.orders.index >= start_date].copy()
        if orders.empty:
            return 0
        orders["value"] = orders["amount"] * orders["price"]
        values = self.total_values

        def _calc_daily(data):
            date = data.index[0]
            total_value = values.loc[date]
            buy_value = data[data.value > 0]["value"].sum()
            sell_value = abs(data[data.value < 0]["value"].sum())
            return (buy_value + sell_value) / (2 * total_value)

        daily_turnover = orders.groupby(orders.index).apply(_calc_daily)
        return daily_turnover.sum() / len(values)

    def calculate_avg_stock_classes(self):
        """计算最近 30 个交易日平均每天持有多少只股票"""
        stock_classes = self.stock_classes[-30:]
        return stock_classes[stock_classes != 0].mean()

    def calculate_year_trading_stocks(self):
        """计算近 250 个交易日交易股票的数量"""
        start_date = self.cum_returns.index[-250:][0]
        stocks = self.orders.stock[self.orders.index >= start_date]
        trading_stocks = stocks.drop_duplicates()
        return len(trading_stocks)

    def calculate_marking_risks(self):
        return {
            "intraday_return": self.returns[-1],
            "annual_return": self.calculate_annual_return(),
            "year_return": self.calculate_year_return(),
            "year_sharpe": self.calculate_year_sharpe(),
            "downside_risk": self.calculate_downside_risk(),
            "year_max_drawdown": self.calculate_max_drawdown(period="year")[0],
            "turnover_ratio": self.calculate_turnover_ratio(),
            "trading_days": len(self.cum_returns),
            "avg_stock_classes": self.calculate_avg_stock_classes(),
            "year_trading_stocks": self.calculate_year_trading_stocks(),
        }

    def calculate_display_risks(self):
        return {
            "total_return": self.proto_cum_returns[-1],
            "annual_return": self.calculate_annual_return(is_proto=True),
            "monthly_return": self.calculate_monthly_return(is_proto=True),
            "intraday_return": self.proto_returns[-1],
            "max_drawdown": self.calculate_max_drawdown(is_proto=True)[0],
        }
