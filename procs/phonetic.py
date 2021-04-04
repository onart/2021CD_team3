'''
단어 풀 연결 관련 함수들

0. 이슈: 숫자가 들어간 클래스/함수명은?
0.1. 숫자를 중심으로 끊을 것.
0.1.1. 끊어진 숫자가 '123'이라고 하면 one two three, 백이십삼, 일이삼, one hundred twenty three를 인정

1. 음절수 컷(+1~+2까지)
2. 모음유사도
3. 
'''

EXC='aehiouwy'
ALPHA=(0,1,2,3,0,1,2,0,0,2,2,4,5,5,0,1,2,6,2,3,0,1,0,2,0,2)
smallA=ord('a')

def soundEx(keyword):   # 일반 케이스
    ret=keyword[0]
    cur='?'
    for c in keyword[1:]:
        i=ALPHA[ord(c)-smallA]
        if i != 0 and c != cur:
            ret+=str(i)
            cur=i
            '''
            if len(ret)==4:
                return ret
                '''
    
    return ret.ljust(4,'0')

def spell(inp, keyword):    # 스펠을 부른 케이스
    return (keyword.find(inp) == 0)


def standardize(keyword):   # snake, camel/pascal 표기법 지원하여 단어 분리, 숫자 분리
    length=len(keyword)
    # snake (first_second_third)
    ls=snake.split(keyword,'_')
    if len(ls) >= 2:
        for i in range(len(ls)):
            ls[i]=ls[i].lower()
        return ls
    # camel/pascal (firstSecondThird/FirstSecondThird)
    for i in range(length):
        keyword('next')
    
