import sys
import os
import torch
import cv2
import numpy as np
from src.config import load_config
from src.utils.datasets import get_dataset

# Add current directory to sys.path to ensure local imports work
sys.path.append(os.getcwd())

class Args:
    def __init__(self):
        self.input_folder = None

def test():
    # Load config
    # We use validation scene
    print("Loading config...")
    cfg = load_config("configs/Replica/validation.yaml", "configs/point_slam.yaml")
    
    # Enable MD2 - COMMENTED OUT TO TEST AUTO-DETECTION
    # cfg['use_md2'] = True
    print(f"Config loaded. use_md2: {cfg.get('use_md2')}")
    
    # Args
    args = Args()
    
    # Get dataset
    print("Loading dataset...")
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")
    
    try:
        dataset = get_dataset(cfg, args, device=device)
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        import traceback
        traceback.print_exc()
        return

    print(f"Dataset loaded. Size: {len(dataset)}")
    
    if len(dataset) == 0:
        print("Dataset is empty!")
        return

    # Check first item
    print("Fetching item 0...")
    # __getitem__ returns: index, color_data, depth_data, pose
    try:
        idx, color, depth, pose = dataset[0]
    except Exception as e:
        print(f"Failed to fetch item 0: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("Item fetched.")
    print(f"Color shape: {color.shape}")
    print(f"Depth shape: {depth.shape}")
    print(f"Pose shape: {pose.shape}")
    
    # Check if depth values are valid
    depth_cpu = depth.detach().cpu().numpy()
    if np.all(depth_cpu == 0):
        print("FAIL: Depth is all zeros!")
    else:
        print(f"Pass: Depth contains values. Min: {depth_cpu.min()}, Max: {depth_cpu.max()}, Mean: {depth_cpu.mean()}")
        
    # Check resolution match
    # Color usually [C, H, W] if simple, but datasets.py lines 109 impl:
    # color_data = color_data.permute(2, 0, 1) -> [3, H, W]
    # depth_data = depth_data[None, None]... -> [1, 1, H, W] or similar if interpolation
    # dataset.py: 
    #   depth_data = F.interpolate(depth_data[None, None], self.crop_size...)[0, 0]
    # So depth is [H, W]
    
    c_shape = color.shape
    d_shape = depth.shape
    
    is_match = False
    # If color is [3, H, W] and depth is [H, W]
    if len(c_shape) == 3 and len(d_shape) == 2:
        if c_shape[1] == d_shape[0] and c_shape[2] == d_shape[1]:
            is_match = True
    
    if is_match:
        print("Pass: Spatial dimensions match (Color [3, H, W], Depth [H, W]).")
    else:
        print(f"WARNING: Dimensions mismatch or unexpected format. C: {c_shape}, D: {d_shape}")

if __name__ == "__main__":
    test()
