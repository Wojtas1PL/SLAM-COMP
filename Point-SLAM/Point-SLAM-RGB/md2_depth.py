import torch
import cv2
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "md2", "monodepth2"))

from networks import ResnetEncoder, DepthDecoder

class MD2Depth:
    def __init__(self, model_path, device="cuda"):
        self.device = device

        self.encoder = ResnetEncoder(18, False)
        self.depth_decoder = DepthDecoder(self.encoder.num_ch_enc)

        self.encoder.load_state_dict(
            torch.load(f"{model_path}/encoder.pth", map_location=device), strict=False)
        self.depth_decoder.load_state_dict(
            torch.load(f"{model_path}/depth.pth", map_location=device), strict=False)

        self.encoder.to(device).eval()
        self.depth_decoder.to(device).eval()

    def infer(self, bgr_image):
        # MD2 expects RGB, 640x192
        rgb = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        rgb = cv2.resize(rgb, (640, 192))
        rgb = torch.from_numpy(rgb).float() / 255.0
        rgb = rgb.permute(2, 0, 1).unsqueeze(0).to(self.device)

        with torch.no_grad():
            features = self.encoder(rgb)
            outputs = self.depth_decoder(features)
            disp = outputs[("disp", 0)]

        # disparity → depth (relative)
        depth = 1.0 / (disp + 1e-6)
        depth = depth.squeeze().cpu().numpy()

        return depth
