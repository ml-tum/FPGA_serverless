#include <iostream>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>
#include "util.h"
using namespace cv;
using namespace std;

const int THRESHOLD = 64;

void func(std::string_view &input, std::stringstream &output)
{
    const char* buf = input.data();
    size_t bytes = input.size();

    InputArray bufarray{buf, (int)bytes};
    Mat img = imdecode(bufarray, IMREAD_ANYCOLOR);
    if(img.rows != 1080 || img.cols != 1920) {
        output<<"Bad request: Wrong dimensions"<<endl;
        return;
    }

    int blockSize = 3;
    int apertureSize = 3;
    double k = 0.04;
    Mat dst = Mat::zeros( img.size(), CV_32FC1 );
    Mat dst_norm = Mat::zeros( img.size(), CV_32FC1 );
    
    cornerHarris( img, dst, blockSize, apertureSize, k );   
    normalize( dst, dst_norm, 0, 255, NORM_MINMAX, CV_32FC1, Mat() );
    
    for( int i = 0; i < dst_norm.rows ; i++ ) {
        for( int j = 0; j < dst_norm.cols; j++ ) {
            if(dst_norm.at<float>(i,j) >= THRESHOLD) {
                output<<"Corner at "<<i<<", "<<j<<endl;
            }
        }
    }
}
