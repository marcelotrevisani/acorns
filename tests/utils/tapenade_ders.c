/*        Generated by TAPENADE     (INRIA, Ecuador team)
    Tapenade 3.15 (master) -  8 Jan 2020 10:53
*/


/*
  Differentiation of function_2 in reverse (adjoint) mode:
   gradient     of useful results: k function_2
   with respect to varying inputs: k
   RW status of diff variables: k:incr function_2:in-killed
*/
void function_2_b(double k, double *kb, double function_2b) {
    double p = sin(k) + cos(k) + pow(k, 2);
    double pb = 0.0;
    double function_2;
    pb = function_2b;
    *kb = *kb + (cos(k)+2*pow(k, 2-1)-sin(k))*pb;
}
