# BlinkOS Assets

This directory contains images, icons, and other media assets for the BlinkOS project.

## Directory Structure

```
assets/
├── icons/              # Application icons
├── images/             # Screenshots and demo images
├── videos/             # Demo videos and recordings
└── README.md          # This file
```

## Asset Guidelines

### Screenshots
- Use PNG format for screenshots
- Recommended resolution: 1920x1080 or higher
- Include descriptive filenames (e.g., `main-control-panel.png`)

### Icons
- Provide multiple sizes (16x16, 32x32, 64x64, 128x128, 256x256)
- Use PNG format with transparency
- Follow macOS icon design guidelines

### Demo Videos
- Use MP4 or WebM format
- Keep file sizes reasonable (<50MB)
- Include captions or descriptions

## Usage

Reference assets in documentation using relative paths:
```markdown
![BlinkOS Control Panel](../assets/images/control-panel.png)
```

## Contributing Assets

When adding new assets:
1. Optimize file sizes
2. Use descriptive filenames
3. Update this README if adding new categories
4. Ensure proper licensing for any third-party assets
