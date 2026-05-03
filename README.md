# BB84 Quantum Key Distribution Simulator

## Overview

This project presents a complete simulation of the BB84 Quantum Key Distribution (QKD) protocol with realistic channel conditions and security analysis. The system is designed to help users understand how quantum cryptography works in practice, especially under the influence of noise and potential eavesdropping.

The simulator integrates quantum circuit modeling, noise simulation, classical post-processing, and machine learning-based eavesdropper detection into a single interactive web-based application.

---------------------------------------------------------------------------------------------------------------------------------------------

## Objectives

* Simulate the BB84 protocol using quantum circuits
* Analyze the effect of different noise models on key generation
* Compute Quantum Bit Error Rate (QBER) under realistic conditions
* Implement CASCADE error correction
* Apply privacy amplification using Toeplitz hashing
* Detect eavesdropping using a trained machine learning model
* Provide an easy-to-use web interface for experimentation

## Features

### Quantum Simulation

* Random quantum bit generation using Qiskit
* Encoding and decoding using BB84 protocol
* Basis selection and measurement simulation

### Noise Modeling

* Amplitude Damping (photon loss)
* Phase Damping (decoherence)
* Depolarizing Noise (random disturbances)
* Pauli Noise (bit-flip and phase-flip errors)
* Sequential combination of multiple noise types

### Performance Analysis

* Global QBER calculation
* Segment-wise QBER evaluation
* Matched basis filtering

### Security Mechanisms

* CASCADE error correction protocol
* Privacy amplification using Toeplitz matrices
* Secret key rate computation

### Machine Learning Integration

* Eavesdropper detection using trained model
* Distinguishes between noise and malicious interference

### Web Interface

* User input for key length, segment size, and noise parameters
* Real-time simulation results
* Message encoding and decoding

## System Architecture

The system consists of the following stages:

1. Key generation using quantum circuits
2. Qubit encoding based on randomly selected bases
3. Transmission through a noisy quantum channel
4. Measurement at receiver side
5. Basis reconciliation and key sifting
6. QBER estimation
7. Error correction using CASCADE
8. Privacy amplification to generate secure key
9. Eavesdropper detection using machine learning
10. Message encryption and decryption

## Installation

Clone the repository to your local system and navigate into the project directory. Install all required dependencies using the requirements file.

Install dependencies using pip and ensure all required Python libraries are available before running the application.

---

## Running the Application

Run the backend server using Python. Once the server starts, open a web browser and access the application through the local host address.

The interface allows configuration of various simulation parameters including noise models and message input.
Run the project:

1. Open terminal in project folder
2. Install dependencies:
   pip install -r requirements.txt
3. Start server:
   python app2.py
4. Open browser:
   http://127.0.0.5500

## Project Structure

app.py handles the backend logic, including quantum simulation, noise modeling, error correction, and API handling.

templates directory contains the HTML frontend used to interact with the simulator.

static directory contains CSS files for styling the web interface.

requirements.txt lists all required Python dependencies.

eve_detector.pkl stores the trained machine learning model used for eavesdropper detection.

README.md provides complete documentation for the project.

-------------------------------------------------------------------------------------------------------------------------------------------
## Output Parameters

The simulator provides the following outputs:

* Global Quantum Bit Error Rate (QBER)
* Number of matched segments
* CASCADE error corrections performed
* Encoded and decoded messages
* Final secure key length after privacy amplification
* Secret Key Rate (SKR)
* Eavesdropper detection result

## Applications

* Educational tool for learning quantum cryptography
* Research platform for analyzing QKD performance
* Demonstration of quantum communication concepts
* Study of noise effects in quantum channels

## Future Work

* Integration with real quantum hardware (IBM Quantum)
* Enhanced machine learning models for detection
* Optimization of CASCADE protocol
* Support for additional QKD protocols
* Cloud deployment for remote access

## Author

Omkar Pawar
Niraj Gharate
B.Tech, Electronics and Communication Engineering
Visvesvaraya National Institute of Technology, Nagpur

# Acknowledgment

This project was developed as part of the final year B.Tech program under academic guidance and support from the faculty of the Electronics and Communication Engineering Department at VNIT Nagpur.
