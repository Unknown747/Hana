Loop
{
    SetTitleMatchMode, 2
    IfWinExist, Hanafuda - Google Chrome
    {
        WinActivate
        WinWaitActive, Hanafuda - Google Chrome
        CoordMode, Mouse, Window
        Click, 979, 883 
        Sleep, 4000  ;
    }
    IfWinExist, MetaMask
    {
        WinActivate
        WinWaitActive, MetaMask
        Click, 381, 187  
        CoordMode, Mouse, Window 
        Send, {WheelDown 10} 
        Sleep, 500
        Click, 301, 726 
        Sleep, 1000
    }
    else
    {
        MsgBox, popup MetaMask gada.
    }
    Sleep, 3
}
