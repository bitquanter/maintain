# -*- coding: utf-8 -*-
# functions which are in common use
from __future__ import division
from functools import reduce
from numpy import nan
from strategy.data.api import get_trade_days, get_price


####################################################### 超买超卖型 ############
# ATR-真实波幅


def ATR(security_list, check_date, timeperiod=14):
    '''
    计算公式：
        MTR:MAX(MAX((HIGH-LOW),ABS(REF(CLOSE,1)-HIGH)),ABS(REF(CLOSE,1)-LOW));
        ATR:MA(MTR,N);
        输出MTR:(最高价-最低价)和1日前的收盘价-最高价的绝对值的较大值和1日前的收盘价-最低价的绝对值的较大值
        输出真实波幅ATR:MTR的N日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数 timeperiod
    输出：
        MTR和ATR 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 ATR
    mtr = {}
    atr = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'high', 'low'],  count=timeperiod * 2)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            mtr[coin] = np.nan
            atr[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_ATR = security_data['close']
            high_ATR = security_data['high']
            low_ATR = security_data['low']
            # 计算 MTR和ATR
            list_mtr = []
            temp = -timeperiod
            while temp < 0:
                t = max(high_ATR[temp] - low_ATR[temp], abs(close_ATR[temp - 1] -
                                                            high_ATR[temp]), abs(close_ATR[temp - 1] - low_ATR[temp]))
                list_mtr.append(t)
                temp += 1
            res = talib.MA(np.array(list_mtr), timeperiod)

            mtr[coin] = list_mtr[-1]
            atr[coin] = res[-1]
    return mtr, atr

# BIAS-乖离率


def BIAS(security_list, check_date, N1=6, N2=12, N3=24):
    '''
    计算公式：
        BIAS1 :(CLOSE-MA(CLOSE,N1))/MA(CLOSE,N1)*100;
        BIAS2 :(CLOSE-MA(CLOSE,N2))/MA(CLOSE,N2)*100;
        BIAS3 :(CLOSE-MA(CLOSE,N3))/MA(CLOSE,N3)*100;
        输出BIAS1 = (收盘价-收盘价的N1日简单移动平均)/收盘价的N1日简单移动平均*100
        输出BIAS2 = (收盘价-收盘价的N2日简单移动平均)/收盘价的N2日简单移动平均*100
        输出BIAS3 = (收盘价-收盘价的N3日简单移动平均)/收盘价的N3日简单移动平均*100
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N1：统计的天数 N1
        N2: 统计的天数 N2
        N3: 统计的天数 N3
    输出：
        BIAS1, BIAS2, BIAS3 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 BIAS
    bias1 = {}
    bias2 = {}
    bias3 = {}
    maxN = max(N1, N2, N3)
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=maxN * 2)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            bias1[coin] = np.nan
            bias2[coin] = np.nan
            bias3[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            current_price = security_data['close'][-1]
            average_price = security_data['close'][-N1:].mean()
            bias1[coin] = (current_price - average_price) / \
                average_price * 100.0

            average_price = security_data['close'][-N2:].mean()
            bias2[coin] = (current_price - average_price) / \
                average_price * 100.0

            average_price = security_data['close'][-N3:].mean()
            bias3[coin] = (current_price - average_price) / \
                average_price * 100.0
    return bias1, bias2, bias3

# CCI-商品路径指标


def CCI(security_list, check_date, N=14):
    '''
    计算公式：
        TYP:=(HIGH+LOW+CLOSE)/3;
        CCI:(TYP-MA(TYP,N))/(0.015*AVEDEV(TYP,N));
        TYP赋值:(最高价+最低价+收盘价)/3
        输出CCI = (TYP-TYP的N日简单移动平均)/(0.015*TYP的N日平均绝对偏差)
        其中，绝对平均偏差= 1/n * (SUM(|xi-x均|), i=1,2,3...n)
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
    输出：
        CCI 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 CCI
    cci = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'high', 'low'],  count=N * 2)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            cci[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_CCI = security_data['close']
            high_CCI = security_data['high']
            low_CCI = security_data['low']
            cci[coin] = talib.CCI(np.array(high_CCI), np.array(
                low_CCI), np.array(close_CCI), N)[-1]
    return cci

# KDJ-随机指标


def KDJ(security_list, check_date, N=9, M1=3, M2=3):
    '''
    计算公式：
        RSV:=(CLOSE- LLV(LOW,N) )/(HHV(HIGH,N)-LLV(LOW,N))*100;
        K:SMA(RSV,M1,1);
        D:SMA(K,M2,1);
        J:3*K-2*D;
        RSV赋值:(收盘价-N日内最低价的最低值)/(N日内最高价的最高值-N日内最低价的最低值)*100
        输出K = RSV的M1日[1日权重]移动平均
        输出D = K的M2日[1日权重]移动平均
        输出J = 3*K-2*D
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M1：统计的天数 M1
        M2：统计的天数 M2
    输出：
        K，D和J 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 计算close的N日移动平均，权重默认为1

    def SMA_CN(close, N):
        close = np.nan_to_num(close)
        return reduce(lambda x, y: ((N - 1) * x + y) / N, close)

    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 KDJ
    n = max(N, M1, M2)
    k = {}
    d = {}
    j = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'high', 'low', 'close'],  count=n * 10)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            k[coin] = np.nan
            d[coin] = np.nan
            j[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            high_KDJ = security_data['high']
            low_KDJ = security_data['low']
            close_KDJ = security_data['close']
            high = np.array(high_KDJ)
            low = np.array(low_KDJ)
            close = np.array(close_KDJ)

            # 使用talib中的STOCHF函数求 RSV
            kValue, dValue = talib.STOCHF(
                high, low, close, N, M2, fastd_matype=0)
            # 求K值(等于RSV的M1日移动平均)
            kValue = np.array([i for i in six.moves.map(lambda x: SMA_CN(
                kValue[:x], M1), range(1, len(kValue) + 1))])
            # 求D值(等于K的M2日移动平均)
            dValue = np.array([i for i in six.moves.map(lambda x: SMA_CN(
                kValue[:x], M2), range(1, len(kValue) + 1))])
            # 求J值
            jValue = 3 * kValue - 2 * dValue

            k[coin] = kValue[-1]
            d[coin] = dValue[-1]
            j[coin] = jValue[-1]
    return k, d, j

# MFI-资金流量指标


def MFI(security_list, check_date, timeperiod=14):
    '''
    计算公式：
        TYP = (最高价 + 最低价 + 收盘价)/3
        V1 = 如果TYP>1日前的TYP,返回TYP*成交量(手),否则返回0的N日累和/如果TYP<1日前的TYP,返回TYP*成交量(手),否则返回0的N日累和
        MFI = 100-(100/(1+V1))
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数 N
    输出：
        MFI 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 MFI
    mfi = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'high', 'low', 'close', 'volume'],  count=timeperiod + 1)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            mfi[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            high_MFI = security_data['high']
            high_MFI = np.array(high_MFI)
            low_MFI = security_data['low']
            low_MFI = np.array(low_MFI)
            volume_MFI = security_data['volume']
            volume_MFI = np.array(volume_MFI)
            close_MFI = security_data['close']
            close_MFI = np.array(close_MFI)
            mfi[coin] = talib.MFI(
                high_MFI, low_MFI, close_MFI, volume_MFI)[-1]
    return mfi

# MTM-动量线


def MTM(security_list, check_date, timeperiod=12):
    '''
    计算公式：
        动量线:收盘价-N日前的收盘价
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数 N
    输出：
        MTM 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 MFI
    mtm = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=timeperiod + 1)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            mtm[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_MTM = security_data['close']
            # 昨天的收盘价 - N日前的收盘价
            mtm[coin] = close_MTM[-1] - close_MTM[-timeperiod - 1]
    return mtm

# ROC-变动率指标


def ROC(security_list, check_date, timeperiod=12):
    '''
    计算公式：
        ROC = 100*(收盘价-N日前的收盘价)/N日前的收盘价
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数 N
    输出：
        ROC 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 ROC
    roc = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=timeperiod * 20)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            roc[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_ROC = security_data['close']
            close_ROC = np.array(close_ROC)
            roc[coin] = talib.ROC(close_ROC, timeperiod)[-1]
    return roc

# RSI-相对强弱指标


def RSI(security_list, check_date, N1=6):
    '''
    计算公式：
        LC:=REF(CLOSE,1);
        RSI1:SMA(MAX(CLOSE-LC,0),N1,1)/SMA(ABS(CLOSE-LC),N1,1)*100;
        LC赋值:1日前的收盘价
        输出RSI1:收盘价-LC和0的较大值的N1日[1日权重]移动平均/收盘价-LC的绝对值的N1日[1日权重]移动平均*100
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N1：统计的天数 N1
    输出：
        RSI 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 MA
    rsi = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=N1 * 20)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            rsi[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_RSI = security_data['close']
            rsi[coin] = talib.RSI(np.array(close_RSI), N1)[-1]
    return rsi

# ACCER-幅度涨速


def ACCER(security_list, check_date, N=8):
    '''
    计算公式：
        ACCER:SLOPE(CLOSE,N)/CLOSE;
        输出幅度涨速:收盘价的N日线性回归斜率/收盘价
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
    输出：
        ACCER 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 ACCER
    accer = {}
    specificCount = N * 4
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=specificCount)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            accer[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_ACCER = security_data['close']
            close_ACCER = np.array(close_ACCER)
            # 计算ACCER
            preAccer = talib.LINEARREG_SLOPE(close_ACCER, N) / close_ACCER

            accer[coin] = preAccer[-1]
    return accer

# ADTM-动态买卖气指标


def ADTM(security_list, check_date, N=23, M=8):
    '''
    计算公式：
        DTM:=IF(OPEN<=REF(OPEN,1),0,MAX((HIGH-OPEN),(OPEN-REF(OPEN,1))));
        DBM:=IF(OPEN>=REF(OPEN,1),0,MAX((OPEN-LOW),(OPEN-REF(OPEN,1))));
        STM:=SUM(DTM,N);
        SBM:=SUM(DBM,N);
        ADTM:IF(STM>SBM,(STM-SBM)/STM,IF(STM=SBM,0,(STM-SBM)/SBM));
        MAADTM:MA(ADTM,M);
        DTM赋值:如果开盘价<=1日前的开盘价,返回0,否则返回(最高价-开盘价)和(开盘价-1日前的开盘价)的较大值
        DBM赋值:如果开盘价>=1日前的开盘价,返回0,否则返回(开盘价-最低价)和(开盘价-1日前的开盘价)的较大值
        STM赋值:DTM的N日累和
        SBM赋值:DBM的N日累和
        输出动态买卖气指标:如果STM>SBM,返回(STM-SBM)/STM,否则返回如果STM=SBM,返回0,否则返回(STM-SBM)/SBM
        输出MAADTM:ADTM的M日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M：统计的天数 M
    输出：
        ADTM和MAADTM 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 ADTM
    adtm_adtm = {}
    adtm_maadtm = {}
    maxN = max(N, M)
    specificCount = maxN * 3
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'open', 'high', 'low'],  count=specificCount)
        nan_count = list(np.isnan(security_data['open'])).count(True)
        if nan_count == len(security_data['open']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            adtm_adtm[coin] = np.nan
            adtm_maadtm[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            open_ADTM = security_data['open']
            high_ADTM = security_data['high']
            low_ADTM = security_data['low']

            # 计算OPEN - REF(OPEN,1)，便于下面计算
            diff_open = np.array(np.diff(open_ADTM))
            # 获取REF(OPEN,1)
            ref_open = np.array(open_ADTM[:-1])
            # 使open_ADTM，high_ADTM，low_ADTM的长度和ref_open的一致
            open_ADTM = np.array(open_ADTM[1:])
            high_ADTM = np.array(high_ADTM[1:])
            low_ADTM = np.array(low_ADTM[1:])
            # 计算DTM
            dtm = [0.0 if diff <= 0 else max(hg_minus_open, open_minus_ref) for diff, hg_minus_open, open_minus_ref in zip(
                diff_open, high_ADTM - open_ADTM, open_ADTM - ref_open)]
            # 计算DBM
            dbm = [0.0 if diff >= 0 else max(open_minus_low, open_minus_ref) for diff, open_minus_low, open_minus_ref in zip(
                diff_open, open_ADTM - low_ADTM, open_ADTM - ref_open)]
            # 计算STM
            stm = talib.SUM(np.array(dtm), N)
            # 计算SBM
            sbm = talib.SUM(np.array(dbm), N)
            # 计算STM-SBM，方便下面计算
            stm_minus_sbm = stm - sbm
            # 计算ADTM
            adtm = [sms / _stm if sms > 0 else (0.0 if sms == 0 else sms / _sbm)
                    for sms, _stm, _sbm in zip(stm_minus_sbm, stm, sbm)]
            # 计算MAADTM
            maadtm = np.mean(adtm[-M:])

            adtm_adtm[coin] = adtm[-1]
            adtm_maadtm[coin] = maadtm
    return adtm_adtm, adtm_maadtm

# BIAS_QL-乖离率_传统版


def BIAS_QL(security_list, check_date, N=6, M=6):
    '''
    计算公式：
        BIAS :(CLOSE-MA(CLOSE,N))/MA(CLOSE,N)*100;
        BIASMA :MA(BIAS,M);
        输出乖离率BIAS :(收盘价-收盘价的N日简单移动平均)/收盘价的N日简单移动平均*100
        输出BIASMA :乖离率的M日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M：统计的天数 M
    输出：
        BIAS和BIASMA 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 BIAS_QL
    bias = {}
    biasma = {}
    maxN = max(N, M)
    specificCount = maxN * 4
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=specificCount)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            bias[coin] = np.nan
            biasma[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_BIAS = security_data['close']
            close_BIAS = np.array(close_BIAS)

            # 计算MA(CLOSE, N)
            close_MA = talib.MA(close_BIAS, N)
            # 计算BIAS
            arrayBIAS = (close_BIAS - close_MA) / close_MA * 100
            # 计算MABIAS
            arrayMABIAS = talib.MA(arrayBIAS, M)

            bias[coin] = arrayBIAS[-1]
            biasma[coin] = arrayMABIAS[-1]
    return bias, biasma

# BIAS36-三六乖离


def BIAS_36(security_list, check_date,  M=6):
    '''
    计算公式：
        BIAS36:MA(CLOSE,3)-MA(CLOSE,6);
        BIAS612:MA(CLOSE,6)-MA(CLOSE,12);
        MABIAS:MA(BIAS36,M);
        输出三六乖离:收盘价的3日简单移动平均-收盘价的6日简单移动平均
        输出BIAS612:收盘价的6日简单移动平均-收盘价的12日简单移动平均
        输出MABIAS:BIAS36的M日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        M：统计的天数 M
    输出：
        BIAS36, BIAS612和MABIAS 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 BIAS36
    N1 = 3
    N2 = 6
    N3 = 12
    bias36 = {}
    bias612 = {}
    mabias = {}
    maxN = max(N1, N2, N3, M)
    specificCount = maxN * 4
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=specificCount)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市或刚上市，返回 NaN 值数据。" % coin)
            bias36[coin] = np.nan
            bias612[coin] = np.nan
            mabias[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_BIAS36 = security_data['close']
            close_BIAS36 = np.array(close_BIAS36)

            # 计算BIAS36
            preBias36 = talib.MA(close_BIAS36, N1) - talib.MA(close_BIAS36, N2)
            # 计算BIAS612
            preBias612 = talib.MA(close_BIAS36, N2) - \
                talib.MA(close_BIAS36, N3)
            # 计算MABIAS
            preMabis = talib.MA(preBias36, M)

            bias36[coin] = preBias36[-1]
            bias612[coin] = preBias612[-1]
            mabias[coin] = preMabis[-1]
    return bias36, bias612, mabias

# DKX-多空线


def DKX(security_list, check_date, M=10):
    '''
    计算公式：
        MID:=(3*CLOSE+LOW+OPEN+HIGH)/6;
        DKX:(20*MID+19*REF(MID,1)+18*REF(MID,2)+17*REF(MID,3)+
        16*REF(MID,4)+15*REF(MID,5)+14*REF(MID,6)+
        13*REF(MID,7)+12*REF(MID,8)+11*REF(MID,9)+
        10*REF(MID,10)+9*REF(MID,11)+8*REF(MID,12)+
        7*REF(MID,13)+6*REF(MID,14)+5*REF(MID,15)+
        4*REF(MID,16)+3*REF(MID,17)+2*REF(MID,18)+REF(MID,20))/210;
        MADKX:MA(DKX,M);
        MID赋值:(3*收盘价+最低价+开盘价+最高价)/6
        输出多空线:(20*MID+19*1日前的MID+18*2日前的MID+17*3日前的MID+16*4日前的MID+15*5日前的MID+14*6日前的MID+13*7日前的MID+12*8日前的MID+11*9日前的MID+10*10日前的MID+9*11日前的MID+8*12日前的MID+7*13日前的MID+6*14日前的MID+5*15日前的MID+4*16日前的MID+3*17日前的MID+2*18日前的MID+20日前的MID)/210
        输出MADKX:DKX的M日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        M：统计的天数 M
    输出：
        DKX和MADKX 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 DKX
    N = 20
    dkx_dkx = {}
    dkx_madkx = {}
    maxN = max(N, M)
    specificCount = maxN * 4
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'low', 'high', 'open'],  count=specificCount)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            dkx_dkx[coin] = np.nan
            dkx_madkx[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_DKX = security_data['close']
            low_DKX = security_data['low']
            high_DKX = security_data['high']
            open_DKX = security_data['open']
            close_DKX = np.array(close_DKX)
            low_DKX = np.array(low_DKX)
            high_DKX = np.array(high_DKX)
            open_DKX = np.array(open_DKX)

            # 计算MID
            mid = (3 * close_DKX + low_DKX + open_DKX + high_DKX) / 6
            # 计算DKX
            dkx = []
            temp = -maxN * 2
            while temp < 0:
                t_sum = 0.0
                # 对于有规律的部分，使用一个循环计算
                for i in range(0, N - 1):  # 0-18
                    t_sum += (N - i) * mid[temp - i]
                # 对于REF(MID, 20)，需要单独计算
                t_sum += mid[temp - N]
                t_res = t_sum / float(210)
                dkx.append(t_res)
                temp += 1
            # 计算MADKX
            madkx = np.mean(dkx[-M:])

            dkx_dkx[coin] = dkx[-1]
            dkx_madkx[coin] = madkx
    return dkx_dkx, dkx_madkx

# KD-随机指标KD


def KD(security_list, check_date, N=9, M1=3, M2=3):
    '''
    计算公式：
        RSV:=(CLOSE-LLV(LOW,N))/(HHV(HIGH,N)-LLV(LOW,N))*100;
        K:SMA(RSV,M1,1);
        D:SMA(K,M2,1);
        RSV赋值:(收盘价-N日内最低价的最低值)/(N日内最高价的最高值-N日内最低价的最低值)*100
        输出K:RSV的M1日[1日权重]移动平均
        输出D:K的M2日[1日权重]移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M1：统计的天数 M1
        M2：统计的天数 M2
    输出：
        K和D 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 计算SMA(X, N, M)， 即X的N日移动平均，M为权重, 若Y=SMA(X,N,M) 则 Y = (M*X+(N-M)*Y')/N,
    # 其中Y'表示上一周期Y值,N必须大于M。返回一个列表

    def SMA(X, N, M=1):
        ret = []
        i = 0
        length = len(X)
        # 跳过X中前面几个 nan 值
        while i < length:
            if np.isnan(X[i]):
                i += 1
            else:
                break
        if i == length:
            ret.append(np.nan)
            return ret
        preY = X[i]  # Y'
        ret.append(preY)
        while i < length:
            Y = (M * X[i] + (N - M) * preY) / float(N)
            ret.append(Y)
            preY = Y
            i += 1
        return ret
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 KD
    kd_K = {}
    kd_D = {}
    maxN = max(N, M1, M2)
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'low', 'high'],  count=maxN * 7)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            kd_K[coin] = np.nan
            kd_D[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_KD = security_data['close']
            high_KD = security_data['high']
            low_KD = security_data['low']
            close_KD = np.array(close_KD)
            high_KD = np.array(high_KD)
            low_KD = np.array(low_KD)
            # 计算 RSV
            list_RSV, temp = talib.STOCHF(
                high_KD, low_KD, close_KD, N, N, fastd_matype=0)
            # 计算 K
            list_K = SMA(list_RSV, M1, 1)
            # 计算 D
            list_D = SMA(list_K, M2, 1)
            if np.isnan(list_RSV[-1]):  # 标的刚上市期间，list_RSV为空，此时list_K, list_D的最后一个值也为空
                log.info("标的 %s 输入数据全是 NaN，该标的可能是刚上市，返回 NaN 值数据。" % coin)
            kd_K[coin] = list_K[-1]
            kd_D[coin] = list_D[-1]
    return kd_K, kd_D

# LWR-LWR威廉指标


def LWR(security_list, check_date, N=9, M1=3, M2=3):
    '''
    计算公式：
        RSV:= (HHV(HIGH,N)-CLOSE)/(HHV(HIGH,N)-LLV(LOW,N))*100;
        LWR1:SMA(RSV,M1,1);
        LWR2:SMA(LWR1,M2,1);
        RSV赋值: (N日内最高价的最高值-收盘价)/(N日内最高价的最高值-N日内最低价的最低值)*100
        输出LWR1:RSV的M1日[1日权重]移动平均
        输出LWR2:LWR1的M2日[1日权重]移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M1：统计的天数 M1
        M2：统计的天数 M2
    输出：
        LWR1和LWR2 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 计算SMA(X, N, M)， 即X的N日移动平均，M为权重, 若Y=SMA(X,N,M) 则 Y = (M*X+(N-M)*Y')/N,
    # 其中Y'表示上一周期Y值,N必须大于M。返回一个列表

    def SMA(X, N, M=1):
        ret = []
        i = 1
        length = len(X)
        # 跳过X中前面几个 nan 值
        while i < length:
            if np.isnan(X[i]):
                i += 1
            else:
                break
        if i < length:
            preY = X[i]  # Y'
            ret.append(preY)
        while i < length:
            Y = (M * X[i] + (N - M) * preY) / float(N)
            ret.append(Y)
            preY = Y
            i += 1
        return ret
    # RSV:= (HHV(HIGH,N)-CLOSE)/(HHV(HIGH,N)-LLV(LOW,N))*100;
    # 返回一个列表

    def STOCHF(high, low, close, N):
        VAR = []
        len_total = len(high)
        i = -len_total
        # 在N-1天之前，取不到LLV(LOW, N)和(HHV(HIGH,N)，所以VAR的值为nan
        while i < -(len_total - N + 1):
            t = np.nan
            VAR.append(t)
            i += 1
        # 终于有了LLV和HHV
        while i < -1:
            # 虽然都是+1，但意义不同，一个是弥补-N，一个是因为Python切片只能取到第二个参数所指的数的前一个
            llv = min(low[i - N + 1: i + 1])
            hhv = max(high[i - N + 1: i + 1])
            t = (hhv - close[i]) / (hhv - llv) * 100
            VAR.append(t)
            i += 1
        # 因为low[-x: 0]取不到数值，所以low/high/close中的最后N个要单独处理
        llv = min(low[i - N + 1:])
        hhv = max(high[i - N + 1:])
        t = (hhv - close[i]) / (hhv - llv) * 100
        VAR.append(t)
        return VAR
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 LWR
    lwr1 = {}
    lwr2 = {}
    maxN = max(N, M1, M2)
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'low', 'high'],  count=maxN * 6)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            lwr1[coin] = np.nan
            lwr2[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_LWR = security_data['close']
            high_LWR = security_data['high']
            low_LWR = security_data['low']
            close_LWR = np.array(close_LWR)
            high_LWR = np.array(high_LWR)
            low_LWR = np.array(low_LWR)
            # 计算 RSV
            list_RSV = STOCHF(high_LWR, low_LWR, close_LWR, N)
            # 计算 LWR1
            list_lwr1 = SMA(list_RSV, M1, 1)
            # 计算 LWR2
            list_lwr2 = SMA(list_lwr1, M2, 1)
            lwr1[coin] = list_lwr1[-1] if len(list_lwr1) != 0 else np.nan
            lwr2[coin] = list_lwr2[-1] if len(list_lwr2) != 0 else np.nan
    return lwr1, lwr2

# MARSI-相对强弱平均线


def MARSI(security_list, check_date, M1=10, M2=6):
    '''
    计算公式：
        DIF:=CLOSE-REF(CLOSE,1);
        VU:=IF(DIF>=0,DIF,0);
        VD:=IF(DIF<0,-DIF,0);
        MAU1:=MEMA(VU,M1);
        MAD1:=MEMA(VD,M1);
        MAU2:=MEMA(VU,M2);
        MAD2:=MEMA(VD,M2);
        # MEMA(X, N)相当于SMA(X, N, 1)
        RSI10:MA(100*MAU1/(MAU1+MAD1),M1);
        RSI6:MA(100*MAU2/(MAU2+MAD2),M2);
        DIF赋值:收盘价-1日前的收盘价
        VU赋值:如果DIF>=0,返回DIF,否则返回0
        VD赋值:如果DIF<0,返回-DIF,否则返回0
        MAU1赋值:VU的M1日平滑移动平均
        MAD1赋值:VD的M1日平滑移动平均
        MAU2赋值:VU的M2日平滑移动平均
        MAD2赋值:VD的M2日平滑移动平均
        输出RSI10:100*MAU1/(MAU1+MAD1)的M1日简单移动平均
        输出RSI6:100*MAU2/(MAU2+MAD2)的M2日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        M1：统计的天数 M1
        M2：统计的天数 M2
    输出：
        RSI10和RSI6 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 计算SMA(X, N, M)， 即X的N日移动平均，M为权重, 若Y=SMA(X,N,M) 则 Y = (M*X+(N-M)*Y')/N,
    # 其中Y'表示上一周期Y值,N必须大于M。返回一个列表

    def SMA(X, N, M=1):
        ret = []
        i = 0
        length = len(X)
        # 跳过X中前面几个 nan 值
        while i < length:
            if np.isnan(X[i]):
                i += 1
            else:
                break
        preY = X[i]  # Y'
        ret.append(preY)
        while i < length:
            Y = (M * X[i] + (N - M) * preY) / float(N)
            ret.append(Y)
            preY = Y
            i += 1
        return ret

    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 MARSI
    rsi10 = {}
    rsi6 = {}
    maxN = max(M1, M2)
    specificCount = maxN * 10
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=specificCount)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            rsi10[coin] = np.nan
            rsi6[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_MARSI = security_data['close']
            close_MARSI = np.array(close_MARSI)

            # 计算DIF，VU 和VD
            temp = -specificCount + 1
            vu = []
            vd = []
            while temp < 0:
                dif = close_MARSI[temp] - close_MARSI[temp - 1]
                if dif >= 0:
                    vu.append(dif)
                    vd.append(0)
                else:
                    vu.append(0)
                    vd.append(-dif)
                temp += 1
            # 计算MAU1, MAD1, MAU2, MAD2
            mau1 = SMA(vu, M1, 1)
            mad1 = SMA(vd, M1, 1)
            mau2 = SMA(vu, M2, 1)
            mad2 = SMA(vd, M2, 1)
            # 将MAU1, MAD1, MAU2, MAD2的类型变为ndarray，以便于计算
            mau1 = np.array(mau1)
            mad1 = np.array(mad1)
            mau2 = np.array(mau2)
            mad2 = np.array(mad2)
            # 计算RSI10和RSI6
            temp = 100 * mau1 / (mau1 + mad1)
            rsi10_MARSI = talib.MA(temp, M1)
            temp = 100 * mau2 / (mau2 + mad2)
            rsi6_MARSI = talib.MA(temp, M2)

            rsi10[coin] = rsi10_MARSI[-1]
            rsi6[coin] = rsi6_MARSI[-1]
    return rsi10, rsi6

# OSC-变动速率线


def OSC(security_list, check_date, N=20, M=6):
    '''
    计算公式：
        OSC:100*(CLOSE-MA(CLOSE,N));
        MAOSC:EXPMEMA(OSC,M);
        输出变动速率线OSC = 100*(收盘价-收盘价的N日简单移动平均)
        输出MAOSC = OSC的M日指数平滑移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M：统计的天数 M
    输出：
        OSC和MAOSC 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 OSC
    osc = {}
    maosc = {}
    maxN = max(N, M)
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=maxN * 10)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            osc[coin] = np.nan
            maosc[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_OSC = security_data['close']
            close_OSC = np.array(close_OSC)
            try:
                # 计算OSC
                list_osc = 100 * (close_OSC - talib.MA(close_OSC, N))
                # 计算MAOSC
                list_maosc = talib.EMA(list_osc, M)
            # 在security_data['close']不为全空，list_osc为全空时，talib.EMA会出错(只有新股才出现这种情况)
            except Exception as e:
                osc[coin] = np.nan
                maosc[coin] = np.nan
            else:
                osc[coin] = list_osc[-1]
                maosc[coin] = list_maosc[-1]
    return osc, maosc

# SKDJ-慢速随机指标


def SKDJ(security_list, check_date, N=9, M=3):
    '''
    计算公式：
        LOWV:=LLV(LOW,N);
        HIGHV:=HHV(HIGH,N);
        RSV:=EMA((CLOSE-LOWV)/(HIGHV-LOWV)*100,M);
        K:EMA(RSV,M);
        D:MA(K,M);
        LOWV赋值:N日内最低价的最低值
        HIGHV赋值:N日内最高价的最高值
        RSV赋值:(收盘价-LOWV)/(HIGHV-LOWV)*100的M日指数移动平均
        输出K:RSV的M日指数移动平均
        输出D:K的M日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M：统计的天数 M
    输出：
        K和D 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 SKDJ
    skdj_K = {}
    skdj_D = {}
    maxN = max(N, M)
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'low', 'high'],  count=maxN * 5)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            skdj_K[coin] = np.nan
            skdj_D[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_SKDJ = security_data['close']
            high_SKDJ = security_data['high']
            low_SKDJ = security_data['low']
            close_SKDJ = np.array(close_SKDJ)
            high_SKDJ = np.array(high_SKDJ)
            low_SKDJ = np.array(low_SKDJ)
            # 计算 RSV
            list_preRSV, temp = talib.STOCHF(
                high_SKDJ, low_SKDJ, close_SKDJ, N, N, fastd_matype=0)
            list_RSV = talib.EMA(list_preRSV, M)
            # 计算 K
            list_K = talib.EMA(list_RSV, M)
            # 计算 D
            list_D = talib.MA(list_K, M)

            skdj_K[coin] = list_K[-1]
            skdj_D[coin] = list_D[-1]
    return skdj_K, skdj_D

# UDL-引力线


def UDL(security_list, check_date, N1=3, N2=5, N3=10, N4=20, M=6):
    '''
    计算公式：
        UDL:(MA(CLOSE,N1)+MA(CLOSE,N2)+MA(CLOSE,N3)+MA(CLOSE,N4))/4;
        MAUDL:MA(UDL,M);
        输出引力线UDL = (收盘价的N1日简单移动平均+收盘价的N2日简单移动平均+收盘价的N3日简单移动平均+收盘价的N4日简单移动平均)/4
        输出MAUDL = UDL的M日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N1：统计的天数 N1
        N2：统计的天数 N2
        N3：统计的天数 N3
        N4：统计的天数 N4
        M：统计的天数 M
    输出：
        UDL和MAUDL 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 UDL
    udl = {}
    maudl = {}
    maxN = max(N1, N2, N3, N4, M)
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=maxN * 4)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            udl[coin] = np.nan
            maudl[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_UDL = security_data['close']
            close_UDL = np.array(close_UDL)
            # 计算UDL
            list_udl = (talib.MA(close_UDL, N1) + talib.MA(close_UDL, N2) +
                        talib.MA(close_UDL, N3) + talib.MA(close_UDL, N4)) / 4
            # 计算MAUDL
            list_maudl = talib.MA(list_udl, M)
            udl[coin] = list_udl[-1]
            maudl[coin] = list_maudl[-1]
    return udl, maudl

# WR-威廉指标


def WR(security_list, check_date, N=10, N1=6):
    '''
    计算公式：
        WR1:100*(HHV(HIGH,N)-CLOSE)/(HHV(HIGH,N)-LLV(LOW,N));
        WR2:100*(HHV(HIGH,N1)-CLOSE)/(HHV(HIGH,N1)-LLV(LOW,N1));
        输出WR1:100*(N日内最高价的最高值-收盘价)/(N日内最高价的最高值-N日内最低价的最低值)
        输出WR2:100*(N1日内最高价的最高值-收盘价)/(N1日内最高价的最高值-N1日内最低价的最低值)
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M：统计的天数 M
    输出：
        WR和MAWR 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np

    # WR:100*(HHV(HIGH,N)-CLOSE)/(HHV(HIGH,N)-LLV(LOW,N));
    # 返回一个列表
    def STOCHF(high, low, close, N):
        VAR = []
        len_total = len(high)
        i = -len_total
        # 在N-1天之前，取不到LLV(LOW, N)和(HHV(HIGH,N)，所以VAR的值为nan
        while i < -(len_total - N + 1):
            t = np.nan
            VAR.append(t)
            i += 1
        # 终于有了LLV和HHV
        while i < -1:
            # 虽然都是+1，但意义不同，一个是弥补-N，一个是因为Python切片只能取到第二个参数所指的数的前一个
            llv = min(low[i - N + 1: i + 1])
            hhv = max(high[i - N + 1: i + 1])
            t = (hhv - close[i]) / (hhv - llv) * 100
            VAR.append(t)
            i += 1
        # 因为low[-x: 0]取不到数值，所以low/high/close中的最后N个要单独处理
        llv = min(low[i - N + 1:])
        hhv = max(high[i - N + 1:])
        t = (hhv - close[i]) / (hhv - llv) * 100
        VAR.append(t)
        return VAR
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 WR
    wr1 = {}
    wr2 = {}
    maxN = max(N, N1)
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'high', 'low'],  count=maxN * 4)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            wr1[coin] = np.nan
            wr2[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_WR = security_data['close']
            high_WR = security_data['high']
            low_WR = security_data['low']

            close_WR = np.array(close_WR)
            high_WR = np.array(high_WR)
            low_WR = np.array(low_WR)

            # 计算WR
            list_wr1 = STOCHF(high_WR, low_WR, close_WR, N)
            # 计算MAWR
            list_wr2 = STOCHF(high_WR, low_WR, close_WR, N1)
            wr1[coin] = list_wr1[-1]
            wr2[coin] = list_wr2[-1]
    return wr1, wr2

# CYF-市场能量


def CYF(security_list, check_date, N=21):
    '''
    计算公式：
        CYF:100-100/(1+EMA(HSL,N));
        输出市场能量:100-100/(1+换手线的N日指数移动平均)
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
    输出：
        CYF 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 计算EMA(X, N, M)， 即X的N日指数移动平均，M为权重, 算法Y=(X*2 + Y'*(N - 1)) / (N + 1)

    def EMA(X, N):
        ret = reduce(lambda y, x: (2 * x + (N - 1) * y) / (N + 1), X)
        return ret
    # 计算 CYF
    cyf_cyf = {}
    specificCount = N + 1
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 获取最近specificCount个交易日
    dates = get_trade_days(end_date=check_date, count=specificCount)
    for coin in security_list:
        # 获取标的的上市和退市日期
        info_coin = get_security_info(coin)
        start = info_coin.start_date
        end = info_coin.end_date
        # 标的未上市或者刚上市或者已退市,
        if start >= dates[-1] or (dates[0] <= start and start <= dates[-1]) or end < dates[-1]:
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市，未上市或刚上市，返回 NaN 值数据。" % coin)
            cyf_cyf[coin] = np.nan
        else:
            q = query(
                valuation.turnover_ratio
            ).filter(
                valuation.code == coin
            )
            # 查询标的(coin)，在dates这些天的市值数据, 放到数组中
            turnover_ratio = [get_fundamentals(q, date=day)['turnover_ratio'][
                0] for day in dates]
            # 计算EMA(HSL,N)
            ema = EMA(turnover_ratio, N)
            # 计算CYF
            cyf = 100 - 100 / (1 + ema)
            cyf_cyf[coin] = cyf
    return cyf_cyf

# FSL-分水岭


def FSL(security_list, check_date):
    '''
    计算公式：
        SWL:(EMA(CLOSE,5)*7+EMA(CLOSE,10)*3)/10;
        SWS:DMA(EMA(CLOSE,12),MAX(1,100*(SUM(VOL,5)/(3*CAPITAL))));
        输出SWL:(收盘价的5日指数移动平均*7+收盘价的10日指数移动平均*3)/10+移动平均
        输出SWS:以1和100*(成交量(手)的5日累和/(3*当前流通股本(手)))的较大值为权重收盘价的12日指数移动平均的动态移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
    输出：
        SWL和SWS 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # DMA为动态移动平均。其计算方式是Y:DMA(X,A);则Y=A*X+(1-A)*REF(Y,1);其中A必须小于1

    def DMA(X, A):
        # 从 X 的不为空值的数据开始计算
        len_X = len(X)
        point = 0  # 开始计算DMA的起始位置
        for i in range(point, len_X):
            if np.isnan(X[i]):
                point += 1
            else:
                break
        if point == len_X:
            log.info('Wrong! X is Empty!')
        preY = X[point]  # REF(Y, 1)的初始值是X[]中的第一个有效值
        for i in range(point, len_X):
            if A[i] >= 1:
                A[i] = 0.9999
            if A[i] <= 0.0:
                A[i] = 0.0001
            Y = A[i] * X[i] + (1 - A[i]) * preY
            preY = Y
        return Y
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 FSL
    fsl_swl = {}
    fsl_sws = {}
    # 通达信中的FSL函数中没有指明N1,N2...，本程序为了表示方便，将计算公式中的一些常数以Nx的形式表示
    N1 = 3
    N2 = 5
    N3 = 7
    N4 = 10
    N5 = 12
    maxN = max(N1, N2, N3, N4, N5)
    specificCount = maxN + 5
    # 获取最近specificCount个交易日
    dates = get_trade_days(end_date=check_date, count=specificCount)
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'volume'],  count=specificCount)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            fsl_swl[coin] = np.nan
            fsl_sws[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_FSL = security_data['close']
            volume_FSL = security_data['volume']
            close_FSL = np.array(close_FSL)
            # 交易量以手为单位
            volume_FSL = [vol / 100 for vol in volume_FSL]
            # 为获取流通股本, 构造一个sqlalchemy.orm.query.Query对象
            q = query(
                valuation.circulating_cap
            ).filter(
                valuation.code == coin
            )
            # 容错处理，在对新股使用get_fundamentals()时会报错，因为根本就获取不了specificCount那么多天的流通股本数据
            try:
                # 计算最近specificCount个交易日的流通股本，单位为万股
                circulating_cap = np.array(
                    [get_fundamentals(q, day)['circulating_cap'][0] for day in dates])
            except IndexError:
                log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
                continue
            except Exception as e:
                log.info("Unexpected Error happened at %s:%s" % (coin, e))
                continue
            finally:
                fsl_swl[coin] = np.nan
                fsl_sws[coin] = np.nan
            # 流通股本以手为单位
            circulating_cap = [cap * 100 for cap in circulating_cap]
            # 计算EMA(CLOSE, N2)
            ema_N2 = talib.EMA(close_FSL, N2)
            # 计算EMA(CLOSE, N4)
            ema_N4 = talib.EMA(close_FSL, N4)
            # 计算EMA(CLOSE, N5)
            ema_N5 = talib.EMA(close_FSL, N5)
            # 计算SUM(VOL,N2)
            sum_N2 = talib.SUM(np.array(volume_FSL), N2)
            # 计算SWL
            swl = (ema_N2 * N3 + ema_N4 * N1) / 10

            pre_max = [100 * sum_t / (N1 * cap)
                       for sum_t, cap in zip(sum_N2, circulating_cap)]
            # 计算MAX(1,100*(SUM(VOL,5)/(3*CAPITAL)))
            pre_sws = [max(0.9999, num) for num in pre_max]
            # 计算SWS
            sws = DMA(ema_N5, pre_sws)

            fsl_swl[coin] = swl[-1]
            fsl_sws[coin] = sws
    return fsl_swl, fsl_sws

# TAPI-加权指数成交值


def TAPI(index_coin, security_list, check_date, M=6):
    '''
    计算公式：
        TAPI:AMOUNT/INDEXC;
        MATAIP:MA(TAPI,M);
        输出加权指数成交值(需下载日线):成交额(元)/大盘的收盘价
        输出MATAIP:TAPI的M日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        M：统计的天数 M
    输出：
        TAPI和MATAPI 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 浅拷贝
    new_security_list = security_list[:]
    # 因为计算TAPI时需要大盘的收盘价数据，所以将大盘标的放在标的列表的最前面
    new_security_list.insert(0, index_coin)
    # 计算 TAPI
    tapi_tapi = {}
    tapi_matapi = {}
    specificCount = M * 4
    point = 0     # 标记，用于判断当前标的是否是大盘
    indexc = 1.0  # 大盘收盘价
    for coin in new_security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'money'],  count=specificCount)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            if point == 0:
                # 大盘数据全为空(这种情况不会发生)
                log.info("大盘： %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            else:
                log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
                tapi_tapi[coin] = np.nan
                tapi_matapi[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            # 获取标的coin的收盘价和交易额
            close_TAPI = security_data['close']
            money_TAPI = security_data['money']
            close_TAPI = np.array(close_TAPI)
            money_TAPI = np.array(money_TAPI)
            if point == 0:
                # 把大盘的收盘价赋值给indexc
                indexc = close_TAPI
            else:
                # 计算TAPI
                tapi = money_TAPI / indexc
                # 计算MATAPI
                matapi = np.mean(tapi[-M:])

                tapi_tapi[coin] = tapi[-1]
                tapi_matapi[coin] = matapi
        point += 1
    return tapi_tapi, tapi_matapi

####################################################### 趋势型 ##############

# CHO-佳庆指标


def CHO(security_list, check_date, N1=10, N2=20, M=6):
    '''
    计算公式：
        MID:=SUM(VOL*(2*CLOSE-HIGH-LOW)/(HIGH+LOW),0);
        CHO:MA(MID,N1)-MA(MID,N2);
        MACHO:MA(CHO,M);
        MID赋值 = 成交量(手)*(2*收盘价-最高价-最低价)/(最高价+最低价)的历史累和
        输出佳庆指标 = MID的N1日简单移动平均-MID的N2日简单移动平均
        输出MACHO = CHO的M日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N1：统计的天数 N1
        N2：统计的天数 N2
    输出：
        CHO和MACHO的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    import pandas as pd
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 CHO
    maxN = max(N1, N2)
    cho_cho = {}
    cho_macho = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='daily', fields=[
                                  'low', 'high', 'close', 'volume'],  count=maxN * 4)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            cho_cho[coin] = np.nan
            cho_macho[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            volume_CHO = security_data['volume']
            close_CHO = security_data['close']
            high_CHO = security_data['high']
            low_CHO = security_data['low']

            # 使得交易量以手为单位
            j = 0
            for i in volume_CHO:
                # 商
                quo = i / 100
                quo = int(quo)
                volume_CHO[j] = quo
                j += 1

            # 计算MID值
            mid = {}
            temp = -maxN * 2
            while temp < 0:
                m = volume_CHO[temp] * (2 * close_CHO[temp] - high_CHO[temp] - low_CHO[
                                        temp]) / (high_CHO[temp] + low_CHO[temp])
                if temp != -maxN * 2:
                    m += mid[temp - 1]
                mid[temp] = m
                temp += 1

            # MID的N1日简单移动平均
            mid = pd.Series(mid)
            avg1 = talib.MA(np.array(mid), N1)
            # MID的N2日简单移动平均
            avg2 = talib.MA(np.array(mid), N2)

            # 计算佳庆指标CHO
            cho = avg1 - avg2
            macho = talib.MA(cho, M)

            cho_cho[coin] = cho[-1]
            cho_macho[coin] = macho[-1]
    return cho_cho, cho_macho

# CYE-市场趋势


def CYE(security_list, check_date):
    '''
     计算公式：
        MAL:=MA(CLOSE,5);
        MAS:=MA(MA(CLOSE,20),5);
        CYEL:(MAL-REF(MAL,1))/REF(MAL,1)*100;
        CYES:(MAS-REF(MAS,1))/REF(MAS,1)*100;
        MAL赋值:收盘价的5日简单移动平均
        MAS赋值:收盘价的20日简单移动平均的5日简单移动平均
        输出CYEL:(MAL-1日前的MAL)/1日前的MAL*100
        输出CYES:(MAS-1日前的MAS)/1日前的MAS*100
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
    输出：
        CYEL和CYES的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 CYE
    cye_cyel = {}
    cye_cyes = {}
    # 计算公式中为定值，在实现过程中以 N和M分别代替
    N = 5
    M = 20
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=M * 2)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            cye_cyel[coin] = np.nan
            cye_cyes[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_CYE = security_data['close']

            # 计算MAL
            close_CYE = np.array(close_CYE)
            mal = talib.MA(close_CYE, N)
            # 计算MAS
            pre_mas = talib.MA(close_CYE, M)
            mas = talib.MA(pre_mas, N)

            # 计算 CYEL和CYES
            temp = -1
            cyel = (mal[temp] - mal[temp - 1]) / mal[temp - 1] * 100
            cyes = (mas[temp] - mas[temp - 1]) / mas[temp - 1] * 100
            cye_cyel[coin] = cyel
            cye_cyes[coin] = cyes
    return cye_cyel, cye_cyes

# DBQR-对比强弱


def DBQR(index_coin, security_list, check_date, N=5, M1=10, M2=20, M3=60):
    '''
    计算公式：
        ZS:(INDEXC-REF(INDEXC,N))/REF(INDEXC,N);
        GG:(CLOSE-REF(CLOSE,N))/REF(CLOSE,N);
        MADBQR1:MA(GG,M1);
        MADBQR2:MA(GG,M2);
        MADBQR3:MA(GG,M3);
        输出ZS = (大盘的收盘价-N日前的大盘的收盘价)/N日前的大盘的收盘价  *上证综合指数*
        输出GG = (收盘价-N日前的收盘价)/N日前的收盘价
        输出MADBQR1 = GG的M1日简单移动平均
        输出MADBQR2 = GG的M2日简单移动平均
        输出MADBQR3 = GG的M3日简单移动平均
    输入：
        index_coin:大盘标的代码
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M1：统计的天数 M1
        M2：统计的天数 M2
        M3：统计的天数 M3
    输出：
        ZS, GG, MADBQR1, MADBQR2和MADBQR3的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    dbqr_zs = {}
    dbqr_gg = {}
    dbqr_madbqr1 = {}
    dbqr_madbqr2 = {}
    dbqr_madbqr3 = {}
    maxN = max(N, M1, M2, M3)
    # 计算ZS
    zs = []
    index_data = get_price(index_coin, end_date=check_date, frequency='1d', fields=[
                           'close'],  count=maxN * 3)
    nan_count = list(np.isnan(index_data['close'])).count(True)
    if nan_count == len(index_data['close']):
        log.info("大盘： %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" %
                 index_coin)
        dbqr_zs[index_coin] = np.nan
    else:
        close_Index = index_data['close']
        temp = -2 * maxN
        while temp < 0:
            t = (close_Index[temp] - close_Index[temp - N]) / \
                close_Index[temp - N]
            zs.append(t)
            temp += 1
        dbqr_zs[index_coin] = zs[-1]

    # 计算 DBQR
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=maxN * 3)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            dbqr_gg[coin] = np.nan
            dbqr_madbqr1[coin] = np.nan
            dbqr_madbqr2[coin] = np.nan
            dbqr_madbqr3[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_DBQR = security_data['close']

            # 计算GG
            gg = []
            temp = -2 * maxN
            while temp < 0:
                t = (close_DBQR[temp] - close_DBQR[temp - N]) / \
                    close_DBQR[temp - N]
                gg.append(t)
                temp += 1

            # 计算MADBQR1, MADBQR2, MADBQR3
            gg = np.array(gg)
            madbqr1 = talib.MA(gg, M1)
            madbqr2 = talib.MA(gg, M2)
            madbqr3 = talib.MA(gg, M3)

            dbqr_gg[coin] = gg[-1]
            dbqr_madbqr1[coin] = madbqr1[-1]
            dbqr_madbqr2[coin] = madbqr2[-1]
            dbqr_madbqr3[coin] = madbqr3[-1]
    return dbqr_zs, dbqr_gg, dbqr_madbqr1, dbqr_madbqr2, dbqr_madbqr3

# DMA-平均差


def DMA(security_list, check_date, N1=10, N2=50, M=10):
    '''
    计算公式：
        DIF:MA(CLOSE,N1)-MA(CLOSE,N2);
        DIFMA:MA(DIF,M);
        输出DIF:收盘价的N1日简单移动平均-收盘价的N2日简单移动平均
        输出DIFMA:DIF的M日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N1：统计的天数 N1
        N2: 统计的天数 N2
        M: 统计的天数 M
    输出：
        DIF和DIFMA 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 计算 DIF和 DIFMA
    dma_dif = {}
    dma_difma = {}
    maxN = max(N1, N2)
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='daily', fields=[
                                  'close'],  count=maxN * 2)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            dma_dif[coin] = np.nan
            dma_difma[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_DMA = security_data['close']
            # 计算收盘价的N1日简单移动平均
            close_N1 = talib.MA(np.array(close_DMA), N1)
            # 计算收盘价的N2日简单移动平均
            close_N2 = talib.MA(np.array(close_DMA), N2)
            # 计算dif 和difma
            dif = close_N1 - close_N2
            difma = talib.MA(dif, M)

            dma_dif[coin] = dif[-1]
            dma_difma[coin] = difma[-1]
    return dma_dif, dma_difma

# DMI - 趋向指标


def DMI(security_list, check_date, N=14,  MM=6):
    '''
    计算公式：
        MTR = 最高价-最低价和最高价-1日前的收盘价的绝对值的较大值和1日前的收盘价-最低价的绝对值的较大值的N日指数平滑移动平均
        HD = 最高价-1日前的最高价
        LD = 1日前的最低价-最低价
        DMP = 如果HD>0并且HD>LD,返回HD,否则返回0的N日指数平滑移动平均
        DMM = 如果LD>0并且LD>HD,返回LD,否则返回0的N日指数平滑移动平均
        输出PDI = DMP*100/MTR
        输出MDI = DMM*100/MTR
        输出ADX = MDI-PDI的绝对值/(MDI+PDI)*100的MM日指数平滑移动平均
        输出ADXR = ADX的MM日指数平滑移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        MM：统计的天数 MM
    输出：
        PDI, MDI, ADX, ADXR的值
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 PDI, MDI, ADX, ADXR
    dmi_pdi = {}
    dmi_mdi = {}
    dmi_adx = {}
    dmi_adxr = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'high', 'low', 'close'],  count=N * 20)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            dmi_pdi[coin] = np.nan
            dmi_mdi[coin] = np.nan
            dmi_adx[coin] = np.nan
            dmi_adxr[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_DMI = security_data['close']
            high_DMI = security_data['high']
            low_DMI = security_data['low']
            maxList = []
            dmpList = []
            dmmList = []
            # 获取 mtr
            temp = -N * 5
            while temp < 0:
                m = max(high_DMI[temp] - low_DMI[temp], abs(high_DMI[temp] -
                                                            close_DMI[temp - 1]), abs(close_DMI[temp - 1] - low_DMI[temp]))
                maxList.append(m)
                temp += 1
            mtr = talib.EMA(np.array(maxList), N)

            # 获取dmp 和 dmm
            temp = -N * 5
            while temp < 0:
                m = 0
                hd = high_DMI[temp] - high_DMI[temp - 1]
                ld = low_DMI[temp - 1] - low_DMI[temp]
                if hd > 0 and hd > ld:
                    m = hd
                else:
                    m = 0
                dmpList.append(m)
                if ld > 0 and ld > hd:
                    m = ld
                else:
                    m = 0
                dmmList.append(m)
                temp += 1

            dmpList, dmmList = np.nan_to_num(np.array(dmpList)), np.nan_to_num(np.array(dmmList))
            dmp = talib.EMA(dmpList, N)
            dmm = talib.EMA(dmmList, N)

            # 获取 mdi 和 pdi
            pdi = dmp * 100 / mtr
            mdi = dmm * 100 / mtr

            # 获取adx 和 adxr
            adxList = abs(mdi - pdi) / (mdi + pdi) * 100
            adx = talib.EMA(adxList, MM)
            adxr = talib.EMA(adx, MM)
            dmi_pdi[coin] = pdi[-1]
            dmi_mdi[coin] = mdi[-1]
            dmi_adx[coin] = adx[-1]
            dmi_adxr[coin] = adxr[-1]
    return dmi_pdi, dmi_mdi, dmi_adx, dmi_adxr

# DPO - 区间震荡线


def DPO(security_list, check_date, N=20,  M=6):
    '''
    计算公式：
        DPO:CLOSE-REF(MA(CLOSE,N),N/2+1);
        MADPO:MA(DPO,M);
        输出区间震荡线DPO = 收盘价-N/2+1日前的收盘价的N日简单移动平均
        输出MADPO = DPO的M日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M：统计的天数 M
    输出：
        DPO 和 MADPO 的值
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 DPO
    dpo_dpo = {}
    dpo_madpo = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=N * 20)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            dpo_dpo[coin] = np.nan
            dpo_madpo[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_DPO = security_data['close']
            dpoList = []
            # 获取收盘价的N日简单移动平均
            close_DPO = np.array(close_DPO)
            closeMA = talib.MA(close_DPO, N)

            # 收盘价 - N/2+1日前的收盘价的N日简单移动平均
            temp = -N
            while temp < 0:
                m = close_DPO[temp] - closeMA[temp - (N // 2 + 1)]
                dpoList.append(m)
                temp += 1
            # DPO的M日简单移动平均
            madpo = talib.MA(np.array(dpoList), M)
            dpo_dpo[coin] = dpoList[-1]
            dpo_madpo[coin] = madpo[-1]
    return dpo_dpo, dpo_madpo

# EMV-简易波动指标


def EMV(security_list, check_date, N=14, M=9):
    '''
    计算公式：
        VOLUME:=MA(VOL,N)/VOL;
        MID:=100*(HIGH+LOW-REF(HIGH+LOW,1))/(HIGH+LOW);
        EMV:MA(MID*VOLUME*(HIGH-LOW) / MA(HIGH-LOW,N),N);
        MAEMV:MA(EMV,M);
        VOLUME = 成交量(手)的N日简单移动平均/成交量(手)
        MID = 100*(最高价+最低价-1日前的最高价+最低价)/(最高价+最低价)
        输出EMV = MID*VOLUME*(最高价-最低价)/最高价-最低价的N日简单移动平均的N日简单移动平均
        输出MAEMV = EMV的M日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M：统计的天数 M
    输出：
        EMV和MAEMV的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 EMV
    emv = {}
    maemv = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='daily', fields=[
                                  'low', 'high', 'close', 'volume'],  count=N * 10)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            emv[coin] = np.nan
            maemv[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            volume_emv = security_data['volume']
            high_emv = security_data['high']
            low_emv = security_data['low']

            mid = []  # list
            volume = []  # list
            pre_emv = []  # list
            hgPlusl = high_emv + low_emv
            hgMinusl = high_emv - low_emv
            # 获取 volume
            volume_emv = np.array(volume_emv)
            volume = talib.MA(volume_emv, N) / volume_emv

            # 获取 mid
            temp = -5 * N
            while temp < 0:
                t = 100 * (hgPlusl[temp] - hgPlusl[temp - 1]) / hgPlusl[temp]
                mid.append(t)
                temp += 1

            # 获取(最高价-最低价的N日简单移动平均)
            hgMinusl = np.array(hgMinusl)
            ma_hgMinusl = talib.MA(hgMinusl, N)
            # 获取用于设置EMV的源数据
            temp = -5 * N
            while temp < 0:
                t = mid[temp] * volume[temp] * \
                    hgMinusl[temp] / ma_hgMinusl[temp]
                pre_emv.append(t)
                temp += 1
            # 获取 EMV
            pre_emv = np.array(pre_emv)
            pre_emv = np.nan_to_num(pre_emv)
            _emv = talib.MA(pre_emv, N)
            emv[coin] = _emv[-1]
            # 获取 MAEMV
            maemv[coin] = talib.MA(_emv, M)[-1]
    return emv, maemv

# GDX-鬼道线


def GDX(security_list, check_date, N=30, M=9):
    '''
     计算公式：
        AA:=ABS((2*CLOSE+HIGH+LOW)/4-MA(CLOSE,N))/MA(CLOSE,N);
        JAX:DMA(CLOSE,AA);
        压力线:(1+M/100)*JAX;
        支撑线:(1-M/100)*JAX;
        AA赋值:(2*收盘价+最高价+最低价)/4-收盘价的N日简单移动平均的绝对值/收盘价的N日简单移动平均
        输出济安线 = 以AA为权重收盘价的动态移动平均
        输出压力线 = (1+M/100)*JAX
        输出支撑线 = (1-M/100)*JAX
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M：统计的天数 M
    输出：
        济安线、压力线和支撑线的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six

    # DMA为动态移动平均。其计算方式是Y:DMA(X,A);则Y=A*X+(1-A)*REF(Y,1);其中A必须小于1
    def DMA(X, A):
        # 从 A 的不为空值的数据开始计算
        len_A = len(A)
        i = 0  # 开始计算DMA的起始位置
        while i < len_A:
            if np.isnan(A[i]):
                i += 1
            else:
                break
        if i == len_A:
            log.info('Wrong! A is Empty!')
        preY = X[i]  # REF(Y, 1)的初始值是X[]中的第一个有效值
        while i < len_A:
            if A[i] >= 1:
                A[i] = 0.9999
            elif A[i] <= 0:
                A[i] = 0.0001
            Y = A[i] * X[i] + (1 - A[i]) * preY
            preY = Y
            i += 1
        return preY

    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 GDX
    gdx_jax = {}
    gdx_ylx = {}
    gdx_zcx = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'high', 'low'],  count=N * 10)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            gdx_jax[coin] = np.nan
            gdx_ylx[coin] = np.nan
            gdx_zcx[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_GDX = security_data['close']
            high_GDX = security_data['high']
            low_GDX = security_data['low']

            # 计算AA值
            MA_Close_GDX = talib.MA(np.array(close_GDX), N)
            ClHgLo = (2 * close_GDX + high_GDX + low_GDX) / 4
            aa = abs(ClHgLo - MA_Close_GDX) / MA_Close_GDX

            # 计算济安线
            jax = DMA(np.array(close_GDX), aa)
            # 计算压力线和支撑线
            M = float(M)
            ylx = jax * (1 + M / 100)
            zcx = jax * (1 - M / 100)

            gdx_jax[coin] = jax
            gdx_ylx[coin] = ylx
            gdx_zcx[coin] = zcx
    return gdx_jax, gdx_ylx, gdx_zcx

# JLHB-绝路航标


def JLHB(security_list, check_date, N=7, M=5):
    '''
    计算公式：
        VAR1:=(CLOSE-LLV(LOW,60))/(HHV(HIGH,60)-LLV(LOW,60))*80;
        B:SMA(VAR1,N,1);
        VAR2:SMA(B,M,1);
        绝路航标:IF(CROSS(B,VAR2) AND B<40,50,0);

        VAR1赋值:(收盘价-60日内最低价的最低值)/(60日内最高价的最高值-60日内最低价的最低值)*80
        输出 B:VAR1的N日[1日权重]移动平均
        输出 VAR2:B的M日[1日权重]移动平均
        输出 绝路航标:如果B上穿VAR2 AND B<40,返回50,否则返回0
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M：统计的天数 M
    输出：
        B, VAR2和绝路航标 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six

    # 计算SMA(X, N, M)， 即X的N日移动平均，M为权重, 若Y=SMA(X,N,M) 则 Y = (M*X+(N-M)*Y')/N,
    # 其中Y'表示上一周期Y值,N必须大于M。返回一个列表
    def SMA(X, N, M=1):
        ret = []
        i = 1
        length = len(X)
        # 跳过X中前面几个 nan 值
        while i < length:
            if np.isnan(X[i]):
                i += 1
            else:
                break
        preY = X[i]  # Y'
        ret.append(preY)
        while i < length:
            Y = (M * X[i] + (N - M) * preY) / float(N)
            ret.append(Y)
            preY = Y
            i += 1
        return ret

    # VAR1:=(CLOSE-LLV(LOW,N))/(HHV(HIGH,N)-LLV(LOW,N))*80;
    # 返回一个列表
    # 功能等效于talib.STOCHF返回的第一个值
    def STOCHF(high, low, close, N=60):
        VAR = []
        len_total = len(high)
        i = -len_total
        # 在N-1天之前，取不到LLV(LOW, N)和(HHV(HIGH,N)，所以VAR的值为nan
        while i < -(len_total - N + 1):
            t = np.nan
            VAR.append(t)
            i += 1
        # 终于有了LLV和HHV
        while i < -1:
            # 虽然都是+1，但意义不同，一个是弥补-N，一个是因为Python切片只能取到第二个参数所指的数的前一个
            llv = min(low[i - N + 1: i + 1])
            hhv = max(high[i - N + 1: i + 1])
            t = (close[i] - llv) / (hhv - llv) * 80
            VAR.append(t)
            i += 1
        # 因为low[-x: 0]取不到数值，所以low/high/close中的最后N个要单独处理
        llv = min(low[i - N + 1:])
        hhv = max(high[i - N + 1:])
        t = (close[i] - llv) / (hhv - llv) * 80
        VAR.append(t)
        return VAR

    # 计算 JLHB
    jlhb_b = {}
    jlhb_var2 = {}
    jlhb_jlhb = {}
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'low', 'high', 'close'],  count=N * 20)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            jlhb_b[coin] = np.nan
            jlhb_var2[coin] = np.nan
            jlhb_jlhb[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_JLHB = security_data['close']
            high_JLHB = security_data['high']
            low_JLHB = security_data['low']

            close = np.array(close_JLHB)
            high = np.array(high_JLHB)
            low = np.array(low_JLHB)

            # 计算VAR1值
            var1 = STOCHF(high, low, close)
            # 计算 B 值
            b = SMA(var1, N, 1)
            # 计算 var2 值
            var2 = SMA(b, M, 1)
            # 计算 绝路航标
            jlhb = 0
            cross = 0
            if b[-2] < var2[-2] and b[-1] > var2[-1]:
                cross = 1
            if cross == 1 and b[-1] < 40:
                jlhb = 50

            jlhb_b[coin] = b[-1]
            jlhb_var2[coin] = var2[-1]
            jlhb_jlhb[coin] = jlhb
    return jlhb_b, jlhb_var2, jlhb_jlhb

# JS-加速线


def JS(security_list, check_date, N=5, M1=5, M2=10, M3=20):
    '''
    计算公式：
        JS:100*(CLOSE-REF(CLOSE,N))/(N*REF(CLOSE,N));
        MAJS1:MA(JS,M1);
        MAJS2:MA(JS,M2);
        MAJS3:MA(JS,M3);
        输出加速线 = 100*(收盘价-N日前的收盘价)/(N*N日前的收盘价)
        输出MAJS1 = JS的M1日简单移动平均
        输出MAJS2 = JS的M2日简单移动平均
        输出MAJS3 = JS的M3日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M1：统计的天数 M1
        M2：统计的天数 M2
        M3：统计的天数 M3
    输出：
        JS, MAJS1, MAJS2和MAJS3 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 JS
    js_jsx = {}
    js_majsx1 = {}
    js_majsx2 = {}
    js_majsx3 = {}
    maxN = max(N, M1, M2, M3)
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=maxN * 3)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            js_jsx[coin] = np.nan
            js_majsx1[coin] = np.nan
            js_majsx2[coin] = np.nan
            js_majsx3[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_JS = security_data['close']

            # 获取加速线 JS
            js = []
            temp = -2 * maxN
            while temp < 0:
                t = 100 * (close_JS[temp] - close_JS[temp - N]
                           ) / (N * close_JS[temp - N])
                js.append(t)
                temp += 1

            # 获取majs1, majs2, majs3
            js = np.array(js)
            majs1 = talib.MA(js, M1)
            majs2 = talib.MA(js, M2)
            majs3 = talib.MA(js, M3)

            js_jsx[coin] = js[-1]
            js_majsx1[coin] = majs1[-1]
            js_majsx2[coin] = majs2[-1]
            js_majsx3[coin] = majs3[-1]
    return js_jsx, js_majsx1, js_majsx2, js_majsx3

# MACD-平滑异同平均


def MACD(security_list, check_date, SHORT=12, LONG=26, MID=9):
    '''
    计算公式：
        DIF:EMA(CLOSE,SHORT)-EMA(CLOSE,LONG);
        DEA:EMA(DIF,MID);
        MACD:(DIF-DEA)*2,COLORSTICK;
        输出DIF = 收盘价的SHORT日指数移动平均-收盘价的LONG日指数移动平均
        输出DEA = DIF的MID日指数移动平均
        输出平滑异同平均 = (DIF-DEA)*2,COLORSTICK
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        SHORT：统计的天数 SHORT
        LONG：统计的天数 LONG
        MID：统计的天数 MID
    输出：
        DIF, DEA和MACD的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 MACD
    macd_dif = {}
    macd_dea = {}
    macd_macd = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=SHORT * 20)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            macd_dif[coin] = np.nan
            macd_dea[coin] = np.nan
            macd_macd[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_macd = security_data['close']

            # 调用talib的MACD函数，获取到dif, dea的列表
            dic = talib.MACD(np.array(close_macd), fastperiod=SHORT,
                             slowperiod=LONG, signalperiod=MID)
            macd_dif[coin] = dic[0][-1]
            macd_dea[coin] = dic[1][-1]
            # 计算 平滑移动平均macd
            macd_macd[coin] = (macd_dif[coin] - macd_dea[coin]) * 2
    return macd_dif, macd_dea, macd_macd

# QACD-快速异同平均


def QACD(security_list, check_date, N1=12, N2=26, M=9):
    '''
    计算公式：
        DIF:EMA(CLOSE,N1)-EMA(CLOSE,N2);
        MACD:EMA(DIF,M);
        DDIF:DIF-MACD;
        输出DIF = 收盘价的N1日指数移动平均-收盘价的N2日指数移动平均
        输出平滑异同平均 = DIF的M日指数移动平均
        输出DDIF = DIF-MACD
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N1：统计的天数 N1
        N2：统计的天数 N2
        M：统计的天数 M
    输出：
        DIF, MACD和DDIF的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 QACD
    qacd_dif = {}
    qacd_macd = {}
    qacd_ddif = {}
    maxN = max(N1, N2)
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=maxN * 20)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            qacd_dif[coin] = np.nan
            qacd_macd[coin] = np.nan
            qacd_ddif[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_QACD = security_data['close']

            # 获取收盘价的N1日指数移动平均
            n1_close = talib.EMA(np.array(close_QACD), N1)
            # 获取收盘价的N2日指数移动平均
            n2_close = talib.EMA(np.array(close_QACD), N2)
            # 获取dif
            dif = n1_close - n2_close
            qacd_dif[coin] = dif[-1]
            # 获取dif的M日指数移动平均
            qacd_macd[coin] = talib.EMA(dif, M)[-1]
            # 获取DDIF
            qacd_ddif[coin] = qacd_dif[coin] - qacd_macd[coin]
    return qacd_dif, qacd_macd, qacd_ddif

# QR-强弱指标


def QR(index_coin, security_list, check_date, N=21):
    '''
    计算公式：
        个股: (CLOSE-REF(CLOSE,N))/REF(CLOSE,N)*100;
        大盘: (INDEXC-REF(INDEXC,N))/REF(INDEXC,N)*100;
        强弱值:EMA(个股-大盘,2),COLORSTICK;

        输出个股 = (收盘价-N日前的收盘价)/N日前的收盘价*100
        输出 大盘 = (大盘的收盘价-N日前的大盘的收盘价)/N日前的大盘的收盘价*100
        输出 强弱值 = 个股-大盘的2日指数移动平均,COLORSTICK
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
    输出：
        个股，大盘和强弱指标的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    qr_dp = {}
    qr_gg = {}
    qr_qrz = {}
    # 计算大盘值
    dp = []
    index_data = get_price(index_coin, end_date=check_date, frequency='1d', fields=[
                           'close'],  count=N * 3)
    nan_count = list(np.isnan(index_data['close'])).count(True)
    if nan_count == len(index_data['close']):
        log.info("大盘： %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" %
                 index_coin)
        qr_dp[index_coin] = np.nan
    else:
        close_Index = index_data['close']
        temp = -2 * N
        while temp < 0:
            t = (close_Index[temp] - close_Index[temp - N]) / \
                close_Index[temp - N] * 100
            dp.append(t)
            temp += 1
        qr_dp[index_coin] = dp[-1]

    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=N * 5)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            qr_gg[coin] = np.nan
            qr_qrz[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_QR = security_data['close']

            # 计算个股值
            gg = []
            temp = -2 * N
            while temp < 0:
                t = (close_QR[temp] - close_QR[temp - N]) / \
                    close_QR[temp - N] * 100
                gg.append(t)
                temp += 1

            # 计算强弱值
            pre_qrz = np.array(gg) - np.array(dp)
            qrz = talib.EMA(pre_qrz, 2)

            qr_gg[coin] = gg[-1]
            qr_qrz[coin] = qrz[-1]
    return qr_gg, qr_dp, qr_qrz

# TRIX-终极指标


def TRIX(security_list, check_date, N=12, M=9):
    '''
    计算公式：
        MTR = 收盘价的N日指数移动平均的N日指数移动平均的N日指数移动平均
        输出三重指数平均线TRIX = (MTR-1日前的MTR)/1日前的MTR*100
        输出MATRIX = TRIX的M日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M：统计的天数 M
    输出：
        TRIX和MATRIX的值
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为TRIX和MATRIX。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 TRIX
    trix_trix = {}
    trix_matrix = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=N * 20)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            trix_trix[coin] = np.nan
            trix_matrix[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_TRIX = security_data['close']

            # 获取收盘价的N日指数移动平均的N日指数移动平均的N日指数移动平均 mtr
            ema_close = talib.EMA(np.array(close_TRIX), N)
            ema2_close = talib.EMA(ema_close, N)
            ema3_close = talib.EMA(ema2_close, N)
            mtr = ema3_close
            # 获取三重指数平均线 trix
            trix = []
            temp = -5 * N
            while temp < 0:
                t = (mtr[temp] - mtr[temp - 1]) / mtr[temp - 1] * 100
                trix.append(t)
                temp += 1
            trix_trix[coin] = trix[-1]
            # 获取 matrix
            trix_matrix[coin] = talib.MA(np.array(trix), M)[-1]
    return trix_trix, trix_matrix

# UOS-终极指标


def UOS(security_list, check_date, N1=7, N2=14, N3=28, M=6):
    '''
    计算公式：
        TH = 最高价和1日前的收盘价的较大值
        TL = 最低价和1日前的收盘价的较小值
        ACC1 = 收盘价-TL的N1日累和/TH-TL的N1日累和
        ACC2 = 收盘价-TL的N2日累和/TH-TL的N2日累和
        ACC3 = 收盘价-TL的N3日累和/TH-TL的N3日累和
        输出终极指标 = (ACC1*N2*N3+ACC2*N1*N3+ACC3*N1*N2)*100/(N1*N2+N1*N3+N2*N3)
        输出MAUOS = UOS的M日指数平滑移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N1：统计的天数 N1
        N2：统计的天数 N2
        N3：统计的天数 N3
        M：统计的天数 M
    输出：
        终极指标和MAUOS的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 UOS
    uos_ultiInc = {}
    uos_mauos = {}
    maxN = max(N1, N2, N3)
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'high', 'low', 'close'],  count=maxN * 10)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            uos_ultiInc[coin] = np.nan
            uos_mauos[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_UOS = security_data['close']
            high_UOS = security_data['high']
            low_UOS = security_data['low']

            # 计算TH 和 TL
            th = []
            tl = []
            temp = -5 * maxN
            while temp < 0:
                t = max(high_UOS[temp], close_UOS[temp - 1])
                th.append(t)
                t = min(low_UOS[temp], close_UOS[temp - 1])
                tl.append(t)
                temp += 1

            # 计算 CLOSE-TL 和 TH-TL
            THMinusTL = []
            CloseMinusTL = []
            temp = -5 * maxN
            while temp < 0:
                t = th[temp] - tl[temp]
                THMinusTL.append(t)
                t = close_UOS[temp] - tl[temp]
                CloseMinusTL.append(t)
                temp += 1

            # 计算acc1, acc2, acc3
            N = [N1, N2, N3]
            acc_TwoDi = []  # 二维列表
            i = 0
            length = len(N)
            while i < length:
                dividend = talib.SUM(np.array(CloseMinusTL), N[i])  # 被除数
                divisor = talib.SUM(np.array(THMinusTL), N[i])  # 被除数
                t = dividend / divisor
                acc_TwoDi.append(t)
                i += 1
            # 为acc1, acc2, acc3赋值
            acc1 = acc_TwoDi[0]
            acc2 = acc_TwoDi[1]
            acc3 = acc_TwoDi[2]

            # 计算 终极指标 ultiIndicator
            ultiIndicator = (acc1 * N2 * N3 + acc2 * N1 * N3 +
                             acc3 * N1 * N2) * 100 / (N1 * N2 + N1 * N3 + N2 * N3)
            # 计算 mauos
            mauos = talib.EMA(ultiIndicator, M)

            uos_ultiInc[coin] = ultiIndicator[-1]
            uos_mauos[coin] = mauos[-1]
    return uos_ultiInc, uos_mauos

# VMACD-量平滑移动平均


def VMACD(security_list, check_date, SHORT=12, LONG=26, MID=9):
    '''
    计算公式：
        DIF:EMA(VOL,SHORT)-EMA(VOL,LONG);
        DEA:EMA(DIF,MID);
        MACD:DIF-DEA,COLORSTICK;
        输出DIF:成交量(手)的SHORT日指数移动平均-成交量(手)的LONG日指数移动平均
        输出DEA:DIF的MID日指数移动平均
        输出平滑异同平均:DIF-DEA,COLORSTICK
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        SHORT：统计的天数 SHORT
        LONG：统计的天数 LONG
        MID：统计的天数 MID
    输出：
        DIF, DEA和MACD 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为DIF, DEA和MACD。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 VMACD
    vmacd_dif = {}
    vmacd_dea = {}
    vmacd_macd = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'volume'],  count=SHORT * 20)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            vmacd_dif[coin] = np.nan
            vmacd_dea[coin] = np.nan
            vmacd_macd[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            volume_VMACD = security_data['volume']

            # 使得交易量以手为单位
            length = len(volume_VMACD)
            i = 0
            while i < length:
                t = volume_VMACD[i]
                t /= 100
                if np.isnan(t):  # 避免有些标的的交易量数据为空值
                    t = np.nan
                else:
                    t = int(t)  # 数据表示，直接取整的误差比四舍五入要小
                volume_VMACD[i] = t
                i += 1
            # 计算成交量(手)的SHORT日指数移动平均
            short_VOL = talib.EMA(np.array(volume_VMACD), SHORT)
            # 计算成交量(手)的LONG日指数移动平均
            long_VOL = talib.EMA(np.array(volume_VMACD), LONG)
            dif = short_VOL - long_VOL
            dea = talib.EMA(dif, MID)
            macd = dif - dea
            vmacd_dif[coin] = dif[-1]
            vmacd_dea[coin] = dea[-1]
            vmacd_macd[coin] = macd[-1]
    return vmacd_dif, vmacd_dea, vmacd_macd

# VPT-量价曲线


def VPT(security_list, check_date, N=51, M=6):
    '''
    计算公式：
        VPT:SUM(VOL*(CLOSE-REF(CLOSE,1))/REF(CLOSE,1),N);
        MAVPT:MA(VPT,M);
        输出量价曲线VPT = 成交量(手)*(收盘价-1日前的收盘价)/1日前的收盘价的N日累和
        输出MAVPT = VPT的M日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M：统计的天数 M
    输出：
        VPT 和 MAVPT 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 VPT
    vpt_vpt = {}
    vpt_mavpt = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'volume', 'close'],  count=N * 2 + 1)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            vpt_vpt[coin] = np.nan
            vpt_mavpt[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_VPT = security_data['close']
            volume_VPT = security_data['volume']

            # 使交易量变为以手为单位
            length = len(volume_VPT)
            i = 0
            while i < length:
                t = volume_VPT[i]
                t /= 100
                t = round(t, 0)  # 与通达信数据相比，四舍五入的误差比直接取整要小
                volume_VPT[i] = t
                i += 1

            # 获取每天的成交量(手)*(收盘价-1日前的收盘价)/1日前的收盘价
            PreVPT = []
            temp = -2 * N
            while temp < 0:
                RefClose_VPT = close_VPT[temp - 1]
                CloseMinus = close_VPT[temp] - RefClose_VPT
                t = volume_VPT[temp] * CloseMinus / RefClose_VPT
                PreVPT.append(t)
                temp += 1

            # 获取VPT 和 MAVPT
            vpt = talib.SUM(np.array(PreVPT), N)
            mavpt = talib.MA(np.array(vpt), M)

            vpt_vpt[coin] = vpt[-1]
            vpt_mavpt[coin] = mavpt[-1]
    return vpt_vpt, vpt_mavpt

# WVAD-威廉变异离散量


def WVAD(security_list, check_date, N=24, M=6):
    '''
    计算公式：
        WVAD:SUM((CLOSE-OPEN)/(HIGH-LOW)*VOL,N)/10000;
        MAWVAD:MA(WVAD,M);
        输出WVAD:(收盘价-开盘价)/(最高价-最低价)*成交量(手)的N日累和/10000
        输出MAWVAD:WVAD的M日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M：统计的天数 M
    输出：
        WVAD 和 MAWVAD的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 WVAD
    wvad_wvad = {}
    wvad_mawvad = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'low', 'high', 'open', 'close', 'volume'],  count=N * 10)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            wvad_wvad[coin] = np.nan
            wvad_mawvad[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_WVAD = security_data['close']
            high_WVAD = security_data['high']
            low_WVAD = security_data['low']
            open_WVAD = security_data['open']
            volume_WVAD = security_data['volume']

            # 交易量以手为单位
            length = len(volume_WVAD)
            i = 0
            while i < length:
                t = volume_WVAD[i]
                t /= 100
                if np.isnan(t):
                    t = np.nan
                else:
                    t = int(t)  # 数据表示，直接取整的误差比四舍五入要小
                volume_WVAD[i] = t
                i += 1

            # 获取每天的(收盘价-开盘价)/(最高价-最低价)*成交量(手)数值
            temp = -2 * N
            pre_WVAD = []
            while temp < 0:
                t = (close_WVAD[temp] - open_WVAD[temp]) / \
                    (high_WVAD[temp] - low_WVAD[temp]) * volume_WVAD[temp]
                pre_WVAD.append(t)
                temp += 1
            # 获取wvad 和 mawvad
            wvad = talib.SUM(np.array(pre_WVAD), N) / 10000
            # 如果wvad全为nan，则返回nan
            ##############################
            mawvad = talib.MA(wvad, M) if not np.isnan(wvad).all() else [nan]
            wvad_wvad[coin] = wvad[-1]
            wvad_mawvad[coin] = mawvad[-1]
    return wvad_wvad, wvad_mawvad

####################################################### 能量型 ##############
# PSY-心理线


def PSY(security_list, check_date, timeperiod=12):
    '''
    计算公式：
        PSY:统计 N 日中满足收盘价>1日前的收盘价的天数/N*100
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数 N
    输出：0
        PSY 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 PSY
    psy = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='daily', fields=[
                                  'close'],  count=timeperiod + 1)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            psy[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_PSY = security_data['close']
            psy_dif = np.diff(close_PSY)[-timeperiod:]
            psy_sign = np.where(psy_dif > 0, 1.0, 0)
            Sum = np.sum(psy_sign)
            psy[coin] = (Sum / timeperiod * 100)
    return psy

# VR-成交量变异率


def VR(security_list, check_date, N=26, M=6):
    '''
    计算公式：
        TH:=SUM(IF(CLOSE>REF(CLOSE,1),VOL,0),N);
        TL:=SUM(IF(CLOSE<REF(CLOSE,1),VOL,0),N);
        TQ:=SUM(IF(CLOSE=REF(CLOSE,1),VOL,0),N);
        VR:100*(TH*2+TQ)/(TL*2+TQ);
        MAVR:MA(VR,M);
        TH赋值:如果收盘价>1日前的收盘价,返回成交量(手),否则返回0的N日累和
        TL赋值:如果收盘价<1日前的收盘价,返回成交量(手),否则返回0的N日累和
        TQ赋值:如果收盘价=1日前的收盘价,返回成交量(手),否则返回0的N日累和
        输出VR:100*(TH*2+TQ)/(TL*2+TQ)
        输出MAVR:VR的M日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M：统计的天数 M
    输出：
        VR和MAVR 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 VR
    vr_vr = {}
    vr_mavr = {}
    maxN = max(N, M)
    specificCount = maxN * 3
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'volume'],  count=specificCount)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            vr_vr[coin] = np.nan
            vr_mavr[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_VR = security_data['close']
            volume_VR = security_data['volume']
            close_VR = np.array(close_VR)
            # 使交易量以手为单位
            volume_VR = np.array([round(vol / 100, 0) for vol in volume_VR])

            # 计算CLOSE-REF(CLOSE,1)
            close_minus_ref = np.diff(close_VR)
            # 使成交量的数据个数与close_minus_ref相同
            volume_VR = volume_VR[1:]
            # 获取计算TH, TL, TQ的源数据
            pre_th = [vol if c_m_ref > 0 else 0.0 for vol,
                      c_m_ref in zip(volume_VR, close_minus_ref)]
            pre_tl = [vol if c_m_ref < 0 else 0.0 for vol,
                      c_m_ref in zip(volume_VR, close_minus_ref)]
            pre_tq = [vol if c_m_ref == 0 else 0.0 for vol,
                      c_m_ref in zip(volume_VR, close_minus_ref)]

            # 计算TH, TL, TQ
            th = talib.SUM(np.array(pre_th), N)
            tl = talib.SUM(np.array(pre_tl), N)
            tq = talib.SUM(np.array(pre_tq), N)
            # 计算VR
            vr = 100 * (th * 2 + tq) / (tl * 2 + tq)
            # 计算MAVR
            mavr = np.mean(vr[-M:])

            vr_vr[coin] = vr[-1]
            vr_mavr[coin] = mavr
    return vr_vr, vr_mavr

# BRAR-情绪指标


def BRAR(security_list, check_date, N=26):
    '''
    计算公式：
        BR:SUM(MAX(0,HIGH-REF(CLOSE,1)),N)/SUM(MAX(0,REF(CLOSE,1)-LOW),N)*100;
        AR:SUM(HIGH-OPEN,N)/SUM(OPEN-LOW,N)*100;
        输出BR:0和最高价-1日前的收盘价的较大值的N日累和/0和1日前的收盘价-最低价的较大值的N日累和*100
        输出AR:最高价-开盘价的N日累和/开盘价-最低价的N日累和*100
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
    输出：
        BR和AR 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 BRAR
    brar_br = {}
    brar_ar = {}
    specificCount = N + 2
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'high', 'low', 'open'],  count=specificCount)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            brar_br[coin] = np.nan
            brar_ar[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_BRAR = security_data['close']
            high_BRAR = security_data['high']
            low_BRAR = security_data['low']
            open_BRAR = security_data['open']

            # 此时需要把数据转换成array类型，因为若是DataFrame，
            # 在之后的计算中会以对应日期来计算，那么计算的结果就不是减前一天的收盘价了
            ref_close_BRAR = np.array(close_BRAR[:-1])
            high_BRAR = np.array(high_BRAR[1:])
            low_BRAR = np.array(low_BRAR[1:])
            open_BRAR = np.array(open_BRAR[1:])
            max1 = [max(0.0, num) for num in (high_BRAR - ref_close_BRAR)]
            max2 = [max(0.0, num) for num in (ref_close_BRAR - low_BRAR)]
            # 计算BR
            sum1 = sum(max1[-N:])
            sum2 = sum(max2[-N:])
            br = sum1 / sum2 * 100
            # 计算AR
            sum3 = talib.SUM(high_BRAR - open_BRAR, N)[-1]
            sum4 = talib.SUM(open_BRAR - low_BRAR, N)[-1]
            ar = sum3 / sum4 * 100

            brar_br[coin] = br
            brar_ar[coin] = ar
    return brar_br, brar_ar

# CR-带状能量线


def CR(security_list, check_date, N=26, M1=10, M2=20, M3=40, M4=62):
    '''
    计算公式：
        MID:=REF(HIGH+LOW,1)/2;
        CR:SUM(MAX(0,HIGH-MID),N)/SUM(MAX(0,MID-LOW),N)*100;
        MA1:REF(MA(CR,M1),M1/2.5+1);
        MA2:REF(MA(CR,M2),M2/2.5+1);
        MA3:REF(MA(CR,M3),M3/2.5+1);
        MA4:REF(MA(CR,M4),M4/2.5+1);
        MID赋值:1日前的最高价+最低价/2
        输出带状能量线:0和最高价-MID的较大值的N日累和/0和MID-最低价的较大值的N日累和*100
        输出MA1:M1/2.5+1日前的CR的M1日简单移动平均
        输出均线:M2/2.5+1日前的CR的M2日简单移动平均
        输出MA3:M3/2.5+1日前的CR的M3日简单移动平均
        输出MA4:M4/2.5+1日前的CR的M4日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M1：统计的天数 M1
        M2：统计的天数 M2
        M3：统计的天数 M3
        M4：统计的天数 M4
    输出：
        CR和MA1，MA2，MA3，MA4 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 CR
    cr_cr = {}
    cr_ma1 = {}
    cr_ma2 = {}
    cr_ma3 = {}
    cr_ma4 = {}
    maxN = max(N, M1, M2, M3, M4)
    specificCount = maxN * 2
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'high', 'low'],  count=specificCount)
        nan_count = list(np.isnan(security_data['high'])).count(True)
        if nan_count == len(security_data['low']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            cr_cr[coin] = np.nan
            cr_ma1[coin] = np.nan
            cr_ma2[coin] = np.nan
            cr_ma3[coin] = np.nan
            cr_ma4[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            high_CR = security_data['high']
            low_CR = security_data['low']
            high_CR = np.array(high_CR)
            low_CR = np.array(low_CR)

            # 计算MID
            t_mid = (high_CR + low_CR) / 2
            # 让mid等于前一天的值
            mid = t_mid[:-1]
            # 计算MAX(0,HIGH-MID)和MAX(0,MID-LOW)
            # 让high_CR, low_CR的长度与mid相同，以便于计算
            high_CR = high_CR[1:]
            low_CR = low_CR[1:]
            max1 = np.array([max(0.0, num) for num in (high_CR - mid)])
            max2 = np.array([max(0.0, num) for num in (mid - low_CR)])
            # 计算CR
            cr = talib.SUM(max1, N) / talib.SUM(max2, N) * 100
            # 计算MA1，MA2，MA3，MA4
            ma_list = []
            num_list = [M1, M2, M3, M4]
            for num in num_list:
                day = num / 2.5 + 1
                day = int(day)
                ma = talib.MA(cr, num)[-day - 1]
                ma_list.append(ma)

            cr_cr[coin] = cr[-1]
            cr_ma1[coin] = ma_list[0]
            cr_ma2[coin] = ma_list[1]
            cr_ma3[coin] = ma_list[2]
            cr_ma4[coin] = ma_list[3]
    return cr_cr, cr_ma1, cr_ma2, cr_ma3, cr_ma4


# CYR-市场强弱
def CYR(security_list, check_date, N=13, M=5):
    '''
    计算公式：
        DIVE:=0.01*EMA(AMOUNT,N)/EMA(VOL,N);
        CYR:(DIVE/REF(DIVE,1)-1)*100;
        MACYR:MA(CYR,M);
        DIVE赋值:0.01*成交额(元)的N日指数移动平均/成交量(手)的N日指数移动平均
        输出市场强弱:(DIVE/1日前的DIVE-1)*100
        输出MACYR:CYR的M日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M：统计的天数 M
    输出：
        CYR和MACYR 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 CYR
    cyr_cyr = {}
    cyr_macyr = {}
    maxN = max(N, M)
    specificCount = maxN * 5
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'volume', 'money'],  count=specificCount)
        nan_count = list(np.isnan(security_data['volume'])).count(True)
        if nan_count == len(security_data['volume']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            cyr_cyr[coin] = np.nan
            cyr_macyr[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            amount_CYR = security_data['money']
            volume_CYR = security_data['volume']

            # 交易量以手为单位
            volume_CYR = [round(vol / 100, 2) for vol in volume_CYR]
            ema_amount = talib.EMA(np.array(amount_CYR), N)
            ema_volume = talib.EMA(np.array(volume_CYR), N)
            # 计算DIVE
            dive = 0.01 * ema_amount / ema_volume
            preDive = dive[:-1]
            dive = dive[1:]
            # 计算CYR
            cyr = (dive / preDive - 1) * 100
            # 计算MACYR
            macyr = np.mean(cyr[-M:])

            cyr_cyr[coin] = cyr[-1]
            cyr_macyr[coin] = macyr
    return cyr_cyr, cyr_macyr

# MASS-梅斯线


def MASS(security_list, check_date, N1=9, N2=25, M=6):
    '''
    计算公式：
        MASS:SUM(MA(HIGH-LOW,N1)/MA(MA(HIGH-LOW,N1),N1),N2);
        MAMASS:MA(MASS,M);
        输出梅斯线:最高价-最低价的N1日简单移动平均/最高价-最低价的N1日简单移动平均的N1日简单移动平均的N2日累和
        输出MAMASS:MASS的M日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N1：统计的天数 N1
        N2：统计的天数 N2
        M：统计的天数 M
    输出：
        MASS和MAMASS 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 MASS
    mass_mass = {}
    mass_mamass = {}
    maxN = max(N1, N2, M)
    specificCount = maxN * 4
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'high', 'low'], count=specificCount)
        nan_count = list(np.isnan(security_data['high'])).count(True)
        if nan_count == len(security_data['high']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            mass_mass[coin] = np.nan
            mass_mamass[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            high_MASS = security_data['high']
            low_MASS = security_data['low']
            high_MASS = np.array(high_MASS)
            low_MASS = np.array(low_MASS)

            # 计算MASS
            MA_HgMinusLow = talib.MA(high_MASS - low_MASS, N1)
            MA_MA_HgMinusLow = talib.MA(MA_HgMinusLow, N1)
            mass = talib.SUM(MA_HgMinusLow / MA_MA_HgMinusLow, N2)
            # 计算MAMASS
            mamass = talib.MA(mass, M)[-1]

            mass_mass[coin] = mass[-1]
            mass_mamass[coin] = mamass
    return mass_mass, mass_mamass


# PCNT-幅度比
def PCNT(security_list, check_date, M=5):
    '''
    计算公式：
        PCNT:(CLOSE-REF(CLOSE,1))/CLOSE*100;
        MAPCNT:EXPMEMA(PCNT,M);
        输出幅度比:(收盘价-1日前的收盘价)/收盘价*100
        输出MAPCNT:PCNT的M日指数平滑移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        M：统计的天数 M
    输出：
        PCNT和MAPCNT 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 PCNT
    pcnt_pcnt = {}
    pcnt_mapcnt = {}
    specificCount = M * 4
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=specificCount)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            pcnt_pcnt[coin] = np.nan
            pcnt_mapcnt[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_PCNT = security_data['close']
            close_PCNT = np.array(close_PCNT)

            refClose_PCNT = close_PCNT[:-1]
            close_PCNT = close_PCNT[1:]
            # 计算PCNT
            pcnt = (close_PCNT - refClose_PCNT) / close_PCNT * 100
            # 计算MAPCNT
            mapcnt = talib.EMA(pcnt, M)
            pcnt_pcnt[coin] = pcnt[-1]
            pcnt_mapcnt[coin] = mapcnt[-1]
    return pcnt_pcnt, pcnt_mapcnt


####################################################### 成交量型 #############

# OBV-累积能量线
def OBV(security_list, check_date, timeperiod=30):
    '''
    计算公式：
        VA = 如果收盘价>1日前的收盘价,返回成交量(手),否则返回-成交量(手)
        OBV = 如果收盘价=1日前的收盘价,返回0,否则返回VA的历史累和
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数 N
    输出：
        OBV 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 OBV
    OBV = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'volume'],  count=timeperiod)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            OBV[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_OBV = security_data['close']
            volume_OBV = security_data['volume']
            close_OBV = np.array(close_OBV)
            volume_OBV = np.array(volume_OBV)
            OBV[coin] = talib.OBV(close_OBV, volume_OBV)[-1]
    return OBV

# AMO-成交金额


def AMO(security_list, check_date, M1=5, M2=10):
    '''
    计算公式：
        AMOW:AMOUNT/10000.0,VOLSTICK;
        AMO1:MA(AMOW,M1);
        AMO2:MA(AMOW,M2);
        输出AMOW:成交额(元)/10000.0,VOLSTICK
        输出AMO1:AMOW的M1日简单移动平均
        输出AMO2:AMOW的M2日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        M1：统计的天数 M1
        M2：统计的天数 M2
    输出：
        AMOW，AMO1和AMO2 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 AMO
    amo_amow = {}
    amo_amo1 = {}
    amo_amo2 = {}
    maxN = max(M1, M2)
    specificCount = maxN * 4
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'money'],  count=specificCount)
        nan_count = list(np.isnan(security_data['money'])).count(True)
        if nan_count == len(security_data['money']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            amo_amow[coin] = np.nan
            amo_amo1[coin] = np.nan
            amo_amo2[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            money_AMO = security_data['money']
            money_AMO = np.array(money_AMO)

            # 计算AMOW
            amow = money_AMO / 10000.0
            # 计算AMO1
            amo1 = np.mean(amow[-M1:])
            # 计算AMO2
            amo2 = np.mean(amow[-M2:])

            amo_amow[coin] = amow[-1]
            amo_amo1[coin] = amo1
            amo_amo2[coin] = amo2
    return amo_amow, amo_amo1, amo_amo2

# CCL-持仓量（适用于期货）


def CCL(futures_list, check_date, M=5):
    '''
    计算公式：
        持仓量:VOLINSTK;
        MACCL:MA(持仓量,M);
        输出持仓量:持仓量
        输出MACCL:持仓量的M日简单移动平均
    输入：
        futures_list:期货代码列表
        check_date：要查询数据的日期
        M：统计的天数 M
    输出：
        CCL和MACCL 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(futures_list, six.string_types):
        futures_list = [futures_list]
    # 计算 CCL
    ccl_ccl = {}
    ccl_maccl = {}
    specificCount = M
    for coin in futures_list:
        futures_data = get_extras(
            'futures_positions', coin, end_date=check_date, count=specificCount)
        nan_count = list(np.isnan(futures_data[coin])).count(True)
        if nan_count == len(futures_data[coin]):
            log.info("金融期货 %s 输入数据全是 NaN，该期货可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            ccl_ccl[coin] = np.nan
            ccl_maccl[coin] = np.nan
        else:
            position_CCL = futures_data[coin]
            position_CCL = np.array(position_CCL)
            # 计算MACCL
            maccl = np.mean(position_CCL[-M:])
            ccl_ccl[coin] = position_CCL[-1]
            ccl_maccl[coin] = maccl
    return ccl_ccl, ccl_maccl

# DBLB-对比量比


def DBLB(index_coin, security_list, check_date, N=5, M=5):
    '''
    计算公式：
        GG:=VOL/SUM(REF(VOL,1),N);
        ZS:=INDEXV/SUM(REF(INDEXV,1),N);
        DBLB:GG/ZS;
        MADBLB:MA(DBLB,M);
        GG赋值:成交量(手)/1日前的成交量(手)的N日累和
        ZS赋值:大盘的成交量/1日前的大盘的成交量的N日累和
        输出对比量比(需下载日线):GG/ZS
        输出MADBLB:DBLB的M日简单移动平均
    输入：
        index_coin: 大盘标的代码
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M：统计的天数 M
    输出：
        DBLB和MADBLB 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 需要浅拷贝，不能是对象的赋值，不然会使原始的security_list也会增加一项
    new_security_list = security_list[:]
    # 因为计算security_list中标的的DBLB需要由大盘数据得出的ZS，且两者计算方式相同，
    # 所以把大盘代码放在标的列表的最前面，把它当做普通标的来计算
    new_security_list.insert(0, index_coin)
    # 标记
    i = 0
    # 计算 DBQRV
    dblb_dblb = {}
    dblb_madblb = {}
    # 全局变量zs
    zs = 0.0
    specificCount = N * 2
    for coin in new_security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'volume'],  count=specificCount)
        nan_count = list(np.isnan(security_data['volume'])).count(True)
        if nan_count == len(security_data['volume']):
            # 为了避免大盘标的代码和原本标的列表中的代码相同引发的冲突，使用循环次数来判断当前标的是否为大盘
            if i == 0:
                log.info("大盘 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
                # 这种情况几乎不会出现，但为了避免出错，所以让zs=1
                zs = 1
            else:
                log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
                dblb_dblb[coin] = np.nan
                dblb_madblb[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            volume_DBQRV = security_data['volume']
            volume_DBQRV = np.array(volume_DBQRV)
            # 计算REF(VOL,N)
            ref_volume = volume_DBQRV[:-1]
            volume_DBQRV = volume_DBQRV[1:]
            # 计算SUM(REF(VOL,1),N)
            sum_ref = talib.SUM(ref_volume, N)
            # 计算ZS/GG
            res = volume_DBQRV / sum_ref
            if i == 0:
                zs = res
            else:
                gg = res
                # 计算DBLB
                dblb = gg / zs
                # 计算MADBLB
                madblb = np.mean(dblb[-M:])

                dblb_dblb[coin] = dblb[-1]
                dblb_madblb[coin] = madblb
        i += 1
    return dblb_dblb, dblb_madblb

# DBQRV-对比强弱量


def DBQRV(index_coin, security_list, check_date, N=5):
    '''
    计算公式：
        ZS:(INDEXV-REF(INDEXV,N))/REF(INDEXV,N);
        GG:(VOL-REF(VOL,N))/REF(VOL,N);
        输出ZS:(大盘的成交量-N日前的大盘的成交量)/N日前的大盘的成交量
        输出GG:(成交量(手)-N日前的成交量(手))/N日前的成交量(手)
    输入：
        index_coin: 大盘标的代码
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
    输出：
        ZS和GG 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 需要浅拷贝，不能是对象的赋值，不然会使原始的security_list也会增加一项
    new_security_list = security_list[:]
    # 因为计算security_list中标的的GG和计算大盘数据得出的ZS计算方式相同，
    # 所以把大盘代码放在标的列表的最后，把大盘标的当做普通标的来处理
    new_security_list.append(index_coin)
    length = len(new_security_list)
    i = 0
    # 计算 DBQRV
    dbqrv_zs = {}
    dbqrv_gg = {}
    specificCount = N * 4
    for coin in new_security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'volume'],  count=specificCount)
        nan_count = list(np.isnan(security_data['volume'])).count(True)
        if nan_count == len(security_data['volume']):
            # 为了避免大盘标的代码和原本标的列表中的代码相同引发的冲突，使用循环次数来判断当前标的是否为大盘
            if i == length - 1:
                log.info("大盘 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
                dbqrv_zs[coin] = np.nan
            else:
                log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
                dbqrv_gg[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            volume_DBQRV = security_data['volume']
            volume_DBQRV = np.array(volume_DBQRV)
            # 计算REF(VOL,N)
            ref_volume = volume_DBQRV[:-N]
            # 使交易量的数据个数与ref_volume相同
            volume_Index = volume_DBQRV[N:]
            # 计算GG/ZS
            res = (volume_Index - ref_volume) / ref_volume
            if i == length - 1:
                dbqrv_zs[coin] = res[-1]
            else:
                dbqrv_gg[coin] = res[-1]
        i += 1
    return dbqrv_zs, dbqrv_gg

# HSL-换手线


def HSL(security_list, check_date, N=5):
    '''
    计算公式：
        HSL:IF((SETCODE==0||SETCODE==1),100*VOL,VOL)/(FINANCE(7)/100);
        MAHSL:MA(HSL,N);
        输出换手线:如果(市场类型(0或者市场类型或者1),返回100*成交量(手),否则返回成交量(手)/(流通股本(股)/100)
        输出MAHSL:HSL的N日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
    输出：
        HSL和MAHSL 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 HSL
    hsl_hsl = {}
    hsl_mahsl = {}
    # 程序执行速度受数据个数（specificCount）影响较大
    specificCount = N * 1
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'volume', 'high'],  count=specificCount)
        nan_count = list(np.isnan(security_data['volume'])).count(True)
        if nan_count == len(security_data['volume']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            hsl_hsl[coin] = np.nan
            hsl_mahsl[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            # 等价于计算IF((SETCODE==0||SETCODE==1),100*VOL,VOL)，因为系统中返回的成交量就是股，而且该函数只用于A股标的
            volume_HSL = security_data['volume']
            volume_HSL = np.array(volume_HSL)
            # 查询code的所有市值数据, 时间是day
            q = query(
                valuation.circulating_cap
            ).filter(
                valuation.code == coin
            )
            # 获取最近specificCount个交易日
            dates = get_trade_days(end_date=check_date, count=specificCount)
            # 计算最近specificCount个交易日的流通股本
            circulating_cap = np.array(
                [get_fundamentals(q, day)['circulating_cap'][0] for day in dates])
            # 计算HSL，通达信获取的流通股本是的1/10000，而计算公式中是volume_HSL / (circulating_cap
            # / 100)，所以此处化简为下面的式子
            hsl = volume_HSL / circulating_cap / 100
            # 计算MAHSL
            mahsl = np.mean(hsl[-N:])

            hsl_hsl[coin] = hsl[-1]
            hsl_mahsl[coin] = mahsl
    return hsl_hsl, hsl_mahsl

# VOL-成交量


def VOL(security_list, check_date, M1=5, M2=10):
    '''
    计算公式：
        VOLUME:VOL,VOLSTICK;
        MAVOL1:MA(VOLUME,M1);
        MAVOL2:MA(VOLUME,M2);
        输出VOLUME:成交量(手),VOLSTICK
        输出MAVOL1:VOLUME的M1日简单移动平均
        输出MAVOL2:VOLUME的M2日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M：统计的天数 M
    输出：
        VOL和MAVOL 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 VOL
    vol_vol = {}
    vol_mavol1 = {}
    vol_mavol2 = {}
    maxN = max(M1, M2)
    specificCount = maxN * 4
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'volume'],  count=specificCount)
        nan_count = list(np.isnan(security_data['volume'])).count(True)
        if nan_count == len(security_data['volume']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            vol_vol[coin] = np.nan
            vol_mavol1[coin] = np.nan
            vol_mavol2[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            volume_VOL = security_data['volume']
            # 计算VOLUME
            volume_VOL = np.array([vol / 100 for vol in volume_VOL])
            # 计算MAVOL1
            MAVOL1 = np.mean(volume_VOL[-M1:])
            # 计算MAVOL2
            MAVOL2 = np.mean(volume_VOL[-M2:])

            vol_vol[coin] = volume_VOL[-1]
            vol_mavol1[coin] = MAVOL1
            vol_mavol2[coin] = MAVOL2
    return vol_vol, vol_mavol1, vol_mavol2

# VRSI-相对强弱量


def VRSI(security_list, check_date, N1=6, N2=12, N3=24):
    '''
    计算公式：
        LC:=REF(VOL,1);
        RSI1:SMA(MAX(VOL-LC,0),N1,1)/SMA(ABS(VOL-LC),N1,1)*100;
        RSI2:SMA(MAX(VOL-LC,0),N2,1)/SMA(ABS(VOL-LC),N2,1)*100;
        RSI3:SMA(MAX(VOL-LC,0),N3,1)/SMA(ABS(VOL-LC),N3,1)*100;
        LC赋值:1日前的成交量(手)
        输出RSI1:成交量(手)-LC和0的较大值的N1日[1日权重]移动平均/成交量(手)-LC的绝对值的N1日[1日权重]移动平均*100
        输出RSI2:成交量(手)-LC和0的较大值的N2日[1日权重]移动平均/成交量(手)-LC的绝对值的N2日[1日权重]移动平均*100
        输出RSI3:成交量(手)-LC和0的较大值的N3日[1日权重]移动平均/成交量(手)-LC的绝对值的N3日[1日权重]移动平均*100
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N1：统计的天数 N1
        N2：统计的天数 N2
        N3：统计的天数 N3
    输出：
        RSI1，VRSI2和VRSI3 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 计算SMA(X, N, M)， 即X的N日移动平均，M为权重, 若Y=SMA(X,N,M) 则 Y = (M*X+(N-M)*Y')/N,
    # 其中Y'表示上一周期Y值,N必须大于M。返回一个值

    def SMA(X, N, M=1):
        ret = reduce(lambda y, x: (M * x + (N - M) * y) / float(N), X)
        return ret
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 VRSI
    vrsi_rsi1 = {}
    vrsi_rsi2 = {}
    vrsi_rsi3 = {}
    maxN = max(N1, N2, N3)
    specificCount = maxN * 10
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'volume'],  count=specificCount)
        nan_count = list(np.isnan(security_data['volume'])).count(True)
        if nan_count == len(security_data['volume']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            vrsi_rsi1[coin] = np.nan
            vrsi_rsi2[coin] = np.nan
            vrsi_rsi3[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            volume_VRSI = security_data['volume']
            # 使交易量以手为单位
            volume_VRSI = [vol / 100 for vol in volume_VRSI]
            # 计算LC
            ref_vol = np.array(volume_VRSI[:-1])
            volume_VRSI = np.array(volume_VRSI[1:])
            # 计算VOL-LC
            vol_minus_ref = volume_VRSI - ref_vol
            # 计算MAX(VOL-LC)
            max_vol_lc = [max(0.0, minus) for minus in vol_minus_ref]
            # 计算ABS(VOL-LC)
            abs_vol_lc = [abs(minus) for minus in vol_minus_ref]
            # 计算SMA(MAX(VOL-LC,0),N,1)
            sma_max_n1 = SMA(max_vol_lc, N1, 1)
            sma_max_n2 = SMA(max_vol_lc, N2, 1)
            sma_max_n3 = SMA(max_vol_lc, N3, 1)
            # 计算SMA(MAX(VOL-LC,0),N,1)
            sma_abs_n1 = SMA(abs_vol_lc, N1, 1)
            sma_abs_n2 = SMA(abs_vol_lc, N2, 1)
            sma_abs_n3 = SMA(abs_vol_lc, N3, 1)
            # 计算RSI
            rsi1 = sma_max_n1 / sma_abs_n1 * 100
            rsi2 = sma_max_n2 / sma_abs_n2 * 100
            rsi3 = sma_max_n3 / sma_abs_n3 * 100

            vrsi_rsi1[coin] = rsi1
            vrsi_rsi2[coin] = rsi2
            vrsi_rsi3[coin] = rsi3
    return vrsi_rsi1, vrsi_rsi2, vrsi_rsi3


####################################################### 均线型 ##############
# BBI-多空均线
def BBI(security_list, check_date, timeperiod1=3, timeperiod2=6, timeperiod3=12, timeperiod4=24):
    '''
    计算公式：
        BBI:(MA(CLOSE,M1)+MA(CLOSE,M2)+MA(CLOSE,M3)+MA(CLOSE,M4))/4;
        输出多空均线BBI:(收盘价的M1日简单移动平均+收盘价的M2日简单移动平均+收盘价的M3日简单移动平均+收盘价的M4日简单移动平均)/4
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod1：统计的天数 N1
        timeperiod2：统计的天数 N2
        timeperiod3：统计的天数 N3
        timeperiod4：统计的天数 N4
    输出：
        BBI 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 BBI
    bbi = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=timeperiod4 * 2)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            bbi[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            # 计算BBI
            x = security_data['close']
            d = (x[-timeperiod1:].mean() + x[-timeperiod2:].mean() +
                 x[-timeperiod3:].mean() + x[-timeperiod4:].mean()) / 4.0
            bbi[coin] = d
    return bbi

# MA-均线


def MA(security_list, check_date, timeperiod=5):
    '''
    计算公式：
        MA1:MA(CLOSE,M1);
        输出MA1:收盘价的M1日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数timeperiod
    输出：
        MA1 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 MA
    ma = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=timeperiod * 2)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            ma[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_MA = security_data['close']
            ma[coin] = talib.MA(np.array(close_MA), timeperiod)[-1]
    return ma

# EXPMA-指数平均线


def EXPMA(security_list, check_date, timeperiod=12):
    '''
    计算公式：
        EXPMA:EMA(CLOSE,timeperiod)
        输出EXP:收盘价的timeperiod日指数移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数
    输出：
        EXPMA 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import talib
    import numpy as np
    expma = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d',
                                   fields=['close'], count=timeperiod)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            expma[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close = np.array(security_data['close'])
            expma[coin] = talib.EMA(close, timeperiod)[-1]
    return expma

# HMA-高价平均线


def HMA(security_list, check_date, timeperiod=12):
    '''
    计算公式：
        HMA:MA(HIGH,timeperiod);
        输出HMA:最高价的timeperiod日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数
    输出：
        HMA 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import numpy as np
    hma = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d',
                                   fields=['high'], count=timeperiod)
        nan_count = list(np.isnan(security_data['high'])).count(True)
        if nan_count == len(security_data['high']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            hma[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            high = np.array(security_data['high'])
            hma[coin] = np.mean(high[-timeperiod:])
    return hma

# LMA-低价平均线


def LMA(security_list, check_date, timeperiod=12):
    '''
    计算公式：
        LMA:MA(LOW,timeperiod)
        LMA:最低价的timeperiod日的平均值
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数
    输出：
        LMA 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import numpy as np
    lma = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d',
                                   fields=['low'], count=timeperiod)
        nan_count = list(np.isnan(security_data['low'])).count(True)
        if nan_count == len(security_data['low']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            lma[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            low = np.array(security_data['low'])
            lma[coin] = np.mean(low[-timeperiod:])
    return lma

# VMA-变异平均线


def VMA(security_list, check_date, timeperiod=12):
    '''
    计算公式：
        VV:=(HIGH+OPEN+LOW+CLOSE)/4
        VMA:MA(VV,timeperiod)
        VV赋值:(最高价+开盘价+最低价+收盘价)/4
        输出VMA:VV的timeperiod日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数
    输出：
        VMA 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import numpy as np
    vma = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d',  fields=[
                                  'low', 'high', 'open', 'close'], count=timeperiod)
        nan_count = list(np.isnan(security_data['low'])).count(True)
        if nan_count == len(security_data['low']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            vma[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            vv = np.array((security_data[
                          'low'] + security_data['close'] + security_data['high'] + security_data['open']) / 4)
            vma[coin] = np.mean(vv[-timeperiod:])
    return vma

# ALLIGAT-鳄鱼线


def ALLIGAT(security_list, check_date, timeperiod=21):
    '''
    计算公式：
        NN:=(H+L)/2;
        上唇:REF(MA(NN,5),3)
        牙齿:REF(MA(NN,8),5)
        下颚:REF(MA(NN,13),8)
        NN赋值:(最高价+最低价)/2
        输出上唇:3日前的NN的5日简单移动平均
        输出牙齿:5日前的NN的8日简单移动平均
        输出下颚:8日前的NN的13日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数
    输出：
        上唇 牙齿 下颚 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import talib
    import numpy as np
    up = {}
    teeth = {}
    down = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d',  fields=[
                                  'high', 'low'], count=timeperiod)
        nan_count = list(np.isnan(security_data['high'])).count(True)
        if nan_count == len(security_data['high']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            up[coin] = np.nan
            teeth[coin] = np.nan
            down[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            NN = np.array((security_data['high'] + security_data['low']) / 2)
            up[coin] = talib.MA(NN, 5)[-4]
            teeth[coin] = talib.MA(NN, 8)[-6]
            down[coin] = talib.MA(NN, 13)[-9]
    return up, teeth, down

# AMV-成本价均线


def AMV(security_list, check_date, timeperiod=13):
    '''
    计算公式：
        AMOV:=VOL*(OPEN+CLOSE)/2;
        AMV:SUM(AMOV,timeperiod)/SUM(VOL,timeperiod);
        AMOV赋值:成交量(手)*(开盘价+收盘价)/2
        输出AMV:AMOV的timeperiod日累和/成交量(手)的timeperiod日累和
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数
    输出：
        AMV 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import talib
    import numpy as np
    amv = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d',  fields=[
                                  'volume', 'open', 'close'], count=timeperiod)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            amv[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            amov = np.array(
                security_data['volume'] * (security_data['close'] + security_data['open']) / 2)
            amv[coin] = (talib.SUM(amov, timeperiod) /
                          talib.SUM(np.array(security_data['volume']), timeperiod))[-1]
    return amv

# BBIBOLL-多空布林线


def BBIBOLL(security_list, check_date, N=11, M=6):
    '''
    计算公式：
        CV:=CLOSE;
        BBIBOLL:(MA(CV,3)+MA(CV,6)+MA(CV,12)+MA(CV,24))/4;
        UPR:BBIBOLL+M*STD(BBIBOLL,N);
        DWN:BBIBOLL-M*STD(BBIBOLL,N);
        CV赋值:收盘价
        输出多空布林线:(CV的3日简单移动平均+CV的6日简单移动平均+CV的12日简单移动平均+CV的24日简单移动平均)/4
        输出UPR:BBIBOLL+M*BBIBOLL的N日估算标准差
        输出DWN:BBIBOLL-M*BBIBOLL的N日估算标准差
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数
        M：统计的天数
    输出：
        BBIBOLL UPR DWN 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import talib
    import numpy as np
    upr = {}
    dwn = {}
    bbi = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d',
                                   fields=['close'], count=23 + N)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            upr[coin] = np.nan
            dwn[coin] = np.nan
            bbi[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            CV = np.array(security_data['close'])
            one_bbi = (talib.MA(CV, 3) + talib.MA(CV, 6) +
                       talib.MA(CV, 12) + talib.MA(CV, 24)) / 4
            m_add_std = M * one_bbi[-N:].std()
            bbi[coin] = one_bbi[-1]
            upr[coin] = (one_bbi + m_add_std)[-1]
            dwn[coin] = (one_bbi - m_add_std)[-1]
    return bbi, upr, dwn

####################################################### 路径型 ##############

# BOLL-布林线


def Bollinger_Bands(security_list, check_date, timeperiod=20, nbdevup=2, nbdevdn=2):
    '''
    计算公式：
        LB:BOLL - nbdevup*STD(CLOSE,timeperiod);
        BOLL:MA(CLOSE,timeperiod);
        UB:BOLL + nbdevdn*STD(CLOSE,timeperiod);
        输出BOLL = 收盘价的M日简单移动平均
        输出LB = BOLL - nbdevup*收盘价的M日估算标准差
        输出UB = BOLL + nbdevdn*收盘价的M日估算标准差
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数 timeperiod
        nbdevup：统计的天数 nbdevup
        nbdevdn：统计的天数 nbdevdn
    输出：
        上轨线UB 、中轨线MB、下轨线LB 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    upperband = {}
    middleband = {}
    lowerband = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=timeperiod * 2)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            upperband[coin] = np.nan
            middleband[coin] = np.nan
            lowerband[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            closeBOLL = security_data['close']
            up, mid, low = talib.BBANDS(
                np.array(closeBOLL), timeperiod, nbdevup, nbdevdn)
            upperband[coin], middleband[coin], lowerband[
                coin] = up[-1], mid[-1], low[-1]
    return upperband, middleband, lowerband

# ENE-轨道线


def ENE(security_list, check_date, N=25, M1=6, M2=6):
    '''
    计算公式：
        UPPER:(1+M1/100)*MA(CLOSE,N);
        LOWER:(1-M2/100)*MA(CLOSE,N);
        ENE:(UPPER+LOWER)/2;
        输出UPPER:(1+M1/100)*收盘价的N日简单移动平均
        输出LOWER:(1-M2/100)*收盘价的N日简单移动平均
        输出轨道线:(UPPER+LOWER)/2
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数
        M1：统计的天数
        M2：统计的天数
    输出：
        UPPER LOWER ENE 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import talib
    import numpy as np
    ene = {}
    upper = {}
    lower = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(
            coin, end_date=check_date, frequency='1d',  fields=['close'], count=N)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            upper[coin] = np.nan
            lower[coin] = np.nan
            ene[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close = np.array(security_data['close'])
            ma_close_n = np.mean(close[-N:])
            a_upper = (1 + M1 / 100.0) * ma_close_n
            a_lower = (1 - M2 / 100.0) * ma_close_n
            ene[coin] = ((a_upper + a_lower) / 2.0)
            upper[coin] = a_upper
            lower[coin] = a_lower
    return upper, lower, ene

# MIKE-麦克支撑压力


def MIKE(security_list, check_date, timeperiod=10):
    '''
    计算公式：
        HLC:=REF(MA((HIGH+LOW+CLOSE)/3,timeperiod),1);
        HV:=EMA(HHV(HIGH,timeperiod),3);
        LV:=EMA(LLV(LOW,timeperiod),3);
        STOR:EMA(2*HV-LV,3);
        MIDR:EMA(HLC+HV-LV,3);
        WEKR:EMA(HLC*2-LV,3);
        WEKS:EMA(HLC*2-HV,3);
        MIDS:EMA(HLC-HV+LV,3);
        STOS:EMA(2*LV-HV,3);
        HLC赋值:1日前的(最高价+最低价+收盘价)/3的timeperiod日简单移动平均
        HV赋值:timeperiod日内最高价的最高值的3日指数移动平均
        LV赋值:timeperiod日内最低价的最低值的3日指数移动平均
        输出STOR:2*HV-LV的3日指数移动平均
        输出MIDR:HLC+HV-LV的3日指数移动平均
        输出WEKR:HLC*2-LV的3日指数移动平均
        输出WEKS:HLC*2-HV的3日指数移动平均
        输出MIDS:HLC-HV+LV的3日指数移动平均
        输出STOS:2*LV-HV的3日指数移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数
    输出：
        STOR, MIDR, WEKR, WEKS, MIDS, STOS 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import talib
    import numpy as np
    stor = {}
    midr = {}
    wekr = {}
    weks = {}
    mids = {}
    stos = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d',  fields=[
                                  'low', 'high', 'close'], count=timeperiod * 3)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            stor[coin] = np.nan
            stos[coin] = np.nan
            midr[coin] = np.nan
            mids[coin] = np.nan
            wekr[coin] = np.nan
            weks[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close = np.array(security_data['close'])
            high = np.array(security_data['high'])
            low = np.array(security_data['low'])
            # 计算HLC
            hlc = talib.MA((high[:-1] + close[:-1] + low[:-1]) / 3, timeperiod)
            # 计算HHV(HIGH,timeperiod) 和 LLV(LOW,timeperiod)
            hhv = []
            llv = []
            for x in range(timeperiod, len(high)):
                hhv.append(max(high[x - timeperiod + 1:x]))
                llv.append(min(low[x - timeperiod + 1:x]))
            # 计算HV 和 LV
            hv = talib.EMA(np.array(hhv), 3)
            lv = talib.EMA(np.array(llv), 3)
            # 取hlc中的最后五个数与hhv和llv的数据长度匹配
            stor[coin] = talib.EMA(2 * hv - lv, 3)[-1]
            # hv和lv当前的长度为20，所以hlc也只取后20个数据
            K = 20
            midr[coin] = talib.EMA(hlc[-K:] + hv - lv, 3)[-1]
            wekr[coin] = talib.EMA(hlc[-K:] * 2 - lv, 3)[-1]
            weks[coin] = talib.EMA(hlc[-K:] * 2 - hv, 3)[-1]
            mids[coin] = talib.EMA(hlc[-K:] + lv - hv, 3)[-1]
            stos[coin] = talib.EMA(lv * 2 - hv, 3)[-1]
    return stor, midr, wekr, weks, mids, stos

# PBX-瀑布线


def PBX(security_list, check_date, timeperiod=9):
    '''
    计算公式：
        PBX:(EMA(CLOSE,timeperiod)+MA(CLOSE,timeperiod*2)+MA(CLOSE,timeperiod*4))/3;
        输出PBX:(收盘价的timeperiod日指数移动平均+收盘价的timeperiod*2日简单移动平均+收盘价的timeperiod*4日简单移动平均)/3
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数
    输出：
        PBX 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import talib
    import numpy as np
    pbx = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d',  fields=[
                                  'close'], count=timeperiod * 4)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            pbx[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close = np.array(security_data['close'])
            tem_pbx = (talib.EMA(close, timeperiod)[-1] + np.mean(
                close[-timeperiod * 2:]) + np.mean(close[-timeperiod * 4:])) / 3.0
            pbx[coin] = tem_pbx
    return pbx

# XS-薛斯通道


def XS(security_list, check_date, timeperiod=13):
    '''
    计算公式：
        VAR2:=CLOSE*VOL;
        VAR3:=EMA((EMA(VAR2,3)/EMA(VOL,3)+EMA(VAR2,6)/EMA(VOL,6)+EMA(VAR2,12)/EMA(VOL,12)+EMA(VAR2,24)/EMA(VOL,24))/4,N);
        SUP:1.06*VAR3;
        SDN:VAR3*0.94;
        VAR4:=EMA(CLOSE,9);
        LUP:EMA(VAR4*1.14,5);
        LDN:EMA(VAR4*0.86,5);
        VAR2赋值:收盘价*成交量(手)
        VAR3赋值:(VAR2的3日指数移动平均/成交量(手)的3日指数移动平均+VAR2的6日指数移动平均/成交量(手)的6日指数移动平均+VAR2的12日指数移动平均/成交量(手)的12日指数移动平均+VAR2的24日指数移动平均/成交量(手)的24日指数移动平均)/4的N日指数移动平均
        输出SUP:1.06*VAR3
        输出SDN:VAR3*0.94
        VAR4赋值:收盘价的9日指数移动平均
        输出LUP:VAR4*1.14的5日指数移动平均
        输出LDN:VAR4*0.86的5日指数移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数
    输出：
        SUP SDN LUP LDN 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import talib
    import numpy as np
    sup = {}
    sdn = {}
    lup = {}
    ldn = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'volume', 'close'],  count=timeperiod * 4)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            sup[coin] = np.nan
            sdn[coin] = np.nan
            lup[coin] = np.nan
            ldn[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close = np.array(security_data['close'])
            volume = np.array(security_data['volume'] / 100.0)
            var2 = close * volume
            var3 = talib.EMA((talib.EMA(var2, 3) / talib.EMA(volume, 3) + talib.EMA(var2, 6) / talib.EMA(volume, 6) +
                              talib.EMA(var2, 12) / talib.EMA(volume, 12) + talib.EMA(var2, 24) / talib.EMA(volume, 24)) / 4, timeperiod)
            sup[coin] = (1.06 * var3)[-1]
            sdn[coin] = (0.94 * var3)[-1]
            var4 = talib.EMA(close, 9)
            lup[coin] = talib.EMA(var4 * 1.14, 5)[-1]
            ldn[coin] = talib.EMA(var4 * 0.86, 5)[-1]
    return sup, sdn, lup, ldn

# XS2-薛斯通道2


def XS2(security_list, check_date, N=102, M=7):
    '''
    计算公式：
        AA:=MA((2*CLOSE+HIGH+LOW)/4,5);
        通道1:AA*N/100;
        通道2:AA*(200-N)/100;
        CC:=ABS((2*CLOSE+HIGH+LOW)/4-MA(CLOSE,20))/MA(CLOSE,20);
        DD:=DMA(CLOSE,CC);
        通道3:(1+M/100)*DD;
        通道4:(1-M/100)*DD;
        AA赋值:(2*收盘价+最高价+最低价)/4的5日简单移动平均
        输出 通道1:AA*N/100
        输出 通道2:AA*(200-N)/100
        CC赋值:(2*收盘价+最高价+最低价)/4-收盘价的20日简单移动平均的绝对值/收盘价的20日简单移动平均
        DD赋值:以CC为权重收盘价的动态移动平均
        输出 通道3:(1+M/100)*DD
        输出 通道4:(1-M/100)*DD
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数
        M：统计的天数
    输出：
        PASS1, PASS2, PASS3, PASS4 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import talib
    import numpy as np
    # DMA为动态移动平均。其计算方式是Y:DMA(X,A);则Y=A*X+(1-A)*REF(Y,1);其中A必须小于1

    def DMA(X, A):
        # 从 A 的不为空值的数据开始计算
        len_A = len(A)
        point = 0  # 开始计算DMA的起始位置
        for i in range(point, len_A):
            if np.isnan(A[i]):
                point += 1
            else:
                break
        if point == len_A:
            log.info('Wrong! A is Empty!')
        preY = X[point]  # REF(Y, 1)的初始值是X[]中的第一个有效值
        for i in range(point, len_A):
            if A[i] >= 1:
                A[i] = 0.9999
            elif A[i] <= 0:
                A[i] = 0.0001
            Y = A[i] * X[i] + (1 - A[i]) * preY
            preY = Y
        return Y
    pass1 = {}
    pass2 = {}
    pass3 = {}
    pass4 = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d',  fields=[
                                  'low', 'high', 'close'], count=max(N, M))
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            pass1[coin] = np.nan
            pass2[coin] = np.nan
            pass3[coin] = np.nan
            pass4[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close = np.array(security_data['close'])
            high = np.array(security_data['high'])
            low = np.array(security_data['low'])
            va = 2 * close + high + low
            aa = talib.MA((va) / 4, 5)
            pass1[coin] = (aa * N / 100.0)[-1]
            pass2[coin] = (aa * (200 - N) / 100.0)[-1]
            cc = (abs((va) / 4 - talib.MA(close, 20)) / talib.MA(close, 20))
            dd = DMA(close, cc)
            pass3[coin] = (1 + M / 100.0) * dd
            pass4[coin] = (1 - M / 100.0) * dd
    return pass1, pass2, pass3, pass4

####################################################### 其他系 ##############

# EMA-指数移动平均


def EMA(security_list, check_date, timeperiod=30):
    '''
    计算公式：
        若Y=EMA(X,N)，则Y=[(2/N+1) * X+(N-1/N+1) * Y'],其中Y'表示上一周期Y值。
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数 timeperiod
    输出：
        EMA（指数移动平均）的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import talib
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 EMA
    ema = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=timeperiod * 2)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            ema[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_EMA = security_data['close']
            ema[coin] = talib.EMA(np.array(close_EMA), timeperiod)[-1]
    return ema

# SMA-移动平均


def SMA(security_list, check_date, N=7, M=1):
    '''
    计算公式：
        计算SMA(X, N, M)， 即X的N日移动平均，M为权重。
        若Y=SMA(X,N,M) 则 Y = (M*X+(N-M)*Y')/N, 其中Y'表示上一周期Y值,N必须大于M。
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
        M：权重 M
    输出：
        SMA(X的 N 日移动平均) 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import numpy as np
    import six
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 SMA
    sma = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=N * 2)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            sma[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_MA = security_data['close']
            close = np.array(close_MA)
            sma[coin] = reduce(lambda y, x: (M * x + (N - M) * y) / N, close)
    return sma

# BDZX-波段之星


def BDZX(security_list, check_date, timeperiod=40):
    '''
    计算公式：
        VAR1:=(HIGH+LOW+CLOSE*2)/4;
        VAR2:=EMA(VAR1,21);
        VAR3:=STD(VAR1,21);
        VAR4:=((VAR1-VAR2)/VAR3*100+200)/4;
        VAR5:(EMA(VAR4,5)-25)*1.56;
        AK: EMA(VAR5,2)*1.22;
        AD1: EMA(AK,2);
        AJ: 3*AK-2*AD1;
        AA:100;
        BB:0;
        CC:80;
        买进: IF(CROSS(AK,AD1),58,20);
        卖出: IF(CROSS(AD1,AK),58,20);
        VAR1赋值:(最高价+最低价+收盘价*2)/4
        VAR2赋值:VAR1的21日指数移动平均
        VAR3赋值:VAR1的21日估算标准差
        VAR4赋值:((VAR1-VAR2)/VAR3*100+200)/4
        输出VAR5:(VAR4的5日指数移动平均-25)*1.56
        输出AK: VAR5的2日指数移动平均*1.22
        输出AD1: AK的2日指数移动平均
        输出AJ: 3*AK-2*AD1
        输出AA:100
        输出布林极限:0
        输出CC:80
        输出买进: 如果AK上穿AD1,返回58,否则返回20
        输出卖出: 如果AD1上穿AK,返回58,否则返回20
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数
    输出：
        AK AD1 AJ AA BB CC BUY SELL的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import talib
    import numpy as np
    ak = {}
    ad1 = {}
    aj = {}
    aa = {}
    bb = {}
    cc = {}
    buy = {}
    sell = {}

    def a_cross(a, b):
        return True if a[-1] > b[-1] and a[-2] < b[-2] else False

    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'low', 'high'],  count=timeperiod)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            aa[coin] = np.nan
            bb[coin] = np.nan
            cc[coin] = np.nan
            buy[coin] = np.nan
            sell[coin] = np.nan
            ak[coin] = np.nan
            ad1[coin] = np.nan
            aj[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close = np.array(security_data['close'])
            high = np.array(security_data['high'])
            low = np.array(security_data['low'])
            # 计算VAR1
            var1 = (2 * close + high + low) / 4
            # 计算VAR2
            var2 = talib.EMA(var1, 21)
            # 计算VAR3
            var3 = var1[-21:].std()
            # 计算VAR4
            var4 = ((var1 - var2) / var3 * 100 + 200) / 4.0
            # 计算VAR5
            var5 = (talib.EMA(var4, 5) - 25) * 1.56
            # 计算AK
            t_ak = talib.EMA(var5, 2) * 1.22
            # 计算AD1
            t_ad1 = talib.EMA(t_ak, 2)

            ak[coin] = t_ak[-1]
            ad1[coin] = t_ad1[-1]
            aj[coin] = 3 * t_ak[-1] - 2 * t_ad1[-1]
            aa[coin] = 100
            bb[coin] = 0
            cc[coin] = 80
            buy[coin] = 58 if(a_cross(t_ak, t_ad1)) else 20
            sell[coin] = 58 if(a_cross(t_ad1, t_ak)) else 20
    return ak, ad1, aj, aa, bb, cc, buy, sell

# CDP-STD-逆势操作


def CDP_STD(security_list, check_date, timeperiod=2):
    '''
    计算公式：
        CH:=REF(H,1);
        CL:=REF(L,1);
        CC:=REF(C,1);
        CDP:(CH+CL+CC)/3;
        AH:2*CDP+CH-2*CL;
        NH:CDP+CDP-CL;
        NL:CDP+CDP-CH;
        AL:2*CDP-2*CH+CL;
        CH赋值:1日前的最高价
        CL赋值:1日前的最低价
        CC赋值:1日前的收盘价
        输出CDP:(CH+CL+CC)/3
        输出AH:2*CDP+CH-2*CL
        输出NH:CDP+CDP-CL
        输出NL:CDP+CDP-CH
        输出AL:2*CDP-2*CH+CL
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数
    输出：
        CDP AH NH NL AL的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import talib
    import numpy as np
    cdp = {}
    ah = {}
    nh = {}
    nl = {}
    al = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'low', 'high'],  count=timeperiod + 1)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            cdp[coin] = np.nan
            ah[coin] = np.nan
            nh[coin] = np.nan
            nl[coin] = np.nan
            al[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            low = security_data['low']
            close = security_data['close']
            high = security_data['high']
            cl = low[-2]
            ch = high[-2]
            cc = close[-2]
            arr = (cl + cc + ch) / 3
            cdp[coin] = arr
            ah[coin] = 2 * arr + ch - 2 * cl
            nh[coin] = 2 * arr - cl
            nl[coin] = 2 * arr - ch
            al[coin] = 2 * arr - 2 * ch + cl
    return cdp, ah, nh, nl, al

# CJDX-超级短线


def CJDX(security_list, check_date, timeperiod=16):
    '''
    计算公式：
        VAR1:=(2*CLOSE+HIGH+LOW)/4;
        VAR2:=EMA(EMA(EMA(VAR1,4),4),4);
        J: (VAR2-REF(VAR2,1))/REF(VAR2,1)*100, COLORSTICK;
        D: MA(J,3);
        K: MA(J,1);
        VAR1赋值:(2*收盘价+最高价+最低价)/4
        VAR2赋值:VAR1的4日指数移动平均的4日指数移动平均的4日指数移动平均
        输出J: (VAR2-1日前的VAR2)/1日前的VAR2*100, COLORSTICK
        输出D: J的3日简单移动平均
        输出K: J的1日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数
    输出：
        J D X 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import talib
    import numpy as np
    j = {}
    d = {}
    k = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'high', 'low'],  count=timeperiod * 2)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            d[coin] = np.nan
            j[coin] = np.nan
            k[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close = np.array(security_data['close'])
            high = np.array(security_data['high'])
            low = np.array(security_data['low'])
            # 计算VAR1
            var1 = (2 * close + high + low) / 4
            # 计算VAR2
            var2 = talib.EMA(talib.EMA(talib.EMA(var1, 4), 4), 4)
            # 计算J
            J = (var2[1:] - var2[:-1]) / var2[:-1] * 100
            j[coin] = J[-1]
            d[coin] = np.mean(J[-3:])
            k[coin] = J[-1]
    return j, d, k

# CYHT-财运亨通


def CYHT(security_list, check_date, timeperiod=60):
    '''
    计算公式：
        VAR1:=(2*CLOSE+HIGH+LOW+OPEN)/5;
        高抛: 80;
        VAR2:=LLV(LOW,34);
        VAR3:=HHV(HIGH,34);
        SK: EMA((VAR1-VAR2)/(VAR3-VAR2)*100,13);
        SD: EMA(SK,3);
        低吸: 20;
        强弱分界: 50;
        VAR4:=IF(CROSS(SK,SD),40,22);
        VAR5:=IF(CROSS(SD,SK),60,78);
        卖出: VAR5;
        买进: VAR4;
        VAR1赋值:(2*收盘价+最高价+最低价+开盘价)/5
        输出高抛: 80
        VAR2赋值:34日内最低价的最低值
        VAR3赋值:34日内最高价的最高值
        输出SK: (VAR1-VAR2)/(VAR3-VAR2)*100的13日指数移动平均
        输出SD: SK的3日指数移动平均
        输出低吸: 20
        输出强弱分界: 50
        VAR4赋值:如果SK上穿SD,返回40,否则返回22
        VAR5赋值:如果SD上穿SK,返回60,否则返回78
        输出卖出: VAR5
        输出买进: VAR4
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数
    输出：
        高抛 SK SD 低吸 强弱分界 卖出 买进的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import talib
    import numpy as np

    def hhv(arr, n):
        a = [max(arr[x: x + n]) for x in range(len(arr) - n + 1)]
        return np.array(a)

    def llv(arr, n):
        a = [min(arr[x: x + n]) for x in range(len(arr) - n + 1)]
        return np.array(a)

    def a_cross(a, b):
        return 1 if a[-1] > b[-1] and a[-2] < b[-2] else 0

    sk = {}
    sd = {}
    h_throw = {}
    weak = {}
    bound = {}
    sell = {}
    buy = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'open', 'close', 'low', 'high'],  count=timeperiod)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            sk[coin] = np.nan
            sd[coin] = np.nan
            sell[coin] = np.nan
            buy[coin] = np.nan
            weak[coin] = np.nan
            bound[coin] = np.nan
            h_throw[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close = np.array(security_data['close'])
            high = np.array(security_data['high'])
            low = np.array(security_data['low'])
            op = np.array(security_data['open'])
            var1 = (2 * close + high + low + op) / 5
            var2 = llv(low, 34)
            var3 = hhv(high, 34)
            t_sk = talib.EMA(
                (var1[33 - timeperiod:] - var2) / (var3 - var2) * 100, 13)
            t_sd = talib.EMA(t_sk, 3)
            var4 = 40 if a_cross(t_sk, t_sd) else 22
            var5 = 60 if a_cross(t_sd, t_sk) else 78
            h_throw[coin] = 80
            sk[coin] = t_sk[-1]
            sd[coin] = t_sd[-1]
            weak[coin] = 20
            bound[coin] = 50
            sell[coin] = var5
            buy[coin] = var4
    return h_throw, sk, sd, weak, bound, sell, buy

# JAX-济安线


def JAX(security_list, check_date, timeperiod=30):
    '''
    计算公式：
        AA:=ABS((2*CLOSE+HIGH+LOW)/4-MA(CLOSE,N))/MA(CLOSE,N);
        济安线:DMA((2*CLOSE+LOW+HIGH)/4,AA)
        CC:=(CLOSE/济安线);
        MA1:=MA(CC*(2*CLOSE+HIGH+LOW)/4,3);
        MAAA:=((MA1-济安线)/济安线)/3;
        TMP:=MA1-MAAA*MA1;
        J:IF(TMP<=济安线,济安线,DRAWNULL)
        A:TMP
        X:IF(TMP<=济安线,TMP,DRAWNULL)
        AA赋值:(2*收盘价+最高价+最低价)/4-收盘价的timeperiod日简单移动平均的绝对值/收盘价的timeperiod日简单移动平均
        输出济安线:以AA为权重(2*收盘价+最低价+最高价)/4的动态移动平均
        CC赋值:(收盘价/济安线)
        MA1赋值:CC*(2*收盘价+最高价+最低价)/4的3日简单移动平均
        MAAA赋值:((MA1-济安线)/济安线)/3
        TMP赋值:MA1-MAAA*MA1
        输出J:如果TMP<=济安线,返回济安线,否则返回无效数
        输出A:TMP
        输出X:如果TMP<=济安线,返回TMP,否则返回无效数
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数
    输出：
        JAX J A X 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import talib
    import numpy as np
    jax = {}
    a = {}
    j = {}
    x = {}
    # DMA为动态移动平均。其计算方式是Y:DMA(X,A);则Y=A*X+(1-A)*REF(Y,1);其中A必须小于1

    def DMA(X, A):
        # 从 A 的不为空值的数据开始计算
        len_A = len(A)
        point = 0  # 开始计算DMA的起始位置
        for i in range(point, len_A):
            if np.isnan(A[i]):
                point += 1
            else:
                break
        if point == len_A:
            log.info('Wrong! A is Empty!')
        preY = X[point]  # REF(Y, 1)的初始值是X[]中的第一个有效值
        for i in range(point, len_A):
            if A[i] >= 1:
                A[i] = 0.9999
            elif A[i] <= 0:
                A[i] = 0.0001
            Y = A[i] * X[i] + (1 - A[i]) * preY
            preY = Y
        return preY
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'high', 'low'],  count=timeperiod * 2)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            jax[coin] = np.nan
            a[coin] = np.nan
            j[coin] = np.nan
            x[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close = np.array(security_data['close'])
            high = np.array(security_data['high'])
            low = np.array(security_data['low'])
            var1 = (2 * close + high + low) / 4
            ma_close_timeperiod = talib.MA(close, timeperiod)
            aa = abs(var1 - ma_close_timeperiod) / ma_close_timeperiod
            tem_jax = DMA(var1, aa)
            cc = close / tem_jax
            pre_ma1 = cc * var1
            ma1 = np.mean(pre_ma1[-3:])
            maaa = ((ma1 - tem_jax) / tem_jax) / 3
            tmp = ma1 - maaa * ma1
            jax[coin] = tem_jax
            j[coin] = tem_jax if tmp <= tem_jax else np.nan
            a[coin] = tmp
            x[coin] = tmp if tmp <= tem_jax else np.nan
    return jax, j, a, x

# JFZX-飓风智能中线


def JFZX(security_list, check_date, timeperiod=30):
    '''
    计算公式：
        VAR2:=SUM(IF(CLOSE>OPEN,VOL,0),timeperiod)/SUM(VOL,timeperiod)*100;
        VAR3:=100-SUM(IF(CLOSE>OPEN,VOL,0),timeperiod)/SUM(VOL,timeperiod)*100;
        多头力量: VAR2;
        空头力量: VAR3;
        多空平衡: 50;
        VAR2赋值:如果收阳线,返回成交量(手),否则返回0的timeperiod日累和/成交量(手)的timeperiod日累和*100
        VAR3赋值:100-如果收阳线,返回成交量(手),否则返回0的timeperiod日累和/成交量(手)的timeperiod日累和*100
        输出多头力量: VAR2
        输出空头力量: VAR3
        输出多空平衡: 50
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数
    输出：
        多头力量 空头力量 多空平衡的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import talib
    import numpy as np
    most = {}
    empty = {}
    balance = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'open', 'volume'],  count=timeperiod)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            most[coin] = np.nan
            empty[coin] = np.nan
            balance[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            volume = np.array(security_data['volume'] / 100)
            close = np.array(security_data['close'])
            op = np.array(security_data['open'])
            tem1 = [volume[x] for x in range(len(close)) if close[x] > op[x]]
            var2 = sum(tem1) / sum(volume) * 100
            most[coin] = var2
            empty[coin] = 100 - var2
            balance[coin] = 50
    return most, empty, balance

# JYJL-交易参考均量


def JYJL(security_list, check_date, N=120, M=5):
    '''
    计算公式：
        单位时间总量: SUM(VOL,N)*100
        单位时间内均量: 单位时间总量/(N/M);
        输出单位时间总量: 成交量(手)的N日累和*100
        输出单位时间内均量: 单位时间总量/(N/M)
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数
        M：统计的天数
    输出：
        单位时间总量 单位时间内均量的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import talib
    import numpy as np
    com = {}
    per = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'volume'],  count=N)
        nan_count = list(np.isnan(security_data['volume'])).count(True)
        if nan_count == len(security_data['volume']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            com[coin] = np.nan
            per[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            volume = np.array(security_data['volume'])
            tem = sum(volume)
            com[coin] = tem
            per[coin] = tem / N * M
    return com, per

# LHXJ-猎狐先觉


def LHXJ(security_list, check_date, timeperiod=100):
    '''
    计算公式：
        VAR1:=(CLOSE*2+HIGH+LOW)/4;
        VAR2:=EMA(VAR1,13)-EMA(VAR1,34);
        VAR3:=EMA(VAR2,5);
        主力弃盘: (-2)*(VAR2-VAR3)*3.8;
        主力控盘: 2*(VAR2-VAR3)*3.8;
        VAR1赋值:(收盘价*2+最高价+最低价)/4
        VAR2赋值:VAR1的13日指数移动平均-VAR1的34日指数移动平均
        VAR3赋值:VAR2的5日指数移动平均
        输出主力弃盘: (-2)*(VAR2-VAR3)*3.8
        输出主力控盘: 2*(VAR2-VAR3)*3.8
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数
    输出：
        弃盘 控盘 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import talib
    import numpy as np
    control = {}
    give_up = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'low', 'high'],  count=timeperiod)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            control[coin] = np.nan
            give_up[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            high = np.array(security_data['high'])
            low = np.array(security_data['low'])
            close = np.array(security_data['close'])
            var1 = (high + low + close * 2) / 4
            var2 = talib.EMA(var1, 13) - talib.EMA(var1, 34)
            var3 = talib.EMA(var2, 5)
            temp = (2 * (var2 - var3) * 3.8)[-1]
            control[coin] = temp
            give_up[coin] = -temp
    return give_up, control

# LYJH-猎鹰歼狐


def LYJH(security_list, check_date, M=80, M1=50):
    '''
    计算公式：
        VAR1:=(HHV(HIGH,36)-CLOSE)/(HHV(HIGH,36)-LLV(LOW,36))*100;
        机构做空能量线: SMA(VAR1,2,1);
        VAR2:=(CLOSE-LLV(LOW,9))/(HHV(HIGH,9)-LLV(LOW,9))*100;
        机构做多能量线: SMA(VAR2,5,1)-8;
        LH: M;
        LH1: M1;
        VAR1赋值:(36日内最高价的最高值-收盘价)/(36日内最高价的最高值-36日内最低价的最低值)*100
        输出机构做空能量线: VAR1的2日[1日权重]移动平均
        VAR2赋值:(收盘价-9日内最低价的最低值)/(9日内最高价的最高值-9日内最低价的最低值)*100
        输出机构做多能量线: VAR2的5日[1日权重]移动平均-8
        输出LH: M
        输出LH1: M1
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        M：统计的天数
        M1：统计的天数
    输出：
        EMPTY MOST LH LH1的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import talib
    import numpy as np

    def hhv(arr, n):
        a = [max(arr[x: x + n]) for x in range(len(arr) - n + 1)]
        return np.array(a)

    def llv(arr, n):
        a = [min(arr[x: x + n]) for x in range(len(arr) - n + 1)]
        return np.array(a)

    def SMA(arr, n, m):
        y = []
        for x in range(len(arr)):
            if x == 0:
                y.append(arr[x])
            else:
                y.append((arr[x] * m + y[x - 1] * (n - m)) / n)
        return np.array(y)

    empty = {}
    most = {}
    lh = {}
    lh1 = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'low', 'high'],  count=M)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            empty[coin] = np.nan
            most[coin] = np.nan
            lh[coin] = np.nan
            lh1[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close = np.array(security_data['close'])
            high = np.array(security_data['high'])
            low = np.array(security_data['low'])
            var1 = (hhv(high, 36) - close[35 - M:]) / \
                (hhv(high, 36) - llv(low, 36)) * 100
            empty[coin] = SMA(var1, 2, 1)[-1]
            var2 = (close[8 - M:] - llv(low, 9)) / \
                (hhv(high, 9) - llv(low, 9)) * 100
            most[coin] = (SMA(var2, 5, 1) - 8)[-1]
            lh[coin] = M
            lh1[coin] = M1
    return empty, most, lh, lh1

# TBP-STD-趋势平衡点


def TBP_STD(security_list, check_date, timeperiod=30):
    '''
    计算公式：
        APX:=(H+L+C)/3;
        TR0:=MAX(H-L,MAX(ABS(H-REF(C,1)),ABS(L-REF(C,1))));
        MF0:=C-REF(C,2);
        MF1:=REF(MF0,1);
        MF2:=REF(MF0,2);
        DIRECT1:=BARSLAST(MF0>MF1 AND MF0>MF2);
        DIRECT2:=BARSLAST(MF0<MF1 AND MF0<MF2);
        DIRECT0:=IF(DIRECT1<DIRECT2,100,-100);
        TBP:REF(REF(C,1)+IF(DIRECT0>50,MIN(MF0,MF1),MAX(MF0,MF1)),1);
        多头获利:REF(IF(DIRECT0>50,APX*2-L,DRAWNULL),1),NODRAW;
        多头停损:REF(IF(DIRECT0>50,APX-TR0,DRAWNULL),1),NODRAW;
        空头回补:REF(IF(DIRECT0<-50,APX*2-H,DRAWNULL),1),NODRAW;
        空头停损:REF(IF(DIRECT0<-50,APX+TR0,DRAWNULL),1),NODRAW;
        APX赋值:(最高价+最低价+收盘价)/3
        TR0赋值:最高价-最低价和最高价-1日前的收盘价的绝对值和最低价-1日前的收盘价的绝对值的较大值的较大值
        MF0赋值:收盘价-2日前的收盘价
        MF1赋值:1日前的MF0
        MF2赋值:2日前的MF0
        DIRECT1赋值:上次MF0>MF1ANDMF0>MF2距今天数
        DIRECT2赋值:上次MF0<MF1ANDMF0<MF2距今天数
        DIRECT0赋值:如果DIRECT1<DIRECT2,返回100,否则返回-100
        输出TBP:1日前的1日前的收盘价+如果DIRECT0>50,返回MF0和MF1的较小值,否则返回MF0和MF1的较大值
        输出多头获利:1日前的如果DIRECT0>50,返回APX*2-最低价,否则返回无效数,NODRAW
        输出多头停损:1日前的如果DIRECT0>50,返回APX-TR0,否则返回无效数,NODRAW
        输出空头回补:1日前的如果DIRECT0<-50,返回APX*2-最高价,否则返回无效数,NODRAW
        输出空头停损:1日前的如果DIRECT0<-50,返回APX+TR0,否则返回无效数,NODRAW
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数
    输出：
        tbp，多头获利，多头停损，空头回补和空头停损 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 STD
    std_tbp = {}
    std_dthl = {}
    std_dtts = {}
    std_kthb = {}
    std_ktts = {}
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'high', 'low'],  count=timeperiod)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            std_tbp[coin] = np.nan
            std_dthl[coin] = np.nan
            std_dtts[coin] = np.nan
            std_kthb[coin] = np.nan
            std_ktts[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_STD = security_data['close']
            high_STD = security_data['high']
            low_STD = security_data['low']
            close_STD = np.array(close_STD)
            high_STD = np.array(high_STD)
            low_STD = np.array(low_STD)

            # 计算APX
            apx = (high_STD + low_STD + close_STD) / 3.0
            # 计算H-L
            high_minus_low = high_STD - low_STD
            # 计算H-REF(C,1))
            high_minus_refclose = high_STD[1:] - close_STD[:-1]
            # 计算L-REF(C,1)
            low_minus_refclose = low_STD[1:] - close_STD[:-1]
            # 计算TR0
            tr0 = [max(h_m_l, abs(h_m_r), abs(l_m_r)) for (h_m_l, h_m_r, l_m_r) in zip(
                high_minus_low[1:], high_minus_refclose, low_minus_refclose)]
            # 计算MF0:=C-REF(C,2);
            mf0 = close_STD[2:] - close_STD[:-2]
            # 计算MF1:=REF(MF0,1);
            mf1 = mf0[:-1]
            # 计算MF2:=REF(MF0,2);
            mf2 = mf0[:-2]

            # 计算DIRECT1
            pre_direct1 = [True if f0 > f1 and f0 > f2 else False for (
                f0, f1, f2) in zip(mf0[2:], mf1[1:], mf2)]
            last_direct1 = pre_direct1.count(False)
            # last_direct1 = max(np.nonzero(np.array(pre_direct1) == True)[0])
            direct1 = len(pre_direct1) - last_direct1 - 1
            # 计算DIRECT2
            pre_direct2 = [True if f0 < f1 and f0 < f2 else False for (
                f0, f1, f2) in zip(mf0[2:], mf1[1:], mf2)]
            last_direct2 = pre_direct2.count(False)
            # last_direct2 = max(np.nonzero(np.array(pre_direct2) == True)[0])
            direct2 = len(pre_direct1) - last_direct2 - 1
            # 计算DIRECT0
            direct0 = 100 if direct1 < direct2 else -100

            # 计算TBP，简化了计算
            min_mf0_mf1 = min(mf0[-2], mf1[-2])
            max_mf0_mf1 = max(mf0[-2], mf1[-2])
            tbp = close_STD[-3] + \
                (min_mf0_mf1 if direct0 > 50 else max_mf0_mf1)

            # 计算多头获利，多头停损，空头回补和空头停损
            ref = 2
            dthl = (apx * 2 - low_STD)[-ref] if direct0 > 50 else np.nan
            dtts = (apx[1:] - tr0)[-ref] if direct0 > 50 else np.nan
            kthb = (apx * 2 - high_STD)[-ref] if direct0 < -50 else np.nan
            ktts = (apx[1:] + tr0)[-ref] if direct0 < -50 else np.nan

            std_tbp[coin] = tbp
            std_dthl[coin] = dthl
            std_dtts[coin] = dtts
            std_kthb[coin] = kthb
            std_ktts[coin] = ktts
    return std_tbp, std_dthl, std_dtts, std_kthb, std_ktts

# ZBCD-准备抄底


def ZBCD(security_list, check_date, timeperiod=10):
    '''
    计算公式：
        VAR1:=money/VOL/7;
        VAR2:=(3*HIGH+LOW+OPEN+2*CLOSE)/7;
        VAR3:=SUM(money,timeperiod)/VAR1/7;
        VAR4:=DMA(VAR2,VOL/VAR3);
        抄底:(CLOSE-VAR4)/VAR4*100
        VAR1赋值:成交额(元)/成交量(手)/7
        VAR2赋值:(3*最高价+最低价+开盘价+2*收盘价)/7
        VAR3赋值:成交额(元)的timeperiod日累和/VAR1/7
        VAR4赋值:以成交量(手)/VAR3为权重VAR2的动态移动平均
        输出抄底:(收盘价-VAR4)/VAR4*100
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        timeperiod：统计的天数
    输出：
        抄底 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据
    '''
    import six
    import talib
    import numpy as np
    # DMA为动态移动平均。其计算方式是Y:DMA(X,A);则Y=A*X+(1-A)*REF(Y,1);其中A必须小于1

    def DMA(X, A):
        # 从 A 的不为空值的数据开始计算
        len_A = len(A)
        point = 0  # 开始计算DMA的起始位置
        for i in range(point, len_A):
            if np.isnan(A[i]):
                point += 1
            else:
                break
        if point == len_A:
            log.info('Wrong! A is Empty!')
        preY = X[point]  # REF(Y, 1)的初始值是X[]中的第一个有效值
        for i in range(point, len_A):
            if A[i] >= 1:
                A[i] = 0.9999
            elif A[i] <= 0:
                A[i] = 0.0001
            Y = A[i] * X[i] + (1 - A[i]) * preY
            preY = Y
        return Y
    cd = {}
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'open', 'low', 'high', 'volume', 'money'],  count=timeperiod * 5)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            cd[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            volume = security_data['volume'] / 100
            money = security_data['money']
            low = security_data['low']
            close = security_data['close']
            high = security_data['high']
            open_ = security_data['open']
            var1 = money / volume / 7
            var2 = (3 * high + 2 * open_ + close + low) / 7
            var3 = talib.SUM(np.array(money), timeperiod) / var1 / 7
            var4 = DMA(var2, volume / var3)
            cd[coin] = (close[-1] - var4) / var4 * 100
    return cd


####################################################### 神系 ###############
# SG-SMX-生命线
def SG_SMX(index_coin, security_list, check_date, N=50):
    '''
    计算公式：
        H1:=HHV(HIGH,N);
        L1:=LLV(LOW,N);
        H2:=HHV(INDEXH,N);
        L2:=LLV(INDEXL,N);
        ZY:=CLOSE/INDEXC*2000;
        ZY1:EMA(ZY,3);
        ZY2:EMA(ZY,17);
        ZY3:EMA(ZY,34);
        H1赋值:N日内最高价的最高值
        L1赋值:N日内最低价的最低值
        H2赋值:N日内大盘的最高价的最高值
        L2赋值:N日内大盘的最低价的最低值
        ZY赋值:收盘价/大盘的收盘价*2000
        输出ZY1:ZY的3日指数移动平均
        输出ZY2:ZY的17日指数移动平均
        输出ZY3:ZY的34日指数移动平均
    输入：
        index_coin: 大盘标的代码
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
    输出：
        ZY1,ZY2和ZY3 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    new_security_list = security_list[:]
    new_security_list.insert(0, index_coin)
    # 计算 SG_smx
    smx_zy1 = {}
    smx_zy2 = {}
    smx_zy3 = {}
    specificCount = N + 1
    close_index = 0.0
    i = 0
    for coin in new_security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=specificCount)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            if i == 0:
                log.info("大盘标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
                close_index = 1.0
            else:
                log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
                smx_zy1[coin] = np.nan
                smx_zy2[coin] = np.nan
                smx_zy3[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_SMX = security_data['close']
            close_SMX = np.array(close_SMX)

            if i == 0:
                # 计算INDEXC
                close_index = close_SMX
            else:
                # 计算ZY
                zy = close_SMX * 2000 / close_index
                # 计算ZY1，ZY2，ZY3
                zy1 = talib.EMA(zy, 3)[-1]
                zy2 = talib.EMA(zy, 17)[-1]
                zy3 = talib.EMA(zy, 34)[-1]
                smx_zy1[coin] = zy1
                smx_zy2[coin] = zy2
                smx_zy3[coin] = zy3
        i += 1
    return smx_zy1, smx_zy2, smx_zy3

# XDT-心电图


def XDT(index_coin, security_list, check_date, P1=5, P2=10):
    '''
    计算公式：
        QR:CLOSE/INDEXC*1000;
        MQR1:MA(QR,P1);
        MQR2:MA(QR,P2);
        输出强弱指标(需下载日线):收盘价/大盘的收盘价*1000
        输出MQR1:QR的P1日简单移动平均
        输出MQR2:QR的P2日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        P1：统计的天数 P1
        P2：统计的天数 P2
    输出：
        QR，MQR1和MAQR2 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    new_security_list = security_list[:]
    new_security_list.insert(0, index_coin)

    # 计算 XDT
    XDT_qr = {}
    XDT_maqr1 = {}
    XDT_maqr2 = {}
    maxN = max(P1, P2)
    specificCount = maxN + 1
    i = 0
    close_index = 0.0
    for coin in new_security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=specificCount)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            # 这种情况几乎不会发生
            if i == 0:
                log.info("大盘标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
                close_index = 1.0
            else:
                log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
                XDT_qr[coin] = np.nan
                XDT_maqr1[coin] = np.nan
                XDT_maqr2[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_XDT = security_data['close']
            close_XDT = np.array(close_XDT)
            if i == 0:
                close_index = close_XDT
            else:
                qr = close_XDT * 1000 / close_index
                maqr1 = np.mean(qr[-P1:])
                maqr2 = np.mean(qr[-P2:])

                XDT_qr[coin] = qr[-1]
                XDT_maqr1[coin] = maqr1
                XDT_maqr2[coin] = maqr2
        i += 1
    return XDT_qr, XDT_maqr1, XDT_maqr2

# SG_LB-量比


def SG_LB(index_coin, security_list, check_date):
    '''
    计算公式：
        ZY2:=VOL/INDEXV*1000;
        量比:ZY2;
        MA5:MA(ZY2,5);
        MA10:MA(ZY2,10);
        ZY2赋值:成交量(手)/大盘的成交量*1000
        输出量比:ZY2
        输出MA5:ZY2的5日简单移动平均
        输出MA10:ZY2的10日简单移动平均
    输入：
        index_coin: 大盘标的代码
        security_list:标的列表
        check_date：要查询数据的日期
    输出：
        SG_LB,MA5和MA10的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    new_security_list = security_list[:]
    new_security_list.insert(0, index_coin)
    # 计算 SG_LB
    lb_lb = {}
    lb_ma5 = {}
    lb_ma10 = {}
    N1 = 5
    N2 = 10
    specificCount = N2 + 1
    volume_index = 1.0
    i = 0
    for coin in new_security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'volume'],  count=specificCount)
        nan_count = list(np.isnan(security_data['volume'])).count(True)
        if nan_count == len(security_data['volume']):
            if i == 0:
                log.info("大盘标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
                volume_index = 1.0
            else:
                log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
                lb_lb[coin] = np.nan
                lb_ma5[coin] = np.nan
                lb_ma10[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            volume_LB = security_data['volume']
            volume_LB = np.array(volume_LB)

            if i == 0:
                # 计算INDEXV
                volume_index = volume_LB
            else:
                # 计算ZY2，因为
                zy2 = volume_LB * 1000 / volume_index
                # 计算MA5
                ma5 = np.mean(zy2[-N1:])
                # 计算MA10
                ma10 = np.mean(zy2[-N2:])
                lb_lb[coin] = zy2[-1]
                lb_ma5[coin] = ma5
                lb_ma10[coin] = ma10
        i += 1
    return lb_lb, lb_ma5, lb_ma10

# SG-PF-强势股评分


def SG_PF(index_coin, security_list, check_date):
    '''
    计算公式：
        ZY1:=CLOSE/INDEXC*1000;
        A1:=IF(ZY1>=HHV(ZY1,3),10,0);
        A2:=IF(ZY1>=HHV(ZY1,5),15,0);
        A3:=IF(ZY1>=HHV(ZY1,10),20,0);
        A4:=IF(ZY1>=HHV(ZY1,2),10,0);
        A5:=COUNT(ZY1>REF(ZY1,1) ,9)*5;
        强势股评分:A1+A2+A3+A4+A5;
        ZY1赋值:收盘价/大盘的收盘价*1000
        A1赋值:如果ZY1>3日内ZY1的最高值,返回10,否则返回0
        A2赋值:如果ZY1>5日内ZY1的最高值,返回15,否则返回0
        A3赋值:如果ZY1>10日内ZY1的最高值,返回20,否则返回0
        A4赋值:如果ZY1>2日内ZY1的最高值,返回10,否则返回0
        A5赋值:统计9日中满足ZY1>1日前的ZY1的天数*5
        输出强势股评分:A1+A2+A3+A4+A5
    输入：
        index_coin：大盘标的代码
        security_list:标的列表
        check_date：要查询数据的日期
    输出：
        强势股评分 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    new_security_list = security_list[:]
    new_security_list.insert(0, index_coin)
    # 计算 PF
    pf_pf = {}
    N1 = 2
    N2 = 3
    N3 = 5
    N4 = 10
    N5 = 9
    specificCount = N4 + 1
    close_index = 1.0
    i = 0
    for coin in new_security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=specificCount)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            if i == 0:
                log.info("大盘标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
                close_index = 1.0
            else:
                log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
                pf_pf[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_PF = security_data['close']
            close_PF = np.array(close_PF)
            if i == 0:
                # 获取大盘的收盘价
                close_index = close_PF
            else:
                zy1 = close_PF * 1000 / close_index
                # 计算A1,A2,A3,A4
                a1 = 10 if zy1[-1] >= max(zy1[-N2:]) else 0
                a2 = 15 if zy1[-1] >= max(zy1[-N3:]) else 0
                a3 = 20 if zy1[-1] >= max(zy1[-N4:]) else 0
                a4 = 10 if zy1[-1] >= max(zy1[-N1:]) else 0
                # 计算ZY1-REF(ZY1, 1)，并获取后N5个值
                pf_dif = np.diff(zy1)[-N5:]
                # 统计COUNT(ZY1>REF(ZY1,1) ,9)
                pf_count = np.sum(np.where(pf_dif > 0, 1, 0))
                a5 = pf_count * 5
                # 计算强势股评分
                pf = a1 + a2 + a3 + a4 + a5
                pf_pf[coin] = pf
        i += 1
    return pf_pf

####################################################### 龙系 ###############
# ZLMM-主力买卖


def ZLMM(security_list, check_date):
    '''
    计算公式：
        LC :=REF(CLOSE,1);
        RSI2:=SMA(MAX(CLOSE-LC,0),12,1)/SMA(ABS(CLOSE-LC),12,1)*100;
        RSI3:=SMA(MAX(CLOSE-LC,0),18,1)/SMA(ABS(CLOSE-LC),18,1)*100;
        MMS:MA(3*RSI2-2*SMA(MAX(CLOSE-LC,0),16,1)/SMA(ABS(CLOSE-LC),16,1)*100,3);
        MMM:EMA(MMS,8);
        MML:MA(3*RSI3-2*SMA(MAX(CLOSE-LC,0),12,1)/SMA(ABS(CLOSE-LC),12,1)*100,5);
        赋值:1日前的收盘价
        RSI2赋值:收盘价-LC和0的较大值的12日[1日权重]移动平均/收盘价-LC的绝对值的12日[1日权重]移动平均*100
        RSI3赋值:收盘价-LC和0的较大值的18日[1日权重]移动平均/收盘价-LC的绝对值的18日[1日权重]移动平均*100
        输出MMS:3*RSI2-2*收盘价-LC和0的较大值的16日[1日权重]移动平均/收盘价-LC的绝对值的16日[1日权重]移动平均*100的3日简单移动平均
        输出MMM:MMS的8日指数移动平均
        输出MML:3*RSI3-2*收盘价-LC和0的较大值的12日[1日权重]移动平均/收盘价-LC的绝对值的12日[1日权重]移动平均*100的5日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
    输出：
        MMS, MMM和MML 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 计算SMA(X, N, M)， 即X的N日移动平均，M为权重, 若Y=SMA(X,N,M) 则 Y = (M*X+(N-M)*Y')/N,
    # 其中Y'表示上一周期Y值,N必须大于M。返回一个列表

    def SMA(X, N, M=1):
        ret = []
        point = 0
        length = len(X)
        # 跳过X中前面几个 nan 值
        for i in range(0, length):
            if np.isnan(X[i]):
                point += 1
            else:
                break
        preY = X[i]  # Y'
        ret.append(preY)
        for i in range(point, length):
            Y = (M * X[i] + (N - M) * preY) / float(N)
            ret.append(Y)
            preY = Y
        return ret
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 ZLMM
    zlmm_mms = {}
    zlmm_mmm = {}
    zlmm_mml = {}
    N1 = 12
    N2 = 16
    N3 = 18
    specificCount = N3 * 6
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=specificCount)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            zlmm_mms[coin] = np.nan
            zlmm_mmm[coin] = np.nan
            zlmm_mml[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_ZLMM = security_data['close']
            close_ZLMM = np.array(close_ZLMM)
            # 计算LC
            lc = close_ZLMM[:-1]
            close_ZLMM = close_ZLMM[1:]
            # 计算MAX(CLOSE-LC,0)
            max_close_lc = [max(close - l, 0.0)
                            for close, l in zip(close_ZLMM, lc)]
            # 计算ABS(CLOSE-LC)
            abs_close_lc = [abs(close - l) for close, l in zip(close_ZLMM, lc)]
            # 计算各种SMA
            sma_max_N1 = SMA(max_close_lc, N1)
            sma_max_N2 = SMA(max_close_lc, N2)
            sma_max_N3 = SMA(max_close_lc, N3)
            sma_abs_N1 = SMA(abs_close_lc, N1)
            sma_abs_N2 = SMA(abs_close_lc, N2)
            sma_abs_N3 = SMA(abs_close_lc, N3)
            # 计算RSI2
            rsi2 = np.array(sma_max_N1) * 100.0 / np.array(sma_abs_N1)
            # 计算RSI3
            rsi3 = np.array(sma_max_N3) * 100.0 / np.array(sma_abs_N3)
            # 计算2*SMA(MAX(CLOSE-LC,0),16,1)/SMA(ABS(CLOSE-LC),16,1)*100
            rsi4 = np.array(sma_max_N2) * 100.0 / np.array(sma_abs_N2)
            # 计算MMS
            mms = talib.MA(3 * rsi2 - 2 * rsi4, 3)
            # 计算MMM
            # EMA(X,N)相当于SMA(X,N+1,2)
            mmm = SMA(mms, 8 + 1, 2)
            # 计算MML
            mml = talib.MA(3 * rsi3 - 2 * rsi2, 5)

            zlmm_mms[coin] = mms[-1]
            zlmm_mmm[coin] = mmm[-1]
            zlmm_mml[coin] = mml[-1]
    return zlmm_mms, zlmm_mmm, zlmm_mml

# RAD-威力雷达


def RAD(index_coin, security_list, check_date, D=3, S=30, M=30):
    '''
    计算公式：
        SM:=(OPEN+HIGH+CLOSE+LOW)/4;
        SMID:=MA(SM,D);
        IM:=(INDEXO+INDEXH+INDEXL+INDEXC)/4;
        IMID:=MA(IM,D);
        SI1:=(SMID-REF(SMID,1))/SMID;
        II:=(IMID-REF(IMID,1))/IMID;
        RADER1:SUM((SI1-II)*2,S)*1000;
        RADERMA:SMA(RADER1,M,1);
        SM赋值:(开盘价+最高价+收盘价+最低价)/4
        SMID赋值:SM的D日简单移动平均
        IM赋值:(大盘的开盘价+大盘的最高价+大盘的最低价+大盘的收盘价)/4
        IMID赋值:IM的D日简单移动平均
        SI1赋值:(SMID-1日前的SMID)/SMID
        II赋值:(IMID-1日前的IMID)/IMID
        输出RADER1:(SI1-II)*2的S日累和*1000
        输出RADERMA:RADER1的M日[1日权重]移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        D：统计的天数 D
        S：统计的天数 S
        M：统计的天数 M
    输出：
        RADER1和RADERMA 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 计算SMA(X, N, M)， 即X的N日移动平均，M为权重, 若Y=SMA(X,N,M) 则 Y = (M*X+(N-M)*Y')/N,
    # 其中Y'表示上一周期Y值,N必须大于M。返回一个值

    def SMA(X, N, M=1):
        ret = []
        point = 0
        length = len(X)
        # 跳过X中前面几个 nan 值
        for i in range(0, length):
            if np.isnan(X[i]):
                point += 1
            else:
                break
        preY = X[i]  # Y'
        for i in range(point, length):
            Y = (M * X[i] + (N - M) * preY) / float(N)
            preY = Y
        return preY
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    new_security_list = security_list[:]
    new_security_list.insert(0, index_coin)
    # 计算 RAD
    rad_rad = {}
    rad_marad = {}
    maxN = max(D, S, M)
    specificCount = maxN * 6
    i = 0
    ii = []
    for coin in new_security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'open', 'close', 'high', 'low'],  count=specificCount)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            if i == 0:
                log.info("大盘标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            else:
                log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            rad_rad[coin] = np.nan
            rad_marad[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            open_RAD = security_data['open']
            close_RAD = security_data['close']
            high_RAD = security_data['high']
            low_RAD = security_data['low']
            open_RAD = np.array(open_RAD)
            close_RAD = np.array(close_RAD)
            high_RAD = np.array(high_RAD)
            low_RAD = np.array(low_RAD)
            # 计算SM
            sm = (open_RAD + high_RAD + close_RAD + low_RAD) / 4.0
            # 计算SMID
            smid = talib.MA(sm, D)
            pre_smid = smid[:-1]
            smid = smid[1:]
            # 计算SI1
            si1 = [(s - pre_s) / s for s, pre_s in zip(smid, pre_smid)]
            if i == 0:
                # 给II赋值
                ii = si1
            else:
                # 计算RADER1
                pre_rader = (np.array(si1) - np.array(ii)) * 2
                rader1 = talib.SUM(pre_rader, S) * 1000.0
                # 计算RADERMA
                raderma = SMA(rader1, M)

                rad_rad[coin] = rader1[-1]
                rad_marad[coin] = raderma
        i += 1
    return rad_rad, rad_marad

# SHT-龙系短线


def SHT(security_list, check_date, N=5):
    '''
    计算公式：
        VAR1:=MA((VOL-REF(VOL,1))/REF(VOL,1),5);
        VAR2:=(CLOSE-MA(CLOSE,24))/MA(CLOSE,24)*100;
        MY: VAR2*(1+VAR1);
        SHT: MY, COLORSTICK;
        SHTMA: MA(SHT,N);
        VAR1赋值:(成交量(手)-1日前的成交量(手))/1日前的成交量(手)的5日简单移动平均
        VAR2赋值:(收盘价-收盘价的24日简单移动平均)/收盘价的24日简单移动平均*100
        输出MY: VAR2*(1+VAR1)
        输出龙系短线: MY, COLORSTICK
        输出SHTMA: SHT的N日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
    输出：
        SHT和SHTMA 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 SHT
    sht_sht = {}
    sht_masht = {}
    specificCount = N * 10
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'volume'],  count=specificCount)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            sht_sht[coin] = np.nan
            sht_masht[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_SHT = security_data['close']
            volume_SHT = security_data['volume']
            # 计算REF(VOL,1)
            pre_volume = volume_SHT[:-1]
            close_SHT = np.array(close_SHT[1:])
            volume_SHT = np.array(volume_SHT[1:])
            # var1中的交易量原本应以手为单位，但因为涉及到交易量相除，就没必要使交易量除以100了
            vol_minus_pre = [(vol - pre_vol) / pre_vol for vol,
                             pre_vol in zip(volume_SHT, pre_volume)]
            # 计算VAR1
            var1 = talib.MA(np.array(vol_minus_pre), 5)
            # 计算MA(CLOSE,24)
            ma_close = talib.MA(close_SHT, 24)
            # 计算VAR1
            var2 = (close_SHT - ma_close) / ma_close * 100
            sht = var2 * (1.0 + var1)
            masht = np.mean(sht[-N:])

            sht_sht[coin] = sht[-1]
            sht_masht[coin] = masht
    return sht_sht, sht_masht

####################################################### 鬼系 ###############
# CYW-主力控盘


def CYW(security_list, check_date):
    '''
    计算公式：
        VAR1:=CLOSE-LOW;
        VAR2:=HIGH-LOW;
        VAR3:=CLOSE-HIGH;
        VAR4:=IF(HIGH>LOW,(VAR1/VAR2+VAR3/VAR2)*VOL,0);
        CYW: SUM(VAR4,10)/10000, COLORSTICK;
        VAR1赋值:收盘价-最低价
        VAR2赋值:最高价-最低价
        VAR3赋值:收盘价-最高价
        VAR4赋值:如果最高价>最低价,返回(VAR1/VAR2+VAR3/VAR2)*成交量(手),否则返回0
        输出主力控盘: VAR4的10日累和/10000, COLORSTICK
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
    输出：
        主力控盘 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 CYW
    cyw_cyw = {}
    N = 10
    specificCount = N * 4
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'high', 'low', 'volume'],  count=specificCount)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            cyw_cyw[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_CYW = security_data['close']
            high_CYW = security_data['high']
            low_CYW = security_data['low']
            volume_CYW = security_data['volume']
            # 交易量以手为单位
            volume_CYW = [vol / 100 for vol in volume_CYW]
            # 变为np.ndarray类型，以方便计算
            close_CYW = np.array(close_CYW)
            high_CYW = np.array(high_CYW)
            low_CYW = np.array(low_CYW)
            volume_CYW = np.array(volume_CYW)

            # 计算VAR1，VAR2和VAR3
            var1 = close_CYW - low_CYW
            var2 = high_CYW - low_CYW
            var3 = close_CYW - high_CYW
            # 计算VAR4
            pre_var4 = (var1 / var2 + var3 / var2) * volume_CYW
            var4 = [pre_v if high > low else 0.0 for pre_v,
                    high, low in zip(pre_var4, high_CYW, low_CYW)]
            # 计算CYW
            cyw = talib.SUM(np.array(var4), N)[-1] / 10000

            cyw_cyw[coin] = cyw
    return cyw_cyw

# CYS-市场盈亏


def CYS(security_list, check_date):
    '''
    计算公式：
        CYC13:=0.01*EMA(AMOUNT,13)/EMA(VOL,13);
        CYS:(CLOSE-CYC13)/CYC13*100;
        CYC13赋值:0.01*成交额(元)的13日指数移动平均/成交量(手)的13日指数移动平均
        输出市场盈亏:(收盘价-CYC13)/CYC13*100
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
    输出：
        市场盈亏 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 计算EMA(X, N, M)， 即X的N日指数移动平均，M为权重, 算法Y=(X*2 + Y'*(N - 1)) / (N + 1)

    def EMA(X, N):
        ret = reduce(lambda y, x: (2 * x + (N - 1) * y) / (N + 1), X)
        return ret
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 CYS
    cys_cys = {}
    N = 13
    specificCount = N * 2
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'money', 'volume', 'close'],  count=specificCount)
        nan_count = list(np.isnan(security_data['money'])).count(True)
        if nan_count == len(security_data['money']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            cys_cys[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            money_CYS = security_data['money']
            volume_CYS = security_data['volume']
            close_CYS = security_data['close']
            # 交易量以手为单位
            volume_CYS = [vol / 100 for vol in volume_CYS]
            # 计算EMA(AMOUNT,13)
            ema_amount = EMA(money_CYS, N)
            # 计算EMA(VOL,13)
            ema_volume = EMA(volume_CYS, N)
            # 计算CYC13
            cyc13 = 0.01 * ema_amount / ema_volume
            # 计算CYS
            cys = (close_CYS[-1] - cyc13) * 100.0 / cyc13

            cys_cys[coin] = cys
    return cys_cys

####################################################### 特色型 ##############
# ZSDB-指数对比


def ZSDB(index_coin, check_date):
    '''
    计算公式：
        A:=REF(INDEXC,1);
        指数涨幅:IF(A>0,(INDEXC-A)*100/A,0),NODRAW;
        输出A:1日前的大盘的收盘价
        输出指数涨幅:如果A>0,返回(大盘的收盘价-A)*100/A,否则返回0,NODRAW
    输入：
        index_coin：大盘标的代码
        check_date：要查询数据的日期
    输出：
        A和指数涨幅 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 计算 ZSDB
    zsdb_a = {}
    zsdb_zszf = {}
    specificCount = 2
    security_data = get_price(index_coin, end_date=check_date, frequency='1d', fields=[
                              'close'],  count=specificCount)
    nan_count = list(np.isnan(security_data['close'])).count(True)
    if nan_count == len(security_data['close']):
        log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
        zsdb_a[coin] = np.nan
        zsdb_zszf[coin] = np.nan
    else:
        if nan_count > 0:
            security_data.fillna(method="bfill", inplace=True)
        close_ZSDB = security_data['close']
        close_ZSDB = np.array(close_ZSDB)
        # 计算A
        a = close_ZSDB[-2]
        # 计算指数涨幅
        zszf = (close_ZSDB[-1] - a) * 100 / a if a > 0 else 0.0

        zsdb_a[index_coin] = a
        zsdb_zszf[index_coin] = zszf
    return zsdb_a, zsdb_zszf

# AROON-阿隆指标


def AROON(security_list, check_date, N=25):
    '''
    计算公式：
        上轨:(N-HHVBARS(H,N))/N*100,COLORRED;
        下轨:(N-LLVBARS(H,N))/N*100,COLORGREEN;
        输出上轨:(N-N日内最高价的最大值距今天数)/N*100,画红色
        输出下轨:(N-N日内最高价的最小值距今天数)/N*100,画绿色
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
    输出：
        上轨和下轨 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 AROON
    aroon_sg = {}
    aroon_xg = {}
    specificCount = N
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'high'],  count=specificCount)
        nan_count = list(np.isnan(security_data['high'])).count(True)
        if nan_count == len(security_data['high']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            aroon_sg[coin] = np.nan
            aroon_xg[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            high_AROON = security_data['high']
            high_AROON = np.array(high_AROON)

            # 获取N天内的最高价的最大值
            hhv = np.nanmax(high_AROON[-N:])
            # 获取到距离今天最近的最高价最大值的下标
            inx_hhv = np.nanmax(np.nonzero(high_AROON == hhv)[0])
            # 获取HHVBARS(H, N)，即hhv距离今天的天数
            day_hhv = N - (inx_hhv + 1)
            # 计算上轨
            sg = (N - day_hhv) * 100 / N

            # 获取N天内的最高价的最小值
            llv = np.nanmin(high_AROON[-N:])
            # 获取到距离今天最近的最高价最小值的下标
            inx_llv = np.nanmax(np.nonzero(high_AROON == llv)[0])
            # 获取HHVBARS(H, N)，即llv距离今天的天数
            day_llv = N - (inx_llv + 1)
            # 计算下轨
            xg = (N - day_llv) * 100 / N

            aroon_sg[coin] = sg
            aroon_xg[coin] = xg
    return aroon_sg, aroon_xg

# CFJT-财富阶梯


def CFJT(security_list, check_date, MM=200):
    '''
    计算公式：
        突破:=REF(EMA(C,14),1);
        A1X:=(EMA(C,10)-突破)/突破*100;
        多方:=IF(A1X>=0,REF(EMA(C,10),BARSLAST(CROSS(A1X,0))+1),DRAWNULL);
        空方:=IF(A1X<0,REF(EMA(C,10),BARSLAST(CROSS(0,A1X))+1),DRAWNULL);
        突破赋值:1日前的收盘价的14日指数移动平均
        A1X赋值:(收盘价的10日指数移动平均-突破)/突破*100
        多方赋值:如果A1X>=0,返回上次A1X上穿0距今天数+1日前的收盘价的10日指数移动平均,否则返回无效数
        空方赋值:如果A1X<0,返回上次0上穿A1X距今天数+1日前的收盘价的10日指数移动平均,否则返回无效数
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        MM：统计的天数 MM
    输出：
        突破，A1X，多方和空方 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 计算SMA(X, N, M)， 即X的N日移动平均，M为权重, 若Y=SMA(X,N,M) 则 Y = (M*X+(N-M)*Y')/N,
    # 其中Y'表示上一周期Y值,N必须大于M。返回一个列表

    def SMA(X, N, M=1):
        ret = []
        point = 0
        length = len(X)
        # 跳过X中前面几个 nan 值
        for i in range(0, length):
            if np.isnan(X[i]):
                point += 1
            else:
                break
        preY = X[i]  # Y'
        ret.append(preY)
        for i in range(point, length):
            Y = (M * X[i] + (N - M) * preY) / float(N)
            ret.append(Y)
            preY = Y
        return ret
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 CFJT
    cfjt_tp = {}
    cfjt_a1x = {}
    cfjt_df = {}
    cfjt_kf = {}
    N = 14
    M = 10
    specificCount = MM
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close'],  count=specificCount)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            cfjt_tp[coin] = np.nan
            cfjt_a1x[coin] = np.nan
            cfjt_df[coin] = np.nan
            cfjt_kf[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_CFJT = security_data['close']
            close_CFJT = np.array(close_CFJT)
            # EMA(X,N)相当于SMA(X,N+1,2)
            # 计算EMA(C,14)和EMA(C,10)
            ema_N_close = SMA(close_CFJT, N + 1, 2)
            ema_M_close = SMA(close_CFJT, M + 1, 2)
            # 计算今天的突破
            tp = ema_N_close[-2]
            # 获取突破的值
            ema_N_close = ema_N_close[:-1]
            # 使得EMA(C, 10)的长度和突破的相同，以方便zip
            ema_M_close = ema_M_close[1:]
            # 计算A1X
            a1x = [(num_ema - num_tp) * 100 / num_tp for num_ema,
                   num_tp in zip(ema_M_close, ema_N_close)]

            # 计算CROSS(A1X,0)和CROSS(0,A1X)
            crs_df = 0
            crs_kf = 0
            try:
                # 从后往前判断，来减少比较次数
                # 舍去第一个数据
                for inc in range(1, MM - 1):
                    inc = -inc
                    now = a1x[inc]
                    pre = a1x[inc - 1]
                    if now > 0.0 and pre < 0.0 and crs_df == 0:
                        crs_df = inc
                    if now < 0.0 and pre > 0.0 and crs_kf == 0:
                        crs_kf = inc
                    # 多方和空方每次只可能出现一个
                    if crs_kf < 0 or crs_df < 0:
                        break
            except IndexError:
                log.info("标的 %s 输入数据中有效数据不足以计算出多方或空方，该标的可能刚上市，返回 NaN 值数据。" % coin)
                cfjt_tp[coin] = np.nan
                cfjt_a1x[coin] = np.nan
                cfjt_df[coin] = np.nan
                cfjt_kf[coin] = np.nan
                continue
            # 计算BARSLAST(CROSS(A1X,0)和BARSLAST(CROSS(0,A1X)
            bar_df = -crs_df - 1
            bar_kf = -crs_kf - 1
            # 容错处理，如果在(1,MM-2)天中都没有计算出crs_df或者crs_kf则使其等于最大值MM-2
            if crs_df == 0:
                bar_df = MM - 2
            if crs_kf == 0:
                bar_kf = MM - 2
            # 计算多方和空方
            df = ema_M_close[-1 - bar_df - 1] if a1x[-1] >= 0 else None
            kf = ema_M_close[-1 - bar_kf - 1] if a1x[-1] < 0 else None

            cfjt_tp[coin] = tp
            cfjt_a1x[coin] = a1x[-1]
            cfjt_df[coin] = df
            cfjt_kf[coin] = kf
    return cfjt_tp, cfjt_a1x, cfjt_df, cfjt_kf

####################################################### 图表型 ##############
# ZX-重心线


def ZX(security_list, check_date):
    '''
    计算公式：
        AV:0.01*AMOUNT/VOL;
        输出AV:0.01*成交额(元)/成交量(手)
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
    输出：
        AV 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 ZX
    zx_av = {}
    specificCount = 1
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'volume', 'money', 'close', 'high', 'low'],  count=specificCount)
        nan_count = list(np.isnan(security_data['volume'])).count(True)
        if nan_count == len(security_data['volume']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            zx_av[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            volume_ZX = security_data['volume']
            money_ZX = security_data['money']
            # 使交易量以手为单位
            volume_ZX = [vol / 100 for vol in volume_ZX]
            # 计算AV
            av = 0.01 * money_ZX[-1] / volume_ZX[-1]

            zx_av[coin] = av
    return zx_av

# PUCU-逆时钟曲线


def PUCU(security_list, check_date, N=24):
    '''
    计算公式：
        PU:MA(CLOSE,N);
        CU:MA(VOL,N);
        输出PU:收盘价的N日简单移动平均
        输出CU:成交量(手)的N日简单移动平均
    输入：
        security_list:标的列表
        check_date：要查询数据的日期
        N：统计的天数 N
    输出：
        PU和CU 的值。
    输出结果类型：
        字典(dict)：键(key)为标的代码，值(value)为数据。
    '''
    import six
    import talib
    import numpy as np
    # 修复传入为单只标的的情况
    if isinstance(security_list, six.string_types):
        security_list = [security_list]
    # 计算 PUCU
    pucu_pu = {}
    pucu_cu = {}
    specificCount = N + 1
    for coin in security_list:
        security_data = get_price(coin, end_date=check_date, frequency='1d', fields=[
                                  'close', 'volume'],  count=specificCount)
        nan_count = list(np.isnan(security_data['close'])).count(True)
        if nan_count == len(security_data['close']):
            log.info("标的 %s 输入数据全是 NaN，该标的可能已退市、未上市或刚上市，返回 NaN 值数据。" % coin)
            pucu_pu[coin] = np.nan
            pucu_cu[coin] = np.nan
        else:
            if nan_count > 0:
                security_data.fillna(method="bfill", inplace=True)
            close_PUCU = security_data['close']
            volume_PUCU = security_data['volume']

            # close_PUCU = np.array(close_PUCU)
            volume_PUCU = [vol / 100 for vol in volume_PUCU]
            # 计算PU
            pu = np.mean(close_PUCU[-N:])
            # 计算CU
            cu = np.mean(volume_PUCU[-N:])

            pucu_pu[coin] = pu
            pucu_cu[coin] = cu
    return pucu_pu, pucu_cu
