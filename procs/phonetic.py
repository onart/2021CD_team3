EXC='aehiouwy'
ALPHA='01230120022455012623010202'
REALNUMBER=')!@#$%^&*('
smallA=ord('a')

BASEORDER=ord('가')

HD=( 'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ',
       'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ' )
MD=('ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ',
     'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ' )
ED=( '', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ',
      'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ',
      'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ')

DM={
    'ㅑ': 'ㅣㅏ',
    'ㅒ': 'ㅣㅐ',
    'ㅕ': 'ㅣㅓ',
    'ㅖ': 'ㅣㅔ',
    'ㅘ': 'ㅗㅏ',
    'ㅙ': 'ㅗㅐ',
    'ㅚ': 'ㅗㅔ',
    'ㅛ': 'ㅣㅗ',
    'ㅝ': 'ㅜㅓ',
    'ㅟ': 'ㅜㅣ',
    'ㅠ': 'ㅣㅜ',
    'ㅢ': 'ㅡㅣ',
    'ㄳ': 'ㄱㅅ',
    'ㄵ': 'ㄴㅈ',
    'ㄶ': 'ㄴㅎ',
    'ㄺ': 'ㄹㄱ',
    'ㄻ': 'ㄹㅁ',
    'ㄼ': 'ㄹㅂ',
    'ㄽ': 'ㄹㅅ',
    'ㄾ': 'ㄹㅌ',
    'ㄿ': 'ㄹㅍ',
    'ㅄ': 'ㅂㅅ',
    }

def subHead(inp, word): # arrange에 사용하게 될 수 있음
    length=min(len(inp), len(word))
    for i in range(length):
        if inp[i] != word[i]:
            return i
    return i


def arrange(inp, words): #일반 기준. keyword는 입력된 음성, words는 함수/클래스 풀
    ar=[]
    basis, eng=kSoundEx(inp)
    linp=len(eng)
    for w in words:
        if len(w)>=linp*2:
            continue
        val=lcsThr(soundEx(w),basis)
        val2=lcsThr(w,eng)
        if eng[0]==w[0]:
            val2+=1
        if val>0:
            ar.append((w, val+val2/10))
    ar.sort(key=lambda x: (x[1], -len(x[0])), reverse=True)
    #print(ar)
    return [x[0] for x in ar]
    
def arrange_s(inp, words):   #spell 기준. keyword는 입력된 음성, words는 함수/클래스 풀
    ar=[]
    jnp=''.join(inp.split())
    for w in words:
        if spell(jnp, w):
            ar.append(w)
    ar.sort(key=lambda x: len(x))
    return ar

def arrange_k(inp, words):
    mx=0
    basis=hme(inp)
    ret='명령'
    for w in words:
        w2=hme(w)
        val=lcsThr(basis, w2)
        if val>mx:
            mx=val
            ret=w
    return ret

def soundEx(keyword):   # 일반 케이스
    ret=str(ALPHA[ord(keyword[0])-smallA])
    if ret=='0':
        ret=keyword[0]
    begin=False
    for c in keyword[1:]:
        if c==' ':
            begin=True
            continue
        elif c.isnumeric():
            begin=False
            ret+=REALNUMBER[int(c)]
            continue
        i=ALPHA[ord(c)-smallA]
        if i=='0':
            if c == ret[-1] and begin:
                continue
            elif c=='w':
                ret+='u'
            else:
                ret+=c
        elif i != ret[-1] or begin:
            ret+=i
        begin=False
    return ret

def kSoundEx(keyword):  # 한국어에 SoundEx를 적용해볼 것
    '''
    #. 끝소리 ㄱㄴㄷㄹㅁㅂㅇ -> 외래어 표기법의 존재로 미적용
    #-1. 연음 받침 뒤 모음 -> 결합 -> 어차피 직렬화시킬 것이므로 무관
    2-1. 비음화 1 ㄴ,ㅁ 앞의 ㄱ계, ㄷ계, ㅂ계는 각각 ㅇ,ㄴ,ㅁ
    2-2. 비음화 2 ㅁ,ㅇ 뒤 ㄹ은 ㄴ
    2-3. 유음화 ㄹ 앞뒤 ㄴ은 ㄹ
    3. 구개음화 ㄷ,ㅌ계 뒤 ㅣ -> ㅈ,ㅊ
    4. 거센소리되기 ㅎ 앞뒤 ㅂㄷㅈㄱ -> ㅍㅌㅊㅋ
    #. 된소리되기 ㄱㄷㅂ계 뒤 ㄱㄷㅂㅅㅈ는 된소리로 -> 어차피 soundex에서 거의 동일시됨
    #. 사이시옷은 어근 접사 관련 법칙도 있기 때문에 생략
    '''
    # 스펠링을 또박또박 부르면 로마자 알파벳이 들어오는 것으로 확인, 전체가 로마자일 때는 arrange_s 사용, 이외에는 그대로 반영
    # 확인된 문제: 여기서 아직 숫자 인식 x, 한영키 한글 설정 시 팔레트에 한글로 입력되어 파일이 안 열림
    h=hme(keyword)
    ret=''
    eng=''
    i=0
    while i<len(h):
        c=h[i]
        if c in HD or c in ED:
            if i<len(h)-1:
                nx=h[i+1]
            else:
                nx=''
            if nx in HD or nx=='':  # 종성(이후 나온 초성과 함께 처리. 단 바로 다음 역시 종성의 일부일 가능성도 있음)
                if c=='ㄱㄲㅋ':
                    if nx in 'ㄴㅁ':    # 비음화
                        ret+=ALPHA[ord('n')-smallA]
                        ret+=ALPHA[ord('g')-smallA]
                        eng+='ng'
                    else:
                        ret+=ALPHA[ord('k')-smallA]
                        if nx in 'ㅎ':  # ㅎ축약
                            i+=1
                        elif nx in 'ㄱ':
                            i+=1
                elif c in 'ㄴ':
                    if nx == 'ㄹ':  # 유음화
                        ret+=ALPHA[ord('l')-smallA]
                        eng+='l'
                    else:
                        ret+=ALPHA[ord('n')-smallA]
                        eng+='n'
                elif c in 'ㄷㅌ':
                    if nx in 'ㄴㅁ':    # 비음화
                        ret+=ALPHA[ord('n')-smallA]
                        eng+='n'
                    elif nx in 'ㅎ':    # ㅎ축약
                        i+=1
                        ret+=ALPHA[ord('d')-smallA]
                        eng+='d'
                    elif nx in 'ㅇ':
                        if h[i+2] in 'ㅑㅒㅕㅖㅛㅠㅣ':  # 구개음화, 정상 입력 시 인덱스에러 없음
                            ret+=ALPHA[ord('j')-smallA]
                            eng+='j'
                        else:
                            ret+=ALPHA[ord('d')-smallA]
                            eng+='d'
                    elif nx in 'ㄷ':
                        i+=1
                        ret+=ALPHA[ord('d')-smallA]
                        eng+='d'
                elif c in 'ㄹ':
                    if nx in 'ㄴㄹ':
                        i+=1
                    ret+=ALPHA[ord('l')-smallA]
                    eng+='l'
                elif c in 'ㅁ':
                    if nx in 'ㄹ':
                        i+=1
                        ret+=ALPHA[ord('m')-smallA]
                        ret+=ALPHA[ord('n')-smallA]
                        eng+='mn'
                    else:
                        ret+=ALPHA[ord('m')-smallA]
                        eng+='m'
                elif c in 'ㅂㅍ':
                    if nx in 'ㅇㄴㅁ':
                        ret+=ALPHA[ord('m')-smallA]
                        eng+='m'
                    else:
                        ret+=ALPHA[ord('b')-smallA]
                        eng+='b'
                    if nx in 'ㅎ':
                        i+=1
                elif c in 'ㅅㅆ':
                    if nx in 'ㅇ':
                        ret+=ALPHA[ord('s')-smallA]
                        eng+='s'
                    elif nx in 'ㄴㅁ':
                        ret+=ALPHA[ord('n')-smallA]
                        eng+='n'
                    else:
                        ret+=ALPHA[ord('d')-smallA]
                        eng+='d'
                elif c in 'ㅈㅊ':
                    ret+=ALPHA[ord('j')-smallA]
                    eng+='j'
                elif c in 'ㅎ':
                    if nx in 'ㄱㄷㅂㅈ':
                        i+=1
                        if nx=='ㄱ':
                            ret+=ALPHA[ord('k')-smallA]
                            eng+='k'
                        elif nx=='ㄷ':
                            ret+=ALPHA[ord('t')-smallA]
                            eng+='t'
                        elif nx=='ㅂ':
                            ret+=ALPHA[ord('p')-smallA]
                            eng+='p'
                        elif nx=='ㅈ':
                            ret+=ALPHA[ord('c')-smallA]
                            eng+='c'
            else:                     # 처음 or 이전이 모음인 초성(ㅇ무시 -> 고의)
                if c in 'ㄱ':
                    ret+=ALPHA[ord('g')-smallA]
                    eng+='g'
                elif c in 'ㄲㅋ':
                    ret+=ALPHA[ord('k')-smallA]
                    eng+='k'
                elif c in 'ㄴ':
                    ret+=ALPHA[ord('n')-smallA]
                    eng+='n'
                elif c in 'ㄷ':
                    ret+=ALPHA[ord('d')-smallA]
                    eng+='d'
                elif c in 'ㄸㅌ':
                    ret+=ALPHA[ord('t')-smallA]
                    eng+='t'
                elif c in 'ㄹ':
                    ret+=ALPHA[ord('r')-smallA]
                    eng+='r'
                elif c in 'ㅁ':
                    ret+=ALPHA[ord('m')-smallA]
                    eng+='m'
                elif c in 'ㅂ':
                    ret+=ALPHA[ord('b')-smallA]
                    eng+='b'
                elif c in 'ㅃㅍ':
                    ret+=ALPHA[ord('p')-smallA]
                    eng+='p'
                elif c in 'ㅅㅆ':
                    ret+=ALPHA[ord('s')-smallA]
                    eng+='s'
                elif c in 'ㅈ':
                    ret+=ALPHA[ord('j')-smallA]
                    eng+='j'
                elif c in 'ㅉㅊ':
                    ret+=ALPHA[ord('c')-smallA]
                    ret+='h'
                    eng+='ch'
                elif c in 'ㅎ':
                    ret+='h'
                    eng+='h'
        elif c in MD:                         # 중성(ㅡ무시 -> 고의)
            if c in 'ㅏ':
                ret+='a'
                eng+='a'
            elif c in 'ㅐㅔ':
                ret+='ae'
                eng+='ae'
            elif c in 'ㅑ':
                ret+='ya'
                eng+='ya'
            elif c in 'ㅒㅖ':
                ret+='ye'
                eng+='ye'
            elif c in 'ㅓㅜ':
                ret+='u'
                eng+='u'
            elif c in 'ㅕ':
                ret+='yeo'
                eng+='yeo'
            elif c in 'ㅗ':
                ret+='o'
                eng+='o'
            elif c in 'ㅛ':
                ret+='yo'
                eng+='yo'
            elif c in 'ㅠ':
                ret+='yu'
                eng+='yu'
            elif c in 'ㅣ':
                if ret=='' or ret[-1]!='i': # 모음 연속 불가능성. 추후 확장할 수도 있고 안 할 수도 있음
                    ret+='i'
                    eng+='i'
        else:
            if c.isalpha():
                eng+=c
                c2=ALPHA[ord(c)-smallA]
                if c == 0:
                    ret+=c
                else:
                    ret+=c2
            elif c.isnumeric():
                eng+=c
                ret+=REALNUMBER[int(c)]
        i+=1
    return ret, eng

def spell(inp, keyword):    # 스펠을 부른 케이스
    keyw=''.join(keyword.split())
    return (keyw.find(inp) == 0)

def lcs(a, b):  # 모든 lcs의 내용을 리스트로 리턴
    prev = [(0, set())]*len(a)
    for i,r in enumerate(a):
        current=[]
        for j,c in enumerate(b):
            if r==c:
                e=prev[j-1][0]+1 if i*j>0 else 1
                if e==1:
                    e=(1, {r})
                else:
                    e=(e, {x+r for x in prev[j-1][1]})
            else:
                up=prev[j] if i>0 else (0, set())
                left=current[-1] if j>0 else (0,set())
                if up[0]>left[0]:
                    e=up
                elif up[0]<left[0]:
                    e=left
                else:
                    e=(up[0], up[1] | left[1])
            current.append(e)
        prev=current
    return list(current[-1][1])

def lcsThr(a, b, THRESHOLD=3): # LCS, 즉 Longest Common Subpronounciation의 길이를 리턴. b 기준:4, a 기준:3
    lcsLst=lcs(a, b)
    mx=0
    for w in lcsLst:
        pos=-1
        cur=0
        mxa=0
        mxb=0
        for letter in w:
            prev=pos
            pos=b.find(letter, pos+1)
            cur=1 if pos-prev>=THRESHOLD+1 else cur+1
            if mxb<cur:
                mxb=cur
        pos=-1
        cur=0
        for letter in w:
            prev=pos
            pos=a.find(letter, pos+1)
            cur=1 if pos-prev>=THRESHOLD else cur+1
            if mxa<cur:
                mxa=cur
        
        mx=max(mx, min(mxa, mxb))

    return mx

def hme(s):
    ret=''
    for c in s:
        try:
            ret+=hmeC(c)
        except IndexError:
            ret+=c
    return ret

def hmeC(letter):    # 리턴 (초, 중, 종성)
    letter=ord(letter)-BASEORDER
    ed=ED[letter % 28]
    letter //= 28
    md=MD[letter % 21]
    letter //= 21
    hd=HD[letter]
    if md in DM:
        md=DM[md]
    if ed in DM:
        ed=DM[ed]
    return hd+md+ed
