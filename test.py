import scipy.fft
import matplotlib.pyplot as plt


# N = 500
T = 0.001
y = [0.0, 0.0, 8000.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 8000.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8500.0, 16500.0, 24500.0, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 25000.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 17500.0, 25000.0, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 32767.5, 24500.0, 16500.0, 8500.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8000.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 15500.0, 8000.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8500.0]
N = len(y)
T = 2 / N
print(T)
print(N)
x = [i * 0.001 for i in range(1, 1000)]
x_f = [(i / (N//2)) * 1.0/(2.0*T) for i in range(0, N//2)]
ft = scipy.fft.fft(y)
print(ft)
y_f = [abs(ft[i]) for i in range(0, len(ft))]
print(y_f)
# print(x_f)
# x_f = np.linspace(0.0, 1.0/(2.0*T), N//2)
# print(np.linspace(0.0, 1.0/(2.0*T), N//2))
# print(len(np.linspace(0.0, 1.0/(2.0*T), N//2)))
# print(N)
# print(N//2)
# print(1.0/(2.0*T))

# print(y_f)
# print(y_f[:N//2])
# print(abs(y_f[:N//2]))

maxi = max(y_f)
# arr = 1/maxi * y_f[:N//2]
print(maxi)
arr = [y_f[i] / maxi for i in range(0, N//2)]
# print(arr)
plt.plot(x_f[:30], arr[:30])
plt.show()
print(x_f)
for i in range(5):
    m = max(arr)
    print(arr.index(m), "  ", m)

    arr.remove(m)

