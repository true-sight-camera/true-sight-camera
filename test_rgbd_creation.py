from PIL import Image
import numpy as np
# import open3d as o3d

# Step 1: Convert PNG to RGBA with Depth Value
def png_to_rgba_with_depth(png_path, depth_value, output_path):
    # Load the PNG image
    image = Image.open(png_path).convert("RGBA")
    data = np.array(image)

    # Replace alpha channel with the hardcoded depth value
    data[..., 3] = random.randint(0, 255)  # Depth value should be an integer (0-255)

    # Save the modified RGBA image
    rgba_image = Image.fromarray(data, "RGBA")
    rgba_image.save(output_path)
    print(f"RGBA image with depth saved to {output_path}")
    return output_path

# # Step 2: Generate Point Cloud from Depth
# def generate_point_cloud_from_rgba(rgba_path):
#     # Load the image as depth data
#     depth_image = o3d.io.read_image(rgba_path)

#     # Convert image to depth array
#     depth_array = np.array(depth_image)

#     # Generate point cloud using the depth values
#     height, width = depth_array.shape[:2]
#     fx = fy = width  # Focal lengths (assumed equal to image width for simplicity)
#     cx = width / 2.0  # Principal point in x (image center)
#     cy = height / 2.0  # Principal point in y (image center)

#     # Create an Open3D image object for depth
#     depth_o3d = o3d.geometry.Image(depth_array)

#     # Create a camera intrinsic matrix
#     intrinsic = o3d.camera.PinholeCameraIntrinsic(width, height, fx, fy, cx, cy)

#     # Generate the point cloud
#     pcd = o3d.geometry.PointCloud.create_from_depth_image(depth_o3d, intrinsic)

#     # Visualize point cloud
#     o3d.visualization.draw_geometries([pcd])
#     return pcd

# Example usage
png_path = "camera_0.png"  # Replace with your input PNG file
output_path = "output_rgba.png"
depth_value = 200  # Replace with your desired depth value (0-255)

rgba_path = png_to_rgba_with_depth(png_path, depth_value, output_path)
# point_cloud = generate_point_cloud_from_rgba(rgba_path)
