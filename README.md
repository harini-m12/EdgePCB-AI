EdgePCB-AI

Intelligent Edge-Based PCB Defect Detection, Severity Assessment and Repairability Analysis with AI-Assisted Inspection

1. Introduction

EdgePCB-AI is a smart edge-based Printed Circuit Board (PCB) inspection solution designed to automatically detect PCB defects, assess their severity and analyse their potential repairability using computer vision and edge computing technologies.

The system acquires PCB images through a USB camera and analyses them using a YOLO ONNX model running on the ARM processor of the PYNQ-Z2 board. Non-Maximum Suppression (NMS) is applied to detection results, followed by defect classification, severity assessment and repairability analysis. Inspection results are visualised through an HDMI display.

A Raspberry Pi 4 is proposed as a secondary edge device for processing inspection data and providing AI-assisted inspection guidance using a quantised Llama model with ExecuTorch. The proposed secondary device will also manage inspection records and provide a local dashboard.

The PYNQ-Z2 and Raspberry Pi 4 are designed to communicate through UART. Only compact inspection data is transferred between the boards; camera images and video are not transmitted. The proposed architecture does not require internet connectivity or Ethernet communication between the boards.

2. Background

Printed Circuit Boards (PCBs) are fundamental components of electronic systems. Defects introduced during manufacturing can affect electrical performance, reliability and product quality.

PCB inspection may involve manual examination, specialised inspection equipment or additional processing facilities. Manual inspection can be time-consuming and dependent on individual expertise.

An efficient, low-cost and self-contained edge-based inspection system is therefore required to automatically detect PCB defects, assess their severity, analyse potential repairability and provide AI-assisted inspection guidance.

3. Proposed Solution

EdgePCB-AI proposes a dual-board edge intelligence architecture for automated PCB quality inspection.

The PYNQ-Z2 acts as the primary inspection device. It acquires images using a USB camera, performs YOLO ONNX inference on the ARM processor, applies Non-Maximum Suppression and analyses detected defects according to predefined severity and repairability rules.

Inspection results are displayed through HDMI and transmitted to the Raspberry Pi 4 through UART.

The Raspberry Pi 4 is planned as the secondary edge device for inspection-data processing, AI-assisted guidance using quantised Llama and ExecuTorch, local data management and dashboard functionality.

Only compact inspection data is exchanged between the devices.

4. Objectives

Automatically inspect PCBs for defects.

Implement YOLO ONNX inference on the PYNQ-Z2 ARM processor.

Identify PCB defects.

Classify PCB defects according to severity.

Analyse potential repairability.

Display inspection results through HDMI.

Transfer inspection data through UART.

Provide AI-assisted inspection guidance using a quantised Llama model.

Manage inspection records using SQLite.

Enable local dashboard functionality.

5. System Architecture

PYNQ-Z2 — Primary Edge Device

The PYNQ-Z2 performs the primary PCB inspection and edge processing.

Processing Pipeline:

USB Camera → OpenCV Preprocessing → YOLO ONNX Runtime CPU → Non-Maximum Suppression → Defect Identification → Severity Assessment → Repairability Analysis → HDMI Display → UART Transmission

Functions:

USB camera image acquisition.

Image preprocessing and resizing.

YOLO ONNX inference using ARM CPU.

Bounding-box generation.

Confidence score extraction.

Non-Maximum Suppression.

Defect identification.

Severity classification.

Repairability analysis.

HDMI inspection visualisation.

UART inspection-data transmission.

Raspberry Pi 4 — Secondary Edge Device (Planned)

The Raspberry Pi 4 is proposed to perform inspection-data processing and AI-assisted inspection support.

Processing Pipeline:

UART Receiver → Data Validation → ExecuTorch Llama Inference → Operator Guidance → SQLite Database → Local Dashboard

Functions:

Receive inspection data.

Validate inspection messages.

Generate AI-assisted inspection guidance.

Manage inspection records.

Maintain inspection history.

Provide local dashboard functionality.

6. Hardware Requirements

Hardware

Function

PYNQ-Z2

PCB inspection and edge processing

USB Camera

PCB image acquisition

HDMI Display

Inspection-result visualisation

Raspberry Pi 4

Planned AI guidance and inspection-data management

UART Interface

Serial communication between boards

PCB Samples

Inspection and testing

7. Software and Technologies

Technology

Application

Python

System development

OpenCV

Image acquisition and preprocessing

YOLO

PCB defect detection

ONNX

Model representation

ONNX Runtime

CPU-based model inference

NumPy

Image and numerical processing

PYNQ

Embedded FPGA board platform

PySerial

UART communication

SQLite

Inspection-data management

Flask

Local dashboard

ExecuTorch

Planned LLM inference runtime

Quantised Llama

Planned AI-assisted inspection guidance

8. PCB Defect Identification

The system supports the identification of the following PCB defect categories:

Defect

Description

Mouse Bite

Irregular PCB edge damage

Spur

Unwanted copper protrusion

Missing Hole

Missing drilled hole

Short

Unintended electrical connection

Open Circuit

Interrupted electrical connection

Spurious Copper

Unwanted copper region

The YOLO ONNX model detects defects and generates bounding boxes and confidence scores for the detected regions.

9. Severity Assessment

Severity values are assigned to detected PCB defects using predefined rule-based classification.

Defect

Example Severity

Mouse Bite

MEDIUM

Spur

LOW

Missing Hole

HIGH

Short

CRITICAL

Open Circuit

CRITICAL

Spurious Copper

MEDIUM

The overall inspection severity is determined using the highest assigned severity among the detected defects.

These are project-defined example rules and require validation against relevant PCB manufacturing and quality criteria.

10. Repairability Analysis

The system provides preliminary repairability classification using predefined rules.

Defect

Example Repairability

Mouse Bite

REWORKABLE

Spur

REWORKABLE

Spurious Copper

REWORKABLE

Missing Hole

NON-REWORKABLE

Short

NON-REWORKABLE

Open Circuit

NON-REWORKABLE

Repairability classification is intended to support inspection decisions. Actual repair and product acceptance decisions must be verified by qualified personnel in accordance with manufacturing criteria and board-specific requirements.

11. Edge AI Processing

The PYNQ-Z2 ARM processor runs YOLO ONNX inference using ONNX Runtime to perform local PCB inspection.

Processing Steps

Acquire images using the USB camera.

Preprocess and resize images.

Execute YOLO ONNX inference.

Extract defect bounding boxes and confidence values.

Apply Non-Maximum Suppression.

Identify detected defect categories.

Classify defects according to severity.

Analyse potential repairability.

Display inspection results through HDMI.

Transfer compact inspection data through UART.

High-resolution image or video transfer between the boards is not required.

12. UART Communication

UART is used to transfer compact PCB inspection data from the PYNQ-Z2 to the Raspberry Pi 4.

Parameter

Configuration

Interface

UART

Baud Rate

115200

Data Format

JSON

Message Termination

Newline

Communication

Serial

Image Transfer

Not used

Example Inspection Message

{
  "id": 12,
  "status": "DEFECT DETECTED",
  "severity": "CRITICAL",
  "count": 2,
  "defects": [
    {
      "name": "short",
      "conf": 0.9682,
      "severity": "CRITICAL",
      "repairability": "NON-REWORKABLE"
    },
    {
      "name": "spur",
      "conf": 0.8954,
      "severity": "LOW",
      "repairability": "REWORKABLE"
    }
  ]
}

Only compact inspection information is transferred. Camera images and video frames are not transmitted through UART.

13. AI-Assisted Inspection (Planned)

A quantised Llama model is proposed for deployment on the Raspberry Pi 4 using ExecuTorch.

The model is intended to analyse structured inspection data containing defect types, severity classifications, confidence values and repairability information.

Planned AI Functions

Explain detected PCB defects.

Generate inspection summaries.

Suggest inspection and verification procedures.

Provide preliminary repair guidance.

Assist operators in understanding inspection results.

AI-assisted guidance is intended to support decision-making and is not a standalone product acceptance tool.

14. Model Deployment Status

Raspberry Pi 4 model deployment is planned for future hardware development.

Component

Status

YOLO ONNX Model

Prepared for PYNQ deployment

ONNX Runtime

Implemented in detector pipeline

Severity Assessment

Rule-based implementation

Repairability Analysis

Rule-based implementation

UART Communication

Code provided; hardware testing pending

Raspberry Pi 4

Planned hardware

ExecuTorch

Planned deployment

Quantised Llama

Planned deployment

Tokenizer

Planned deployment

SQLite Database

Raspberry Pi software component

Local Dashboard

Raspberry Pi software component

The model-related files currently provided are documentation placeholders and are not deployable neural-network model artifacts.

15. Project Structure

EdgePCB-AI/
│
├── README.md
│
├── pynq_board/
│   ├── pcb_detector.py
│   ├── severity_engine.py
│   ├── serial_communication.py
│   ├── config.json
│   └── best1.onnx
│
└── raspberry_pi/
    ├── serial_receiver.py
    ├── llm_service.py
    ├── database.py
    ├── dashboard.py
    ├── config.json
    ├── requirements.txt
    │
    ├── models/
    │   ├── model.pte
    │   └── tokenizer.model
    │
    └── templates/
        └── index.html

16. Installation and Operation

PYNQ-Z2

Install or verify compatible packages:

pip install numpy opencv-python pyserial onnxruntime

Run the PCB inspection program:

cd pynq_board
python3 pcb_detector.py

The system will access the USB camera, process images, detect PCB defects, assess severity and repairability, display inspection results through HDMI and transmit compact inspection messages through UART.

Raspberry Pi 4 (Planned Deployment)

Install the required software:

sudo apt update
sudo apt install python3-venv python3-pip

Create a Python virtual environment:

cd raspberry_pi

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

UART configuration, ExecuTorch runtime installation and model deployment will be required when the Raspberry Pi 4 becomes available.

17. Expected Outputs

PCB with Defects

The inspection system is expected to display:

Inspection status.

Defect types.

Bounding boxes.

Confidence values.

Defect count.

Severity classification.

Repairability classification.

Processing latency.

PCB without Detected Defects

Status: NO DEFECT

Severity: NONE

Defect count: 0

A no-detection result does not guarantee that the PCB is defect-free.

AI-Assisted Inspection Guidance (Planned)

The Raspberry Pi 4 is planned to provide:

Inspection summaries.

Defect explanations.

Verification recommendations.

Preliminary repair guidance.

Quality-control assistance.

18. Benefits

Edge-based PCB inspection.

Self-contained inspection architecture.

No internet dependency during inspection.

No Ethernet communication between boards.

CPU-based ONNX inference on the PYNQ-Z2 ARM processor.

Compact UART data transmission.

HDMI inspection visualisation.

Severity assessment.

Repairability analysis.

Future AI-assisted inspection guidance.

Local inspection-data management.

Dual-board edge intelligence architecture.

19. Limitations

Defect detection performance depends on the training and validation datasets.

Model confidence does not necessarily represent actual detection accuracy.

Severity rules require validation.

Repairability classifications are preliminary.

Raspberry Pi 4 hardware is not yet available.

ExecuTorch model compatibility and resource utilisation require investigation.

AI-assisted guidance must be verified by engineering personnel.

UART communication must be validated on the actual hardware.

20. Future Development

Deploy a quantised Llama model using ExecuTorch.

Implement AI-assisted inspection guidance.

Develop a local inspection dashboard.

Improve PCB defect detection using expanded datasets.

Validate severity rules against manufacturing criteria.

Optimise edge inference latency.

Implement inspection analytics.

Develop automated inspection reports.

Investigate resource utilisation across both boards.

21. Conclusion

EdgePCB-AI proposes a self-contained edge intelligence system for automated PCB defect detection, severity assessment and repairability analysis.

The PYNQ-Z2 performs visual inspection using a USB camera and YOLO ONNX Runtime on the ARM processor. Detected defects are evaluated using predefined severity and repairability rules, and inspection results are visualised through HDMI.

A Raspberry Pi 4 is proposed as a secondary edge device for AI-assisted inspection guidance using a quantised Llama model and ExecuTorch, inspection-data management and local dashboard functionality.

Together, the PYNQ-Z2 and Raspberry Pi 4 are intended to form a modular edge intelligence system combining embedded computer vision, edge processing and AI-assisted inspection for PCB quality-control applications.

Project Information

Parameter

Description

Project Name

EdgePCB-AI

Project Title

Intelligent Edge-Based PCB Defect Detection, Severity Assessment and Repairability Analysis with AI-Assisted Inspection

Primary Edge Device

PYNQ-Z2

Secondary Edge Device

Raspberry Pi 4 (Planned)

Communication

UART

Detection Runtime

ONNX Runtime

Future AI Runtime

ExecuTorch

Application

Automated PCB Quality Inspection
