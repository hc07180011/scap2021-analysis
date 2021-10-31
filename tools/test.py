import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


font = FontProperties(fname=r"DFLiHei-Bd.ttc")

plt.figure(dpi=400)
plt.pie([203, 122, 118, 63, 21, 14, 14])
plt.legend(["大學(203)", "程式交易(122)", "當沖(118)", "Line(63)", "Dcard(21)", "存股(14)", "TMBA(14)"], prop=font, loc="best")
plt.title("555 份問卷來源 (2021/10/30 18:00)", fontproperties=font)

plt.savefig("test.png")
