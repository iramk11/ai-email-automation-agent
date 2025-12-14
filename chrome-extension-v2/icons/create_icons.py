#!/usr/bin/env python3
"""
Generate PNG icons from SVG for Chrome extension
Requires: pip install cairosvg pillow
"""

try:
    import cairosvg
    from PIL import Image
    import io
    import os

    # SVG content
    svg_content = '''<svg width="128" height="128" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#6366f1;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#4f46e5;stop-opacity:1" />
        </linearGradient>
      </defs>
      <rect width="128" height="128" rx="24" fill="url(#grad)"/>
      <path d="M32 40 L64 64 L96 40 M32 64 L64 88 L96 64" stroke="white" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
      <circle cx="96" cy="40" r="8" fill="white"/>
      <circle cx="96" cy="64" r="8" fill="white"/>
    </svg>'''

    sizes = [16, 48, 128]
    
    for size in sizes:
        # Convert SVG to PNG
        png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'), output_width=size, output_height=size)
        
        # Save PNG
        output_path = f'icon{size}.png'
        with open(output_path, 'wb') as f:
            f.write(png_data)
        
        print(f'Created {output_path} ({size}x{size})')
    
    print('\n✅ Icons created successfully!')
    
except ImportError:
    print("""
    Missing dependencies. Install with:
    pip install cairosvg pillow
    
    Or use an online SVG to PNG converter:
    1. Open icon.svg in a browser
    2. Use a tool like https://cloudconvert.com/svg-to-png
    3. Export at 16x16, 48x48, and 128x128 pixels
    4. Save as icon16.png, icon48.png, icon128.png
    """)

