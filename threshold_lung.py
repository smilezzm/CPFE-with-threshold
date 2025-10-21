import numpy as np
import nibabel as nib
from lungmask import LMInferer
import SimpleITK as sitk
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

def threshold_lung(filepath: str, maskpath: str, LAA_bound: list=[-1024,-950], HAA_bound: list=[-700, -200]):
    # filepath looks like "./patient1_1.nii.gz"
    # maskpath looks like "./masks/patient1_1.nii.gz" Should first create the "mask" directory
    
    # 1. Get a mask for the lungs (1 for right lung and 2 for left lung)
    # Create the inferer
    inferer = LMInferer()
    # Load your input image
    input_image = sitk.ReadImage(filepath)
    # Apply the segmentation
    segmentation = inferer.apply(input_image)  # Returns a numpy array
    # Convert result to SimpleITK image and copy metadata
    result_out = sitk.GetImageFromArray(segmentation)
    result_out.CopyInformation(input_image)
    # Write the output with proper file extension
    sitk.WriteImage(result_out, maskpath)

    # 2. Find the statistics of the lung regions
    img = nib.load(filepath).get_fdata()
    mask = nib.load(maskpath).get_fdata()
    lung_img = img[(mask == 1) | (mask == 2)]
    # compute the LAA and HAA ratios over the entire lung region
    LAA_ratio = np.sum((lung_img >= LAA_bound[0]) & (lung_img <= LAA_bound[1])) / lung_img.size
    HAA_ratio = np.sum((lung_img >= HAA_bound[0]) & (lung_img <= HAA_bound[1])) / lung_img.size
    note = f"LAA ratio: {LAA_ratio:.4f}\nHAA ratio: {HAA_ratio:.4f}"
    plot_lung_hist(img, mask, bins=150, note=note,
                   hu_range=(-1024, 0), laa_bound=LAA_bound, haa_bound=HAA_bound)
    
    # Plot interactive slice viewer with LAA/HAA highlighting
    plot_interactive_slices(img, mask, LAA_bound=LAA_bound, HAA_bound=HAA_bound)


def lung_histogram(ct: np.ndarray, mask: np.ndarray, bins: int = 100, hu_range: tuple = (-1024, 0)):
    lung_voxels = ct[(mask == 1) | (mask == 2)]
    hist, edges = np.histogram(lung_voxels, bins=bins, range=hu_range)
    return hist, edges

def plot_lung_hist(ct: np.ndarray, mask: np.ndarray, bins: int = 100, note: str = "", hu_range: tuple = (-1024, 0),
                   laa_bound: list = [-1024, -950], haa_bound: list = [-700, -200]):
    hist, edges = lung_histogram(ct, mask, bins=bins, hu_range=hu_range)
    centers = 0.5 * (edges[:-1] + edges[1:])
    plt.figure(figsize=(6, 4))
    plt.bar(centers, hist, width=np.diff(edges), color="steelblue", align="center")

    if laa_bound:
        for x in laa_bound:
            plt.axvline(x, color="orange", linestyle="--", linewidth=1.5, label="LAA bound" if x == laa_bound[0] else None)
    if haa_bound:
        for x in haa_bound:
            plt.axvline(x, color="red", linestyle="--", linewidth=1.5, label="HAA bound" if x == haa_bound[0] else None)
    if note:
        plt.text(0.65, 0.95, note, transform=plt.gca().transAxes, va="top")
    if laa_bound or haa_bound:
        plt.legend(loc="upper left")

    plt.xlabel("HU")
    plt.ylabel("Voxel count")
    plt.title("Lung intensity histogram")
    plt.tight_layout()
    plt.show(block=False)


def plot_interactive_slices(ct: np.ndarray, mask: np.ndarray, 
                            LAA_bound: list = [-1024, -950], 
                            HAA_bound: list = [-700, -200]):
    """
    Interactive slice viewer with LAA (blue) and HAA (red) highlighting.
    Use mouse scroll to navigate through slices.
    Shows slice image and corresponding histogram side by side.
    """
    
    # Get number of slices (assuming z is the last dimension)
    num_slices = ct.shape[2]
    
    # Create figure with two subplots
    fig, (ax_img, ax_hist) = plt.subplots(1, 2, figsize=(16, 7))
    plt.subplots_adjust(bottom=0.15, left=0.05, right=0.95, wspace=0.3)
    
    # Initialize with middle slice
    current_slice = num_slices // 2
    
    # Create RGB image for the first slice
    def create_overlay_slice(slice_idx):
        # Get the slice
        ct_slice = ct[:, :, slice_idx]
        mask_slice = mask[:, :, slice_idx]
        
        # Normalize CT slice to 0-1 range for display
        ct_display = np.clip(ct_slice, -1024, 0)
        ct_display = (ct_display + 1024) / 1024
        
        # Create RGB image (grayscale base)
        rgb_image = np.stack([ct_display, ct_display, ct_display], axis=-1)
        
        # Create lung mask (only consider pixels in lung regions)
        lung_mask = (mask_slice == 1) | (mask_slice == 2)
        
        # Highlight LAA regions in yellow
        laa_mask = lung_mask & (ct_slice >= LAA_bound[0]) & (ct_slice <= LAA_bound[1])
        rgb_image[laa_mask] = [1, 1, 0]  # Yellow
        
        # Highlight HAA regions in red
        haa_mask = lung_mask & (ct_slice >= HAA_bound[0]) & (ct_slice <= HAA_bound[1])
        rgb_image[haa_mask] = [1, 0, 0]  # Red
        
        return rgb_image
    
    # Function to create histogram for a slice
    def create_slice_histogram(slice_idx):
        ct_slice = ct[:, :, slice_idx]
        mask_slice = mask[:, :, slice_idx]
        
        # Get lung voxels for this slice
        lung_voxels = ct_slice[(mask_slice == 1) | (mask_slice == 2)]
        
        if lung_voxels.size == 0:
            return None, None, None, None
        
        # Calculate LAA and HAA ratios for this slice
        laa_ratio = np.sum((lung_voxels >= LAA_bound[0]) & (lung_voxels <= LAA_bound[1])) / lung_voxels.size
        haa_ratio = np.sum((lung_voxels >= HAA_bound[0]) & (lung_voxels <= HAA_bound[1])) / lung_voxels.size
        
        # Create histogram
        hist, edges = np.histogram(lung_voxels, bins=100, range=(-1024, 0))
        centers = 0.5 * (edges[:-1] + edges[1:])
        
        return hist, centers, laa_ratio, haa_ratio
    
    # Display initial slice
    im = ax_img.imshow(create_overlay_slice(current_slice), cmap='gray', origin='lower')
    ax_img.set_title(f'Slice {current_slice + 1}/{num_slices}\nLAA: Yellow | HAA: Red', fontsize=12)
    ax_img.axis('off')
    
    # Display initial histogram
    hist, centers, laa_ratio, haa_ratio = create_slice_histogram(current_slice)
    bars = ax_hist.bar(centers, hist, width=np.diff(np.linspace(-1024, 0, 101)), 
                       color="steelblue", align="center")
    
    # Add LAA and HAA boundary lines
    laa_lines = [ax_hist.axvline(LAA_bound[0], color="blue", linestyle="--", linewidth=2, label="LAA bound"),
                 ax_hist.axvline(LAA_bound[1], color="blue", linestyle="--", linewidth=2)]
    haa_lines = [ax_hist.axvline(HAA_bound[0], color="red", linestyle="--", linewidth=2, label="HAA bound"),
                 ax_hist.axvline(HAA_bound[1], color="red", linestyle="--", linewidth=2)]
    
    # Add text annotation for ratios
    text_annotation = ax_hist.text(0.65, 0.95, 
                                   f'LAA ratio: {laa_ratio:.4f}\nHAA ratio: {haa_ratio:.4f}',
                                   transform=ax_hist.transAxes, va="top", fontsize=10,
                                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    ax_hist.set_xlabel("HU", fontsize=11)
    ax_hist.set_ylabel("Voxel count", fontsize=11)
    ax_hist.set_title(f"Lung Intensity Histogram - Slice {current_slice + 1}", fontsize=12)
    ax_hist.legend(loc="upper left")
    ax_hist.set_xlim(-1024, 0)
    
    # Function to update slice and histogram
    def update_slice(val):
        nonlocal current_slice
        current_slice = int(val)
        
        # Update slice image
        rgb_image = create_overlay_slice(current_slice)
        im.set_data(rgb_image)
        ax_img.set_title(f'Slice {current_slice + 1}/{num_slices}\nLAA: Yellow | HAA: Red', fontsize=12)
        
        # Update histogram
        hist, centers, laa_ratio, haa_ratio = create_slice_histogram(current_slice)
        if hist is not None:
            for bar, h in zip(bars, hist):
                bar.set_height(h)
            
            # Update text annotation
            text_annotation.set_text(f'LAA ratio: {laa_ratio:.4f}\nHAA ratio: {haa_ratio:.4f}')
            ax_hist.set_title(f"Lung Intensity Histogram - Slice {current_slice + 1}", fontsize=12)
            
            # Adjust y-axis limit if needed
            ax_hist.set_ylim(0, max(hist) * 1.1)
        
        fig.canvas.draw_idle()
    
    # Add slider
    ax_slider = plt.axes((0.2, 0.05, 0.6, 0.03))
    slider = Slider(ax_slider, 'Slice', 0, num_slices - 1, 
                    valinit=current_slice, valstep=1)
    slider.on_changed(update_slice)
    
    # Mouse scroll event
    def on_scroll(event):
        nonlocal current_slice
        if event.button == 'up':
            current_slice = min(current_slice + 1, num_slices - 1)
        elif event.button == 'down':
            current_slice = max(current_slice - 1, 0)
        slider.set_val(current_slice)
    
    fig.canvas.mpl_connect('scroll_event', on_scroll)
    
    plt.show()


if __name__ == "__main__":
    threshold_lung('./train_1_a_1.nii.gz','./mask/train_1_a_1.nii.gz')