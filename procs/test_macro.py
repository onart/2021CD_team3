import pyautogui as pag
import keyboard

while True:
    if keyboard.is_pressed('shift'):
        pag.keyDown('ctrl')
        pag.press('f5')
        pag.keyUp('ctrl')

    if keyboard.is_pressed('pause+a'):
        pag.keyDown('ctrl')
        pag.keyDown('k')
        pag.press('c')
        pag.keyUp('k')
        pag.keyUp('ctrl')

    if keyboard.is_pressed('pause+s'):
        pag.keyDown('ctrl')
        pag.keyDown('k')
        pag.press('u')
        pag.keyUp('k')
        pag.keyUp('ctrl')

    if keyboard.is_pressed('ESC'): 
        break

#shift 실행/ pause+a 한줄 주석처리/ pause+s 한줄 주석해제/ESC 종료
