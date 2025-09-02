/*
 *  Oblivious DNN is the same as non-oblivious DNN.
 */
 #include <stdio.h>
 #include <stdlib.h>
 #include <math.h>


 
 #define ReLU(x) (x > 0) ? x : 0
 static int seed = 0;
 static int nInputs = 1 << 8;
 static int nL1Neurons = 1 << 8;
 static int nOutputs = 1 << 6;
 
 long GenRandFloat(int max){
  return ((long)rand() / (long)(RAND_MAX / max));
}

void __attribute__((noinline)) Inference(long* input, long* output, long* W1, long* B1, long* W2, long* B2){
  long* L1Output = (long*)malloc(sizeof(long) * nL1Neurons);
  long* L2Output = (long*)malloc(sizeof(long) * nOutputs);

  /// L1Output = ReLU(W1 * input + B2)
  for(int i = 0; i < nL1Neurons; i++){
      L1Output[i] = B1[i];
      for(int j = 0; j < nInputs; j++)
          L1Output[i] += W1[i * nInputs + j] * input[j];
      L1Output[i] = ReLU(L1Output[i]);
  }

  /// L2Output = ReLU(W2 * L1Output + B1)
  for(int i = 0; i < nOutputs; i++){
      L2Output[i] = B2[i];
      for(int j = 0; j < nL1Neurons; j++)
          L2Output[i] += W2[i * nL1Neurons + j] * L1Output[j];
      L2Output[i] = ReLU(L2Output[i]);
  }

  // Compute exponentials and accumulate the sum.
  long  sum = 0.0;
  for (int i = 0; i < nOutputs; i++) {
      L2Output[i] = exp(L2Output[i]);
      sum += L2Output[i];
  }

  for(int i = 0; i < nOutputs; i++){
      output[i] = L2Output[i] / sum;
  }

  free(L1Output);
  free(L2Output);
}

int main(){
  srand(seed);

  // Initialize inputs
  long* input = (long*)malloc(sizeof(long) * nInputs);
  for(int i = 0; i < nInputs; i++)
      input[i] = GenRandFloat(10);


  // Initialize outputs
  long* output = (long*)malloc(sizeof(long) * nOutputs);

  // Initialize layer 1
  long* W1 = (long*) malloc(sizeof(long) * nInputs * nL1Neurons);
  long* B1 = (long*) malloc(sizeof(long) * nL1Neurons);
  for(int i = 0; i < nL1Neurons; i++){
      B1[i] = GenRandFloat(10) - GenRandFloat(10);
      for(int j = 0; j < nInputs; j++)
          W1[i*nInputs + j] = GenRandFloat(10) - GenRandFloat(10);
  }

  // Initialize layer 2
  long* W2 = (long*) malloc(sizeof(long) * nL1Neurons * nOutputs);
  long* B2 = (long*) malloc(sizeof(long) * nOutputs);
  for(int i = 0; i < nOutputs; i++){
      B2[i] = GenRandFloat(10) - GenRandFloat(10);
      for(int j = 0; j < nL1Neurons; j++)
          W2[i*nL1Neurons + j] = GenRandFloat(10) - GenRandFloat(10);
  }

  Inference(input, output, W1, B1, W2, B2);

  //Print output
  //for(int i = 0; i < nOutputs; i++)
  //    printf("%f ", output[i]);
  //ee_printf("\n");

  free(input);
  free(output);
  free(W1);
  free(B1);
  free(W2);
  free(B2);

  return 0;
}
