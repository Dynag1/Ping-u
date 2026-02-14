from PIL import Image
import os

def remove_background(input_path, output_path, tolerance=50):
    img = Image.open(input_path).convert("RGBA")
    datas = img.getdata()
    
    # Sample background color from top-left corner
    bg_color = img.getpixel((0, 0))
    bg_r, bg_g, bg_b, _ = bg_color
    
    new_data = []
    for item in datas:
        # item is (r, g, b, a)
        # Calculate distance from background color
        r, g, b = item[0], item[1], item[2]
        
        # Simple distance check (can be improved closer to Euclidean)
        diff = abs(r - bg_r) + abs(g - bg_g) + abs(b - bg_b)
        
        # Also force remove very dark pixels even if not matching corner exactly
        is_very_dark = r < 40 and g < 40 and b < 50
        
        if diff < tolerance or is_very_dark:
            new_data.append((0, 0, 0, 0)) # Transparent
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    img.save(output_path, "PNG")
    print(f"Saved transparent logo to {output_path}")
    return img

def create_favicon(img, output_path):
    icon = img.resize((32, 32), Image.Resampling.LANCZOS)
    icon.save(output_path, format='ICO')
    print(f"Saved favicon to {output_path}")

def create_app_icon(img, output_path):
    icon = img.resize((256, 256), Image.Resampling.LANCZOS)
    icon.save(output_path, "PNG")
    print(f"Saved app icon to {output_path}")

if __name__ == "__main__":
    base_dir = "/home/hemge/Clood/021 - Programmation/Python/Ping ü/src/web/static/img"
    input_file = os.path.join(base_dir, "logo_raw.png")
    output_logo = os.path.join(base_dir, "logo.png")
    output_favicon = os.path.join(base_dir, "favicon.ico")
    output_icon = os.path.join(base_dir, "icon.png") # For .deb/.exe
    
    # Root dir for global icons
    root_dir = "/home/hemge/Clood/021 - Programmation/Python/Ping ü"
    
    # Process
    if os.path.exists(input_file):
        processed_img = remove_background(input_file, output_logo, tolerance=100)
        
        # Favicon for web (32x32)
        create_favicon(processed_img, output_favicon)
        
        # App Icon png (256x256)
        create_app_icon(processed_img, output_icon)
        
        # Overwrite root icons for Build (.exe / .deb)
        root_logo_png = os.path.join(root_dir, "logoP.png")
        root_logo_ico = os.path.join(root_dir, "logoP.ico")
        root_icon_ico = os.path.join(root_dir, "icon.ico")
        
        # Save logoP.png
        processed_img.save(root_logo_png)
        print(f"Updated {root_logo_png}")
        
        # Save multi-size ICO
        processed_img.save(root_logo_ico, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
        print(f"Updated {root_logo_ico}")
        
        processed_img.save(root_icon_ico, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
        print(f"Updated {root_icon_ico}")
        
    else:
        print(f"Input file not found: {input_file}")
