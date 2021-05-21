from time import sleep
from procs.makeTree import rel2abs

# 수행부
def loadSet():  # 유저가 구성한 매크로 불러오기 코드
    f = open("macro.txt", 'r')
    lines = f.readlines()
    for line in lines:
        spite_line = line.split()
        list_make = []
        for i in range(len(spite_line)):
            if i == 0:
                keyv = spite_line[0]
            elif spite_line[i] == '키':
                if spite_line[i+1] == '입력':
                    list_make.append(['키 입력',spite_line[i+2]])

            elif spite_line[i] == '시간':
                if spite_line[i+1] == '지연':
                    list_make.append(['시간 지연',spite_line[i+2]])

            elif spite_line[i] == '팔레트':
                list_make.append(['팔레트',spite_line[i+1]])

            elif spite_line[i] == '명령':
                list_make.append(['명령',spite_line[i+1]])

        customCommands[keyv] = list_make


                    
    f.close()
    pass

def saveSet():  # 유저가 구성한 매크로 저장 코드
    f = open("macro.txt", 'w')
    for i in customCommands.keys():
        f.write(i+" ")
        for j in customCommands.get(i):
            f.write(j[0]+" "+j[1]+" ")
        f.write("\n")

    f.close()
    pass

def stall(time):    # 시간 지연 수행

    sleep(time)

def palette(COM_name):  # 팔레트 명령 수행
    temp=pyperclip.paste()
    pyperclip.copy(COM_name)
    if IDE == 0:
        pag.hotkey('ctrl', 'p')
        sleep(0.05)
        pag.write('>')
        pag.hotkey('ctrl','v')
        pag.press('enter')

    elif IDE == 1:
        pag.hotkey('ctrl','alt','a')
        sleep(0.05)
        pag.hotkey('ctrl','v')
        pag.press('enter')

    elif IDE == 2:
        pag.hotkey('ctrl','3')
        sleep(0.05)
        pag.hotkey('ctrl','v')
        pag.press('enter')

    elif IDE == 3:
        pag.hotkey('ctrl','shift','a')
        sleep(0.05)
        pag.hotkey('ctrl','v')
        pag.press('enter')
    pyperclip.copy(temp)

def opn(sel4):     # 클래스/함수/파일 열기, 인수: main의 sel4

    if len(sel4)==1:    # 인덱스 0에 파일 이름
        openRoutine(sel4[0])
        return
    else:               # 인덱스 1에 파일 이름, 인덱스 2에 시작 위치
        openRoutine(sel4[1])
        lineRoutine(sel4[2][0])

    
def openRoutine(name):
    if IDE==0:
        pag.hotkey('ctrl','p')
        pyperclip.copy(name)
        sleep(0.05)
        pag.hotkey('ctrl','v')
        pag.press('enter')
    elif IDE==1:
        pag.hotkey('ctrl','o')
        pyperclip.copy(rel2abs[name])
        sleep(0.05)
        pag.hotkey('ctrl','v')
        pag.press('enter')
    elif IDE==2:
        palette('open file')
        sleep(0.05)
        pyperclip.copy(rel2abs[name])
        pag.hotkey('ctrl','v')
        pag.press('enter')
    elif IDE==3:
        pag.hotkey('ctrl','shift','n')
        pyperclip.copy(name)
        sleep(0.05)
        pag.hotkey('ctrl','v')
        pag.press('enter')

def lineRoutine(no):
    if IDE==2:
        pag.hotkey('ctrl','l')
    else:
        pag.hotkey('ctrl','g')
    sleep(0.05)
    pag.write(str(no))
    pag.press('enter')

press_key = []
callStack=[]

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
        com=builtInCommands[name][IDE]
    elif name in customCommands:
        com=customCommands[name]
    else:   # '명령' 이후 없는 명령 등장
        return

    if name not in callStack:
        callStack.append(name)
    else:
        return

    for comm in com:
        if comm[0] == '키 입력':
            keyIn(comm[1])
        else:
            keyRel()
            if comm[0]=='시간 지연':
                stall(float(comm[1]))
            elif comm[0]=='팔레트':
                palette(comm[1])
            elif comm[0]=='명령':
                execute(comm[1])
    keyRel()
    callStack.pop()
    
    string_macro = ''
    if name in builtInCommands: 
        for j in builtInCommands[name][IDE]:
                string_macro = string_macro + j[1] + "+"
        return string_macro[:-1]
        

# 선별부
import os, sys
import pyautogui as pag
sys.path.append(os.path.abspath('..'))
import procs.phonetic as ph
import pyperclip

builtInCommands={
    '코드위로이동':((('키 입력','alt'),('키 입력','up')),(('키 입력','alt'),('키 입력','up')),(('키 입력','alt'),('키 입력','up')),(('키 입력','alt'),('키 입력','up'))),
    '코드아래로이동':((('키 입력','alt'),('키 입력','down')),(('키 입력','alt'),('키 입력','down')),(('키 입력','alt'),('키 입력','down')),(('키 입력','alt'),('키 입력','down'))),
    '중단점':((('키 입력','f9'),),(('키 입력','f9'),),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','b')),(('키 입력','ctrl'),('키 입력','f8'),)),
    '탐색기':((('키 입력','ctrl'),('키 입력','b')),(('키 입력','ctrl'),('키 입력','alt'),('키 입력','l')),(('키 입력','alt'),('키 입력','shift'),('키 입력','p'),('키 입력','q')),(('키 입력','ctrl'),('키 입력','alt'),('키 입력','l'))),
    '접기':((('키 입력','ctrl'),('키 입력','shift'),('키 입력','[')),(('키 입력','ctrl'),('키 입력','M'),('키 입력','M')),(('키 입력','ctrl'),('키 입력','+')),()),
    '펴기':((('키 입력','ctrl'),('키 입력','shift'),('키 입력',']')),(('키 입력','ctrl'),('키 입력','M'),('키 입력','M')),(('키 입력','ctrl'),('키 입력','+')),()),
    '선택주석':((('키 입력','shift'),('키 입력','alt'),('키 입력','a')),(('키 입력','ctrl'),('키 입력','k'),('키 입력','c')),(('키 입력','ctrl'),('키 입력','/')),(('키 입력','ctrl'),('키 입력','/'))),
    '주석':((('키 입력','ctrl'),('키 입력','/')),(()),(('키 입력','ctrl'),('키 입력','/')),(('키 입력','ctrl'),('키 입력','/'))),
    '자동완성':((('키 입력','ctrl'),('키 입력','space')),(('키 입력','ctrl'),('키 입력','space')),(('키 입력','ctrl'),('키 입력','space')),(('키 입력','ctrl'),('키 입력','space'))),
    '이전위치':((('키 입력','alt'),('키 입력','left')),(('키 입력','ctrl'),('키 입력','-')),(('키 입력','alt'),('키 입력','left')),(())),
    '오류위치':((('키 입력','f8')),(()),(('키 입력','ctrl'),('키 입력','.')),(())),
    '다시열기':((('키 입력','ctrl'),('키 입력','shift'),('키 입력','t')),(()),(('키 입력','alt'),('키 입력','left')),(())),
    '모든참조':((('키 입력','shift'),('키 입력','f12')),(('키 입력','shift'),('키 입력','f12')),(('키 입력','ctrl'),('키 입력','alt'),('키 입력','h')),(('키 입력','alt'),('키 입력','f7'))),
    '리팩터링':((('키 입력', 'ctrl'), ('키 입력', 'shift'),('키 입력','r')),(('키 입력','alt'),('키 입력','enter')),(('키 입력','alt'),('키 입력','shift'),('키 입력','t')),(('키 입력','shift'),('키 입력','f6'))),
    '모두접기':((('키 입력','ctrl'),('키 입력','k'),('키 입력','0')),(('키 입력','ctrl'),('키 입력','m'),('키 입력','o')),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','/')),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','-'))),
    '모두펴기':((('키 입력','ctrl'),('키 입력','k'),('키 입력','j')),(('키 입력','ctrl'),('키 입력','m'),('키 입력','l')),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','*')),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','+'))),
    '자동정렬':((()),(('키 입력','ctrl'),('키 입력','k'),('키 입력','f')),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','f')),(('키 입력','ctrl'),('키 입력','alt'),('키 입력','i'))),
    '파일열기':((('키 입력', 'ctrl'), ('키 입력', 'p')),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','t')),(()),(('키 입력','ctrl'),('키 입력','shift'),('키 입력','n'))),
    '새파일':((('키 입력','ctrl'),('키 입력','n')),(('키 입력','ctrl'),('키 입력','n')),(('키 입력','ctrl'),('키 입력','n')),(('키 입력','alt'),('키 입력','insert'))),
    '이름변경':((('키 입력','f2'),),(('키 입력','ctrl'),('키 입력','r')),(('키 입력','alt'),('키 입력','shift'),('키 입력','r')),(('키 입력','shift'),('키 입력','f6'))),
    '정의로이동':((('키 입력','f12'),),(('키 입력','f12'),),(('키 입력','f3'),),(())),
    '정의보기':((('키 입력','alt'),('키 입력','f12')),(('키 입력','alt'),('키 입력','f12')),(('키 입력','f3')),(())),
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
    key.sort(key=lambda x: len(x))
    key.sort(key=lambda x: len(x)!=len(inp))
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

