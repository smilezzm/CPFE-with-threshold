(editted with Claude Sonnet 4.5)
# Lung CT Analysis Tool - Setup and Usage Guide

This tool analyzes lung CT scans to calculate LAA (Low Attenuation Area) and HAA (High Attenuation Area) ratios, and provides interactive visualizations.

## Prerequisites

A blank computer with no Python or development tools installed.

## Installation Steps

### Step 1: Install Python

1. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download Python 3.8 or later (recommended: Python 3.11 or 3.12)
3. Run the installer
4. **IMPORTANT**: Check the box "Add Python to PATH" during installation
5. Click "Install Now"
6. Verify installation by opening Command Prompt (Windows) or Terminal (Mac/Linux) and typing:
   ```bash
   python --version
   ```
   You should see something like `Python 3.11.x`

   (There is a guid on how to open Command Prompt in Windows: [https://www.163.com/dy/article/JO80DNUR055629UX.html](https://www.163.com/dy/article/JO80DNUR055629UX.html). **Almost all the commands below are to be run in Command Prompt or Terminal.**)

### Step 2: Install Anaconda (Recommended Alternative)

If you prefer using Anaconda (which makes package management easier):

1. Go to [https://www.anaconda.com/download](https://www.anaconda.com/download)
2. Download the installer for your operating system
3. Run the installer and follow the prompts
4. After installation, open Anaconda Prompt (Windows) or Terminal (Mac/Linux) 

### Step 3: Create a Virtual Environment (Recommended)

Using Anaconda:
```bash
conda create -n lung_analysis python=3.11
conda activate lung_analysis
```

Or using standard Python:
```bash
python -m venv lung_env
# On Windows:
lung_env\Scripts\activate
# On Mac/Linux:
source lung_env/bin/activate
```

### Step 4: Install Required Python Packages

With your virtual environment activated, install the required packages:

```bash
pip install numpy
pip install nibabel
pip install SimpleITK
pip install matplotlib
pip install lungmask
```

Or install all at once:
```bash
pip install numpy nibabel SimpleITK matplotlib lungmask
```

**Note**: The `lungmask` package may take a few minutes to install as it includes deep learning models.

### Step 5: Install a Code Editor (Optional)

#### Option A: Visual Studio Code (Recommended)
1. Go to [https://code.visualstudio.com/](https://code.visualstudio.com/)
2. Download and install VS Code
3. Install Python extension:
   - Open VS Code
   - Click on Extensions icon (or press Ctrl+Shift+X)
   - Search for "Python"
   - Install the official Python extension by Microsoft

#### Option B: Use Any Text Editor
You can also use Notepad (Windows), TextEdit (Mac), or any text editor you prefer.

## Running the Script

### Method 1: Using Command Line

1. Open Command Prompt (Windows) or Terminal (Mac/Linux)
2. Navigate to the project directory:
   ```bash
   cd "path\to\your\project\folder"
   ```
3. Activate your virtual environment (if you created one):
   ```bash
   # If you use Anaconda:
   conda activate lung_analysis
   
   # If you use standard Python on Windows:
   lung_env\Scripts\activate
   
   # If you use standard Python on Mac/Linux:
   source lung_env/bin/activate
   ```
4. Run the script:
   ```bash
   python threshold_lung.py
   ```

### Method 2: Using VS Code

1. Open VS Code
2. Click "File" → "Open Folder" and select your project folder
3. Open `threshold_lung.py`
4. Select your Python interpreter (bottom right corner):
   - Click on the Python version shown
   - Choose the virtual environment you created
5. Press F5 or click the "Run" button to execute the script

## Script Configuration

Before running, edit the last line of `threshold_lung.py` to specify your input files:

```python
if __name__ == "__main__":
    threshold_lung('./your_ct_file.nii.gz', './mask/your_mask_file.nii.gz')
```

Replace:
- `'./your_ct_file.nii.gz'` with the path to your CT scan file
- `'./mask/your_mask_file.nii.gz'` with the desired output path for the lung mask

**Note**: Make sure the `mask` directory exists before running, or create it:
```bash
mkdir mask
```

### Custom LAA and HAA Bounds

You can also customize the LAA and HAA thresholds:

```python
threshold_lung('./your_ct_file.nii.gz', 
               './mask/your_mask_file.nii.gz',
               LAA_bound=[-1024, -950],  # Default LAA range
               HAA_bound=[-700, -200])   # Default HAA range
```

## Output

When you run the script, you will see:

1. **Figure 1: Overall Lung Histogram**
   - Shows the intensity distribution across all lung voxels
   - Displays total LAA and HAA ratios
   - Orange dashed lines: LAA boundaries
   - Red dashed lines: HAA boundaries

2. **Figure 2: Interactive Slice Viewer** (Two subplots)
   - **Left**: CT slice with color overlay
     - Yellow regions: LAA (Low Attenuation Areas)
     - Red regions: HAA (High Attenuation Areas)
     - Grayscale: Normal lung tissue
   - **Right**: Histogram for the current slice
     - Shows intensity distribution for that specific slice
     - Displays LAA and HAA ratios for the slice
     - Blue dashed lines: LAA boundaries
     - Red dashed lines: HAA boundaries

### Navigating the Interactive Viewer

- **Mouse Scroll**: Scroll up/down to move through slices
- **Slider**: Use the slider at the bottom to jump to specific slices
- Both the image and histogram update automatically as you change slices

## Troubleshooting

### "Python is not recognized as an internal or external command"
- Python was not added to PATH during installation
- Reinstall Python and check "Add Python to PATH"
- Or manually add Python to your system PATH

### "No module named 'nibabel'" (or other package)
- The package is not installed
- Activate your virtual environment and run: `pip install nibabel`

### "FileNotFoundError: [Errno 2] No such file or directory"
- Check that your input file path is correct
- Make sure the `mask` directory exists (create it with `mkdir mask`)
- Use absolute paths if relative paths don't work

### "lungmask installation fails"
- Try installing with: `pip install lungmask --no-cache-dir`
- Make sure you have a stable internet connection
- On some systems, you may need to install PyTorch separately first:
  ```bash
  pip install torch torchvision
  pip install lungmask
  ```

### Figures don't show up
- Make sure you're not running in a headless environment
- On some systems, you may need to install additional display backends:
  ```bash
  # For Linux:
  sudo apt-get install python3-tk
  ```

### Memory Issues
- Large CT scans may require significant RAM
- Close other applications to free up memory
- Consider processing one scan at a time

## File Structure

```
project_folder/
│
├── threshold_lung.py          # Main script
├── README.md                  # This file
├── mask/                      # Directory for generated lung masks
│   └── [output masks here]
├── train_1_a_1.nii.gz        # Example CT scan file
└── [your CT scan files]
```

## Data Format

- Input files should be in NIfTI format (`.nii` or `.nii.gz`)
- CT scans should contain Hounsfield Unit (HU) values
- Typical HU range for lung analysis: -1024 to 0

## Additional Notes

- First run may be slower as the lungmask model is downloaded and initialized
- The lung mask is automatically generated using a pre-trained deep learning model
- Generated masks are saved to the specified path for future use
- You can reuse masks to avoid regenerating them each time

## References

- lungmask: Automatic lung segmentation using deep learning
- NIfTI format: Standard medical imaging format
- LAA/HAA analysis: Common metrics for lung disease assessment

## Support

For issues specific to:
- **lungmask**: Visit [https://github.com/JoHof/lungmask](https://github.com/JoHof/lungmask)
- **nibabel**: Visit [https://nipy.org/nibabel/](https://nipy.org/nibabel/)
- **Python**: Visit [https://www.python.org/](https://www.python.org/)
