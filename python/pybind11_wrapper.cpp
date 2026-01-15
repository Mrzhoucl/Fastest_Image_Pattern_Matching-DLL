#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "TemplateMatcher.h"
#include <opencv2/opencv.hpp>

namespace py = pybind11;
using namespace TemplateMatching;

// 将numpy数组转换为OpenCV Mat
cv::Mat numpy_to_mat(py::array_t<unsigned char> input) {
    py::buffer_info buf_info = input.request();
    
    if (buf_info.ndim != 2 && buf_info.ndim != 3) {
        throw std::runtime_error("Input array must be 2D (grayscale) or 3D (BGR)");
    }
    
    int height = buf_info.shape[0];
    int width = buf_info.shape[1];
    int channels = (buf_info.ndim == 3) ? buf_info.shape[2] : 1;
    
    if (channels == 1) {
        return cv::Mat(height, width, CV_8UC1, (unsigned char*)buf_info.ptr);
    } else if (channels == 3) {
        cv::Mat mat(height, width, CV_8UC3, (unsigned char*)buf_info.ptr);
        cv::Mat gray;
        cv::cvtColor(mat, gray, cv::COLOR_BGR2GRAY);
        return gray;
    } else {
        throw std::runtime_error("Unsupported number of channels");
    }
}

// 将OpenCV Mat转换为numpy数组
py::array_t<unsigned char> mat_to_numpy(const cv::Mat& mat) {
    if (mat.channels() == 1) {
        py::array_t<unsigned char> result({mat.rows, mat.cols});
        py::buffer_info buf_info = result.request();
        std::memcpy(buf_info.ptr, mat.data, mat.rows * mat.cols);
        return result;
    } else {
        py::array_t<unsigned char> result({mat.rows, mat.cols, mat.channels()});
        py::buffer_info buf_info = result.request();
        std::memcpy(buf_info.ptr, mat.data, mat.rows * mat.cols * mat.channels());
        return result;
    }
}

PYBIND11_MODULE(templatematcher, m) {
    m.doc() = "Fast Image Pattern Matching Library";

    // MatchConfig
    py::class_<MatchConfig>(m, "MatchConfig")
        .def(py::init<>())
        .def_readwrite("max_pos", &MatchConfig::iMaxPos)
        .def_readwrite("max_overlap", &MatchConfig::dMaxOverlap)
        .def_readwrite("score", &MatchConfig::dScore)
        .def_readwrite("tolerance_angle", &MatchConfig::dToleranceAngle)
        .def_readwrite("min_reduce_area", &MatchConfig::iMinReduceArea)
        .def_readwrite("use_simd", &MatchConfig::bUseSIMD)
        .def_readwrite("sub_pixel_estimation", &MatchConfig::bSubPixelEstimation)
        .def_readwrite("bitwise_not", &MatchConfig::bBitwiseNot)
        .def_readwrite("stop_layer1", &MatchConfig::bStopLayer1)
        .def_readwrite("tolerance_range", &MatchConfig::bToleranceRange)
        .def_readwrite("tolerance1", &MatchConfig::dTolerance1)
        .def_readwrite("tolerance2", &MatchConfig::dTolerance2)
        .def_readwrite("tolerance3", &MatchConfig::dTolerance3)
        .def_readwrite("tolerance4", &MatchConfig::dTolerance4);

    // SingleTargetMatch
    py::class_<SingleTargetMatch>(m, "MatchResult")
        .def_readonly("pt_lt", &SingleTargetMatch::ptLT)
        .def_readonly("pt_rt", &SingleTargetMatch::ptRT)
        .def_readonly("pt_rb", &SingleTargetMatch::ptRB)
        .def_readonly("pt_lb", &SingleTargetMatch::ptLB)
        .def_readonly("pt_center", &SingleTargetMatch::ptCenter)
        .def_readonly("angle", &SingleTargetMatch::dMatchedAngle)
        .def_readonly("score", &SingleTargetMatch::dMatchScore)
        .def("__repr__", [](const SingleTargetMatch& m) {
            return "MatchResult(score=" + std::to_string(m.dMatchScore) + 
                   ", angle=" + std::to_string(m.dMatchedAngle) + 
                   ", center=(" + std::to_string(m.ptCenter.x) + 
                   ", " + std::to_string(m.ptCenter.y) + "))";
        });

    // MatchResult (wrapper)
    py::class_<MatchResult>(m, "MatchResults")
        .def_readonly("success", &MatchResult::success)
        .def_readonly("matches", &MatchResult::matches)
        .def_readonly("execution_time_ms", &MatchResult::executionTimeMs)
        .def("__len__", [](const MatchResult& r) { return r.matches.size(); })
        .def("__getitem__", [](const MatchResult& r, size_t i) {
            if (i >= r.matches.size()) throw py::index_error();
            return r.matches[i];
        })
        .def("__iter__", [](const MatchResult& r) {
            return py::make_iterator(r.matches.begin(), r.matches.end());
        }, py::keep_alive<0, 1>());

    // TemplateMatcher
    py::class_<TemplateMatcher>(m, "TemplateMatcher")
        .def(py::init<>())
        .def("learn_pattern", [](TemplateMatcher& self, py::array_t<unsigned char> template_img) {
            cv::Mat mat = numpy_to_mat(template_img);
            return self.LearnPattern(mat);
        }, "Learn pattern from template image (numpy array)")
        .def("learn_pattern_from_file", [](TemplateMatcher& self, const std::string& filepath) {
            cv::Mat img = cv::imread(filepath, cv::IMREAD_GRAYSCALE);
            if (img.empty()) {
                throw std::runtime_error("Failed to load image: " + filepath);
            }
            return self.LearnPattern(img);
        }, "Learn pattern from image file", py::arg("filepath"))
        .def("match", [](TemplateMatcher& self, py::array_t<unsigned char> source_img, 
                         const MatchConfig& config) {
            cv::Mat mat = numpy_to_mat(source_img);
            return self.Match(mat, config);
        }, "Match template in source image (numpy array)", 
           py::arg("source_img"), py::arg("config") = MatchConfig())
        .def("match_from_file", [](TemplateMatcher& self, const std::string& filepath, 
                                   const MatchConfig& config) {
            cv::Mat img = cv::imread(filepath, cv::IMREAD_GRAYSCALE);
            if (img.empty()) {
                throw std::runtime_error("Failed to load image: " + filepath);
            }
            return self.Match(img, config);
        }, "Match template in source image file", 
           py::arg("filepath"), py::arg("config") = MatchConfig())
        .def("is_pattern_learned", &TemplateMatcher::IsPatternLearned);

    // Visualization functions
    m.def("draw_match_result", [](py::array_t<unsigned char> image, 
                                   const std::vector<SingleTargetMatch>& matches,
                                   const std::vector<int>& color = {0, 255, 0},
                                   int thickness = 1,
                                   bool draw_labels = true) {
        cv::Mat img = numpy_to_mat(image);
        if (img.channels() == 1) {
            cv::cvtColor(img, img, cv::COLOR_GRAY2BGR);
        }
        cv::Scalar cv_color(color[0], color[1], color[2]);
        Visualization::DrawMatchResult(img, matches, cv_color, thickness, draw_labels);
        return mat_to_numpy(img);
    }, "Draw match results on image",
       py::arg("image"), py::arg("matches"),
       py::arg("color") = std::vector<int>{0, 255, 0},
       py::arg("thickness") = 1,
       py::arg("draw_labels") = true);

    // Point2d wrapper for Python
    py::class_<cv::Point2d>(m, "Point2d")
        .def(py::init<double, double>(), py::arg("x") = 0.0, py::arg("y") = 0.0)
        .def_readwrite("x", &cv::Point2d::x)
        .def_readwrite("y", &cv::Point2d::y)
        .def("__repr__", [](const cv::Point2d& p) {
            return "Point2d(" + std::to_string(p.x) + ", " + std::to_string(p.y) + ")";
        });
}
