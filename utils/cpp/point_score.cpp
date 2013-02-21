#include <math.h>

score_info point_score(double x1, double y1, double x2, double y2) {
  double dx = std::abs(x1-x2);
  double y_ratio = y1/y2;
  double y_margin = pow(std::max(y1,y2),2.2)/1000000;

  double x_comp = pow((0.015*dx),4);
  double y_comp = pow(std::max((double)0,abs(y_ratio-1)-y_margin),(double)5);
  double point_weight = y_margin+1;

  score_info result = {(1/(x_comp+y_comp+1))*point_weight,
                       point_weight};
  return result;
}
