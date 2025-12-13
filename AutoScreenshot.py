import pyautogui
import time
import os
import datetime
import tkinter
from tkinter import messagebox
from PIL import Image, ImageTk	# 外部ライブラリ

#######################################*
# 変数定義
# (環境に応じて変更する)
#######################################*
# 取得範囲
global x1, y1, x2, y2
x1 = y1 = x2 = y2 = 0
# スクショ間隔(秒)
span = 2
# 出力フォルダ頭文字
h_foldername = "output"
# 出力ファイル頭文字
h_filename = "img"
# スクリーンショットを開始するまでの時間(秒)
wait = 5
# 縮小倍率の規定
RESIZE_RETIO = 2

#######################################*
# 数値の入力
#######################################*
def input_number(str):
	n = -1
	while True:
		try:
			n = int(input(str))
			break
		except ValueError:
			print("ERROR: A non-numeric character was entered.")
			break
		except EOFError:
			break
	return n

#######################################*
# ドラッグ開始した時のイベント
#######################################*
def start_point_get(event):
	# グローバル変数に書き込みを行なうため宣言
	global x1, y1

	# すでに"rect1"タグの図形があれば削除
	canvas1.delete("rect1")

	# canvas1上に四角形を描画（rectangleは矩形の意味）
	canvas1.create_rectangle(event.x,
							 event.y,
							 event.x + 1,
							 event.y + 1,
							 outline="red",
							 tag="rect1")

	# グローバル変数に座標を格納
	x1, y1 = event.x, event.y

#######################################*
# ドラッグ中のイベント
#######################################*
def rect_drawing(event):
	# ドラッグ中のマウスポインタが領域外に出た時の処理
	if event.x < 0:
		x2 = 0
	else:
		x2 = min(img_resized.width, event.x)
	if event.y < 0:
		y2 = 0
	else:
		y2 = min(img_resized.height, event.y)

	# "rect1"タグの画像を再描画
	canvas1.coords("rect1", x1, y1, x2, y2)

#######################################*
# ドラッグを離したときのイベント
#######################################*
def release_action(event):
	global x1, y1, x2, y2

	# "rect1"タグの画像の座標を元の縮尺に戻して取得
	x1, y1, x2, y2 = [
		round(n * RESIZE_RETIO) for n in canvas1.coords("rect1")
	]

	# スクリーンショット領域の確認
	s = '領域指定を終了しますか？\n' + '(' + str(x1) + ' , ' + str(y1) + ') x (' + str(x2) + ' , ' + str(y2) + ')'
	result = pyautogui.confirm(s, buttons=['OK', 'Cancel'])
	if result == 'OK':
		root.destroy()
	else:
		x1 = y1 = x2 = y2 = 0

#######################################*
# スクリーンショットする領域の取得
#######################################*
# 表示する画像の取得（スクリーンショット）
img = pyautogui.screenshot()

# スクリーンショットした画像は表示しきれないので画像リサイズ
img_resized = img.resize(size=(int(img.width / RESIZE_RETIO),
							   int(img.height / RESIZE_RETIO)),
						 resample=Image.BILINEAR)

root = tkinter.Tk()

# tkinterウィンドウを常に最前面に表示
root.attributes("-topmost", True)

# tkinterで表示できるように画像変換
img_tk = ImageTk.PhotoImage(img_resized)

# Canvasウィジェットの描画
canvas1 = tkinter.Canvas(root,
						 bg="black",
						 width=img_resized.width,
						 height=img_resized.height)

# Canvasウィジェットに取得した画像を描画
canvas1.create_image(0, 0, image=img_tk, anchor=tkinter.NW)

# Canvasウィジェットを配置し、各種イベントを設定
canvas1.pack()
canvas1.bind("<ButtonPress-1>", start_point_get)
canvas1.bind("<Button1-Motion>", rect_drawing)
canvas1.bind("<ButtonRelease-1>", release_action)
root.mainloop()

# 矩形が選択されなかった場合は終了する
if (x1 + y1 + x2 + y2) == 0:
	exit()

#######################################*
# 実行時に定義する変数の入力
#######################################*
# ページ数の入力
page = input_number("input number of pages to screenshot: ")
if page == -1: exit()

# 開始インデックス番号の入力
index = input_number("input starting index number: ")
if index == -1: exit()

#######################################*
# スクリーンショット取得処理
#######################################*
# 待機時間 (この間にスクショを取得するウィンドウをアクティブにする)
for i in range(wait):
	print(str(wait-i) + " seconds to start...")
	time.sleep(1)

# 開始
print("Start auto screenshot")

# 出力フォルダ作成
os.makedirs(h_foldername, exist_ok=True)

# ページ数分スクリーンショットをとる
for p in range(page):
	# 出力ファイル名(頭文字_連番.png)
	out_filename = h_filename + "_" + str(index).zfill(3) + '.png'
	print(str(p+1).zfill(3) + ": " + out_filename)

	# スクリーンショット取得・保存処理
	# キャプチャ範囲： 左上のx座標, 左上のy座標, 幅, 高さ
	s = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))

	# 出力パス： 出力フォルダ名 / 出力ファイル名
	s.save(h_foldername + '/' + out_filename)

	# 右矢印キー押下 または 左クリック押下 (動作する方を有効にする)
#	pyautogui.keyDown('right')
#	pyautogui.press('right')
	pyautogui.click()

	# ファイルのインデックスを更新
	index = index + 1

	# 次のスクリーンショットまで待機
	time.sleep(span)

tk.messabebox.showinfo('終了しました')

