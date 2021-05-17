'''
IDE에 내릴 명령은 여기에 작성해 주세요.
IDE 종류와 명령 이름만 주면 명령을 찾아서 수행할 수 있게 작성해 주시기 바랍니다.
매크로 명령도 마찬가지입니다. ADT를 미리 적어두겠습니다. execute 빼고 매개변수는 자유롭게 구성하시면 됩니다.
'''

# 수행부
def loadSet():  # 유저가 구성한 매크로 불러오기 코드
    pass

from time import sleep
from procs.makeTree import rel2abs

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

    elif IDE == '비주얼 스튜디오':
        pag.keyDown('ctrl')
        pag.keyDown('alt')
        pag.press('a')
        pag.keyUp('alt')
        pag.keyUp('ctrl')
        sleep(0.1)
        pag.write(COM_name)
        pag.press('enter')

    elif IDE == '이클립스':
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

    elif IDE == 'PyCharm':
        pag.keyDown('ctrl')
        pag.keyDown('shift')
        pag.press('a')
        pag.keyUp('shift')
        pag.keyUp('ctrl')
        sleep(0.1)
        pag.write(COM_name)
        pag.press('enter')

def opn(sel4):     # 클래스/함수/파일 열기, 인수: main의 sel4

    if len(sel4)==1:    # 인덱스 0에 파일 이름
        openRoutine(sel4[0])
        return
    else:               # 인덱스 1에 파일 이름, 인덱스 2에 시작 위치
        openRoutine(sel4[1])
        lineRoutine(sel4[2][0])

    
def openRoutine(name):
    if IDE==0:
        pag.keyDown('ctrl')
        pag.press('p')
        pag.keyUp('ctrl')
        sleep(0.1)
        pag.write(name)
        pag.press('enter')
    elif IDE==1:
        pag.keyDown('ctrl')
        pag.press('o')
        pag.keyUp('ctrl')
        sleep(0.1)
        pag.write(rel2abs[name])
        pag.press('enter')
    elif IDE==2:
        palette('open file')
        pag.write(rel2abs[name])
        pag.press('enter')
    elif IDE==3:
        pag.keyDown('ctrl')
        pag.keyDown('shift')
        pag.press('n')
        pag.keyUp('shift')
        pag.keyUp('ctrl')
        sleep(0.1)
        pag.write(name)
        pag.press('enter')

def lineRoutine(no):
    if IDE==2:
        pag.keyDown('ctrl')
        pag.press('l')
        pag.keyUp('ctrl')
    else:
        pag.keyDown('ctrl')
        pag.press('g')
        pag.keyUp('ctrl')
    sleep(0.03)
    pag.write(str(no))
    pag.press('enter')

press_key = []

IDE = -1

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
    if name in builtInCommands:
        com=builtInCommands[name]
    elif name in customCommands:
        com=customCommands[name]
    else:   # '명령' 이후 없는 명령 등장
        return

    for comm in com[IDE]:
        if comm[0] == '키 입력':
            keyIn(comm[1])
        else:
            keyRel()
            if comm[0]=='시간 지연':
                stall(float(comm[1]))
            elif comm[0]=='팔레트':
                palette(comm[1])
            elif comm[0]=='명령':
                if name != comm[1]:
                    execute(comm[1])
    keyRel()

# 선별부
import os, sys
import pyautogui as pag
sys.path.append(os.path.abspath('..'))
import procs.phonetic as ph

builtInCommands={
    '코드위로이동':((('키 입력','alt'),('키 입력','up')),(('키 입력','alt'),('키 입력','up')),(('키 입력','alt'),('키 입력','up')),(('키 입력','alt'),('키 입력','up'))),
    '코드아래로이동':((('키 입력','alt'),('키 입력','down')),(('키 입력','alt'),('키 입력','down')),(('키 입력','alt'),('키 입력','down')),(('키 입력','alt'),('키 입력','down'))),
    '중단점':((('키 입력','f9')),(('키 입력','f9')),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','b')),(('키 입력','ctrl'),('키 입력','f8'))),
    '탐색기':((('키 입력','ctrl'),('키 입력','b')),(('키 입력','ctrl'),('키 입력','alt'),('키 입력','l')),(('키 입력','alt'),('키 입력','shift'),('키 입력','p'),('키 입력','q')),(('키 입력','ctrl'),('키 입력','alt'),('키 입력','l'))),
    '접기':((('키 입력','ctrl'),('키 입력','shift'),('키 입력','[')),(('키 입력','ctrl'),('키 입력','M'),('키 입력','M')),(('키 입력','ctrl'),('키 입력','+')),()),
    '펴기':((('키 입력','ctrl'),('키 입력','shift'),('키 입력',']')),(('키 입력','ctrl'),('키 입력','M'),('키 입력','M')),(('키 입력','ctrl'),('키 입력','+')),()),
    '선택주석':((('키 입력','shift'),('키 입력','alt'),('키 입력','a')),(('키 입력','ctrl'),('키 입력','k'),('키 입력','c')),(('키 입력','ctrl'),('키 입력','/')),(('키 입력','ctrl'),('키 입력','/'))),
    '주석':((('키 입력','ctrl'),('키 입력','/')),(()),(('키 입력','ctrl'),('키 입력','/')),(('키 입력','ctrl'),('키 입력','/'))),
    '자동완성':((('키 입력','ctrl'),('키 입력','space')),(('키 입력','ctrl'),('키 입력','space')),(('키 입력','ctrl'),('키 입력','space')),(('키 입력','ctrl'),('키 입력','space'))),
    '이전위치':((('키 입력','alt'),('키 입력','left')),(('키 입력','ctrl'),('키 입력','-')),(('키 입력','alt'),('키 입력','left')),(())),
    '오류위치':((('키 입력','f8')),(()),(('키 입력','ctrl'),('키 입력','.')),(())),
    '창이동':((('키 입력','ctrl'),('키 입력','pageup')),(()),(('키 입력','ctrl'),('키 입력','f6')),(('키 입력','ctrl'),('키 입력','tab'))),
    '닫은것열기':((('키 입력','ctrl'),('키 입력','shift'),('키 입력','t')),(()),(('키 입력','alt'),('키 입력','left')),(())),
    '모든참조':((('키 입력','shift'),('키 입력','f12')),(('키 입력','shift'),('키 입력','f12')),(('키 입력','ctrl'),('키 입력','alt'),('키 입력','h')),(('키 입력','alt'),('키 입력','f7'))),
    '리팩터링':((('키 입력', 'ctrl'), ('키 입력','r')),(('키 입력','alt'),('키 입력','enter')),(('키 입력','alt'),('키 입력','shift'),('키 입력','t')),(('키 입력','shift'),('키 입력','f6'))),
    '모두접기':((('키 입력','ctrl'),('키 입력','k'),('키 입력','0')),(('키 입력','ctrl'),('키 입력','m'),('키 입력','o')),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','/')),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','-'))),
    '모두펴기':((('키 입력','ctrl'),('키 입력','k'),('키 입력','j')),(('키 입력','ctrl'),('키 입력','m'),('키 입력','l')),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','*')),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','+'))),
    '자동정렬':((()),(('키 입력','ctrl'),('키 입력','k'),('키 입력','f')),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','f')),(('키 입력','ctrl'),('키 입력','alt'),('키 입력','i'))),
    '대문자':((('팔레트', 'transform to up')),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','u')),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','x')),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','u'))),
    '소문자':((('팔레트', 'transform to lo')),(('키 입력','ctrl'),('키 입력','u')),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','x')),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','u'))),
    '파일이동':((()),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','t')),(()),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','n'))),
    '새파일':((('키 입력','ctrl'),('키 입력','n')),(('키 입력','ctrl'),('키 입력','n')),(('키 입력','ctrl'),('키 입력','n')),(('키 입력','alt'),('키 입력','insert'))),
    '라인삭제':((('키 입력', 'ctrl'), ('키 입력', 'shift'),('키 입력', 'k')),(('키 입력', 'ctrl'),('키 입력', 'l')),(('키 입력','ctrl'),('키 입력','d')),(('키 입력','ctrl'),('키 입력','y')))

    #'':((('키 입력',''),('키 입력','')),(('키 입력',''),('키 입력','')),(('키 입력',''),('키 입력','')),(('키 입력',''),('키 입력',''))),
    #'이름': ((vscode),(vs),(eclipse),(pycharm))
}

customCommands=dict()

def matchK(inp):
    inp=normalize(inp)
    key=list(builtInCommands)
    key2=list(customCommands)
    key3=['명령', '보기', '탐색']
    key.extend(key2)
    key.extend(key3)
    key=[normalize(x) for x in key]
    key=[x for x in key if len(x)==len(inp)]    # 음절 수 동일한 것 우선. 단 나머지를 아예 제외시키진 않을 예정
    ret=ph.arrange_k(inp, key)
    return ret


def normalize(inp): # 공백만 제거
    return ''.join(inp.split())

def ideUP(name):
    global IDE
    try:
        IDE=('비주얼 스튜디오 코드','비주얼 스튜디오','이클립스','PyCharm').index(name)
    except ValueError:
        pass



