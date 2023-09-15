# Reproduction of a Defogging Algorithm Using Dark Channel Prior

> Reference paper : [Single Image Haze Removal Using Dark Channel Prior | IEEE Journals & Magazine | IEEE Xplore](https://ieeexplore.ieee.org/document/5567108)

## Introduction

### Dark Channel Prior

暗通道去雾算法是基于一个统计性质的先验定理：**在无雾图像中的非天空区域中，一些像素的RGB三通道中的像素值会很低，接近于0**。这个自然规律可以表达为
$$
J^{dark}(k) = min_{C \in \{r,g,b\}}(min_{x\in\omega_k} J^c(x))\approx0
$$
其中，J为无雾图像，k代表图像中的一个点坐标，遍历r,g,b通道，每个通道中以k为中心的局部窗口$\omega_k$里，找一个最小值，分别是$min_{x\in\omega_k} J^r(x)$、$min_{x\in\omega_k} J^g(x)$、$min_{x\in\omega_k} J^b(x)$，最后在三者中找到最小值。

### Foggy Degradation Model

暗通道去雾模型为
$$
I = t\cdot J + (1-t)\cdot A
$$
其中，I为观测到的有雾图像，J是需要恢复的无雾图像，k是一个像素坐标，A是全局大气光，t是一个描述物体没有被散射抵达摄像机的传输率。简单来说，已知I，估计A与t，求J。

#### Evaluation A

估计全局大气光的方法有很多，最简单的方法就是选取全图最亮的点。对于天空而言，雾气感最强，可以认为无限远，经过长距离的散射，t值几乎等于0，观测到的值$I(k) \approx (1-t(k))\cdot A(k) = A(k) = A$。A是全局值，可以这么粗糙的估计。

基于此，何凯明老师提出**从观测图像的暗通道$I^{dark}$中选取最亮的前0.1%的点，这些点对应到原图I中再去找最亮的点作为A的估计，三通道分别找到$A^r$,$A^g$,$A^b$**，该方法估计出来的A则不一定为全局最亮的点，具有一定的鲁棒性。

#### Evaluation t

> In the haze image , the intensity of these dark pixels in that channel is mainly contributed by the airlight. Therefore, these dark pixels can directly provide accurate estimation of the haze`s transmission.
>
> 在有雾图像的暗通道中，（非天空区域）点的亮度值主要是大气光贡献的，场景本身的暗通道的亮度值应该趋近于0，所以，有雾图像的暗通道可以用来准确估计雾的传输率。

在雾天退化模型中
$$
I = t \cdot J  + (1-t)\cdot A
$$
取其暗通道，然后找局部最小值，由暗通道先验定理知，$t \cdot J = 0$，得到$I = (1-t)\cdot A$,其中A和I已知，即可直接求t。数学描述如下：(作者假设局部的空气是同质的，t(x)在局部区域$\omega_x$是一样的（uniform），而且三通道已知)
$$ {equation}
\begin{align}

I^{dark}(k)&= \min\limits_{x \in \omega_k } \min\limits_{c \in \{r,g,b\}}I^c(x) \\
&= \min\limits_{x \in \omega_k}(\min\limits_{c \in r,g,b}(t
(x)\cdot J^c(x)+(1-t(x))\cdot A^c))

\end{align}
$$ {equation}



由暗通道先验定理知$J^{dark} = \min \limits_{x \in \omega_k} \max \limits_{c \in \{r,g,b\}}J^c(y) \approx 0$，且假设在每一个窗口内透射率t(x)为常熟，定义它为$\tilde t(x)$,并且A值已经给定，所以进行化简可得
$$
\tilde t(x) =1-  \min \limits_{x \in \omega_k} (\min \limits_{c \in \{r,g,b\}} \frac{I^c(x)}{A^c})
$$
所以这就是透射率$\tilde t(x)$的预估值。

不过，在现实生活中，即使是晴天白云，空气中也存在着一些颗粒，因此，看远处的物体还是能感觉到雾的影响。另外，雾的存在让人类感受到景深的存在，因此，有必要在去雾的时候保留一定的雾，这可以通过在最后的结果式引入一个在[0,1]的因子，则可改写成
$$
\tilde t(x) =1- \omega \min \limits_{x \in \omega_k} (\min \limits_{c \in \{r,g,b\}} \frac{I^c(x)}{A^c})
$$

#### Restore J

在雾天退化模型上，带入A，t的预估值，则最终的恢复公式为:(其中当投射图t的值很小时，会导致J的值偏大，从而使得图像整体向白场过渡，因此一般可设置一阈值T0，当t值小于T0，令t=T0，本文所有的效果图均以T0=0.1为标准计算)
$$
J(x) = \frac{I(x)- A}{\max(t(x),t_0)} + A
$$

## Reference

1. [图像去雾，何凯明_clxiaoclxiao的博客-CSDN博客](https://blog.csdn.net/qq_26499769/article/details/51801048)
