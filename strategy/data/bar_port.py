#!/usr/bin/env python
# coding: utf-8
from .bcolz_store import get_bcolz_day_store, get_bcolz_minute_store


def get_date_by_count(security, end_date, count):
    store = get_bcolz_day_store()
    return store.get_date_by_count(security, end_date, count)


def get_date_by_period(security, start_date, end_date):
    store = get_bcolz_day_store()
    return store.get_date_by_period(security, start_date, end_date)


def get_minute_bar_by_count(security, end_dt, count, fields, include_now=True):
    store = get_bcolz_minute_store()
    return store.get_bar_by_count(security, end_dt, count, fields, include_now=include_now)


def get_minute_bar_by_period(security, start_dt, end_dt, fields, include_now=True):
    store = get_bcolz_minute_store()
    return store.get_bar_by_period(security, start_dt, end_dt, fields, include_now=include_now)


def get_daily_bar_by_count(security, end_date, count, fields, include_now=True):
    store = get_bcolz_day_store()
    return store.get_bar_by_count(security, end_date, count, fields, include_now=include_now)


def get_daily_bar_by_period(security, start_date, end_date, fields, include_now=True):
    store = get_bcolz_day_store()
    return store.get_bar_by_period(security, start_date, end_date, fields, include_now=include_now)

def get_minute_by_count(security, end_dt, count, include_now=True):
    store = get_bcolz_minute_store()
    return store.get_minute_by_count(security, end_dt, count, include_now=include_now)

def get_minute_by_period(security, start_dt, end_dt, include_now=True):
    store = get_bcolz_minute_store()
    return store.get_minute_by_period(security, start_dt, end_dt, include_now=include_now)