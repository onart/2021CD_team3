import os, time, re, threading, sys, traceback

sys.path.append(os.path.abspath('..'))

import procs.phonetic as phonetic

ext=dict()
modTimes=dict() # 파일 이름: [기록된 수정 시각, 타임스탬프]
rel2abs=dict()  # 파일 절대 경로 따로 저장

STAMP=0
TOPDIR=''
# 사용자에게 보여줄/IDE에서 탐색할 파일 이름: [len(TOPDIR)+1:]로 슬라이싱해야 함

scannerLock=threading.Lock()

# 템플릿: <...>까지 이름에 포함, 타입이 T 같이 돼 있는 것은 그대로 적음

# 클래스 {'이름': [파일, 시작 위치(행/열), 끝 위치(행/열)] }
classes=dict()
# 함수 {'이름': [[파일, 시작 위치(행/열), 끝 위치(행/열), 스코프(전역 or 클래스이름), 매개변수], [파일, 시작 위치(행/열), 끝 위치(행/열), 스코프(전역 or 클래스이름), 매개변수]]}
functs=dict()

class Pool:
    '''
    호출 순서: update(자동) -> soundIn(음성 입력 시) -> __getitem__(선택 시)
    '''
    def __init__(self):
        self.fu=dict()
        self.cl=dict()
        self.fi=dict()
        self.candid=set()

    def __getitem__(self, index):
        if index not in self.candid:
            return [[]]
        kfu=[]
        kcl=[]
        kfi=[]
        itm=0
        recent=None
        if index in self.fu:
            for fun in self.fu[index]:
                for func in functs[fun]:
                    ts=[fun]
                    ts.extend(func)
                    kfu.append(ts)
                    itm+=1
                    recent=ts
        if index in self.cl:
            for cla in self.cl[index]:
                ts=[cla]
                ts.extend(classes[cla])
                kcl.append(ts)
                itm+=1
                recent=ts
        if index in self.fi:
            kfi=self.fi[index]
            itm+=len(self.fi[index])
            if itm==1:
                recent=[self.fi[index][0]]
        if itm==1:
            return recent
        return [kfu, kcl, kfi]
    
    def clear(self):
        self.candid.clear()
        self.fu.clear()
        self.cl.clear()
        self.fi.clear()

    def normalize(self, name):  # 현재 단계: 로마자만 소문자로 남기고 나머지 제거(숫자도 제거)
        ret=''
        name=name.split('\\')[-1]
        for i in name:
            if ord(i)>=ord('a') and ord(i)<=ord('z'):
                ret+=i
            elif ord(i)>=ord('A') and ord(i)<=ord('Z'):
                ret+=' '
                ret+=i.lower()
            elif i=='_':
                ret+=' '
            else:
                ret+=' '

        return ' '.join(ret.split())

    def update(self):
        self.clear()
        for fi in modTimes:
            nfi=self.normalize(fi)
            self.candid.add(nfi)
            if nfi in self.fi:
                self.fi[nfi].append(fi)
            else:
                self.fi[nfi]=[fi]
        for fu in functs:
            nfu=self.normalize(fu)
            self.candid.add(nfu)
            if nfu in self.fu:
                self.fu[nfu].append(fu)
            else:
                self.fu[nfu]=[fu]
        for cl in classes:
            ncl=self.normalize(cl)
            self.candid.add(ncl)
            if ncl in self.cl:
                self.cl[ncl].append(cl)
            else:
                self.cl[ncl]=[cl]
    
    def soundIn(self, input):   # 인수: 구글 STT에서 받은 결과물(str, 영어), 리턴: 풀 내 후보
        input=self.normalize(input)
        ret=phonetic.arrange_s(input, self.candid)
        if len(ret)<3:
            ret.extend(phonetic.arrange(input, self.candid)[:3])
        elif len(ret)>10:
            # 너무 많아서 잘렸다고 안내
            ret=ret[:10]
        ret2=[]
        for r in ret:
            if r not in ret2:
                ret2.append(r)
        return ret2


POOL=Pool()

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

# 파이썬 magic function
python_magic_func = ["__new__", "__init__", "__add__", "__doc__", "__bool__", "__mul__", "__sub__", "__le__", "__ge__", "__del__",
                     "__bytes__", "__format__", "__len__", "__iter__", "__reversed__", "__contains__", "__iter__" ]

def setTop(dname):
    global TOPDIR
    TOPDIR=dname
    #os.chdir(dname)

def pyFillTree(fname, prog):
    code = prog.readlines()

    class_indent_for_scope = {}
    def_indent_for_nested_function = {}
    for row, line in enumerate(code):  # 행번호 0부터 시작

        line = line.rstrip()
        line_split = line.split()

        if (line and ':' in line and line_split[0] == 'class'):
            def_indent_for_nested_function = {}
            if (line_split[1][-1] == ':'):
                class_name = line_split[1][:-1]
            else:
                class_name = line_split[1]
            class_start_r = row
            class_start_c = 0
            class_end_r = None
            class_end_c = -1
            if ('(' in class_name):  # 클래스 이름에서 파라미터 삭제
                idx = class_name.find('(')
                class_name = class_name[:idx]
            for new_row, next in enumerate(code[row + 1:], start=row + 1):
                next_split = next.split()
                if (next_split and next[0] != ' '):
                    class_end_r = new_row - 1
                    break
            else:
                class_end_r = len(code)
            classes[class_name] = [fname, (class_start_r + 1, class_start_c), (class_end_r + 1, class_end_c)]
            class_indent_for_scope[line.find('class')] = class_name
        elif (line and ':' in line and line_split[0] == 'def'):
            fn_name = ''
            fn_para = ''
            fn_scope = ''
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
            if ('(' in fn_name):  # 함수 이름에서 파라미터 삭제
                idx = fn_name.find('(')
                fn_name = fn_name[:idx]

            if(fn_name in python_magic_func): # 매직 function 인 경우, 아예 집어넣지 않음
                continue
            for new_row, next in enumerate(code[row + 1:], start=row):  # 함수가 같은 줄에서 끝나는 경우 생각
                next_split = next.split()

                if (next_split and next.find(next_split[0]) < fn_start_c + 4 and new_row > row):
                    fn_end_r = new_row - 1
                    break
            else:
                fn_end_r = len(code)
            if (line.find('def') == 0):
                fn_scope = ''  # scope 전역일 때는 빈문자열로
            else:
                _i = 1
                while True: #가장 가까운 감싼 클래스 찾기
                    try:
                        fn_scope += class_indent_for_scope[line.find('def') - 4*_i]
                        break
                    except:
                        _i += 1
                try:
                    fn_scope += '.{}'.format(def_indent_for_nested_function[line.find('def') -4])
                except:
                    pass
            functs[fn_name] = functs.get(fn_name, [])
            functs[fn_name].append(
                [fname, [fn_start_r + 1, fn_start_c], [fn_end_r + 1, fn_end_c], fn_scope, fn_para.rstrip()])
            def_indent_for_nested_function[line.find('def')] = fn_name

    prog.close()

def cFillTree(fname, prog):
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
                        classes[tok1]=[fname, stp, curly[i+1]]
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
                        classes[tok1]=[fname, stp, curly[i+1]]  # 끝점은 curly[i+1]이 아니니 고칠 것
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
                                    classes[tok2]=[fname, stp, (lineNo, colNo)]
                                break
                        break
                    tok2=targc+tok2
                    stp=(lineNo, colNo)

    prog.close()

def cpp_classes_renew(re_str, name_length, lines, ignore_list, fname):
    
    for class_index in re.finditer(re_str, lines):

        index = class_index.span()[0]

        # ignore_list에 있으면 제거
        do_continue = False
        
        for start, end in ignore_list:
            
            if index >= start and index <= end:
                do_continue = True
                break

        if do_continue:
            continue
                

        # 이름 찾기    
        br_index = lines[index:].find('{')     
        name = lines[index+name_length+1:index+br_index-1]
        name = name.strip(' \n\t')

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
        classes[name]=[fname, (row, column), (end_row, end_column)]

def cppFillTree(fname, prog):
    lines=prog.read()

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
            # '"' 인 경우
            if lines[index-1] == "'" and lines[index+1] == "'":
                continue
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
    cpp_classes_renew('class[ \n\t]+\w+?[ \n\t]*{', len('class'), lines, ignore_list, fname)

    # 구조체 찾기
    cpp_classes_renew('struct[ \n\t]+\w+?[ \n\t]*{', len('struct'), lines, ignore_list, fname)

    # 열거형 찾기
    cpp_classes_renew('enum[ \n\t]+\w+?[ \n\t]*{', len('enum'), lines, ignore_list, fname)

    # 공용체 찾기
    cpp_classes_renew('union[ \n\t]+\w+?[ \n\t]*{', len('union'), lines, ignore_list, fname)

    # 함수 찾기
    for func_index in re.finditer('\)[ \n\t]*{', lines, re.S):

        index = func_index.span()[0]

        # 앞 괄호 찾기
        br_count = 0
        index -= 1
        
        while index >= 0:

            if lines[index] == '(':
                
                if br_count == 0:
                    break
                else:
                    br_count -= 1

            elif lines[index] == ')':
                
                br_count += 1

            index -= 1

        index -= 1

        # 앞 token 찾기
        while index >= 0 and lines[index] in ('\n', '\t', ' '):
            index -= 1

        if index < 0:
            continue

        end = index + 1

        while index >= 0 and lines[index] not in ('\n', '\t', ' '):
            index -= 1

        if index < 0:
            continue

        start = index + 1
            
        name = lines[start:end]
        
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
        scope = ''

        # 매개변수 찾기
        start = lines[index:].find('(') + index + 1
        end = lines[index:].find(')') + index
        args = lines[start:end]

        args=' '.join(args.split())
        
        

        # 함수 {'이름': [[파일, 시작 위치(행/열), 끝 위치(행/열), 스코프(전역 or 클래스이름), 매개변수], [파일, 시작 위치(행/열), 끝 위치(행/열), 스코프(전역 or 클래스이름), 매개변수]]}
        if functs.get(name) == None:
            functs[name] = []
            functs[name].append((fname, (row, column), (end_row, end_column), scope, args))
        else:
            functs[name].append((fname, (row, column), (end_row, end_column), scope, args))            
    
    prog.close()

def javaFillTree(fname, prog):
    func_range = ['public','protected','private']
    func_form = ['void','boolean','short','int','long','float','double']

    row = 0
    
    split_line = []
    
    save_line = []
    
    class_info = []
    class_start_locate1 = []
    class_start_locate2 = []
    class_end_locate = []
    
    func_info = []
    func_start_locate1 = []
    func_start_locate2 = []
    func_end_locate = []
    func_scope = []
    func_loc_para = []
    func_para = []
    
    ignore_index = []
    
    while True:
        row = row+1
        line = prog.readline()

        if line.find('//') != -1:
            line = line.split('//')[0]    

        if line.find('/*') != -1:
            ignore_index.append([row,line.find('/*'),'-1'])

        if line.find('*/') != -1:
            ignore_index.append([row,line.find('*/'),'1'])
                
        save_line.append(line)
        
        if not line: break #주석처리한 부분 저장

    
    for lines in save_line:
        split_line.append(lines.split())


    num_i = 0
        
    for i in split_line:
        num_i = num_i+1
        for j in i:

            if j == 'class':
                class_info.append(i[i.index(j)+1].split('{')[0])
                class_start_locate1.append([num_i,0])
                
                                               
            if j in func_range:
                if i[i.index(j)+1] in func_form:

                    if i[i.index(j)+2].split('(')[0][-1] != ';':
                        func_info.append(i[i.index(j)+2].split('(')[0])
                        func_start_locate1.append([num_i,0])

            if j == 'void':
                if i[i.index(j)+1].split('(')[0][-1] != ';':
                    func_info.append(i[i.index(j)+1].split('(')[0])
                    func_start_locate1.append([num_i,0])

            # function (), function( ), function() 고려해서 이름, 시작 행 가공
                    


    class_index = 0
    func_index = 0

    
    for class_name in class_info:
        class_index = class_index+1
        num_k = 0
        for k in save_line:
            num_k = num_k+1
            if num_k >= class_start_locate1[class_index-1][0]:
                if k.find('{') != -1:
                    class_start_locate2.append([num_k,k.find('{')]) # class 시작위치 찾음
                    break

    
    for func_name in func_info:
        func_index = func_index+1
        num_k = 0
        for k in save_line:
            num_k = num_k+1
            if num_k >= func_start_locate1[func_index-1][0]:
                if k.find('{') != -1:
                    func_start_locate2.append([num_k,k.find('{')]) # function 시작위치 찾음
                    break



    class_index = 0
    func_index = 0

    
    for class_name in class_info:
        class_index = class_index+1
        num_k = 0
        check_num = 0
        for k in save_line:
            num_k = num_k+1
            if num_k >= class_start_locate2[class_index-1][0]:
               
                if k.find('{') != -1:
                    check_num = check_num + 1
                    
                if k.find('}') != -1:
                    check_num = check_num - 1

                if check_num == 0:
                    class_end_locate.append([num_k,k.find('}')]) # class 끝위치 찾음
                    break

    
    for func_name in func_info:
        func_index = func_index+1
        num_k = 0
        check_num = 0
        for k in save_line:
            num_k = num_k+1
            if num_k >= func_start_locate2[func_index-1][0]:
                if k.find('{') != -1:
                    check_num = check_num + 1
                    
                if k.find('}') != -1:
                    check_num = check_num - 1

                if check_num == 0:
                    func_end_locate.append([num_k,k.find('}')]) # function 끝위치 찾음
                    break


    for locate_fn in range(0,len(func_start_locate2)):
        func_scope.append('')
        for locate_ca in range(0,len(class_start_locate2)):
            if func_start_locate2[locate_fn][0] >= class_start_locate2[locate_ca][0]:
                if func_end_locate[locate_fn][0] <= class_end_locate[locate_ca][0]:
                    func_scope[locate_fn] = class_info[locate_ca]
                    break #function scope 찾음


    func_index = 0
    for func_name in func_info:
        func_index = func_index+1
        num_k = 0
        check_num = 0
        for k in save_line:
            num_k = num_k+1
            if num_k == func_start_locate1[func_index-1][0]:
                func_loc_para.append([k.find('('),k.find(')')])
                func_para.append(k[k.find('(')+1:k.find(')')])


    for len_class in range(0,len(class_info)):
        classes[class_info[len_class]]=[fname,class_start_locate2[len_class],class_end_locate[len_class]]

    for len_func in range(0,len(func_info)):
        functs[func_info[len_func]]=[fname,func_start_locate2[len_func],func_end_locate[len_func],func_scope[len_func],func_para[len_func]]

    prog.close()

def gc():   # 제거된 파일에 대하여 기존 정보를 제거
    global classes, functs, modTimes
    rmm=[] # 데이터에서 제거할 파일
    for f in modTimes:
        if modTimes[f][1]!=STAMP:
            rmm.append(f)
            classes={x:classes[x] for x in classes if classes[x][0] != f}
            for fu in functs:
                functs[fu]=[x for x in functs[fu] if len(x)>0 and x[0] != f]
            functs={x:functs[x] for x in functs if len(functs[x]) != 0}
    for f in rmm:
        modTimes.pop(f)
        rel2abs.pop(f)

def forMod(fname):  # 수정된 파일에 대하여 기존 정보를 제거
    global classes, functs
    classes={x:classes[x] for x in classes if classes[x][0] != fname}
    for fu in functs:
        functs[fu]=[x for x in functs if x[0] != fname]

def scanDir(top):   # 입력값: 시작 시 설정한 top 디렉토리의 절대 경로. 기본 10초당 1회 호출, 어떤 음성이든 입력 시 즉시 호출 후 음성처리
    try:
        cont=[x for x in os.scandir(top) if x.is_dir() or os.path.splitext(x.name)[1] in ext]
    except FileNotFoundError:   # top 폴더가 삭제당함
        return
    for c in cont:
        fa=c.path
        fr=fa[len(TOPDIR)+1:]
        if c.is_dir():
            scanDir(fa)
        elif c.is_file:
            fext=os.path.splitext(fr)[1]
            prog=open(fa, encoding='UTF-8')
            try:
                mtime=c.stat().st_mtime
                modTimes[fr][1]=STAMP
                if modTimes[fr][0]!=mtime:
                    modTimes[fr][0]=mtime
                    forMod(fr)
                    try:
                        ext[fext](fr, prog)
                    except UnicodeDecodeError:
                        prog.close()
                        prog=open(fa, encoding='cp949')
                        try:
                            ext[fext](fr, prog)
                        except:
                            print('error',fr)
                            traceback.print_exc()
                            modTimes[fr]=[mtime, 0]
                    except:
                        print('error:',fr)
                        traceback.print_exc()
                        modTimes[fr]=[mtime, 0]
                
            except KeyError:
                modTimes[fr]=[mtime, STAMP]
                rel2abs[fr]=fa
                try:
                    ext[fext](fr, prog)
                except UnicodeDecodeError:
                    prog.close()
                    prog=open(fa, encoding='cp949')
                    ext[fext](fr, prog)
                except:
                    print('error:',fr)
                    traceback.print_exc()
                    modTimes[fr]=[mtime, 0]
            prog.close()

def scanTH():
    while True:
        scanNgc()
        # 업데이트 완료 신호
        time.sleep(10)

def scanNgc():  # git repo인 경우, 'git diff --name-status' 명령어로 더 빠르게 우회하도록(단, 이것은 커밋만 안 하면 계속 뜨기 때문에 후보를 걸러줄 뿐이며 역으로 커밋을 하면 바뀌었더라도 안 뜸) 하는 것 고려
    if len(TOPDIR)==0:
        return
    scannerLock.acquire()
    global STAMP
    STAMP=time.time()
    scanDir(TOPDIR)
    gc()
    POOL.update()
    scannerLock.release()


ext.update({
    '.py': pyFillTree,
    '.c': cFillTree,
    '.cpp': cppFillTree,
    '.java': javaFillTree,
    '.h': cppFillTree,
})


