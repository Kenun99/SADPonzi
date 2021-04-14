# SADPonzi: Detecting and Characterizing Ponzi Schemes inEthereum Smart Contracts

SADPonzi is a detection for Ponzi scheme smart contracts (ponzitract) base on symbolic execution technology. We implement it atop 

[teEther](https://github.com/nescio007/teether):

## Quickstart

1.  Use `Python 3.6.9` and build virtual environment

    ```bash
    $ python -m venv ./venv
    $ source ./venv/bin/activate
    ```

2.  Install dependencies

```bash
$ python -m pip install -r requirements.txt
```

3.  Detect ponzitract (\*.bin)

```bash
$ python /home/toor/SADPonzi/teether/bin/gen_exploit.py <path_to_bin>
```



### Ground Truth Benchmark

We filter the dataset used in https://github.com/blockchain-unica/ethereum-ponzi and get 133 ground truth ponzitracts (see our paper for details). At the meantimes, we collect 1395 DApp as non-Ponzi cases from dapptotal.com.  



### Public Dataset

We apply SADPonzi to all the 3.4 million smart contracts deployed by EOAs in Ethereum and identify 835 Ponzi scheme smart contracts in total, with a volume of over 17 million US Dollar invested from victims. See [this link](http://) for details.



## Academia

Our paper [**SADPonzi: Detecting and Characterizing Ponzi Schemes inEthereum Smart Contracts**]( ) was published at the [XXX ](http://xxx.com) ([slides](https://www.usenix.org/sites/default/files/conference/protected-files/security18_slides_krupp.pdf)).

```

```
