import numpy as np
import pygame
import sys
import traceback
import copy
from pygame.locals import *

pygame.init()
pygame.mixer.init()

###
h = 0
w = 0
###

# 颜色
background = (201, 202, 187)
checkerboard = (80, 80, 80)
button = (52, 53, 44)

# 音乐


# 其他全局变量
clock = pygame.time.Clock()
t = True # 用于控制顺序
running = True # 用于结束游戏后阻止落子
# 定义储存所有棋盘状态的列表（用于悔棋）
map2 = copy.deepcopy(map)
maps = [map2]

# 定义窗口
screen = pygame.display.set_mode([1200, 806])
#定义窗口宽和高为1200和806


# 绘制棋盘
def Draw_a_chessboard(screen):
    # 填充背景色
    screen.fill(background)
    Background = pygame.image.load("bg3.jpg").convert_alpha()
    screen.blit(Background, (0, 0))
    # 画棋盘
    for i in range(9):
        pygame.draw.line(screen, checkerboard, (89 * i + 3, 93), (89 * i + 3, 713))
        pygame.draw.line(screen, checkerboard, (93, 89 * i + 3), (713, 89 * i + 3))
        #绘制直线段,起始点为(40*i+3,3)，中止点为(40*i+3,803)，颜色为checkerboard，线段宽度默认为1
    # 画边线
    pygame.draw.line(screen, checkerboard, (93, 93), (713, 93), 5)
    pygame.draw.line(screen, checkerboard, (93, 93), (93,713), 5)
    pygame.draw.line(screen, checkerboard, (713, 93), (713, 713), 5)
    pygame.draw.line(screen, checkerboard, (93, 713), (713, 713), 5)

    #在screen对象上画一个对象，颜色为button，[900,350]为绘制位置,[120,100]为尺寸，5为指定边框宽度
    pygame.draw.rect(screen, button, [900, 350, 120, 100], 5)
    pygame.draw.rect(screen, button, [900, 500, 120, 100], 5)
    pygame.draw.rect(screen, button, [900, 650, 200, 100], 5)
    s_font = pygame.font.Font('font.ttf', 40)
    #从一个字体文件创建一个Font对象，40为size
    #第一个参数是写的文字，第二个参数是布尔值，是否开启抗锯齿，第三个是颜色为button
    text1 = s_font.render("先手", True, button)
    text2 = s_font.render("后手", True, button)
    text3 = s_font.render("退出游戏", True, button)
    screen.blit(text1, (920, 370))
    screen.blit(text2, (920, 520))
    screen.blit(text3, (920, 670))


# 绘制棋子（横坐标，纵坐标，屏幕，棋子颜色（1代表黑，2代表白））
def Draw_a_chessman(x, y, screen, color):
    if color == 1:
        Black_chess = pygame.image.load("Black_chess.png").convert_alpha()
        screen.blit(Black_chess, (89 * x + 3 - 15, 89* y + 3 - 15))
        #在(40 * x + 3 - 15, 40 * y + 3 - 15)绘制一个黑棋子
    if color == 2:
        White_chess = pygame.image.load("White_chess.png").convert_alpha()
        screen.blit(White_chess, (89 * x + 3 - 15, 89 * y + 3 - 15))


# 绘制带有棋子的棋盘
def Draw_a_chessboard_with_chessman(map, screen):
    screen.fill(background)
    Draw_a_chessboard(screen)
    for i in range(9):
        for j in range(9):
            Draw_a_chessman(i + 1, j + 1, screen, map[i][j])




# 定义存储棋盘的列表
map = []
for i in range(24):
    map.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])


# 清零map列表
def clear():
    global map
    for i in range(9):
        for j in range(9):
            map[i][j] = 0


# 绘制提示器（类容，屏幕，字大小）
def text(s, screen, x):
    # 先把上一次的类容用一个矩形覆盖
    pygame.draw.rect(screen, background, [850, 100, 1200, 100])
    #在screen中[850,100]处位置，画一个大小为[1200,100]、颜色为bakground矩形

    # 定义字体跟大小
    s_font = pygame.font.Font('font.ttf', x)
    # 定义类容，是否抗锯齿，颜色
    s_text = s_font.render(s, True, button)
    #写一串文字“s”，抗锯齿，颜色为Button

    # 将字放在窗口指定位置
    screen.blit(s_text, (880, 100))
    pygame.display.flip()
    #更新整个待显示的 Surface 对象到屏幕上


# 主函数
def init():
    # 将 t，map，running设置为可改的
    global t, map, running, maps, r, h, w, map2, screen
    # 将map置零
    clear()

    # 定义窗口名字
    pygame.display.set_caption("五子棋")

    # 在窗口画出棋盘，提示器以及按钮
    Draw_a_chessboard(screen)
    pygame.display.flip()

def Who_first():
    while True:
        for event in pygame.event.get():
        # 从队列中获取事件
        # 点击x则关闭窗口
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # 点击窗口里面类容则完成相应指令
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos[0], event.pos[1]
                    if 900 < x < 1020 and 350 < y < 450:
                        return 1
                    if 900 < x < 1100 and 500 < y < 600:
                        return 0


def human_step():
    """
    运行一步的操作
    :return: 返回location=[x,y]
    """
    global t, map, running, maps, r, h, w
    # 只有running为真才能落子，主要用于游戏结束后防止再次落子
    if running:
        if t:
            color = 1
            text('AI落子', screen, 54)
        else:
            color = 2
            text('人类落子', screen, 54)
    i = 0
    j = 0

    for event in pygame.event.get():
        #从队列中获取事件
        # 点击x则关闭窗口
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # 点击窗口里面类容则完成相应指令
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                x, y = event.pos[0], event.pos[1]
                for i in range(9):
                   for j in range(9):
                        # 点击棋盘相应位置
                        if i * 89 + 3 + 20 < x < i * 89 + 3 + 109 and j * 89 + 3 + 20 < y < j * 89 + 3 + 109 and not \
                        map[i][j] and running:
                            # 在棋盘相应位置落相应颜色棋子
                            Draw_a_chessman(i + 1, j + 1, screen, 2)
                            map[i][j] = 2

                            w = i
                            h = 7-j
                            # 将map存入maps
                            map3 = copy.deepcopy(map)
                            maps.append(map3)



                            return [h, w]

                # 点击‘退出游戏’，退出游戏
                if 900 < x < 1100 and 650 < y < 750:
                    pygame.quit()
                    sys.exit()


        clock.tick(60)



def AI_step(x,y):
    """
    x,y 为AI返回的要走的坐标
    这个函数将x,y这个位置落上AI的棋子
    :return:
    """
    i = y
    j = 7-x

    Draw_a_chessman(i + 1, j +1, screen, 1)
    map[i][j] = 1

def Human_win():
    text('人类胜利', screen, 40)

def AI_win():
    text('AI胜利', screen, 40)

def TIE():
    text('死棋', screen, 40)


if __name__ == "__main__":
    try:
        init()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()

