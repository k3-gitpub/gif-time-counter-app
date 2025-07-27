from PIL import Image
from tkinter import Tk, filedialog, Button, Label, StringVar

def get_gif_info(filepath):
    with Image.open(filepath) as im:
        total_duration = 0
        frame_count = 0
        try:
            while True:
                duration = im.info.get('duration', 0)
                total_duration += duration
                frame_count += 1
                im.seek(im.tell() + 1)
        except EOFError:
            pass
    return total_duration / 1000, frame_count  # (秒, フレーム数)

def select_and_show():
    gif_path = filedialog.askopenfilename(
        title="GIFファイルを選択してください",
        filetypes=[("GIF files", "*.gif")]
    )
    if gif_path:
        duration, frames = get_gif_info(gif_path)
        if duration > 0:
            fps = frames / duration
        else:
            fps = 0
        result.set(
            f"再生時間:   {duration} 秒\n"
            f"フレーム数:    {frames} 枚\n"
            f"FPS:             {fps:.0f} fps"
        )
    else:
        result.set("ファイルが選択されませんでした。")

if __name__ == "__main__":
    root = Tk()
    root.title("GIF情報カウンター")
    result = StringVar()
    result.set("ボタンを押してGIFを選択してください。")
    Button(root, text="GIFファイルを選択", command=select_and_show).pack(pady=10)
    Label(root, textvariable=result, justify="left").pack(padx=10, pady=10)
    root.mainloop()