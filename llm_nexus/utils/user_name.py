import logging
import getpass, subprocess, ctypes
import ctypes.wintypes as wt

class UserNameSingleton:
    _instance = None
    _user_name = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserNameSingleton, cls).__new__(cls)
            cls._user_name = None
        return cls._instance
    
    def __init__(self):
        if self._user_name is None:
            self.__get_user_name()
        
        pass

    @classmethod
    def get_instance(cls):

        if cls._instance is None:
            cls._instance = cls()
            cls._instance.__get_user_name()

        return cls._instance
    
    @property
    def user_name(self):
        if not self._user_name:
            self.__get_user_name()
            logging.info(f"Determined user name: {self._user_name}")

        return self._user_name

    def __get_user_name(self) -> str:

        try:
            NameDisplay = 3
            GetUserNameExW = ctypes.windll.secur32.GetUserNameExW
            GetUserNameExW.argtypes = [ctypes.c_int, wt.LPWSTR, ctypes.POINTER(wt.DWORD)]
            GetUserNameExW.restype = wt.BOOL
            size = wt.DWORD(0)
            GetUserNameExW(NameDisplay, None, ctypes.byref(size))
            buf = ctypes.create_unicode_buffer(size.value or 256)
            if GetUserNameExW(NameDisplay, buf, ctypes.byref(size)):
                v = buf.value.strip()
                if v:
                    self._user_name = v
                    return v
                
        except Exception:
            pass

        # 2) PowerShell local/domain
        try:
            powershell_str = r'''
        $u = $env:USERNAME
        try { $l = Get-LocalUser -Name $u -ErrorAction Stop; if ($l.FullName) { $l.FullName; exit } } catch {}
        try { $a = Get-ADUser -Identity $u -Properties DisplayName -ErrorAction Stop; if ($a.DisplayName) { $a.DisplayName; exit } } catch {}
        exit 1
        '''
            out = subprocess.check_output(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", powershell_str],
                text=True, stderr=subprocess.DEVNULL
            ).strip()
            if out:
                self._user_name = out
        except Exception:
            pass
        
        self._user_name = getpass.getuser()


UserNameSingleton_instance = UserNameSingleton.get_instance()

def get_user_name() -> str:
    try:
        return str(UserNameSingleton_instance.user_name)
    except Exception:
        pass

if __name__ == "__main__":
    print(get_user_name())