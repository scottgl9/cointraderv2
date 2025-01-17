import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
from ta.trend import MACD, STCIndicator, KSTIndicator
from ta.volume import ChaikinMoneyFlowIndicator
from pytorch_forecasting import TemporalFusionTransformer, TimeSeriesDataSet
from pytorch_forecasting.data import GroupNormalizer
from pytorch_forecasting.metrics import MAE
from pytorch_lightning import Trainer, LightningModule
from sklearn.model_selection import train_test_split
import torch
import argparse
from ta.momentum import UltimateOscillator, StochasticOscillator
from ta.trend import CCIIndicator

def load_candle_data(file_path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'], format='mixed')
    df['Timestamp'] = df['Date'].apply(lambda x: int(x.timestamp()))
    df = df.sort_values(by=['Timestamp', 'Symbol']).reset_index(drop=True)
    df.drop(columns=['Date'], inplace=True)
    df['Symbol'] = df['Symbol'].apply(lambda x: x.replace('USDT', '-USDT'))
    print(df.head())
    return df

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df.rename(columns={'Volume USDT': 'Volume'}, inplace=True)
    result = []
    for ticker, group in df.groupby("Symbol"):
        group['rsi'] = RSIIndicator(close=group['Close'], window=14).rsi()
        macd = MACD(close=group['Close'], window_slow=26, window_fast=12, window_sign=9)
        group['macd'] = macd.macd()
        group['macd_signal'] = macd.macd_signal()
        group['atr'] = AverageTrueRange(high=group['High'], low=group['Low'], close=group['Close'], window=14).average_true_range()
        group['natr'] = (group['atr'] / group['Close']) * 100
        group['cmf'] = ChaikinMoneyFlowIndicator(high=group['High'], low=group['Low'], close=group['Close'], volume=group['Volume'], window=20).chaikin_money_flow()
        group['z_score'] = (group['Close'] - group['Close'].rolling(window=20).mean()) / group['Close'].rolling(window=20).std()
        supertrend = STCIndicator(close=group['Close'], window_slow=50, window_fast=23, cycle=10)
        group['supertrend'] = (supertrend.stc() - supertrend.stc().mean()) / supertrend.stc().std()
        kst = KSTIndicator(close=group['Close'], roc1=10, roc2=15, roc3=20, roc4=30, window1=10, window2=10, window3=10, window4=15)
        group['kst'] = kst.kst()
        group['kst_signal'] = kst.kst_sig()
        short_ma = group['Volume'].rolling(window=12).mean()
        long_ma = group['Volume'].rolling(window=26).mean()
        group['vo'] = ((short_ma - long_ma) / long_ma) * 100

        uo = UltimateOscillator(high=group['High'], low=group['Low'], close=group['Close'], window1=7, window2=14, window3=28)
        group['uo'] = uo.ultimate_oscillator()

        stoch = StochasticOscillator(high=group['High'], low=group['Low'], close=group['Close'], window=14, smooth_window=3)
        group['stoch_k'] = stoch.stoch()
        group['stoch_d'] = stoch.stoch_signal()

        cci = CCIIndicator(high=group['High'], low=group['Low'], close=group['Close'], window=20)
        group['cci'] = cci.cci()

        # percent price change in the last 50 candles
        group["pct_change"] = (group["Close"].pct_change(50) * 100)

        group = group.fillna(0)
        result.append(group)
    return pd.concat(result).reset_index(drop=True)

def prepare_data(df: pd.DataFrame):
    # Predict the percent price change over next 10 candles
    df['price_strength'] = ((df['Close'].shift(-10) - df['Close']) / df['Close']) * 100
    df['time_idx'] = df.groupby("Symbol").cumcount()
    df['group'] = df['Symbol']
    train_df, val_df = train_test_split(df, test_size=0.2, shuffle=False)
    training = TimeSeriesDataSet(
        train_df,
        time_idx="time_idx",
        target="price_strength",
        group_ids=["group"],
        min_encoder_length=50,
        max_encoder_length=50,
        min_prediction_length=1,
        max_prediction_length=1,
        static_categoricals=["Symbol"],
        time_varying_known_reals=["time_idx"],
        time_varying_unknown_reals=[
            "rsi", "macd", "macd_signal", "natr", "cmf", "z_score",
            "supertrend", "kst", "kst_signal", "vo", "uo", "stoch_k", "stoch_d", "cci", "pct_change"
        ],
        target_normalizer=GroupNormalizer(),
    )
    validation = training.to_dataloader(train=False, batch_size=64)
    train_loader = training.to_dataloader(train=True, batch_size=64)
    return train_loader, validation, training

class TFTLightningModule(LightningModule):
    def __init__(self, training):
        super().__init__()
        self.model = TemporalFusionTransformer.from_dataset(
            training,
            learning_rate=1e-3,
            hidden_size=16,
            attention_head_size=1,
            dropout=0.1,
            hidden_continuous_size=8,
            output_size=1,
            loss=MAE(),
            reduce_on_plateau_patience=4,
        ).to(torch.device('cuda' if torch.cuda.is_available() else 'cpu'))

    def training_step(self, batch, batch_idx):
        x, y = batch
        output = self.model(x)
        y_hat = output.prediction
        loss = self.model.loss(y_hat, y)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=1e-3)

def train_model(train_loader, validation, training):
    model = TFTLightningModule(training)
    trainer = Trainer(
        max_epochs=30,
        devices=1 if torch.cuda.is_available() else None,
        accelerator='gpu' if torch.cuda.is_available() else 'cpu',
        gradient_clip_val=0.1,
    )
    trainer.fit(model, train_loader, validation)
    return model

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train a TFT model for price strength.')
    parser.add_argument('--csv_path', type=str, default='data/crypto_hourly_data/cryptotoken_full_binance_1h.csv', help='Path to the CSV file')
    args = parser.parse_args()
    df = load_candle_data(args.csv_path)
    df = compute_indicators(df)
    train_loader, validation, training = prepare_data(df)
    trained_model = train_model(train_loader, validation, training)
