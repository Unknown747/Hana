isFirstRun := true

Loop
{
    SetTitleMatchMode, 2
    IfWinExist, Hanafuda - Google Chrome
    {
        WinActivate
        WinWaitActive, Hanafuda - Google Chrome
        Send, {WheelDown 10}
        CoordMode, Mouse, Window
        Click, 979, 883 
        Sleep, 4000 
    }

    attempt := 0
    success := false
    while (attempt < 3) 
    {
        IfWinExist, MetaMask
        {
            success := true
            WinActivate
            WinWaitActive, MetaMask
            Send, {WheelDown 10}
            Sleep, 1690
            if (isFirstRun)
            {
                Send, {Tab 13} 
                isFirstRun := false 
            }
            else
            {
                Send, {Tab 14}
            }

            Sleep, 500
            Send, {Enter}
            break 
        }
        else
        {
            attempt++ 
            Sleep, 420
        }
    }

    if (!success)
    {
        MsgBox, Popup MetaMask tidak ada njir.
    }
    Sleep, 1000
}
