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

# cpp 예약어
reserved_word_cpp = ["__multiple_inheritance", "__single_inheritance", "__virtual_inheritance",
                 "catch", "class", "const_cast", "delete", "dynamic_cast", "explicit", "export", "false", "friend", "inline", "mutable",
                 "namespace", "new", "operator", "private", "protected", "public", "reinterpret_cast", "static_cast", "template",
                 "this", "throw", "true", "try", "typeid", "typename", "using", "virtual", "wchar_t"
                     ]
# c 예약어
reserved_word_c = ["__asm", "__based", "__cdecl", "__declspec", "__except", "__far", "__fastcall", "__finally", "__fortran",
                   "__huge", "__inline", "__int16", "__int32", "__int64" "__int8", "__interrupt", "__leave", "__loadds"," __near",
                   "__pascal", "__saveregs", "__segment", "__segname", "__self", "__stdcall", "__try", "__uuidof",
                   "auto", "bool", "break", "case", "char", "const", "continue", "default", "defined", "do", "double",
                   "else", "enum", "extern", "float", "for", "goto", "if", "int", "long", "register", "return",
                   "short", "signed", "sizeof", "static", "struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while"
                   ]

def pyFillTree(fname):
    prog=open(fname, 'r', encoding = 'UTF-8')
    code = prog.readlines()
    class_indent_for_scope = {}
    for row, line in enumerate(code):  # 행번호 0부터 시작

        line = line.rstrip()
        line_split = line.split()

        if (line and line[-1] == ':' and line_split[0] == 'class'):

            if (line_split[1][-1] == ':'):
                class_name = line_split[1][:-1]
            else:
                class_name = line_split[1]
            class_start_r = row
            class_start_c = 0
            class_end_r = None
            class_end_c = -1
            for new_row, next in enumerate(code[row + 1:], start=row + 1):
                next_split = next.split()
                if (next_split and next[0] != ' '):
                    class_end_r = new_row - 1
                    break
            classes.append([class_name, fname, [class_start_r, class_end_c], [class_end_r, class_end_c]])
            class_indent_for_scope[line.find('class')] = class_name
        elif (line and line[-1] == ':' and line_split[0] == 'def'):
            fn_name = ''
            fn_para = ''
            check = False
            for i in range(line.find('def') + 3, len(line)):
                if (line[i] != ' ' and line[i] != '(' and check == False):
                    fn_name += line[i]
                elif (line[i] == '('):
                    check = True
                elif (check and line[i] != ')'):
                    fn_para += line[i]
                elif (line[i] == ')'):
                    break
            fn_start_r = row
            fn_start_c = line.find('def')
            fn_end_r = None
            fn_end_c = -1

            for new_row, next in enumerate(code[row + 1:], start=row + 1):
                next_split = next.split()
                if (next_split and next.find(next_split[0]) != fn_start_c + 4):
                    fn_end_r = new_row - 1
                    break
            if (line.find('def') == 0):
                fn_scope = 'global'
            else:
                fn_scope = class_indent_for_scope[line.find('def') - 4]
            functs[fn_name] = functs.get(fn_name, [])
            functs[fn_name].append(
                [fname, [fn_start_r, fn_start_c], [fn_end_r, fn_end_c], fn_scope, fn_para.rstrip().split(',')])

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
        det=0   # 0: 초기, 1: ) 만남, 2: ( 만남, 3: ( 앞 토큰 만남, 4: ( 앞 토큰 완료, 5: ( 앞앞 토큰 만남, 6: ) 만나지 않고 다른 걸 만남(일반 이름, enum, union, struct 중 하나), 
        while True:
            colNo-=1
            if colNo<0:
                lineNo-=1
                if lineNo==0:   # 파일의 처음을 만난 경우, } 또는 ;를 만난 것과 동일 취급
                    if det==4 or det==5:
                        try:
                            functs[tok1].append([fname, stp, curly[i+1], '', ' '.join(param.split())])
                        except KeyError:
                            functs[tok1]=[[fname, stp, curly[i+1], '', ' '.join(param.split())]]
                        finally:
                            break
                    elif det==7:
                        classes.append([tok1, fname, stp, curly[i+1]])
                colNo=len(lines[lineNo-1])
            targc=lines[lineNo-1][colNo-1]
            if det==0:
                if targc not in '\n\t ':
                    if targc==')':
                        det=1
                        param=''
                    elif targc=='=':    # 전역배열
                        break
                    else:
                        det=6
                        tok1=targc
            elif det==1:
                if targc != '(':
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
                    if targc in '};':   # 확인된 문제: 주석 내의 ;를 만나도 종료되므로 의미가 잘림
                        try:
                            functs[tok1].append([fname, stp, curly[i+1], '', ' '.join(param.split())])
                        except KeyError:
                            functs[tok1]=[[fname, stp, curly[i+1], '', ' '.join(param.split())]]
                        finally:
                            break
                    tok2=targc+tok2
                    stp=(lineNo, colNo)
            elif det==6:
                if targc not in '\n\t ':
                    tok1=targc+tok1
                else:
                    tok2=''
                    if tok1 in ('struct', 'enum', 'union'): # 중괄호 이후로 이동해서 이름 찾기, 없을 리는 없지만 없으면 classes에 저장하지 않음
                        det=8
                    else:
                        det=7
            elif det==7:
                if targc not in '\n\t ':
                    if targc in '};': # 
                        classes.append([tok1, fname, stp, curly[i+1]])  # 끝점은 curly[i+1]이 아니니 고칠 것
                        break
                    tok2=targc+tok2
                    stp=(lineNo, colNo)
            elif det==8:
                if targc not in '\n\t ':
                    if targc in '};':
                        lineNo = -curly[i+1][0]
                        colNo = curly[i+1][1]
                        while True:
                            colNo+=1
                            if colNo > len(lines[lineNo-1]):
                                colNo=1
                                lineNo+=1
                                if lineNo > len(lines):
                                    break
                            targc=lines[lineNo-1][colNo-1]
                            if targc != ';':
                                tok2 += targc
                            else:
                                tok2=tok2.strip()
                                if len(tok2)>0:
                                    classes.append([tok2, fname, stp, (lineNo, colNo)])
                                break
                        break
                    tok2=targc+tok2
                    stp=(lineNo, colNo)
                
    # print(classes)
    # 현재 sloc 20000 가량의 파일 대상으로, 0.2초 가량 소모
    prog.close()

def cppFillTree(fname):
    prog=open(fname, 'r', encoding='UTF8')

    lines = prog.read()

    ignore_list = []

    
    # 인덱스 리스트
    indexes = []
    for match in re.finditer('//',lines):
        indexes.append(match.span()[0])
    for match in re.finditer('"',lines):
        indexes.append(match.span()[0])
    for match in re.finditer('/\*',lines):
        indexes.append(match.span()[0])

    indexes.sort()

    # '"'인 경우 미포함
    # '//', '/*', '"' 찾아서 ignore_list에 추가
    for index in indexes:
        
        if index > len(lines) - 2:
            break

        # ignore_list에 있다면 패스
        do_continue = False
        
        for start, end in ignore_list:
            
            if index >= start and index <= end:
                do_continue = True
                break

        if do_continue:
            continue

        # ignore_list append
        
        if lines[index:index+2] == '//':
            end = lines[index:].find('\n') + index + 1
            ignore_list.append((index, end))
        
        elif lines[index:index+2] == '/*':
            end = lines[index:].find('*/') + index + 2
            ignore_list.append((index, end))
            
        else:
            end = lines[index+1:].find('"') + index + 2
            ignore_list.append((index, end))

    # for debug
    '''
    for start, end in ignore_list:
        print(lines[start:end])

    print("end of ignore")
    print(len(ignore_list))

    input()
    '''
    
    # class 찾기
    for class_index in re.finditer('class', lines):

        index = class_index.span()[0]

        # ignore_list에 있으면 제거
        do_continue = False
        
        for ignore_index, tup in enumerate(ignore_list):
            
            start, end = tup
            
            if start >= index:

                start, end = ignore_list[ignore_index-1]
                
                # ignore_list 안에 있으면
                if index >= start and index < end:
                    do_continue = True
                break

        if do_continue:
            continue
                

        # 이름 찾기    
        br_index = lines[index:].find('{')     
        name = lines[index+6:index+br_index-1]

        # 시작 행, 열 찾기
        row = lines[:index].count('\n') + 1
        rindex = lines[:index].rfind('\n')
        column = index - rindex - 1

        # 끝 행, 열 찾기
        br_indexes = []
        
        for match in re.finditer('{', lines[index:]):
            br_indexes.append(match.span()[0])
        for match in re.finditer('}', lines[index:]):
            br_indexes.append(match.span()[0])

        br_indexes.sort()

        open_count = 0        
        for br_index in br_indexes:
            
            if lines[index+br_index] == '{':
                open_count += 1
            elif lines[index+br_index] == '}':
                open_count -= 1

            if open_count == 0:
                close_pos = br_index + index
                break
        
        end_row = lines[:close_pos].count('\n') + 1
        rindex = lines[:close_pos].rfind('\n')
        end_column = close_pos - rindex - 1
            
        
        # 클래스 ('이름', 파일, 시작 위치(행/열), 끝 위치(행/열), )
        classes.append((name, fname, (row, column), (end_row, end_column)))


    # 함수 찾기
    for func_index in re.finditer(' .*\(.*\)[ \n\t]*{',lines):

        index = func_index.span()[0]
        br_index = lines[index:].find('(') + index

        name = lines[index:br_index].strip()
        if name in reserved_word_cpp or name in reserved_word_c:
            continue

        # 시작 행, 열 찾기
        row = lines[:index].count('\n') + 1
        rindex = lines[:index].rfind('\n')
        column = index - rindex - 1

        # 끝 행, 열 찾기
        br_indexes = []
        
        for match in re.finditer('{', lines[index:]):
            br_indexes.append(match.span()[0])
        for match in re.finditer('}', lines[index:]):
            br_indexes.append(match.span()[0])

        br_indexes.sort()

        open_count = 0        
        for br_index in br_indexes:
            
            if lines[index+br_index] == '{':
                open_count += 1
            elif lines[index+br_index] == '}':
                open_count -= 1

            if open_count == 0:
                close_pos = br_index + index
                break
        
        end_row = lines[:close_pos].count('\n') + 1
        rindex = lines[:close_pos].rfind('\n')
        end_column = close_pos - rindex - 1

        # 스코프 찾기, 미완료
        scope = None

        # 매개변수 찾기
        start = lines[index].find('(')
        end = lines[index].find(')')
        args = lines[start:end]
        
        

        # 함수 {'이름': [[파일, 시작 위치(행/열), 끝 위치(행/열), 스코프(전역 or 클래스이름), 매개변수], [파일, 시작 위치(행/열), 끝 위치(행/열), 스코프(전역 or 클래스이름), 매개변수]]}
        if functs.get(name) == None:
            functs[name] = []
            functs[name].append((fname, (row, column), (end_row, end_column), scope, args))
        else:
            functs[name].append((fname, (row, column), (end_row, end_column), scope, args))            
    
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
        POOL.add(fi.lower())
    for cl in classes:
        POOL.add(cl[0].lower())
    for fu in functs:
        POOL.add(fu.lower())

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
