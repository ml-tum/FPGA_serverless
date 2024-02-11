#include <iostream>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>
#include "../util/util.h"
using namespace cv;
using namespace std;

const int THRESHOLD = 64;

const int bufsize = 4*1024*1024;
char buf[bufsize];

int main()
{
    std::cin.read(buf, bufsize);
    size_t bytes = std::cin.gcount();
    if(bytes >= bufsize) {
        cout<<"Bad request: Buffer too small"<<endl;
        return 1;
    }

    InputArray bufarray{buf, (int)bytes};
    Mat img = imdecode(bufarray, IMREAD_ANYCOLOR);
    if(img.rows != 1080 || img.cols != 1920) {
        cout<<"Bad request: Wrong dimensions"<<endl;
        return 1;
    }

    int blockSize = 3;
    int apertureSize = 3;
    double k = 0.04;
    Mat dst = Mat::zeros( img.size(), CV_32FC1 );
    Mat dst_norm = Mat::zeros( img.size(), CV_32FC1 );
    
    measure_start();
    cornerHarris( img, dst, blockSize, apertureSize, k );   
    normalize( dst, dst_norm, 0, 255, NORM_MINMAX, CV_32FC1, Mat() );
    measure_end();
    
    for( int i = 0; i < dst_norm.rows ; i++ ) {
        for( int j = 0; j < dst_norm.cols; j++ ) {
            if(dst_norm.at<float>(i,j) >= THRESHOLD) {
                cout<<"Corner at "<<i<<", "<<j<<endl;
            }
        }
    }
    
    measure_write("corner", "cpu", 1080*1920*1);

    return 0;
}
