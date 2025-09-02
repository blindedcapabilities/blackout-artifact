#!/bin/bash

cd ./risc_oblivious_blinded
make clean 
make rv64 

cd ..
cd ./risc_oblivious_hybrid
make clean
make rv64 

cd ..
cd ./risc_oblivious_nonblinded
make clean
make rv64 
