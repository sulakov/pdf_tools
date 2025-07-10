# PDF Tools – Compress and Merge iPhone Scans  
Author: Eugen Sulakov

This lightweight PyQt5 desktop tool was born from a simple practical need:  
When scanning long multi-page documents with an iPhone, two problems arise:

1. **iPhone Notes splits long scans into multiple PDFs** due to internal page limits.
2. **Each PDF is extremely large**, as every page is stored as a full-resolution color photo.

### What this app does

- Compresses iPhone-style scanned PDFs into grayscale, low-DPI, optimized JPEG
- Merges split PDFs into one file, with automatic folder structure and naming
- Features batch processing, progress bar, and presets for text documents

### Preset Profiles

| Profile           | DPI | JPEG | Notes                 |
|-------------------|-----|------|------------------------|
| High Quality       | 144 | 60%  | Crisp text             |
| Balanced           | 100 | 40%  | Good for normal use    |
| iPhone Optimized   | 72  | 25%  | Best for scanned pages |
| Ultra Small        | 72  | 20%  | For minimal file size  |

Updated - I encountered the fact that in some documents there is a need to save color photos, so 3 color profiles were added to the presets.

### Install dependencies
```bash
pip install PyMuPDF pillow PyQt5
```

### Run the tool
```bash
python pdf_tools.py
```
