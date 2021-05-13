'''
IDE에 내릴 명령은 여기에 작성해 주세요.
IDE 종류와 명령 이름만 주면 명령을 찾아서 수행할 수 있게 작성해 주시기 바랍니다.
매크로 명령도 마찬가지입니다. ADT를 미리 적어두겠습니다. execute 빼고 매개변수는 자유롭게 구성하시면 됩니다.
'''

# 수행부
def loadSet():  # 유저가 구성한 매크로 불러오기 코드
    pass

from time import sleep

def saveSet():  # 유저가 구성한 매크로 저장 코드
    pass

def stall(time):    # 시간 지연 수행

    sleep(time)


def palette(COM_name):  # 팔레트 명령 수행

    if IDE == '비주얼 스튜디오 코드':
        pag.keyDown('ctrl')
        pag.keyDown('shift')
        pag.press('p')
        pag.keyUp('shift')
        pag.keyUp('ctrl')
        sleep(0.1)
        pag.write(COM_name)
        pag.press('enter')
          
    if IDE == '비주얼 스튜디오':
        pag.keyDown('ctrl')
        pag.keyDown('alt')
        pag.press('a')
        pag.keyUp('alt')
        pag.keyUp('ctrl')
        sleep(0.1)
        pag.write(COM_name)
        pag.press('enter')
            
    if IDE == '이클립스':
        pag.keyDown('ctrl')
        pag.keyDown('alt')
        pag.keyDown('shift')
        pag.press('t')
        pag.keyUp('shift')
        pag.keyUp('alt')
        pag.keyUp('ctrl')
        pag.press('enter')
        sleep(0.1)
        pag.write(COM_name)
        pag.press('enter')
            
    if IDE == 'PyCharm':
        pag.keyDown('ctrl')
        pag.keyDown('shift')
        pag.press('a')
        pag.keyUp('shift')
        pag.keyUp('ctrl')
        sleep(0.1)
        pag.write(COM_name)
        pag.press('enter')

def opn(IDE_name, COM_name):     # 클래스/함수/파일 열기


    vscode_command = {'파일열기':['ctrl','p'],'현재파일닫기':['ctrl','f4'],'특정행이동':['ctrl','g'],'모든파일닫기':['ctrl','k','w']}
    vs_command = {'파일열기':['ctrl','o'],'현재파일닫기':['ctrl','f4'],'특정행이동':['ctrl','g'],'모든파일닫기':['alt','w','l']}
    eclipse_command = {'파일열기':['ctrl','shift','r'],'현재파일닫기':['ctrl','f4'],'특정행이동':['ctrl','l'],'모든파일닫기':['ctrl','shift','f4']}
    pycharm_command = {'파일열기':['ctrl','shift','n'],'현재파일닫기':['ctrl','f4'],'특정행이동':['ctrl','g'],'모든파일닫기':[]}
    
    if IDE_name == '비주얼 스튜디오 코드':
        for keyb in vscode_command[COM_name]:
            pag.keyDown(keyb)
            
        for keyb in reversed(vscode_command[COM_name]):
            pag.keyUp(keyb)
          
    elif IDE_name == '비주얼 스튜디오':
        for keyb in vs_command[COM_name]:
            pag.keyDown(keyb)
            
        for keyb in reversed(vs_command[COM_name]):
            pag.keyUp(keyb)
            
    elif IDE_name == '이클립스':
        for keyb in eclipse_command[COM_name]:
            pag.keyDown(keyb)
            
        for keyb in reversed(eclipse_command[COM_name]):
            pag.keyUp(keyb)
            
    elif IDE_name == 'PyCharm':
        for keyb in pycharm_command[COM_name]:
            pag.keyDown(keyb)
            
        for keyb in reversed(pycharm_command[COM_name]):
            pag.keyUp(keyb)
    

press_key = []

IDE = 'IDE 명'

# keyboard 모듈: 키 누르는 매크로
# pag 모듈: 텍스트 입력용

def keyIn(Inputkey):    # 키 입력
    pag.keyDown(Inputkey)
    press_key.append(Inputkey)
            
def keyRel():   # 키 떼기
    for k in press_key:
        pag.keyUp(k)
    press_key.clear()

def execute(name):
    # 이름으로 명령 찾아서 수행. 명령은 kCommands 안에 있고 반복문을 이용해 기초 명령들을 호출하면 될 것 같습니다.
    # 참고로 명령, 보기, 탐색은 여기서 수행하는 것이 아니며, 메인 측에서 IDE를 활성화시킨 상태에서 이것을 호출할 것입니다.
    com=kCommands[name]

    for comm in com:
        if comm[0] == '키 입력':
            keyIn(comm[1])
        else:
            keyRel()
            if comm=='시간 지연':
                stall(com[com.index(comm)+1])
            elif comm=='팔레트':
                palette(com[com.index(comm)+1])
            elif comm=='명령':
                execute(com[com.index(comm)+1])
    keyRel()

# 선별부
import os, sys
import pyautogui as pag
sys.path.append(os.path.abspath('..'))
import procs.phonetic as ph

kCommands=dict()

def matchK(inp):
    inp=normalize(inp)
    key=list(kCommands.keys())
    key2=['명령', '보기', '탐색']
    key.extend(key2)
    ret=ph.arrange_k(inp, key)
    return ret


def normalize(inp): # 공백만 제거
    return ''.join(inp.split())



kCommands.update({
    '모두접기':[('팔레트','fold all')],
    '파일열기':[('키 입력', 'ctrl'), ('키 입력', 'p')],

})

