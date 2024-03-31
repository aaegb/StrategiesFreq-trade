from freqtrade.strategy import IStrategy, informative
from pandas import DataFrame
import freqtrade.vendor.qtpylib.indicators as qtpylib
import talib.abstract as ta
from freqtrade.persistence import Trade
from datetime import datetime, timedelta
from typing import Optional, Union

class strat_template (IStrategy):

    def version(self) -> str:
        return "template-v1"

    INTERFACE_VERSION = 3

    minimal_roi = {
        "0": 0.05
    }

    stoploss = -0.05

    timeframe = '15m'

    process_only_new_candles = True
    startup_candle_count = 999

    use_custom_stoploss = True

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime, current_rate: float, current_profit: float, **kwargs) -> float:
        
        sl_new = 1

        if (current_time - timedelta(minutes=15) >= trade.open_date_utc):

            dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
            current_candle = dataframe.iloc[-1].squeeze()
            current_profit = trade.calc_profit_ratio(current_candle['close'])

            if (current_profit >= 0.03):
                sl_new = 0.01

        return sl_new

    def custom_exit(self, pair: str, trade: Trade, current_time: datetime, current_rate: float, current_profit: float, **kwargs) -> Optional[Union[str, bool]]:

        if ((current_time - timedelta(minutes=15)) >= trade.open_date_utc):

            dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
            current_candle = dataframe.iloc[-1].squeeze()
            current_profit = trade.calc_profit_ratio(current_candle['close'])
            
            if (current_profit >= 0):
                if (current_candle['rsi'] >= 70):
                    return "rsi_overbought"

    @informative('30m')
    def populate_indicators_inf1(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        dataframe['rsi'] = ta.RSI(dataframe['close'], 14)

        return dataframe

    @informative('1h')
    def populate_indicators_inf2(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        dataframe['rsi'] = ta.RSI(dataframe['close'], 14)

        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe['ema_26'] = ta.EMA(dataframe['close'], 26)
        dataframe['ema_34'] = ta.EMA(dataframe['close'], 34)
        dataframe['rsi'] = ta.RSI(dataframe['close'], 14)
        dataframe['ema_4_rsi'] = ta.EMA(dataframe['rsi'], 4)

        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            qtpylib.crossed_above(dataframe['ema_26'], dataframe['ema_34'])
            &
            (dataframe['rsi_30m'] < 50)
            &
            (dataframe['rsi_1h'] < 30)
            &
            (dataframe['ema_4_rsi'] < 70)
            &
            (dataframe['volume'] > 0)
            , ['enter_long', 'enter_tag']
        ] = (1, 'golden cross')

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            qtpylib.crossed_below(dataframe['ema_26'], dataframe['ema_34'])
            &
            (dataframe['volume'] > 0)
            , ['exit_long', 'exit_tag']
        ] = (1, 'death cross')

        return dataframe
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe['ema_34'] = ta.EMA(dataframe['close'], 34)
        dataframe['ema_26'] = ta.EMA(dataframe['close'], 26)
        dataframe['rsi'] = ta.RSI(dataframe['close'], 14)
        dataframe['ema_4_rsi'] = ta.EMA(dataframe['rsi'], 4)

        return dataframe