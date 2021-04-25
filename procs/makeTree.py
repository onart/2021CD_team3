import os, time, re
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
    lines = prog.readlines()
    ign=[]  # 무시해야 할 것: 문자/문자열 리터럴 내, 주석 내. "", //, /**/ 은 먼저 나오는 쪽이 이김
    lineNo=0
    cur=0   # 0: 보통, 1: 일반주석, 2: 문자열리터럴

    # 무시해야 할 부분 추가
    for line in lines:
        lineNo+=1
        i=0
        if line.find('"')==-1 and line.find('//')==-1 and line.find("'")==-1 and line.find('/*')==-1 and line.find('*/')==-1:
            continue
        while i<len(line):
            ch=line[i]
            if ch in ('"', '/', "'", '*'):
                if cur==0:
                    if ch=='"':
                        cur=2
                        ign.append((lineNo, i+1))
                    elif ch=='/':
                        try:
                            if line[i+1]=='*':
                                cur=1
                                ign.append((lineNo, i+1))
                                i+=1
                            elif line[i+1]=='/':
                                ign.append((lineNo, i+1))
                                ign.append((-lineNo, len(line)))
                                break
                        except IndexError:
                            pass
                    elif ch=="'":
                        ign.append((lineNo, i+1))
                        i=line.find("'", i+1)+1
                        ign.append((-lineNo, i))
                elif cur==1:
                    ed=line.find('*/', i)
                    if ed==-1:
                        break
                    else:
                        ign.append((-lineNo, ed+1))
                        i=ed+2
                        cur=0
                elif cur==2:
                    ed=line.find('"', i)
                    if ed==-1:
                        break
                    else:
                        if ed==0 or line[ed-1]!='\\':
                            ign.append((-lineNo, ed+1))
                            cur=0
                            i=ed+1
            i+=1

    # 전역 범위의 중괄호 위치 탐색
    iign=iter(ign)
    try:
        ran=(next(iign), next(iign))
    except StopIteration:
        ran=None
    depth=0
    att=False
    i=0
    j=0
    curly=[]
    while i < len(lines):
        if ran is not None and i+1 == ran[0][0]:
            att=True
        else:
            att=False
        while True:
            if att and j+1 == ran[0][1]:
                i=abs(ran[1][0])-1
                j=ran[1][1]-1
                try:
                    ran=(next(iign), next(iign))
                except StopIteration:
                    ran=None
                if ran is not None and i+1 == ran[0][0]:
                    att=True
                else:
                    att=False
            if j>=len(lines[i]):
                j=0
                break
            if lines[i][j]=='{':
                depth+=1
                if depth==1:
                    curly.append((i+1, j+1))
            elif lines[i][j]=='}':
                depth-=1
                if depth==0:
                    curly.append((-i-1, j+1))
            j+=1
            if j>=len(lines[i]):
                j=0
                break
        i+=1
    # 각 중괄호 시작점에서 거꾸로 앞 토큰 찾기: 
    # 앞에 바로 )가 나오는 경우, 그 앞의 ( 앞의 토큰이 함수 이름, 그보다 앞 토큰 시작점이 함수 시작점
    # 바로 앞이 )가 아닌 경우, 그 토큰을 그대로 사용
    # 바로 앞 토큰이 struct/enum/union인 경우, } 뒤를 보는데 바로 뒤가 ;인 경우 그냥 무시
    for i in range(len(curly)):
        if curly[i][0]<0:
            continue
        # {의 위치
        lineNo=curly[i][0]
        colNo=curly[i][1]
        det=0   # 0: 초기, 1: ) 만남, 2: ( 만남, 3: ( 앞 토큰 만남, 4: ( 앞 토큰 완료, 5: ( 앞앞 토큰 만남, 6: ) 만나지 않고 다른 걸 만남, 
        while True:
            colNo-=1
            if colNo<0:
                lineNo-=1
                colNo=len(lines[lineNo-1])
            targc=lines[lineNo-1][colNo-1]
            if det==0:
                if targc not in '\n\t ':
                    if targc==')':
                        det=1
                        param=''
                    else:
                        det=6
                        tok1=targc
            elif det==1:
                if targc != '(':
                    if targc != '\n':
                        if targc=='\t':
                            param=' '+param
                        else:
                            param=targc+param
                else:
                    det=2
            elif det==2:
                if targc not in '\n\t ':
                    det=3
                    tok1=targc
            elif det==3:
                if targc not in '\n\t ':
                    tok1=targc+tok1
                else:
                    det=4
            elif det==4:
                if targc not in '\n\t ':
                    det=5
                    tok2=targc
            elif det==5:
                if targc not in '\n\t ':
                    tok2=targc+tok2
                else:
                    try:
                        functs[tok1].append([fname, curly[i], curly[i+1], '', param])   # curly[i+1]는 끝 위치가 맞지만 curly[i]는 시작 위치가 아니니 수정 예정
                    except KeyError:
                        functs[tok1]=[[fname, curly[i], curly[i+1], '', param]]
                    break
            elif det==6:
                break
    print(functs)
    # 현재 sloc 20000 가량의 파일 대상으로, 0.2초 가량 소모
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
