from unittest import mock

def called_t1():
    m = mock.Mock()
    m.hello.return_value = "hi"   # 이게 마치 m이라는 객체에 hello라는 멤버가 있고, 그걸 함수라고 간주하고, return vlaue를 hi로 설정하겠다 이 말인거지? 
    # print(m.hello("x","y"))              # hi
    print(m.hello())
    print(m.hello())

    m.hello.assert_called_once_with()      # hello()가 정확히 한 번, 인자 없이 호출됐는지 만약 두 번 호출되면 assert된다. 
    # m.hello.assert_called_once_with("x","y") #


def real_hello(name):
    return f"Hi, {name}"

def t2():
    m = mock.Mock()
    m.hello = mock.create_autospec(real_hello, return_value="ok")
    m.hello("CoCo")
    # m.hello() # TypeError 인자 부족
    # m.hello("a","b") # TypeError 인자 과다
    m.hello.assert_called_once_with("CoCo")
    print(m.hello.call_count)
    

class Dog: 
    def __init__(self, name):
        self.name = name
    def bark(self):
        return f"{self.name} says bbaaark!!"

def t3():
    d = Dog("BoBBy")
    print(d.bark())

t3()
