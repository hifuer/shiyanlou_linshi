# -*-coding:utf-8 -*-
"""
2048 游戏
2019.12.21
"""
import curses #curses 用来在终端上显示图形界面
from random import randrange, choice # random  生成随机数
from collections import defaultdict  #collections 提供字典 defaultdict .可以指定key值不存在时，vlaue 的默认值

#主逻辑
#输入见W(上)，A(左），S（下），D（右），R（重置），Q（退出）
#ord()一个字符为参数，返回ASCII数值，与捕捉见关联
letter_codes=[ord(ch) for ch in 'WASDRQwasdrq']
actions=['Up','Left','Down','Right','Restart','Exit']
#关联输入与行为关联：
actions_dict=dict(zip(letter_codes,actions*2))

#2处理用户有效输入
def get_user_action(keyboard):
    char='N'
    while char not in actions_dict:
        #返回按下的ASSCII 码值
        char=keyboard.getch()
    #返回输入见行为
    return actions_dict[char]

###矩阵转置
def transpose(field):
    return [list(row) for row in zip(*field)]
#矩阵逆转（不是逆矩阵）
def invert(field):
    return [row[::-1] for row in field]

#创建棋盘 4×4  ～2048 指定高宽及游戏胜利条件
class GameField(object):
    def __init__(self, height=4, width=4, win=2048):
        self.height=height
        self.width=width
        self.win_value=win  #过关分数
        self.scroe=0 #当前分
        self.highscore=0  #最高分
        self.reset()  #棋盘重置
        
    def reset(self):
        #更新分数
        if self.score > self.highscore:
            self.highscore=self.score
        self.scre=0
        #初始化游戏界面
        self.field= [[0 for i in range(self.width)] for j in range(self.heigh)]
        self.spawn()
        self.spawn()
        
    def move(self,direction):
        #走一步 可通过 转置 逆转， 直接从左移得到其余三个方向的移动曹植
        def move_row_left(row):
            def tighten(row):
                '''把零散的非零单元挤到一块'''
                #非零元素加入新列表
                new_row=[i for i in row if i != 0]
                #按照原列表的大小，给新列表后补零
                new_row += [0 for i in range(len(row)  - len(new_row))]
                return new_row

            def merage(row):
                """对邻近元素进行合并"""
                pair=False
                new_row=[]
                for i in range(len(row)):
                    if pair:
                        #合并后，加入乘 2后的元素0元素后面
                        new_row.append(2 * row[i])
                        #更新分数
                        self.score += 2 * row[i]
                        pair=False
                    else:
                        #判断邻近元素是否能合并
                        if i + 1 < len(row) and row[i] == row[i +1]:
                            pair=True
                            #可以合并时，新列表加入元素 0
                            new_row.append(0)
                        else:
                            #不能合并，新列表中加入该元素
                            new_row.append(row[i])
                    #断言合并后不会改变行列大小，否则报错
                    assert len(new_row) == len(row)
                    return new_row
                #先挤到一块再合并再挤到一块
                return tighten(merage(tighten(row)))
        #创建 moves字典，把不同的棋盘操作作为不同的 Key ,对应不同的方法函数
        moves={}
        moves['Left'] = lambda field: [move_row_left(row) for row in field]
        moves['Right']= lambda field: invert(moves['Left'](invert(field)))
        moves['Up'] = lambda field: transpose(moves['Left'](transpose(field)))
        moves['Down']=lambda field: transpose(moves['Right'](transpose(field)))
        #判断棋盘操作是否存在且可行
        if direction in moves:
            if self.move_is_possible(direction):
                self.field=moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False

    #判断输赢
    def is_win(self):
        #任意一个位置的数大于设定的win值时，游戏胜利
        return any(any(i >=self.win_value for i in row) for row in self.field)

    def is_gameover(self):
        #无法移动和合并时，游戏失败
        return not any(self.move_is_possible(move) for move in actions)

    def draw(self,screen):
        help_string1='(W)Up (S)Down (A)Left (D)Right '
        help_string2='         (R)Restart  (Q)Exit'
        gameover_string='       GAME OVER'
        win_string='         YOU WIN! '

        #绘制函数
        def cast(string):
            #addstr() 将传入内容展示到终端
            screen.addstr(string + '\n')

        #划线水平
        def draw_hor_separator():
            line= '+' + ('+------' * self.width + '+')[1:]
            separator=defaultdict(lambda:line)
            if not hasattr(draw_hor_separator,"countter"):
                dram_hor_separator.counter=0
            cast(separator[draw_hor_separator.counter])
            draw_hor_separator.counter +=1
            #cast(line)

        #竖立线
        def draw_row(row):
            cast(''.join('|{: ^5} '.format(num) if num > 0 else '|      ' for num in row) + '|')

        #清屏
        screen.clear()
        #分数 最高分
        cast('SCORE: ' + str(self.score))
        if 0 !=self.highscore:
            cast('HIGHSCORE: ' + str(self.highscore))

        #边框
        for row in self.field:
            draw_how_separator()
            draw_row(row)
        draw_hor_separator()

        #提示文字
        if self.is_win():
            cast(win_string)
        else:
            if self.is_gameover():
                cast(gameover_string)
            else:
                cast(help_string1)
        cast(help_string2)

    #随机生成2或4
    def spawn(self):
        #从100中取出一个随机数，如果大于89，new_element等于4，否则等于2
        new_element= 4 if randrange(100) > 89 else 2
        #得到一个随机空白的元组坐标
        (i,j) =choice([(i,j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0])
        self.field[i][j] = new_element
    #判断能否移动
    def move_is_possible(self,direction):
        '''传入要移动的方向
        判断能否向这个方向移动
        '''
        def row_is_left_movable(row):
            '''判断一行里面能否有元素进行左移或合并
            '''
            def change(i):
                #当左边有空位（0），右边有数字时，可以向左移动
                if row[i] == 0 and row[i + 1] != 0:
                    return True
                if row[i] != 0 and row[i + 1] ==row[i]:
                    return True
                return False
            return any(change(i) for i in range(len(row)-1))
        #检查能否移动（合并也可以看做是在移动）
        check={}
        #判断矩阵每一行有没有可以移动的元素
        check['Left'] = lambda field: any(row_is_left_movable(row) for row in field)
        #判断矩阵每一行有没有可以右移的元素。只判断，变化后，不用再还原
        check['Right'] =lambda field: check['Left'](invert(field))
        check['Up'] = lambda field: check['Left'](transpose(field))
        check['Down']=lambda field:check['Right'](transpose(field))

        #如果 direction 是”左右上下“ 即字典 check 中存在的操作，就执行它对应的函数
        if direction in check:
            #传入矩阵，执行对应函数
            return check[direction](self.field)
        else:
            return False


def main(stdscr):
    def init():
        """
        初始化游戏键盘
        """
        #重置游戏
        game_field.reset()
        return 'Game'

    def not_game(state):
        """展示游戏结束界面。
        读取用户输入得到 action,判断时重启游戏还是结束游戏
        """
        #根据状态画出游戏的界面
        game_field.draw(stdscr)
        #用户输入action ，判读游戏重启或结束
        action=get_user_action(stdscr)
        #defaultdict参数是 callable类型，需要传一个函数
        responses=defaultdict(lambda: state)
        #在字典中新建两个键值对
        responses['Restart'], responses['Exit'] = 'Init','Exit'
        return responses[action]
    def game():
        """画面当前棋盘状态
        读取用户输入得到 action
        """
        #根据状态画出游戏的界面
        game_field.draw(stdscr)
        #用户输入action ，判读游戏重启或结束
        action=get_user_action(stdscr)

        if action == 'Restart':
            return 'Init'
        if action == 'Exit':
            return 'Eixt'
        if  game_field.move(action):# move successful
            if game_field.is_win():
                return 'Win'
            if game_field.is_gameover():
                return 'Gameover'
    return 'Game'

    #状态机循环
    static_actions = {
            'Init': init,
            'Win': lambda: no_game('Win'),
            'Gameover': lambda: not_game('Gameover'),
            'Game': game
    }

    #配颜色值
    curses.use_default_colors()
    #实例化获胜条件 32
    game_field=GameField(win=32)

    state = 'Init'

    #状态机开始循环
    while state !='Exit':
        state = state_acctions[state]()

curses.wrapper(main)




















