import numpy as np
import torch
import torch.nn as nn
from typing import Dict

class SeaIceUNet(nn.Module):
    """
    A genuine U-Net architecture for spatio-temporal sea-ice concentration prediction.
    Takes recent timesteps of environmental variables and predicts future sea ice concentration.
    """
    def __init__(self, in_channels: int, out_channels: int = 1):
        super(SeaIceUNet, self).__init__()
        
        # Simple U-Net structure suitable for spatial fields
        def conv_block(in_c, out_c):
            return nn.Sequential(
                nn.Conv2d(in_c, out_c, kernel_size=3, padding=1),
                nn.ReLU(inplace=True),
                nn.Conv2d(out_c, out_c, kernel_size=3, padding=1),
                nn.ReLU(inplace=True)
            )
            
        self.enc1 = conv_block(in_channels, 16)
        self.pool1 = nn.MaxPool2d(2)
        
        self.enc2 = conv_block(16, 32)
        self.pool2 = nn.MaxPool2d(2)
        
        self.bottleneck = conv_block(32, 64)
        
        self.upconv2 = nn.ConvTranspose2d(64, 32, kernel_size=2, stride=2)
        self.dec2 = conv_block(64, 32)
        
        self.upconv1 = nn.ConvTranspose2d(32, 16, kernel_size=2, stride=2)
        self.dec1 = conv_block(32, 16)
        
        self.final = nn.Conv2d(16, out_channels, kernel_size=1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        e1 = self.enc1(x)
        p1 = self.pool1(e1)
        
        e2 = self.enc2(p1)
        p2 = self.pool2(e2)
        
        b = self.bottleneck(p2)
        
        u2 = self.upconv2(b)
        
        # Ensure spatial dims match before concat (in case of odd sizes, pad)
        diffY = e2.size()[2] - u2.size()[2]
        diffX = e2.size()[3] - u2.size()[3]
        u2 = nn.functional.pad(u2, [diffX // 2, diffX - diffX // 2, diffY // 2, diffY - diffY // 2])
        
        c2 = torch.cat([e2, u2], dim=1)
        d2 = self.dec2(c2)
        
        u1 = self.upconv1(d2)
        diffY = e1.size()[2] - u1.size()[2]
        diffX = e1.size()[3] - u1.size()[3]
        u1 = nn.functional.pad(u1, [diffX // 2, diffX - diffX // 2, diffY // 2, diffY - diffY // 2])
        
        c1 = torch.cat([e1, u1], dim=1)
        d1 = self.dec1(c1)
        
        out = self.final(d1)
        # Output is in range [0, 1], we map to [0, 100] for concentration
        return self.sigmoid(out) * 100.0


class SeaIceModel:
    """
    Sea-Ice Concentration Spatiotemporal network wrapper.
    Utilizes a U-Net to forecast concentration.
    """
    def __init__(self, forecast_horizon_days: int = 1, seed: int = None):
        self.forecast_horizon_days = forecast_horizon_days
        if seed is not None:
            torch.manual_seed(seed)
            np.random.seed(seed)
            
        # We assume input has 1 channel per historical timestep (e.g., T days of SIC)
        # For simplicity of the interface, we expect T=3 historical days.
        self.history_days = 3
        # Output channels = forecast horizon
        self.unet = SeaIceUNet(in_channels=self.history_days, out_channels=self.forecast_horizon_days)
        self.unet.eval() # Start in eval mode

    def predict(self, temporal_window: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Predicts sea-ice concentration for the next `forecast_horizon_days`.
        
        Args:
            temporal_window: Dict of variables. Expects "sea_ice_concentration" 
                             of shape (T, lat, lon).
                             
        Returns:
            np.ndarray: Predicted sea-ice concentration of shape (forecast_horizon_days, lat, lon).
        """
        if "sea_ice_concentration" not in temporal_window:
            raise ValueError("Missing required input: 'sea_ice_concentration'")
            
        sic = temporal_window["sea_ice_concentration"]
        
        if sic.ndim != 3:
            raise ValueError(f"Expected 3D array (T, lat, lon), got {sic.ndim}D")
            
        T, lat, lon = sic.shape
        if T == 0 or lat == 0 or lon == 0:
            raise ValueError("Input dimensions cannot be zero.")
            
        # We need exactly self.history_days. Pad or truncate as needed.
        if T < self.history_days:
            # Pad with the earliest available data
            pad_size = self.history_days - T
            padding = np.repeat(sic[0:1], pad_size, axis=0)
            sic = np.concatenate([padding, sic], axis=0)
        elif T > self.history_days:
            sic = sic[-self.history_days:]
            
        # Normalization [0, 100] -> [0, 1] for network stability
        sic_norm = sic / 100.0
            
        # Convert to tensor: shape (1, C, H, W)
        with torch.no_grad():
            x = torch.tensor(sic_norm, dtype=torch.float32).unsqueeze(0)
            
            # Forward pass
            predictions = self.unet(x)
            
            # Remove batch dim: shape (forecast_horizon, lat, lon)
            predictions_np = predictions.squeeze(0).numpy()
            
        return np.clip(predictions_np, 0.0, 100.0)
