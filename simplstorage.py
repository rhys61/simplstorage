import hashlib as h
from pathlib import Path
import base64,sys,subprocess,os,inspect
from pickle import dumps,loads
from cryptography.fernet import Fernet as F

def keyderivative(t,i=100000,salt="just pick a salt",hashname="sha256"):
    return h.pbkdf2_hmac(hash_name=hashname,password=t.encode(),salt=salt.encode(),iterations=i,dklen=32)

def ferenc(message,key,plainafter=True):
    try:
        key = base64.urlsafe_b64encode(sha256(key.encode('utf-8'),True).digest())
    except AttributeError:
        key = base64.urlsafe_b64encode(sha256(key,True).digest())
        
    fenc = F(key)
    try:
        message = message.encode('utf-8')
    except:
        pass
    if plainafter:
        return fenc.encrypt(message).decode('utf-8') 
    return fenc.encrypt(message)

def ferdec(message,key):
    try:
        key = base64.urlsafe_b64encode(sha256(key.encode('utf-8'),True).digest())
    except AttributeError:
        key = base64.urlsafe_b64encode(sha256(key,True).digest())
    
    if not isinstance(message,bytes):
        message = message.encode('utf-8')
    fenc = F(key)
    return fenc.decrypt(message).decode("utf-8")

def programPath():
    module = sys.modules.get('__main__')
    if module and hasattr(module, '__file__'):
        return os.path.realpath(module.__file__)
    
    for frame in inspect.stack():
        if frame.frame.f_globals.get('__name__') == '__main__':
            if frame.filename and os.path.exists(frame.filename):
                return os.path.realpath(frame.filename)

def sha256(inpt,raw=False):
    if raw:
        return h.sha256(inpt)
    try:
        return h.sha256(inpt.encode('utf-8')).hexdigest()
    except AttributeError:
        return h.sha256(inpt).hexdigest()



class LocalStorage:
    def __init__(self,password=None,time=400000,salt="i dont want to code in a random salt. im too lazy tbh"):
        self.mainprogram = programPath()
        if password == None:
            password = self.mainprogram
        password += self.mainprogram
        self.key = sha256(keyderivative(password,time,salt+self.mainprogram)+self.mainprogram.encode())
        self.filename = Path(os.environ["PROGRAMDATA"])/"Python Package Data"/"SimplStorage.dat"
        self.filename.parent.mkdir(parents=True,exist_ok=True)
        try:
            with open(self.filename,"rb"):
                pass
        except FileNotFoundError:
            self.filename.touch()
    
    def store(self,data,handler):
        if handler is None:
            return
        elif isinstance(handler,(list,tuple,set)):
            handler = list(handler)
            if isinstance(data,(list,tuple,set)):
                data = list(data)
            else:
                data = [data]
        else:
            handler = [handler]
            if isinstance(data,(tuple,set)):
                data = list(data)
            else:
                data = [data]
        if len(data) > len(handler):
            data = data[:len(handler)]
        if len(data) < len(handler):
            handler = handler[:len(data)]
        with open(self.filename,"rb+") as file:
            lines = file.read().splitlines()
            existing = {}
            for i in range(0,len(lines),2):
                try:
                    existing[ferdec(lines[i],self.key)] = i
                except:
                    pass
            for n in range(len(handler)):
                pickledata = dumps(data[n])
                encodeddata = ferenc(pickledata.hex(),self.key).encode("utf-8")
                if handler[n] in existing:
                    line = existing[handler[n]]
                    lines[line] = ferenc(handler[n],self.key).encode("utf-8")
                    lines[line+1] = encodeddata
                else:
                    existing[handler[n]] = len(lines)
                    lines.append(ferenc(handler[n],self.key).encode("utf-8"))
                    lines.append(encodeddata)
            lines = [line+b"\n" for line in lines]
            file.seek(0)
            file.writelines(lines)
            file.truncate()
        return True
    
    def retrieve(self,handler=None,getall=False):
        if handler is None and getall == False:
            return
        elif isinstance(handler,(list,tuple,set)):
            handler = list(handler)
        else:
            handler = [handler]
        if getall:
            with open(self.filename,"rb") as file:
                lines = file.read().splitlines()
                linenums = []
                for i in range(0,len(lines),2):
                    try:
                        ferdec(lines[i],self.key)
                        linenums.append(i)
                    except:
                        continue
                if len(linenums) == 0:
                    return None
                returning = []
                for line in linenums:
                    try:
                        returning.append((loads(bytes.fromhex(ferdec(lines[line+1].decode("utf-8"),self.key))),ferdec(lines[line].decode(),self.key)))
                    except Exception as e:
                        returning.append(False)
                if len(returning) == 1:
                    return returning[0]
                return returning
        else:
            with open(self.filename,"rb") as file:
                lines = file.read().splitlines()
                linenums = []
                for i in range(0,len(lines),2):
                    try:
                        if ferdec(lines[i],self.key) in handler:
                            linenums.append(i)
                    except:
                        pass
                if len(linenums) == 0:
                    return None
                returning = []
                for line in linenums:
                    try:
                        returning.append(loads(bytes.fromhex(ferdec(lines[line+1].decode("utf-8"),self.key))))
                    except:
                        returning.append(False)
                if len(returning) == 1:
                    return returning[0]
                return returning
    
    def exists(self,handler):
        if handler is None:
            return
        elif isinstance(handler,(list,tuple,set)):
            handler = list(handler)
        else:
            handler = [handler]
        with open(self.filename,"rb") as file:
            fileread = file.read().splitlines()
            line = False
            returns = [False for _ in handler]
            for i in range(0,len(fileread),2):
                try:
                    tester = ferdec(fileread[i],self.key)
                    if tester in handler:
                        returns[handler.index(tester)] = True
                except:
                    continue
            if len(returns) == 1:
                return returns[0]
            return returns
    
    def delete(self,handler):
        if handler is None:
            return
        elif isinstance(handler,(list,tuple,set)):
            handler = list(handler)
        else:
            handler = [handler]
        with open(self.filename,"rb+") as file:
            fileread = file.read().splitlines()
            filenew = []
            for i in range(0,len(fileread),2):
                try:
                    if ferdec(fileread[i],self.key) in handler:
                        continue
                    raise AttributeError
                except:
                    filenew.append(fileread[i])
                    filenew.append(fileread[i+1])
            
            filenew = [line+b'\n' for line in filenew]
            file.seek(0)
            file.writelines(filenew)
            file.truncate()
    
    def deleteall(self):
        with open(self.filename,"rb+") as file:
            fileread = file.read().splitlines()
            for i in range(0,len(fileread),2):
                try:
                    ferdec(fileread[i],self.key)
                    fileread[i] = False
                    fileread[i+1] = False
                
                except:
                    continue
            filenew = fileread[:]
            for i,line in zip(range(0,len(fileread),2),fileread[::2]):
                if line == False:
                    for j in range(i,len(filenew)-2):
                        filenew[j] = filenew[j+2]
                    del filenew[-2:]
            filenew = [line+b'\n' for line in filenew]
            file.seek(0)
            file.writelines(filenew)
            file.truncate()
    
    def pop(self,handler):
        out = self.retrieve(handler)
        self.delete(handler)
        return out
    
    def returndata(self,data=None,multiple=False,binary=False):
        if data is None:
            return b"" if binary else ""
        elif multiple:
            if isinstance(data,(list,tuple,set)):
                data = list(data)
            else:
                data = [data]
        else:
            if isinstance(data,(tuple,set)):
                data = list(data)
            else:
                data = [data]
        returning = []
        for n in range(len(data)):
            if binary:
                returning.append(ferenc(dumps(data[n]).hex(),self.key))
            else:
                returning.append(ferenc(dumps(data[n]).hex(),self.key).encode("utf-8"))
        if len(returning) == 1:
            return returning[0]
        return returning
    
    def changefile(self,filepath):
        alldata = self.retrieve(getall=True)
        self.deleteall()
        self.filename = Path(filepath)
        self.filename.parent.mkdir(parents=True,exist_ok=True)
        try:
            with open(self.filename,"rb"):
                pass
        except FileNotFoundError:
            self.filename.touch()
        handlers = []
        data = []
        for group in alldata:
            data.append(group[0])
            handlers.append(group[1])
        self.store(data,handlers)



class GlobalStorage:
    def __init__(self,key="no key provided",time=400000,salt="i dont want to code in a random salt. im too lazy tbh"):
        self.key = sha256(keyderivative(key+":P",time,salt+"lmao this is so fun to code in stupid easter-eggs"))
        self.filename = Path(os.environ["PROGRAMDATA"])/"Python Package Data"/"SimplStorage.dat"
        self.filename.parent.mkdir(parents=True,exist_ok=True)
        try:
            with open(self.filename,"rb"):
                pass
        except FileNotFoundError:
            self.filename.touch()
        self.helloworld = "Hello World!"
    
    def store(self,data,handler):
        if handler is None:
            return
        elif isinstance(handler,(list,tuple,set)):
            handler = list(handler)
            if isinstance(data,(list,tuple,set)):
                data = list(data)
            else:
                data = [data]
        else:
            handler = [handler]
            if isinstance(data,(tuple,set)):
                data = list(data)
            else:
                data = [data]
        if len(data) > len(handler):
            data = data[:len(handler)]
        if len(data) < len(handler):
            handler = handler[:len(data)]
        with open(self.filename,"rb+") as file:
            lines = file.read().splitlines()
            existing = {}
            for i in range(0,len(lines),2):
                try:
                    existing[ferdec(lines[i],self.key)] = i
                except:
                    pass
            for n in range(len(handler)):
                pickledata = dumps(data[n])
                encoded_data = ferenc(pickledata.hex(),self.key).encode("utf-8")
                if handler[n] in existing:
                    line = existing[handler[n]]
                    lines[line] = ferenc(handler[n],self.key).encode("utf-8")
                    lines[line+1] = encoded_data
                else:
                    existing[handler[n]] = len(lines)
                    lines.append(ferenc(handler[n],self.key).encode("utf-8"))
                    lines.append(encoded_data)
            lines = [line+b"\n" for line in lines]
            file.seek(0)
            file.writelines(lines)
            file.truncate()
        return True
    
    def retrieve(self,handler):
        if handler is None:
            return
        elif isinstance(handler,(list,tuple,set)):
            handler = list(handler)
        else:
            handler = [handler]
        with open(self.filename,"rb") as file:
            lines = file.read().splitlines()
            linenums = []
            for i in range(0,len(lines),2):
                try:
                    if ferdec(lines[i],self.key) in handler:
                        linenums.append(i)
                except:
                    continue
            if len(linenums) == 0:
                return None
            returning = []
            for line in linenums:
                try:
                    returning.append(loads(bytes.fromhex(ferdec(lines[line+1].decode("utf-8"),self.key))))
                except:
                    returning.append(False)
            if len(returning) == 1:
                return returning[0]
            return returning
    
    def exists(self,handler):
        if handler is None:
            return
        elif isinstance(handler,(list,tuple,set)):
            handler = list(handler)
        else:
            handler = [handler]
        with open(self.filename,"rb") as file:
            fileread = file.read().splitlines()
            line = False
            returns = [False for _ in handler]
            for i in range(0,len(fileread),2):
                try:
                    tester = ferdec(fileread[i],self.key)
                    if tester in handler:
                        returns[handler.index(tester)] = True
                except:
                    continue
            if len(returns) == 1:
                return returns[0]
            return returns
    
    def delete(self,handler):
        if handler is None:
            return
        elif isinstance(handler,(list,tuple,set)):
            handler = list(handler)
        else:
            handler = [handler]
        with open(self.filename,"rb+") as file:
            fileread = file.read().splitlines()
            filenew = []
            for i in range(0,len(fileread),2):
                try:
                    if ferdec(fileread[i],self.key) in handler:
                        continue
                    raise AttributeError
                except:
                    filenew.append(fileread[i])
                    filenew.append(fileread[i+1])
            
            filenew = [line+b'\n' for line in filenew]
            file.seek(0)
            file.writelines(filenew)
            file.truncate()
    
    def deleteall(self):
        with open(self.filename,"rb+") as file:
            fileread = file.read().splitlines()
            for i in range(0,len(fileread),2):
                try:
                    ferdec(fileread[i],self.key)
                    fileread[i] = False
                    fileread[i+1] = False
                
                except:
                    continue
            filenew = fileread[:]
            for i,line in zip(range(0,len(fileread),2),fileread[::2]):
                if line == False:
                    for j in range(i,len(filenew)-2):
                        filenew[j] = filenew[j+2]
                    del filenew[-2:]
            filenew = [line+b'\n' for line in filenew]
            file.seek(0)
            file.writelines(filenew)
            file.truncate()
    
    def pop(self,handler):
        out = self.retrieve(handler)
        self.delete(handler)
        return out