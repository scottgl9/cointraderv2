# Train a Temporal Fusion Transformer model on cryptocurrency data
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.trend import MACD, SMAIndicator, STCIndicator, KSTIndicator
from ta.volume import OnBalanceVolumeIndicator, ChaikinMoneyFlowIndicator
from pytorch_forecasting import TemporalFusionTransformer, TimeSeriesDataSet
from pytorch_forecasting.data import GroupNormalizer
from pytorch_forecasting.metrics import QuantileLoss
from pytorch_lightning import Trainer
from sklearn.model_selection import train_test_split
from pytorch_lightning import LightningModule
import torch
import argparse

# Step 1: Load Data
def load_candle_data(file_path) -> pd.DataFrame:
    """
    Load and preprocess cryptocurrency candle data.
    Expects a CSV with columns: timestamp, ticker, open, high, low, close, volume.
    """
    df = pd.read_csv(file_path)
    # Convert the Date column to datetime format
    df['Date'] = pd.to_datetime(df['Date'], format='mixed') #'%Y-%m-%d %H:%M:%S')
    # Convert the Date column to unix timestamp
    df['Timestamp'] = df['Date'].apply(lambda x: int(x.timestamp()))
    # Sort the DataFrame by the Date column
    df = df.sort_values(by=['Timestamp', 'Symbol']).reset_index(drop=True)
    df.drop(columns=['Date'], inplace=True)
    # Convert all symbols ending with 'USDT' to '-USDT'
    df['Symbol'] = df['Symbol'].apply(lambda x: x.replace('USDT', '-USDT'))
    # Display the first few rows of the DataFrame
    print(df.head())
    return df

# Step 2: Compute Indicators for Each Cryptocurrency
def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute technical indicators for each cryptocurrency.
    """
    result = []
    # Rename Volume USDT to Volume
    df.rename(columns={'Volume USDT': 'Volume'}, inplace=True)

    for ticker, group in df.groupby("Symbol"):
        print(f"Processing {ticker}...")

        # Add RSI
        group['rsi'] = RSIIndicator(close=group['Close'], window=14).rsi()

        # Add MACD
        macd = MACD(close=group['Close'], window_slow=26, window_fast=12, window_sign=9)
        group['macd'] = macd.macd()
        group['macd_signal'] = macd.macd_signal()

        # Add NATR (Normalized Average True Range)
        group['atr'] = AverageTrueRange(high=group['High'], low=group['Low'], close=group['Close'], window=14).average_true_range()
        group['natr'] = (group['atr'] / group['Close']) * 100

        # Add CMF (Chaikin Money Flow)
        group['cmf'] = ChaikinMoneyFlowIndicator(high=group['High'], low=group['Low'], close=group['Close'], volume=group['Volume'], window=20).chaikin_money_flow()

        # Add Z-Score
        group['z_score'] = (group['Close'] - group['Close'].rolling(window=20).mean()) / group['Close'].rolling(window=20).std()

        # Add SuperTrend
        supertrend = STCIndicator(close=group['Close'], window_slow=50, window_fast=23, cycle=10)
        group['supertrend'] = supertrend.stc()

        # Normalize SuperTrend
        group['supertrend'] = (group['supertrend'] - group['supertrend'].mean()) / group['supertrend'].std()

        # Add KST (Know Sure Thing)
        kst = KSTIndicator(close=group['Close'], roc1=10, roc2=15, roc3=20, roc4=30, window1=10, window2=10, window3=10, window4=15)
        group['kst'] = kst.kst()
        group['kst_signal'] = kst.kst_sig()

        # Add volume oscillator (VO)
        short_ma = df['Volume'].rolling(window=12).mean()
        long_ma = df['Volume'].rolling(window=26).mean()
        vo = ((short_ma - long_ma) / long_ma) * 100
        group['vo'] = vo

        # Fill any NaNs from indicators
        group = group.fillna(0)
        result.append(group)

    return pd.concat(result).reset_index(drop=True)

# Step 3: Preprocess Data for PyTorch Forecasting
def prepare_data(df: pd.DataFrame):
    """
    Prepare the dataframe for training a Temporal Fusion Transformer.
    """
    # Add a target column: Predict price movement direction (1 for up, 0 for down)
    #df['price_movement'] = (df['Close'].shift(-1) > df['Close']).astype(int)

    # Add a target column: Predict price movement direction over the next 10 candles (1 for up, 0 for down)
    df['price_movement'] = (df['Close'].shift(-10) > df['Close']).astype(int)

    # Add time index and group column
    df['time_idx'] = df.groupby("Symbol").cumcount()
    df['group'] = df['Symbol']  # Group by ticker

    # Split into train and validation
    train_df, val_df = train_test_split(df, test_size=0.2, shuffle=False, stratify=None)

    # Define the TimeSeriesDataSet
    training = TimeSeriesDataSet(
        train_df,
        time_idx="time_idx",
        target="price_movement",
        group_ids=["group"],
        min_encoder_length=50,  # Include 50 historical hours
        max_encoder_length=50,
        min_prediction_length=1,
        max_prediction_length=1,
        static_categoricals=["Symbol"],  # Ticker as a static categorical variable
        time_varying_known_reals=["time_idx"],
        time_varying_unknown_reals=[
            "rsi", "macd", "macd_signal", "natr", "cmf", "z_score", "supertrend", "kst", "kst_signal", "vo"
        ],
        target_normalizer=GroupNormalizer(),
    )

    validation = training.to_dataloader(train=False, batch_size=64)
    train_loader = training.to_dataloader(train=True, batch_size=64)

    return train_loader, validation, training

# Step 4: Train the Model
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
            output_size=7,  # Number of quantiles for probabilistic forecasting
            loss=QuantileLoss(),
            reduce_on_plateau_patience=4,
            #logging_metrics=None
        )

    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self.model(x)
        loss = self.model.loss(y_hat, y)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=1e-3)

def train_model(train_loader, validation, training):
    """
    Train a Temporal Fusion Transformer on the prepared data.
    """
    # Define the model
    model = TFTLightningModule(training)

    # Create a PyTorch Lightning trainer
    trainer = Trainer(
        max_epochs=30,
        devices=1 if torch.cuda.is_available() else None,
        accelerator='gpu' if torch.cuda.is_available() else 'cpu',
        gradient_clip_val=0.1,
    )

    # Train the model
    trainer.fit(model, train_dataloaders=train_loader, val_dataloaders=validation)

    return model

# Main Workflow
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Trade simulation with past klines.')
    parser.add_argument('--csv_path', type=str, default='data/crypto_hourly_data/cryptotoken_full_binance_1h.csv', help='Path to the CSV file')
    parser.add_argument('--symbols', type=str, default='BTC-USDT,ETH-USDT,SOL-USDT,HBAR-USDT,DOT-USDT,DOGE-USDT', help='Comma separated list of symbols')
    args = parser.parse_args()
    df = load_candle_data(args.csv_path)

    # Filter the DataFrame by the Timestamp column
    #df = df[(df['Timestamp'] >= start_ts) & (df['Timestamp'] <= end_ts)]

    # Step 2: Compute Indicators
    df = compute_indicators(df)

    # Step 3: Prepare Data
    train_loader, validation, training = prepare_data(df)

    # Step 4: Train the Model
    model = train_model(train_loader, validation, training)
