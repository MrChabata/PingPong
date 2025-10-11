s = input().split()
a = int(s[0])
b = int(s[1])
c = int(s[2])
p = int(s[3])

D = b**2 - 4 * a * c
print(D)
x = -b / (2 * a)
print(x)
f = (a * p**2 + b * p + c) / a
print(f)

if D > 0 and x > p and f > 0:
    print("оба корня справа")
elif D > 0 and x > p and f == 0:
    print(f"один корень лежит в {p}, другой правее {p}")
elif f < 0:
    print(f"один корень лежит левее {p}, другой правее {p}")
elif D > 0 and x < p and f == 0:
    print(f"один корень лежит в {p}, другой левее {p}")
elif D > 0 and x < p and f > 0:
    print("оба корня слева")
elif D == 0 and x > p:
    print("один корень справа")
elif D == 0 and x < p:
    print("один корень слева")
elif D == 0 and x == p:
    print("один корень и это", p)
else:
    print("нет решений")