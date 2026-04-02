import torch
import torch.nn as nn

class PositionalEncoding(nn.Module):
    def __init__(self, d_model=128, max_len=200):
        super().__init__()
        self.pos = nn.Parameter(torch.randn(1, max_len, d_model))
    def forward(self, x):
        return x + self.pos[:, :x.size(1)]

class SignModel(nn.Module):
    def __init__(self, input_dim=50, d_model=128, num_classes=500):
        super().__init__()
        self.proj = nn.Linear(input_dim, d_model)
        self.pos = PositionalEncoding(d_model)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=8,
            dim_feedforward=256,
            batch_first=True,
            dropout=0.1
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=3)
        self.fc = nn.Linear(d_model, num_classes)

    def forward(self, x):
        x = self.proj(x)
        x = self.pos(x)
        x = self.encoder(x)
        feat = x.mean(dim=1)
        return self.fc(feat)