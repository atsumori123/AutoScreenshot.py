import argparse
import pyautogui
import time
import os
import datetime
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk	# 外部ライブラリ

#######################################*
# 変数定義
# (環境に応じて変更する)
#######################################*
# 取得範囲
global start_x, start_y, end_x, end_y
start_x = start_y = end_x = end_y = 0
# スクショ間隔(秒)
span = 2
# 出力フォルダ頭文字
h_foldername = "output"
# 出力ファイル頭文字
h_filename = "img"
# スクリーンショットを開始するまでの時間(秒)
wait = 5

#######################################*
# スクリーンショットの領域を取得
#######################################*
class ClipScreen():
	# 縮小倍率の規定
	RESIZE_RETIO = 2

	def __init__(self):
		# クリップ座標
		self.x1 = self.y1 = self.x2 = self.y2 = 0

		# 表示する画像の取得（スクリーンショット）
		self.img = pyautogui.screenshot()

		# スクリーンショットした画像は表示しきれないので画像リサイズ
		self.img_resized = self.img.resize(size=(int(self.img.width / ClipScreen.RESIZE_RETIO),
												 int(self.img.height / ClipScreen.RESIZE_RETIO)),
												 resample=Image.BILINEAR)

		self.root = tk.Tk()

		# tkinterウィンドウを常に最前面に表示
		self.root.attributes("-topmost", True)

		# tkinterで表示できるように画像変換
		img_tk = ImageTk.PhotoImage(self.img_resized)

		# Canvasウィジェットの描画
		self.canvas1 = tk.Canvas(self.root, bg="black",
								 width=self.img_resized.width,
								 height=self.img_resized.height)

		# Canvasウィジェットに取得した画像を描画
		self.canvas1.create_image(0, 0, image= img_tk, anchor=tk.NW)

		# Canvasウィジェットを配置し、各種イベントを設定
		self.canvas1.pack()
		self.canvas1.bind("<ButtonPress-1>", self.start_point_get)
		self.canvas1.bind("<Button1-Motion>", self.rect_drawing)
		self.canvas1.bind("<ButtonRelease-1>", self.release_action)

		self.root.mainloop()

	#######################################*
	# ドラッグ開始した時のイベント
	#######################################*
	def start_point_get(self, event):
		# すでに"rect1"タグの図形があれば削除
		self.canvas1.delete("rect1")

		# canvas1上に四角形を描画（rectangleは矩形の意味）
		self.canvas1.create_rectangle(event.x, event.y,
									  event.x + 1, event.y + 1,
									  outline="red", tag="rect1")

		# クラス変数に座標を格納
		self.x1, self.y1 = event.x, event.y

	#######################################*
	# ドラッグ中のイベント
	#######################################*
	def rect_drawing(self, event):
		# ドラッグ中のマウスポインタが領域外に出た時の処理
		if event.x < 0:
			self.x2 = 0
		else:
			self.x2 = min(self.img_resized.width, event.x)
		if event.y < 0:
			self.y2 = 0
		else:
			self.y2 = min(self.img_resized.height, event.y)
	
		# "rect1"タグの画像を再描画
		self.canvas1.coords("rect1", self.x1, self.y1, self.x2, self.y2)

	#######################################*
	# ドラッグを離したときのイベント
	#######################################*
	def release_action(self, event):
		global start_x, start_y, end_x, end_y
	
		# "rect1"タグの画像の座標を元の縮尺に戻して取得
		start_x, start_y, end_x, end_y = [
			round(n * ClipScreen.RESIZE_RETIO) for n in self.canvas1.coords("rect1")
		]
	
		# スクリーンショット領域の確認
		s = 'この領域でスクリーンショットを取得してもよろしいですか？\n\n' + '(' + str(self.x1) + ' , ' + str(self.y1) + ') x (' + str(self.x2) + ' , ' + str(self.y2) + ')'
		result = pyautogui.confirm(s, buttons=['OK', 'Cancel'])
		if result == 'OK':
			self.root.destroy()
		else:
			start_x = start_y = end_x = end_y = 0

if __name__ == "__main__":
	# 引数設定
	parser = argparse.ArgumentParser()
	parser.add_argument("-n", help="number of pages to screenshot", type=int)
	parser.add_argument("-i", help="starting index number", type=int)
	parser.add_argument("-s", help="screenshot area. format is 'x1,y2,x2,y2'")
	args = parser.parse_args()

	# 引数(ページ数, 開始インデックス番号)チェック
	page = 1 if args.n == None else args.n
	index = 1 if args.i == None else args.i

	# 引数(スクリーンショットの領域)チェック
	if args.s:
		l = args.s.split(',')
		if len(l) != 4:
			print("Screenshot area is incorrect.")
			exit()
		start_x, start_y, end_x, end_y = [int(n) for n in l]
		if (start_x >= end_x) or (start_y >= end_y):
			print("Invalid screenshot area.")
			exit()
	else:
		ClipScreen()
		if (start_x + start_y + end_x + end_y) == 0:
			print("Auto screenshot has been cancelled.")
			exit()

	# 実行条件の表示
	print("Auto screen shot")
	print("  screenshot page num : " + str(page))
	print("  start index number  : " + str(index))
	print("  screenshot area     : (%d,%d) x (%d,%d)" % (start_x, start_y, end_x, end_y))
	print("")

	#######################################*
	# スクリーンショット取得処理
	#######################################*
	# 待機時間 (この間にスクショを取得するウィンドウをアクティブにする)
	for i in range(wait):
		print(f"\r{wait-i} seconds to start...", end="")
		time.sleep(1)
	
	# 開始
	print("\nStart auto screenshot")
	
	# 出力フォルダ作成
	os.makedirs(h_foldername, exist_ok=True)
	
	# ページ数分スクリーンショットをとる
	for p in range(page):
		# 出力ファイル名(頭文字_連番.png)
		out_filename = h_filename + "_" + str(index).zfill(3) + '.png'
		print(str(p+1).zfill(3) + ": " + out_filename)
	
		# スクリーンショット取得・保存処理
		# キャプチャ範囲： 左上のx座標, 左上のy座標, 幅, 高さ
		s = pyautogui.screenshot(region=(start_x, start_y, end_x-start_x, end_y-start_y))
	
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
	
	print("end")

