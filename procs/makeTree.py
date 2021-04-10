import os, time

ext=dict()
modTimes=dict() # 파일 이름: [기록된 수정 시각, 타임스탬프]

STAMP=0

struct=[]

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

def gc():   # 파일이 제거된 경우에 대비하여 modTimes와 struct에서 해당 내용을 없애는 함수. struct에서 먼저 제거하고 modTimes에서 제거
    for f in modTimes:
        if modTimes[f][1]!=STAMP:
            # struct에서 제거
            # modTimes에서 제거
            pass

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
                    if modTimes[f][0]!=mtime:
                        modTimes[f][0]=mtime
                        # 해당 파일에 대하여 구조 업데이트하는 코드(ext[fext]가 해당 함수)
                        ext[fext](f)
                    modTimes[f][1]=STAMP                        
                except KeyError:
                    modTimes[f][0]=mtime
                    modTimes[f][1]=STAMP
                    ext[fext](f)
    gc()
    '''재귀호출이 있으므로 이런 코드 넣으면 안 됨!!
    time.sleep(10)
    scanDir(top)
    '''

ext.update({
    'py': pyFillTree,
    'c': cFillTree,
    'cpp': cppFillTree,
    'java': javaFillTree,
})