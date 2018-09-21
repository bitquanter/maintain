# coding:utf-8
import json
bp_coin_pair = {}
# 火币币对
huobi_coin = {}
huobi_coin['ht'] = ['xrp', 'iost', 'dash', 'eos', 'bch', 'ltc', 'etc']
huobi_coin['btc'] = ['xmr', 'bch', 'eth', 'ltc', 'etc', 'eos', 'omg', 'xrp', 'dash', 'zec', 'ada', 'steem', 'iota', 'poly', 'kan', 'lba', 'wan', 'bft', 'btm', 'ont', 'iost', 'ht', 'trx', 'smt', 'ela', 'wicc', 'ocn', 'zla', 'abt', 'mtx', 'nas', 'ven', 'dta', 'neo', 'wax', 'bts', 'zil', 'theta', 'ctxc', 'srn', 'xem', 'icx', 'dgd', 'chat', 'wpr', 'lun', 'swftc', 'snt', 'meet', 'yee', 'elf', 'let', 'qtum', 'lsk', 'itc', 'soc', 'qash', 'mds', 'eko', 'topc', 'mtn', 'act', 'hsr', 'stk', 'storj', 'gnx', 'dbc', 'snc', 'cmt', 'tnb', 'ruff', 'qun', 'zrx', 'knc', 'blz', 'propy', 'rpx', 'appc', 'aidoc', 'powr', 'cvc', 'pay', 'qsp', 'dat', 'rdn', 'mco', 'rcn', 'mana', 'utk', 'tnt', 'gas', 'bat', 'ost', 'link', 'gnt', 'mtl', 'evx', 'req', 'adx', 'ast', 'eng', 'salt', 'edu', 'xvg', 'wtc', 'bifi', 'bcx', 'bcd', 'sbtc', 'btg', 'waves', 'dcr', 'pai', 'box', 'dgb', 'gxs', 'xlm', 'bix', 'hit', 'bt1', 'bt2', 'xzc', 'vet']
huobi_coin['usdt'] = ['btc', 'bch', 'eth', 'etc', 'ltc', 'eos', 'xrp', 'omg', 'dash', 'zec', 'ada', 'steem', 'iota', 'ocn', 'soc', 'ctxc', 'act', 'btm', 'bts', 'ont', 'iost', 'ht', 'trx', 'dta', 'neo', 'qtum', 'smt', 'ela', 'ven', 'theta', 'snt', 'zil', 'xem', 'nas', 'ruff', 'hsr', 'let', 'mds', 'storj', 'elf', 'itc', 'cvc', 'gnt', 'wicc', 'hb10', 'cmt', 'bix', 'pai', 'vet']
huobi_coin['eth'] = ['xmr', 'eos', 'omg', 'iota', 'ada', 'steem', 'poly', 'kan', 'lba', 'wan', 'bft', 'zrx', 'ast', 'knc', 'ont', 'ht', 'btm', 'iost', 'smt', 'ela', 'trx', 'abt', 'nas', 'ocn', 'wicc', 'zil', 'ctxc', 'zla', 'wpr', 'dta', 'mtx', 'theta', 'srn', 'ven', 'bts', 'wax', 'hsr', 'icx', 'mtn', 'act', 'blz', 'qash', 'ruff', 'cmt', 'elf', 'meet', 'soc', 'qtum', 'itc', 'swftc', 'yee', 'lsk', 'lun', 'let', 'gnx', 'chat', 'eko', 'topc', 'dgd', 'stk', 'mds', 'dbc', 'snc', 'pay', 'qun', 'aidoc', 'tnb', 'appc', 'rdn', 'utk', 'powr', 'bat', 'propy', 'mana', 'req', 'cvc', 'qsp', 'evx', 'dat', 'mco', 'gnt', 'gas', 'ost', 'link', 'rcn', 'tnt', 'eng', 'salt', 'adx', 'edu', 'xvg', 'wtc', 'waves', 'dcr', 'pai', 'box', 'dgb', 'gxs', 'xlm', 'bix', 'hit', 'xzc', 'vet']
bp_coin_pair['huobi'] = huobi_coin
# OK币对
ok_coin = {}
ok_coin['bch'] = ['ltc', 'etc', 'act', 'avt', 'bcd', 'bcx', 'btg', 'cmt', 'dash', 'dgd', 'edo', 'eos', 'sbtc']
ok_coin['btc'] = ['ltc', 'eth', 'etc', 'bch', 'xrp', 'xem', 'xlm', 'iota', '1st', 'aac', 'abt', 'ace', 'act', 'aidoc', 'amm', 'ark', 'ast', 'atl', 'auto', 'avt', 'bcd', 'bcs', 'bcx', 'bec', 'bkx', 'bnt', 'brd', 'bt1', 'bt2', 'btg', 'btm', 'cag', 'can', 'cbt', 'chat', 'cic', 'cmt', 'ctr', 'cvc', 'dadi', 'dash', 'dat', 'dent', 'dgb', 'dgd', 'dna', 'dnt', 'dpy', 'edo', 'elf', 'eng', 'enj', 'eos', 'evx', 'fair', 'fun', 'gas', 'gnt', 'gnx', 'gsc', 'gtc', 'gto', 'hmc', 'hot', 'hsr', 'icn', 'icx', 'ins', 'insur', 'int', 'iost', 'ipc', 'itc', 'kcash', 'key', 'knc', 'la', 'lend', 'lev', 'light', 'link', 'lrc', 'mag', 'mana', 'mco', 'mda', 'mdt', 'mith', 'mkr', 'mof', 'mot', 'mth', 'mtl', 'nano', 'nas', 'neo', 'ngc', 'nuls', 'oax', 'of', 'okb', 'omg', 'ont', 'ost', 'pay', 'poe', 'ppt', 'pra', 'pst', 'qtum', 'qun', 'qvt', 'r', 'rcn', 'rct', 'rdn', 'read', 'ref', 'ren', 'req', 'rfr', 'rnt', 'salt', 'san', 'sbtc', 'show', 'smt', 'snc', 'sngls', 'snm', 'snt', 'soc', 'spf', 'ssc', 'stc', 'storj', 'sub', 'swftc', 'tct', 'theta', 'tio', 'tnb', 'topc', 'tra', 'trio', 'true', 'trx', 'ubtc', 'uct', 'ugc', 'ukg', 'utk', 'vee', 'vib', 'viu', 'wbtc', 'wfee', 'wrc', 'wtc', 'xmr', 'xuc', 'yee', 'yoyo', 'zec', 'zen', 'zip', 'zrx']
ok_coin['usdt'] = ['btc', 'ltc', 'eth', 'etc', 'bch', 'xrp', 'xem', 'xlm', 'iota', '1st', 'aac', 'abt', 'ace', 'act', 'aidoc', 'amm', 'ark', 'ast', 'atl', 'auto', 'avt', 'bcd', 'bec', 'bkx', 'bnt', 'brd', 'btg', 'btm', 'cag', 'can', 'cbt', 'chat', 'cic', 'cmt', 'ctr', 'cvc', 'dadi', 'dash', 'dat', 'dent', 'dgb', 'dgd', 'dna', 'dnt', 'dpy', 'edo', 'elf', 'eng', 'enj', 'eos', 'evx', 'fair', 'fun', 'gas', 'gnt', 'gnx', 'gsc', 'gtc', 'gto', 'hmc', 'hot', 'hsr', 'icn', 'icx', 'ins', 'insur', 'int', 'iost', 'ipc', 'itc', 'kcash', 'key', 'knc', 'la', 'lend', 'lev', 'light', 'link', 'lrc', 'mag', 'mana', 'mco', 'mda', 'mdt', 'mith', 'mkr', 'mof', 'mot', 'mth', 'mtl', 'nano', 'nas', 'neo', 'ngc', 'nuls', 'oax', 'of', 'okb', 'omg', 'ont', 'ost', 'pay', 'poe', 'ppt', 'pra', 'pst', 'qtum', 'qun', 'qvt', 'r', 'rcn', 'rct', 'rdn', 'read', 'ref', 'ren', 'req', 'rfr', 'rnt', 'salt', 'san', 'show', 'smt', 'snc', 'sngls', 'snm', 'snt', 'soc', 'spf', 'ssc', 'stc', 'storj', 'sub', 'swftc', 'tct', 'theta', 'tio', 'tnb', 'topc', 'tra', 'trio', 'true', 'trx', 'ubtc', 'uct', 'ugc', 'ukg', 'utk', 'vee', 'vib', 'viu', 'wfee', 'wrc', 'wtc', 'xmr', 'xuc', 'yee', 'yoyo', 'zec', 'zen', 'zip', 'zrx']
ok_coin['eth'] = ['ltc', 'etc', 'bch', 'xrp', 'xem', 'xlm', 'iota', '1st', 'aac', 'abt', 'ace', 'act', 'aidoc', 'amm', 'ark', 'ast', 'atl', 'auto', 'avt', 'bec', 'bkx', 'bnt', 'brd', 'btm', 'cag', 'can', 'cbt', 'chat', 'cic', 'cmt', 'ctr', 'cvc', 'dadi', 'dash', 'dat', 'dent', 'dgb', 'dgd', 'dna', 'dnt', 'dpy', 'edo', 'elf', 'eng', 'enj', 'eos', 'evx', 'fair', 'fun', 'gas', 'gnt', 'gnx', 'gsc', 'gtc', 'gto', 'hmc', 'hot', 'hsr', 'icn', 'icx', 'ins', 'insur', 'int', 'iost', 'ipc', 'itc', 'kcash', 'key', 'knc', 'la', 'lend', 'lev', 'light', 'link', 'lrc', 'mag', 'mana', 'mco', 'mda', 'mdt', 'mith', 'mkr', 'mof', 'mot', 'mth', 'mtl', 'nano', 'nas', 'neo', 'ngc', 'nuls', 'oax', 'of', 'okb', 'omg', 'ont', 'ost', 'pay', 'poe', 'ppt', 'pra', 'pst', 'qtum', 'qun', 'qvt', 'r', 'rcn', 'rct', 'rdn', 'read', 'ref', 'ren', 'req', 'rfr', 'rnt', 'salt', 'san', 'show', 'smt', 'snc', 'sngls', 'snm', 'snt', 'soc', 'spf', 'ssc', 'stc', 'storj', 'sub', 'swftc', 'tct', 'theta', 'tio', 'tnb', 'topc', 'tra', 'trio', 'true', 'trx', 'ubtc', 'uct', 'ugc', 'ukg', 'utk', 'vee', 'vib', 'viu', 'wfee', 'wrc', 'wtc', 'xmr', 'xuc', 'yee', 'yoyo', 'zec', 'zen', 'zip', 'zrx']
bp_coin_pair['okex'] = ok_coin
# 币安币对
bib_coin = {}
#bib_coin['btc'] = ['wings', 'rep', 'btg', 'bcpt', 'brd', 'blz', 'lun', 'wabi', 'edo', 'appc', 'vibe', 'ost', 'ark', 'agi', 'lend', 'qtum', 'gnt', 'dash', 'zil', 'eos', 'neo', 'ins', 'sngls', 'link', 'cnd', 'gvt', 'vib', 'gto', 'aion', 'iotx', 'theta', 'storm', 'qlc', 'mana', 'xrp', 'req', 'dnt', 'powr', 'nxs', 'ont', 'tnb', 'storj', 'xmr', 'poly', 'key', 'nas', 'arn', 'hc', 'xem', 'tusd', 'trx', 'nano', 'rcn', 'bat', 'cloak', 'nuls', 'mth', 'wtc', 'steem', 'zrx', 'bcd', 'rlc', 'kmd', 'rdn', 'icn', 'ncash', 'ardr', 'grs', 'snt', 'qsp', 'oax', 'mco', 'xlm', 'ae', 'lsk', 'knc', 'hsr', 'bnt', 'wpr', 'bnb', 'poe', 'wan', 'iota', 'ppt', 'cmt', 'strat', 'phx', 'nav', 'chat', 'qkc', 'waves', 'dlt', 'vet', 'mda', 'bcn', 'enj', 'gas', 'dgd', 'sky', 'cdt', 'eth', 'eng', 'adx', 'tnt', 'data', 'bts', 'ast', 'elf', 'poa', 'zen', 'yoyo', 'mft', 'dent', 'icx', 'bcc', 'pivx', 'iost', 'nebl', 'sc', 'ven', 'npxs', 'zec', 'mtl', 'xzc', 'snm', 'evx', 'cvc', 'hot', 'salt', 'amb', 'fun', 'trig', 'xvg', 'ltc', 'via', 'dock', 'gxs', 'rpx', 'omg', 'loom', 'bqx', 'etc', 'fuel', 'sys', 'mod', 'ada', 'sub', 'lrc']
#bib_coin['eth'] = ['arn', 'cnd', 'enj', 'qsp', 'bcd', 'mtl', 'tnt', 'rpx', 'qtum', 'gto', 'wpr', 'ltc', 'omg', 'storm', 'fuel', 'vibe', 'snm', 'sc', 'rep', 'grs', 'ven', 'steem', 'adx', 'salt', 'gvt', 'wan', 'xlm', 'nuls', 'cdt', 'nxs', 'mda', 'bcn', 'mft', 'bat', 'xmr', 'tusd', 'cmt', 'vet', 'bnt', 'sky', 'trx', 'bts', 'wings', 'evx', 'iost', 'rdn', 'trig', 'nas', 'wabi', 'eng', 'ark', 'ardr', 'dlt', 'mana', 'waves', 'loom', 'mth', 'phx', 'fun', 'sys', 'poa', 'elf', 'link', 'storj', 'dock', 'xrp', 'ont', 'lun', 'ast', 'nebl', 'sngls', 'lsk', 'lrc', 'nav', 'zen', 'lend', 'theta', 'xzc', 'qkc', 'gnt', 'zrx', 'btg', 'zil', 'via', 'hc', 'ada', 'data', 'ins', 'sub', 'iotx', 'bnb', 'hsr', 'appc', 'bcpt', 'icn', 'amb', 'oax', 'icx', 'cvc', 'powr', 'pivx', 'brd', 'xvg', 'mod', 'rlc', 'ost', 'tnb', 'poe', 'bqx', 'cloak', 'kmd', 'qlc', 'snt', 'xem', 'dash', 'ppt', 'req', 'blz', 'zec', 'wtc', 'ae', 'vib', 'bcc', 'ncash', 'etc', 'rcn', 'knc', 'hot', 'edo', 'yoyo', 'strat', 'key', 'neo', 'chat', 'eos', 'mco', 'gxs', 'nano', 'dnt', 'aion', 'npxs', 'agi', 'iota', 'dgd', 'dent']
bib_coin['usdt'] = ['btc'] # ['xlm', 'eos', 'ven', 'ltc', 'vet', 'iota', 'ada', 'btc', 'etc', 'bnb', 'trx', 'tusd', 'nuls', 'xrp', 'bcc', 'ont', 'qtum', 'icx', 'eth', 'neo']
#bib_coin['bnb'] = ['etc', 'rlc', 'nano', 'qlc', 'enj', 'poa', 'wabi', 'blz', 'pivx', 'ardr', 'cnd', 'xzc', 'bcn', 'appc', 'ven', 'via', 'bcc', 'trig', 'poly', 'ost', 'storm', 'amb', 'rep', 'iota', 'tusd', 'ltc', 'rcn', 'sc', 'bat', 'adx', 'wtc', 'qsp', 'steem', 'zil', 'dlt', 'agi', 'wan', 'lsk', 'sky', 'brd', 'nebl', 'bts', 'vet', 'icx', 'cvc', 'zen', 'sys', 'aion', 'loom', 'gto', 'ae', 'neo', 'ada', 'xlm', 'ncash', 'mco', 'theta', 'rdn', 'ont', 'mft', 'nxs', 'eos', 'nav', 'waves', 'yoyo', 'nas', 'nuls', 'gnt', 'xrp', 'xem', 'powr', 'cmt', 'bcpt', 'rpx', 'phx', 'qtum']
bp_coin_pair['binance'] = bib_coin
# bitfinex 币对
bitfinex_coin = {}
bitfinex_coin['eth'] = ['iot', 'eos', 'san', 'omg', 'bch', 'neo', 'etp', 'qtm', 'avt', 'edo', 'dat', 'qsh', 'yyw', 'gnt', 'snt', 'bat', 'mna', 'fun', 'zrx', 'tnb', 'spk', 'trx', 'rcn', 'rlc', 'aid', 'sng', 'rep', 'elf', 'ios', 'aio', 'req', 'rdn', 'lrc', 'wax', 'dai', 'cfi', 'agi', 'bft', 'mtn', 'ode', 'ant', 'dth', 'mit', 'stj', 'xlm', 'xvg', 'mkr', 'ven', 'knc', 'poa', 'lym', 'utk', 'vee', 'dad', 'ors', 'auc', 'poy', 'fsn', 'cbt', 'sen', 'nca', 'cnd', 'ctx', 'see', 'ess', 'atm', 'hot', 'dta', 'wpr', 'zil', 'bnt', 'abs', 'xra', 'man']
bitfinex_coin['gbp'] = ['btc', 'eth', 'neo', 'eos', 'iot', 'xlm']
bitfinex_coin['jpy'] = ['btc', 'eth', 'neo', 'eos', 'iot', 'xlm', 'xvg']
bitfinex_coin['eur'] = ['btc', 'iot', 'eth', 'neo', 'xlm', 'xvg']
bitfinex_coin['btc'] = ['ltc', 'eth', 'etc', 'rrt', 'zec', 'xmr', 'dsh', 'xrp', 'iot', 'eos', 'san', 'omg', 'bch', 'neo', 'etp', 'qtm', 'avt', 'edo', 'btg', 'dat', 'qsh', 'yyw', 'gnt', 'snt', 'bat', 'mna', 'fun', 'zrx', 'tnb', 'spk', 'trx', 'rcn', 'rlc', 'aid', 'sng', 'rep', 'elf', 'ios', 'aio', 'req', 'rdn', 'lrc', 'wax', 'dai', 'cfi', 'agi', 'bft', 'mtn', 'ode', 'ant', 'dth', 'mit', 'stj', 'xlm', 'xvg', 'bci', 'mkr', 'ven', 'knc', 'poa', 'lym', 'utk', 'vee', 'dad', 'ors', 'auc', 'poy', 'fsn', 'cbt', 'zcn', 'sen', 'nca', 'cnd', 'ctx', 'pai', 'see', 'ess', 'atm', 'hot', 'dta', 'iqx', 'wpr', 'zil', 'bnt']
bitfinex_coin['usd'] = ['btc', 'ltc', 'eth', 'etc', 'rrt', 'zec', 'xmr', 'dsh', 'xrp', 'iot', 'eos', 'san', 'omg', 'bch', 'neo', 'etp', 'qtm', 'avt', 'edo', 'btg', 'dat', 'qsh', 'yyw', 'snt', 'bat', 'mna', 'fun', 'zrx', 'tnb', 'spk', 'trx', 'rcn', 'rlc', 'sng', 'rep', 'elf', 'ios', 'aio', 'req', 'rdn', 'lrc', 'wax', 'dai', 'cfi', 'agi', 'bft', 'mtn', 'ode', 'ant', 'dth', 'mit', 'stj', 'xlm', 'xvg', 'bci', 'mkr', 'ven', 'knc', 'poa', 'lym', 'utk', 'vee', 'dad', 'ors', 'auc', 'poy', 'fsn', 'cbt', 'zcn', 'sen', 'nca', 'cnd', 'ctx', 'pai', 'see', 'ess', 'atm', 'hot', 'dta', 'iqx', 'wpr', 'zil', 'bnt', 'abs', 'xra']
bitfinex_coin['eos'] = ['iqx']
bp_coin_pair['bitfinex'] = bitfinex_coin
# bibox币对
bix_coin = {}
bix_coin['dai'] = ['eth', 'btc']
bix_coin['btc'] = ['bix', 'gtc', 'eth', 'ltc', 'bch', 'etc', 'tnb', 'eos', 'cmt', 'btm', 'pra', 'lend', 'rdn', 'mana', 'hpb', 'elf', 'mkr', 'itc', 'mot', 'gnx', 'cat', 'cag', 'aidoc', 'bto', 'amm', 'wax', 'c20', 'snov', 'blt', 'dta', 'gto', 'jnt', 'sxut', 'czr', 'tnc', 'cpc', 'trx', 'fsn', 'uuu', 'abt', 'kick', 'key', 'bbn', 'med', 'qtum', 'dxt', 'neo', 'lgo', 'dash', 'nper', 'acat', 'ipsx', 'bot', 'poa', 'mt', 'eosdac', 'lkn', 'instar', 'red', 'lba', 'pai', 'cwv', 'bcv', 'mtc', 'hdac', 'boe', 'at', 'upp', 'sgc', 'her', 'dcc', 'rte', 'ttc', 'car', 'bznt', 'bu', 'ac3', 'ht', 'ttt', 'orme', 'xnk']
bix_coin['eth'] = ['bix', 'gtc', 'etc', 'bch', 'ltc', 'tnb', 'eos', 'cmt', 'btm', 'pra', 'lend', 'rdn', 'mana', 'hpb', 'elf', 'mkr', 'itc', 'mot', 'gnx', 'cat', 'cag', 'aidoc', 'bto', 'amm', 'wax', 'c20', 'snov', 'blt', 'dta', 'gto', 'jnt', 'sxut', 'czr', 'tnc', 'cpc', 'trx', 'fsn', 'uuu', 'abt', 'kick', 'key', 'bbn', 'med', 'qtum', 'dxt', 'neo', 'lgo', 'dash', 'nper', 'acat', 'ipsx', 'bot', 'poa', 'mt', 'eosdac', 'lkn', 'instar', 'red', 'lba', 'pai', 'cwv', 'bcv', 'mtc', 'hdac', 'boe', 'at', 'upp', 'sgc', 'her', 'dcc', 'rte', 'ttc', 'car', 'bznt', 'bu', 'ac3', 'ht', 'ttt', 'rfr', 'orme', 'xnk']
bix_coin['usdt'] = ['btc', 'eth', 'ltc', 'etc', 'eos', 'bix', 'qtum', 'neo', 'dash', 'hpb', 'btm', 'fsn', 'upp', 'bu', 'ht', 'bch']
bix_coin['bix'] = ['mt', 'hpb', 'eosdac', 'bto', 'gtc', 'btm', 'instar', 'red', 'lba', 'cwv', 'bcv', 'mtc', 'boe', 'upp', 'sgc', 'her', 'dcc', 'rte', 'ttc', 'bznt', 'bu', 'ac3', 'rfr', 'orme']
bp_coin_pair['bibox'] = bix_coin
# zb币对
zb_coin = {}
zb_coin['btc'] = ['btp', 'sbtc', 'eos', 'gnt', 'bth', 'xem', 'btm', 'bds', 'snt', 'kan', 'zrx', 'mtl', 'xwc', 'mith', 'mana', 'ubtc', 'cdc', 'hotc', 'slt', 'bts', 'neo', 'hpy', 'topc', 'safe', 'hlc', 'chat', 'bite', 'bat', 'epc', 'lbtc', 'eth', 'tv', '1st', 'doge', 'edo', 'ltc', 'bcc', 'ddm', 'ent', 'omg', 'bcx', 'true', 'rcn', 'hsr', 'ada', 'knc', 'qtum', 'etc', 'icx', 'xuc', 'gram', 'xrp', 'mco', 'bcd', 'eosdac', 'bcw', 'qun', 'fun', 'zb', 'btn', 'sub', 'ae', 'ink', 'dash', 'xlm']
zb_coin['usdt'] = ['xrp', 'btn', 'etc', 'btm', 'hlc', 'tv', 'bts', 'hotc', 'lbtc', 'snt', 'eosdac', 'eth', 'rcn', 'btp', 'bth', 'xlm', 'cdc', 'mco', 'xwc', 'mana', 'knc', 'hsr', 'ae', 'ltc', 'neo', 'safe', 'bcx', 'dash', 'ddm', 'bat', 'qun', 'eos', 'zb', 'zrx', 'mith', 'sbtc', 'bcw', 'bcd', 'gnt', 'omg', 'hpy', 'topc', 'icx', '1st', 'fun', 'ent', 'edo', 'true', 'ubtc', 'chat', 'btc', 'slt', 'sub', 'ink', 'doge', 'mtl', 'gram', 'xem', 'ada', 'kan', 'qtum', 'bcc']
zb_coin['qc'] = ['xlm', 'zb', 'bds', 'gram', 'mtl', 'doge', 'xuc', 'ink', 'ddm', 'bcc', 'tv', 'mana', 'zrx', 'bat', 'hlc', 'neo', 'mco', 'safe', 'edo', 'kan', 'gnt', 'chat', 'rcn', 'lbtc', 'eos', 'xem', 'ada', 'bts', 'epc', 'btp', 'btn', '1st', 'slt', 'btc', 'xrp', 'mith', 'qun', 'dash', 'bcw', 'btm', 'qtum', 'eth', 'sbtc', 'hpy', 'etc', 'ent', 'ltc', 'aaa', 'omg', 'hsr', 'bcx', 'ubtc', 'icx', 'topc', 'ae', 'snt', 'bitcny', 'bth', 'fun', 'eosdac', 'true', 'knc', 'hotc', 'sub', 'cdc', 'pdx', 'xwc', 'bcd', 'usdt']
zb_coin['zb'] = ['eth', 'xrp', 'dash', 'bcc', 'hsr', 'etc', 'ltc', 'bts', 'qtum', 'eos']
bp_coin_pair['zb'] = zb_coin
# kucoin币对
kucoin_coin = {}
kucoin_coin['kcs'] = ['neo', 'ltc', 'prl', 'tky', 'cs', 'drgn', 'etc', 'gas']
kucoin_coin['neo'] = ['gas', 'soul', 'tky', 'tnc', 'drgn', 'dent', 'loom', 'eos']
kucoin_coin['btc'] = ['eth', 'neo', 'vet', 'kcs', 'tmt', 'olt', 'tfd', 'zinc', 'ut', 'cbc', 'cpc', 'dag', 'dcc', 'edr', 'egt', 'ela', 'loc', 'xlm', 'lala', 'nusd', 'cs', 'aoa', 'etn', 'iht', 'wan', 'dacc', 'dock', 'kick', 'go', 'aph', 'bax', 'deb', 'lym', 'omx', 'ont', 'qkc', 'shl', 'srn', 'datx', 'elec', 'iotx', 'loom', 'mobi', 'open', 'soul', 'tomo', 'trac', 'sphtx', 'cov', 'elf', 'man', 'stk', 'zil', 'zpt', 'dadi', 'bpt', 'tky', 'tnc', 'capp', 'nano', 'poly', 'cxo', 'dta', 'ing', 'mtn', 'ocn', 'snc', 'tel', 'wax', 'cofi', 'pareto', 'adb', 'bos', 'hkn', 'hpb', 'iost', 'ary', 'dbc', 'key', 'gat', 'phx', 'r', 'cv', 'ltc', 'qlc', 'tio', 'acat', 'drgn', 'itc', 'exy', 'mwat', 'agi', 'j8t', 'dent', 'loci', 'cat', 'act', 'arn', 'bch', 'can', 'eos', 'etc', 'gas', 'jnt', 'axpr', 'play', 'chp', 'dna', 'prl', 'utk', 'dash', 'ebtc', 'fota', 'pura', 'cag', 'gla', 'hav', 'spf', 'time', 'abt', 'enj', 'bnty', 'elix', 'aix', 'dat', 'wtc', 'aion', 'qtum', 'dgb', 'snov', 'brd', 'amb', 'btm', 'xlr', 'mana', 'rhoc', 'xas', 'ukg', 'chsb', 'poll', 'ins', 'omg', 'tfl', 'wpr', 'flixx', 'lend', 'knc', 'la', 'bcd', 'snm', 'powr', 'onion', 'btg', 'hsr', 'pbl', 'mod', 'ppt', 'gvt', 'hst', 'snt', 'sub', 'bcpt', 'nebl', 'cvc', 'mth', 'nuls', 'pay', 'rdn', 'req', 'qsp']
kucoin_coin['usdt'] = ['btc', 'eth', 'bch', 'neo', 'kcs', 'nusd', 'cs', 'tky', 'nano', 'ltc', 'drgn', 'ocn', 'dent', 'etc', 'btg', 'eos', 'dadi', 'dash', 'dock', 'go', 'kick', 'open', 'vet', 'xlm', 'omg', 'hav', 'qtum']
kucoin_coin['eth'] = ['neo', 'vet', 'kcs', 'tmt', 'olt', 'tfd', 'zinc', 'ut', 'cbc', 'cpc', 'dag', 'dcc', 'edr', 'egt', 'ela', 'loc', 'xlm', 'lala', 'nusd', 'cs', 'aoa', 'etn', 'iht', 'wan', 'dacc', 'dock', 'kick', 'go', 'aph', 'bax', 'deb', 'lym', 'omx', 'ont', 'qkc', 'shl', 'srn', 'datx', 'elec', 'iotx', 'loom', 'mobi', 'open', 'soul', 'tomo', 'trac', 'sphtx', 'cov', 'elf', 'man', 'stk', 'zil', 'zpt', 'dadi', 'bpt', 'tky', 'tnc', 'capp', 'nano', 'poly', 'cxo', 'dta', 'ing', 'mtn', 'ocn', 'snc', 'tel', 'wax', 'cofi', 'pareto', 'adb', 'bos', 'hkn', 'hpb', 'iost', 'ary', 'dbc', 'key', 'gat', 'phx', 'r', 'cv', 'ltc', 'qlc', 'tio', 'acat', 'drgn', 'itc', 'agi', 'exy', 'mwat', 'j8t', 'dent', 'loci', 'cat', 'act', 'arn', 'bch', 'can', 'eos', 'etc', 'jnt', 'axpr', 'play', 'chp', 'dna', 'prl', 'utk', 'dash', 'ebtc', 'fota', 'pura', 'cag', 'gla', 'hav', 'spf', 'time', 'abt', 'enj', 'bnty', 'elix', 'aix', 'dat', 'aion', 'dgb', 'snov', 'brd', 'amb', 'btm', 'xlr', 'mana', 'rhoc', 'xas', 'ukg', 'chsb', 'poll', 'ins', 'omg', 'tfl', 'wpr', 'flixx', 'lend', 'knc', 'la', 'bcd', 'snm', 'powr', 'onion', 'btg', 'hsr', 'pbl', 'mod', 'ppt', 'gvt', 'hst', 'snt', 'sub', 'bcpt', 'nebl', 'cvc', 'mth', 'nuls', 'pay', 'rdn', 'req', 'qsp']
bp_coin_pair['kucoin'] = kucoin_coin
# fcoin币对
fcoin_coin = {}
fcoin_coin['btc'] = ['ft', 'eth', 'bch', 'ltc', 'etc', 'eos', 'iota', 'xrp']
fcoin_coin['usdt'] = ['btc', 'eth', 'bch', 'ltc', 'ft', 'etc', 'btm', 'bnb', 'zip', 'xrp', 'fi', 'fcandy', '777', 'xps', 'pra', 'hpc', 'gu', 'ft1808', 'iota', 'ft1810_i', 'eos', 'ft1809']
fcoin_coin['eth'] = ['ft', 'zip', 'omg', 'zrx', 'fi', 'icx', 'zil', 'ae', '777', 'gus', 'cccx', 'banca', 'pra', 'dcc', 'sss', 'mdt', 'tst', 'pmd', 'rte', 'xps', 'tct', 'dws', 'ngot', 'at', 'soc', 'blz', 'ocn', 'datx', 'gtc', 'let', 'dag', 'yee', 'aaa', 'nc', 'ait', 'arp', 'gram', 'ifood', 'hpc', 'sgcc', '3db', 'xmx', 'rct', 'cit', 'ees', 'fair', 'brm', 'sda', 'cbr', 'tkt', 'vct', 'biz', 'show', 'pai', 'iov', 'iht', 'fota', 'ejoy', 'iic', 'wte', 'fres', 'mesh', 'icc', 'ionc', 'drct', 'oas', 'but', 'aidoc', 'cofi', 'lxt', 'edu', 'dta', 'msc', 'gene', 'ccc', 'dscoin', 'boc', 'tos', 'fuel', 'pnt', 'sec', 'mof', 'rnt', 'wicc', 'fff', 'cps', 'zsc', 'latx', 'dht', 'see', 'ink', 'sac', 'scl', 'mith', 'smt', 'newos', 'hotc', 'ptt', 'dpn', 'lth', 'jll', 'uto', 'vpp', 'osch', 'ruff', 'baic', 'orme', 'pun', 'facc', 'cwv', 'lmm', 'vlc', 'icst', 'drink1', 'drink', 'musk', 'mxm', 'mitx', 'int', 'btmc', 'cnmc', 'fti', 'qos', 'bhpc', 'dacc', 'unc', 'maya', 'eai', 'mot', 'kan', 'tat', 'box', 'cosm', 'loom', 'gse', 'iost', 'hpb', 'risk', 'vnt', 'vboom', 'ugc', 'kcash', 'rrc', 'vaac', 'lba', 'knc', 'gto', 'bfdt', 'est', 'xin', 'ole', 'bkbt', 'you', 'win', 'fish', 'olt', 'agi', 'kora', 'bft', 'abt', 'mds', 'ors', 'cai', 'tac', 'etc', 'ltc', 'eos', 'iota', 'xrp']
bp_coin_pair['fcoin'] = fcoin_coin
# otcbtc币对
otcbtc_coin = {}
otcbtc_coin['btc'] = ['eth', 'eos', 'gxs', 'bch', 'zec', 'qtum', 'otb', 'trx', 'bnb', 'kin', 'ae', 'xmx', 'rntb', 'key', 'xlm', 'xrp', 'ltc', 'neo', 'pra', 'bcb', 'ada', 'gas', 'ss', 'oct']
otcbtc_coin['eth'] = ['btc', 'eos', 'bch', 'gxs', 'zec', 'qtum', 'otb', 'trx', 'dew', 'bnb', 'uip', 'jex', 'mds', 'lrc', 'tnb', 'pix', 'snt', 'wlk', 'kin', 'credo', 'yoyow', 'seer', 'ae', 'knc', 'iost', 'kk', 'xmx', 'sac', 'rntb', 'bto', 'ait', 'gcs', 'zrx', 'omg', 'cbr', 'ruff', 'key', 'kkc', 'xlm', 'zil', 'btm', 'mobi', 'xrp', 'ees', 'ltc', 'neo', 'pra', 'bcb', 'ada', 'gas', 'eosdac', 'cps', 'ss', 'bcat', 'mt', 'oct']
otcbtc_coin['usdt'] = ['eth', 'btc', 'eos', 'otb', 'bch', 'ada', 'neo', 'ltc', 'xrp', 'xlm']
otcbtc_coin['otb'] = ['eos', 'bch', 'ada', 'neo', 'ltc', 'xrp', 'xlm', 'eosram']
otcbtc_coin['eos'] = ['eosdac', 'eosram', 'oct', 'iq', 'karma']
bp_coin_pair['otcbtc'] = otcbtc_coin
# bigone 币对
bigone_coin = {}
bigone_coin['btc'] = ['dta', 'xin', 'mana', 'neo', 'prs', 'gnt', 'qtum', 'cre', 'idt', 'adx', 'mag', 'knc', 'atn', 'eth', 'pay', 'link', 'mco', 'tnb', 'gnx', 'btm', 'sc', 'dew', 'pix', 'etc', 'at', 'bto', 'sngls', 'ekt', 'elf', 'fair', 'iost', 'mtn', 'fgc', 'gcs', 'ink', 'zec', 'ait', 'bcdn', 'show', 'zrx', 'snt', 'lun', 'bcd', 'eosdac', 'bts', 'pst', 'uip', 'musk', 'gxs', 'qube', 'gct', 'bch', 'sbtc', 'hmc', 'qun', 'cdt', 'dgd', 'storj', 'omg', 'tnt', 'myst', 'eos', 'ltc', 'bat', 'btg', 'cvc', 'read', 'tct', 'edg', 'ae', 'chat', '1st']
bigone_coin['eth'] = ['xin', 'lun', 'idt', 'dta', 'cre', 'omg', 'prs', 'dew', 'mana', 'tct', 'jlp', 'bto', 'eos', 'uto', 'ait', 'chat', 'mtn', 'hmc', 'uip', 'mag', 'qube', 'boe', 'eosdac', 'iost', 'tnb', 'candy', 'bot', 'gct', 'hot', 'gcs', 'sngls', 'fgc', 'oct']
bigone_coin['usdt'] = ['one', 'eth', 'btc', 'bch', 'eos']
bigone_coin['eos'] = ['meetone', 'edna', 'one', 'add', 'karma', 'atd', 'iq', 'horus']
bp_coin_pair['bigone'] = bigone_coin
# binmex币对
binmex_coin = {}
#binmex_coin['xbt'] = ['eth', 'fct', 'ltc', 'lsk']
binmex_coin['usd'] = ['xbt', 'ltc', 'xlt']
#binmex_coin['eth'] = ['dao']
#binmex_coin['xxx'] = ['xbt', 'eth', 'ltc', 'usd', 'fct', 'lsk']
#binmex_coin['cny'] = ['.a50', 'xbt']
bp_coin_pair['binmex'] = binmex_coin



def get_trade_symbol(exchange):
    '''
    返回指定交易所币对字典
    '''
    if exchange not in bp_coin_pair:
        return None
    else:
        return bp_coin_pair[exchange]
    pass


def get_all_tick_keys():
    '''
    获取所有ticker redis键
    '''
    keys = []
    for exchange in bp_coin_pair:
        for base_currency in bp_coin_pair[exchange]:
            for trade_currency in bp_coin_pair[exchange][base_currency]:
                key = 'tick/%s/%s%s'%(exchange, trade_currency, base_currency)
                keys.append(key)
    return keys
    pass


def get_all_depth_keys():
    '''
    获取所有depth redis键
    '''
    keys = []
    for exchange in bp_coin_pair:
        for base_currency in bp_coin_pair[exchange]:
            for trade_currency in bp_coin_pair[exchange][base_currency]:
                key = 'depth/%s/%s%s'%(exchange, trade_currency, base_currency)
                keys.append(key)
    return keys
    pass
