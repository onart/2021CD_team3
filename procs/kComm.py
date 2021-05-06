'''
IDE에 내릴 명령은 여기에 작성해 주세요.
IDE 종류와 명령 이름만 주면 명령을 찾아서 수행할 수 있게 작성해 주시기 바랍니다.
매크로 명령도 마찬가지입니다. ADT를 미리 적어두겠습니다. execute 빼고 매개변수는 자유롭게 구성하시면 됩니다.
'''

# 수행부
def loadSet():  # 유저가 구성한 매크로 불러오기 코드
    pass

def saveSet():  # 유저가 구성한 매크로 저장 코드
    pass

def stall():    # 시간 지연 수행
    pass

def palette():  # 팔레트 명령 수행
    pass

def call():     # 다른 명령어
    pass

def keyIn():    # 키 입력
    pass

def execute(name):  
    # 이름으로 명령 찾아서 수행. 명령은 kCommands 안에 있고 반복문을 이용해 기초 명령들을 호출하면 될 것 같습니다.
    # 참고로 명령, 보기, 탐색은 여기서 수행하는 것이 아니며, 메인 측에서 IDE를 활성화시킨 상태에서 이것을 호출할 것입니다.
    com=kCommands[name]
    pass

# 선별부
import os, sys
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

})