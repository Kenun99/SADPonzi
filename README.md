# Move to https://github.com/Kenun99/tse_sadponzi

# SADPonzi: Detecting and Characterizing Ponzi Schemes inEthereum Smart Contracts

SADPonzi is a detection for Ponzi scheme smart contracts (ponzitract) base on symbolic execution technology. We implement it atop [teEther](https://github.com/nescio007/teether):



### Ground Truth Benchmark

We filter the dataset used in https://github.com/blockchain-unica/ethereum-ponzi and get 133 ground truth ponzitracts (see our paper for details). At the meantimes, we collect 1262 DApp as non-Ponzi cases from dapptotal.com. (see [link](https://github.com/Kenun99/SADPonzi/tree/main/dataset/rq1))





### Robustness Benchark


We generate four groups of data for the robustness experiment. (see [link](https://github.com/Kenun99/SADPonzi/tree/main/dataset/rq2))



### Large Scale Dataset


We apply SADPonzi to all the 3.4 million smart contracts deployed by EOAs in Ethereum and identify 835 Ponzi scheme smart contracts in total, with a volume of over 17 million US Dollar invested from victims. (see [link](https://github.com/Kenun99/SADPonzi/tree/main/dataset/rq3))



## Academia

Our paper [SADPonzi: Detecting and Characterizing Ponzi Schemes in Ethereum Smart Contracts](https://dl.acm.org/doi/10.1145/3460093) was published at the [ACM Sigmetrics' 21](https://www.sigmetrics.org/sigmetrics2021/).

```
@article{10.1145/3460093,
author = {Chen, Weimin and Li, Xinran and Sui, Yuting and He, Ningyu and Wang, Haoyu and Wu, Lei and Luo, Xiapu},
title = {SADPonzi: Detecting and Characterizing Ponzi Schemes in Ethereum Smart Contracts},
year = {2021},
issue_date = {June 2021},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
volume = {5},
number = {2},
url = {https://doi.org/10.1145/3460093},
doi = {10.1145/3460093},
journal = {Proc. ACM Meas. Anal. Comput. Syst.},
month = jun,
articleno = {26},
numpages = {30},
keywords = {symbolic execution, smart contract, ethereum, Ponzi scheme}
}
```
