# SADPonzi: Detecting and Characterizing Ponzi Schemes inEthereum Smart Contracts

SADPonzi is a detection for Ponzi scheme smart contracts (ponzitract) base on symbolic execution technology. We implement it atop [teEther](https://github.com/nescio007/teether):



### Ground Truth Benchmark

We filter the dataset used in https://github.com/blockchain-unica/ethereum-ponzi and get 133 ground truth ponzitracts (see our paper for details). At the meantimes, we collect 1262 DApp as non-Ponzi cases from dapptotal.com. (see [link](https://github.com/Kenun99/SADPonzi/tree/main/dataset/rq1))





### Robustness Benchark


We generate four groups of data for the robustness experiment. (see [link](https://github.com/Kenun99/SADPonzi/tree/main/dataset/rq2))



### Large Scale Dataset


We apply SADPonzi to all the 3.4 million smart contracts deployed by EOAs in Ethereum and identify 835 Ponzi scheme smart contracts in total, with a volume of over 17 million US Dollar invested from victims. (see [link](https://github.com/Kenun99/SADPonzi/tree/main/dataset/rq3))



## Academia

Our paper [**SADPonzi: Detecting and Characterizing Ponzi Schemes inEthereum Smart Contracts**]( ) was published at the [XXX ](http://xxx.com) ([slides](https://www.usenix.org/sites/default/files/conference/protected-files/security18_slides_krupp.pdf)).

```

```

