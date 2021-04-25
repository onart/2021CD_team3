import os, time
import phonetic

ext=dict()
modTimes=dict() # 파일 이름: [기록된 수정 시각, 타임스탬프]

STAMP=0

# 템플릿: <...>까지 이름에 포함, 타입이 T 같이 돼 있는 것은 그대로 적음

# 클래스 ('이름', 파일, 시작 위치(행/열), 끝 위치(행/열), )
classes=[]
# 함수 {'이름': [[파일, 시작 위치(행/열), 끝 위치(행/열), 스코프(전역 or 클래스이름), 매개변수], [파일, 시작 위치(행/열), 끝 위치(행/열), 스코프(전역 or 클래스이름), 매개변수]]}
functs=dict()
# 단어풀(set)
POOL=set()

def pyFillTree(fname):
    prog=open(fname, 'r')
    prog.close()

def cFillTree(fname):
    prog=open(fname, 'r')
    prog.close()

def cppFillTree(fname):
    prog=open(fname, 'r')
    prog.close()

def javaFillTree(fname):
    prog=open(fname, 'r')
    prog.close()

def gc():   # 제거된 파일에 대하여 기존 정보를 제거
    global classes, functs, modTimes
    rmm=[] # 데이터에서 제거할 파일
    for f in modTimes:
        if modTimes[f][1]!=STAMP:
            rmm.append(f)
            classes=[x for x in classes if x[1] != f]
            for fu in functs:
                functs[fu]=[x for x in functs if x[0] != f]
            functs={x:functs[x] for x in functs if len(functs[x]) != 0}
    for f in rmm:
        modTimes.pop(f)

def forMod(fname):  # 수정된 파일에 대하여 기존 정보를 제거
    global classes, functs
    classes=[x for x in classes if x[1] != fname]
    for fu in functs:
        functs[fu]=[x for x in functs if x[0] != fname]

def poolUP():
    global POOL, classes, modTimes, functs
    POOL.clear()
    for fi in modTimes:
        POOL.add(fi)
    for cl in classes:
        POOL.add(cl[0])
    for fu in functs:
        POOL.add(fu)

def scanDir(top):   # 입력값: 시작 시 설정한 top 디렉토리의 절대 경로. 기본 10초당 1회 호출, 어떤 음성이든 입력 시 즉시 호출 후 음성처리
    STAMP=time.time()
    cont=os.listdir(top)
    for c in cont:
        f=os.path.join(top, c)
        if os.path.isdir(f):
            scanDir(f)
        elif os.path.isfile(f):
            fext=os.path.splitext(f)[1]
            if fext in ext: # 정해진 확장자 검사
                try:
                    mtime=os.path.getmtime(f)
                    if modTimes[f][0]!=mtime:   # 기존 파일이 수정됨
                        modTimes[f][0]=mtime
                        # 해당 파일에 대하여 구조 업데이트하는 코드(ext[fext]가 해당 함수)
                        forMod(f)
                        ext[fext](f)
                    modTimes[f][1]=STAMP                        
                except KeyError:                # 새 파일이 생성됨
                    modTimes[f][0]=mtime
                    modTimes[f][1]=STAMP
                    ext[fext](f)

def scanNgc(top):   # 음성 입력 시 스레드 중지 후 재시작
    while True:
        scanDir(top)
        gc()
        poolUP()
        # 업데이트 완료 신호
        time.sleep(10)

ext.update({
    'py': pyFillTree,
    'c': cFillTree,
    'cpp': cppFillTree,
    'java': javaFillTree,
    'h': cppFillTree,
})