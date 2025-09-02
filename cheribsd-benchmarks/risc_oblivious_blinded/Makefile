# List of suffixes for all variants.
SUFFIXES = 12 14 16 18 20

# Generate object names for each benchmark.
FIND_MAX_OBJS       = $(foreach S, $(SUFFIXES), find_max_$S.o)
INT_SORT_OBJS       = $(foreach S, $(SUFFIXES), int_sort_$S.o)
MATRIX_MULT_OBJS    = $(foreach S, $(SUFFIXES), matrix_mult_$S.o)
BINARY_SEARCH_OBJS  = $(foreach S, $(SUFFIXES), binary_search_$S.o)
DNN_SEARCH_OBJS  		= $(foreach S, $(SUFFIXES), dnn_$S.o)

# The main target depends on all generated objects.
rv64: $(FIND_MAX_OBJS) $(INT_SORT_OBJS) $(MATRIX_MULT_OBJS) $(BINARY_SEARCH_OBJS) $(DNN_SEARCH_OBJS)

HOME_DIR   = $(HOME)/cheri/
SYSROOT_DIR ?= $(HOME_DIR)/output/rootfs-riscv64-purecap

RV64_GCC = $(HOME_DIR)/output/sdk/bin/riscv64-unknown-freebsd-clang \
           -target riscv64-unknown-freebsd -mno-relax -mcmodel=medium \
           --sysroot=$(SYSROOT_DIR) -fuse-ld=lld -march=rv64gcxcheri \
           -std=c2x -mabi=l64pc128d  -mno-xcheri-rvc -v

# Pattern rule for binary_search targets.
binary_search_%.o: binary_search_%.c
	$(RV64_GCC) $^ -O3 -Wall  -o $@

# Pattern rule for find_max targets.
find_max_%.o: ../include/asm.c find_max_%.c
	$(RV64_GCC) $^ -O3 -Wall -o $@

# Pattern rule for int_sort targets.
int_sort_%.o: ../include/asm.c int_sort_%.c
	$(RV64_GCC) $^ -O3 -Wall -o $@

# Pattern rule for matrix_mult targets.
matrix_mult_%.o: matrix_mult_%.c
	$(RV64_GCC) $^ -O3 -Wall -g -o $@

# Pattern rule for matrix_mult targets.
dnn%.o: dnn%.c
	$(RV64_GCC) $^ -O3 -Wall -o $@ -lm

clean:
	rm -f *.o
