# Simulation util functions file #
import cv2
import numpy as np

def get_vertices_from_img(filename: str, scale: float):
    img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    alpha = img[:, :, 3]
    _, thresh = cv2.threshold(alpha, 1, 255, cv2.THRESH_BINARY) # black white mask
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    main_contour = max(contours, key=cv2.contourArea)

    epsilon = 0.01 * cv2.arcLength(main_contour, True)
    approx_poly = cv2.approxPolyDP(main_contour, epsilon, True)

    vertices = []
    height, width = alpha.shape
    for point in approx_poly:
        # Convert from image coordinates to centered physics coordinates
        x = (point[0][0] - (width / 2)) * scale
        y = ((height / 2) - point[0][1]) * scale # Flip Y because images are top-down
        vertices.append((x, y))
        
    return vertices

def apply_brownian_motion(env_objects, strength=25):
        """Applies brownian motion to objects in the environment."""
        if not env_objects: return

        jitter = np.random.normal(0, strength, (len(env_objects), 2))
        rotational_jitter = np.random.normal(0, strength*0.25, len(env_objects))

        for i, body in enumerate(env_objects):
            body.apply_force_at_world_point(tuple(jitter[i]), body.position)
            body.torque += rotational_jitter[i]
            