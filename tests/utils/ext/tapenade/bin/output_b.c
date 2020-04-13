/*        Generated by TAPENADE     (INRIA, Ecuador team)
    Tapenade 3.15 (master) -  8 Jan 2020 10:53
*/
#include <adBuffer.h>

/*
  Differentiation of function_0 in reverse (adjoint) mode:
   gradient     of useful results: d function_0 a b c
   with respect to varying inputs: d a b c
   RW status of diff variables: d:incr function_0:in-killed a:incr
                b:incr c:incr
*/
void function_0_b(double a, double *ab, double b, double *bb, double c, double
        *cb, double d, double *db, double function_0b) {
    double p = (a*a+b*b+c*c+d*d)*(1+1/(a*d-b*c));
    double pb = 0.0;
    double temp;
    double temp0;
    double tempb;
    double tempb0;
    double function_0;
    pb = function_0b;
    temp = a*d - b*c;
    temp0 = 1.0/temp;
    tempb = (temp0+1)*pb;
    tempb0 = -(temp0*(a*a+b*b+c*c+d*d)*pb/temp);
    *ab = *ab + d*tempb0 + 2*a*tempb;
    *db = *db + a*tempb0 + 2*d*tempb;
    *bb = *bb + 2*b*tempb - c*tempb0;
    *cb = *cb + 2*c*tempb - b*tempb0;
}
