from PIL import Image
import numpy as np
import cv2
import random
import numpy as np
import open3d as o3d

def png_to_rgba_with_depth(png_path, output_path):
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

# Step 1: Convert RGBA to Grayscale Depth Map
def convert_rgba_to_depth(rgba_path, output_path, depth_value=200):
    # Read the RGBA image
    rgba_image = cv2.imread(rgba_path, cv2.IMREAD_UNCHANGED)  # Load as RGBA

    # Validate if the image has an alpha channel
    if rgba_image is None or rgba_image.shape[2] != 4:
        raise ValueError("Input image is not an RGBA image.")

    # Convert RGBA to grayscale (use R channel or average RGB channels)
    depth_map = cv2.cvtColor(rgba_image, cv2.COLOR_RGBA2GRAY)

    # Scale depth values to the range needed for Open3D
    depth_map = (depth_map.astype(np.float32) / 255.0) * depth_value

    # Save as a depth-compatible format (16-bit PNG)
    cv2.imwrite(output_path, depth_map.astype(np.uint16))
    return output_path

# Step 2: Generate Point Cloud from Depth Map
def generate_point_cloud_from_depth(depth_path):
    # Load the depth image
    depth_image = o3d.io.read_image(depth_path)

    # Convert the Open3D image to a NumPy array to get dimensions
    depth_array = np.asarray(depth_image)
    height, width = depth_array.shape

    # Create an Open3D depth image object
    depth_o3d = o3d.geometry.Image(depth_array)

    # Intrinsic parameters (modify if known for your camera)
    fx = fy = width  # Assumes square pixels
    cx = width / 2.0
    cy = height / 2.0
    intrinsic = o3d.camera.PinholeCameraIntrinsic(width, height, fx, fy, cx, cy)

    # Generate point cloud
    pcd = o3d.geometry.PointCloud.create_from_depth_image(
        depth_o3d, intrinsic, depth_scale=1.0, depth_trunc=1000.0, stride=1
    )

    # Visualize point cloud
    o3d.visualization.draw_geometries([pcd])
    return pcd


# Main Function
if __name__ == "__main__":
    img_path = "camera_0.png"

    # Input RGBA image path
    rgba_path = "output_rgba.png"  # Replace with your RGBA image path

    # Output depth map path
    depth_path = "depth_image.png"

    rgba_path = png_to_rgba_with_depth(img_path, rgba_path)

    # Convert RGBA image to depth map
    depth_value = 200  # Adjust as needed
    converted_depth_path = convert_rgba_to_depth(rgba_path, depth_path, depth_value)

    # Generate point cloud from depth map
    point_cloud = generate_point_cloud_from_depth(converted_depth_path)
