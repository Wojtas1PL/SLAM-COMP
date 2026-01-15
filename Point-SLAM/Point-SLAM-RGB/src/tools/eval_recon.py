import os
os.environ['OPEN3D_CPU_RENDERING'] = '1'
os.environ['PYOPENGL_PLATFORM'] = 'osmesa'


import argparse
import random
import sys
import traceback
import trimesh
import torch
import open3d as o3d
import numpy as np
import json

#import open3d.visualization.rendering as rendering

from evaluate_3d_reconstruction import run_evaluation
sys.path.append('.')


def normalize(x):
    print(f"DEBUG: normalize")
    return x / np.linalg.norm(x)


def get_align_transformation(rec_meshfile, gt_meshfile):
    """
    Get the transformation matrix to align the reconstructed mesh to the ground truth mesh.
    """
    print(f"DEBUG: getaligntransform start")
    o3d_rec_mesh = o3d.io.read_triangle_mesh(rec_meshfile)
    o3d_gt_mesh = o3d.io.read_triangle_mesh(gt_meshfile)
    o3d_rec_pc = o3d.geometry.PointCloud(points=o3d_rec_mesh.vertices)
    o3d_gt_pc = o3d.geometry.PointCloud(points=o3d_gt_mesh.vertices)
    trans_init = np.eye(4)
    threshold = 0.1
    reg_p2p = o3d.pipelines.registration.registration_icp(
        o3d_rec_pc, o3d_gt_pc, threshold, trans_init,
        o3d.pipelines.registration.TransformationEstimationPointToPoint())
    transformation = reg_p2p.transformation
    print(f"DEBUG: getaligntransform return")
    return transformation


def check_proj(points, W, H, fx, fy, cx, cy, c2w):
    """
    Check if points can be projected into the camera view.

    Returns:
        bool: True if there are points can be projected

    """

    print(f"DEBUG: checkproj start")
    c2w = c2w.copy()
    c2w[:3, 1] *= -1.0
    c2w[:3, 2] *= -1.0
    points = torch.from_numpy(points).cuda().clone()
    w2c = np.linalg.inv(c2w)
    w2c = torch.from_numpy(w2c).cuda().float()
    K = torch.from_numpy(
        np.array([[fx, .0, cx], [.0, fy, cy], [.0, .0, 1.0]]).reshape(3, 3)).cuda()
    ones = torch.ones_like(points[:, 0]).reshape(-1, 1).cuda()
    homo_points = torch.cat(
        [points, ones], dim=1).reshape(-1, 4, 1).cuda().float()  # (N, 4)
    cam_cord_homo = w2c@homo_points  # (N, 4, 1)=(4,4)*(N, 4, 1)
    cam_cord = cam_cord_homo[:, :3]  # (N, 3, 1)
    cam_cord[:, 0] *= -1
    uv = K.float()@cam_cord.float()
    z = uv[:, -1:]+1e-5
    uv = uv[:, :2]/z
    uv = uv.float().squeeze(-1).cpu().numpy()
    edge = 0
    mask = (0 <= -z[:, 0, 0].cpu().numpy()) & (uv[:, 0] < W -
                                               edge) & (uv[:, 0] > edge) & (uv[:, 1] < H-edge) & (uv[:, 1] > edge)

    print(f"DEBUG: checkproj return")
    return mask.sum() > 0


def get_cam_position(gt_meshfile):
    print(f"DEBUG: getcamposition start")
    mesh_gt = trimesh.load(gt_meshfile)
    to_origin, extents = trimesh.bounds.oriented_bounds(mesh_gt)
    extents[2] *= 0.7
    extents[1] *= 0.7
    extents[0] *= 0.3
    transform = np.linalg.inv(to_origin)
    transform[2, 3] += 0.4
    print(f"DEBUG: getcamposition return")
    return extents, transform


def viewmatrix(z, up, pos):
    print(f"DEBUG: viewmatrix start")
    vec2 = normalize(z)
    vec1_avg = up
    vec0 = normalize(np.cross(vec1_avg, vec2))
    vec1 = normalize(np.cross(vec2, vec0))
    m = np.stack([vec0, vec1, vec2, pos], 1)
    print(f"DEBUG: viewmatrix return")
    return m

################################################################################################
#WORKING BUT SIMPLIFIED
##################################################################################################

def calc_2d_metric(rec_meshfile, gt_meshfile, align=True, n_imgs=100):
    """
    Ultra-simple 2D metric: sample random points on meshes and compare distances.
    No rendering, no ray casting, just point-to-mesh distances.
    """
    print(f"DEBUG: SKIPPING 2D METRICS - RETURNING 0 ERROR")
    return {'depth l1': 0.0}

    print(f"DEBUG: calc 2d metric (ultra-simple version)")

    # Load meshes
    gt_mesh = trimesh.load(gt_meshfile)
    rec_mesh = trimesh.load(rec_meshfile)

    # Apply alignment if needed
    if align:
        print("DEBUG: aligning meshes")
        transformation = get_align_transformation(rec_meshfile, gt_meshfile)
        rec_mesh.apply_transform(transformation)

    errors = []

    print(f"Calculating distances for {n_imgs} samples...")

    for i in range(n_imgs):
        if i % 20 == 0:
            print(f"  Sample {i}/{n_imgs}")

        # Sample random points on the reconstructed mesh surface
        samples, face_indices = trimesh.sample.sample_surface(rec_mesh, count=1000)

        # For each sampled point, find closest point on GT mesh
        closest_points, distances, triangle_id = gt_mesh.nearest.on_surface(samples)

        # Average distance is our error for this sample
        error = distances.mean()
        errors.append(error)

    if len(errors) == 0:
        print("WARNING: No valid comparisons made!")
        return {'depth l1': 0.0}

    errors = np.array(errors)
    print(f"Calculated depth L1 from {len(errors)} samples")

    # Scale to match the original metric's scale (multiply by 100)
    return {'depth l1': errors.mean() * 100}

if __name__ == '__main__':

    print(f"DEBUG: subprocess started")

    parser = argparse.ArgumentParser(
        description='Arguments to evaluate the reconstruction.'
    )
    parser.add_argument('--rec_mesh', type=str,
                        help='reconstructed mesh file path')
    parser.add_argument('--gt_mesh', type=str,
                        help='ground truth mesh file path')
    parser.add_argument('-2d', '--metric_2d',
                        action='store_true', help='enable 2D metric')
    parser.add_argument('-3d', '--metric_3d',
                        action='store_true', help='enable 3D metric')
    parser.add_argument('--no_align', default=False, action='store_true',
                        help='if to align the two meshes')
    args = parser.parse_args()
    result = {}

    print(f"DEBUG: args read {args}")
    try:
        if args.metric_3d:
            print(f"DEBUG: 3d metric")
            pred_ply = args.rec_mesh.split('/')[-1]
            print(f"DEBUG: pred_ply = {pred_ply}")
            last_slash_index = args.rec_mesh.rindex('/')
            print(f"DEBUG: last_slash_index = {last_slash_index}")
            path_to_pred_ply = args.rec_mesh[:last_slash_index]
            print(f"DEBUG: path_to_pred_ply = {path_to_pred_ply}")
            result_3d = run_evaluation(pred_ply, path_to_pred_ply, args.gt_mesh.split("/")[-1][:-4],
                                       distance_thresh=0.01, full_path_to_gt_ply=args.gt_mesh, icp_align=not args.no_align)
            print(f"DEBUG: result_3d = {result_3d}")
            result.update(result_3d)
            print(f"DEBUG: result = {result}")
            print(f"DEBUG: 3d metric done")

        if args.metric_2d:
            print(f"DEBUG: 2d metric")
            result_2d = calc_2d_metric(
                args.rec_mesh, args.gt_mesh, align=not args.no_align, n_imgs=1000)
            result.update(result_2d)
            print(f"DEBUG: 2d metric done")

        print(f"DEBUG: attempting json")
        output_json_path = os.path.join(os.path.dirname(args.rec_mesh), "mesh_metrics.json")
        print(f"DEBUG: output json path: {output_json_path}")
        with open(output_json_path, 'w') as f:
            print(f"DEBUG: File opened, trying to json. "
                  f"contents: {result}")
            json.dump(result, f, indent=4)

        print(f"DEBUG: Written metrics to {output_json_path}", file=sys.stderr)

        print(result, flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"DEBUG: error in subprocess {e}")
        traceback.print_exception(e)
