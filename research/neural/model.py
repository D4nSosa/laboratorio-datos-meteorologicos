"""Baseline CNN-GRU for labelled meteorological image sequences.

PyTorch is optional: importing this module does not require the ML extra.
"""
try:
    import torch
    from torch import nn
except ImportError:  # pragma: no cover - depends on optional environment
    torch = None
    nn = None

if nn is not None:
    class AtmosphericSequenceNet(nn.Module):
        """Classify a sequence shaped [batch, time, channels, height, width]."""
        def __init__(self, input_channels: int, num_classes: int, hidden_size: int = 128):
            super().__init__()
            if input_channels < 1 or num_classes < 2 or hidden_size < 1:
                raise ValueError("input_channels and hidden_size must be positive; num_classes must be >= 2.")
            self.encoder = nn.Sequential(
                nn.Conv2d(input_channels, 32, kernel_size=3, padding=1), nn.BatchNorm2d(32), nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Conv2d(32, 64, kernel_size=3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
                nn.AdaptiveAvgPool2d((1, 1)), nn.Flatten(),
            )
            self.temporal = nn.GRU(input_size=64, hidden_size=hidden_size, batch_first=True)
            self.classifier = nn.Linear(hidden_size, num_classes)

        def forward(self, inputs):
            if inputs.ndim != 5:
                raise ValueError("Expected [batch, time, channels, height, width].")
            batch, steps, channels, height, width = inputs.shape
            frames = inputs.reshape(batch * steps, channels, height, width)
            encoded = self.encoder(frames).reshape(batch, steps, -1)
            sequence, _ = self.temporal(encoded)
            return self.classifier(sequence[:, -1, :])
else:
    class AtmosphericSequenceNet:  # pragma: no cover - optional dependency
        def __init__(self, *args, **kwargs):
            raise ImportError("AtmosphericSequenceNet requiere PyTorch. Instalalo en el entorno experimental, no en el sitio público.")
