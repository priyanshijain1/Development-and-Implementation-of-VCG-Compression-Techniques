# Development and Implementation of VCG Compression Techniques

This project explores Vectorcardiography (VCG) signal compression using two different approaches:

1. FFT-based compression as a baseline method
2. Discrete Wavelet Transform (DWT) with Grey Wolf Optimization (GWO) for adaptive threshold selection

The repository includes sample patient signal files, a custom GWO implementation, and Tkinter-based desktop interfaces for compressing VCG components and visualizing reconstruction quality.

## Overview

VCG signals contain three primary components:

- `VX`
- `VY`
- `VZ`

Because biomedical signals can be expensive to store and transmit, compression is important. This project focuses on reducing signal size while preserving reconstruction quality using these metrics:

- `MSE` - Mean Squared Error
- `PSNR` - Peak Signal-to-Noise Ratio
- `PRD` - Percent Root Difference
- `CR` - Compression Ratio

## Methods Included

### 1. FFT-Based Compression

Implemented in `method_1.py`

- Applies Fast Fourier Transform to the selected VCG signal
- Removes low-magnitude frequency components using a user-defined threshold
- Reconstructs the signal with inverse FFT
- Displays original vs reconstructed waveforms and average compression metrics

### 2. DWT + GWO Compression

Implemented in `dwt_with_gwo.py`

- Applies wavelet decomposition to the VCG signal
- Uses thresholding on wavelet coefficients for compression
- Optimizes the threshold with Grey Wolf Optimization
- Penalizes high-distortion solutions to preserve signal quality
- Displays reconstructed signals and per-component metrics in the GUI

### 3. Grey Wolf Optimizer

Implemented in `GWO.py`

- Custom implementation of the Grey Wolf Optimization algorithm
- Used to search for an effective compression threshold in the DWT-based workflow
- Built with helper structures from the bundled `EvoloPy` package

## Project Structure

```text
.
|-- GWO.py
|-- dwt_with_gwo.py
|-- method_1.py
|-- patient_1/
|-- patient_2/
|-- patient_3/
|-- EvoloPy/
`-- README.md
```

## Dataset Files

The repository contains sample patient records inside:

- `patient_1/`
- `patient_2/`
- `patient_3/`

Each patient folder includes files such as:

- `.hea`
- `.dat`
- `.xyz`

These are used by `wfdb` to read the VCG records.

## Requirements

Install the main Python dependencies before running the project:

```bash
pip install numpy matplotlib scipy wfdb pywavelets
```

Tkinter is also required for the desktop GUI and is usually included with standard Python installations.

## How to Run

### Run the FFT-Based GUI

```bash
python method_1.py
```

### Run the DWT + GWO GUI

```bash
python dwt_with_gwo.py
```

## Workflow

### FFT Method

1. Load a VCG record
2. Select `VX`, `VY`, `VZ`, or `All`
3. Enter a compression threshold
4. Compress and reconstruct the signal
5. View plots and average performance metrics

### DWT + GWO Method

1. Load a VCG record
2. Select the signal component and wavelet family
3. Run GWO to find an effective threshold
4. Compress and reconstruct the signal using wavelet coefficients
5. View plots and quality/compression metrics for each component

## Current Notes

- The GUI scripts currently use hardcoded dataset paths. If the project is moved to another machine, update the `file_paths` list inside `method_1.py` and `dwt_with_gwo.py`.
- The project is structured as an academic or experimental implementation rather than a packaged production library.
- The repository includes an `evolopy_env/` virtual environment directory, but you may prefer creating a fresh local environment for reproducibility.

## Possible Improvements

- Replace hardcoded paths with a file picker
- Save compression results to CSV
- Add support for more wavelet families and decomposition levels
- Add direct comparison charts between FFT and DWT + GWO methods
- Convert the project into a reusable Python package

## Use Cases

- Biomedical signal compression research
- Comparison of transform-based compression methods
- Educational demonstration of optimization-assisted signal processing
- Small-scale experimentation with VCG reconstruction quality

## Acknowledgements

- `wfdb` for reading physiological waveform records
- `PyWavelets` for wavelet decomposition and reconstruction
- `EvoloPy` for optimization support components used alongside the custom GWO implementation

## License

No license file is currently included in this repository. If you plan to share or publish the project, consider adding one.
