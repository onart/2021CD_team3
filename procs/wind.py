'''
활성 윈도우 이름
'''
import time, ctypes
from os import popen
IDE_LIST=('Visual Studio Code', 'Microsoft Visual Studio', 'Eclipse IDE')
IDE_REPR=('비주얼 스튜디오 코드', '비주얼 스튜디오', '이클립스')

IDE_PROC={  # key: 프로세스 이름, value: [표시 이름, set(열외 타이틀)]
    'pycharm64.exe':['PyCharm', {
            'Create Project',
            'Settings',
            'Confirm Exit',
        }],
    'Code.exe': ['비주얼 스튜디오 코드', {

        }],
    'devenv.exe': ['비주얼 스튜디오', {

        }],
    'eclipse.exe':['이클립스', {

        }],
    }

def wname(s, pname):
    if (pname not in IDE_PROC) or (s in IDE_PROC[pname][1]):
        return 'others'
    if pname=='pyCharm':
        return 'PyCharm'
    for i in range(len(IDE_LIST)):
        if s.find(IDE_LIST[i],-len(IDE_LIST[i])) != -1:
            return IDE_REPR[i]
    return 'others'

def currentWindow(receiver):    #스레드 함수
    lib=ctypes.windll.LoadLibrary('user32.dll')
    pid=ctypes.c_ulong()
    p_pid=ctypes.pointer(pid)
    while True:
        hwnd = lib.GetForegroundWindow()
        # SetForegroundWindow(핸들)로 다른 창 활성화 가능
        buffer = ctypes.create_unicode_buffer(255)
        lib.GetWindowTextW(hwnd, buffer, ctypes.sizeof(buffer))
        lib.GetWindowThreadProcessId(hwnd, p_pid)
        try:
            pname=popen('tasklist /fi "pid eq {}"'.format(pid.value)).read().split('\n')[3].split()[0]
        except IndexError:
            pname=''
        wind = wname(buffer.value, pname)
        if wind != receiver.activeWindow.text:
            try:
                receiver.activeWindow.setText(wind)
            except RuntimeError:
                print('wind Thread: runtime error')
                return
            if wind=='others':
                pass
            else:
                receiver.hIdeWnd=hwnd
            # print(cur)
        time.sleep(0.2)   # 갱신 시간 수


class corner_case():
    def test1(self):
        print("dsd")
        def test2():
            print("sds")
    class corner_in_corner():
        def test3(self):
            print("sdsds")
            def test4():
                print("dsdsds")
