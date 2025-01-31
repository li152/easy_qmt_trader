from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from xtquant import xtconstant
import time
import pandas as pd
import random
import math
import json
import math
def conv_time(ct):
    '''
    conv_time(1476374400000) --> '20161014000000.000'
    '''
    local_time = time.localtime(ct / 1000)
    data_head = time.strftime('%Y%m%d%H%M%S', local_time)
    data_secs = (ct - int(ct)) * 1000
    time_stamp = '%s.%03d' % (data_head, data_secs)
    return time_stamp
class MyXtQuantTraderCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        """
        连接断开
        :return:
        """
        print("connection lost")
    def on_stock_order(self, order):
        """
        委托回报推送
        :param order: XtOrder对象
        :return:
        """
        print("on order callback:")
        print(order.stock_code, order.order_status, order.order_sysid)
    def on_stock_asset(self, asset):
        """
        资金变动推送
        :param asset: XtAsset对象
        :return:
        """
        print("on asset callback")
        print(asset.account_id, asset.cash, asset.total_asset)
    def on_stock_trade(self, trade):
        """
        成交变动推送
        :param trade: XtTrade对象
        :return:
        """
        print("on trade callback")
        print(trade.account_id, trade.stock_code, trade.order_id)
    def on_stock_position(self, position):
        """
        持仓变动推送
        :param position: XtPosition对象
        :return:
        """
        print("on position callback")
        print(position.stock_code, position.volume)
    def on_order_error(self, order_error):
        """
        委托失败推送
        :param order_error:XtOrderError 对象
        :return:
        """
        print("on order_error callback")
        print(order_error.order_id, order_error.error_id, order_error.error_msg)
    def on_cancel_error(self, cancel_error):
        """
        撤单失败推送
        :param cancel_error: XtCancelError 对象
        :return:
        """
        print("on cancel_error callback")
        print(cancel_error.order_id, cancel_error.error_id, cancel_error.error_msg)
    def on_order_stock_async_response(self, response):
        """
        异步下单回报推送
        :param response: XtOrderResponse 对象
        :return:
        """
        print("on_order_stock_async_response")
        print(response.account_id, response.order_id, response.seq)
class easy_qmt_trader:
    def __init__(self,path= r'D:/国金QMT交易端模拟/userdata_mini',
                  session_id = 123456,account='55009640',account_type='STOCK',
                  is_slippage=True,slippage=0.01) -> None:
        '''
        简化版的qmt_trder方便大家做策略的开发类的继承
        '''
        self.xt_trader=''
        self.acc=''
        self.path=path
        self.session_id=int(self.random_session_id())
        self.account=account
        self.account_type=account_type
        if is_slippage==True:
            self.slippage=slippage
        else:
            self.slippage=0
    def random_session_id(self):
        '''
        随机id
        '''
        session_id=''
        for i in range(0,9):
            session_id+=str(random.randint(1,9))
        return session_id
    def select_slippage(self,stock='600031',price=15.01,trader_type='buy'):
        '''
        选择滑点
        安价格来滑点，比如0.01就是一块
        etf3位数,股票可转债2位数
        '''
        stock=self.adjust_stock(stock=stock)
        data_type=self.select_data_type(stock=stock)
        if data_type=='fund' or data_type=='bond':
            slippage=self.slippage/10
            if trader_type=='buy' or trader_type==23:
                price=price+slippage
            else:
                price=price-slippage
        else:
            slippage=self.slippage
            if trader_type=='buy' or trader_type==23:
                price=price+slippage
            else:
                price=price-slippage
        return price
    def check_is_trader_date_1(self,trader_time=4,start_date=9,end_date=14,start_mi=0,jhjj='否'):
        '''
        检测是不是交易时间
        '''
        if jhjj=='是':
            jhjj_time=15
        else:
            jhjj_time=30
        loc=time.localtime()
        tm_hour=loc.tm_hour
        tm_min=loc.tm_min
        wo=loc.tm_wday
        if wo<=trader_time:
            if tm_hour>=start_date and tm_hour<=end_date:
                if tm_hour==9 and tm_min<jhjj_time:
                    return False
                elif tm_min>=start_mi:
                    return True
                else:
                    return False
            else:
                return False    
        else:
            print('周末')
            return False
    def select_data_type(self,stock='600031'):
        '''
        选择数据类型
        '''
        if stock[:3] in ['110','113','123','127','128','111','118'] or stock[:2] in ['11','12']:
            return 'bond'
        elif stock[:3] in ['510','511','512','513','514','515','516','517','518','588','159','501','164'] or stock[:2] in ['16']:
            return 'fund'
        else:
            return 'stock'
    def adjust_stock(self,stock='600031.SH'):
        '''
        调整代码
        '''
        if stock[-2:]=='SH' or stock[-2:]=='SZ' or stock[-2:]=='sh' or stock[-2:]=='sz':
            stock=stock.upper()
        else:
            if stock[:3] in ['600','601','603','688','510','511',
                             '512','513','515','113','110','118','501'] or stock[:2] in ['11']:
                stock=stock+'.SH'
            else:
                stock=stock+'.SZ'
        return stock
    def check_stock_is_av_buy(self,stock='128036',price='156.700',amount=10,hold_limit=100000):
        '''
        检查是否可以买入
        '''
        hold_stock=self.position()
        try:
            del hold_stock['Unnamed: 0']
        except:
            pass
        account=self.balance()
        try:
            del account['Unnamed: 0']
        except:
            pass
        #买入是价值
        value=price*amount
        cash=account['可用金额'].tolist()[-1]
        frozen_cash=account['冻结金额'].tolist()[-1]
        market_value=account['持仓市值'].tolist()[-1]
        total_asset=account['总资产'].tolist()[-1]
        if cash>=value:
            print('允许买入{} 可用现金{}大于买入金额{} 价格{} 数量{}'.format(stock,cash,value,price,amount))
            return True
        else:
            print('不允许买入{} 可用现金{}小于买入金额{} 价格{} 数量{}'.format(stock,cash,value,price,amount))
            return False
    def check_stock_is_av_sell(self,stock='128036',amount=10):
        '''
        检查是否可以卖出
        '''
        #stock=self.adjust_stock(stock=stock)
        hold_data=self.position()
        try:
            del hold_data['Unnamed: 0']
        except:
            pass
        account=self.balance()
        try:
            del account['Unnamed: 0']
        except:
            pass
        #买入是价值
        cash=account['可用金额'].tolist()[-1]
        frozen_cash=account['冻结金额'].tolist()[-1]
        market_value=account['持仓市值'].tolist()[-1]
        total_asset=account['总资产'].tolist()[-1]
        stock_list=hold_data['证券代码'].tolist()
        if stock in stock_list:
            hold_num=hold_data[hold_data['证券代码']==stock]['可用余额'].tolist()[-1]
            if hold_num>=amount:
                print('允许卖出：{} 持股{} 卖出{}'.format(stock,hold_num,amount))
                return True
            else:
                print('不允许卖出持股不足：{} 持股{} 卖出{}'.format(stock,hold_num,amount))
                return False
        else:
            print('不允许卖出没有持股：{} 持股{} 卖出{}'.format(stock,0,amount))
            return False
    def connect(self):
        '''
        连接
        path qmt userdata_min是路径
        session_id 账户的标志,随便
        account账户,
        account_type账户内类型
        '''
        print('链接qmt')
        # path为mini qmt客户端安装目录下userdata_mini路径
        path = self.path
        # session_id为会话编号，策略使用方对于不同的Python策略需要使用不同的会话编号
        session_id = self.session_id
        xt_trader = XtQuantTrader(path, session_id)
        # 创建资金账号为1000000365的证券账号对象
        account=self.account
        account_type=self.account_type
        acc = StockAccount(account_id=account,account_type=account_type)
        # 创建交易回调类对象，并声明接收回调
        callback = MyXtQuantTraderCallback()
        xt_trader.register_callback(callback)
        # 启动交易线程
        xt_trader.start()
        # 建立交易连接，返回0表示连接成功
        connect_result = xt_trader.connect()
        if connect_result==0:
            # 对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功
            subscribe_result = xt_trader.subscribe(acc)
            print(subscribe_result)
            self.xt_trader=xt_trader
            self.acc=acc
            return xt_trader,acc
        else:
            print('qmt连接失败')
    def order_stock(self,stock_code='600031.SH', order_type=xtconstant.STOCK_BUY,
                    order_volume=100,price_type=xtconstant.FIX_PRICE,price=20,strategy_name='',order_remark=''):
            '''
            下单，统一接口
            :param account: 证券账号
                :param stock_code: 证券代码, 例如"600000.SH"
                :param order_type: 委托类型, 23:买, 24:卖
                :param order_volume: 委托数量, 股票以'股'为单位, 债券以'张'为单位
                :param price_type: 报价类型, 详见帮助手册
                :param price: 报价价格, 如果price_type为指定价, 那price为指定的价格, 否则填0
                :param strategy_name: 策略名称
                :param order_remark: 委托备注
                :return: 返回下单请求序号, 成功委托后的下单请求序号为大于0的正整数, 如果为-1表示委托失败
            '''
        
            # 对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功
            subscribe_result = self.xt_trader.subscribe(self.acc)
            print(self.xt_trader.query_stock_asset_async(account=self.acc,callback=subscribe_result))
            #print(subscribe_result)
            stock_code = self.adjust_stock(stock=stock_code)
            price=self.select_slippage(stock=stock_code,price=price,trader_type=order_type)
            # 使用指定价下单，接口返回订单编号，后续可以用于撤单操作以及查询委托状态
            fix_result_order_id = self.xt_trader.order_stock(account=self.acc,stock_code=stock_code, order_type=order_type,
                                                            order_volume=order_volume, price_type=price_type,
                                                            price=price, strategy_name=strategy_name, order_remark=order_remark)
            print('交易类型{} 代码{} 价格{} 数量{} 订单编号{}'.format(order_type,stock_code,price,order_volume,fix_result_order_id))
            return fix_result_order_id
    def buy(self,security='600031.SH', order_type=xtconstant.STOCK_BUY,
                    amount=100,price_type=xtconstant.FIX_PRICE,price=20,strategy_name='',order_remark=''):
        '''
        单独独立股票买入函数
        '''
        # 对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功
        subscribe_result = self.xt_trader.subscribe(self.acc)
        print(self.xt_trader.query_stock_asset_async(account=self.acc,callback=subscribe_result))
        #print(subscribe_result)
        stock_code =self.adjust_stock(stock=security)
        price=self.select_slippage(stock=security,price=price,trader_type='buy')
        order_volume=amount
        # 使用指定价下单，接口返回订单编号，后续可以用于撤单操作以及查询委托状态
        if order_volume>0:
            fix_result_order_id = self.xt_trader.order_stock_async(account=self.acc,stock_code=stock_code, order_type=order_type,
                                                                order_volume=order_volume, price_type=price_type,
                                                                price=price, strategy_name=strategy_name, order_remark=order_remark)
            print('交易类型{} 代码{} 价格{} 数量{} 订单编号{}'.format(order_type,stock_code,price,order_volume,fix_result_order_id))
            return fix_result_order_id
        else:
            print('买入 标的{} 价格{} 委托数量{}小于0有问题'.format(stock_code,price,order_volume))
    def sell(self,security='600031.SH', order_type=xtconstant.STOCK_SELL,
                    amount=100,price_type=xtconstant.FIX_PRICE,price=20,strategy_name='',order_remark=''):
        '''
        单独独立股票卖出函数
        '''
        # 对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功
        subscribe_result = self.xt_trader.subscribe(self.acc)
        print(self.xt_trader.query_stock_asset_async(account=self.acc,callback=subscribe_result))
        #print(subscribe_result)
        stock_code =self.adjust_stock(stock=security)
        price=self.select_slippage(stock=security,price=price,trader_type='sell')
        order_volume=amount
        # 使用指定价下单，接口返回订单编号，后续可以用于撤单操作以及查询委托状态
        if order_volume>0:
            fix_result_order_id = self.xt_trader.order_stock(account=self.acc,stock_code=stock_code, order_type=order_type,
                                                                order_volume=order_volume, price_type=price_type,
                                                                price=price, strategy_name=strategy_name, order_remark=order_remark)
            print('交易类型{} 代码{} 价格{} 数量{} 订单编号{}'.format(order_type,stock_code,price,order_volume,fix_result_order_id))
            return fix_result_order_id
        else:
            print('卖出 标的{} 价格{} 委托数量{}小于0有问题'.format(stock_code,price,order_volume))

    def order_stock_async(self,stock_code='600031.SH', order_type=xtconstant.STOCK_BUY,
                    order_volume=100,price_type=xtconstant.FIX_PRICE,price=20,strategy_name='',order_remark=''):
        '''
         释义 
        - 对股票进行异步下单操作，异步下单接口如果正常返回了下单请求序号seq，会收到on_order_stock_async_response的委托反馈
        * 参数
        - account - StockAccount 资金账号
        - stock_code - str 证券代码， 如'600000.SH'
        - order_type - int 委托类型
        - order_volume - int 委托数量，股票以'股'为单位，债券以'张'为单位
        - price_type - int 报价类型
        - price - float 委托价格
        - strategy_name - str 策略名称
        - order_remark - str 委托备注
        '''
        # 对交易回调进行订阅，订阅后可以收到交易主推，返回0表示订阅成功
        subscribe_result = self.xt_trader.subscribe(self.acc)
        print(self.xt_trader.query_stock_asset_async(account=self.acc,callback=subscribe_result))
        #print(subscribe_result)
        stock_code = self.adjust_stock(stock=stock_code)
        price=self.select_slippage(stock=stock_code,price=price,trader_type=order_type)
        # 使用指定价下单，接口返回订单编号，后续可以用于撤单操作以及查询委托状态
        fix_result_order_id = self.xt_trader.order_stock_async(account=self.acc,stock_code=stock_code, order_type=order_type,
                                                            order_volume=order_volume, price_type=price_type,
                                                            price=price, strategy_name=strategy_name, order_remark=order_remark)
        print('交易类型{} 代码{} 价格{} 数量{} 订单编号{}'.format(order_type,stock_code,price,order_volume,fix_result_order_id))
        return fix_result_order_id
    def cancel_order_stock(self,order_id=12):
        '''
        :param account: 证券账号
            :param order_id: 委托编号, 报单时返回的编号
            :return: 返回撤单成功或者失败, 0:成功,  -1:委托已完成撤单失败, -2:未找到对应委托编号撤单失败, -3:账号未登陆撤单失败
        '''
        # 使用订单编号撤单
        cancel_order_result = self.xt_trader.cancel_order_stock(account=self.acc,order_id=order_id)
        if cancel_order_result==0:
            print('成功')
        elif cancel_order_result==-1:
            print('委托已完成撤单失败')
        elif cancel_order_result==-2:
            print('找到对应委托编号撤单失败')
        elif cancel_order_result==-3:
            print('账号未登陆撤单失败')
        else:
            pass
        return cancel_order_result
    def cancel_order_stock_async(self,order_id=12):
        '''
        * 释义 
        - 根据订单编号对委托进行异步撤单操作
        * 参数
        - account - StockAccount  资金账号 
        - order_id - int 下单接口返回的订单编号
        * 返回 
        - 返回撤单请求序号, 成功委托后的撤单请求序号为大于0的正整数, 如果为-1表示委托失败
        * 备注
        - 如果失败，则通过撤单失败主推接口返回撤单失败信息
        '''
        # 使用订单编号撤单
        cancel_order_result = self.xt_trader.cancel_order_stock_async(account=self.acc,order_id=order_id)
        if cancel_order_result==0:
            print('成功')
        elif cancel_order_result==-1:
            print('委托已完成撤单失败')
        elif cancel_order_result==-2:
            print('找到对应委托编号撤单失败')
        elif cancel_order_result==-3:
            print('账号未登陆撤单失败')
        else:
            pass
        return cancel_order_result
    def query_stock_asset(self):
        '''
        :param account: 证券账号
            :return: 返回当前证券账号的资产数据
        '''
        # 查询证券资产
        
        asset = self.xt_trader.query_stock_asset(account=self.acc)
        data_dict={}
        if asset:
            data_dict['账号类型']=asset.account_type
            data_dict['资金账户']=asset.account_id
            data_dict['可用金额']=asset.cash
            data_dict['冻结金额']=asset.frozen_cash
            data_dict['持仓市值']=asset.market_value
            data_dict['总资产']=asset.total_asset
            return data_dict
        else:
            print('获取失败资金')
            data_dict['账号类型']=[None]
            data_dict['资金账户']=[None]
            data_dict['可用金额']=[None]
            data_dict['冻结金额']=[None]
            data_dict['持仓市值']=[None]
            data_dict['总资产']=[None]
            return  data_dict
    def balance(self):
        '''
        对接同花顺
        '''
        try:
            asset = self.xt_trader.query_stock_asset(account=self.acc)
            df=pd.DataFrame()
            if asset:
                df['账号类型']=[asset.account_type]
                df['资金账户']=[asset.account_id]
                df['可用金额']=[asset.cash]
                df['冻结金额']=[asset.frozen_cash]
                df['持仓市值']=[asset.market_value]
                df['总资产']=[asset.total_asset]
                return df
        except:
            print('获取账户失败，读取上次数据，谨慎使用')
            df=pd.DataFrame()
            return df
    def query_stock_orders(self):
        '''
        当日委托
         :param account: 证券账号
        :param cancelable_only: 仅查询可撤委托
        :return: 返回当日所有委托的委托对象组成的list
        '''
        orders = self.xt_trader.query_stock_orders(self.acc)
        print("委托数量", len(orders))
        data=pd.DataFrame()
        if len(orders) != 0:
            for i in range(len(orders)):
                df=pd.DataFrame()
                df['账号类型']=[orders[i].account_type]
                df['资金账号']=[orders[i].account_id]
                df['证券代码']=[orders[i].stock_code]
                df['证券代码']=df['证券代码'].apply(lambda x:str(x)[:6])
                df['订单编号']=[orders[i].order_id]
                df['柜台合同编号']=[orders[i].order_sysid]
                df['报单时间']=[orders[i].order_time]
                df['委托类型']=[orders[i].order_type]
                df['委托数量']=[orders[i].order_volume]
                df['报价类型']=[orders[i].price_type]
                df['委托价格']=[orders[i].price]
                df['成交数量']=[orders[i].traded_volume]
                df['成交均价']=[orders[i].traded_price]
                df['委托状态']=[orders[i].order_status]
                df['委托状态描述']=[orders[i].status_msg]
                df['策略名称']=[orders[i].strategy_name]
                df['委托备注']=[orders[i].order_remark]
                data=pd.concat([data,df],ignore_index=True)
            data['报单时间']=pd.to_datetime(data['报单时间'],unit='s')
            return data
        else:
            print('目前没有委托')
            return data
    def today_entrusts(self):
        '''
        对接同花顺
        今天委托
        '''
        def select_data(x):
            if x==48:
                return '未报'
            elif x==49:
                return '待报'
            elif x==50:
                return '已报'
            elif x==51:
                return '已报待撤'
            elif x==52:
                return '部分待撤'
            elif x==53:
                return '部撤'
            elif x==54:
                return '已撤'
            elif x==55:
                return '部成'
            elif x==56:
                return '已成'
            elif x==57:
                return '废单'
            else:
                return '废单'
        orders = self.xt_trader.query_stock_orders(self.acc)
        print("委托数量", len(orders))
        data=pd.DataFrame()
        if len(orders) != 0:
            for i in range(len(orders)):
                df=pd.DataFrame()
                df['账号类型']=[orders[i].account_type]
                df['资金账号']=[orders[i].account_id]
                df['证券代码']=[orders[i].stock_code]
                df['证券代码']=df['证券代码'].apply(lambda x:str(x)[:6])
                df['订单编号']=[orders[i].order_id]
                df['柜台合同编号']=[orders[i].order_sysid]
                df['报单时间']=[orders[i].order_time]
                df['委托类型']=[orders[i].order_type]
                df['委托数量']=[orders[i].order_volume]
                df['报价类型']=[orders[i].price_type]
                df['委托价格']=[orders[i].price]
                df['成交数量']=[orders[i].traded_volume]
                df['成交均价']=[orders[i].traded_price]
                df['委托状态']=[orders[i].order_status]
                df['委托状态描述']=[orders[i].status_msg]
                df['策略名称']=[orders[i].strategy_name]
                df['委托备注']=[orders[i].order_remark]
                data=pd.concat([data,df],ignore_index=True)
            data['报单时间']=df['报单时间'].apply(conv_time)
            data['委托状态翻译']=data['委托状态'].apply(select_data)
            data['未成交数量']=data['委托数量']-data['成交数量']
            data['未成交价值']=data['未成交数量']*data['委托价格']
            return data
        else:
            print('目前没有委托')
            return data
    def query_stock_trades(self):
        '''
        当日成交
        '''
        trades = self.xt_trader.query_stock_trades(self.acc)
        print("成交数量:", len(trades))
        data=pd.DataFrame()
        if len(trades) != 0:
            for i in range(len(trades)):
                df=pd.DataFrame()
                df['账号类型']=[trades[i].account_type]
                df['资金账号']=[trades[i].account_id]
                df['证券代码']=[trades[i].stock_code]
                df['证券代码']=df['证券代码'].apply(lambda x:str(x)[:6])
                df['委托类型']=[trades[i].order_type]
                df['成交编号']=[trades[i].traded_id]
                df['成交时间']=[trades[i].traded_time]
                df['成交均价']=[trades[i].traded_price]
                df['成交数量']=[trades[i].traded_volume]
                df['成交金额']=[trades[i].traded_amount]
                df['订单编号']=[trades[i].order_id]
                df['柜台合同编号']=[trades[i].order_sysid]
                df['策略名称']=[trades[i].strategy_name]
                df['委托备注']=[trades[i].order_remark]
                data=pd.concat([data,df],ignore_index=True)
            data['成交时间']=pd.to_datetime(data['成交时间'],unit='s')
            return data
        else:
            print('今日没有成交')     
            return data
    def today_trades(self):
        '''
        对接同花顺
        今日成交
        '''
        trades = self.xt_trader.query_stock_trades(self.acc)
        print("成交数量:", len(trades))
        data=pd.DataFrame()
        if len(trades) != 0:
            for i in range(len(trades)):
                df=pd.DataFrame()
                df['账号类型']=[trades[i].account_type]
                df['资金账号']=[trades[i].account_id]
                df['证券代码']=[trades[i].stock_code]
                df['证券代码']=df['证券代码'].apply(lambda x:str(x)[:6])
                df['委托类型']=[trades[i].order_type]
                df['成交编号']=[trades[i].traded_id]
                df['成交时间']=[trades[i].traded_time]
                df['成交均价']=[trades[i].traded_price]
                df['成交数量']=[trades[i].traded_volume]
                df['成交金额']=[trades[i].traded_amount]
                df['订单编号']=[trades[i].order_id]
                df['柜台合同编号']=[trades[i].order_sysid]
                df['策略名称']=[trades[i].strategy_name]
                df['委托备注']=[trades[i].order_remark]
                data=pd.concat([data,df],ignore_index=True)
            def select_data(x):
                if x==xtconstant.STOCK_BUY:
                    return '证券买入'
                elif x==xtconstant.STOCK_SELL:
                    return '证券卖出'
                else:
                    return '无'
            df['操作']=df['委托类型'].apply(select_data)
            data['成交时间']=pd.to_datetime(data['成交时间'],unit='s')
            return data
        else:
            print('今日没有成交')     
            return data
    def query_stock_positions(self):
        '''
        查询账户所有的持仓
        '''
        positions = self.xt_trader.query_stock_positions(self.acc)
        print("持仓数量:", len(positions))
        data=pd.DataFrame()
        if len(positions) != 0:
            for i in range(len(positions)):
                df=pd.DataFrame()
                df['账号类型']=[positions[i].account_type]
                df['资金账号']=[positions[i].account_id]
                df['证券代码']=[positions[i].stock_code]
                df['证券代码']=df['证券代码'].apply(lambda x:str(x)[:6])
                df['持仓数量']=[positions[i].volume]
                df['可用数量']=[positions[i].can_use_volume]
                df['平均建仓成本']=[positions[i].open_price]
                df['市值']=[positions[i].market_value]
                data=pd.concat([data,df],ignore_index=True)
            return data
        else:
            print('没有持股')
            df=pd.DataFrame()
            df['账号类型']=[None]
            df['资金账号']=[None]
            df['证券代码']=[None]
            df['持仓数量']=[None]
            df['可用数量']=[None]
            df['平均建仓成本']=[None]
            df['市值']=[None]
            return df
    def position(self):
        '''
        对接同花顺
        持股
        '''
        try:
            positions = self.xt_trader.query_stock_positions(self.acc)
            print("持仓数量:", len(positions))
            data=pd.DataFrame()
            if len(positions) != 0:
                for i in range(len(positions)):
                    df=pd.DataFrame()
                    df['账号类型']=[positions[i].account_type]
                    df['资金账号']=[positions[i].account_id]
                    df['证券代码']=[positions[i].stock_code]
                    df['证券代码']=df['证券代码'].apply(lambda x:str(x)[:6])
                    df['股票余额']=[positions[i].volume]
                    df['可用余额']=[positions[i].can_use_volume]
                    df['成本价']=[positions[i].open_price]
                    df['参考成本价']=[positions[i].open_price]
                    df['市值']=[positions[i].market_value]
                    data=pd.concat([data,df],ignore_index=True)
                return data
            else:
                df=pd.DataFrame()
                df['账号类型']=None
                df['资金账号']=None
                df['证券代码']=None
                df['股票余额']=None
                df['可用余额']=None
                df['成本价']=None
                df['市值']=None
                df['选择']=None
                df['持股天数']=None
                df['交易状态']=None
                df['明细']=None
                df['证券名称']=None
                df['冻结数量']=None
                df['市价']=None
                df['盈亏']=None
                df['盈亏比(%)']=None
                df['当日买入']=None	
                df['当日卖出']=None
                return df
                
        except:
            df=pd.DataFrame()
            return df
    def run_forever(self):
        '''
        阻塞线程，接收交易推送
        '''
        self.xt_trader.run_forever()
    def stop(self):
        self.xt_trader.stop()
if __name__=='__main__':
    models=easy_qmt_trader()
    models.connect()
    print(models.query_stock_orders())
    models.buy()
    models1=easy_qmt_trader(account='55009680',session_id=123457)
    models1.connect()
    print(models1.query_stock_positions())
    
