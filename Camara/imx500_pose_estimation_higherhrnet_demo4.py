import argparse
import sys
import time

import numpy as np
from libcamera import Transform
from picamera2 import CompletedRequest, MappedArray, Picamera2
from picamera2.devices.imx500 import IMX500, NetworkIntrinsics
from picamera2.devices.imx500.postprocess import COCODrawer
import picamera2.devices.imx500.postprocess as pp
print(pp.__file__)

from picamera2.devices.imx500.postprocess_highernet import \
    postprocess_higherhrnet

last_boxes = None
last_scores = None
last_keypoints = None
WINDOW_SIZE_H_W = (480, 640)


def ai_output_tensor_parse(metadata: dict):
    """Parse the output tensor into a number of detected objects, scaled to the ISP output."""
    global last_boxes, last_scores, last_keypoints
    np_outputs = imx500.get_outputs(metadata=metadata, add_batch=True)
    if np_outputs is not None:
        keypoints, scores, boxes = postprocess_higherhrnet(outputs=np_outputs,
                                                           img_size=WINDOW_SIZE_H_W,
                                                           img_w_pad=(0, 0),
                                                           img_h_pad=(0, 0),
                                                           detection_threshold=args.detection_threshold,
                                                           network_postprocess=True)

        if scores is not None and len(scores) > 0:
            last_keypoints = np.reshape(np.stack(keypoints, axis=0), (len(scores), 17, 3))
            last_boxes = [np.array(b) for b in boxes]
            last_scores = np.array(scores)
    return last_boxes, last_scores, last_keypoints


def ai_output_tensor_draw(request: CompletedRequest, boxes, scores, keypoints, stream='main'):
    """Draw the detections for this request onto the ISP output."""
    with MappedArray(request, stream) as m:
        if boxes is not None and len(boxes) > 0:
            drawer.annotate_image(m.array, boxes, scores,
                                  np.zeros(scores.shape), keypoints, args.detection_threshold,
                                  args.detection_threshold, request.get_metadata(), picam2, stream)

            for person in keypoints:
                # Verificamos puntos clave
                shoulder = person[5]
                elbow = person[7]
                wrist = person[9]

                if (shoulder[2] > args.detection_threshold and
                    elbow[2] > args.detection_threshold and
                    wrist[2] > args.detection_threshold):

                    # Vectores desde el codo
                    vec1 = np.array([shoulder[0] - elbow[0], shoulder[1] - elbow[1]])
                    vec2 = np.array([wrist[0] - elbow[0], wrist[1] - elbow[1]])

                    # Producto punto y c�lculo de �ngulo
                    unit_vec1 = vec1 / np.linalg.norm(vec1)
                    unit_vec2 = vec2 / np.linalg.norm(vec2)
                    dot_product = np.dot(unit_vec1, unit_vec2)
                    angle_rad = np.arccos(np.clip(dot_product, -1.0, 1.0))
                    angle_deg = np.degrees(angle_rad)

                    # Determinamos color por ángulo (con tolerancia)
                    if 170 <= angle_deg <= 190:
                        color = (0, 0, 255, 255)  # Azul
                    elif 80 <= angle_deg <= 100:
                        color = (0, 255, 0, 255)  # Verde
                    elif 260 <= angle_deg <= 280:
                        color = (255, 165, 0, 255)  # Naranja
                    elif angle_deg <= 10 or angle_deg >= 350:
                        color = (255, 0, 0, 255)  # Rojo
                    else:
                        color = (128, 128, 128, 255)  # Gris si no coincide con ninguno

                    # Dibujar cuadro indicador
                    m.array[10:60, 10:60] = color


def picamera2_pre_callback(request: CompletedRequest):
    """Analyse the detected objects in the output tensor and draw them on the main output image."""
    boxes, scores, keypoints = ai_output_tensor_parse(request.get_metadata())
    ai_output_tensor_draw(request, boxes, scores, keypoints)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, help="Path of the model",
                        default="/usr/share/imx500-models/imx500_network_higherhrnet_coco.rpk")
    parser.add_argument("--fps", type=int, help="Frames per second")
    parser.add_argument("--detection-threshold", type=float, default=0.2,
                        help="Post-process detection threshold")
    parser.add_argument("--labels", type=str,
                        help="Path to the labels file")
    parser.add_argument("--print-intrinsics", action="store_true",
                        help="Print JSON network_intrinsics then exit")
    return parser.parse_args()


def get_drawer():
    categories = intrinsics.labels
    categories = [c for c in categories if c and c != "-"]
    return COCODrawer(categories, imx500, needs_rescale_coords=False)


if __name__ == "__main__":
    args = get_args()

    # This must be called before instantiation of Picamera2
    imx500 = IMX500(args.model)
    intrinsics = imx500.network_intrinsics
    if not intrinsics:
        intrinsics = NetworkIntrinsics()
        intrinsics.task = "pose estimation"
    elif intrinsics.task != "pose estimation":
        print("Network is not a pose estimation task", file=sys.stderr)
        exit()

    # Override intrinsics from args
    for key, value in vars(args).items():
        if key == 'labels' and value is not None:
            with open(value, 'r') as f:
                intrinsics.labels = f.read().splitlines()
        elif hasattr(intrinsics, key) and value is not None:
            setattr(intrinsics, key, value)

    # Defaults
    if intrinsics.inference_rate is None:
        intrinsics.inference_rate = 10
    if intrinsics.labels is None:
        with open("assets/coco_labels.txt", "r") as f:
            intrinsics.labels = f.read().splitlines()
    intrinsics.update_with_defaults()

    if args.print_intrinsics:
        print(intrinsics)
        exit()

    drawer = get_drawer()

    picam2 = Picamera2(imx500.camera_num)
    config = picam2.create_preview_configuration(controls={'FrameRate': intrinsics.inference_rate}, buffer_count=12, transform=Transform(hflip=True, vflip=False))

    imx500.show_network_fw_progress_bar()
    picam2.start(config, show_preview=True)
    imx500.set_auto_aspect_ratio()
    picam2.pre_callback = picamera2_pre_callback

    while True:
        time.sleep(0.5)
