"""
图片压缩脚本：将 molly-h5/images 中的图片压缩为 WebP 格式
PNG -> WebP (lossy, quality 85), JPG -> WebP (quality 80)
同时限制最大宽度，大幅减小文件体积
"""
from PIL import Image
import os, glob

SRC = 'D:/workbuddy/2026-06-05-task-18/molly-h5/images'
TARGET_DIR = SRC  # 输出到同一目录

# 压缩配置
CONFIG = {
    'molly_':    {'max_w': 900,  'q': 85, 'format': 'webp'},  # Molly 角色大图
    'head_molly':{'max_w': 700,  'q': 85, 'format': 'webp'},  # Molly 头像
    'painting-': {'max_w': 1000, 'q': 80, 'format': 'webp'},  # 名画
    'cover':     {'max_w': 800,  'q': 82, 'format': 'webp'},  # 封面
    'molly_artist_icon': {'max_w': 400, 'q': 82, 'format': 'webp'},  # 小图标
    'molly_head_icon':   {'max_w': 120, 'q': 85, 'format': 'webp'},  # 头像小图
}

DEFAULT_CFG = {'max_w': 1200, 'q': 80, 'format': 'webp'}

def get_config(fname):
    for prefix, cfg in CONFIG.items():
        if fname.startswith(prefix):
            return cfg
    return DEFAULT_CFG

def compress_image(filepath):
    fname = os.path.basename(filepath)
    name_no_ext = os.path.splitext(fname)[0]
    
    # 跳过 bak 和非图片文件
    if fname.endswith('.bak'):
        return None
    
    cfg = get_config(fname)
    
    try:
        img = Image.open(filepath)
        orig_size = os.path.getsize(filepath)
        orig_w, orig_h = img.size
        
        # 缩放
        max_w = cfg['max_w']
        if orig_w > max_w:
            ratio = max_w / orig_w
            new_w = max_w
            new_h = int(orig_h * ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            print(f'  Resize: {orig_w}x{orig_h} -> {new_w}x{new_h}')
        
        # PNG RGBA 转 RGB (白色背景)，如果不需要透明的话
        # Molly PNG 需要保留透明 -> 使用 WebP 支持 alpha
        if img.mode == 'RGBA':
            # WebP 支持原生 alpha
            pass
        elif img.mode == 'P':
            img = img.convert('RGBA')
        elif img.mode == 'CMYK':
            img = img.convert('RGB')
        
        # 输出路径
        fmt = cfg['format']
        ext = 'webp' if fmt == 'webp' else 'jpg'
        out_path = os.path.join(TARGET_DIR, f'{name_no_ext}.{ext}')
        
        save_kwargs = {'quality': cfg['q'], 'method': 6}
        if fmt == 'webp':
            save_kwargs['lossless'] = False
        
        img.save(out_path, format=fmt.upper(), **save_kwargs)
        
        new_size = os.path.getsize(out_path)
        reduction = (1 - new_size / orig_size) * 100
        
        print(f'  {fname} ({orig_size//1024}KB) -> {name_no_ext}.{ext} ({new_size//1024}KB)  -{reduction:.0f}%')
        
        # 删除原文件
        if os.path.samefile(out_path, filepath) is False:
            os.remove(filepath)
            if out_path != filepath:
                pass
        
        return out_path
    except Exception as e:
        print(f'  ERROR {fname}: {e}')
        return None

# 收集所有图片
all_files = glob.glob(f'{SRC}/*.png') + glob.glob(f'{SRC}/*.jpg')
all_files = [f for f in all_files if not f.endswith('.bak')]

print(f'找到 {len(all_files)} 个图片文件\n')

total_before = sum(os.path.getsize(f) for f in all_files)
print(f'压缩前总大小: {total_before/1024/1024:.1f}MB\n')

# 压缩
processed = []
for f in sorted(all_files):
    result = compress_image(f)
    if result:
        processed.append(result)

total_after = sum(os.path.getsize(f) for f in processed)
print(f'\n压缩后总大小: {total_after/1024/1024:.1f}MB')
print(f'总体缩减: {(1-total_after/total_before)*100:.0f}%')
print(f'\n当前目录文件:')
for f in sorted(os.listdir(SRC)):
    sz = os.path.getsize(os.path.join(SRC, f))
    print(f'  {f}: {sz//1024}KB')
