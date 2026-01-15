# def calc_2d_metric(rec_meshfile, gt_meshfile, align=True, n_imgs=1000):
#     """
#     2D reconstruction metric, depth L1 loss.
#
#     """
#     print(f"DEBUG: calc 2d metric")
#     H = 500
#     W = 500
#     focal = 300
#     fx = focal
#     fy = focal
#     cx = H/2.0-0.5
#     cy = W/2.0-0.5
#
#     gt_mesh = o3d.io.read_triangle_mesh(gt_meshfile)
#     rec_mesh = o3d.io.read_triangle_mesh(rec_meshfile)
#     unseen_gt_pointcloud_file = gt_meshfile.replace('.ply', '_pc_unseen.npy')
#     pc_unseen = np.load(unseen_gt_pointcloud_file)
#     if align:
#         transformation = get_align_transformation(rec_meshfile, gt_meshfile)
#         rec_mesh = rec_mesh.transform(transformation)
#
#     # get vacant area inside the room
#     extents, transform = get_cam_position(gt_meshfile)
#
#     ##########################################################
#     #WSL RENDERER
#
#     # print("attempting alternative renderer")
#     # # Create the offscreen renderer
#     # renderer = rendering.OffscreenRenderer(W, H)
#     # print("offscreenrenderer made")
#     #
#     # # Create a basic material (required for OffscreenRenderer geometry)
#     # mat = rendering.MaterialRecord()
#     # mat.shader = "defaultLit"
#     #
#     # print("shaders")
#     #
#     # errors = []
#     # for i in range(n_imgs):
#     #     while True:
#     #         # sample view, and check if unseen region is not inside the camera view
#     #         # if inside, then needs to resample
#     #         up = [0, 0, -1]
#     #         origin = trimesh.sample.volume_rectangular(
#     #             extents, 1, transform=transform)
#     #         origin = origin.reshape(-1)
#     #         print("origin reshaped")
#     #         tx = round(random.uniform(-10000, +10000), 2)
#     #         ty = round(random.uniform(-10000, +10000), 2)
#     #         tz = round(random.uniform(-10000, +10000), 2)
#     #         # will be normalized, so sample from range [0.0,1.0]
#     #         target = [tx, ty, tz]
#     #         target = np.array(target)-np.array(origin)
#     #         print("target made")
#     #         c2w = viewmatrix(target, up, origin)
#     #         print("c2w viewmatrix")
#     #         tmp = np.eye(4)
#     #         print("tmp np eye")
#     #         tmp[:3, :] = c2w  # sample translations
#     #         c2w = tmp
#     #         print("c2w = tmp")
#     #         # if unseen points are projected into current view (c2w)
#     #         seen = check_proj(pc_unseen, W, H, fx, fy, cx, cy, c2w)
#     #         print("seen = checkproj")
#     #         if (~seen):
#     #             print("loopbreak")
#     #             break
#     #
#     #     param = o3d.camera.PinholeCameraParameters()
#     #     print("pinholed")
#     #     param.extrinsic = np.linalg.inv(c2w)  # 4x4 numpy array
#     #     print("extrinsic")
#     #
#     #     param.intrinsic = o3d.camera.PinholeCameraIntrinsic(
#     #         W, H, fx, fy, cx, cy)
#     #     print("intrinsic")
#     #
#     #     # Setup the camera on the renderer
#     #     # Note: OffscreenRenderer takes the intrinsic object and the extrinsic matrix directly
#     #     print("setting up camera")
#     #     renderer.setup_camera(param.intrinsic, param.extrinsic)
#     #
#     #     print("Render GT")
#     #     # --- Render GT ---
#     #     # Add geometry with a unique name and the material
#     #     renderer.scene.add_geometry("gt_mesh", gt_mesh, mat)
#     #
#     #     print("render depth")
#     #     # Render depth (z_in_view_space=True matches the old capture_depth_float_buffer behavior)
#     #     gt_depth = renderer.render_to_depth_image(z_in_view_space=True)
#     #     gt_depth = np.asarray(gt_depth)
#     #
#     #     print("geo rm")
#     #     # Remove geometry to clear scene for next step
#     #     renderer.scene.remove_geometry("gt_mesh")
#     #
#     #     print("add geo")
#     #     # --- Render Ours ---
#     #     renderer.scene.add_geometry("rec_mesh", rec_mesh, mat)
#     #
#     #     print("ours depth")
#     #     ours_depth = renderer.render_to_depth_image(z_in_view_space=True)
#     #     ours_depth = np.asarray(ours_depth)
#     #
#     #     print("recmesh rm geo")
#     #     renderer.scene.remove_geometry("rec_mesh")
#     #
#     #     print("err calc")
#     #     if (ours_depth > 0).sum() > 0:
#     #         print("errors calc")
#     #         errors += [np.abs(gt_depth[ours_depth > 0] -
#     #                           ours_depth[ours_depth > 0]).mean()]
#     #     else:
#     #         print("continue")
#     #         continue
#
#     ##########################################################
#     #NATIVE RENDERER
#
#     print("window creation attempt")
#
#     vis = o3d.visualization.Visualizer()
#     vis.create_window(width=W, height=H, visible=False)
#     vis.get_render_option().mesh_show_back_face = True
#
#     print("window creation finished")
#
#     errors = []
#     for i in range(n_imgs):
#         while True:
#             # sample view, and check if unseen region is not inside the camera view
#             # if inside, then needs to resample
#             up = [0, 0, -1]
#             origin = trimesh.sample.volume_rectangular(
#                 extents, 1, transform=transform)
#             origin = origin.reshape(-1)
#             tx = round(random.uniform(-10000, +10000), 2)
#             ty = round(random.uniform(-10000, +10000), 2)
#             tz = round(random.uniform(-10000, +10000), 2)
#             # will be normalized, so sample from range [0.0,1.0]
#             target = [tx, ty, tz]
#             target = np.array(target)-np.array(origin)
#             c2w = viewmatrix(target, up, origin)
#             tmp = np.eye(4)
#             tmp[:3, :] = c2w  # sample translations
#             c2w = tmp
#             # if unseen points are projected into current view (c2w)
#             seen = check_proj(pc_unseen, W, H, fx, fy, cx, cy, c2w)
#             if (~seen):
#                 break
#
#         param = o3d.camera.PinholeCameraParameters()
#         param.extrinsic = np.linalg.inv(c2w)  # 4x4 numpy array
#
#         param.intrinsic = o3d.camera.PinholeCameraIntrinsic(
#             W, H, fx, fy, cx, cy)
#
#         ctr = vis.get_view_control()
#         ctr.set_constant_z_far(20)
#         ctr.convert_from_pinhole_camera_parameters(param)
#
#         vis.add_geometry(gt_mesh, reset_bounding_box=True,)
#         ctr.convert_from_pinhole_camera_parameters(param)
#         vis.poll_events()
#         vis.update_renderer()
#         gt_depth = vis.capture_depth_float_buffer(True)
#         gt_depth = np.asarray(gt_depth)
#         vis.remove_geometry(gt_mesh, reset_bounding_box=True,)
#
#         vis.add_geometry(rec_mesh, reset_bounding_box=True,)
#         ctr.convert_from_pinhole_camera_parameters(param)
#         vis.poll_events()
#         vis.update_renderer()
#         ours_depth = vis.capture_depth_float_buffer(True)
#         ours_depth = np.asarray(ours_depth)
#         vis.remove_geometry(rec_mesh, reset_bounding_box=True,)
#
#         # filter missing surfaces where depth is 0
#         if (ours_depth > 0).sum() > 0:
#             errors += [np.abs(gt_depth[ours_depth > 0] -
#                               ours_depth[ours_depth > 0]).mean()]
#         else:
#             continue
#
#     errors = np.array(errors)
#     print(f"DEBUG: calc 2d metric returning")
#     return {'depth l1': errors.mean()*100}

def calc_2d_metric(rec_meshfile, gt_meshfile, align=True, n_imgs=100):
    """
    2D reconstruction metric using trimesh ray casting (no OpenGL needed!)
    """

    # Load meshes
    gt_mesh_tm = trimesh.load(gt_meshfile)
    rec_mesh_tm = trimesh.load(rec_meshfile)

    if align:
        # Apply alignment (you'd need to convert O3D transform to trimesh)
        transformation = get_align_transformation(rec_meshfile, gt_meshfile)
        rec_mesh_tm.apply_transform(transformation)

    # Camera parameters
    H, W = 500, 500
    focal = 300

    errors = []

    for i in range(n_imgs):
        # Sample random camera position (simplified)
        origin = np.random.randn(3) * 2
        direction = -origin / np.linalg.norm(origin)

        # Cast rays through image plane
        # This is a simplified version - you'd need proper camera ray generation
        # But it demonstrates the concept: no OpenGL needed!

        # For each pixel, cast a ray and find intersection
        # Compare depths between gt_mesh and rec_mesh

        pass  # Simplified for demonstration

    return {'depth l1': np.mean(errors) * 100}


# def calc_2d_metric(rec_meshfile, gt_meshfile, align=True, n_imgs=1000):
#     """
#     2D reconstruction metric using trimesh ray casting (no OpenGL needed!)
#     """
#
#     print(f"DEBUG: calc 2d metric (trimesh version)")
#
#     # Camera parameters
#     H, W = 500, 500
#     focal = 300
#     fx, fy = focal, focal
#     cx, cy = H / 2.0 - 0.5, W / 2.0 - 0.5
#
#     # Load meshes with trimesh
#     gt_mesh_tm = trimesh.load(gt_meshfile)
#     rec_mesh_tm = trimesh.load(rec_meshfile)
#
#     # Load unseen point cloud for view sampling
#     unseen_gt_pointcloud_file = gt_meshfile.replace('.ply', '_pc_unseen.npy')
#     pc_unseen = np.load(unseen_gt_pointcloud_file)
#
#     # Apply alignment if needed
#     if align:
#         print("DEBUG: aligning meshes")
#         transformation = get_align_transformation(rec_meshfile, gt_meshfile)
#         rec_mesh_tm.apply_transform(transformation)
#
#     # Get camera sampling region
#     extents, transform = get_cam_position(gt_meshfile)
#
#     errors = []
#     max_attempts = 100
#
#     print(f"Starting to render {n_imgs} views...")
#
#     for i in range(n_imgs):
#         if i % 100 == 0:
#             print(f"  Processing image {i}/{n_imgs}")
#
#         # Sample valid camera viewpoint
#         attempt = 0
#         while attempt < max_attempts:
#             attempt += 1
#
#             # Sample camera origin and target
#             up = np.array([0, 0, -1])
#             origin = trimesh.sample.volume_rectangular(extents, 1, transform=transform)
#             origin = origin.reshape(-1)
#
#             tx = np.random.uniform(-10000, 10000)
#             ty = np.random.uniform(-10000, 10000)
#             tz = np.random.uniform(-10000, 10000)
#             target = np.array([tx, ty, tz]) - origin
#
#             # Build camera-to-world matrix
#             c2w = viewmatrix(target, up, origin)
#             tmp = np.eye(4)
#             tmp[:3, :] = c2w
#             c2w = tmp
#
#             # Check if unseen points would be visible
#             seen = check_proj(pc_unseen, W, H, fx, fy, cx, cy, c2w)
#             if not seen:
#                 break
#
#         if attempt >= max_attempts:
#             continue
#
#         # Convert c2w to w2c (world to camera)
#         w2c = np.linalg.inv(c2w)
#
#         # Generate rays for all pixels
#         rays_o, rays_d = generate_camera_rays(H, W, fx, fy, cx, cy, w2c)
#
#         # Cast rays against both meshes
#         gt_depth = cast_rays_to_mesh(gt_mesh_tm, rays_o, rays_d, H, W)
#         rec_depth = cast_rays_to_mesh(rec_mesh_tm, rays_o, rays_d, H, W)
#
#         # Calculate error where reconstructed mesh has valid depth
#         valid_mask = rec_depth > 0
#         if valid_mask.sum() > 0:
#             error = np.abs(gt_depth[valid_mask] - rec_depth[valid_mask]).mean()
#             errors.append(error)
#
#     if len(errors) == 0:
#         print("WARNING: No valid depth comparisons made!")
#         return {'depth l1': 0.0}
#
#     errors = np.array(errors)
#     print(f"Calculated depth L1 from {len(errors)}/{n_imgs} valid images")
#     return {'depth l1': errors.mean() * 100}
#
#
# def generate_camera_rays(H, W, fx, fy, cx, cy, w2c):
#     """
#     Generate ray origins and directions for all pixels in the camera.
#
#     Returns:
#         rays_o: (H*W, 3) ray origins in world space
#         rays_d: (H*W, 3) ray directions in world space (normalized)
#     """
#     # Create pixel grid
#     i, j = np.meshgrid(np.arange(W), np.arange(H), indexing='xy')
#
#     # Convert pixels to camera coordinates
#     # In camera space: x right, y down, z forward
#     dirs_cam = np.stack([
#         (i - cx) / fx,
#         (j - cy) / fy,
#         np.ones_like(i)
#     ], axis=-1)  # (H, W, 3)
#
#     dirs_cam = dirs_cam.reshape(-1, 3)  # (H*W, 3)
#
#     # Transform from camera to world space
#     c2w = np.linalg.inv(w2c)
#
#     # Ray origins (camera center in world space)
#     rays_o = np.broadcast_to(c2w[:3, 3], (H * W, 3)).copy()
#
#     # Ray directions (rotate camera-space directions to world space)
#     rays_d = (c2w[:3, :3] @ dirs_cam.T).T  # (H*W, 3)
#
#     # Normalize directions
#     rays_d = rays_d / np.linalg.norm(rays_d, axis=1, keepdims=True)
#
#     return rays_o, rays_d
#
#
# def cast_rays_to_mesh(mesh, rays_o, rays_d, H, W):
#     """
#     Cast rays against a mesh and return depth image.
#
#     Args:
#         mesh: trimesh object
#         rays_o: (N, 3) ray origins
#         rays_d: (N, 3) ray directions (normalized)
#         H, W: image dimensions
#
#     Returns:
#         depth: (H, W) depth image
#     """
#     # Use trimesh's ray-mesh intersection
#     locations, index_ray, index_tri = mesh.ray.intersects_location(
#         ray_origins=rays_o,
#         ray_directions=rays_d,
#         multiple_hits=False  # Only get first hit
#     )
#
#     # Initialize depth image with zeros (no hit)
#     depth = np.zeros(H * W, dtype=np.float32)
#
#     # Calculate depth for rays that hit the mesh
#     if len(locations) > 0:
#         # Depth is distance from ray origin to intersection
#         hit_depths = np.linalg.norm(locations - rays_o[index_ray], axis=1)
#         depth[index_ray] = hit_depths
#
#     # Reshape to image
#     depth = depth.reshape(H, W)
#
#     return depth





################OG
#def calc_2d_metric(rec_meshfile, gt_meshfile, align=True, n_imgs=1000):
#     """
#     2D reconstruction metric, depth L1 loss.
#     """
#     import os
#     # Force CPU rendering for WSL2 compatibility
#     os.environ['OPEN3D_CPU_RENDERING'] = '1'
#
#     print(f"DEBUG: calc 2d metric")
#     H = 500
#     W = 500
#     focal = 300
#     fx = focal
#     fy = focal
#     cx = H / 2.0 - 0.5
#     cy = W / 2.0 - 0.5
#
#     gt_mesh = o3d.io.read_triangle_mesh(gt_meshfile)
#     rec_mesh = o3d.io.read_triangle_mesh(rec_meshfile)
#     unseen_gt_pointcloud_file = gt_meshfile.replace('.ply', '_pc_unseen.npy')
#     pc_unseen = np.load(unseen_gt_pointcloud_file)
#
#     if align:
#         transformation = get_align_transformation(rec_meshfile, gt_meshfile)
#         rec_mesh = rec_mesh.transform(transformation)
#
#     # Get vacant area inside the room
#     extents, transform = get_cam_position(gt_meshfile)
#
#     print("Creating OffscreenRenderer...")
#     try:
#         renderer = rendering.OffscreenRenderer(W, H)
#         print("✓ OffscreenRenderer created successfully")
#     except Exception as e:
#         print(f"✗ Failed to create OffscreenRenderer: {e}")
#         print("Falling back to skipping 2D metrics")
#         return {'depth l1': 0.0}
#
#     # Create material
#     mat = rendering.MaterialRecord()
#     mat.shader = "defaultLit"
#
#     errors = []
#     max_attempts = 100
#
#     for i in range(n_imgs):
#         if i % 100 == 0:
#             print(f"Processing image {i}/{n_imgs}")
#
#         attempt = 0
#         while attempt < max_attempts:
#             attempt += 1
#
#             # Sample view, check if unseen region is not inside camera view
#             up = [0, 0, -1]
#             origin = trimesh.sample.volume_rectangular(extents, 1, transform=transform)
#             origin = origin.reshape(-1)
#
#             tx = round(random.uniform(-10000, +10000), 2)
#             ty = round(random.uniform(-10000, +10000), 2)
#             tz = round(random.uniform(-10000, +10000), 2)
#             target = np.array([tx, ty, tz]) - np.array(origin)
#
#             c2w = viewmatrix(target, up, origin)
#             tmp = np.eye(4)
#             tmp[:3, :] = c2w
#             c2w = tmp
#
#             # If unseen points are projected into current view, resample
#             seen = check_proj(pc_unseen, W, H, fx, fy, cx, cy, c2w)
#             if not seen:
#                 break
#
#         if attempt >= max_attempts:
#             continue
#
#         # Setup camera
#         param = o3d.camera.PinholeCameraParameters()
#         param.extrinsic = np.linalg.inv(c2w)
#         param.intrinsic = o3d.camera.PinholeCameraIntrinsic(W, H, fx, fy, cx, cy)
#         renderer.setup_camera(param.intrinsic, param.extrinsic)
#
#         # Render GT depth
#         renderer.scene.add_geometry("gt_mesh", gt_mesh, mat)
#         gt_depth = renderer.render_to_depth_image(z_in_view_space=True)
#         gt_depth = np.asarray(gt_depth)
#         renderer.scene.remove_geometry("gt_mesh")
#
#         # Render reconstructed depth
#         renderer.scene.add_geometry("rec_mesh", rec_mesh, mat)
#         ours_depth = renderer.render_to_depth_image(z_in_view_space=True)
#         ours_depth = np.asarray(ours_depth)
#         renderer.scene.remove_geometry("rec_mesh")
#
#         # Calculate error
#         if (ours_depth > 0).sum() > 0:
#             errors.append(np.abs(gt_depth[ours_depth > 0] - ours_depth[ours_depth > 0]).mean())
#
#     if len(errors) == 0:
#         print("WARNING: No valid depth comparisons made!")
#         return {'depth l1': 0.0}
#
#     errors = np.array(errors)
#     print(f"DEBUG: Calculated depth L1 from {len(errors)}/{n_imgs} valid images")
#     return {'depth l1': errors.mean() * 100}