/*===============================================================*/
/*                                                               */
/*                       check_result.cpp                        */
/*                                                               */
/*      Software evaluation of training and test error rate      */
/*                                                               */
/*===============================================================*/

#include <cstdio>
#include "typedefs.h"
#include <fstream>
#include <iostream>

void check_results(LabelType* result, const LabelType* expected, int cnt)
{
  int correct_cnt = 0;

  // std::ofstream ofile;
  // ofile.open("outputs.txt");
  bool print_result=true;
  // if (ofile.is_open())
  if (print_result)
  {
    for (int i = 0; i < cnt; i ++ )
    {
      if (result[i] != expected[i])
        std::cout << "Test " << i << ": expected = " << int(expected[i]) << ", result = " << int(result[i]) << std::endl;
        // ofile << "Test " << i << ": expected = " << int(expected[i]) << ", result = " << int(result[i]) << std::endl;
      else
        correct_cnt ++;
    }

    // ofile << "\n\t " << correct_cnt << " / " << cnt << " correct!" << std::endl;
    std::cout << "\n\t " << std::dec << correct_cnt << " / " << cnt << " correct!" << std::endl;
    // ofile.close();
  }
  else
  {
    std::cout << "Failed to create output file!" << std::endl;
  }
      

}
