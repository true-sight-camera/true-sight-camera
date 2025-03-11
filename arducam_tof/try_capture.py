import cv2
import numpy as np
import ArducamDepthCamera as ac

def resize_with_padding(image, target_width, target_height):
    h, w = image.shape[:2]
    scale = min(target_width / w, target_height / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    pad_x = (target_width - new_w) // 2
    pad_y = (target_height - new_h) // 2
    
    padded = cv2.copyMakeBorder(resized, pad_y, pad_y, pad_x, pad_x, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    return padded

def normalize_depth(depth_buf):
    depth_min = np.min(depth_buf)
    depth_max = np.max(depth_buf)
    if depth_max > depth_min:  # Avoid division by zero
        normalized = (depth_buf - depth_min) / (depth_max - depth_min) * 255.0
    else:
        normalized = np.zeros_like(depth_buf)  # If all values are the same
    return normalized.astype(np.uint8)

def main():
    print("Arducam Depth Camera Depth Map Capture.")
    print("  SDK version:", ac.__version__)

    cam = ac.ArducamCamera()
    ret = cam.open(ac.Connection.CSI, 0)
    if ret != 0:
        print("Failed to open camera. Error code:", ret)
        return

    ret = cam.start(ac.FrameType.DEPTH)
    if ret != 0:
        print("Failed to start camera. Error code:", ret)
        cam.close()
        return

    info = cam.getCameraInfo()
    print(f"Camera resolution: {info.width}x{info.height}")

    frame = cam.requestFrame(2000)
    if frame is not None and isinstance(frame, ac.DepthData):
        depth_buf = frame.depth_data
        depth_map = normalize_depth(depth_buf)
        print(depth_map[1][1])
        
        # Resize depth map while preserving aspect ratio with padding
        target_resolution = (1280, 800)
        padded_depth_map = resize_with_padding(depth_map, *target_resolution)
        print(padded_depth_map[1][1])
        
        # Apply color map after resizing
        color_depth_map = cv2.applyColorMap(padded_depth_map, cv2.COLORMAP_RAINBOW)
        
        filename = "depth_map.png"
        cv2.imwrite(filename, color_depth_map)
        print(f"Depth map saved as {filename} with resolution {target_resolution}")
        
        cam.releaseFrame(frame)
    
    cam.stop()
    cam.close()

if __name__ == "__main__":
    main()
