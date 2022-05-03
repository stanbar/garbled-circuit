# Garbled Circuit protocol

Yao's Garbled Circuits (GC) is the most widley known and celebrated MPC technique, It is usually seen as best-performing, and many of the protocols we conver build on Yao's GC. It runs in constant rounds.

The idea of Garbled Circuits is to represent a function $F(x,y)$ as a key-value table $T_{x,y}$. Where the key is the concatenation of inputs $x|y$ and value is the output of $F(x,y)$. We represent such table as $T_{x,y}=\langle F(x,y) \rangle$. The output of $F(x,y)$ is obtained simply by retreiving $T_{x,y}$ from the corresponding row $x,y$.

For example if the functionality is f(x,y) = x > y. where the x and y are in Finite field of size 4. Then the first party construct a table. 

0 0 -> false
0 1 -> false
1 0 -> true
1 1 -> false

To make such functionality private, the first party $P_1$, encrypts each row using two random keys $k_x$ and $k_y$. 

0 0 -> enc_{k_x_0, k_y_0}(false)
0 1 -> enc_{k_x_0, k_y_1}(false)
1 0 -> enc_{k_x_1, k_y_0}(true)
1 1 -> enc_{k_x_1, k_y_1}(false)

To optimise the size of the table we use so-called point-and-permute.


