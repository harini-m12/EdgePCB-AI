
import cv2
import numpy as np
import onnxruntime as ort
import time
import json
import os

from pynq.overlays.base import BaseOverlay
from pynq.lib.video import VideoMode

from severity_engine import evaluate_defects
from serial_communication import initialize_serial, send_inspection, close_serial



MODEL_PATH = "best1.onnx"

CAMERA_ID = 0

IMG_SIZE = 416

CONF_THRESHOLD = 0.25

IOU_THRESHOLD = 0.45

INSPECTION_INTERVAL = 2.0

DISPLAY_WIDTH = 1280

DISPLAY_HEIGHT = 720

CLASS_NAMES = [
    "mouse_bite",
    "spur",
    "missing_hole",
    "short",
    "open_circuit",
    "spurious_copper"
]



print("[INFO] Loading YOLO ONNX model...")

session = ort.InferenceSession(
    MODEL_PATH,
    providers=["CPUExecutionProvider"]
)

input_name = session.get_inputs()[0].name

output_name = session.get_outputs()[0].name

print("[INFO] Model loaded.")

print("[INFO] Input shape:",
      session.get_inputs()[0].shape)

print("[INFO] Output shape:",
      session.get_outputs()[0].shape)



print("[INFO] Initializing HDMI...")

base = BaseOverlay("base.bit")

hdmi_out = base.video.hdmi_out

hdmi_out.configure(
    VideoMode(DISPLAY_WIDTH, DISPLAY_HEIGHT, 24)
)

hdmi_out.start()

print("[INFO] HDMI started.")



print("[INFO] Opening USB camera...")

cap = cv2.VideoCapture(CAMERA_ID)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, DISPLAY_WIDTH)

cap.set(cv2.CAP_PROP_FRAME_HEIGHT, DISPLAY_HEIGHT)

if not cap.isOpened():

    raise RuntimeError("USB camera cannot be opened")


print("[INFO] Camera opened.")



print("[INFO] Initializing UART...")

initialize_serial()

print("[INFO] UART initialized.")



def preprocess(frame):

    image = cv2.resize(
        frame,
        (IMG_SIZE, IMG_SIZE)
    )

    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    image = image.astype(np.float32) / 255.0

    image = np.transpose(
        image,
        (2, 0, 1)
    )

    image = np.expand_dims(
        image,
        axis=0
    )

    return image




def calculate_iou(box1, box2):

    x1 = max(box1[0], box2[0])

    y1 = max(box1[1], box2[1])

    x2 = min(box1[2], box2[2])

    y2 = min(box1[3], box2[3])

    intersection = max(0, x2 - x1) * max(0, y2 - y1)

    area1 = (
        max(0, box1[2] - box1[0]) *
        max(0, box1[3] - box1[1])
    )

    area2 = (
        max(0, box2[2] - box2[0]) *
        max(0, box2[3] - box2[1])
    )

    union = area1 + area2 - intersection

    if union <= 0:

        return 0.0

    return intersection / union

def nms(boxes, scores, classes):

    selected = []

    if len(boxes) == 0:

        return selected

    order = np.argsort(scores)[::-1]

    while len(order) > 0:

        current = order[0]

        selected.append(current)

        remaining = []

        for index in order[1:]:

            if classes[index] != classes[current]:

                remaining.append(index)

                continue

            iou = calculate_iou(
                boxes[current],
                boxes[index]
            )

            if iou < IOU_THRESHOLD:

                remaining.append(index)

        order = np.array(
            remaining,
            dtype=np.int64
        )

    return selected




def postprocess(prediction, original_width, original_height):

    boxes = []

    scores = []

    classes = []

    prediction = np.squeeze(prediction)

    if prediction.ndim != 2:

        return boxes, scores, classes

    # Convert [features, detections] into
    # [detections, features]

    if prediction.shape[0] < prediction.shape[1]:

        prediction = prediction.T

    num_classes = len(CLASS_NAMES)

    expected_features = 4 + num_classes

    if prediction.shape[1] != expected_features:

        raise ValueError(
            "Unexpected YOLO output shape: "
            + str(prediction.shape)
            + ". Expected "
            + str(expected_features)
            + " features per detection."
        )


    for row in prediction:

        box_values = row[:4]

        class_scores = row[4:]

        class_id = int(
            np.argmax(class_scores)
        )

        confidence = float(
            class_scores[class_id]
        )

        if confidence < CONF_THRESHOLD:

            continue

        cx, cy, w, h = box_values

        # Convert from 416x416 coordinates
        # to original image coordinates

        scale_x = original_width / IMG_SIZE

        scale_y = original_height / IMG_SIZE

        x1 = int((cx - w / 2) * scale_x)

        y1 = int((cy - h / 2) * scale_y)

        x2 = int((cx + w / 2) * scale_x)

        y2 = int((cy + h / 2) * scale_y)

        # Clip coordinates to image boundaries

        x1 = max(0, min(x1, original_width - 1))

        y1 = max(0, min(y1, original_height - 1))

        x2 = max(0, min(x2, original_width - 1))

        y2 = max(0, min(y2, original_height - 1))

        if x2 <= x1 or y2 <= y1:

            continue

        boxes.append([
            x1, y1, x2, y2
        ])

        scores.append(confidence)

        classes.append(class_id)

    # NMS

    selected = nms(
        boxes,
        scores,
        classes
    )

    boxes = [
        boxes[i] for i in selected
    ]

    scores = [
        scores[i] for i in selected
    ]

    classes = [
        classes[i] for i in selected
    ]

    return boxes, scores, classes

def draw_detections(frame, boxes, scores, classes):

    for box, score, cls in zip(
        boxes,
        scores,
        classes
    ):

        x1, y1, x2, y2 = box

        name = CLASS_NAMES[int(cls)]

        label = (
            name + " "
            + str(round(score * 100, 1))
            + "%"
        )

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            label,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    return frame

def draw_dashboard(
    frame,
    pcb_status,
    overall_severity,
    count,
    latency
):

    cv2.rectangle(
        frame,
        (0, 0),
        (frame.shape[1], 120),
        (30, 30, 30),
        -1
    )

    cv2.putText(
        frame,
        "EDGEPCB-AI INSPECTION",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "STATUS: " + pcb_status,
        (30, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        "SEVERITY: " + overall_severity,
        (30, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "DEFECT COUNT: " + str(count),
        (800, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "LATENCY: " + str(round(latency, 2)) + " ms",
        (800, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    return frame


last_inspection_time = 0

inspection_id = 0

print("[INFO] Starting PCB inspection...")

try:

    while True:

        ret, frame = cap.read()

        if not ret:

            print("[WARNING] Camera frame failed.")

            time.sleep(0.1)

            continue

        original_height, original_width = frame.shape[:2]

        start_time = time.time()
        input_tensor = preprocess(frame)

        prediction = session.run(
            [output_name],
            {input_name: input_tensor}
        )[0]

        boxes, scores, classes = postprocess(
            prediction,
            original_width,
            original_height
        )

        latency = (
            time.time() - start_time
        ) * 1000

        frame = draw_detections(
            frame,
            boxes,
            scores,
            classes
        )

        current_time = time.time()

        if (
            current_time - last_inspection_time
            >= INSPECTION_INTERVAL
        ):

            last_inspection_time = current_time

            inspection_id += 1

            raw_defects = []

            for cls, score in zip(classes, scores):

                defect_name = CLASS_NAMES[int(cls)]

                raw_defects.append({

                    "name": defect_name,

                    "confidence": float(score)

                })

            defects, overall_severity = evaluate_defects(
                raw_defects
            )

            if defects:

                pcb_status = "DEFECT DETECTED"

            else:

                pcb_status = "NO DEFECT"
            inspection_payload = {

                "id": inspection_id,

                "status": pcb_status,

                "severity": overall_severity,

                "count": len(defects),

                "defects": [

                    {

                        "name": item["name"],

                        "conf": round(
                            item["confidence"],
                            4
                        ),

                        "severity": item["severity"],

                        "repairability": item["repairability"]

                    }

                    for item in defects

                ]

            }

            try:

                send_inspection(
                    inspection_payload
                )

                print(
                    "[UART SENT]",
                    json.dumps(
                        inspection_payload
                    )
                )

            except Exception as e:

                print(
                    "[UART ERROR]",
                    str(e)
                )

            print(
                "[INSPECTION]",
                pcb_status,
                overall_severity,
                len(defects)
            )

        else:

            # Dashboard status uses the current
            # frame's detections even between sends.

            raw_defects = []

            for cls, score in zip(classes, scores):

                raw_defects.append({

                    "name": CLASS_NAMES[int(cls)],

                    "confidence": float(score)

                })

            defects, overall_severity = evaluate_defects(
                raw_defects
            )

            pcb_status = (
                "DEFECT DETECTED"
                if defects
                else "NO DEFECT"
            )
        frame = draw_dashboard(
            frame,
            pcb_status,
            overall_severity,
            len(defects),
            latency
        )

        frame = cv2.resize(
            frame,
            (DISPLAY_WIDTH, DISPLAY_HEIGHT)
        )

        # HDMI video output expects RGB

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )
        hdmi_out.writeframe(
            rgb_frame
        )

        time.sleep(0.01)


except KeyboardInterrupt:

    print("[INFO] Inspection stopped.")


finally:

    cap.release()

    close_serial()

    print("[INFO] Camera released.")

    print("[INFO] UART closed.")
