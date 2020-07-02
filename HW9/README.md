# HW9 Submission

## Questions

### How long does it take to complete the training run? (hint: this session is on distributed training, so it will take a while)
It took 1536m23s

The command is modified as below with "time" to capture accurate stats.
Had to kill the run at 52000 steps 

```bash
nohup bash -c "time mpirun --allow-run-as-root -n 4 -H 10.45.220.130:2,10.45.220.139:2 -bind-to none -map-by slot --mca btl_tcp_if_include eth0 -x NCCL_SOCKET_IFNAME=eth0 -x NCCL_DEBUG=INFO -x LD_LIBRARY_PATH python run.py --config_file=/data/transformer-base.py --use_horovod=True --mode=train_eval" &
```

### Do you think your model is fully trained? How can you tell?

The evaluation loss kept on decreasing, but at a slow rate. If we run for more steps, the loss may still decrease, but it can lead to overfitting.

### Were you overfitting?

I was not able to observe the validation loss (stopped training after 50K). So it is not clear whether the model is overfitting. 

### Were your GPUs fully utilized?

 - The GPUs were fully utlized. I tried nvidia-smi on both machines and I am able to see that they hit 100%
 - The Memory-Usage on both GPUs were close to 100%

```text
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 418.67       Driver Version: 418.67       CUDA Version: 10.1     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  Tesla V100-PCIE...  Off  | 00000000:00:07.0 Off |                    0 |
| N/A   38C    P0    43W / 250W |  15424MiB / 16130MiB |    100%      Default |
+-------------------------------+----------------------+----------------------+
|   1  Tesla V100-PCIE...  Off  | 00000000:00:08.0 Off |                    0 |
| N/A   39C    P0    44W / 250W |  15424MiB / 16130MiB |    100%      Default |
+-------------------------------+----------------------+----------------------+

+-----------------------------------------------------------------------------+
| NVIDIA-SMI 418.67       Driver Version: 418.67       CUDA Version: 10.1     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  Tesla V100-PCIE...  Off  | 00000000:00:07.0 Off |                    0 |
| N/A   38C    P0    43W / 250W |  15422MiB / 16130MiB |    100%      Default |
+-------------------------------+----------------------+----------------------+
|   1  Tesla V100-PCIE...  Off  | 00000000:00:08.0 Off |                    0 |
| N/A   38C    P0    45W / 250W |  15424MiB / 16130MiB |    100%      Default |
+-------------------------------+----------------------+----------------------+
```

### Did you monitor network traffic (hint: apt install nmon ) ? Was network the bottleneck?

The network is not a bottleneck. The network Speed is 1000Mbps. 
The Recv and Trans speed is 230 Mbps max both , individually. So together it does not come close to 1000Mbps.

### Take a look at the plot of the learning rate and then check the config file. Can you explan this setting?

The file "transformer-base.py" has the following setting:

```bash
 48   "lr_policy": transformer_policy,
 49   "lr_policy_params": {
 50     "learning_rate": 2.0,
 51     "warmup_steps": 8000,
 52     "d_model": d_model,
 53   },
```

So, until step 8000, the learning rate goes learnearly up. (high learning rate), then it slows down. 

### How big was your training set (mb)? How many training lines did it contain?

The training set is 636 Mb (English) + 710 Mb (German). Total is 1.3G
Total 4562102 lines each.  

### What are the files that a TF checkpoint is comprised of?

Below are the files that a TF checkpoint is comprised of

```
-rw-r--r-- 1 root root     36131 Jun 27 05:55 model.ckpt-0.index
-rw-r--r-- 1 root root 852267044 Jun 27 05:55 model.ckpt-0.data-00000-of-00001
-rw-r--r-- 1 root root        81 Jun 27 05:55 checkpoint
-rw-r--r-- 1 root root  15374541 Jun 27 05:55 model.ckpt-0.meta
```

### How big is your resulting model checkpoint (mb)?
```
-rw-r--r-- 1 shajikk1 shajikk1 852267044 Jun 28 04:49 'val_loss=1.6078-step-48013.data-00000-of-00001'
-rw-r--r-- 1 shajikk1 shajikk1     36131 Jun 28 04:49 'val_loss=1.6078-step-48013.index'
-rw-r--r-- 1 shajikk1 shajikk1  15374535 Jun 28 04:49 'val_loss=1.6078-step-48013.meta'
```

The model check point consists of 3 files of total 867 Mb.


### Remember the definition of a "step". How long did an average step take?
The average step took 1.714 seconds. Added up all the averages printed in nohup.out and found the average of that using bc utility.

### How does that correlate with the observed network utilization between nodes?
Yes, the nmap Recv and Trans output for each machine seems to change around 2 seconds and that shows some correlation.

