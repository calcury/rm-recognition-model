import os
from PIL import Image

def crop_image_to_640x480(image_path):
    """
    将图片裁剪为640x480（中间裁剪）
    
    Args:
        image_path: 图片文件的路径
    """
    try:
        # 打开图片
        with Image.open(image_path) as img:
            # 获取图片原始尺寸
            original_width, original_height = img.size
            target_width, target_height = 640, 480
            
            # 检查图片是否小于目标尺寸（小于则不处理，避免拉伸）
            if original_width < target_width or original_height < target_height:
                print(f"⚠️  {os.path.basename(image_path)} 尺寸({original_width}x{original_height})小于640x480，跳过裁剪")
                return
            
            # 计算中间裁剪区域的坐标
            # 计算水平方向裁剪起始点：(原始宽度 - 目标宽度) / 2
            left = (original_width - target_width) / 2
            # 计算垂直方向裁剪起始点：(原始高度 - 目标高度) / 2
            top = (original_height - target_height) / 2
            # 裁剪区域结束点
            right = left + target_width
            bottom = top + target_height
            
            # 执行裁剪（PIL要求坐标为整数）
            cropped_img = img.crop((int(left), int(top), int(right), int(bottom)))
            
            # 保存裁剪后的图片（覆盖原文件，如需保留原文件可修改保存路径）
            # 如果想保留原文件，可将下面的image_path改为 f"{os.path.splitext(image_path)[0]}_cropped{os.path.splitext(image_path)[1]}"
            cropped_img.save(image_path)
            print(f"✅ {os.path.basename(image_path)} 裁剪完成，新尺寸：{cropped_img.size}")
            
    except Exception as e:
        print(f"❌ 处理 {os.path.basename(image_path)} 时出错：{str(e)}")

def process_all_images_in_current_dir():
    """处理当前目录下的所有图片"""
    # 支持的图片格式
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    
    # 获取当前目录路径
    current_dir = os.getcwd()
    print(f"📁 正在处理目录：{current_dir}")
    print("----------------------------------------")
    
    # 遍历目录中的所有文件
    for filename in os.listdir(current_dir):
        # 检查文件是否为支持的图片格式
        if filename.lower().endswith(supported_formats):
            file_path = os.path.join(current_dir, filename)
            # 跳过目录（只处理文件）
            if os.path.isfile(file_path):
                crop_image_to_640x480(file_path)
    
    print("----------------------------------------")
    print("🎉 所有图片处理完成！")

if __name__ == "__main__":
    # 安装依赖提示（首次运行需要）
    # pip install pillow
    try:
        import PIL
    except ImportError:
        print("⚠️  未检测到Pillow库，请先运行：pip install pillow")
    else:
        process_all_images_in_current_dir()
