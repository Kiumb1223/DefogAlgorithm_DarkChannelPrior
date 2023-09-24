

# Reproduction of a Defogging Algorithm Using Dark Channel Prior

> Reference paper : [Single Image Haze Removal Using Dark Channel Prior | IEEE Journals & Magazine | IEEE Xplore](https://ieeexplore.ieee.org/document/5567108)

![res2](https://github.com/Kiumb1223/img_store/blob/master/Res.png)

OriginalPic-----------------DarkChannelPic----------------DefogImage

## Introduction

### Dark Channel Prior

暗通道去雾算法是基于一个统计性质的先验定理：**在无雾图像中的非天空区域中，一些像素的RGB三通道中的像素值会很低，接近于0**。这个自然规律可以表达为
$$
J^{dark}(k) = min_{C \in \{r,g,b\}}(min_{x\in\omega_k} J^c(x))\approx0 \tag{*}
$$
其中，J为无雾图像，k代表图像中的一个点坐标，遍历r,g,b通道，每个通道中以k为中心的局部窗口$\omega_k$里，找一个最小值，分别是$min_{x\in\omega_k} J^r(x)$、$min_{x\in\omega_k} J^g(x)$、$min_{x\in\omega_k} J^b(x)$，最后在三者中找到最小值。

### Foggy Degradation Model

暗通道去雾模型为
$$
I = t\cdot J + (1-t)\cdot A \tag{**}
$$
其中，I为观测到的有雾图像，J是需要恢复的无雾图像，k是一个像素坐标，A是全局大气光，t是一个描述物体没有被散射抵达摄像机的传输率。A的物理意义是在没有雾的情况下，远处物体上的亮度，因为论文里面设置成全局空气光，所以可以感性地看做成一张白色的图片。而透射率则代表着光线被散射的比例，其值越大，光线被散射和吸收的作用越强，光线强度也越弱，表示该位置受到雾的遮挡越小。

我是按照抠图公式$I = F\cdot\alpha + B \cdot (1-\alpha)$来进行理解的。在抠图公式里I为图像，F为前景图像，B为背景图像，α为透明度。所以，（**)式一个直观上的理解为一个雾气图像I是无雾图像J和白色图像A按照透明度t叠加形成的。

所以，去雾的思路是需要求出A值和t值进而求出J图像。

而如何求出A值和t值，何凯明老师使用了暗通道先验这个统计规律（这个统计规律本身也存在不适用的场景，见limitations of the Dehaze Algorithms节）。

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

I^{dark}(k)&= \min\limits_{x \in \omega_k } \min\limits_{c \in \{r,g,b\}}I^c(x) \notag \\
&= \min\limits_{x \in \omega_k}(\min\limits_{c \in r,g,b}(t
(x)\cdot J^c(x)+(1-t(x))\cdot A^c))\notag 

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

#### Guided Filter

> 对于求解得到的传递函数，应用滤波器对其进行细化；又因为原文中使用的是软抠图的方法，过程复杂，速度缓慢，因此采用导向滤波对传递函数进行滤波。

引导滤波较之于Gaussian、Laplacian、Sobel等传统滤波方法来说，滤波器和图像是相互关联的。在引导滤波中，滤波器是导向图（Guided Image）。

不过，在定义导向滤波器之前，首先需要明确最关键的假设是：导向滤波器是导向图I和滤波器输出图q之间的局部线性模型(1-1)，即
$$
\left\{
\begin{align*}
q_i &= a_kI_i +b_k,\forall i \in \omega_k \tag{1-1}\\
q   &= p - n \tag{1-2}
\end{align*}
\right.
$$
其中，在图像的局部窗口$\omega _k$中，a~k~和b~k~都是常量系数。对局部线性模型的求导既有$\nabla q = a \nabla I$,所以输出图中的边缘信息都仅来自导向图I，也正如此，导向滤波才可以起到保留边缘细节的作用。

其中，式子(1-2)中表明输出图像q是输入图像p中叠加了噪声图像n。

现在为了输出图像和输入图像尽可能差异变小（结构上的差异，而不是像素值的差异），所以提出了基于均方误差，带有正则项的损失函数
$$
\begin{align}

E(a_k,b_k) = \Sigma_{i \in \omega_k}[(a_kI_i+b_k -p_i)^2+ \epsilon a_k^2] \tag{1-3}
\end{align}
$$
所以，为了使得式子(1-3)能达到最小，所以对a~k~和b~k~求偏导，最后结果为
$$
\begin{align}
&a_k = \frac{\frac{1}{\abs{\omega _k}} \sum\limits_{i \in \omega_k}p_iI_i-\overline p_k \bar I_k}{\bar I^2 _k - {\bar I_k}^2 + \epsilon} \tag{1-4}
\\

&b_k  = \bar p_k + \alpha _k \bar I_k\tag{1-5} \\

&\bar I_k为窗口\omega_k内引导图的均值；\notag \\
&\bar p_k为窗口\omega_k范围内的均值； \notag \\
&\abs {\omega_k}  为窗口\omega_k像素数量; \notag 

\end{align}
$$

用一句话来总结**引导滤波尽可能让输出图像的梯度和导向图相似，同时让输出图像的灰度与输入图像相似，以此来保留边缘并且滤除噪声**

所以编程实现就基于式子(1-4)与(1-5)，伪代码为![](https://img-blog.csdnimg.cn/2020030914115948.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0hJVkFOMQ==,size_16,color_FFFFFF,t_70)

##### Application of Guided Filter

- 以自身作为引导图的保边平滑滤波

- **以原图引导的对透射率滤波的暗通道去雾**

- 以原图引导的对权重图滤波的引导图像融合

### limitations of the Dehaze Algorithms

The dark channel prior may be invalid when the scene object is inherently similar to the airlight (e.g., snowy ground or a white wall) over a large local region and no shadow is cast on it.  

选择性滤波，与高斯滤波、双边滤波相比，具有导向性。通过输入一幅图像（矩阵）作为导向图，由此滤波器知道哪些地方是边缘，从而保护边缘。再达到滤波的同时，保持边缘细节。

## Comprehension

### Comprehension about Dark Channel Prior

我刚开始看这篇论文有个困惑就是暗通道这个规律与去雾到底是什么关系？现在我的思考结果是：（这是我自己的思考结果，可能会想当然）

在数学意义上，暗通道为（**）式提供了一个限制条件（*\*）式，进而能求出A、t、J，即完成去雾；

在物理意义上，暗通道提供了被雾遮挡的物体的轮廓信息——因为雾是白色的，像素值肯定是偏大的；而暗通道的定义将这部分像素值给过滤掉了，反而保留下了被雾遮挡的物体的像素信息。所以论文的工作就是依据这些信息来复原被雾遮挡的物体。

除了暗通道算法的理解之外，我还有一点深刻的感触就是**学知识不要学二手的**。我刚开始的时候是看博客来学习的，但是学的很模糊。所以我后来找了原文来看，里面的很多细节在博客里都没有详细说明，所以看完论文之后有种豁然开朗的感觉。

### Comprehension about Guide Filter

现在我结合暗通道去雾来阐述下我自己对于导向滤波的理解。

为什么要在暗通道去雾算法中添加导向滤波这一步骤呢？原本按照第一部分中的公式推导计算出A、t，的确能得到去雾之后的图像。但是，观察论文中所展示的这些去雾之后的图像，发现由于透射率图过于粗糙导致图像的部分区域的去雾效果不好，所以需要应用导向滤波来对透射率图进行细化。

我们选择原始图像的灰度图来作为引导图I，透射率图为输入图像p。而如何细化透射率图呢？我的理解主要是依据ω这项，当透射率图p与引导图像i结构上越相似时，引导图像i的高频细节也就保留越多，所以输出的透射率图在这些区域上也就更精细。

### Process Flow Chart

![暗通道去雾流程图](https://github.com/Kiumb1223/img_store/blob/master/%E6%9A%97%E9%80%9A%E9%81%93%E5%8E%BB%E9%9B%BE%E6%B5%81%E7%A8%8B%E5%9B%BE.png)

## Reference

1. [图像去雾，何凯明_clxiaoclxiao的博客-CSDN博客](https://blog.csdn.net/qq_26499769/article/details/51801048)
1. [导向滤波(Guided Filter)公式详解_lsflll的博客-CSDN博客](https://blog.csdn.net/weixin_43194305/article/details/88959183?ops_request_misc=%7B%22request%5Fid%22%3A%22169502725216800188584831%22%2C%22scm%22%3A%2220140713.130102334..%22%7D&request_id=169502725216800188584831&biz_id=0&spm=1018.2226.3001.4187)
1. [图像处理基础（一）引导滤波 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/438206777)
