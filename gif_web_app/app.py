import os
from flask import Flask, request, render_template, flash, redirect, url_for
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename

# --- 設定 ---
# アップロードされたファイルを保存するフォルダ
UPLOAD_FOLDER = 'uploads'
# アップロードを許可するファイルの拡張子
ALLOWED_EXTENSIONS = {'gif'}

# --- Flaskアプリケーションの初期化 ---
app = Flask(__name__)
# UPLOAD_FOLDERをFlaskの設定に追加
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# flashメッセージ（ユーザーへの通知）機能に必要な秘密鍵
app.config['SECRET_KEY'] = 'a_very_secret_key_for_flash_messages' 
# アップロードされるファイルの最大サイズ（例: 16MB）
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# --- ヘルパー関数 ---
def allowed_file(filename):
    """アップロードされたファイルが許可された拡張子かチェックする"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_gif_info(filepath):
    """GIFファイルを解析して再生時間とフレーム数を取得する"""
    with Image.open(filepath) as im:
        # ファイルが本当にGIF形式か確認する
        if im.format != 'GIF':
            raise ValueError("ファイルはGIF形式ではありません。")

        total_duration = 0
        frame_count = 0
        try:
            while True:
                duration = im.info.get('duration', 0)
                # 一部のGIFではdurationが0の場合があるため、標準的な100ms(10fps)を割り当てる
                if duration == 0:
                    duration = 100
                total_duration += duration
                frame_count += 1
                im.seek(im.tell() + 1)
        except EOFError:
            if frame_count == 0:
                raise ValueError("GIFからフレームを読み取れませんでした。")
            return total_duration / 1000, frame_count  # (秒, フレーム数)

# --- ルーティング ---
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    # POSTリクエスト（ファイルがアップロードされた）の場合
    if request.method == 'POST':
        # リクエストにファイルが含まれているかチェック
        if 'file' not in request.files:
            flash('ファイルがリクエストに含まれていません', category='error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # ユーザーがファイルを選択しなかった場合（ファイル名が空）
        if file.filename == '':
            flash('ファイルが選択されていません', category='error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # 安全なファイル名に変換（危険な文字を削除）
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # ファイルを UPLOAD_FOLDER に保存
            file.save(filepath)

            try:
                duration, frames = get_gif_info(filepath)
                if duration > 0:
                    fps = frames / duration
                else:
                    fps = 0 # ゼロ除算を避ける

                results = {
                    'filename': filename,
                    'duration': f"{duration:.2f}",
                    'frames': frames,
                    'fps': f"{fps:.1f}"
                }
                # 解析結果をテンプレートに渡して表示
                return render_template('index.html', results=results)
            except (UnidentifiedImageError, ValueError) as e:
                flash(f'ファイル "{filename}" の解析に失敗しました。有効なGIFファイルか確認してください。', category='error')
                return redirect(url_for('upload_file'))
            except Exception as e:
                # 予期せぬエラーをログに出力しておくとデバッグに役立つ
                app.logger.error(f"An unexpected error occurred for {filename}: {e}")
                flash('予期せぬエラーが発生しました。もう一度お試しください。', category='error')
                return redirect(url_for('upload_file'))
        else:
            flash('許可されているファイル形式はGIFのみです。', category='error')
            return redirect(request.url)
    # GETリクエスト（単にページを訪れた）の場合
    return render_template('index.html')

if __name__ == '__main__':
    # 'uploads' フォルダがなければ作成する
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True) # debug=True は開発中のみ使用します
