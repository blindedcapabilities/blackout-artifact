
# BLACKOUT

This repository contains the **BLACKOUT artifact** and related resources.

Our artifact can be run in Bluespec simulation or on real hardware (which requires a
Xilinx VCU118 FPGA (UltraScale+ Virtex) and a Vivado license, version 2019.1).
In simulation mode, you can obtain limited performance results (sufficient to
reproduce the general overhead reported in the paper) and run all security
tests. However, tests related to CheriBSD and crypto benchmarks require VCU118. 

## Artifact Abstract
Lack of memory-safety and exposure to side channels are two
prominent, persistent challenges for the secure implementation of
software. Memory-safe programming languages promise to significantly reduce the prevalence of memory-safety bugs, but make it
more difficult to implement side-channel-resistant code. We aim to
address both memory-safety and side-channel resistance by augmenting memory-safe hardware with the ability for data-oblivious
programming. We describe an extension to the CHERI capability
architecture to provide blinded capabilities that allow data-oblivious
computation to be carried out by userspace tasks. We also present
BLACKOUT, our realization of blinded capabilities on a FPGA softcore
based on the speculative out-of-order CHERI-Toooba processor and
extend the CHERI-enabled Clang/LLVM compiler and the CheriBSD
operating system with support for blinded capabilities. BLACKOUT
makes writing side-channel-resistant code easier by making non-
data-oblivious operations via blinded capabilities explicitly fault.
Through rigorous evaluation we show that BLACKOUT ensures memory operated on through blinded capabilities is securely allocated,
used, and reclaimed and demonstrate that, in benchmarks comparable to those used by previous work, BLACKOUT imposes only a small
performance degradation (1.5% geometric mean) compared to the
baseline CHERI-Toooba processor.

More Information

- BLACKOUT: Data-Oblivious Computation with Blinded Capabilities  
  https://arxiv.org/pdf/2504.14654

- Blog post: Making Software Both Memory-Safe and Speculation-Safe  
  https://blog.ssg.aalto.fi/2025/10/making-software-both-memory-safe-and.html


```bibtex
@inproceedings{ElAtali25,
  title = {{BLACKOUT}: {Data-Oblivious Computation} with {Blinded Capabilities}},
  booktitle = {Proceedings of the 2025 {{ACM SIGSAC Conference}} on {{Computer}} and {{Communications Security}} ({{CCS}} '25)},
  author = {ElAtali, Hossam and G{\"u}lmez, Merve and Nyman, Thomas and Asokan, N.},
  year = {2025},
  month = oct,
  publisher = {ACM CCS'25},
  address = {Taipei, Taiwan},
  doi = {10.1145/3719027.3765169},
}
```

## Structure
The overall structure of the artifact is as follows:
  - [Simulation](#simulation-test) 
    * [Performance Evaluations](#performance-evaluations)
      * [coremark benchmark test](#coremark-test)
      * [binary search](#binary-search)
    * [Security Test](#security-test) 
      * [spectre test](#spectre-test) 
      * [libra noninference test](#libra-noninterference-test)
      * [property test](#property-test)
    
  - [Hardware testing](#hardware-test-vcu118) 
      * [Manual Building](#manual-building)
      * [Flashing FPGA and running benchmark on CheriBSD](#flashing-fpga-and-running-benchmark-on-cheribsd)

The dataset used for the paper results can be found under [`CCS_Submission_Dataset`](./CCS_Submission_Dataset/).


# Simulation Test 

To facilitate artifact evaluation, we provide instructions for running the experiments using our Docker images:

```bash
./docker_install.sh

# Note: if this is the first installation of Docker, logout from the current shell
#        and login again to enable the "docker" group in the current user
```

After installation, verify that Docker is working correctly by running:
`docker run --rm hello-world` command succeeds. If you get a permission error, make sure [your user is in the "docker" group](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)


Our Dockerfile automatically builds all dependencies, including clang, newlib,
and the Bluespec simulation mode of the Toooba core, for both the BLACKOUT and
baseline configurations. The image requires approximately 14 GB of disk space.

```sh
docker build -t blackout .

docker run -i -t blackout
```

## Performance Evaluations 

### Coremark Test 

To build for the baseline and purecap

```sh
cd $BLINDED_SW_ROOT
./build_scripts/build_coremark_for_sim.sh 
```
<details>
  <summary>Click to expand build output</summary>

```sh
=== CoreMark build script ===
[*] Building CoreMark (purecap)...
[✓] purecap build complete: ./benchmarks/coremark/coremark_purecap.elf  (log: ./build_logs/build_purecap.log, took 1s)
[*] Building CoreMark (baseline)...
[✓] baseline build complete: ./benchmarks/coremark/coremark_baseline.elf  (log: ./build_logs/build_baseline.log, took 1s)
=== All builds finished successfully ===
```
</details> 

To run for the baseline and purecap

```sh
cd $BLINDED_SW_ROOT
./build_scripts/run_coremark_for_sim.sh 
```
Excepted output 

```sh
=== CoreMark Performance Summary ===
Core                 Config          Total ticks     Δ         Overhead
CHERI-Toooba         baseline (nocap) 97621           -          -         
                     purecap         100606          2985       3.06%     

Blinded CHERI-Toooba baseline (nocap) 97621           -          -         
                     purecap         100606          2985       3.06%     
```
Note: The results in the paper are based on real hardware measurements (see in
Table 3), whereas
these results come from simulation. The ratios may differ slightly. 


## Binary Search
This script runs the binary_search algorithm in simulation mode. It is related to Figure 5-(c).
```sh
cd $BLINDED_SW_ROOT
./build_scripts/build_sim_bench.sh 
```
```sh
./build_scripts/run_sim_bench.sh
[*] Running binary_search_purecap_12 ...
    [purecap] cycles = 826
[*] Running binary_search_baseline_12 ...
    [baseline] cycles = 764
[*] Running binary_search_blinded_12 ...
    [blinded] cycles = 826

===== Summary Ratios =====
baseline/blinded = 764 / 826 = 0.92
baseline/purecap = 764 / 826 = 0.92
blinded/purecap = 826 / 826 = 1.00
```

## Security Test 
This section covers Section 7.3. 
### Spectre Test
First, we build the blinded and non-blinded versions of the Spectre tests.
```
cd $BLINDED_SW_ROOT
./build_scripts/build_spec_tests.sh
```
Excepted output  

<details>
  <summary>Click to expand build output</summary>

```sh
[*] Building Spectre Test (spec_btb_cheri)...
[✓] spec_btb_cheri build complete: /home/ubuntu/blinded-cheri-sw//benchmarks/spectretest/spec_btb_cheri.elf (log: /home/ubuntu/blinded-cheri-sw//build_logs/build_spec_btb_cheri.log, took 1s)
[*] Building Spectre Test (spec_rsb_cheri)...
[✓] spec_rsb_cheri build complete: /home/ubuntu/blinded-cheri-sw//benchmarks/spectretest/spec_rsb_cheri.elf (log: /home/ubuntu/blinded-cheri-sw//build_logs/build_spec_rsb_cheri.log, took 0s)
[*] Building Spectre Test (spec_stl_cheri)...
[✓] spec_stl_cheri build complete: /home/ubuntu/blinded-cheri-sw//benchmarks/spectretest/spec_stl_cheri.elf (log: /home/ubuntu/blinded-cheri-sw//build_logs/build_spec_stl_cheri.log, took 1s)
[*] Building Spectre Test (spec_btb_cheri_blinded)...
[✓] spec_btb_cheri_blinded build complete: /home/ubuntu/blinded-cheri-sw//benchmarks/spectretest/spec_btb_cheri_blinded.elf (log: /home/ubuntu/blinded-cheri-sw//build_logs/build_spec_btb_cheri_blinded.log, took 0s)
[*] Building Spectre Test (spec_rsb_cheri_blinded)...
[✓] spec_rsb_cheri_blinded build complete: /home/ubuntu/blinded-cheri-sw//benchmarks/spectretest/spec_rsb_cheri_blinded.elf (log: /home/ubuntu/blinded-cheri-sw//build_logs/build_spec_rsb_cheri_blinded.log, took 1s)
[*] Building Spectre Test (spec_stl_cheri_blinded)...
[✓] spec_stl_cheri_blinded build complete:
/home/ubuntu/blinded-cheri-sw//benchmarks/spectretest/spec_stl_cheri_blinded.elf
(log:
/home/ubuntu/blinded-cheri-sw//build_logs/build_spec_stl_cheri_blinded.log, took
1s)
```

</details> 



We then obtain simulation logs for each test.

```sh 
./build_scripts/generate_spec_logs.sh
[*] Processing spec_btb_cheri ...
    [LEAK] Secret leaked!
[*] Processing spec_rsb_cheri ...
    [LEAK] Secret leaked!
[*] Processing spec_stl_cheri ...
    [LEAK] Secret leaked!
[*] Processing spec_btb_cheri_blinded ...
    [SAFE] No leak detected.
[*] Processing spec_rsb_cheri_blinded ...
    [SAFE] No leak detected.
[*] Processing spec_stl_cheri_blinded ...
    [SAFE] No leak detected.
[✓] All tests completed in 4m 21s
```

### Libra noninterference Test

To run the Libra non-interference test, we build the two test cases, generate
vcd files for them, and then run the Libra evaluation script with the relevant
CHERI-Toooba signals. This result is related to Section 7.3 Empirical non-interference evaluation
This benchmark may take up to 1 hour.
```
cd $BLINDED_SW_ROOT
./build_scripts/build_binary_search_non_inference.sh
./build_scripts/generate_vcd_file.sh
./build_scripts/run-security-evaluation.sh ./benchmarks/binary_search_non_inter/binary_search_4_X.vcd ./benchmarks/binary_search_non_inter/binary_search_4_Y.vcd
```

Expected output:
```
All checks passed!
```

### Property Test 
This test shows how to use blinded data in stack, heap, or global area as
explained in Section 6.2 BLACKOUT Software Stack. 

```sh
cd $BLINDED_SW_ROOT
./build_scripts/build_property_test_for_sim.sh
```

<details>
  <summary>Click to expand build output</summary>

```sh
Benchmark directory: 
[*] Building blinded_global...
[*] Generating disassembly for blinded_global...
[✓] blinded_global done (took 1s)
[*] Building blinded_malloc...
[*] Generating disassembly for blinded_malloc...
[✓] blinded_malloc done (took 1s)
[*] Building blinded_stack...
[*] Generating disassembly for blinded_stack...
[✓] blinded_stack done (took 1s)
All benchmarks processed successfully!
```

</details> 

To run this test, run the following command
```sh
./build_scripts/run_property_test.sh
```

```sh
[blinded_global] ✅ Blinded test passed
[blinded_stack] ✅ Blinded test passed
[blinded_malloc] ✅ Blinded test passed
```

# Hardware Test on VCU118

This part requires Xilinx VCU118 FPGA (UltraScale+ Virtex) and a Vivado license,
version 2019.1. 

We provide pre-built bitstreams and binaries under the [`prebuilt`](./prebuilt/) directory.  
If you prefer not to build everything manually, you can skip ahead to the
[flashing fpga and benchmarking step](#flashing-fpga-and-running-benchmark-on-cheribsd).

## Manual Building

### Generate the Bitstreams

### Baseline Toooba
Clone the CHERI BESSPIN-GFE repository into a new $GFE_REPO directory, and replace the Toooba directory with the baseline version:
```sh
git clone https://github.com/CTSRD-CHERI/BESSPIN-GFE.git $GFE_REPO
cd $GFE_REPO
./init_submodules.sh

cd $GFE_REPO/bluespec-processors/P3/Toooba/
git checkout 1ae93da4 
git submodule update --init --recursive
```

Build the Toooba RTL and BESSPIN-GFE bitstream:

```sh
cd $GFE_REPO/bluespec-processors/P3/Toooba/src_SSITH_P3
make compile    # takes a while
cp Verilog_RTL/* xilinx_ip/hdl/
cd $GFE_REPO
./setup_soc_project.sh bluespec_p3 
./build.sh bluespec_p3
```

The generated bitstream can be found here:

```sh
cp $GFE_REPO/vivado/soc_bluespec_p3/soc_bluespec_p3.runs/impl_1/design_1.bit
$HOME/prebuilt/bitstreams/baseline/soc_bluespec_p3.bit

cp $GFE_REPO/vivado/soc_bluespec_p3/soc_bluespec_p3.runs/impl_1/design_1.ltx
$HOME/prebuilt/bitstreams/baseline/soc_bluespec_p3.ltx
``` 
#### Blinded Toooba 
For the Blinded bluespec-toooba, apply the necessary patches:
```sh
cd $GFE_REPO/bluespec-processors/P3/Toooba/
git apply ${HOME}/patch/toooba.patch 
cd $GFE_REPO/bluespec-processors/P3/Toooba/libs/cheri-cap-lib 
git apply ${HOME}/patch/cheri_cap_lib.patch
``` 
Build Toooba RTL and BESSPIN-GFE bitstream:

```sh
cd $GFE_REPO/bluespec-processors/P3/Toooba/src_SSITH_P3
make compile    # takes a while
cp Verilog_RTL/* xilinx_ip/hdl/
cd $GFE_REPO
./setup_soc_project.sh bluespec_p3 
./build.sh bluespec_p3
```

Find the bitstreams in the 

```sh
cp $GFE_REPO/vivado/soc_bluespec_p3/soc_bluespec_p3.runs/impl_1/design_1.bit
$HOME/prebuilt/bitstreams/blackout/soc_bluespec_p3.bit
``` 
### To build CheriBSD Kernel and LLVM 

[Cheribuild](https://github.com/CTSRD-CHERI/cheribuild) provides a convenient
way to build the CheriBSD kernel, LLVM, and related components. 
 
```sh
git clone https://github.com/CTSRD-CHERI/cheribuild $CHERIBUILD
```
By default, cheribuild expects the source folder to be at: `~/cheri/`

Clone and build LLVM:
```sh
cd ~/cheri/
git clone git@github.com:CTSRD-CHERI/llvm-project.git
cd $(CHERIBUILD)
./cheribuild.py llvm-native
```


### To build benchmark binary 


```sh
cd cheribsd-benchmarks
./benchmark.sh 
python copy_to_minimal.py ~/cheri/extra-files-minimal ## Copies object files only
```
Clone and prepare CheriBSD:
```sh
cd ~/cheri/
git clone https://github.com/CTSRD-CHERI/cheribsd.git
git checkout b2ad856aac657e26a9117ea6662289575e6eb514
git apply ./patch/cheribsd.diff 
```
Build the kernel:
```
cd $(CHERIBUILD)
./cheribuild.py  cheribsd-mfs-root-kernel-riscv64-purecap    --cheribsd-mfs-root-kernel-riscv64-purecap/build-fpga-kernels --cheribsd-mfs-root-kernel-riscv64-purecap/build-bench-kernels --cheribsd-mfs-root-kernel-riscv64-purecap/no-debug-kernel   -d 
```
The kernel will be out in the `~/cheri/output`

## Flashing FPGA and running benchmark on CheriBSD
The cheribuild system provides easy-to-use `vcu118-run.py` scripts that allow
you to flash the FPGA and run the CheriBSD kernel.


```sh
cd $(CHERIBUILD)
./vcu118-run.py  --bios $(HOME)/cheri/output/sdk/bbl-gfe/riscv64-purecap/bbl --kernel $(HOME)/cheri/output/kernel-riscv64-purecap.CHERI-PURECAP-GFE-NODEBUG  --gdb $(HOME)/opt/riscv/bin/riscv64-unknown-elf-gdb  --openocd $(HOME)/opt/bin/openocd 
```

Once the system boots into CheriBSD, you can follow the following script in
CheriBSD rootfs to evaluate the benchmark:

To reproduce the results shown in Figure 4 and Figure 5, you can run the
following command:

```sh
time risc_oblivious_blinded/binary_search_16.o 
```

### Running benchmark on baremetal

### Load elf file to FPGA 

Start OpenOCD
```sh
openocd -f testing/targets/ssith_gfe.cfg
```

Build baremetal benchmark:

```sh
./blinded-cheri-sw/baremetal_elf.sh
```
To get the output from terminal 
```sh
socat stdin,raw,echo=0 /dev/ttyUSB2,raw,echo=0  
```
Connect to FPGA via GDB
```sh
riscv64-unknown-elf-gdb -x  some.elf
target remote localhost:3333
load 
```

Open GDB: 
```sh
riscv64-unknown-elf-gdb -x  some.elf
target remote localhost:3333
load 
```
The benchmark will automatically run and print results for 1000 iterations, including the mean and variance.

These results correspond to Figure 5-c in the paper.

License:
Changes to original repo is subject to

© Ericsson AB 2025

© SSG 2025

Apache License, Version 2.0